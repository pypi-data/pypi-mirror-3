import numpy as np
import scipy as SP
import pdb, sys, pickle
import scipy.linalg
import scipy.linalg as LA
from multiprocessing import Process, Pool
import logging as LG
import linear_regression
sys.path.append(".")
import os
#from IPython.kernel import client

def pinv(x,regulariser=None):
    if regulariser==None:
	return SP.linalg.pinv(x)
    else:
        return (SP.dot(SP.linalg.inv(SP.dot(x.T,x)  + regulariser*SP.eye(x.shape[1])),x.T))

def mlreg(X,Z,missing=None, regulariser = None):
    """ Maximum Likelihood REGression method that is widely used by other classes"""
    if missing is None: missing = SP.zeros(X.shape[0], bool)
    phiI = pinv(X[~missing,:], regulariser = regulariser) 
    return SP.dot(phiI,Z[~missing]).T


def mlpred(X,Z,missing=None, return_W=False):
    if missing is None: missing = SP.zeros(X.shape[0], bool)
    wml = mlreg(X,Z,missing)
    if return_W: return (SP.dot(X[~missing], wml.T), wml)
    else: return SP.dot(X[~missing], wml.T)


def lod(X,Z, miss=None, returnPred=False, covs=None):
    if miss is None: miss = SP.zeros(X.shape[0], bool)
    X = X[~miss]
    Z = Z[~miss]
    Z1 = Z2 = None

    # compute residuals and variances for the nested models
    if covs is None:
        Z1 = Z
        Z2 = Z1 - mlpred(X, Z1)
    else:
        covs = covs[~miss]
        Z1 = Z - mlpred(covs, Z)
        Z2 = Z - mlpred(SP.concatenate((X.T, covs.T)).T, Z)

    V1 = Z1.var(axis=0)
    V2 = Z2.var(axis=0)

    # compute log-odds for both
    LLbg = -X.shape[0]/2*(SP.log(V1*(2*SP.pi))) - 1/(2*V1)*((Z1**2).sum(axis=0))
    LL   = -X.shape[0]/2*(SP.log(V2*(2*SP.pi))) - 1/(2*V2)*((Z2**2).sum(axis=0))

    if not returnPred: return LL - LLbg
    else: return (LL-LLbg, Z - Z2)


def lod2fdr(lod):
    """calculate fdr estimate from likelihood ratio scores
    somewhat a hack but works ok"""
    score = -SP.log(1 + SP.exp(lod))
    return SP.exp(score)
        
def run_associations(Y,X,covs):
    [Ny, N] = Y.shape

    Nx = X.shape[1]

    lods = SP.zeros([Nx, N])

    #add mean column:
    if covs is None: covs = SP.ones([Ny,1])

    for a in xrange(Nx):
        lods[a,:] = lod(X[:,a:a+1],Y,covs=covs)

    return lods

def run_interact(Y, intA, intB, covs,max=False):
    """ Calculate log-odds score for the nested model of including a multiplicative term between intA and intB into the additive model """
    [Ny, N] = Y.shape

    Na = intA.shape[1] # number of interaction terms 1
    Nb = intB.shape[1] # number of interaction terms 2

    # for each snp/gene/factor combination, run a lod
    # snps need to be diced bc of missing values - iterate over them, else in arrays
    lods = SP.zeros([Na, Nb, N])

    #add mean column:
    if covs is None: covs = SP.ones([Ny,1])

    # for each pair of interacting terms
    for a in range(Na):
        for b in range(Nb):
            # calculate additive and interaction terms
            C = SP.concatenate((covs.T, intA[:,a:a+1].T, intB[:,b:b+1].T)).T
            X = intA[:,a:a+1]*intB[:,b:b+1]
            lods[a,b] = lod(X, Y[:,:], covs=C[:,:])        
    if max:
        lods = lods.max(axis=2)
    return lods

    
def run_interact_parallel(Y, intA, intB, covs,max=False,Njobs=5):
    """ Calculate log-odds score for the nested model of including a multiplicative term between intA and intB into the additive model """
    [Ny, N] = Y.shape

    Np = Y.shape[1]    # number of phenotypes
    Na = intA.shape[1] # number of interaction terms 1
    Nb = intB.shape[1] # number of interaction terms 2

    # Ipython conf
    tc = client.TaskClient()
    mec = client.MultiEngineClient()
    eng_ids = mec.get_ids()
    assert eng_ids > 0, "No engine started"	
    assert eng_ids > Njobs, "Not enough engines for the number of jobs required"

    #linear_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linear_regression.py")
    lmm_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lmm/lmm_fast.py")
    mec.run(lmm_file)
    #mec.run(linear_file)

    # for each snp/gene/factor combination, run a lod
    # snps need to be diced bc of missing values - iterate over them, else in arrays
    if max:
        lods = SP.zeros([Na, Nb])
    else:
        lods = SP.zeros([Na, Nb, N])
        
    Isplit = SP.array(SP.linspace(0,Na,Njobs+1),dtype='int')

    jobs = []
    for n in xrange(Njobs):
        i0 = Isplit[n]
        i1 = Isplit[n+1]
        intA_= intA[:,i0:i1]
	full_args = (Y, intA_, intB, covs, max)
	job = client.MapTask(run_interact, args=full_args)
	jobs.append(tc.run(job))
	
    tc.barrier(jobs)
    
    #slot results back in:
    for n in xrange(Njobs):
        i0 = Isplit[n]
        i1 = Isplit[n+1]
        lods[i0:i1] = tc.get_task_result(jobs[n])
    
    return lods
