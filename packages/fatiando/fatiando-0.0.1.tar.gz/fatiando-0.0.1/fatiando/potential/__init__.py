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
Potential field direct modeling, inversion, transformations and utilities.

**DIRECT MODELLING**

* :mod:`fatiando.potential.prism`
* :mod:`fatiando.potential.polyprism`
* :mod:`fatiando.potential.talwani`

The direct modeling modules provide ways to calculate the gravitational and
magnetic field of various types of geometric objects. For 3D right rectangular
prisms, use :mod:`fatiando.potential.prism`. For 2D bodies with polygonal
vertical cross-sections, use :mod:`fatiando.potential.talwani`. For 3D bodies
with polygonal horizontal cross-sections, use
:mod:`fatiando.potential.polyprism`.

**INVERSION**

* :mod:`fatiando.potential.basin2d`

The inverse modeling modules use the direct models and the
:mod:`fatiando.inversion` package to solve potential field inverse problems.

**PROCESSING**

* :mod:`fatiando.potential.transform`

The processing modules offer tools to prepare potential field data before or
after modeling.

----

"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = 'Created 16-Mar-2010'


from fatiando.potential import prism, polyprism, transform, talwani
