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
Various tools for seismic and seismology, like direct modeling, inversion
(tomography), epicenter determination, etc.

**DIRECT MODELING AND INVERSION**

* :mod:`fatiando.seismic.traveltime`
* :mod:`fatiando.seismic.epicenter`
* :mod:`fatiando.seismic.profile`

**TOMOGRAPHY**

* :mod:`fatiando.seismic.srtomo`

----

"""
__author__ = 'Leonardo Uieda (leouieda@gmail.com)'
__date__ = 'Created 11-Sep-2010'

from fatiando.seismic import epicenter, traveltime, srtomo, profile
