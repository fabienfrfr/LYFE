#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 10 16:19:36 2021

@author: fabien
"""

import numpy as np

from GRAPH_GEN import GRAPH

import copy

################################ GRAPH Evolution Augmenting Topology
class GRAPH_EAT(GRAPH):
    def __init__(self, GEN_PARAM, NET):
        if GEN_PARAM != None :
            # first generation
            NB_P_GEN, I, O, P_MIN = GEN_PARAM
            #Inheritance of Graph_gen
            super().__init__(NB_P_GEN, I, O, P_MIN)
        else : 
            self.IO, self.NEURON_LIST, self.LIST_C = NET
        
    def NEXT_GEN(self, MUT = None):
        # copy of module (heritage)
        IO, NEURON_LIST, LIST_C = self.IO, copy.deepcopy(self.NEURON_LIST), copy.deepcopy(self.LIST_C)
        # adding mutation (variation)
        if MUT == None :
            MUT = np.random.choice(5, p=4*[0.225]+[0.1])
        #print('Mutation type : '+str(MUT))
        if MUT == 0 :
            # add connection
            NEURON_LIST = self.ADD_CONNECTION(NEURON_LIST, LIST_C)
        elif MUT == 1 :
            # add neuron
            NEURON_LIST, LIST_C = self.ADD_NEURON(NEURON_LIST)
        elif MUT == 2 :
            # add layers
            NEURON_LIST, LIST_C = self.ADD_LAYERS(NEURON_LIST, LIST_C)
        elif MUT == 3 :
            # cut doublon connect neuron
            NEURON_LIST = self.CUT_CONNECTION(NEURON_LIST)
        elif MUT == 4 :
            # cut neuron
            NEURON_LIST, LIST_C = self.CUT_NEURON(NEURON_LIST, LIST_C)
        # return neuronList with mutation or not
        return GRAPH_EAT(None,[IO, NEURON_LIST.copy(), LIST_C.copy()])
    
    ### MUTATION PART
    def ADD_CONNECTION(self, NEURON_LIST, LIST_C) :
        # add Nb connect
        idx = np.random.randint(NEURON_LIST.shape[0])
        NEURON_LIST[idx,2] += 1
        # add element list
        idx_ = np.random.randint(LIST_C.shape[0])
        NEURON_LIST[idx,-1] += [LIST_C[idx_, 1:].tolist()]
        return  NEURON_LIST

    def ADD_NEURON(self, NEURON_LIST):
        NB_LAYER = NEURON_LIST[:,0].max()
        # add neuron in one layers
        if NB_LAYER == 1 : IDX_N = 1
        else : IDX_N = np.random.randint(1,NB_LAYER)
        NEURON_LIST[IDX_N,1] += 1
        idx_new, idx_c_new = NEURON_LIST[IDX_N,0], NEURON_LIST[IDX_N,1]-1
        # add connection
        IDX_C = np.random.randint(NB_LAYER)
        NEURON_LIST[IDX_C, 2] += 1
        NEURON_LIST[IDX_C,-1] += [[idx_new, idx_c_new]]
        # update list_connection
        LIST_C = self.LISTING_CONNECTION(NEURON_LIST.shape[0]-1, NEURON_LIST[:,:-1])
        return NEURON_LIST, LIST_C

    def ADD_LAYERS(self, NEURON_LIST, LIST_C):
        # new one neuron layers (erreur ne doit pas etre au meme endroit)
        idx_new = NEURON_LIST[:,0].max() + 1
        POS_X_new = np.random.randint(1,NEURON_LIST[:,3].max())
        NEW_NEURON = np.array([idx_new, 1, 1, POS_X_new, []])
        # connection of new neuron input
        IDX_C = np.where(LIST_C[:,0] < POS_X_new)[0]
        idx_c = IDX_C[np.random.randint(IDX_C.shape[0])]
        list_c = LIST_C[idx_c, 1:] ; #print(list_c)
        NEW_NEURON[-1] = [list(list_c)]
        # adding connection of downstream neuron (REVOIR : car pas necessaire de vers l'avant, ne doit pas etre au meme endroit c'est tout! )
        IDX_N = np.where(NEURON_LIST[:,3] > POS_X_new)[0]
        idx_n = IDX_N[np.random.randint(IDX_N.shape[0])]
        NEURON_LIST[idx_n, 2] += 1
        NEURON_LIST[idx_n, -1] += [[idx_new, 0]]
        # add layers and update list
        NEURON_LIST = np.concatenate((NEURON_LIST,NEW_NEURON[None]), axis=0)
        LIST_C = self.LISTING_CONNECTION(NEURON_LIST.shape[0]-1, NEURON_LIST[:,:-1])
        return NEURON_LIST, LIST_C
    
    def CUT_CONNECTION(self, NEURON_LIST):
        # listing of connection
        CONNECT_DATA = self.CONNECTED_DATA(NEURON_LIST)
        # choose connect duplicate (doublon : ! min connect, otherwise : return)
        c_u, ret = np.unique(CONNECT_DATA[:,2:], axis=0, return_counts=True)
        idx_doublon = np.where(ret > 1)[0]
        if idx_doublon.shape == (0,) :
            return NEURON_LIST
        c_2_cut = c_u[idx_doublon[np.random.randint(len(idx_doublon))]]
        # find cut connection (! 1st link : vestigial, otherwise : return)
        IDX_CD = np.where((CONNECT_DATA[:,1] !=0)*(CONNECT_DATA[:,2:] == c_2_cut).all(axis=1))[0]
        if IDX_CD.shape == (0,) :
            return NEURON_LIST
        idx_cd = IDX_CD[np.random.randint(IDX_CD.shape)][0]
        idx, idx_ = CONNECT_DATA[idx_cd, :2]
        # update neuronlist
        IDX = np.where(NEURON_LIST[:,0] == idx)[0]
        NEURON_LIST[IDX,2] -= 1
        del(NEURON_LIST[IDX,-1][0][int(idx_)])
        return NEURON_LIST
    
    def CUT_NEURON(self, NEURON_LIST, LIST_C):
        # listing of connection
        CONNECT_DATA = self.CONNECTED_DATA(NEURON_LIST)
        ## find possible neuron (no ones connection)
        c_n, ret = np.unique(CONNECT_DATA[:,0], return_counts=True)
        idx_ones = c_n[np.where(ret == 1)[0]]
        # ones verif
        if idx_ones.shape[0] != 0 :
            # select index
            bool_o  = np.any([CONNECT_DATA[:,0] == i for i in idx_ones], axis = 0)
            C = CONNECT_DATA[bool_o,2:]
            # select doublon
            bool_o_ = np.any([(CONNECT_DATA[:,2:] == d).all(axis=1) for d in C], axis=0)
            # choose neuron
            C_ = CONNECT_DATA[np.invert(bool_o_), 2:]
        else :
            # choose neuron
            C_ = CONNECT_DATA[:, 2:]
        # delete input
        C_ = C_[C_[:,0] != 0]
        # return if no connection
        if C_.shape[0] == 0 :
            return NEURON_LIST, LIST_C
        # choise index (REVOIR : ne pas choisir la premiere connection ??? pour garder un lien entre l'entrée et la sortie)
        idx, idx_ = C_[np.random.randint(C_.shape[0])]
        IDX = np.where(NEURON_LIST[:,0] == idx)[0]
        # return if no neuron
        NEW_NB_NEURON = NEURON_LIST[IDX, 1] - 1
        if NEW_NB_NEURON == 0 :
            return NEURON_LIST, LIST_C
        # remove one neuron number
        NEURON_LIST[IDX, 1] = NEW_NB_NEURON
        #print(idx, idx_)
        # update list of neuron
        for n in NEURON_LIST :
            list_c = np.array(n[-1])
            # boolean element
            egal = (list_c == [idx, idx_]).all(axis=1)
            sup_ = (list_c[:,0] == idx) * (list_c[:,1] >= idx_)
            # change connection (permutation)
            if sup_.any() :
                list_c[sup_,1] -= 1
                list_c = list_c[np.invert(egal)]
            # update neuronlist
            n[-1] = list_c.tolist()
            n[2] = len(n[-1])
        # update connection list
        LIST_C = self.LISTING_CONNECTION(NEURON_LIST.shape[0]-1, NEURON_LIST[:,:-1])
        return NEURON_LIST, LIST_C
    
    def CONNECTED_DATA(self, NEURON_LIST):
        CONNECT_DATA = []
        for n in NEURON_LIST :
            idx = n[0]*np.ones((n[2],1))
            idx_ = np.arange(n[2])[:,None]
            c = np.array(n[-1])
            CONNECT_DATA += [np.concatenate((idx,idx_,c),axis=1)]
        CONNECT_DATA = np.concatenate(CONNECT_DATA)
        return CONNECT_DATA
