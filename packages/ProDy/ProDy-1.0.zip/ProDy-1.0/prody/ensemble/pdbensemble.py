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

"""This module defines a class for handling ensembles of PDB conformations."""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2012 Ahmet Bakan'

import numpy as np
from prody import Atomic, AtomGroup
from prody.measure import getRMSD, _calcTransformation, _applyTransformation
from prody.tools import checkCoords, importLA

from ensemble import Ensemble
from conformation import PDBConformation

__all__ = ['PDBEnsemble']

pkg = __import__(__package__) 
LOGGER = pkg.LOGGER
                

class PDBEnsemble(Ensemble):
    
    """This class enables handling coordinates for heterogeneous structural 
    datasets and stores identifiers for individual conformations.
    
    |example| See usage usage in :ref:`pca-xray`, :ref:`pca-dimer`, and 
    :ref:`pca-blast`.
    
    .. note:: This class is designed to handle conformations with missing
       coordinates, e.g. atoms that are note resolved in an X-ray structure.
       For unresolved atoms, the coordinates of the reference structure is
       assumed in RMSD calculations and superpositions."""

    def __init__(self, title='Unknown'):
        
        self._labels = []
        Ensemble.__init__(self, title)
        
    def __repr__(self):
        return '<PDB' + Ensemble.__repr__(self)[1:]
    
    def __str__(self):
        return 'PDB' + Ensemble.__str__(self)
    
    def __add__(self, other):
        """Concatenate two ensembles. The reference coordinates of *self* is 
        used in the result."""
        
        if not isinstance(other, Ensemble):
            raise TypeError('an Ensemble instance cannot be added to an {0:s} '
                            'instance'.format(type(other)))
        elif self.numAtoms() != other.numAtoms():
            raise ValueError('Ensembles must have same number of atoms.')
    
        ensemble = PDBEnsemble('{0:s} + {1:s}'.format(self.getTitle(), 
                                                   other.getTitle()))
        ensemble.setCoords(self._coords.copy())
        ensemble.addCoordset(self._confs.copy(), self._weights.copy())
        other_weights = other.getWeights()
        if other_weights is None:
            ensemble.addCoordset(other.getCoordsets())
        else:
            ensemble.addCoordset(other._confs.copy(), other_weights)
        return ensemble
    
    def __iter__(self):
        n_confs = self._n_csets
        for i in range(n_confs):
            if n_confs != self._n_csets:
                raise RuntimeError('number of conformations in the ensemble '
                                   'changed during iteration')
            yield PDBConformation(self, i)
    
    def __getitem__(self, index):
        """Return a conformation at given index."""
        
        if isinstance(index, int):
            return self.getConformation(index) 
        elif isinstance(index, slice):
            ens = PDBEnsemble('{0:s} ({1[0]:d}:{1[1]:d}:{1[2]:d})'.format(
                                self._title, index.indices(len(self))))
            ens.setCoords(self.getCoords())
            ens.addCoordset(self._confs[index].copy(), 
                            self._weights[index].copy())
            return ens
        elif isinstance(index, (list, np.ndarray)):
            ens = PDBEnsemble('Conformations of {0:s}'.format(self._title))
            ens.setCoords(self.getCoords())
            ens.addCoordset(self._confs[index].copy(), 
                            self._weights[index].copy())
            return ens
        else:
            raise IndexError('invalid index')
            
    def _superpose(self):
        """Superpose conformations and update coordinates."""

        calcT = _calcTransformation
        applyT = _applyTransformation
        if self._sel is None:
            weights = self._weights
            coords = self._coords
            confs = self._confs
            for i, conf in enumerate(confs):
                confs[i] = applyT(calcT(conf, coords, weights[i]), confs[i])
        else:            
            indices = self._indices
            weights = self._weights[:, indices]
            coords = self._coords[indices]
            confs_selected = self._confs[:,indices]
            confs = self._confs
            for i, conf in enumerate(confs_selected):
                confs[i] = applyT(calcT(conf, coords, weights[i]), confs[i]) 

    def addCoordset(self, coords, weights=None, allcoordsets=True):
        """Add coordinate set(s) as conformation(s).

        :class:`~.Atomic` instances are accepted as *coords* argument.  
        If *allcoordsets* is ``True``, all coordinate sets from the 
        :class:`~.Atomic` instance will be appended to the ensemble. 
        Otherwise, only the active coordinate set will be appended.

        *weights* is an optional argument. If provided, its length must
        match number of atoms. Weights of missing (not resolved) atoms 
        must be equal to ``0`` and weights of those that are resolved
        can be anything greater than ``0``. If not provided, weights of 
        atoms in this coordinate set will be set equal to ``1``."""
        
        assert isinstance(allcoordsets, bool), 'allcoordsets must be boolean'
        if weights is not None:
            assert isinstance(weights, np.ndarray), 'weights must be ndarray'
            
        ag = None
        if isinstance(coords, Atomic):
            atoms = coords
            if isinstance(coords, AtomGroup):
                ag = atoms
            else:
                ag = atoms.getAtomGroup()
            if allcoordsets:
                coords = atoms.getCoordsets()
            else: 
                coords = atoms.getCoords()
            title = ag.getTitle() 
        elif isinstance(coords, np.ndarray):
            title = 'Unknown'
        else:
            title = str(coords)
            try:
                if allcoordsets:
                    coords = coords.getCoordsets()
                else: 
                    coords = coords.getCoords()
            except AttributeError:            
                raise TypeError('coords must be a Numpy array or must have '
                                'getCoordinates attribute')

        coords = checkCoords(coords, 'coords', cset=True, 
                             n_atoms=self._n_atoms, reshape=True)
        n_csets, n_atoms, _ = coords.shape
        if self._n_atoms == 0:
            self._n_atoms = n_atoms
        if weights is None:
            weights = np.ones((n_csets, n_atoms, 1), dtype=float)
        else:
            weights = checkWeights(weights, n_atoms, n_csets)

        while '  ' in title:
            title = title.replace('  ', ' ')
        title = title.replace(' ', '_')
        
        if n_csets > 1:
            self._labels += ['{0:s}_{1:d}'
                                  .format(title, i+1) for i in range(n_csets)]
        else:
            if ag is not None and ag.numCoordsets() > 1:
                self._labels.append('{0:s}_{1:d}'.format(title, 
                                         atoms.getACSIndex()))
            else:                
                self._labels.append(title)
        if self._confs is None and self._weights is None:
            self._confs = coords
            self._weights = weights
            self._n_csets = n_csets
        elif self._confs is not None and self._weights is not None:
            self._confs = np.concatenate((self._confs, coords), axis=0)
            self._weights = np.concatenate((self._weights, weights), axis=0)
            self._n_csets += n_csets
        else:
            raise RuntimeError('_confs and _weights must be set or None at '
                               'the same time')

    def getLabels(self):
        """Return identifiers of the conformations in the ensemble."""
        
        return list(self._labels)
    
    def getCoordsets(self, indices=None):
        """Return a copy of coordinate set(s) at given *indices* for selected 
        atoms. *indices* may be an integer, a list of integers or ``None``. 
        ``None`` returns all coordinate sets. 
    
        .. warning:: When there are atoms with weights equal to zero (0),
           their coordinates will be replaced with the coordinates of the
           ensemble reference coordinate set.
        """
        
        if self._confs is None:
            return None
    
        if indices is None:
            indices = slice(None)
        elif isinstance(indices, (int, long)): 
            indices = np.array([indices])
        coords = self._coords
        if self._sel is None:
            confs = self._confs[indices].copy()
            for i, w in enumerate(self._weights[indices]):
                which = w.flatten()==0
                confs[i, which] = coords[which]
        else:
            selids = self._indices
            coords = coords[selids]
            confs = self._confs[indices, selids]
            for i, w in enumerate(self._weights[indices]):
                which = w[selids].flatten()==0
                confs[i, which] = coords[which]
        return confs
    
    _getCoordsets = getCoordsets
    
    def iterCoordsets(self):
        """Iterate over coordinate sets. A copy of each coordinate set for
        selected atoms is returned. Reference coordinates are not included."""
        
        conf = PDBConformation(self, 0)
        for i in range(self._n_csets):
            conf._index = i
            yield conf.getCoords()
   
    def delCoordset(self, index):
        """Delete a coordinate set from the ensemble."""
        
        Ensemble.delCoordset(self, index)
        if isinstance(index, int):
            index = [index]
        else:
            index = list(index)
        index.sort(reverse=True)
        for i in index:
            self._labels.pop(i)
            
    def getConformation(self, index):
        """Return conformation at given index."""

        if self._confs is None:
            raise AttributeError('conformations are not set')
        if not isinstance(index, int):
            raise TypeError('index must be an integer')
        n_confs = self._n_csets
        if -n_confs <= index < n_confs:
            if index < 0:
                index = n_confs + index
            return PDBConformation(self, index)
        else:
            raise IndexError('conformation index out of range')

    def getMSFs(self):
        """Calculate and return mean square fluctuations (MSFs). 
        Note that you might need to align the conformations using 
        :meth:`superpose` or :meth:`iterpose` before calculating MSFs."""
        
        if self._confs is None: 
            return
        indices = self._indices
        if indices is None:
            coords = self._coords
            confs = self._confs
            weights = self._weights > 0
        else:
            coords = self._coords[indices]
            confs = self._confs[:,indices]
            weights = self._weights[:,indices] > 0
        weightsum = weights.sum(0)
        mean = np.zeros(coords.shape)
        for i, conf in enumerate(confs):
            mean += conf * weights[i]
        mean /= weightsum
        ssqf = np.zeros(mean.shape)
        for i, conf in enumerate(confs):
            ssqf += ((conf - mean) * weights[i]) ** 2
        return ssqf.sum(1) / weightsum.flatten()
    
    def getRMSDs(self):
        """Calculate and return root mean square deviations (RMSDs). Note that 
        you might need to align the conformations using :meth:`superpose` or 
        :meth:`iterpose` before calculating RMSDs."""
        
        if self._confs is None or self._coords is None: 
            return None
    
        if self._sel is None:
            return getRMSD(self._coords, self._confs, self._weights)
        else:
            indices = self._indices
            return getRMSD(self._coords[indices], self._confs[:,indices],
                           self._weights[:, indices])

    def setWeights(self, weights):
        """Set atomic weights."""
        
        if self._n_atoms == 0:
            raise AttributeError('coordinates are not set')
        elif not isinstance(weights, np.ndarray): 
            raise TypeError('weights must be an ndarray instance')
        elif weights.shape[:2] != (self._n_csets, self._n_atoms):
            raise ValueError('shape of weights must (n_confs, n_atoms[, 1])')
        if weights.dtype not in (np.float32, float):
            try:
                weights = weights.astype(float)
            except ValueError:
                raise ValueError('coords array cannot be assigned type '
                                 '{0:s}'.format(float))
        if np.any(weights < 0):
            raise ValueError('weights must greater or equal to 0')
            
        if weights.ndim == 2:
            weights = weights.reshape((self._n_csets, self._n_atoms, 1))
        self._weights = weights


