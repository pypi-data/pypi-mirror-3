"""Covariance functions suitable for GPLVM"""


import scipy as SP
from pygp.covar import CovarianceFunction
import pdb


class LinearInteractCF(CovarianceFunction):
    """

    linear interaction covariance function This covariance assumes that
    part of the inputs X are SNPS and the remainder are latent
    factors.  Furthermore this covariance function maintains a list
    with interaction candidates, where each interaction has it's own
    weight which is a hyperparameter (one per SNP/factor pair).

    """

    def __init__(self, n_dimensions=1, interact_dimension_indices=None,
		 dimension_indices=None, interact_pairs=[], **kw_args):
        """
        n_dimensions                      : total number of dimensions
        dimension_indices(None)           : dimension indices for interactions (1)
        interact_dimension_indices(None)  : dimension indices for interactions (2)
        default: all dimensions as in n_dimensions
        """       

        # inherited constructor
	super(CovarianceFunction, self).__init__(**kw_args)

        # init dimensions
        self._set_dimension_indices(n_dimensions=n_dimensions,
				    interact_dimension_indices = interact_dimension_indices,
				    dimension_indices = dimension_indices,
				    interact_pairs = interact_pairs)
        

    def _set_dimension_indices(self, n_dimensions = 1, interact_dimension_indices = None,
			       dimension_indices = None, interact_pairs=[]):
        """

	set dimension indices for the two types of input dimensions to interact

	"""

        if dimension_indices is not None:
            self.dimension_indices = dimension_indices
        else:
            self.dimension_indices = SP.arange(0,n_dimensions)
        if interact_dimension_indices is not None:
            self.interact_dimension_indices = interact_dimension_indices
        else:
            self.interact_dimension_indices = SP.arange(0,n_dimensions)
        self.interact_pairs = interact_pairs

        # number of hyperparameters:
        self.n_hyperparameters = len(self.interact_pairs)
        
        
    def _filter_i(self,i):
        """

	Filter ineraction dimensions

	"""

        return i[:,self.interact_dimension_indices]

    def _filter_input_dimensions_interact(self,x1,x2):
        """
        """
        if x2 == None:
            xf = self._filter_i(x1)
            return xf,xf
        return self._filter_i(x1), self._filter_i(x2)
    
    def K(self,logtheta,x1,x2=None):
        #1. get inputs data
        if x2 is None:
            x2 = x1
        n = x1.shape[0]

        #2. exponentiate amplitude parameters
        A = SP.exp(2*logtheta)
        RV = SP.zeros([n,n])
        for ip in xrange(len(self.interact_pairs)):
            p = self.interact_pairs[ip]
            i_f = self.dimension_indices[p[0]]
            i_i = self.interact_dimension_indices[p[1]]
            #binarize the SNP state to 0/1 to have a propper interaction again
            x1_f = x1[:,i_f]
            x1_i = x1[:,i_i]
            x2_f = x2[:,i_f]
            x2_i = x2[:,i_i]
            x1_ = x1_f * x1_i
            x2_ = x2_f * x2_i
            RV+= A[ip]*SP.outer(x1_,x2_)
        return RV
        pass

    def Kgrad_theta(self,logtheta,x1,i):
        A = SP.exp(2*logtheta[i])
        p = self.interact_pairs[i]
        i_f = self.dimension_indices[p[0]]
        i_i = self.interact_dimension_indices[p[1]]
        x1_f = x1[:,i_f]
        x1_i = x1[:,i_i]
        x1_ = x1_f * x1_i
        RV= 2*A*SP.outer(x1_,x1_)
        return RV

    def Kgrad_x(self,logtheta,x1,x2,d):
        A = SP.exp(2*logtheta)
        RV = SP.zeros([x1.shape[0],x2.shape[0]])

        #get interaction partners
        n = x1.shape[0]
        for ip in xrange(len(self.interact_pairs)):
            p = self.interact_pairs[ip]
            i_f = self.dimension_indices[p[0]]
            i_i = self.interact_dimension_indices[p[1]]
            if i_f!=d:
                continue
            x1_f = x1[:,i_f]
            x1_i = x1[:,i_i]
            x2_f = x2[:,i_f]
            x2_i = x2[:,i_i]

            x2_ = (x2_f*x2_i)[SP.newaxis,:]
            dx1_ = (x1_i)[:,SP.newaxis]
            RV[:,:] += A[ip] * (dx1_*x2_)
        return RV
        pass

    def Kgrad_xdiag(self,logtheta,x1,d):
        A = SP.exp(2*logtheta)
        RV = SP.zeros([x1.shape[0]])

        #get interaction partners
        n = x1.shape[0]
        for ip in xrange(len(self.interact_pairs)):
            p = self.interact_pairs[ip]
            i_f = self.dimension_indices[p[0]]
            i_i = self.interact_dimension_indices[p[1]]
            #i_state = self.interact_dimension_indices[p[2]]
            if i_f!=d:
                continue
            x1_f = x1[:,i_f]
            x1_i = x1[:,i_i]
            x1_ = x1_f*x1_i
            dx1_ = (x1[:,i_i])
            RV[:] += 2*A[ip] * dx1_*x1_
        return RV
        
