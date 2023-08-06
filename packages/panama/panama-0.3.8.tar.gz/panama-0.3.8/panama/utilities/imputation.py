import scipy as SP
import pdb





def eigenstratImputation(X, imissX=None, maxval=2.0):
    """
    impute SNPs as in
    'Principle components analysis corrects for stratification in genome-wide association studies'
    Price et al 2006 (Nature Genetics) page 908, Section 'Methhods', 'Inference of axes of variation'

    Input:
      X:        [n_indiv * n_SNP] matrix of SNPs, missing values are SP.nan
      maxval:   maximum value in X (default is 2 assuming 012 encoding)

    Output:
      X_ret:        [n_ind * n_SNP] matrix of imputed and standardized SNPs
    """
    if imissX is None:
        imissX = SP.isnan(X)
    
    n_i,n_s=X.shape
    if imissX is None:
        n_obs_SNP=SP.ones(X.shape)
    else:    
        i_nonan=(~imissX)
        n_obs_SNP=i_nonan.sum(0)
        X[imissX]=0.0
    snp_sum=(X).sum(0)
    one_over_sqrt_pi=(1.0+snp_sum)/(2.0+maxval*n_obs_SNP)
    one_over_sqrt_pi=1./SP.sqrt(one_over_sqrt_pi*(1.-one_over_sqrt_pi))
    snp_mean=(snp_sum*1.0)/(n_obs_SNP)
    X_ret=X-snp_mean
    X_ret*=one_over_sqrt_pi
    if imissX is not None:
        X_ret[imissX]=0.0
    return X_ret


