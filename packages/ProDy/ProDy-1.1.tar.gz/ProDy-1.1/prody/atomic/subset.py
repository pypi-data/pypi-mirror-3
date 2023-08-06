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

import numpy as np

from atom import Atom
from fields import ATOMIC_FIELDS, ATOMIC_ATTRIBUTES, READONLY
from fields import wrapGetMethod, wrapSetMethod
from pointer import AtomPointer
from prody import LOGGER

__all__ = ['AtomSubset']

class AtomSubsetMeta(type):

    def __init__(cls, name, bases, dict):

        for field in ATOMIC_FIELDS.values():
            
            if field.private:
                continue

            meth = field.meth_pl
            getMeth = 'get' + meth
            setMeth = 'set' + meth
            # Define public method for retrieving a copy of data array
            if field.call:
                def getData(self, var=field.var, call=field.call):
                    if self._ag._data[var] is None:
                        [getattr(self._ag, meth)() for meth in call]
                    return self._ag._data[var][self._indices]
            else:
                def getData(self, var=field.var):
                    array = self._ag._data[var]
                    if array is None:
                        return None
                    return array[self._indices] 
            getData = wrapGetMethod(getData)
            getData.__name__ = getMeth
            getData.__doc__ = field.getDocstr('get')
            setattr(cls, getMeth, getData)
            setattr(cls, '_' + getMeth, getData)
            
            if field.readonly:
                continue
            
            # Define public method for setting values in data array
            def setData(self, value, var=field.var, none=field.none):
                array = self._ag._data[var]
                if array is None:
                    raise AttributeError(var + ' data is not set')
                array[self._indices] = value
                if none:
                    [self._ag.__setattr__(nm,  None) if nm[0] == '_' else
                     self._ag._data.__setitem__(nm,  None) for nm in none]
            setData = wrapSetMethod(setData)
            setData.__name__ = setMeth 
            setData.__doc__ = field.getDocstr('set')  
            setattr(cls, setMeth, setData)

                        
class AtomSubset(AtomPointer):
    
    """A class for manipulating subset of atoms in an :class:`~.AtomGroup`.
    Derived classes are:
        
      * :class:`~.Selection`
      * :class:`~.Segment`
      * :class:`~.Chain`
      * :class:`~.Residue`
    
    This class stores a reference to an :class:`~.AtomGroup` instance, a set of 
    atom indices, and active coordinate set index for the atom group.
    
    """
    
    __metaclass__ = AtomSubsetMeta    
    
    __slots__ = ['_ag', '_indices', '_acsi', '_selstr']
    
    def __init__(self, ag, indices, acsi, **kwargs):
        
        AtomPointer.__init__(self, ag, acsi)

        if not isinstance(indices, np.ndarray):
            indices = np.array(indices, int)
        elif not indices.dtype == int:
            indices = indices.astype(int)
        
        if kwargs.get('unique'):
            self._indices = indices
        else:
            self._indices = np.unique(indices)
        
        self._selstr = kwargs.get('selstr')

    def __len__(self):
        
        return len(self._indices)

    def getCoords(self):
        """Return a copy of coordinates from the active coordinate set."""
        
        if self._ag._coords is not None:
            # Since this is not slicing, a view is not returned
            return self._ag._coords[self.getACSIndex(), self._indices]
    
    _getCoords = getCoords
    
    def setCoords(self, coords):
        """Set coordinates in the active coordinate set."""
        
        if self._ag._coords is not None:
            self._ag._coords[self.getACSIndex(), self._indices] = coords
            self._ag._setTimeStamp(self.getACSIndex())
    
    def getCoordsets(self, indices=None):
        """Return coordinate set(s) at given *indices*, which may be an integer 
        or a list/array of integers."""
        
        if self._ag._coords is None:
            return None
        if indices is None:
            return self._ag._coords[:, self._indices]
        if isinstance(indices, (int, slice)):
            return self._ag._coords[indices, self._indices]
        if isinstance(indices, (list, np.ndarray)):
            return self._ag._coords[indices, self._indices]
        raise IndexError('indices must be an integer, a list/array of '
                         'integers, a slice, or None')
                         
    _getCoordsets = getCoordsets

    def iterCoordsets(self):
        """Yield copies of coordinate sets."""
        
        coords = self._ag._getCoordsets()
        if coords is not None:
            indices = self._indices
            for xyz in coords:
                yield xyz[indices]

    _iterCoordsets = iterCoordsets
    
    def getIndices(self):
        """Return a copy of the indices of atoms."""
        
        return self._indices.copy()
    
    def _getIndices(self):
        """Return indices of atoms."""
        
        return self._indices
    
    def numAtoms(self):
        """Return number of atoms."""
        
        return len(self._indices)

    def iterAtoms(self):
        """Yield atoms."""

        ag = self._ag
        acsi = self.getACSIndex()
        for index in self._indices:
            yield Atom(ag=ag, index=index, acsi=acsi)

    __iter__ = iterAtoms
    
    def getData(self, label):
        """Return a copy of data associated with *label*, if it is present."""
        
        try:
            data = self._ag._data[label]
        except KeyError:
            pass
        else:
            return data[self._indices]
    
    _getData = getData
    
    def setData(self, label, data):
        """Update *data* associated with *label*.
        
        :raise AttributeError: when data associated with *label* is not present
        """
        
        if label in READONLY:
            raise AttributeError('{0:s} is read-only'.format(repr(label)))
        if label in ATOMIC_ATTRIBUTES:
            raise AttributeError('{0:s} must be changed using `set{1:s}` '
                'method'.format(repr(label), ATOMIC_ATTRIBUTES[label].meth_pl))
        try:
            self._ag._data[label][self._index] = data 
        except KeyError:
            raise AttributeError('data with label {0:s} must be set for '
                                 'AtomGroup first'.format(repr(label)))
