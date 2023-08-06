import os, sys, pdb, numpy
import distutils.core
from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

# DEFINE VERSION HERE
version_number = '0.3.5'
compile_flags = ["-O3"]

if sys.platform != "darwin":
    compile_flags.append("-march=native")
else:
    os.environ['ARCHFLAGS'] = "-arch i386 -arch x86_64"

ext_modules = [Extension(
    name="panama.core.lmm.lmm",
    language="c++", # mac g++ -dynamic != gcc -dynamic
    sources=["panama/core/lmm/lmm.pyx",
	     "panama/core/lmm/c_lmm.cpp",
	     "panama/core/lmm/utils/Gamma.cpp",
	     "panama/core/lmm/utils/FisherF.cpp",
	     "panama/core/lmm/utils/Beta.cpp",
	     "panama/core/lmm/utils/MathFunctions.cpp",
	     "panama/core/lmm/utils/BrentC.cpp"
             ],
    include_dirs = [numpy.get_include()],
    extra_compile_args = compile_flags,
    )]


setup(name = 'panama',
      url = 'http://ml.sheffield.ac.uk/qtl/panama/',
      version = version_number,
      description = 'a novel probabilistic model to account for confounding factors in eQTL studies',
      long_description = open('README.txt').read(),
      author = 'Nicolo Fusi*, Oliver Stegle*, Neil Lawrence',
      author_email = 'nicolo.fusi@sheffield.ac.uk',
      packages = ['panama.core', 'panama.core.lmm', 'panama.utilities', 'panama.data'],
      package_data = {'': ['*.csv', '*.pdf', '*.txt']},
      scripts = ['bin/panama'],
      py_modules = ['panama.__init__'],      
      cmdclass = {'build_ext': build_ext, 'inplace': True},
      install_requires = ['numpy >= 1.5',
			  'scipy >= 0.8',
			  'matplotlib >= 0.99',
			  'ipython >= 0.10',
			  'sphinx',
			  'pyzmq',
			  'Cython',
			  'pandas',
			  'pygp'],
      license = 'GPL v2.0',
      ext_modules = ext_modules
      )
