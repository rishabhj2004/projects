"""
fineweb_download.py

Download and save FineWeb dataset shards (2–7 GB of text).
"""

import os
import multiprocessing as mp
from datasets import load_dataset

# ----------------------------
# Settings
# ----------------------------
dataset_name = "HuggingFaceFW/fineweb-edu"   # Good replacement for OpenWebText
split = "train"                              # Use training split
output_dir = "fineweb_shards"                 # Folder where shards are saved
target_size_gb = 7                            # Approx. total size (set between 2–7)
shard_size_mb = 100                           # Each file ~100MB
num_proc = mp.cpu_count()                     # Parallelism for speed

os.makedirs(output_dir, exist_ok=True)

# ----------------------------
# Load dataset (streaming mode = True so it won’t download all at once)
# ----------------------------
print(f"Loading dataset: {dataset_name}")
dataset = load_dataset(dataset_name, split=split, streaming=True)

# ----------------------------
# Write dataset into shards
# ----------------------------
def write_shards():
    shard_idx = 0
    buffer = []
    buffer_size = 0
    total_size = 0

    for i, example in enumerate(dataset):
        text = example.get("text", "")
        buffer.append(text + "\n")
        buffer_size += len(text.encode("utf-8"))

        # When buffer hits ~100MB, write a shard
        if buffer_size >= shard_size_mb * 1024 * 1024:
            shard_path = os.path.join(output_dir, f"shard_{shard_idx:05d}.txt")
            with open(shard_path, "w", encoding="utf-8") as f:
                f.writelines(buffer)

            shard_size_gb = buffer_size / (1024**3)
            total_size += shard_size_gb
            print(f"Saved {shard_path} ({shard_size_gb:.2f} GB). Total so far: {total_size:.2f} GB")

            buffer = []
            buffer_size = 0
            shard_idx += 1

            if total_size >= target_size_gb:
                print(f"Reached target size of {target_size_gb} GB. Stopping.")
                break

    # Write any leftover buffer
    if buffer:
        shard_path = os.path.join(output_dir, f"shard_{shard_idx:05d}.txt")
        with open(shard_path, "w", encoding="utf-8") as f:
            f.writelines(buffer)
        print(f"Saved leftover {shard_path}")

if __name__ == "__main__":
    write_shards()

