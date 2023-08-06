import scipy.stats as st
import numpy as NP
cimport numpy as NP
from libcpp cimport bool

cdef extern from "numpy/arrayobject.h":
    ctypedef int intp
    ctypedef extern class numpy.ndarray [object PyArrayObject]:
        cdef char *data
        cdef int nd
        cdef intp *dimensions
        cdef intp *strides
        cdef int flags


###nLLeval
cdef extern from "lmm.h": 
    double c_nLLeval "nLLeval" (double ldelta,double* dUY,double* dUX,double* dS,int n,int d)
    double c_optdelta "optdelta" (double* dUY,double* dUX,double* dS,int n,int d,int numintervals,double ldeltamin,double ldeltamax)
    void c_train_associations "train_associations" (double* dLOD,double* dX,double* dY,double* dK,double* dC,int nn,int ns,int np,int nc,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0)
    void c_train_interactions "train_interactions" (double* dPVALS,double* dLOD,double* dX,double* dY,double* dK,double* dC,double* dI,int nn,int ns,int np,int nc,int ni,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp, bool use_ftest)

    void c_train_associations_SingleSNP "train_associations_SingleSNP" ( double* PV, double* LL, double* ldelta, double* X, double* Y, double* U, double* S, double* C, int nn,int ns,int np,int nc, int numintervals, double ldeltamin, double ldeltamax)

def ndarrayF64toC(ndarray A):
    #transform numpy object to enforce Fortran contiguous byte order 
    #(meaining column-first order for Cpp interfacing)
    return NP.asarray(A, order="F")
#   OLD and c-tingous version
#     assert (<object>A).dtype == NP.float64
#     if not (<object>A).flags["C_CONTIGUOUS"]:
#         Ac = A.copy('C')
#     else:
#         Ac = A
#     return Ac
        
def train_associations(ndarray X,ndarray Y,ndarray K,ndarray C,int numintervalsAlt=0,double ldeltaminAlt=-1,double ldeltamaxAlt=1,int numintervals0=100,double ldeltamin0=-5,double ldeltamax0=5,calc_pval=True):
    #1. get dimensions
    cdef int nn = X.dimensions[0]
    cdef int ns = X.dimensions[1]
    cdef int np = Y.dimensions[1]
    cdef int nc = C.dimensions[1]
    #2. create result structure for LOD
    cdef NP.ndarray LOD=NP.zeros([np,ns],dtype=NP.float)
    #3. get raw data pointers
    X = ndarrayF64toC(X)
    Y = ndarrayF64toC(Y)
    K = ndarrayF64toC(K)
    C = ndarrayF64toC(C)
    LOD = ndarrayF64toC(LOD)  
    cdef double *dY = <double* > Y.data
    cdef double *dX = <double* > X.data
    cdef double *dK = <double* > K.data
    cdef double *dC = <double* > C.data
    cdef double *dLOD = <double*> LOD.data               
    #4. call C
    c_train_associations(dLOD,dX,dY,dK,dC,nn,ns,np,nc,numintervalsAlt,ldeltaminAlt,ldeltamaxAlt,numintervals0,ldeltamin0,ldeltamax0)
    #5. return
    if calc_pval:
        pval = st.chi2.sf(2*(LOD),1)
        return LOD, pval
    else:
        return LOD
   
def train_interactions(ndarray X,ndarray Y,ndarray K,ndarray C,ndarray Inter,int numintervalsAlt=0,double ldeltaminAlt=-1,double ldeltamaxAlt=1,int numintervals0=100,double ldeltamin0=-5,double ldeltamax0=5,bool refit_delta0_snp=False,use_ftest=False):
    #1. get dimensions
    cdef int nn = X.dimensions[0]
    cdef int ns = X.dimensions[1]
    cdef int np = Y.dimensions[1]
    cdef int nc = C.dimensions[1]
    cdef int ni = Inter.dimensions[1]
    #2. create result structure for final pvalues
    cdef NP.ndarray PV=NP.zeros([np,ns],dtype=NP.float,order="F")
    cdef NP.ndarray LOD=NP.zeros([np,ns],dtype=NP.float,order="F")	
    #3. get raw data pointers
    X = ndarrayF64toC(X)
    Y = ndarrayF64toC(Y)
    K = ndarrayF64toC(K)
    C = ndarrayF64toC(C)
    Inter = ndarrayF64toC(Inter)
    PV = ndarrayF64toC(PV)  
    LOD = ndarrayF64toC(LOD)	
    cdef double *dY = <double* > Y.data
    cdef double *dX = <double* > X.data
    cdef double *dK = <double* > K.data
    cdef double *dC = <double* > C.data
    cdef double *dInter = <double*> Inter.data
    cdef double *dPV = <double*> PV.data               
    cdef double *dLOD = <double*> LOD.data               
    #4. call C
    c_train_interactions(dPV,dLOD,dX,dY,dK,dC,dInter,nn,ns,np,nc,ni,numintervalsAlt,ldeltaminAlt,ldeltamaxAlt,numintervals0,ldeltamin0,ldeltamax0,refit_delta0_snp,use_ftest)
    return LOD,PV

def train_associations_SingleSNP( ndarray X, ndarray Y, ndarray U, ndarray S, ndarray C, int numintervals = 100, double ldeltamin = -10.0, double ldeltamax = 10.0):
    #1. get dimensions
    cdef int nn = X.dimensions[0]
    cdef int ns = X.dimensions[1]
    cdef int np = Y.dimensions[1]
    cdef int nc = C.dimensions[1]
    #2. create result structure for final pvalues
    cdef NP.ndarray PV=NP.zeros([np,ns],dtype=NP.float,order="F")
    cdef NP.ndarray LL=NP.zeros([np,ns],dtype=NP.float,order="F")
    cdef NP.ndarray ldelta=NP.zeros([np,ns],dtype=NP.float,order="F")
    #3. get raw data pointers
    X = ndarrayF64toC(X)
    Y = ndarrayF64toC(Y)
    S = ndarrayF64toC(S)
    U = ndarrayF64toC(U)
    C = ndarrayF64toC(C)
    U = ndarrayF64toC(U)
    S = ndarrayF64toC(S)	
    PV = ndarrayF64toC(PV)  
    LL = ndarrayF64toC(LL)  
    ldelta = ndarrayF64toC(ldelta)  
    cdef double *dY = <double* > Y.data
    cdef double *dX = <double* > X.data
    cdef double *dU = <double* > U.data
    cdef double *dS = <double* > S.data
    cdef double *dC = <double* > C.data
    cdef double *dPV = <double*> PV.data
    cdef double *dLL = <double*> LL.data
    cdef double *dldelta = <double*> ldelta.data               
    #4. call C
    c_train_associations_SingleSNP( dPV, dLL, dldelta, dX, dY, dU, dS, dC, nn, ns, np, nc, numintervals, ldeltamin, ldeltamax)
    return PV,LL,ldelta

          
def optdelta(ndarray UY,ndarray UX,ndarray S):
    UX = ndarrayF64toC(UX)
    UY = ndarrayF64toC(UY)
    S = ndarrayF64toC(S)
    cdef double *dUX = <double*> UX.data
    cdef double *dUY = <double*> UY.data
    cdef double *dS = <double*> S.data
    cdef int n = UX.dimensions[0]
    cdef int d = UX.dimensions[1]
    return c_optdelta(dUY,dUX,dS,n,d,100,-10.,10.)


def nLLeval(double ldelta,ndarray UY,ndarray UX,ndarray S):
    UX = ndarrayF64toC(UX)
    UY = ndarrayF64toC(UY)
    S = ndarrayF64toC(S)
    cdef double *dUX = <double*> UX.data
    cdef double *dUY = <double*> UY.data
    cdef double *dS = <double*> S.data
    cdef int n = UX.dimensions[0]
    cdef int d = UX.dimensions[1]
    return c_nLLeval(ldelta,dUY,dUX,dS,n,d)
###


