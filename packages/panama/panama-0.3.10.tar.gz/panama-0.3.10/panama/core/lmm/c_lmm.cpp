#if !defined(c_lmm_cpp)
#define c_lmm_cpp

#include "lmm.h"
#include <assert.h>


bool VERBOSE=false;

const double L2pi=1.8378770664093453;
#define etadouble const 

/* Python interface functions*/


double nLLeval(double ldelta,double* dUY,double* dUX,double* dS,int n,int d)
   {
   //1. map matrix to the one we want
   Map<PMatrix > UX(dUX,n,d);
   Map<PMatrix > UY(dUY,n,1);
   Map<PMatrix > S (dS,n,1);
   PMatrix F_tests;
   return nLLeval(F_tests,ldelta,UY,UX,S);
   }


double optdelta(double* dUY,double* dUX,double* dS,int n,int d,int numintervals,double ldeltamin,double ldeltamax)
{
  //1. map matrix to the one we want
  Map<PMatrix > UX(dUX,n,d);
  Map<PMatrix > UY(dUY,n,1);
  Map<PMatrix > S (dS,n,1);
  //std::cout << numintervals << "," << ldeltamin << "," << ldeltamax;
  return optdelta(UY,UX,S,numintervals,ldeltamin,ldeltamax); //1. map matrix to the one we want
}

void train_associations(double* dLOD,double* dX,double* dY,double* dK,double* dC,int nn,int ns,int np,int nc,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0)
{

	//1. map matrix objects
	Map<PMatrix > X(dX,nn,ns);
	Map<PMatrix > Y(dY,nn,np);
	Map<PMatrix > C(dC,nn,nc);
	Map<PMatrix > K(dK,nn,nn);

	//reserve fresh matrix for LOD
	PMatrix  LOD(np,ns);
	train_associations(LOD,X,Y,K,C,numintervalsAlt,ldeltaminAlt,ldeltamaxAlt,numintervals0,ldeltamin0,ldeltamax0);
	//copy memory for output
	memcpy(dLOD,LOD.data(), sizeof(double)*np*ns);
}

void train_interactions(double* dPvals,double* dLOD,double* dX,double* dY,double* dK,double* dC,double* dI,int nn,int ns,int np,int nc,int ni,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp, bool use_ftest)
{
	//1. map matrix objects
		Map<PMatrix > X(dX,nn,ns);
		Map<PMatrix > Y(dY,nn,np);
		Map<PMatrix > C(dC,nn,nc);
		Map<PMatrix > K(dK,nn,nn);
		Map<PMatrix > I(dI,nn,ni);

		//reserve fresh matrix for LOD
		PMatrix  pvals(np,ns);
		PMatrix  LOD(np,ns);
		train_interactions(pvals,LOD,X,Y,K,C,I,numintervalsAlt,ldeltaminAlt,ldeltamaxAlt,numintervals0,ldeltamin0,ldeltamax0,refit_delta0_snp, use_ftest);
		//copy memory for output
		memcpy(dPvals,pvals.data(), sizeof(double)*np*ns);
		memcpy(dLOD,LOD.data(),sizeof(double)*np*ns);
}

void train_associations_SingleSNP( double* PV, double* LL, double* ldelta, double* X, double* Y, double* U, double* S, double* C, int nn,int ns,int np,int nc, int numintervals, double ldeltamin, double ldeltamax)
{
	assert(ns==1);

	//1. map matrix objects
		Map<PMatrix > mX(X,nn,ns);
		Map<PMatrix > mY(Y,nn,np);
		Map<PMatrix > mC(C,nn,nc);
		Map<PMatrix > mU(U,nn,nn);
		Map<PMatrix > mS(S,nn,1);

		//reserve fresh matrix for LOD
		PMatrix  mPV(np,ns);
		PMatrix mLL(np,ns);
		PMatrix mldelta(np,ns);
		train_associations_SingleSNP(mPV, mLL, mldelta, mX, mY, mU, mS, mC, numintervals, ldeltamin, ldeltamax);
		//copy memory for output
		memcpy(PV,mPV.data(), sizeof(double)*np*ns);
		memcpy(LL,mLL.data(), sizeof(double)*np*ns);
		memcpy(ldelta,mldelta.data(), sizeof(double)*np*ns);
}



/* Internal C++ functions */
inline double nLLeval(PMatrix& F_tests, double ldelta,const PMatrix& UY,const PMatrix& UX,const PMatrix& S)
   {
   size_t n = UX.rows();
   size_t d = UX.cols();
   assert(UY.cols() == 1);
   /*
   std::cout << UX<< "\n\n";
   std::cout << UY<< "\n\n";
   std::cout << S<< "\n\n";
   */
   
   double delta = exp(ldelta);
   PMatrix Sdi = S.array() + delta;
   double ldet = 0.0;
   for (size_t ind = 0; ind < n; ++ind)
      {
      ldet += log(Sdi.data()[ind]);
      }
   //std::cout << "ldet" << ldet << "\n\n";
   //elementwise inverse
   Sdi = Sdi.array().inverse();
   
   //replice Sdi
   PMatrix XSdi = (UX.array()*Sdi.replicate(1,d).array()).transpose();
   
   PMatrix XSX=XSdi*UX;
   PMatrix XSY=XSdi*UY;

   //least sqaures solution of XSX*beta = XSY
   //decomposition of K
	SelfAdjointEigenSolver<PMatrix> eigensolver(XSX);
	   
   PMatrix U_X = eigensolver.eigenvectors();
PMatrix S_X = eigensolver.eigenvalues();
   
   //std::cout << "XSX\n" << XSX << "\n\n";

   //std::cout << "XSX_reconstr\n" << U_X * S_X.asDiagonal() * U_X.transpose() << "\n\n";

   //std::cout << "\nS_X : \n" << S_X << "\n\n";

   PMatrix beta = U_X.transpose() * XSY;
   
   F_tests=PMatrix::Zero(d,1);
   
   //PMatrix S_i = PMatrix::Zero(d,d);
   for(size_t dim = 0; dim < d; ++dim)
      {
      if (S_X(dim,0)>3E-8)
         {
         beta(dim)/=S_X(dim,0);
         //S_i(dim,dim) = 1.0/S_X(dim,0);
         for(size_t dim2 = 0; dim2<d; ++dim2)
            {
            F_tests(dim2,0)+= U_X(dim2,dim)*U_X(dim2,dim)/S_X(dim,0);
            }
         }
      else
         {
         beta(dim)=0.0;
         }
      }
   

   beta=U_X*beta;
   

   PMatrix res  = UY-UX*beta;
   
   //sqared residuals
   res.array()*=res.array();
   res.array()*=Sdi.array();
   double sigg2 = res.array().sum()/n;
   
   //compute the F-statistics
   F_tests.array()=beta.array()*beta.array()/F_tests.array();
   F_tests.array()/=sigg2;
   
   double nLL   = 0.5*(n*L2pi+ldet+n+n*log(sigg2));
   return nLL;
   }

/* Internal C++ functions */
inline PMatrix nLLevalAllY(double ldelta,const PMatrix& UY,const PMatrix& UX,const PMatrix& S)
   {
   size_t n = UX.rows();
   size_t d = UX.cols();
   size_t p = UY.cols();

   /*
   std::cout << UX<< "\n\n";
   std::cout << UY<< "\n\n";
   std::cout << S<< "\n\n";
   */
   
   double delta = exp(ldelta);
   PMatrix Sdi = S.array() + delta;
   double ldet = Sdi.array().log().sum();
   
   //std::cout << "ldet" << ldet << "\n\n";
   //elementwise inverse
   Sdi = Sdi.array().inverse();
   //std::cout << "Sdi" << Sdi << "\n\n";

   //replice Sdi
   PMatrix XSdi = (UX.array()*Sdi.replicate(1,d).array()).transpose();
   

   PMatrix XSX=XSdi*UX;
   PMatrix XSY=XSdi*UY;
   
   //std::cout << "XSdi" << XSdi << "\n\n";
   //std::cout << "XSX" << XSX << "\n\n";

   //least squares solution of XSX*beta = XSY
   PMatrix beta = XSX.colPivHouseholderQr().solve(XSY);
   PMatrix res  = UY-UX*beta;
   //squared residuals
   res.array()*=res.array();
   res.array()*=Sdi.replicate(1,p).array();
   //PMatrix sigg2 = PMatrix(1,p);
   PMatrix nLL = PMatrix(1,p);
   for (size_t phen = 0; phen < p; ++phen)
      {
      double sigg2 = res.col(phen).array().sum()/n;
      nLL(0,phen)   = 0.5*(n*L2pi+ldet+n+n*log(sigg2));
      }
   return nLL;
   }


double optdelta(const PMatrix& UY,const PMatrix& UX,const PMatrix& S,int numintervals,double ldeltamin,double ldeltamax)
{
       //grid variable with the current likelihood evaluations
       PMatrix nllgrid     = PMatrix::Ones(numintervals,1).array()*HUGE_VAL;
       PMatrix ldeltagrid = PMatrix::Zero(numintervals,1); 

  	//current delta
	double ldelta  = ldeltamin;
	double ldeltaD = (ldeltamax-ldeltamin);
	ldeltaD/=((double)numintervals-1);
	double nllmin = HUGE_VAL;
	double ldeltaopt_glob = 0;

   PMatrix f_tests;
	for (int i=0;i<(numintervals);i++)
	{
	  nllgrid(i,0) = nLLeval(f_tests, ldelta,UY,UX,S);
	  ldeltagrid(i,0) = ldelta;
	  //std::cout<< "nnl( " << ldelta << ") = " << nllgrid(i,0) <<  "VS" << nllmin << ")\n\n";
		if (nllgrid(i,0)<nllmin)
		{
		  //		std::cout << "new min (" << nllmin << ") -> " <<  nllgrid(i,0) << "\n\n";
			nllmin = nllgrid(i,0);
			ldeltaopt_glob = ldelta;
		}
		//move on delta
		ldelta += ldeltaD;
	}//end for all intervals

   //std::cout << "\n\n nLL_i:\n" << nllgrid;
	return ldeltaopt_glob;
}

PMatrix optdeltaAllY( const PMatrix& UY, const PMatrix& UX, const PMatrix& S, const PMatrix& ldeltagrid)
   {
   size_t n_p = UY.cols();
   size_t numintervals = ldeltagrid.rows();
   
   //grid variable with the current likelihood evaluations
   PMatrix nllgrid    = PMatrix::Ones(numintervals,n_p).array()*HUGE_VAL;
   
   //current delta
   
   for (size_t i=0;i<numintervals;i++)
      {
      nllgrid.row(i) = nLLevalAllY(ldeltagrid(i,0),UY,UX,S);
      //ldeltagrid(0,i) = ldelta;
      
      }//end for all intervals
   return nllgrid;
   }



void train_associations(PMatrix& LOD,const PMatrix& X,const PMatrix& Y,const PMatrix& K,const PMatrix& C,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0)
{
	//get dimensions:
	//samples
	int nn = X.rows();
	//snps
	int ns = X.cols();
	//phenotypes
	int np = Y.cols();
	//covaraites
	int nc = C.cols();
	//make sure the size of N/Y is correct
	assert(nn==Y.rows());
	assert(nn==C.rows());

	//resize output variable if needed
	LOD.resize(np,ns);

	//decomposition of K
	SelfAdjointEigenSolver<PMatrix> eigensolver(K);
	PMatrix U = eigensolver.eigenvectors();
	PMatrix S = eigensolver.eigenvalues();

	//transform everything
	PMatrix UX = U.transpose()*X;
	PMatrix UY = U.transpose()*Y;
	PMatrix Ucovariates = U.transpose()*C;

	//result matries: think about what to store in the end
	PMatrix ldelta0(np,1);
	PMatrix ldelta(np,ns);
	PMatrix nLL0(np,1);
	PMatrix nLL(np,ns);

	//reserve memory for snp-wise foreground model
	PMatrix UX_(nn,nc+1);
	//store covariates upfront
	UX_.block(0,0,nn,nc) = Ucovariates;
   PMatrix f_tests;
	for (int ip=0;ip<np;ip++)
	{
		//get UY columns
		PMatrix UY_ = UY.block(0,ip,nn,1);
		//fit delta on null model
		ldelta0(ip) = optdelta(UY_,Ucovariates,S,numintervals0,ldeltamin0,ldeltamax0);
		// std::cout << ip << ":"<<ldelta0(ip) <<"\n";
		nLL0(ip)   = nLLeval(f_tests,ldelta0(ip),UY_,Ucovariates,S);
		for (int is=0;is<ns;is++)
		{
			//1. construct foreground testing SNP transformed
			UX_.block(0,nc,nn,1) = UX.block(0,is,nn,1);
			//2. fit delta
			if (numintervalsAlt>0)
				//fit delta on alt model also
				ldelta(ip,is) = optdelta(UY_,UX_,S,numintervalsAlt,ldelta0(ip)+ldeltaminAlt,ldelta0(ip)+ldeltamaxAlt);
			else
				ldelta(ip,is) = ldelta0(ip);
			//3. evaluate
         PMatrix f_tests;
			nLL(ip,is) = nLLeval(f_tests,ldelta(ip,is),UY_,UX_,S);
			//4. calc lod score
			LOD(ip,is) = (-1.0)*(nLL(ip,is)-nLL0(ip));
		} //end for SNP
	}//end for phenotypes
}



void train_interactions(PMatrix& pvals, PMatrix& LOD,const PMatrix& X, const PMatrix& Y, const PMatrix& K, const PMatrix& C, const PMatrix& I,int numintervalsAlt, double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp, bool use_ftest)
   {
	//get dimensions:
	//samples
	int nn = X.rows();
	//snps
	int ns = X.cols();
	//phenotypes
	int np = Y.cols();
	//covaraites
	int nc = C.cols();
	//interaction partners
	int ni = I.cols();
	//make sure the size of N/Y is correct
	assert(nn==Y.rows());
	assert(nn==C.rows());
	assert(nn==I.rows());

	//resize output variable if needed
	pvals.resize(np,ns);
	LOD.resize(np,ns);

	//decomposition of K
	SelfAdjointEigenSolver<PMatrix> eigensolver(K);
	PMatrix U = eigensolver.eigenvectors();
	PMatrix S = eigensolver.eigenvalues();

	//transform everything
	PMatrix UX = U.transpose()*X;
	PMatrix UY = U.transpose()*Y;
	PMatrix Ucovariates = U.transpose()*C;
	PMatrix Uinter      = U.transpose()*I;

	//result matries: think about what to store in the end
	PMatrix ldelta0(np,1);
	PMatrix ldelta(np,ns);
	PMatrix nLL0(np,ns);
	PMatrix nLL(np,ns);

#if 0
   PMatrix ldelta0_(np,1);
   PMatrix ldeltagrid(numintervals0,1);
   for (size_t interval = 0; interval < numintervals0; ++interval)
      {
      ldeltagrid(interval,0) = ldeltamin0 + interval*((ldeltamax0 - ldeltamin0)/(1.0*(numintervals0-1)));
      }
   //std::cout << "\n\n grid:\n" << ldeltagrid;
   PMatrix nllgrid = optdeltaAllY(UY, Ucovariates, S, ldeltagrid);
   //std::cout << "\n\n nLL:\n" << nllgrid;
	//1. fit background covariances on phenotype and covariates alone
	for (int ip=0;ip<np;ip++)
		{
			//get UY columns
			PMatrix UY_ = UY.block(0,ip,nn,1);
			//fit delta on null model without any background
			ldelta0(ip) = optdelta(UY_,Ucovariates,S,numintervals0,ldeltamin0,ldeltamax0);
         ldelta0_(ip) = ldeltamin0;
         size_t i_min = 0;
         for(size_t interval = 1; interval < numintervals0; ++interval)
            {
            if(nllgrid(interval,ip)<nllgrid(i_min,ip))
               {
               ldelta0_(ip) = ldeltagrid(interval,0);
               i_min = interval;
               }
            }
		}
   std::cout << "\n\n ldelta0:\n" << ldelta0;
   std::cout << "\n\n ldelta0_:\n" << ldelta0_;
#else
   PMatrix ldeltagrid(numintervals0,1);
   for (size_t interval = 0; interval < (size_t)numintervals0; ++interval)
      {
      ldeltagrid(interval,0) = ldeltamin0 + interval*((ldeltamax0 - ldeltamin0)/(1.0*(numintervals0-1)));
      }
   //std::cout << "\n\n grid:\n" << ldeltagrid;
   PMatrix nllgrid = optdeltaAllY(UY, Ucovariates, S, ldeltagrid);
   //std::cout << "\n\n nLL:\n" << nllgrid;
	//1. fit background covariances on phenotype and covariates alone
   for (size_t ip=0;ip<(size_t)np;ip++)
		{
		ldelta0(ip) = ldeltamin0;
         size_t i_min = 0;
         for(size_t interval = 1; interval < (size_t)numintervals0; ++interval)
            {
            if(nllgrid(interval,ip)<nllgrid(i_min,ip))
               {
   
               ldelta0(ip) = ldeltagrid(interval,0);
               i_min = interval;
               }
            }
		}
#endif
	//store template for foreground covariance
	PMatrix UX_(nn,nc+ni+ni+1);
	UX_.block(0,0,nn,nc)   = Ucovariates;
	UX_.block(0,nc,nn,ni)  = Uinter;
	//store template for background covariance
	PMatrix Ucovariates_(nn,nc+ni+1);
	Ucovariates_.block(0,0,nn,nc)   = Ucovariates;
	Ucovariates_.block(0,nc,nn,ni)  = Uinter;

	for (int is=0;is<ns;is++)
	   {
		//1. update background and frorground contributions
		Ucovariates_.block(0,nc+ni,nn,1) = UX.block(0,is,nn,1);
		UX_.block(0,nc+ni,nn,1) = UX.block(0,is,nn,1);
		//2. calculate and add interaction term
		// (elemnetwise product of X at SNP with all interaction terms
		PMatrix Xi = I.array()*X.block(0,is,nn,1).replicate(1,ni).array();
		//transform
		PMatrix UXi = U.transpose()*Xi;
		//add to foreground covariance
		UX_.block(0,nc+ni+1,nn,ni) = UXi;

		for (int ip=0;ip<np;ip++)
		   {
			//get UY columns
			PMatrix UY_ = UY.block(0,ip,nn,1);

			double _ldelta0 = ldelta0(ip);
			double _ldelta   = ldelta0(ip);
			//refit 0 model per SNP?
			if (!use_ftest && refit_delta0_snp)
				_ldelta0 = optdelta(UY_,Ucovariates_,S,numintervals0,ldeltamin0,ldeltamax0);
			//fit foreground model?
			if (numintervalsAlt>0)
			   {
				//fit delta on alt model also
				_ldelta = optdelta(UY_,UX_,S,numintervalsAlt,_ldelta0+ldeltaminAlt,_ldelta0+ldeltamaxAlt);
				ldelta(ip,is) = _ldelta;
			   }
			//evaluate null and foreground model
         PMatrix f_tests;
         
         nLL(ip,is)   = nLLeval(f_tests,_ldelta,UY_,UX_,S);
			         
         if(!use_ftest)
            {
            nLL0(ip,is)   = nLLeval(f_tests,_ldelta0,UY_,Ucovariates_,S);
            //4. calc lod score
	    LOD(ip,is) = (-1.0)*(nLL(ip,is)-nLL0(ip,is));
            //calc p-value
            pvals(ip,is) = Gamma::gammaQ(nLL0(ip,is)-nLL(ip,is),(double)0.5*1.0);
            }
         else
            {
            //calc p-value
            pvals(ip,is) = 1.0 -FisherF::Cdf(f_tests(nc+ni+1),1.0 , (double)(nn - f_tests.rows()));
            }
         //double pval_F = 1.0 -FisherF::Cdf(f_tests(nc+ni+1),1.0 , (double)(nn - f_tests.rows()));
         //double pval_LRT=Gamma::gammaQ(nLL0(ip,is)-nLL(ip,is),(double)0.5*1.0);
         //printf("nLL0 : %.4f nLL : %.4f F: %.4f, LRT %.4f, \ndiff = %.4f, fstat: %.4f, p_f: %.4f\n",nLL0(ip,is),nLL(ip,is), log(pval_F),log(pval_LRT),log(pval_F)-log(pval_LRT),f_tests(nc+ni+1), FisherF::Cdf(f_tests(nc+ni+1),1.0 , (double)(nn - f_tests.rows())));
         //printf("\n");
	   	}// :: for pheno
	   }// :: for snp

   }

void train_associations_SingleSNP(PMatrix& PV, PMatrix& LL, PMatrix& ldelta, const PMatrix& X,const PMatrix& Y,const PMatrix& U, const PMatrix& S, const PMatrix& C, int numintervals, double ldeltamin, double ldeltamax)
	{
	//get dimensions:
	//samples
	size_t nn = X.rows();
	//snps
	size_t ns = X.cols();
	assert( ns == 1 );
	//phenotypes
	size_t np = Y.cols();
	//covaraites
	size_t nc = C.cols();
	//make sure the size of N/Y is correct
	assert(nn==Y.rows());
	assert(nn==C.rows());

	//resize output variable if needed
	PV.resize(np,ns);
	LL.resize(np,ns);

	//transform everything
	PMatrix UX = U.transpose()*X;
	PMatrix UY = U.transpose()*Y;
	PMatrix Ucovariates = U.transpose()*C;

	//result matrices: think about what to store in the end
	//PMatrix ldelta(np,ns);

	//reserve memory for snp-wise foreground model
	PMatrix UX_(nn,nc+1);
	//store covariates upfront
	UX_.block(0,0,nn,nc) = Ucovariates;
	UX_.block(0,nc,nn,1) = UX;
    PMatrix ldeltagrid(numintervals,1);

   for (size_t interval = 0; interval < (size_t)numintervals; ++interval)
	  {
	  ldeltagrid(interval,0) = ldeltamin + interval*((ldeltamax - ldeltamin)/(1.0*(numintervals-1)));
	  }
	//std::cout << "\n\n grid:\n" << ldeltagrid;
	PMatrix nllgrid = optdeltaAllY(UY, UX_, S, ldeltagrid);
	//std::cout << "\n\n nLL:\n" << nllgrid;
	//1. fit background covariances on phenotype and covariates alone
	for (size_t ip=0;ip<np;ip++)
		{
		ldelta(ip) = ldeltamin;
		 size_t i_min = 0;
		   for(size_t interval = 1; interval < (size_t)numintervals; ++interval)
			{
			if(nllgrid(interval,ip)<nllgrid(i_min,ip))
			   {
				//printf("oldmin : %.4f, newmin : %.4f, newdelta : %.4f, interval : %i\n" ,nllgrid(i_min,ip) , nllgrid(interval,ip), ldeltagrid(interval,0),interval);
			   ldelta(ip) = ldeltagrid(interval,0);
			   i_min = interval;
			   }
			}
		 //get UY columns
		 		PMatrix UY_ = UY.block(0,ip,nn,1);
		 		//fit delta on null model
		 		PMatrix f_tests(nc+1,1);
		 		LL(ip)   = -1.0*nLLeval(f_tests, ldelta(ip), UY_, UX_, S);
		 		PV(ip) = 1.0-FisherF::Cdf(f_tests(1,0), 1.0 , (double)(nn - f_tests.rows()));
				  //printf("ip : %i, ldelta : %.4f, PV: %.4f LL: %.4f\n", (int)ip, ldelta(ip),(PV(ip)),LL(ip));
				  //  for(size_t dim = 0; dim<(size_t)f_tests.rows();++dim)
				//	{
					//  printf("f[%i] : %.4f, ",(int)dim,f_tests(dim));
					//}
		 		//if( FisherF::Cdf(f_tests(f_tests.rows()-1,0), 1.0 , (double)(nn - f_tests.rows())) < 0.0 )
		 			//{
		 			//printf("\noutch!");//3.1756

					 // printf("  LLmin: %.4f nn:%i dim:%i F(3.1756):%.4f \n", nllgrid(i_min,ip), (int)nn, (int) f_tests.rows(),FisherF::Cdf(3.0, 1.0 , 18.0));
		 			//LL(ip)   = -1.0 * nLLeval(f_tests, ldelta(ip), UY_, UX_, S);
		 			//}


		 		//printf("\n\n");
		   }

   	}

#endif //c_lmm_cpp
