#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:42:20 2021
@author: fabien
"""

import torch, torch.nn as nn
import numpy as np

from Q_AGENT import Q_AGENT

import pylab as plt

### PARAMETER PART
TEST = True

### FUNCTION PART
def DRAW_NETWORK(net_graph,in_):
    global neuron_in, neuron_out
    ## Generate layer node
    # TRIPLET : (IDX, X, INDEX_ = Y)
    neuron_in, neuron_out = [], []
    # Input part :
    for n in range(in_):
        neuron_out += [[0,0,n]]
    # Layering
    for n in net_graph :
        # input part
        for n_ in range(n[2]) :
            neuron_in  += [[n[0],n[3]-0.25,n_]]
        # output part
        for n_ in range(n[1]) :
            neuron_out  += [[n[0],n[3]+0.25,n_]]
    neuron_in, neuron_out = np.array(neuron_in), np.array(neuron_out)
    ## Connect each Node
    for n in net_graph :
        i = 0
        for n_ in n[-1] :
            connect_a = [n[3]-0.25, i]
            idx = np.where((n_ == neuron_out[:, 0::2]).all(axis=1))[0]
            connect_b = neuron_out[idx][:,1:]
            X = np.concatenate((np.array([connect_a]), connect_b))
            if X[0,0] > X[1,0] :
                plt.plot(X[:,0], X[:,1], 'k', lw=1, alpha=0.9)
            else :
                plt.plot(X[:,0], X[:,1], 'r', lw=2, alpha=0.7)
            # increment
            i+=1
    ## Polygon neuron draw
    idx = np.unique(neuron_out[:,0])
    for i in idx :
        in_idx = np.where(i == neuron_in[:,0])[0]
        out_idx = np.where(i == neuron_out[:,0])[0]
        if in_idx.shape == (0,) :
            x, y = np.max(neuron_out[out_idx,1:], axis=0)
        else :
            x_i, y_i = np.max(neuron_in[in_idx,1:], axis=0)
            x_o, y_o = np.max(neuron_out[out_idx,1:], axis=0)
            x, y = np.mean((x_i, x_o)), np.max((y_i, y_o))
        # fill between polygon
        plt.fill_between([x-0.5,x+0.5], [y+0.5,y+0.5], -0.5, alpha=0.5)
    ## Plot the graph-network
    plt.scatter(neuron_in[:,1], neuron_in[:,2], s=10); plt.scatter(neuron_out[:,1], neuron_out[:,2], s=30)
    #plt.savefig('NETWORK.svg'); plt.show(); plt.close()

def MODEL_BASIC(net_rnn, io):
    # regression type (MSE)
    criterion = nn.MSELoss(reduction='sum')
    optimizer = torch.optim.SGD(net_rnn.parameters(), lr=1e-6)
    # Training Loop
    for t in range(5):
        # randomised IO
        X = torch.randn(batch_size,io[0])
        y = torch.randn(batch_size,io[1])
        # Forward pass: Compute predicted y by passing x to the model
        y_pred = net_rnn(X)
        ############print(y_pred)
        # Compute and print loss
        loss = criterion(y_pred, y)
        ############print(t, loss.item())
        # Zero gradients, perform a backward pass, and update the weights.
        optimizer.zero_grad()
        loss.backward()#retain_graph=True)
        optimizer.step()
    return None

def MODEL_ENV(AGENT, train_size):
    for n in range(train_size) :
        # Basic Env Gen
        IMG = np.random.random((batch_size,MAP_SIZE,MAP_SIZE))
        POS = np.random.randint(0,MAP_SIZE,2)
        # Memory
        x = POS[None].copy()
        # first step
        In_COOR = np.mod(POS + AGENT.X, MAP_SIZE)
        new_state = IMG[0][In_COOR[:,0],In_COOR[:,1]][None]
        # Loop
        i, DONE = 1, False
        for img in IMG[1:] :
            # new input
            prev_state = new_state.copy()
            # Action
            action = AGENT.ACTION(prev_state)
            action_coor = AGENT.Y[action]
            # position update
            POS = np.mod(POS + action_coor, MAP_SIZE)
            # memory
            x = np.concatenate((x,POS[None].copy()), axis=0)
            # step reward
            reward = np.random.randint(-1,2)
            # Input update
            In_COOR = np.mod(POS + AGENT.X, MAP_SIZE)
            new_state = img[In_COOR[:,0],In_COOR[:,1]][None]
            # DONE
            i += 1
            if i == batch_size : DONE = True
            # Memory update
            AGENT.SEQUENCING(prev_state,action,new_state,reward,DONE)
        # Reinforcement learning
        AGENT.OPTIM()
    # last move
    plt.scatter(x[[0,-1],0],x[[0,-1],1], c="k")
    plt.plot(x[:,0],x[:,1], c="k")
    plt.imshow(IMG[0]); plt.show()

def ROTATION_3(X_CENTER, NEW_CENTER) :
    THETA = np.linspace(np.pi/2, (3./2)*np.pi, 3)
    X_ROTATED = []
    for t in THETA :
        # rotation matrix
        r = np.array(( (np.cos(t), -np.sin(t)),(np.sin(t),  np.cos(t)) ))
        # rotation
        X_ROT = r.dot(X_CENTER.T)
        # increment
        X_ROTATED += [np.rint(X_ROT.T).astype(int) + NEW_CENTER]
    return X_ROTATED
    
### TESTING PART
if TEST :
    # Parameter
    IO = (9,3)
    NB_P_GEN = 2
    batch_size = 16
    MAP_SIZE = 12
    N_TIME = 12
    NB_GEN = 9
    
    ARG_TUPLE = (IO,NB_P_GEN, batch_size, MAP_SIZE, N_TIME, NB_GEN)
    ## Init
    AGENT = Q_AGENT(*ARG_TUPLE[:-1])
    
    ############### plot neuron list
    NET_GRAPH = AGENT.NEURON_LIST
    DRAW_NETWORK(NET_GRAPH,IO[0])
    
    ############### training test
    NET_RNN = AGENT.MODEL
    
    ### basic-training
    #MODEL_BASIC(NET_RNN, IO)

    ### q-training
    #MODEL_ENV(AGENT, 10)
    
    ### Mutation
    NEW_AGENT = AGENT.LAUNCH_MUTATION()
    """
    COP_GRAPH = GRAPH_EAT(None,[IO, NET_GRAPH.copy(), AGENT.NET.LIST_C.copy()])
    NEW_GRAPH = NEW_GRAPH.NEXT_GEN(4)
    print(COP_GRAPH.NEURON_LIST)
    print(NEW_GRAPH.NEURON_LIST)

    """
    ############### plot new neuron list
    NEW_NET_GRAPH = NEW_AGENT.NEURON_LIST
    
    print(NET_GRAPH)
    print(NEW_NET_GRAPH)
    
    DRAW_NETWORK(NEW_NET_GRAPH,IO[0])
    
    ############### density IO
    INPUT_D = np.zeros((5,5))
    OUTPUT_D = np.zeros((3,3))
    
    X_ = NEW_AGENT.X
    Y_ = NEW_AGENT.Y
    
    X = X_ + [2,2]
    Y = Y_ + [1,1]
    
    INPUT_D[tuple(map(tuple, X.T))] += 1
    OUTPUT_D[tuple(map(tuple, Y.T))] += 1
    
    plt.close(); plt.imshow(INPUT_D); plt.show()
    
    # rotation
    X_ROT = ROTATION_3(X_, [2,2])
    
    for x in X_ROT :
        INPUT_D[tuple(map(tuple, x.T))] += 1
    
    # normalisation
    INPUT_D = INPUT_D/INPUT_D.sum()
    OUTPUT_D = OUTPUT_D/OUTPUT_D.sum()
    
    plt.close(); plt.imshow(INPUT_D); plt.show()

"""
################################ XOR FIT
X = np.mgrid[0:batch_size,0:I][1]
y = 1*np.logical_xor(X < 3, X > 5)

# Convert to tensor
X, y = torch.tensor(X, dtype=torch.float), torch.tensor(y, dtype=torch.float)

"""