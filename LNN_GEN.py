#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 14:01:21 2020
@author: fabien
"""

import torch, torch.nn as nn
import numpy as np

################################ PARAMETER
I,O = 5,5
D = 5; R = np.random.randint(D)
batch_size = 10

################################ First GEN
# First Net : 'Index','NbNeuron','NbConnect','x','y','listInput'
Net = np.array([[-1, O, 2,  D, 0, []],
                [ 0, I, I, -1, 0, []],
                [ 1, 1, 1,  R, R, []]])
# Adjacency in Net
for n in Net :
    connect = []
    if n[3] == -1 : connect = [[-1,-1]]
    else :
        loc = Net[Net[:,3] < n[3]][:,0]
        for i in range(n[2]):
            idx_ = loc[np.random.randint(len(loc))]
            c_out = np.random.randint(int(Net[Net[:,0] == idx_, 2]))
            connect += [[idx_, c_out]]
    n[-1] = connect

################################ Custom neural network
class Network(nn.Module):
    def __init__(self, Net):
        super().__init__()
        self.Net = Net
        self.Layers = nn.ModuleList([nn.Sequential(nn.Linear(n[2], n[1]), nn.ReLU()) for n in self.Net])
        self.trace = Net.shape[0]*[[]]
        
    def forward(self,x):
        self.trace = self.Net.shape[0]*[[]]
        order = np.argsort(self.Net[:, 3])
        for i in range(len(order)) :
            idx = order[i]
            if i == 0 : x = self.Layers[idx](x)
            else :
                tensor = []
                for j,k in self.Net[idx, -1] :
                    idx_ = np.where(Net[:,0] == j)[0][0]
                    tensor += [self.trace[idx_][:,None,k]]
                tensor_in = torch.cat(tensor, dim=1)
                x = self.Layers[idx](tensor_in)
            self.trace[idx] = x
        return x

##### XOR Fit Part
X = np.mgrid[0:batch_size,0:I][1]
y = 1*np.logical_xor(X < 3, X > 5)

# Convert to tensor
X, y = torch.tensor(X, dtype=torch.float), torch.tensor(y, dtype=torch.float)

# Model init
model = Network(Net)
criterion = torch.nn.MSELoss(reduction='sum')
optimizer = torch.optim.SGD(model.parameters(), lr=1e-6)
# Training Loop
for t in range(1000):
    # Forward pass: Compute predicted y by passing x to the model
    y_pred = model(X)

    # Compute and print loss
    loss = criterion(y_pred, y)
    if t % 100 == 99:
        print(t, loss.item())

    # Zero gradients, perform a backward pass, and update the weights.
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

##### XOR Predict Part
y_pred = model(X)
print(y,y_pred)
