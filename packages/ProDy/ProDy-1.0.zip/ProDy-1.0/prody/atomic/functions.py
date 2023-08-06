# -*- coding: utf-8 -*-
# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2012 Ahmet Bakan
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

"""This module defines utility functions for handling atomic classes and data.
"""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'


from numpy import load, savez

from prody.tools import openFile

from atomic import Atomic
from fields import ATOMIC_ATTRIBUTES
from atomgroup import AtomGroup
from bond import trimBonds, evalBonds

__all__ = ['loadAtoms', 'saveAtoms']

pkg = __import__(__package__)
LOGGER = pkg.LOGGER

def saveAtoms(atoms, filename=None, **kwargs):
    """Save *atoms* in ProDy internal format.  All atomic classes are accepted 
    as *atoms* argument.  This function saves user set atomic data as well.  
    Note that title of the AtomGroup instance is used as the filename when 
    *atoms* is not an AtomGroup.  To avoid overwriting an existing file with 
    the same name, specify a *filename*."""
    
    if not isinstance(atoms, Atomic):
        raise TypeError('atoms must be Atomic instance, not {0:s}'
                        .format(type(atoms)))
    if isinstance(atoms, AtomGroup):
        ag = atoms
        title = ag.getTitle()
    else:
        ag = atoms.getAtomGroup()
        title = str(atoms)
    
    if filename is None:
        filename = ag.getTitle().replace(' ', '_')
    filename += '.ag.npz'
    attr_dict = {'title': title}
    attr_dict['n_atoms'] = atoms.numAtoms()
    attr_dict['n_csets'] = atoms.numCoordsets()
    attr_dict['cslabels'] = atoms.getCSLabels()
    coords = atoms._getCoordsets()
    if coords is not None:
        attr_dict['coordinates'] = coords
    bonds = ag._bonds
    bmap = ag._bmap
    if bonds is not None and bmap is not None:
        if isinstance(atoms, AtomGroup):
            attr_dict['bonds'] = bonds
            attr_dict['bmap'] = bmap
            attr_dict['numbonds'] = ag._data['numbonds']
        else:
            bonds = trimBonds(bonds, atoms._getIndices())
            attr_dict['bonds'] = bonds
            attr_dict['bmap'], attr_dict['numbonds'] = \
                evalBonds(bonds, len(atoms))
        
    for key, data in ag._data.iteritems():
        if key == 'numbonds':
            continue
        if data is not None:
            attr_dict[key] = data 
    ostream = openFile(filename, 'wb', **kwargs)
    savez(ostream, **attr_dict)
    ostream.close()
    return filename

SKIP = set(['title', 'n_atoms', 'n_csets', 'bonds', 'bmap',
            'coordinates', 'cslabels', 'numbonds'])

def loadAtoms(filename):
    """Return :class:`AtomGroup` instance from *filename*.  This function makes
    use of :func:`numpy.load` function.  See also :func:`saveAtoms`."""
    
    LOGGER.timeit()
    attr_dict = load(filename)
    files = set(attr_dict.files)
    # REMOVE support for _coordinates IN v1.0
    if not 'n_atoms' in files:
        raise ValueError("'{0:s}' is not a valid atomic data file"
                         .format(filename))
    title = str(attr_dict['title'])
    if 'coordinates' in files:
        coords = attr_dict['coordinates']
        ag = AtomGroup(title)
        ag._n_csets = int(attr_dict['n_csets'])
        ag._coords = coords
    ag._n_atoms = int(attr_dict['n_atoms'])
    ag._setTimeStamp()
    if 'bonds' in files and 'bmap' in files and 'numbonds' in files:
        ag._bonds = attr_dict['bonds']
        ag._bmap = attr_dict['bmap']
        ag._data['numbonds'] = attr_dict['numbonds']
    for key, data in attr_dict.iteritems():
        if key in SKIP:
            continue
        if key in ATOMIC_ATTRIBUTES:
            ag._data[key] = data
        else:
            ag.setData(key, data)
    if ag.numCoordsets() > 0:
        ag._acsi = 0
    if 'cslabels' in files:
        ag.setCSLabels(list(attr_dict['cslabels']))
    LOGGER.timing('Atom group was loaded in %.2fs.')
    return ag
