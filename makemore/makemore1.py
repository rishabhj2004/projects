import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import math
import random
import sys
import torch
data=open("names.txt","r").read().splitlines()
chars = sorted(set(''.join(data)))  
chars =['.'] + chars     
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}
#neural network approach
import torch.nn.functional as F
xs,ys=[],[]
for w in data:
    ch=['.']+list(w)+['.']
    for ch1,ch2 in zip(ch,ch[1:]):
        ix1=stoi[ch1]
        ix2=stoi[ch2]
        xs.append(ix1)
        ys.append(ix2)
xs=torch.tensor(xs)
ys=torch.tensor(ys)
xenc=F.one_hot(xs,num_classes=27).float()
W=torch.randn((27,27),requires_grad=True) #random based on normal probability distribution
#forward pass
for i in range(100):
    logits=xenc@W # cross product (matrix multiplication)
    counts=logits.exp() #counts equal to N matrix above
    probs=counts/counts.sum(1,keepdims=True) #probabilities for next character
    #the last two lines are called softmax
    loss=-probs[torch.arange(len(ys)),ys].log().mean()+ 0.01*(W**2).mean() # This is L1 regularization (0.01 is the strength of regularization)  
    W.grad=None
    #backward pass
    loss.backward()
    W.data-=100*W.grad
print("loss: ",loss.item())

for i in range(5):
    out=[]
    ix=0
    while True:
        xenc=F.one_hot(torch.tensor([ix]),num_classes=27).float()
        logits=xenc@W 
        counts=logits.exp() 
        p=counts/counts.sum(1,keepdims=True)
        ix=torch.multinomial(p,num_samples=1, replacement=True).item()
        out.append(itos[ix])
        if ix==0:
            break
    print(''.join(out))
