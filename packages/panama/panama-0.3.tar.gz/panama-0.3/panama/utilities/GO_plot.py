import numpy as np
import scipy as sp
import pdb, sys, pickle
import matplotlib
import matplotlib.pylab as plt
import pandas
from Tango import *

matplotlib.rcParams.update({'xtick.labelsize':16})

def plot_GO(golist, models = ['LIMMI', 'SVA'], cutoff = 0.05):
    assert len(golist) <= 2, 'this function supports comparisons between two models only'
    
    tango = Tango()
    plt.figure()
    plt.axes([0.1, 0.65, 0.85, 0.3]) 
    if len(golist) == 2:
	cur_width = 0.0
	width = 0.4
    else:
	cur_width = 0.0
	width = 0.8

    model_counts = []
    for g in golist:
	go = pandas.read_csv(g, sep='\t', index_col = 1)
	counts = go[go['Benjamini'] <= cutoff]['Count']
	model_counts.append(counts)

    if len(golist) == 2:
	go_categories = list(set.union(set(model_counts[0].keys()),
				       set(model_counts[1].keys())))
    else:
	go_categories = model_counts[0].keys()

	
    for i in range(len(models)):
	labels, vals = [], []
	for c in go_categories:
	    labels.append(c.split('~')[1])
	    try:
		vals.append(model_counts[i][c])
	    except KeyError:
		vals.append(0.0)


	pos = sp.arange(len(labels))
 	plt.bar(pos + cur_width, vals, width = width,
 		align='edge', color = tango.nextMedium())
	cur_width += width

    plt.xticks(pos+0.4, labels, rotation = 90)
    plt.ylabel('Number of genes')
    plt.grid(False)
    plt.savefig('test.pdf')
    return go


if __name__ == '__main__':
    go = plot_GO(['../papers/LIMMI_paper/supp/GO_annot_LIMMI.txt'], models = ['LIMMI'])
    #'../papers/LIMMI_paper/supp/GO_annot_SVA.txt'])
