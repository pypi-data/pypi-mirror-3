# -*- coding: utf-8 -*-
"""
Created on Wed Nov 16 14:25:50 2011

@author: Sat Kumar Tomer
@website: www.ambhas.com
@email: satkumartomer@gmail.com
"""
from __future__ import division
import numpy as np
from ambhas.err import L

class GW_1D():
    """
    This class perform the groundwater modelling
    """
    
    def __init__(self, R, Dnet=0):
        """
        R: rainfall
        Dnet: net groundwater draft
        """
        self.R = R
        self.Dnet = 0
        
    def set_parameters(self, F, G, r, hmin=0):
        """
        F: model parameter
        G: model parameter
        r: recharge factor
        hmin: groundwater level at which based flow ceases
        
        sy: specific yield
        lam: decay constant
        """
        self.F = F
        self.G = G
        self.r = r
        self.hmin = hmin
        
        self.lam = (1-F)**2/G
        self.sy = (1-F)/G
            
    def run_model(self, hini, t):
        """
        hini: initial groundwater level
        t: time
        """
        u = self.r*self.R-self.Dnet # net input
        
        h = np.empty(t+1) # create empty array
        h[0] = hini  - self.hmin       # set the initial condition
                
        for k in range(t):
            h[k+1] = self.F*h[k] + self.G*u[k]
            
            
        self.h = h + self.hmin
    
    def ens(self, F_lim, G_lim, r_lim, hmin_lim, ens, hini, h_obs, t):
        """
        generate ensemble based on ensemble of parameters
        Input:
            F: min and max of F
            G: min and max of G
            r: min and max of r
            hmin: min and max of hmin
            ens: no. of ensembles
            hini: initial gw level
            t: final time
        """
        F_ens = F_lim[0] + (F_lim[1]-F_lim[0]) * np.random.rand(ens)
        G_ens = G_lim[0] + (G_lim[1]-G_lim[0]) * np.random.rand(ens)
        r_ens = r_lim[0] + (r_lim[1]-r_lim[0]) * np.random.rand(ens)
        hmin_ens = hmin_lim[0] + (hmin_lim[1]-hmin_lim[0]) * np.random.rand(ens)
        
        self.NS = np.empty(ens)
        for i in range(ens):
            self.set_parameters(F_ens[i], G_ens[i], r_ens[i], hmin_ens[i])
            self.run_model(hini, t)
            self.NS[i] = NS(self.h, h_obs[:t+1])
   
#if __name__ == "__main__":
#    # forcing
#    R = np.random.rand(100)
#    foo = GW_1D(R)
#    
#    # parameter
#    F = 0.8
#    G = 10
#    r = 0.1
#    #foo.set_parameters(F, G, r)
#    
#    # initial condition
#    h_ini = 10
#    
#    # run the model    
#    #foo.run_model(h_ini, 100)
#    
#    # get the simulated data
#    #h_sim = foo.h
#    
#    # ensemble
#    h_obs = np.random.rand(101)
#    foo.ens([0.5, 1.0], [1, 20], [0, 0.2], [50,70], 10, 20, h_obs, 10)
#    print(foo.NS)
    
    
    