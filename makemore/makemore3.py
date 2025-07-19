import numpy as np
import torch
import torch.nn.functional as F #for one hot encoding
import pandas as pd
from matplotlib import pyplot as plt
import random

words=open("names.txt","r").read().splitlines()

chars = sorted(set(''.join(words)))  
chars =['.'] + chars     
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
block_size=5

# creating traing testing and validation dataset
def buildDataset(words):
    X=[]
    Y=[]
    for w in words:
        #print(w)
        context=[0]*block_size
        for ch in w +'.':
            ix=stoi[ch]
            Y.append(ix)
            X.append(context)
            #print(''.join(itos[i] for i in context))
            context=context[1:]+[ix]
    X=torch.tensor(X)
    Y=torch.tensor(Y)
    return X,Y

random.shuffle(words)
n=int(0.8*len(words))
m=int(0.9*len(words))
Xtrain,Ytrain=buildDataset(words[:n])
XVal,YVal=buildDataset(words[n:m])
Xtest,Ytest=buildDataset(words[m:])

n_emb=10 #dimansionality of each character
n_n=300 #number of neurons
C=torch.randn(len(chars),n_emb) 
W1=torch.randn(n_emb*block_size,n_n) * (5/3) / ((n_emb*block_size)**0.5) #to prevent plateau region of tanh for h
#the above formula is given in the pytorch documentation for standard deviation of tanh 
B1=torch.randn(n_n) * 0.01
W2 = torch.randn(n_n, len(chars)) / np.sqrt(n_n)
B2=torch.randn(len(chars)) * 0

bngain=torch.ones(1,n_n)
bnbais=torch.zeros(1,n_n) #batch normalization parameters 
bnmean_running = torch.zeros(1, n_n)
bnstd_running = torch.ones(1, n_n)

parameters=[C,W1,W2,B1,B2,bngain,bnbais]

for p in parameters:
    p.requires_grad=True

stepi=[]
lossi=[]
lr=0.1

batch_size=60

for i in range(200000): 
    #minibatch
    ix=torch.randint(0,Xtrain.shape[0],(batch_size,)) 
    #forward pass
    emb=C[Xtrain[ix]]
    embcat=emb.view(emb.shape[0],-1)
    hpreact = embcat @ W1 + B1
    #batch normalization
    batch_mean = hpreact.mean(0, keepdim=True)
    batch_var = hpreact.var(0, unbiased=False, keepdim=True)
    hpreact = bngain * (hpreact - batch_mean) / torch.sqrt(batch_var + 1e-5) + bnbais

    with torch.no_grad():
        bnmean_running = 0.99 * bnmean_running + 0.01 * batch_mean
        bnstd_running = 0.99 * bnstd_running + 0.01 * batch_var
        
    h=torch.tanh(hpreact)
    logits=h @ W2 +B2
    loss=F.cross_entropy(logits,Ytrain[ix])
    #backward pass
    for p in parameters:
        p.grad=None
    loss.backward()
    if i>150000: #step decay learning rate
        lr=0.01
    for p in parameters:
        p.data-=lr*p.grad
    stepi.append(i)
    lossi.append(loss.item())
print("training loss: ",loss.item())

# validation
with torch.no_grad():
    emb = C[XVal]
    embcat = emb.view(emb.shape[0], -1)
    hpreact = embcat @ W1 + B1
    hpreact = bngain * (hpreact - bnmean_running) / torch.sqrt(bnstd_running + 1e-5) + bnbais
    h = torch.tanh(hpreact)
    logits = h @ W2 + B2
    val_loss = F.cross_entropy(logits, YVal)
print("Validation loss:", val_loss.item())

#sampling
with torch.no_grad():
    for _ in range(20):
        out = []
        Context = [0] * block_size
        while True:
            emb = C[torch.tensor([Context])]
            hpreact = emb.view(1, -1) @ W1 + B1
            hpreact = bngain * (hpreact - bnmean_running) / torch.sqrt(bnstd_running + 1e-5) + bnbais
            h = torch.tanh(hpreact)
            logits = h @ W2 + B2
            probs = F.softmax(logits, dim=1)
            ix = torch.multinomial(probs, num_samples=1).item()
            out.append(ix)
            Context = Context[1:] + [ix]
            if ix == 0 or len(out) > 30:
                break
        print("".join(itos[i] for i in out))
