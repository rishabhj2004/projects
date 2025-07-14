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
block_size=3

# creating traing testing and validation dataset
def buildDataset(words):
    block_size=3
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

C=torch.randn(27,10) #for 10 dimensions
W1=torch.randn(30,300) #300 neurons for the first hidden layers (30 coz 3*10)
B1=torch.randn(300)
W2=torch.randn(300,27) #300 inputs and 27 outputs
B2=torch.randn(27)
parameters=[C,W1,W2,B1,B2]

for p in parameters:
    p.requires_grad=True

stepi=[]
lossi=[]
lr=0.1

for i in range(200000): #we need to code decay learning rate
    #minibatch
    ix=torch.randint(0,Xtrain.shape[0],(60,)) #32 is the batch size
    #forward pass
    emb=C[Xtrain[ix]]
    h=torch.tanh(emb.view(-1,30) @ W1 + B1)
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

plt.plot(stepi,lossi)

emb=C[XVal]
h=torch.tanh(emb.view(-1,30) @ W1 + B1)
logits=h @ W2 +B2
loss=F.cross_entropy(logits,YVal)
print("Validation loss: ",loss.item())

# for sampling
for _ in range(20):
    out=[]
    Context=[0]*block_size
    while True:
        emb=C[torch.tensor([Context])]
        h=torch.tanh(emb.view(-1,30) @ W1 + B1)
        logits=h @ W2 +B2
        probs=F.softmax(logits,dim=1)
        ix=torch.multinomial(probs,num_samples=1).item() #choosing by probability
        out.append(ix)
        Context=Context[1:]+[ix]
        if ix==0:
            break
    print("".join(itos[i] for i in out))
