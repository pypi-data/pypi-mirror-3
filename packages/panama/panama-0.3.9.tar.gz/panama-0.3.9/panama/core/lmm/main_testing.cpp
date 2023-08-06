/*
 *  Testing script for LMM library
 *
 */

#if !defined(main_testing_cpp)
#define main_testing_cpp

#include "lmm.h"
#include <iostream>

int main (int argc, char * const argv[]) {
	
	if (0)
		{
		//simulate a small problem and run LMM

		//size
		size_t n_samples = 20;
		size_t n_snps  = 100;
		size_t n_pheno = 100;
		//size_t n_cov   = 1;

		//simulate...
		PMatrix X(n_samples,n_snps);
		PMatrix Y(n_samples,n_pheno);
		PMatrix K(n_samples,n_samples);
		PMatrix C = PMatrix::Ones(n_samples,1);
		//PMatrix C(n_samples,1);
	   //C.setRandom();
	   X.setRandom();

	   Y.setRandom();


	   //1 interaction factor
		PMatrix I(n_samples,1);
	   I.setRandom();

		K.setRandom();
	   K=K*K.transpose();
	   for(size_t i=0; i<n_samples; ++i)
		  {
		  K(i,i)+=1.0;
		  }
	   SelfAdjointEigenSolver<PMatrix> eigensolver(K);

	   PMatrix U = eigensolver.eigenvectors();
		PMatrix S = eigensolver.eigenvalues();

	   Y =  U.transpose() * Y;
	   PMatrix S_sqr = PMatrix::Zero(n_samples,n_samples);
	   for(size_t i=0; i<n_samples;++i)
		  {
		  S_sqr(i,i) = sqrt(S(i,0));
		  }
	   Y=S_sqr*Y;

	   
		//std::cout << K;
		//std::cout <<"\n\nX:\n"<< X;
		//std::cout <<"\n\nY:\n"<< Y;

		//create LOD matrix
		PMatrix LOD(n_pheno,n_snps);


		train_interactions(LOD,X,Y,K,C,I,0,-1.,1.,100,-5,5,false,true);
		std::cout <<"\n\nPV:\n"<< LOD;
		printf("\n\nFisher:%.4f",FisherF::Cdf(0.1,1.0,1.0));

		}
	else
		{
		//size
		size_t n_samples = 1200;
		size_t n_snps  = 1;
		size_t n_pheno = 10000;
		//size_t n_cov   = 1;


		//simulate...
		//PMatrix X = PMatrix::Ones(n_samples,n_snps);
		PMatrix X(n_samples,n_snps);
		PMatrix Y= PMatrix::Ones(n_samples,n_pheno);
		PMatrix K= PMatrix::Zero(n_samples,n_samples);
		PMatrix C = PMatrix::Ones(n_samples,1);
		//PMatrix C(n_samples,1);
	   //C.setRandom();
	   X.setRandom();
	   Y.setRandom();
      PMatrix Y1(n_samples, n_pheno);
      Y1.setRandom();
	   PMatrix Y2(n_samples, n_pheno);
	   Y2.setRandom();
      double pi_=2.0*acos(0.0);
      for(size_t sample = 0;sample<n_samples;++sample)
         {
         for(size_t phen = 0;phen<n_pheno;++phen)
            {
            Y(sample,phen) = std::sqrt(-2.0*std::log(Y1(sample,phen)*0.5+0.5))*std::cos(pi_*(Y2(sample,phen)-1.0));
            }
         }


	   K.setRandom();
	   K=1.0/n_samples *K*K.transpose();
	   for(size_t i=0; i<n_samples; ++i)
		  {
		  K(i,i)+=1E-6;
		  }
	   SelfAdjointEigenSolver<PMatrix> eigensolver(K);

	   PMatrix U = eigensolver.eigenvectors();
	   PMatrix S = eigensolver.eigenvalues();

	   PMatrix S_sqr = PMatrix::Zero(n_samples,n_samples);
	   for(size_t i=0; i<n_samples;++i)
		  {
		  S_sqr(i,i) = (sqrt(S(i,0))+5.0)/5.0;
		  }
	   Y=S_sqr*Y;
      Y =  U * Y;
	   
	   //Y+=1.0*Y2;

		//std::cout << K;
		//std::cout <<"\n\nX:\n"<< X;
		//std::cout <<"\n\nY:\n"<< Y;

		//create LOD matrix
		PMatrix PV = PMatrix::Zero(n_pheno,n_snps);
		PMatrix ldelta = PMatrix::Zero(n_pheno,n_snps);
		PMatrix LL = PMatrix::Zero(n_pheno,n_snps);

		train_associations_SingleSNP(PV, LL, ldelta, X, Y, U, S, C, 50, -10.0, 10.0);
		std::cout <<"\nPV :\n"<< PV <<"\n\n";
		//std::cout <<"\nLL :\n"<< LL <<"\n\n";
		//std::cout <<"\nldelta :\n"<< ldelta <<"\n\n";
		//std::cout <<"\nX :\n"<< X <<"\n\n";
		}
	//std::cout << "done";

	//void train_interactions(PMatrix& LOD,const PMatrix& X,const PMatrix& Y,const PMatrix& K,const PMatrix& C,const PMatrix& I,int numintervalsAlt,double ldeltaminAlt,double ldeltamaxAlt,int numintervals0,double ldeltamin0,double ldeltamax0,bool refit_delta0_snp);



}

#endif //main_testing_cpp
