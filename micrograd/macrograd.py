import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import math
import random

class Value:
    def __init__(self,data=0,children=(),op=''): 
        self.data=data
        self.children=set(children) #just so that we can keep track of what values are being operated
        self.op=op # keeps track of operation being performed
        self.grad=0.0
        self._backward= lambda : None
        
    def __repr__(self):
        return f"Value(data={self.data})"
        
    def __add__(self,other): #this __add__ just means that whenever two objects are sent with addition in mind (instead of just one parameter) it wont just create the data obj but will add the values of the two objs sent and will create a new obj data
        other= other if isinstance(other,Value) else Value(other) #if other is not an object we wrap it into an object
        out=Value(self.data+other.data,(self,other),'+') 
        def _backward():
            self.grad+=1*out.grad
            other.grad+=1*out.grad
        out._backward=_backward
        return out

    def __radd__(self,other):
        return self+other

    def __neg__(self):
        return self*(-1)

    def __sub__(self,other):
        return self+(-other)

    def __rsub__(self, other):
        return Value(other - self.data)
        
    def __mul__(self,other):
        other= other if isinstance(other,Value) else Value(other)
        out=Value(self.data*other.data,(self,other),'*')
        def _backward():
            self.grad += other.data*out.grad
            other.grad += self.data*out.grad
        out._backward =_backward
        return out

    def __rmul__(self,other):
        return self*other

    def __truediv__(self,other):
        return self*other**(-1)

    def __rtruediv__(self, other):
        return Value(other) * self**(-1)

    def exp(self):
        x=self.data
        out=Value(math.exp(x),(self,),'exp')
        def _backward():
            self.grad+=out.data*out.grad
        out._backward=_backward
        return out
        
    def tanh(self):
        x=self.data
        t= (math.exp(x*2)-1)/(math.exp(x*2)+1)
        out=Value(t,(self,),'tanh')
        def _backward():
            self.grad+=(1-t**2)*out.grad
        out._backward=_backward
        return out

    def relu(self):
        out = Value(0 if self.data < 0 else self.data, (self,), 'ReLU')
        def _backward():
            self.grad += (out.data > 0) * out.grad
        out._backward = _backward
        return out

    

    def log(self):
        x = self.data
        out = Value(math.log(x), (self,), 'log')
        def _backward():
            self.grad += (1 / x) * out.grad
        out._backward = _backward
        return out

    def __pow__(self,other):
        assert isinstance(other,(int,float))
        out=Value(self.data**other,(self,),f'**{other}')
        def _backward():
            self.grad+=other*(self.data**(other-1))*out.grad
        out._backward=_backward
        return out

    def backward(self):
        topo = []
        visited = set()

        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v.children:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        self.grad = 1.0  
        for node in reversed(topo):
            node._backward()
            

class Neuron:
    def __init__(self,nin):
        self.w=[Value(random.uniform(-1,1)) for _ in range(nin)] # uses random weights from -1 to 1 for each input(nin)
        self.b=Value(random.uniform(-1,1)) #random bias

    def __call__(self,x):
        act=sum((wi*xi for wi,xi in zip(self.w,x)),self.b)
        out=act.tanh()
        return out

    def parameters(self):
        return self.w+[self.b]

class Layer:
    def __init__(self,nin,nout):
        self.neurons=[Neuron(nin) for i in range(nout)]
    def __call__(self,x):
        outs=[n(x) for n in self.neurons]
        return outs[0] if len(outs)==1 else outs
    def parameters(self):
        params=[]
        for neuron in self.neurons:
            ps=neuron.parameters()
            params.extend(ps)
        return params

class MLP:
    def __init__(self,nin,nouts):
        sz=[nin]+nouts
        self.layers=[Layer(sz[i],sz[i+1]) for i in range(len(nouts))]

    def __call__(self,x):
        for layer in self.layers:
            x=layer(x)
        return x

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]
