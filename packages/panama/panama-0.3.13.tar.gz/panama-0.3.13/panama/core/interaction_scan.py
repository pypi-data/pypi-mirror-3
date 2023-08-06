import sys, os, string, pickle, copy, pdb
sys.path.append('./../../pygp')
sys.path.append('./../../')
#gplvm model
from pygp.covar import linear, noise, combinators, fixed, mu
import pygp.gp.gplvm as GPLVM
import pygp.gp.gplvm_ard as GPLVM_ARD
# customized covariance function:
from interaction_covar import *
import pygp.priors.lnpriors as lnpriors
import pygp.likelihood as lik
import linear_regression as linreg
import logging as LG
import scipy as SP
import numpy as N
from panama.utilities import fdr
import scipy.stats as st
import scipy.sparse as sparse
import testing


def scan(Y, S, X, K, pv_min, all_X, sparse_storage, interactions_iter = None, parallel = False, Njobs = 0,
	 correct_interactions = None, **kw_args):
    """sub function doing the actual scan"""

    interactions_qv, interactions_pv = None, []
    
    if not all_X:
	PV = []
	INDEX = []

	# sometimes (like when we are simulating) we don't want to store sparse QVs, so
	# let's just compute the whole thing
	if not sparse_storage:
	    PV = SP.empty((S.shape[1], Y.shape[1], X.shape[1]))
	    LODS = SP.empty((S.shape[1], Y.shape[1], X.shape[1]))

	# only for testing
	# Xt = pickle.load(open('/mnt/nicolo_storage/limmi/simulation/results/true_LVs.pickle', 'r'))
	# K = SP.dot(Xt, Xt.T)

	if K == None:
	    K = SP.zeros((Y.shape[0],Y.shape[0]))
	    
	for i in range(X.shape[1]):

	    [lod,pv_lmm] = testing.interface(S, Y, K, I = X[:,i:i+1], model = "LMM",
				       parallel = parallel,
				       jobs = Njobs, return_fields= ['lod','pv'], Ftest = True, **kw_args)

	    if sparse_storage:
		# 1. figure out which pv are < min
		Irel = pv_lmm < pv_min
		# add random number of PVs for histogram calculation etc.
		# fix: add 100,000 random PV observations
		fraction = 100000.0/Irel.size
		Irandom = SP.random.rand(Irel.shape[0],Irel.shape[1])<fraction

		# store pvalues for histograms and stuff
		interactions_pv.extend(pv_lmm[Irandom])

		pv_rel = pv_lmm[Irel]
		index = SP.nonzero(Irel)
		index_snps = index[0]
		index_genes  = index[1]
		index_factors = SP.ones_like(index_genes)*i
		index_full = SP.concatenate((index_snps[:,SP.newaxis],index_genes[:,SP.newaxis],index_factors[:,SP.newaxis]),axis=1)
		INDEX.extend(index_full)
		PV.extend(pv_rel)
	    else:
		PV[:,:,i] = pv_lmm
		LODS[:,:,i] = lod		    

	# calc effective number of tests
	n_effective_tests = X.shape[1] * Y.shape[1] * S.shape[1] * interactions_iter

	if sparse_storage:
	    #convert everything into arrays
	    PV = SP.array(PV)
	    INDEX = SP.array(INDEX)

	    QV = fdr.qvalues(PV, m = n_effective_tests, fix_lambda = pv_min)
	    QVMi = SP.concatenate((SP.array(INDEX), SP.array(QV)[:, SP.newaxis]), axis=1)

	    # use more sane types (it used to be all floats64), this 
	    dtype = N.dtype({'names':['SNP','gene', 'factor', 'qv'],
			     'formats':[N.uint,N.uint,N.uint,N.float64]})
	    QVMi = N.rec.fromarrays(QVMi.swapaxes(1,0), dtype=dtype)

	    # sort by QV
	    Is = QV.argsort()
	    QV = QV[Is]
	    INDEX = INDEX[Is]

	else:
	    QV = fdr.qvalues(PV, m = n_effective_tests)
	    QVMi = QV.min(axis=2) # minimize across factors
	    # QVMi = QV.min(axis=1) # minimize across genes


	# store qvalues
	interactions_qv = QVMi

    #return Index: snps, genes, factors
    inter_results = (interactions_pv,
		     interactions_qv) 
    
    return [INDEX,QV,inter_results]


def get_candidate_interactions(Y, S, X, K, pv_max_stored = 1.0, topn_interactions = 3, FDR_addition_interactions = 0.01, candidate_interactions = [], **kw_args):    

    #find interactions
    fit_all_X = False

    # MLM based scan
    # see details in function on meaning of index
    sparse_storage = True

    if pv_max_stored == None:
	pv_min = FDR_addition_interactions
    else:
	pv_min = pv_max_stored

    [INDEX,QV,inter_results] = scan(Y, S, X, K, pv_min, fit_all_X, sparse_storage, **kw_args)

    # QV are sorted by size already
    
    if sparse_storage:
	# starting index on those guys that are still in the game
	Iok = SP.ones(QV.shape[0],dtype='bool')

	print "Significant QVs", (QV < FDR_addition_interactions).sum()

	# find new candidate guys to append:
	new_candidate_interactions = []
	# iteratively cycle throug best SNP and factor
	while True:

	    # only add the top n interactions
	    if len(new_candidate_interactions) == topn_interactions:
		break

	    # check still candidates in the game
	    if not Iok.any():
		break

	    # take the current best guy (they are ordered)
	    ic = SP.nonzero(Iok)[0][0]

	    qvm = QV[ic]
	    if qvm > FDR_addition_interactions:
		#break if best guy worse than cutoff
		break

	    # get factor/snp index
	    [i_snp,i_gene,i_factor] = INDEX[ic]

	    # append to candidates
	    new_candidate_interactions.append((i_factor, i_snp))

	    # adjust IOK to skip that factor and SNP in followup rounds
	    i_bad_snp = (INDEX[:,0] == i_snp)
	    i_bad_factor = (INDEX[:,2] == i_factor)

	    # Iok[i_bad_snp | i_bad_factor] = False
	    Iok[i_bad_snp] = False

	    print "Remaining sign. QVs: ", (QV[Iok] < FDR_addition_interactions).sum()
    else:
	# set QV for SNPS that are already in candidates to 1
	# if len(candidate_interactions) != 0:
	#    interacting_SNPs = SP.array(candidate_interactions)[:, 1]
	#    QV[interacting_SNPs,:] = 1

	QV = QV.min(axis=1) # minimize across genes
	new_candidate_interactions = []
	#iteratively cycle throug best SNP and factor

	while True:
	    # only add the top n interactions
	    if len(new_candidate_interactions) == topn_interactions:
		break

	    # find best factor/snp combination
	    qvm = QV.min()
	    qvmw = SP.where(QV==qvm)
	    
	    if qvm > FDR_addition_interactions:
		#break if no one left
		break

	    # factor/snp index
	    [i_snp,i_factor] = [qvmw[0][0],qvmw[1][0]]


	    # this could be useful in the case of LD (blanks region)
	    # low_snp = max(0, i_snp-10)
	    # hi_snp = min(i_snp+10, self.snps.shape[1])	    
	    # QV[low_snp:hi_snp,:] = 1.

	    # remove from QV table
	    QV[i_snp,:] = 1.
	    QV[:,i_factor] = 1.

	    # append to candidates
	    new_candidate_interactions.append((i_factor, i_snp))

    Nint_new = len(new_candidate_interactions)
    Nint_old = len(candidate_interactions)
    print new_candidate_interactions
    candidate_interactions.extend(new_candidate_interactions)
    LG.info("Interaction candidates: %d, added %d" % (Nint_old, Nint_new))
    
    return Nint_new, candidate_interactions, inter_results

