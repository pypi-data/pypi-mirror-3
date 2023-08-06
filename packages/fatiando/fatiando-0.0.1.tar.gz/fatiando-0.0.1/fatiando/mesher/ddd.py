# Copyright 2010 The Fatiando a Terra Development Team
#
# This file is part of Fatiando a Terra.
#
# Fatiando a Terra is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Fatiando a Terra is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Fatiando a Terra.  If not, see <http://www.gnu.org/licenses/>.
"""
Create and operate on meshes of 3D objects like prisms, polygonal prisms,
tesseroids, etc.

**Elements**

* :func:`fatiando.mesher.ddd.Prism`
* :func:`fatiando.mesher.ddd.PolygonalPrism`

**Meshes**

* :class:`fatiando.mesher.ddd.PrismMesh`
* :class:`fatiando.mesher.ddd.PrismRelief`

**Utility functions**

* :func:`fatiando.mesher.ddd.extract`
* :func:`fatiando.mesher.ddd.filter`
* :func:`fatiando.mesher.ddd.center`

----

"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = '13-Sep-2010'

import numpy
import matplotlib.mlab

from fatiando import logger

log = logger.dummy()

# For lazy imports of TVTK, since it's very slow to import
tvtk = None


def _lazy_import_tvtk():
    """
    Do the lazy import of tvtk
    """
    global tvtk
    # For campatibility with versions of Mayavi2 < 4
    if tvtk is None:
        try:
            from tvtk.api import tvtk
        except ImportError:
            from enthought.tvtk.api import tvtk
    
def Prism(x1, x2, y1, y2, z1, z2, props=None):
    """
    Create a 3D right rectangular prism.

    Parameters:
    
    * x1, x2
        South and north borders of the prism
    * y1, y2
        West and east borders of the prism
    * z1, z2
        Top and bottom of the prism
    * props
        Dictionary with the physical properties assigned to the prism.
        Ex: ``props={'density':10, 'susceptibility':10000}``
        
    Returns:
    
    * prism
        Dictionary describing the prism

    """
    prism = {'x1':float(x1), 'x2':float(x2), 'y1':float(y1), 'y2':float(y2),
             'z1':float(z1), 'z2':float(z2)}
    if props is not None:
        for prop in props:
            prism[prop] = props[prop]
    return prism

def PolygonalPrism(vertices, z1, z2, props=None):
    """
    Create a 3D prism with polygonal crossection.

    Parameters:
    
    * vertices
        List of (x,y) pairs with the coordinates of the vertices. MUST BE
        CLOCKWISE or will give inverse result.
    * z1, z2
        Top and bottom of the prism
    * props
        Dictionary with the physical properties assigned to the prism.
        Ex: ``props={'density':10, 'susceptibility':10000}``
        
    Returns:
    
    * prism
        Dictionary describing the prism

    """
    x, y = numpy.array(vertices).T
    prism = {'x':x, 'y':y, 'z1':z1, 'z2':z2}
    if props is not None:
        for prop in props:
            prism[prop] = props[prop]
    return prism
    
class PrismRelief():
    """
    Generate a 3D model of a relief (topography) using prisms.
    
    Use to generate:
    * topographic model
    * basin model
    * Moho model
    * etc

    PrismRelief can used as list of prisms. It acts as an iteratior (so you
    can loop over prisms). It also has a ``__getitem__`` method to access
    individual elements in the mesh.
    In practice, PrismRelief should be able to be passed to any function that
    asks for a list of prisms, like :func:`fatiando.potential.prism.gz`.

    Parameters:
    
    * ref
        Reference level. Prisms will have:
            * bottom on zref and top on z if z > zref;
            * bottom on z and top on zref otherwise.
    * dims
        ``(dy, dx)``: the dimensions of the prisms in the y and x directions
    * nodes
        ``(x, y, z)`` where x, y, and z are arrays with the x, y and z
        coordinates of the center of the top face of each prism.
        x and y should be on a regular grid.

    """

    def __init__(self, ref, dims, nodes):
        x, y, z = nodes
        if len(x) != len(y) != len(z):
            raise ValueError, "nodes has x,y,z coordinates of different lengths"
        self.x, self.y, self.z = x, y, z
        self.size = len(x)
        self.ref = ref
        self.dy, self.dx = dims
        self.props = {}
        log.info("Generating 3D relief with right rectangular prisms:")
        log.info("  number of prisms = %d" % (self.size))
        log.info("  reference level = %s" % (str(ref)))
        log.info("  dimensions of prisms = %g x %g" % (dims[0], dims[1]))
        # The index of the current prism in an iteration. Needed when mesh is
        # used as an iterator
        self.i = 0

    def __len__(self):
        return self.size

    def __iter__(self):
        self.i = 0
        return self

    def __getitem__(self, index):
        # To walk backwards in the list
        if index < 0:
            index = self.size + index
        xc, yc, zc = self.x[index], self.y[index], self.z[index]
        x1 = xc - 0.5*self.dx
        x2 = xc + 0.5*self.dx
        y1 = yc - 0.5*self.dy
        y2 = yc + 0.5*self.dy
        if zc <= self.ref:
            z1 = zc
            z2 = self.ref
        else:            
            z1 = self.ref
            z2 = zc
        props = dict([p, self.props[p][index]] for p in self.props)
        return Prism(x1, x2, y1, y2, z1, z2, props=props)
        
    def next(self):
        if self.i >= self.size:
            raise StopIteration
        prism = self.__getitem__(self.i)
        self.i += 1
        return prism

    def addprop(self, prop, values):
        """
        Add physical property values to the prisms.

        **WARNING**: If a the z value of any point in the relief is bellow the
        reference level, its corresponding prism will have the physical property
        value with oposite sign than was assigned to it.

        Parameters:
        
        * prop
            Name of the physical property.
        * values
            List or array with the value of this physical property in each
            prism of the mesh.
            
        """
        def correct(v, i):
            if self.z[i] > self.ref:
                return -v
            return v
        self.props[prop] = [correct(v, i) for i, v in enumerate(values)]

class PrismMesh(object):
    """
    Generate a 3D regular mesh of right rectangular prisms.

    Prisms are ordered as follows: first layers (z coordinate), then EW rows (y)
    and finaly x coordinate (NS).

    Remember that the coordinate system is x->North, y->East and z->Down

    Ex: in a mesh with shape ``(3,3,3)`` the 15th element (index 14) has z index
    1 (second layer), y index 1 (second row), and x index 2 (third element in
    the column).

    PrismMesh can used as list of prisms. It acts as an iteratior (so you can 
    loop over prisms). It also has a ``__getitem__`` method to access individual 
    elements in the mesh. In practice, PrismMesh should be able to be passed 
    to any function that asks for a list of prisms, like 
    :func:`fatiando.potential.prism.gz`.

    To make the mesh incorporate a topography, use
    meth:`fatiando.mesher.ddd.PrismMesh.carvetopo`

    Example::

        >>> def show(p):
        ...     print ' | '.join('%s : %.1f' % (k, p[k]) for k in sorted(p))
        >>> mesh = PrismMesh((0,1,0,2,0,3),(1,2,2))
        >>> for p in mesh:
        ...     show(p)
        x1 : 0.0 | x2 : 0.5 | y1 : 0.0 | y2 : 1.0 | z1 : 0.0 | z2 : 3.0
        x1 : 0.5 | x2 : 1.0 | y1 : 0.0 | y2 : 1.0 | z1 : 0.0 | z2 : 3.0
        x1 : 0.0 | x2 : 0.5 | y1 : 1.0 | y2 : 2.0 | z1 : 0.0 | z2 : 3.0
        x1 : 0.5 | x2 : 1.0 | y1 : 1.0 | y2 : 2.0 | z1 : 0.0 | z2 : 3.0
        >>> show(mesh[0])
        x1 : 0.0 | x2 : 0.5 | y1 : 0.0 | y2 : 1.0 | z1 : 0.0 | z2 : 3.0
        >>> show(mesh[-1])
        x1 : 0.5 | x2 : 1.0 | y1 : 1.0 | y2 : 2.0 | z1 : 0.0 | z2 : 3.0

    Example with physical properties::

        >>> def show(p):
        ...     print '|'.join('%s:%g' % (k, p[k]) for k in sorted(p))
        >>> props = {'density':[2670.0, 1000.0]}
        >>> mesh = PrismMesh((0,2,0,4,0,3),(1,1,2),props=props)
        >>> for p in mesh:
        ...     show(p)
        density:2670|x1:0|x2:1|y1:0|y2:4|z1:0|z2:3
        density:1000|x1:1|x2:2|y1:0|y2:4|z1:0|z2:3

    Parameters:
    
    * bounds
        ``[xmin, xmax, ymin, ymax, zmin, zmax]``: boundaries of the mesh.
    * shape
        Number of prisms in the x, y, and z directions, ie ``(nz, ny, nx)``
    * props
        Dictionary with the physical properties of each prism in the mesh.
        Each key should be the name of a physical property. The corresponding
        value should be a list with the values of that particular property on
        each prism of the mesh.

    """

    def __init__(self, bounds, shape, props=None):
        object.__init__(self)
        log.info("Generating 3D right rectangular prism mesh:")
        nz, ny, nx = shape
        size = int(nx*ny*nz)
        x1, x2, y1, y2, z1, z2 = bounds
        dx = float(x2 - x1)/nx
        dy = float(y2 - y1)/ny
        dz = float(z2 - z1)/nz
        self.shape = tuple(int(i) for i in shape)
        self.size = size
        self.dims = (dx, dy, dz)
        self.bounds = bounds
        if props is None:
            self.props = {}
        else:
            self.props = props
        log.info("  bounds = (x1, x2, y1, y2, z1, z2) = %s" % (str(bounds)))
        log.info("  shape = (nz, ny, nx) = %s" % (str(shape)))
        log.info("  number of prisms = %d" % (size))
        log.info("  prism dimensions = (dx, dy, dz) = %s" % (str(self.dims)))
        # The index of the current prism in an iteration. Needed when mesh is
        # used as an iterator
        self.i = 0
        # List of masked prisms. Will return None if trying to access them
        self.mask = []
        
    def __len__(self):
        return self.size

    def __getitem__(self, index):
        # To walk backwards in the list
        if index < 0:
            index = self.size + index
        if index in self.mask:
            return None
        nz, ny, nx = self.shape
        k = index/(nx*ny)
        j = (index - k*(nx*ny))/nx
        i = (index - k*(nx*ny) - j*nx)
        x1 = self.bounds[0] + self.dims[0]*i
        x2 = x1 + self.dims[0]
        y1 = self.bounds[2] + self.dims[1]*j
        y2 = y1 + self.dims[1]
        z1 = self.bounds[4] + self.dims[2]*k
        z2 = z1 + self.dims[2]
        props = dict([p, self.props[p][index]] for p in self.props)
        return Prism(x1, x2, y1, y2, z1, z2, props=props)

    def __iter__(self):
        self.i = 0
        return self

    def next(self):
        if self.i >= self.size:
            raise StopIteration
        prism = self.__getitem__(self.i)
        self.i += 1
        return prism

    def addprop(self, prop, values):
        """
        Add physical property values to the cells in the mesh.

        Different physical properties of the mesh are stored in a dictionary.

        Parameters:
        
        * prop
            Name of the physical property.
        * values
            List or array with the value of this physical property in each
            prism of the mesh. For the ordering of prisms in the mesh see the
            docstring for PrismMesh
            
        """
        self.props[prop] = values
        
    def carvetopo(self, x, y, height):
        """
        Mask (remove) prisms from the mesh that are above the topography.
        
        Accessing the ith prism will return None if it was masked (above the
        topography).
        Also mask prisms outside of the topography grid provided.
        The topography height information does not need to be on a regular grid,
        it will be interpolated.
    
        Parameters:
           
        * x, y
            Arrays with x and y coordinates of the grid points
        * height
            Array with the height of the topography
                
        """
        nz, ny, nx = self.shape
        x1, x2, y1, y2, z1, z2 = self.bounds
        dx, dy, dz = self.dims
        # The coordinates of the centers of the cells
        xc = numpy.arange(x1, x2, dx) + 0.5*dx
        # Sometimes arange returns more due to rounding
        if len(xc) > nx:
            xc = xc[:-1]
        yc = numpy.arange(y1, y2, dy) + 0.5*dy
        if len(yc) > ny:
            yc = yc[:-1]
        zc = numpy.arange(z1, z2, dz) + 0.5*dz
        if len(zc) > nz:
            zc = zc[:-1]
        XC, YC = numpy.meshgrid(xc, yc)
        # -1 if to transform height into z coordinate
        topo = -1*matplotlib.mlab.griddata(x, y, height, XC, YC).ravel()
        # griddata returns a masked array. If the interpolated point is out of
        # of the data range, mask will be True. Use this to remove all cells
        # bellow a masked topo point (ie, one with no height information)
        if numpy.ma.isMA(topo):
            topo_mask = topo.mask
        else:
            topo_mask = [False for i in xrange(len(topo))]
        c = 0
        for cellz in zc:
            for h, masked in zip(topo, topo_mask):
                if masked or cellz < h:
                    self.mask.append(c)
                c += 1

    def dump(self, fname, fmt='vtk'):
        """
        Dump the mesh to a file.

        File formats:
        
        * vtk
            Save the mesh as VTK UnstructuredGrid
        * ubc
            Save the mesh in the format required by UBC-GIF program MeshTools3D

        Parameters:
        
        * fname
            File name or open file object.
        * fmt
            File format
            
        """
        pass

def extract(key, prisms):
    """
    Extract a list of values of a key from each prism in a list

    Parameters:
    
    * key
        string representing the key whose value will be extracted.
        Should be one of the arguments to :func:`fatiando.mesher.ddd.Prism`
        
    * prisms
        A list of :func:`fatiando.mesher.ddd.Prism` objects.
        
    Returns:
    
    * Array with the extracted values

    """
    def getkey(p):
        if p is None:
            return None
        return p[key]
    return [getkey(p) for p in prisms]

def vfilter(vmin, vmax, key, prisms):
    """
    Return prisms from a list of Prism with a key that lies within a given
    range.

    Parameters:
    
    * prisms
        List of :func:`fatiando.mesher.ddd.Prism`
    * vmin
        Minimum value
    * vmax
        Maximum value
    * key
        The key of the prisms whose value will be used to filter
        
    Returns:
    
    * filtered
        List of prisms whose *key* falls within the given range

    """
    filtered = [p for p in prisms if p is not None and p[key] >= vmin and
                p[key] <= vmax]
    return filtered

def center(cell):
    """
    Return the coordinates of the center of a given cell.

    Paremters:
    
    * cell
        A cell (like :func:`fatiando.mesher.ddd.Prism`)

    Returns:
    
    * tuple
        ``(xc, yc, zc)`` coordinates
        
    """
    xc = 0.5*(cell['x1'] + cell['x2'])
    yc = 0.5*(cell['y1'] + cell['y2'])
    zc = 0.5*(cell['z1'] + cell['z2'])
    return (xc, yc, zc)
    
def _test():
    import doctest
    doctest.testmod()
    print "doctest finished"

if __name__ == '__main__':
    _test()
