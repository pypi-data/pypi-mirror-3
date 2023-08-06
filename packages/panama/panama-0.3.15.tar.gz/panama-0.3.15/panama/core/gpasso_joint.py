"""
GPasso
- Gaussian process association test
"""

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
import testing, interaction_scan


class GPLVMassoJ(object):
    """some details:
    fixed parameters (setData)
    snp_dimensions        : dimension index of snps (0..Ns)
    factor_dimensions     : dimension index of factors (Ns..Ns+Nf)

    learning parameters
    candidate_assoications : index with SNPs to include in the factor learning
    candidate_interactions : index with factor x SNP pairs to include in the factor learning
    ard: perform ard on the factors, i.e. estimate one varinace per factor
    lam: L1 penalty for factors
    """

    def __init__(self, sigma = 0.1, n_factors = 100, gplvm_init = 'randn', model = 'gplvm', add_associations = True,
		 pop_cf = False, mean_cf = True, asso_method = 'LMM', interact_method ='LMM', keep_latent = False,
		 parallelize = False, max_int_lod = False, Njobs = 5, ard = False, lam = 0, verbose_plot_dir = None,
		 Kpop = None, FA_noise = False, FDR_addition_associations = 0.2, FDR_addition_interactions = 0.01,
		 topn_interactions = 1, sim = None, testing_directory = None, fixed_latent_dim = False, pv_max_stored = None):

        self.testing_directory = testing_directory
        self.sim=sim
        self.n_factors = n_factors
        self.gplvm_init = string.upper(gplvm_init)
        self.model  = model
        self.sigma  = sigma
        self.candidate_interactions = []
        self.candidate_associations = []
	self.interactions_qv = []
	self.interactions_pv = []	

	self.fixed_latent_dim = fixed_latent_dim
	
        #iterations
        self.train_iterations = 0
	self.interactions_iter = 0

	# threshold for storing pvalues (stores only pv < thresh)
	self.pv_max_stored = pv_max_stored
	
        # threshold for adding stuff both in normal PANAMA and in LIMMI
        self.FDR_addition_associations = FDR_addition_associations
        self.FDR_addition_interactions = FDR_addition_interactions
	self.topn_interactions = topn_interactions # only add the top n inter.
	
        self.add_associations = add_associations
        self.use_pop_cf = pop_cf
        self.use_mean_cf = mean_cf
        self.keep_latent = keep_latent
	self.asso_method = asso_method
        self.cutoff_factors = 0 # threshold that decides when a factor is off
	
	# Add_interactions will be switched on later if gplvm_interact is selected
	self.add_interactions = False
        self.hyperparams = None  # erase hyperparams
        self.lmls = [] # log marginal likelihoods
        self.parallelize = parallelize
        self.Njobs = Njobs
        self.max_int_lod = max_int_lod
        self.ard = ard # (Boolean) should we use the ARD covariance?
        self.lam = lam
        self.verbose_plot_dir = verbose_plot_dir
	self.Kpop = Kpop
	# use a different noise level for each dimension
	self.FA_noise = FA_noise

	
    def setData(self, snps, pheno, covariates = None, pop_snps = None,normalize_pheno=True,normalize_geno=True):
	"""
	Loads the data, centering and scaling the SNPs and the phenotype

	"""

        self.nN = snps.shape[0]
        self.nD = pheno.shape[1]
        self.nS = snps.shape[1]


        if covariates is None:
            covariates = SP.zeros([self.nN,0])

        self.nC = covariates.shape[1]

        assert snps.shape[0]==pheno.shape[0], 'dimension mismatch'
        assert covariates.shape[0]==snps.shape[0], 'dimension mismatch'

        #uncentered raw SNPS
        #there are needed for interaction tests
        self.snps_raw = snps.copy()

	# Normalize SNPs
        if normalize_geno:
            LG.info("Centering and scaling the SNPs...")
            snps = snps - snps.mean(axis=0)
            snps /= snps.std(axis=0)

        if normalize_pheno:
            # Normalize genes
            LG.info("Centering and scaling the phenotype...")
            pheno = pheno - pheno.mean(axis=0)
            pheno /= pheno.std(axis=0)

        # SNPS/PHENO
        self.snps  = snps
        self.pheno = pheno

        self.covariates = covariates

        #set starting SNP dimensions and factor dimensions
        self.pop_snps = pop_snps

        #initialize GP object
	self._init_gp()

    def lMl(self):
        """
	Returns the NEGATIVE log marginal likelihood

	"""

        return self.gp.LML(self.hyperparams)

    def setLatent(self,x):
        """
	Sets the latent variables
	"""
        self.hyperparams['x'] = x


    def findK(self,**kw_args):
        """
	Returns the number of PCA dimensions that explain 95% of the variance

	"""

    	Y = self.pheno.copy()
    	Y -= Y.mean(axis=0)
    	Y /= Y.std(axis=0)
    	U, s, V = SP.linalg.svd(Y, full_matrices = False)
    	eigv = SP.sort(s**2)[::-1]
    	expl = SP.cumsum(eigv)

    	return min(self.n_factors,SP.nonzero(expl/expl.max() > 0.90)[0].min())


    def get_covar_param_index(self, covar):
	"""
	Finds the index of the hyperparameters for a given covariance function

	"""

        # determine indices of covariance:
        icf = 0
        np = 0
        # find covariance parametrs
        while (self.covar_list[icf] != covar):
            np += self.covar_list[icf].get_number_of_parameters()
            icf +=1
        assert self.covar_list[icf] == covar, 'covariance not found!'

        nparam = covar.n_hyperparameters
        Ip = SP.arange(np,np+nparam)

        return Ip

    def get_explained_var(self):
	hyperparams = {'covar': copy.deepcopy(self.hyperparams['covar']),
		       'lik': copy.deepcopy(self.hyperparams['lik']),
		       'x': copy.deepcopy(self.hyperparams['x'])}
	
	for cf in self.covar_list:
	    cf_name = cf.__class__.__name__
	    param_index = self.get_covar_param_index(cf)
	    param = hyperparams['covar'][param_index]
	    if cf_name == "LinearCFARD":
		param = 1/param
		X_var = hyperparams['x'].var(axis=0)
		param = X_var * param
	    elif cf_name == "LinearCF":
		param = SP.exp(param)
		X_var = self.snps[:,self.candidate_associations].var(axis=0)
		param = X_var * param
	    elif cf_name == "LinearInteractCF":
		if len(self.candidate_interactions) > 0:
		    param = SP.exp(param)
		    X_var = hyperparams['x'].var(axis=0)[SP.array(self.candidate_interactions)[:,0]]
		    S_var = self.snps.var(axis=0)[SP.array(self.candidate_interactions)[:,1]]
		    param = param*S_var*X_var
	    else:
		param = SP.exp(param)

		
	    print cf_name, param.round(4), param.sum().round(4)

	# noise
	param = SP.exp(hyperparams['lik'])
	print "noise", param.round(4)

	
    def get_K_testing(self,correct_trans = True, correct_confounders = True,
		      correct_interactions = True, noise = True, Ix = None,
		      refit_confounders = True):

        """
	Returns a corrected covariance structure

        correct_trans: include genetic component (True)
        correct_confounders: include confounders in covariance (True)
        noise: include noise (True)
        """

        # 1. create copy of current hyperparmas, dropping latent factors X
	hyperparams = {'covar': copy.deepcopy(self.hyperparams['covar']),
		       'lik': copy.deepcopy(self.hyperparams['lik'])}
	
        I_snp = self.get_covar_param_index(self.snp_cf)
        # find confounder covariance parameters
        I_factor = self.get_covar_param_index(self.factor_cf)
        # filter for optimization
        Ifilter = {'covar': SP.ones(len(hyperparams['covar']),dtype='bool'),
		   'lik': SP.ones(len(hyperparams['lik']),dtype='bool')}

	# If we are in interaction mode, this option kills the interaction
	# covariance
	if self.model == "gplvm_interact" and not correct_interactions:
	    index_interactions = self.get_covar_param_index(self.interact_cf)
	    hyperparams['covar'][index_interactions] = SP.log(1E-10)
            # construct filter for optimizer         
            Ifilter['covar'][index_interactions] = False
	    
        if not correct_trans:
            # switch off SNP effects
            hyperparams['covar'][I_snp] = SP.log(1E-10)
            # construct filter for optimizer         
            Ifilter['covar'][I_snp] = False

        if not correct_confounders:
            # switch off confounder CF
            # note these are not! operated in log space and are 1/p!
            hyperparams['covar'][I_factor] = 1E10
            Ifilter['covar'][I_factor] = False

	if not refit_confounders:
	    # correct_confounders kills the confounders and takes them out of the optimization
	    # this statement just removes them from the opt
            Ifilter['covar'][I_factor] = False

        # reoptimize covariance structure:
        # REMEMBER: excludes latent variables from optimization
        [hyperparams_o,opt_lml_o] = GPLVM.opt_hyper(self.gp,hyperparams,Ifilter=Ifilter,bounds=self.hyperparams_bounds,priors = self.hyperparams_priors)

        if Ix is not None:
	    # switch off some of the factors
	    factors_off = I_factor[~Ix]
            hyperparams_o['covar'][factors_off] = 1E10

        if not noise:
            # disables noise
	    if self.FA_noise:
		hyperparams_o['lik'] = SP.log(1E-10)
	    else:
		hyperparams_o['lik'] = SP.log(SP.ones(self.nD)*1E-10)

        # compute the covariance matrix
        K   = self.gp.covar.K(hyperparams_o['covar'],self.gp.x)
	
        return [K,hyperparams_o]

    def _get_residuals(self, prediction = False, **kw_args):
        """calculate PANAMA residuals"""
        #1. get K without or with trans guys:
        [K,hyperparams_o] = self.get_K_testing(noise=True,**kw_args)
        KV = self.gp.get_covariances(hyperparams_o)
        #2. get cross covariance (merely removing noise here)
        Kstar = self.gp.covar.K(hyperparams_o['covar'],self.gp.x,self.gp.x)
        #3. calc predictions manually:
        mu = SP.dot(Kstar.transpose(),KV['alpha'])
        Y_ = self.pheno-mu
	if prediction:
	    return Y_, mu
	else:
	    return Y_

    def getAssociations(self,correct_trans=False):
	"""
        Association scan given current training state of the PANAMA model
	Returns: qvalues, pvalues
	"""

	LG.info("Association testing...")

        if string.upper(self.asso_method)=='ML':
            #calc residulas on Y
            Y_ = self._get_residuals(correct_trans=correct_trans)
            K  = None
        elif string.upper(self.asso_method)=='LMM':
            #use raw Y, LMM is taking care of this
            Y_= self.pheno
            [K,hyperparams_o] = self.get_K_testing(correct_trans=correct_trans,
                                                correct_confounders = True,
						noise=False)

	# find associations running a simple (and fast) linear model
	pval = testing.interface(self.snps, Y_,K, I = None,
				 model=string.upper(self.asso_method), parallel = self.parallelize,
				 file_directory = None, jobs = self.Njobs)[0]
 	# convert to qvalues
        qval = fdr.qvalues(pval)
        return qval,pval
    

    def getLatent(self,filter_active=False,ard_reweight=False,pca_rotation=False,rotate_varimax=False):
        """return active LVs
        ard_reweight: reweight factors by ARD relevances (False)
        pca_rotation: rotate to PCA solution (False)
        rotate_varimax: varimax rotation of factors (False)
        """

        X = self.hyperparams['x'].copy()
        I_ard = self.get_covar_param_index(self.factor_cf)

	aw_X_var = X.var(axis=0)
	aw_X_var /= aw_X_var.max()

	cutoff = self.cutoff_factors
	active = (aw_X_var > cutoff)

        # ARD reweighting and PCA rotation?
        if ard_reweight:
            I_ard = self.get_covar_param_index(self.factor_cf)
            a_w = 1/self.hyperparams['covar'][I_ard]
            X = SP.multiply(SP.sqrt(a_w), X)
	    
        if pca_rotation:
	    X -= X.mean(axis=0)
            X = GPLVM.PCA(SP.dot(X, X.T),self.n_factors)[0]

        if rotate_varimax:
            U, s, Vh = SP.linalg.svd(X, full_matrices = False)
            X = SP.dot(U, SP.diag(s))
	    
        # restrict to subset
        if filter_active:
            X = X[:,active]
            return X, active 

	return X


    def add_SNP_factor_associations(self):
        """
	Scans the SNP to find which ones overlap with the latent confounders.
	"""
	S = self.snps
	# get weighted latent variables
	X = self.getLatent(ard_reweight=True,pca_rotation=True)
        # Center the latent variables and the SNPs
	X -= X.mean(axis = 0)
        # Center SNPs
	S -= S.mean(axis = 0)

        # Get the covariance function that accounts for the current set of associations
        [K,hyperparams_o] = self.get_K_testing(correct_trans=True,correct_confounders=False,noise=False)

	# Association testing:
        PV = testing.interface(S, X, K, I = None, model = "LMM",parallel = self.parallelize, jobs = self.Njobs,
			       file_directory=self.testing_directory)[0]

        # Number of tests conducted
        Neff = self.n_factors*self.nS
        QV = fdr.qvalues(PV,m=Neff)

	# If needed, save diagnostic plots
        if self.verbose_plot_dir is not None:
            import pylab as PL
	    PL.figure(2)
	    PL.clf()
            PL.plot(self.candidate_associations, [1 for x in self.candidate_associations],  "rx")
            PL.savefig(os.path.join(self.verbose_plot_dir,'candidates_%d.png' % (self.train_iterations)))
            PL.figure(3)
	    PL.clf()
	    QVs = SP.array([SP.sort(QV[:,i]) for i in xrange(QV.shape[1])])
	    PL.plot(QVs.T)
            PL.savefig(os.path.join(self.verbose_plot_dir,'QVs_%d.png' % (self.train_iterations)))


	# Set the qvalue of the current associations to 1
	QV[self.candidate_associations,:] = 1

	# Greedily construct addition set by adding the BEST (lowest qv) SNP for each factor
	# (if significant)
	new_candidates = []
	for i in xrange(QV.shape[1]):
	    i_best = QV[:,i].argmin()
	    qv_best = QV[:,i].min()
	    # if significant, add it
	    if qv_best<=self.FDR_addition_associations:
		new_candidates.append(i_best)
		# and set the corrisponding qvalue to 1 
		QV[i_best,:] = 1

	# Add candidates
	Nc_old = len(self.candidate_associations)
	self.candidate_associations.extend(new_candidates)
	Nc = len(self.candidate_associations)

	dl = Nc-Nc_old
	#check everything is fine
	assert len(SP.unique(self.candidate_associations))==len(self.candidate_associations), 'added non-unique snps'
	LG.info("Candidates: %d, added: %d" % (Nc,dl))
	return dl

    
    def add_snp_factor_interactions(self):
        """
        Scan for interactions between all SNPs and genes, factors
        """

        #interactions_iter: conting number of effective iterations so far
	self.interactions_iter += 1

	correct_interactions = True
	
	# get the covariance matrix
	K = self.Kpop
	
        # get latent factors and rotate to PCA
	X = self.getLatent(ard_reweight = True, pca_rotation = True, rotate_varimax = False)

	inter = interaction_scan.get_candidate_interactions(self.pheno, self.snps, X, K,
							    interactions_iter = self.interactions_iter,
							    pv_max_stored = self.pv_max_stored,
							    topn_interactions = self.topn_interactions,
							    FDR_addition_interactions = self.FDR_addition_interactions,
							    candidate_interactions = self.candidate_interactions,
							    correct_interactions = correct_interactions,
							    parallel = self.parallelize,
							    Njobs = self.Njobs)

	Nint_new, self.candidate_interactions, int_pv_qv = inter
	self.interactions_pv, self.interactions_qv = int_pv_qv
	
	return Nint_new
    


    def train(self,Niter=1,Niter_interact=3,**kw_args):
        """
	Trains the latent variable model while adding associations and/or interactions

	Parameters:

	Niter = number of training iterations (if 1, just trains the GPLVM, without adding associations
	or interactions)

	"""
	
	LG.info("Training PANAMA with an association FDR of %.2f" % self.FDR_addition_associations)

	if self.model == "gplvm_interact":
	    LG.info("LIMMI's interaction FDR is set to %.2f, adding at most %d interactions" % (self.FDR_addition_interactions,
												self.topn_interactions))
	
        # retrain once
	retrain = True
	# iteration counter
	it = 0

	# init the mode variable
	mode = None

        # current mode of covariance additions
        if self.add_associations:
	    LG.info("add_associations mode active")
            mode = 'add_associations'
        elif self.add_interactions:
	    LG.info("add_interactions mode active")	    
            mode = 'add_interactions'
        # ok, now the actual loop
	while (retrain and it < Niter):
            # association scan and interactions require one training iteration
            if self.train_iterations > 0:
		# adds association terms
                if mode == 'add_associations':
                    LG.info("adding factors-SNPs associations")
		    asso_added = self.add_SNP_factor_associations()
		    if (asso_added==0):
                        # switch mode to interactions?
                        if self.add_interactions:
			    LG.info("All associations added, switching to adding interactions")
                            mode = 'add_interactions'
                            Niter = it+Niter_interact
                        else:
                            break
                elif mode == 'add_interactions':
                    LG.info("Adding factors-SNPs interactions")
                    int_added = self.add_snp_factor_interactions()

                    if int_added == 0:
                        break
			
            LG.info('Train iteration %d/%d' % (it+1, Niter))
	    # If we are at the first iteration, find an estimate for K
	    if self.train_iterations == 0:
		if not self.fixed_latent_dim:
		    # determine latent dimensionality in first iteration
		    self._init_gp()
		    K = self.findK()
		    self.n_factors = K
		    # kill hyperparmas again because number of factors changed!
		    self.hyperparams = None
		    LG.info("PCA-initialized dimensionality: %d" % K)
		else:
		    LG.info("User-supplied latent dimensionality: %d" % self.n_factors)

            #note: we swtiched iterative factors on, which trians factors and hyperparameters in turns:
            self.train_gplvm(iterative_factors=False,**kw_args)
            # increase iteration counter
            self.train_iterations +=1
	    it+=1
            # store lml
            self.lmls.append(self.lMl())
        pass
        
                          
    def train_gplvm(self, gradcheck = False, Nrestarts = 1, diagnostics = True,iterative_factors=False,n_iterative_factors=3, **kw_args):
        """
	Trains the GPLVM model without priors.
	Nrestarts specifies the number of random restarts
	iterative_factors: train factors and hyperparameters in turns
	"""
        def opt_hyper(iterative_factors=False):
            if iterative_factors:
                #note: we always refit the likelihood as there seems to be no good reason to not do so:
                #filter for learning covar params:
                Ifilter_covar = {'covar': SP.ones(len(self.hyperparams['covar']),dtype='bool'),
                                 'lik': SP.ones(len(self.hyperparams['lik']),dtype='bool'),
                                 'x': SP.zeros(self.hyperparams['x'].shape,dtype='bool')}

                #filter for learning factors
                Ifilter_factors = {'covar': SP.zeros(len(self.hyperparams['covar']),dtype='bool'),
                                 'lik': SP.ones(len(self.hyperparams['lik']),dtype='bool'),
                                 'x': SP.ones(self.hyperparams['x'].shape,dtype='bool')}
                #iterate
                opt_params = self.hyperparams
                for i in xrange(n_iterative_factors):
                    [opt_params,opt_lml]= GPLVM.opt_hyper(self.gp,opt_params,gradcheck=gradcheck,bounds=self.hyperparams_bounds,priors = None,Ifilter=Ifilter_covar, **kw_args)
		    # opt_params['x'] = self.getLatent(ard_reweight=True, rotate_varimax = True)
                    [opt_params,opt_lml]= GPLVM.opt_hyper(self.gp,opt_params,gradcheck=gradcheck,bounds=self.hyperparams_bounds,priors = None,Ifilter=Ifilter_factors, **kw_args)
                #end for
                
            else:
                [opt_params,opt_lml]= GPLVM.opt_hyper(self.gp,self.hyperparams,gradcheck=gradcheck,bounds=self.hyperparams_bounds,priors = None, **kw_args)

            return  [opt_params,opt_lml]

        
        
        lmls = []
        params = []
	i = 0 
	while i < Nrestarts:
            # trains the GPLVM without priors
	    self._init_gp()
	    i += 1
            #opt
            [opt_params,opt_lml] = opt_hyper(iterative_factors=iterative_factors)
            lmls.append(opt_lml)
            params.append(opt_params)

        # save restart results
        self.restart_results = {'lmls': SP.array(lmls), 'params': SP.array(params)}

	# find best run and use the parameters from that
        ibest = self.restart_results['lmls'].argmin()
        opt_model_params = self.restart_results['params'][ibest]
        self.hyperparams = opt_model_params

        # invalidate caches
        self.QV_asso = None

	# If a plot directory is supplied, plots the factor activations
        if self.verbose_plot_dir is not None:
	    import pylab as PL
            PL.figure(4)
            PL.clf()
            I_factor = self.get_covar_param_index(self.factor_cf)
            weights = 1/self.hyperparams['covar'][I_factor]
            x       = self.hyperparams['x']
            weightseff   = weights*x.std(axis=0)
            PL.bar(SP.arange(len(weightseff)),weightseff)
            PL.savefig(os.path.join(self.verbose_plot_dir,'active_factors%d.pdf' % (self.train_iterations)))


    #####PRIVATE METHODS######
    def _init_latent(self):
        """
	Returns starting point for latent variables
	"""
        # initialise latent variables
        if self.gplvm_init=='PCA':
            [Spca,Wpca] = GPLVM.PCA(self.pheno,self.n_factors)
            self.X0 = Spca.copy()
            x_latent = Spca
        elif self.gplvm_init=='RANDN':
            x_latent = SP.random.randn(self.nN,self.n_factors) * 0.1
        elif self.gplvm_init=='PCA_RANDN':
            # Noisy PCA
            [Spca,Wpca] = GPLVM.PCA(self.pheno,self.n_factors)
            self.X0 = Spca.copy()
            x_latent = Spca
            x_latent += 0.1*SP.random.randn(self.nN,self.n_factors)
        elif isinstance(self.gplvm_init,SP.ndarray):
            assert self.gplvm_init.shape==(self.nN,self.n_factors)
            x_latent = self.gplvm_init.copy()
        else:
            raise Excetion('unknown initialization method')
        return x_latent

        
    def _init_gp(self, hyperparams_latent = None):
        """
	Initialization of gp models and covariances. If xlantent and/or hyperparams_latent
	are supplied, it skips the initialization with PCA/randn and uses the provided
	latent variables and hyperparameters
	"""

        # all snps
        self.snp_dimensions   = SP.arange(0,self.nS)
        # then covariates
        self.covar_dimensions = SP.arange(self.nS,self.nS+self.nC)
        # then factors
        self.factor_dimensions = SP.arange(self.nS+self.nC,self.nS+self.nC+self.n_factors)

        snp_dimensions = self.snp_dimensions
        factor_dimensions = self.factor_dimensions

      
        # 2. construct covariances                
        # construct GPLVM model
        covar = []

        # 2.0 mean CF
        self.mean_cf  = mu.MuCF(self.nN)
        self.mean_cf_covar = SP.array([1E-3])
        self.mean_cf_covar_bound = [(-SP.inf,10)]
        self.mean_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]]

        # 2.1 noise init	
	if not self.FA_noise:
	    self.noise_cf_covar = SP.array([self.sigma])
	    self.noise_cf_covar_bound = [(-SP.inf,10)]
	    self.noise_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]]
        else:
	    self.noise_cf_covar = SP.log(SP.ones(self.nD)+self.sigma*SP.random.randn(self.nD))
	    self.noise_cf_covar_bound = [(-SP.inf,10)] * self.nD
	    self.noise_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]] * self.nD

        # 2.2 global genetics CF (population only)
        if self.use_pop_cf:
	    assert self.Kpop != None, "use_pop_cf is true but no population structure covariance was supplied"	    
            self.pop_cf = fixed.FixedCF(K=self.Kpop)
            self.pop_cf_covar = SP.array([1])
            self.pop_cf_covar_bound = [(-SP.inf,10)]
            self.pop_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]]

        # 2.3 Covariates CF
        self.cov_cf = linear.LinearCFARD(dimension_indices = self.covar_dimensions)
        self.cov_cf_covar = SP.array([SP.exp(1)]*self.nC)
        self.cov_cf_covar_bound = [(1E-3,SP.inf)]*self.nC
        self.cov_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]] * self.nC
       
        # 2.3 SNP covariance function
        self.snp_cf = linear.LinearCF(dimension_indices = snp_dimensions[self.candidate_associations])
        self.snp_cf_covar = SP.array([1]*len(self.candidate_associations))
        self.snp_cf_covar_bound = [(-SP.inf,10)]*len(self.candidate_associations)
        self.snp_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]]*len(self.candidate_associations)
               
        # 2.4 factor covariance function
        if self.ard:
            # use new ARD covariance function, this stilll operatores inlog space!
            # weights in new covariances are just 1/logtheta[i], so no exp!
            self.factor_cf = linear.LinearCFARD(dimension_indices = factor_dimensions)
            # use SP.exp such that log from this is 1 again:
	    if hyperparams_latent == None:
		self.factor_cf_covar = SP.array([SP.exp(100)]*self.n_factors)
	    else:
		self.factor_cf_covar = SP.exp(hyperparams_latent)
            self.factor_cf_covar_bound = [(1E-3,SP.inf)]*self.n_factors
            self.factor_cf_covar_prior = [[lnpriors.lnL1,[self.lam]]]*self.n_factors
            pass
        else:
            self.factor_cf = linear.LinearCFISO(dimension_indices = factor_dimensions)

	    if hyperparams_latent == None:
		self.factor_cf_covar = SP.array([1])
	    else:
		self.factor_cf_covar = hyperparams_latent
		
            self.factor_cf_covar_bound = [(-SP.inf,10)]
	    self.factor_cf_covar_prior = [[lnpriors.lnL1,[self.lam]]]


        self.covar_list = []
        self.covar_cf_list = []
        self.covar_cf_bounds = []
        self.covar_cf_priors = []
        
        #optinal: mean_cf and population CF:
        if self.use_mean_cf:
            self.covar_list.extend([self.mean_cf])
            self.covar_cf_list.extend([self.mean_cf_covar])
            self.covar_cf_bounds.extend(self.mean_cf_covar_bound)
            self.covar_cf_priors.extend(self.mean_cf_covar_prior)
        if self.use_pop_cf:
            self.covar_list.extend([self.pop_cf])
            self.covar_cf_list.extend([self.pop_cf_covar])
            self.covar_cf_bounds.extend(self.pop_cf_covar_bound)
            self.covar_cf_priors.extend(self.pop_cf_covar_prior)

        #add covariance CF if needed
        if self.nC>0:
            self.covar_list.extend([self.cov_cf])
            self.covar_cf_list.extend([self.cov_cf_covar])
            self.covar_cf_bounds.extend(self.cov_cf_covar_bound)
            self.covar_cf_priors.extend(self.cov_cf_covar_prior)
            

        #add snp cf and noise CF
        self.covar_list.extend([self.snp_cf])
        self.covar_cf_list.extend([self.snp_cf_covar])
        self.covar_cf_bounds.extend(self.snp_cf_covar_bound)
        self.covar_cf_priors.extend(self.snp_cf_covar_prior)
	

	# Factor CF common to PANAMA and LIMMI
        if self.model == 'gplvm' or self.model == "gplvm_interact":
            self.covar_list.extend([self.factor_cf])
            self.covar_cf_list.extend([self.factor_cf_covar])
            self.covar_cf_bounds.extend(self.factor_cf_covar_bound)
            self.covar_cf_priors.extend(self.factor_cf_covar_prior)

	    # specific to LIMMI
	    if self.model == "gplvm_interact":
		self.interact_cf = LinearInteractCF(dimension_indices = factor_dimensions,
						    interact_dimension_indices = snp_dimensions,
						    interact_pairs = copy.deepcopy(self.candidate_interactions))
		self.interact_cf_covar = SP.array([1]*len(self.candidate_interactions))
		# TODO: is this right???
		self.interact_cf_covar_bound = [(-SP.inf,10)]*len(self.candidate_interactions)
		self.interact_cf_covar_prior = [[lnpriors.lnuniformpdf,[]]]*len(self.candidate_interactions)

		self.covar_list.extend([self.interact_cf])
		self.covar_cf_list.extend([self.interact_cf_covar])
		self.covar_cf_bounds.extend(self.interact_cf_covar_bound)
		self.covar_cf_priors.extend(self.interact_cf_covar_prior)
                # print "switching on add_interactions because of gplvm_interact"
                # self.add_interactions = True

	       		
        else:
            raise Exception("unknown covariance model")

        # create sum CF
        self.covariance_gplvm = combinators.SumCF(tuple(self.covar_list))
	    
	# construct hyperparameters
        log_covar = SP.log(SP.concatenate(self.covar_cf_list))

        # Initialize observed inputs
        x_obs = self.snps
        x_covar = self.covariates
	# Initialize latent variables
	x_latent = self._init_latent()

	self.hyperparams_init = {'covar':log_covar,'x':x_latent, 'lik': self.noise_cf_covar}
        if (self.hyperparams is None) or (not self.keep_latent):
            self.hyperparams = copy.deepcopy(self.hyperparams_init)
        else:
            self.hyperparams['covar'] = self.hyperparams_init['covar']
	    self.hyperparams['lik'] = self.hyperparams_init['lik']
	
	
        # create GP object
	if not self.FA_noise:
	    self.gp = GPLVM.GPLVM(covar_func = self.covariance_gplvm, likelihood = lik.GaussLikISO())
	else:
	    self.gp = GPLVM_ARD.GPLVMARD(covar_func = self.covariance_gplvm,
					 likelihood = lik.GaussLikARD(n_dimensions = self.nD))


        # set x_latent in this state to 0.
        # this ensures that the first iteration latent variables (before training) are not used
        x_latent0 = SP.zeros_like(x_latent)
             
        self.X = SP.concatenate((x_obs,x_covar,x_latent0),axis=1)
        # set active dimensions in covariance function:
        self.gp.setData(x=self.X,y=self.pheno,gplvm_dimensions=factor_dimensions)
        # create bounds
        self.hyperparams_bounds = {'covar': SP.array(self.covar_cf_bounds),
				   'lik': SP.array(self.noise_cf_covar_bound)}
        # create prior
        self.hyperparams_priors = {'covar': SP.array(self.covar_cf_priors),
				   'lik': SP.array(self.noise_cf_covar_prior)}

	# self.get_explained_var()
        pass
