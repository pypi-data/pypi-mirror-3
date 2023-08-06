"""
Interactive modeling of 1D vertical seismic profiling data in layered media
"""
import numpy
from fatiando.ui.gui import Lasagne

thickness = [10, 20, 5, 10, 45, 80]
zp = numpy.arange(0.5, sum(thickness), 0.5)
vmin, vmax = 500, 10000
app = Lasagne(thickness, zp, vmin, vmax)
app.run()
app.savedata('meh.txt')
