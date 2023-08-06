import sys, os

def get_num_threads():
    return os.getenv("OMP_NUM_THREADS")

def set_num_threads(num):
    """
    Sets the number of threads used by MKL. It is possible to control
    that using either MKL_NUM_THREADS or OMP_NUM_THREADS
    """
    
    os.environ["OMP_NUM_THREADS"] = str(num)

    return os.getenv("OMP_NUM_THREADS")

def set_dynamic_load(cond):
    """
    MKL_DYNAMIC being TRUE means that Intel MKL will always try to pick
    what it considers the best number of threads, up to the maximum
    specified by the user. MKL_DYNAMIC being FALSE means that Intel MKL
    will not deviate from the number of threads the user requested, unless
    there are reasons why it has no choice. The value of MKL_DYNAMIC is by
    default set to TRUE, regardless of OMP_DYNAMIC, whose default value
    may be FALSE.

    In general, you should set MKL_DYNAMIC to FALSE only under
    circumstances that Intel MKL is unable to detect, for example, when
    nested parallelism is desired where the library is called already from
    a parallel section. Please refer to "MKL_DYNAMIC" in the Intel MKL
    User's Guide for details        
    """

    if cond:
	os.environ['OMP_DYNAMIC'] = "TRUE"
    else:
	os.environ['OMP_DYNAMIC'] = "FALSE"

    return cond

def get_dynamic_load(cond):
    return os.getenv("OMP_DYNAMIC")

def get_num_cores():
    """
    Returns the number of cores available on the system
    """
    
    return os.sysconf("SC_NPROCESSORS_ONLN")
