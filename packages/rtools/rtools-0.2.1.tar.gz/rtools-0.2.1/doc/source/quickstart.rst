.. _quickstart:

Quick Start
#################


Create a colormap to be used in matplotlib using RColorMap


.. plot::
    :include-source:

    from rtools import *
    rmap = RColorMap("heat")
    cmap = rmap.colormap()
    A = np.array(range(100))
    A.shape = (10,10)
    plt.pcolor(A,cmap=cmap, vmin=0, vmax=100)
    plt.colorbar()
 

