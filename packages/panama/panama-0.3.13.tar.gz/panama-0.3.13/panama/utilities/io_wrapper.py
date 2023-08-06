import cPickle
import scipy as SP

def load(filename, file_type = "pickle"):

    if file_type == "pickle":
	f = open(filename + ".pickle", "r")
	contents = cPickle.load(f)
	f.close()
    else:
	import h5py
	f = h5py.File(filename + ".h5",'r')
	contents = SP.asarray(f['data'])
	f.close()
	
    return contents

def write(data, filename, file_type = "pickle"):

    if file_type == "pickle":
	f = open(filename + ".pickle", "w")
	cPickle.dump(data, f, -1)
	f.close()
    else:
	import h5py
	f = h5py.File(filename + ".h5", 'w')
	f.create_dataset(name="data", data=data)
	f.close()


    return data
