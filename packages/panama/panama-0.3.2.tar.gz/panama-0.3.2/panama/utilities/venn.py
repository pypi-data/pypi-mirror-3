"""
Adapted version from pybedtools

"""
import pdb

def venn_mpl(a, b, c, colors=None, outfn=None, labels=None):
    """
    *a*, *b*, and *c* are filenames to BED-like files.

    *colors* is a list of matplotlib colors for the Venn diagram circles.

    *outfn* is the resulting output file.  This is passed directly to
    fig.savefig(), so you can supply extensions of .png, .pdf, or whatever your
    matplotlib installation supports.

    *labels* is a list of labels to use for each of the files; by default the
    labels are ['a','b','c']
    """

    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    if colors is None:
        colors = ['r','b','g']

    radius = 6.0
    center = 0.0
    offset = radius / 2

    if labels is None:
        labels = ['a','b','c']

    circle_a = Circle(xy = (center-offset, center+offset), radius=radius, edgecolor=colors[0], label=labels[0])
    circle_b = Circle(xy = (center+offset, center+offset), radius=radius, edgecolor=colors[1], label=labels[1])
    circle_c = Circle(xy = (center,        center-offset), radius=radius, edgecolor=colors[2], label=labels[2])


    fig = plt.figure(facecolor='w')
    ax = fig.add_subplot(111)

    for circle in (circle_a, circle_b, circle_c):
        circle.set_facecolor('none')
        circle.set_linewidth(3)
        ax.add_patch(circle)

    ax.axis('tight')
    ax.axis('equal')
    ax.set_axis_off()


    kwargs = dict(horizontalalignment='center')

    # Unique to A
    ax.text( center-2*offset, center+offset, str(len(a - b - c)), **kwargs)

    # Unique to B
    ax.text( center+2*offset, center+offset, str(len(b - a - c)), **kwargs)

    # Unique to C
    ax.text( center, center-2*offset, str(len(c - a - b)), **kwargs)

    # A and B not C
    ax.text( center, center+2*offset-0.5*offset, str(len((a & b) - c)), **kwargs)

    # A and C not B
    ax.text( center-1.2*offset, center-0.5*offset, str(len((a & c) - b)), **kwargs)

    # B and C not A
    ax.text( center+1.2*offset, center-0.5*offset, str(len((b & c) - a)), **kwargs)

    # all
    ax.text( center, center, str(len(a & b & c)), **kwargs)

    ax.legend(loc='best')

    fig.savefig(outfn)
    plt.close(fig)


# venn_mpl(set([1,2,3]), set([1,3,5,6]), set([3,54,1,4]))
