import os, time, math, glob
import numpy as np
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group
from torch.utils.data import Dataset
from torch.nn import functional as F
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torch import nn
from torch.cuda.amp import GradScaler

@dataclass
class GPTConfig:
  block_size: int = 1024
  vocab_size: int = 50257 #5000 byte pair encoding merges + 256 original tokens + 1 <|endoftext|> token
  n_layer: int = 12 #no. of layers
  n_head: int = 12 #no. of heads
  n_embed: int = 768

class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config.n_embed % config.n_head == 0
        self.c_attn = nn.Linear(config.n_embed, 3 * config.n_embed)
        self.c_proj = nn.Linear(config.n_embed, config.n_embed)
        self.n_head = config.n_head
        self.n_embed = config.n_embed
        self.register_buffer(
            "bias",
            torch.tril(torch.ones(config.block_size, config.block_size))
                 .view(1, 1, config.block_size, config.block_size)
        )

    def forward(self, x):
        B, T, C = x.size()
        qkv = self.c_attn(x)
        q, k, v = qkv.split(self.n_embed, dim=2)
        k = k.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        q = q.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
        v = v.view(B, T, self.n_head, C // self.n_head).transpose(1, 2)

        #att = (q @ k.transpose(-2, -1)) / math.sqrt(k.size(-1))
        #att = att.masked_fill(self.bias[:, :, :T, :T] == 0, float('-inf'))
        #att = F.softmax(att, dim=-1)
        #y = att @ v
        y=F.scaled_dot_product_attention(q,k,v,is_causal=True)
        y = y.transpose(1, 2).contiguous().view(B, T, C)
        y = self.c_proj(y)
        return y

class MLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.c_fc = nn.Linear(config.n_embed, 4 * config.n_embed)
        self.gelu = nn.GELU(approximate='tanh')
        self.c_proj = nn.Linear(4 * config.n_embed, config.n_embed)

    def forward(self, x):
        x = self.c_fc(x)
        x = self.gelu(x)
        x = self.c_proj(x)
        return x

class Block(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln_1 = nn.LayerNorm(config.n_embed)
        self.attn = CausalSelfAttention(config)
        self.ln_2 = nn.LayerNorm(config.n_embed)
        self.mlp = MLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x

class GPT(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config = config

        self.transformer = nn.ModuleDict(dict(
            wte = nn.Embedding(config.vocab_size, config.n_embd),
            wpe = nn.Embedding(config.block_size, config.n_embd),
            h = nn.ModuleList([Block(config) for _ in range(config.n_layer)]),
            ln_f = nn.LayerNorm(config.n_embd),
        ))
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size, bias=False)

        # weight sharing scheme
        self.transformer.wte.weight = self.lm_head.weight

        # init params
        self.apply(self._init_weights)

    def _init_weights(self, module):
        if isinstance(module, nn.Linear):
            std = 0.02
            if hasattr(module, 'NANOGPT_SCALE_INIT'):
                std *= (2 * self.config.n_layer) ** -0.5
            torch.nn.init.normal_(module.weight, mean=0.0, std=std)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        # idx is of shape (B, T)
        B, T = idx.size()
        assert T <= self.config.block_size, f"Cannot forward sequence of length {T}, block size is only {self.config.block_size}"
        # forward the token and posisition embeddings
        pos = torch.arange(0, T, dtype=torch.long, device=idx.device) # shape (T)
        pos_emb = self.transformer.wpe(pos) # position embeddings of shape (T, n_embd)
        tok_emb = self.transformer.wte(idx) # token embeddings of shape (B, T, n_embd)
        x = tok_emb + pos_emb
        # forward the blocks of the transformer
        for block in self.transformer.h:
            x = block(x)
        # forward the final layernorm and the classifier
        x = self.transformer.ln_f(x)
        logits = self.lm_head(x) # (B, T, vocab_size)
        loss = None
        if targets is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        return logits, loss

    @classmethod
    def from_pretrained(cls, model_type):
        """Loads pretrained GPT-2 model weights from huggingface"""
        assert model_type in {'gpt2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl'}
        from transformers import GPT2LMHeadModel
        print("loading weights from pretrained gpt: %s" % model_type)

        # n_layer, n_head and n_embd are determined from model_type
        config_args = {
            'gpt2':         dict(n_layer=12, n_head=12, n_embd=768),  # 124M params
            'gpt2-medium':  dict(n_layer=24, n_head=16, n_embd=1024), # 350M params
            'gpt2-large':   dict(n_layer=36, n_head=20, n_embd=1280), # 774M params
            'gpt2-xl':      dict(n_layer=48, n_head=25, n_embd=1600), # 1558M params
        }[model_type]
        config_args['vocab_size'] = 50257 # always 50257 for GPT model checkpoints
        config_args['block_size'] = 1024 # always 1024 for GPT model checkpoints
        # create a from-scratch initialized minGPT model
        config = GPTConfig(**config_args)
        model = GPT(config)
        sd = model.state_dict()
        sd_keys = sd.keys()
        sd_keys = [k for k in sd_keys if not k.endswith('.attn.bias')] # discard this mask / buffer, not a param

        # init a huggingface/transformers model
        model_hf = GPT2LMHeadModel.from_pretrained(model_type)
        sd_hf = model_hf.state_dict()

        # copy while ensuring all of the parameters are aligned and match in names and shapes
        sd_keys_hf = sd_hf.keys()
        sd_keys_hf = [k for k in sd_keys_hf if not k.endswith('.attn.masked_bias')] # ignore these, just a buffer
        sd_keys_hf = [k for k in sd_keys_hf if not k.endswith('.attn.bias')] # same, just the mask (buffer)
        transposed = ['attn.c_attn.weight', 'attn.c_proj.weight', 'mlp.c_fc.weight', 'mlp.c_proj.weight']
        # basically the openai checkpoints use a "Conv1D" module, but we only want to use a vanilla Linear
        # this means that we have to transpose these weights when we import them
        assert len(sd_keys_hf) == len(sd_keys), f"mismatched keys: {len(sd_keys_hf)} != {len(sd_keys)}"
        for k in sd_keys_hf:
            if any(k.endswith(w) for w in transposed):
                # special treatment for the Conv1D weights we need to transpose
                assert sd_hf[k].shape[::-1] == sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k].t())
            else:
                # vanilla copy over the other parameters
                assert sd_hf[k].shape == sd[k].shape
                with torch.no_grad():
                    sd[k].copy_(sd_hf[k])

        return model

    def configure_optimizers(self, weight_decay, learning_rate, device_type):
        # start with all of the candidate parameters (that require grad)
        param_dict = {pn: p for pn, p in self.named_parameters()}
        param_dict = {pn: p for pn, p in param_dict.items() if p.requires_grad}
        # create optim groups. Any parameters that is 2D will be weight decayed, otherwise no.
        # i.e. all weight tensors in matmuls + embeddings decay, all biases and layernorms don't.
        decay_params = [p for n, p in param_dict.items() if p.dim() >= 2]
        nodecay_params = [p for n, p in param_dict.items() if p.dim() < 2]
        optim_groups = [
            {'params': decay_params, 'weight_decay': weight_decay},
            {'params': nodecay_params, 'weight_decay': 0.0}
        ]
        num_decay_params = sum(p.numel() for p in decay_params)
        num_nodecay_params = sum(p.numel() for p in nodecay_params)
        if master_process:
            print(f"num decayed parameter tensors: {len(decay_params)}, with {num_decay_params:,} parameters")
            print(f"num non-decayed parameter tensors: {len(nodecay_params)}, with {num_nodecay_params:,} parameters")
        # Create AdamW optimizer and use the fused version if it is available
        fused_available = 'fused' in inspect.signature(torch.optim.AdamW).parameters
        use_fused = fused_available and device_type == "cuda"
        if master_process:
            print(f"using fused AdamW: {use_fused}")
        optimizer = torch.optim.AdamW(optim_groups, lr=learning_rate, betas=(0.9, 0.95), eps=1e-8, fused=use_fused)
        return optimizer

import tiktoken
import numpy as np

data_root = "fineweb_shards"   # folder with shard_*.npy
out_dir = "log"                # checkpoints/logs
os.makedirs(out_dir, exist_ok=True)

B = 4                # micro-batch size per GPU
T = 1024             # sequence length
grad_accum_steps = 16   # gradient accumulation
max_steps = 1000        # set higher when doing real training
lr = 3e-4
eval_interval = 100
eval_batches = 50
device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
compile_model = False

ddp = int(os.environ.get("RANK", -1)) != -1
if ddp:
    init_process_group(backend="nccl")
    ddp_rank = int(os.environ["RANK"])
    ddp_local_rank = int(os.environ["LOCAL_RANK"])
    ddp_world_size = int(os.environ["WORLD_SIZE"])
    device = f"cuda:{ddp_local_rank}"
    torch.cuda.set_device(device)
    master_process = ddp_rank == 0
else:
    ddp_rank = 0
    ddp_local_rank = 0
    ddp_world_size = 1
    master_process = True

if master_process:
    print(f"Using device={device}, dtype={dtype}, ddp_world_size={ddp_world_size}")

def mmap_tokens_from_file(path):
    return np.load(path, mmap_mode="r")  # each shard is a flat array of tokens

class DataLoaderLite:
    def __init__(self, B, T, process_rank, num_processes, split, data_root="fineweb_shards"):
        self.B, self.T = B, T
        self.process_rank = process_rank
        self.num_processes = num_processes
        assert split in {"train", "val"}

        all_shards = sorted(glob.glob(os.path.join(data_root, "*.npy")))
        if master_process:
            print(f"[DataLoaderLite] found {len(all_shards)} shards")
        # crude split: 90% train, 10% val
        n_val = max(1, len(all_shards) // 10)
        if split == "train":
            self.shard_paths = all_shards[:-n_val]
        else:
            self.shard_paths = all_shards[-n_val:]

        self.current_shard = 0
        self.tokens_np = mmap_tokens_from_file(self.shard_paths[self.current_shard])
        self.shard_len = len(self.tokens_np)
        self.current_position = self.B * self.T * self.process_rank

    def _advance_shard(self):
        self.current_shard = (self.current_shard + 1) % len(self.shard_paths)
        self.tokens_np = mmap_tokens_from_file(self.shard_paths[self.current_shard])
        self.shard_len = len(self.tokens_np)
        self.current_position = self.B * self.T * self.process_rank

    def next_batch(self):
        B, T = self.B, self.T
        needed = B * T + 1
        if self.current_position + needed > self.shard_len:
            self._advance_shard()
        start = self.current_position
        end = start + needed
        np_slice = self.tokens_np[start:end]
        t = torch.tensor(np_slice.astype(np.int64), dtype=torch.long)
        x = t[:-1].view(B, T)
        y = t[1:].view(B, T)
        self.current_position += B * T * self.num_processes
        return x, y

train_loader = DataLoaderLite(B, T, ddp_rank, ddp_world_size, split="train", data_root=data_root)
val_loader = DataLoaderLite(B, T, ddp_rank, ddp_world_size, split="val", data_root=data_root)

model = GPT(config).to(device)

if compile_model:
    model = torch.compile(model)

raw_model = model
if ddp:
    model = DDP(model, device_ids=[ddp_local_rank])

optimizer = AdamW(model.parameters(), lr=lr)
scaler = GradScaler()

def estimate_loss():
    model.eval()
    losses = []
    for _ in range(eval_batches):
        X, Y = val_loader.next_batch()
        X, Y = X.to(device), Y.to(device)
        with torch.no_grad():
            with torch.autocast(device_type="cuda", dtype=dtype):
                _, loss = model(X, Y)
        losses.append(loss.item())
    model.train()
    return sum(losses) / len(losses)

# training loop
for step in range(start_step, max_steps):
    optimizer.zero_grad()
    loss_accum = 0.0

    for micro in range(grad_accum_steps):
        X, Y = train_loader.next_batch()
        X, Y = X.to(device), Y.to(device)
        with torch.autocast(device_type="cuda", dtype=dtype):
            _, loss = model(X, Y)
            loss = loss / grad_accum_steps
        scaler.scale(loss).backward()
        loss_accum += loss.item()

    scaler.step(optimizer)
    scaler.update()

    if master_process and step % 10 == 0:
        print(f"Step {step}: loss={loss_accum:.4f}")

    if step % eval_interval == 0 and master_process:
        val_loss = estimate_loss()
        print(f"Step {step}: val_loss={val_loss:.4f}")
        ckpt = {
            "model": raw_model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "step": step,
        }
        torch.save(ckpt, ckpt_path)

# optionally resume
start_step = 0
ckpt_path = os.path.join(out_dir, "latest.pt")
if os.path.isfile(ckpt_path):
    checkpoint = torch.load(ckpt_path, map_location=device)
    raw_model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    start_step = checkpoint["step"]+1
    if master_process:
        print(f"Resumed from {ckpt_path} at step {start_step}")

for step in range(start_step, max_steps):
    optimizer.zero_grad()
    loss_accum = 0.0

    for micro in range(grad_accum_steps):
        X, Y = train_loader.next_batch()
        X, Y = X.to(device), Y.to(device)
        with torch.autocast(device_type="cuda", dtype=dtype):
            out = model(X, labels=Y)
            loss = out.loss / grad_accum_steps
        scaler.scale(loss).backward()
        loss_accum += loss.item()

    scaler.step(optimizer)
    scaler.update()

    if master_process and step % 10 == 0:
        print(f"Step {step}: loss={loss_accum:.4f}")

    if step % eval_interval == 0 and master_process:
        val_loss = estimate_loss()
        print(f"Step {step}: val_loss={val_loss:.4f}")
        ckpt = {
            "model": raw_model.state_dict(),
            "optimizer": optimizer.state_dict(),
            "step": step,
        }
        torch.save(ckpt, ckpt_path)

if ddp:
    destroy_process_group()

