"""
2D interactive direct gravity modeling with polygons
"""
import numpy
from fatiando.ui.gui import Moulder

area = (0, 100000, 0, 5000)
xp = numpy.arange(0, 100000, 1000)
zp = numpy.zeros_like(xp)
app = Moulder(area, xp, zp)
app.run()
