import scipy.stats as ST
import scipy as SP
import matplotlib.pylab as PL
def qq_plot(pval=None, filename=None, distr='chi2'):
    """
    draws a QQ plot for a set of pvalues
    Input:
    pval     pvalues 1-dimensional double array, values between 0 and 1
    distr    string indicating the type of distribution [chi2]
    """
    if distr=='chi2':
        n_tests=pval.shape[0];
        pnull=(SP.arange(n_tests)+.5)/n_tests;
        qnull=ST.chi2.isf(pnull,1);
        
        qemp=(ST.chi2.isf(SP.sort(pval),1));
        PL.figure();
        PL.plot(qnull,qemp,'.');
        PL.plot(qnull,qnull);
        PL.ylabel('LOD scores')
        PL.xlabel('$\chi^2$ quantiles')
        if filename is not None:
            PL.savefig(filename)
              
        
        
