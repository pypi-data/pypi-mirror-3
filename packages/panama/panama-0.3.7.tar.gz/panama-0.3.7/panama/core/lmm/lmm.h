#ifndef LMM_H
#define LMM_H

#include <stdlib.h>
#include <math.h>
#include <iostream>
#include <stdio.h>
#include <cmath>

//global variable
const double _PI = (double)2.0*std::acos((double)0.0);
const double _log2pi=std::log((double)2.0*_PI);

#include "Eigen/Eigen"
#include "utils/MathFunctions.h"
#include "utils/Gamma.h"
#include "utils/Beta.h"
#include "utils/FisherF.h"
#include "utils/BrentC.h"

//get eigen namespace in
using namespace Eigen;


//standard Matrix types that maybe useful here:
//we use columnmajor here because it is more efficient for the LMM code (Note that rowMajor is the order in python)
typedef Matrix<double, Dynamic, Dynamic, ColMajor> PMatrix;
typedef Matrix<double, Dynamic,1> PVector;


//Pythonic versions of the interface
double nLLeval(double ldelta,double* dUY,double* dUX,double* dS,int n,int d);
double optdelta(double* dUY,double* dUX,double* dS,int n,int d,int numintervals=100,double ldeltamin=-10,double ldeltamax=+10);
void train_associations(double* dLOD,double* dX,double* dY,double* dK,double* dC,int nn,int ns,int np,int nc,int numintervalsAlt=0,double ldeltaminAlt=-1,double ldeltamaxAlt=+1,int numintervals0=100,double ldeltamin0=-5,double ldeltamax0=+5);
void train_interactions(double* dPVALS,double* dLOD,double* dX,double* dY,double* dK,double* dC,double* dI,int nn,int ns,int np,int nc,int ni,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp, bool use_ftest);
void train_associations_SingleSNP( double* PV, double* LL, double* ldelta, double* X, double* Y, double* U, double* S, double* C, int nn,int ns,int np,int nc, int numintervals, double ldeltamin, double ldeltamax);


// Proper C/C++ versions
inline double nLLeval(PMatrix & F_tests, double ldelta,const PMatrix& UY,const PMatrix& UX,const PMatrix& S);
inline double optdelta(const PMatrix& UY,const PMatrix& UX,const PMatrix& S,int numintervals=100,double ldeltamin=-10,double ldeltamax=10);

void train_associations(PMatrix& LOD,const PMatrix& X,const PMatrix& Y,const PMatrix& K,const PMatrix& C,int numintervalsAlt=0,double ldeltaminAlt=-1,double ldeltamaxAlt=+1,int numintervals0=100,double ldeltamin0=-5,double ldeltamax0=+5);
void train_interactions(PMatrix& pvals,PMatrix& LOD,const PMatrix& X,const PMatrix& Y,const PMatrix& K,const PMatrix& C,const PMatrix& I,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp, bool use_ftest);
void train_associations_SingleSNP(PMatrix& PV, PMatrix& LL, PMatrix& ldelta, const PMatrix& X,const PMatrix& Y,const PMatrix& U, const PMatrix& S, const PMatrix& C, int numintervals, double ldeltamin, double ldeltamax);
//CLMM class which handles LMM computations


#endif //LMM_H
