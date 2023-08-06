import os, sys, cPickle, pdb
sys.path.append('./../../pygp/')
sys.path.append("./../../")
import linear_regression as linreg
import scipy as SP
import numpy as N
import numpy.random as random
import scipy.stats as st
from panama.utilities import mkl
from panama.utilities import fdr
from panama.utilities import io_wrapper as pw
from panama.core.gpasso_joint import *
import logging as LG

try:
    from panama.tests.other_models import sva
    from panama.tests.other_models import ice    
    import panama.tests.other_models.peer.vbfa as VBFA
except ImportError:
    pass

from panama.utilities.plot_parameters import *
file_type = "hdf5"


def save_everything(qv, pv, dir_name, name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    pw.write((qv, pv), os.path.join(dir_name,name), file_type)


def PANAMA(expr, snps, model = "default", tf_correction = False, pop_struct = False,
	   write_files = False, dump_asso_object = False, verbose_plots = False,
	   dir_name = "./", statistics = False, parallel = True,
	   jobs = 2, return_asso_object = False, max_train_iter = 10, **kw_args):

    if model == "default":
	panama_model = "gplvm"
    else:
	panama_model = "gplvm_interact"

    if dir_name != None and verbose_plots:
	verbose_dir = os.path.join(dir_name,'verbose_plots')
	if not os.path.exists(verbose_dir):
	    os.makedirs(verbose_dir)
    else:
	verbose_dir = None
	
    Kpop = None
    if type(pop_struct) != type(True): # if it's not a boolean
	assert pop_struct.shape[0] == pop_struct.shape[1], "Kpop must be NxN"
	assert pop_struct.shape[0] == expr.shape[0], "Kpop must be NxN, Y should be NxD"	
	
	Kpop = pop_struct # use the matrix
	pop_struct = True # this is needed (see assignment pop_cf = pop_struct)	
    elif pop_struct: # if it's true but no Kpop is provided, compute it
	Kpop = SP.cov(snps)
     

    asso = GPLVMassoJ(gplvm_init = "randn",
		      model = panama_model,
		      mean_cf = True,
		      pop_cf = pop_struct,
                      asso_method = 'LMM',
                      parallelize= parallel,
		      ard = True,
                      Njobs = jobs,
		      verbose_plot_dir=verbose_dir,
		      Kpop = Kpop,
                      **kw_args
                      )

    asso.add_interactions = False # TEMPORARY
    asso.setData(snps=snps,pheno=expr,normalize_geno=False, normalize_pheno = False)
    asso.train(Niter=max_train_iter,maxiter=1E5,Nrestarts=1,gradcheck=False, diagnostics=False)
    
    if dump_asso_object:
	if not os.path.exists(dir_name):
	    os.makedirs(dir_name)
	# backend is "pickle" because hdf5 can't serialize objects
	pw.write(asso, os.path.join(dir_name,"asso_object"), "pickle")
	objects_dir = os.path.join(dir_name,"objects/")
	pw.write(asso.getLatent(ard_reweight=True,
				pca_rotation=True,
				rotate_varimax = False),
		 os.path.join(objects_dir,"PANAMA_factors"), file_type)

    
    if parallel:
	# Don't use multithreaded scipy, we are going to parallelize and we need the cores    
	mkl.set_num_threads(1)

    qv, pv = asso.getAssociations()
    # qv_inter, pv_inter = asso.getInteractions()

    if statistics:
	LG.info("Associations: %d" % (qv<0.05).sum())
	gc = fdr.estimate_lambda(pv)
	LG.info("Genomic control: %.4f" % (gc))

    if tf_correction:
	# set to None to force recalc
	asso.QV_asso = None
	qvT, pvT = asso.getAssociations(correct_trans=True)
	if statistics:
	    gcT = fdr.estimate_lambda(pvT)
	    LG.info("associations: %d" % (qvT<0.05).sum())
	    LG.info("genomic control: %.4f" % (gcT))

    if write_files:
	save_everything(qv, pv, dir_name, "PANAMA")
	if tf_correction:
	    save_everything(qvT, pvT, dir_name, "PANAMA_trans")

    # restore default
    mkl.set_num_threads(mkl.get_num_cores())
    
    if tf_correction:
	return qv, pv, qvT, pvT

    if return_asso_object:
	return qv, pv, asso

    return qv, pv


def LIMMI(expr, snps, dir_name = None, write_files = True,
	  statistics = False, max_interaction_iter = 5, dump_asso_object = False, **kw_args):
    
    if dir_name is not None:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    qv, pv, asso = PANAMA(expr, snps, model = "gplvm_interact", return_asso_object = True,
			  dump_asso_object = False,  dir_name = dir_name, write_files = True, **kw_args)

    asso.get_explained_var()
    
    objects_dir = os.path.join(dir_name,"objects/")

    if not os.path.exists(objects_dir):
	os.makedirs(objects_dir)

    if dump_asso_object:
	pw.write(asso, os.path.join(objects_dir ,"PANAMA_object"), "pickle")

    asso.add_interactions = True
    asso.add_associations = False
    num_interactions = None
    
    for i in range(max_interaction_iter):
	# train LIMMI
	asso.train(Niter_interact = 1, maxiter=1E5, Nrestarts=1, gradcheck=False, diagnostics=False)
	asso.get_explained_var()
	# run LMM scan
	qv, pv = asso.getAssociations()	
	# save associations
	save_everything(qv, pv, dir_name, "LIMMI_iteration%d" % i)
	# save interactions and factors
	pw.write(asso.interactions_qv, os.path.join(objects_dir,"LIMMI_iteration%d_qv" % i), file_type)
	pw.write(asso.getLatent(ard_reweight=True,
				pca_rotation=True,
				rotate_varimax = False),
		 os.path.join(objects_dir,"LIMMI_iteration%d_factors" % i), file_type)
	pw.write(asso.interactions_pv, os.path.join(objects_dir ,"LIMMI_interaction_pv"), file_type)
	
	if dump_asso_object:
	    pw.write(asso, os.path.join(objects_dir,"LIMMI_iteration%d_object % i"), "pickle")
	
	if num_interactions != None and num_interactions == len(asso.candidate_interactions):
	    break
	else:
	    num_interactions = len(asso.candidate_interactions)
	
    pass

def linear(expr, snps, write_files = False, dir_name = None, statistics = False, parallel = False, jobs = 0):
    LG.info("Testing LINEAR:")
    lods = linreg.run_associations(expr,snps,None)
    pv = (1. - st.chi2.cdf(2*lods, 1))
    qv = fdr.qvalues(pv)

    if statistics:
	print "associations: %d" % (qv<0.05).sum()
	gc = fdr.estimate_lambda(pv)
	print "genomic control: %.4f" % (gc)

    if write_files:
	save_everything(qv, pv, dir_name, "LINEAR")

    return qv, pv

def SVA(expr, snps, interactions = True, write_files = False, dir_name = None,
	parallel = True, jobs = 10, statistics = False, proper = False, sparse_pvmin = 1.0,
	Kpop = None):
    
    LG.info("Testing SVA:")

    if proper:
	Y, X, W = sva.sva(expr, covariates = snps, return_ZN = True)
	lods = linreg.run_associations(Y,snps,None)
	pv = (1. - st.chi2.cdf(2*lods, 1))
	qv = fdr.qvalues(pv)
    else:
	qv, pv, X, W, Y = sva.run_eqtl(expr, snps)
	
    if statistics:
	print "associations: %d" % (qv<0.05).sum()
	gc = fdr.estimate_lambda(pv)
	print "genomic control: %.4f" % (gc)

    if interactions:
	QVMi, PVi = model_free_interactions(Y, snps, X, Kpop, parallel, jobs, sparse_pvmin)
	interactions_intermediate_qv = QVMi
	
	if write_files:
	    objects_dir = os.path.join(dir_name,"objects/")
	    pw.write(interactions_intermediate_qv, os.path.join(objects_dir ,"SVA_qv"), file_type)
	    pw.write(X, os.path.join(objects_dir ,"SVA_factors"), file_type)
	    pw.write(PVi, os.path.join(objects_dir, "SVA_interactions_pv"), file_type)	    

    if write_files:
	save_everything(qv, pv, dir_name, "SVA")


    return qv, pv


def ICE(expr, snps, write_files = False, statistics = False, parallel = False, jobs = 0, dir_name = None):
    def split(n, iterable, padvalue=None):
	"split(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
	return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)

    if parallel:
	from multiprocessing import Process, Pool
	from itertools import izip_longest
	Q = snps.shape[1]

	splits = list(split(Q/jobs, range(Q-(Q%jobs)), padvalue=None))
	if Q % jobs != 0:
	    splits.append(range(Q-(Q%jobs), Q))

	pool = Pool(processes=len(splits))
	proc = []
	for s in splits:
	    proc.append(pool.apply_async(ice.run_eqtl, (expr, snps[:,s])))

	qv, pv = [], []
	for p in proc:
	    qvi, pvi = p.get()
	    qv.append(qvi)
	    pv.append(pvi)

	qvs = qv[0]
	for i in range(1,len(qv)):
	    qvs = SP.concatenate((qvs, qv[i]))

	pvs = pv[0]
	for i in range(1,len(pv)):
	    pvs = SP.concatenate((pvs, pv[i]))

	qv, pv = qvs, pvs
	    
    else:
	print "Testing ICE:"
	qv, pv = ice.run_eqtl(expr, snps)

    if statistics:
	print "nrAsso: %d" % (qv<0.05).sum()
	gc = fdr.estimate_lambda(pv)
	print "genomic control: %.4f" % (gc)
    if write_files:
	save_everything(qv, pv, dir_name, "ICE")

    return qv, pv

def PEER(expr, snps, write_files = False, dir_name = None, statistics = False, interactions = True, sparse_pvmin = 1.0, **kw_args):
    prior = 1

    if prior==1:
        priors = {'Alpha':{'priors':[1E-2,1E2]}}
    elif prior==2:
        priors = {'Alpha':{'priors':[1E-1,1E1]}}
    elif prior==3:
        priors = {'Alpha':{'priors':[1E-2,1E4]}}


    #use prior settings from peer publication:
    Ng = expr.shape[1]
    #use a fixed setting for the number of gnes
    # Ng = 6000.

    #priors = {'Alpha':{'priors':[1E-7*Ng,1E-1*Ng]},'Eps':{'priors':[1.,100.]}}
    #priors = {'Alpha':{'priors':[1E-6*Ng,1E-1*Ng]},'Eps':{'priors':[1.,10.]}}
    nIterations = 3
    components = 50

    Y = expr
    vbfa = VBFA.CVBFA(E1=Y,priors=priors,nIterations=nIterations,components=components)
    vbfa.iterate()
    Yp = vbfa.getPrediction().E1

    Ycorr = Y-Yp
    #run linear
    lods = linreg.run_associations(Ycorr,snps,None)
    pv = (1. - st.chi2.cdf(2*lods, 1))
    qv = fdr.qvalues(pv)

    if interactions:
	QVMi = model_free_interactions(expr, snps, vbfa.S.E1, False, 0, sparse_pvmin)
	interactions_intermediate_qv = QVMi
	
	if write_files:
	    objects_dir = os.path.join(dir_name,"objects/")
	    pw.write((interactions_intermediate_qv, vbfa.S.E1), os.path.join(objects_dir ,"PEER_object"), file_type)

    
    if statistics:
	print "associations: %d" % (qv<0.05).sum()
	gc = fdr.estimate_lambda(pv)
	print "genomic control: %.4f" % (gc)

    if write_files:
	save_everything(qv, pv, dir_name, "PEER")

    return qv, pv


def model_free_interactions(expr, snps, X, Kpop, parallel, jobs, pv_min):
    sparse_storage = True

    K = SP.zeros((expr.shape[0],expr.shape[0]))

    if Kpop != None:
	K = Kpop

    PV = []
    INDEX = []

    n_effective_tests = X.shape[1] * expr.shape[1] * snps.shape[1]

    # sometimes (like when we are simulating) we don't want to store sparse QVs, so
    # let's just compute the whole thing
    if not sparse_storage:
	PV = SP.empty((self.snps.shape[1], Y.shape[1],X.shape[1]))

    pv_def = None
    
    for i in range(X.shape[1]):
	[lod, pv_lmm] = testing.interface(snps, expr, K, I = X[:,i:i+1], model = "LMM",
				   return_fields = ['lod', 'pv'],
				   parallel = parallel, jobs = jobs)

	pv_lmm = st.chi2.sf(2*(lod),1)

	if i == 0:
	    pv_def = pv_lmm.copy()
	    
	if sparse_storage:
	    #1. figure out which pv are < min
	    Irel = pv_lmm<pv_min
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

    if sparse_storage:
	#convert everything into arrays
	PV = SP.array(PV)
	INDEX = SP.array(INDEX)
	QV = fdr.qvalues(PV, m = n_effective_tests, fix_lambda = pv_min)
	QVMi = SP.concatenate((SP.array(INDEX), SP.array(QV)[:, SP.newaxis]), axis=1)
    else:
	QV = fdr.qvalues(PV, m = n_effective_tests)
	QVMi = QV.min(axis=2) # minimize across factors

    return QVMi, pv_def
