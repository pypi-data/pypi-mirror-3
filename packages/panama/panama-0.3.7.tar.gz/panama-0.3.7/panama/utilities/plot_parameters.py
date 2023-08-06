import sys, os
import matplotlib

try:
    display = os.environ['DISPLAY']
    if sys.platform == "darwin":
	matplotlib.use('MacOSX')
    if display == "screen":
	matplotlib.use('PDF')
# if running from screen/ssh (no -X), switch to PDF backend
except KeyError:
    matplotlib.use('PDF')

# import pylab as PL
import pylab as plt
plparams = {'axes.labelsize': 22,
          'text.fontsize': 20,
          'title.fontsize': 20,
          'legend.fontsize': 20,
          'xtick.labelsize': 22,
          'ytick.labelsize': 22,
          'text.usetex': False}
plt.rcParams.update(plparams)
