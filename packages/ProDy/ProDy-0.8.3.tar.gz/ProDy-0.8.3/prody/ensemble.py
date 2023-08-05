# ProDy: A Python Package for Protein Dynamics Analysis
# 
# Copyright (C) 2010-2011 Ahmet Bakan
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

"""This module defines a class for working on conformational ensembles and 
also arbitrary coordinate data sets.

Classes
-------

  * :class:`Ensemble`
  * :class:`Conformation`
  * :class:`PDBEnsemble`
  * :class:`PDBConformation`
  * :class:`Trajectory`
  * :class:`DCDFile`
  * :class:`Frame`
  
Base Classes
------------

  * :class:`EnsembleBase`
  * :class:`TrajectoryBase`
  * :class:`TrajectoryFile`
  * :class:`ConformationBase`
  
  
Inheritance Diagram
-------------------

.. inheritance-diagram:: prody.ensemble
   :parts: 1

Functions
---------

    * :func:`saveEnsemble`
    * :func:`loadEnsemble`
    * :func:`calcSumOfWeights`
    * :func:`showSumOfWeights`
    * :func:`trimEnsemble`
    * :func:`parseDCD`
    * :func:`writeDCD`

    
Examples
--------

Results from the example :ref:`pca-xray-calculations` will be used to
illustrate class methods and functions in the module.

>>> from prody import *

>>> ensemble = loadEnsemble('p38_X-ray.ens.npz')

"""

__author__ = 'Ahmet Bakan'
__copyright__ = 'Copyright (C) 2010-2011 Ahmet Bakan'

from time import time
import os.path
import datetime
from struct import calcsize, unpack, pack
import math

import numpy as np
import prody
LOGGER = prody.LOGGER
from prody import measure

PISQUARE = np.pi ** 2

__all__ = ['Ensemble', 'Conformation', 'PDBEnsemble', 'PDBConformation',
           'Trajectory', 'DCDFile', 'Frame',
           'EnsembleBase', 'TrajectoryBase', 'TrajectoryFile', 
           'ConformationBase',
           'saveEnsemble', 'loadEnsemble', 
           'calcSumOfWeights', 'showSumOfWeights', 'trimEnsemble',
           'parseDCD', 'writeDCD']
        
plt = None

def checkCoordsArray(array, arg='array', cset=False, n_atoms=None, 
                     reshape=None):
    """Return array if checks pass, otherwise raise an exception."""

    assert isinstance(arg, str), 'arg must be a string'
    assert isinstance(cset, bool), 'cset must be a boolean'
    assert n_atoms is None or isinstance(n_atoms, int) and n_atoms >= 0, \
        'n_atoms must be a positive integer'
    assert reshape is None or isinstance(reshape, bool), \
        'reshape must be a boolean'

    if not isinstance(array, np.ndarray):
        raise TypeError(arg + ' must be a Numpy array')
    elif cset and array.ndim not in (2,3): 
        raise ValueError(arg + '.ndim must be  2 or 3'.format(ndim))
    elif not cset and array.ndim != 2:
        raise ValueError(arg + '.ndim must be 2')
    elif array.shape[-1] != 3:
        raise ValueError(arg + '.shape[-1] of 3, i.e. ([n_csets,]n_atoms,3)')
    if n_atoms is not None and n_atoms != 0 and array.shape[-2] != n_atoms:
        raise ValueError(arg + ' size do nut match number of atoms')
    if array.dtype != float:
        try:
            array = array.astype(float)
        except ValueError:
            raise ValueError(arg + '.astype(float) fails, float type could '
                             'not be assigned')
    if cset and reshape and array.ndim == 2:
        array = array.reshape([1, array.shape[0], 3])
    return array

def checkWeightsArray(weights, n_atoms, n_csets=None):
    """Return weights if checks pass, otherwise raise an exception."""
    
    assert isinstance(n_atoms, int) and n_atoms > 0, \
        'n_atoms must be a positive integer'
    assert n_csets is None or isinstance(n_csets, int) and n_csets > 0, \
        'n_csets must be a positive integer'
    
    if not isinstance(weights, np.ndarray):
        raise TypeError('weights must be a Numpy array')
    elif n_csets is None and weights.ndim not in (1, 2):
        raise ValueError('weights.dim must be 1 or 2')
    elif n_csets is not None:
        if weights.ndim not in (1, 2, 3):
            raise ValueError('weights.dim must be 1, 2, or 3')
        elif weights.ndim == 3 and weights.shape[0] != n_csets:
            raise ValueError('weights.shape must be (n_csets, n_atoms, 1)')
    elif weights.ndim in (2, 3) and weights.shape[-1] != 1:
        raise ValueError('shape of weights must be ([n_csets,] n_atoms, 1)')
    elif weights.dtype != float:
        try:
            weights = weights.astype(float)
        except ValueError:
            raise ValueError(arg + '.astype(float) fails, float type could '
                             'not be assigned')
    if np.any(weights < 0):
        raise ValueError('all weights must greater or equal to 0')
    if weights.ndim == 1:
        weights = weights.reshape((n_atoms, 1))
    if n_csets is not None and weights.ndim == 2:
        weights = np.tile(weights.reshape((1, n_atoms, 1)), (n_csets, 1, 1))
    return weights

class EnsembleBase(object):
    
    """Base class for :class:`Ensemble` and :class:`TrajectoryBase`. 
    This class provides methods for associating instances with an 
    :class:`~prody.atomic.AtomGroup` and handling reference coordinates."""

    def __init__(self, name):
        self._name = str(name)
        if self._name == '':
            self._name = 'Unnamed'
        self._coords = None         # reference
        self._n_atoms = 0
        self._n_csets = 0 # number of conformations/frames/coordinate sets
        self._weights = None
        self._ag = None
        self._sel = None
        self._indices = None # indices of selected atoms

    def __len__(self):
        return self._n_csets

    def getName(self):
        """Return name of the instance."""
        
        return self._name

    def setName(self, name):
        """Set name of the instance."""
        
        self._name = str(name)
    
    def getNumOfAtoms(self):
        """Return number of atoms."""
        
        return self._n_atoms
   
    def getNumOfCoordsets(self):
        """Return number of coordinate sets, i.e conformations or frames."""
        
        return self._n_csets
    
    def getNumOfSelected(self):
        """Return number of selected atoms."""
        
        if self._sel is None:
            return self._n_atoms
        return len(self._indices) 
    
    def getAtomGroup(self):
        """Return associated atom group instance."""
        
        return self._ag
    
    def setAtomGroup(self, ag, setref=True):
        """Associate the instance with an :class:`~prody.atomic.AtomGroup`.
        
        Note that at association, active coordinate set of the 
        :class:`~prody.atomic.AtomGroup`, if it has one, will be set as 
        the reference coordinates for the ensemble or trajectory. Changes in 
        :class:`~prody.atomicAtomGroup` active coordinate set will not be
        reflected to the reference coordinates. If you want to preserve the 
        present reference coordinates, pass ``setref=False``. 
        
        """
        
        if ag is None:
            self._ag = None
        else:
            if not isinstance(ag, prody.AtomGroup):
                raise TypeError('ag must be an AtomGroup instance')
            if self._n_atoms != 0 and ag.getNumOfAtoms() != self._n_atoms:
                raise ValueError('AtomGroup must have same number of atoms')
            self._ag = ag
            if setref:
                coords = ag.getCoordinates()
                if coords is not None:
                    self._coords = coords 
                    LOGGER.info('Coordinates of {0:s} is set as the reference '
                                'for {1:s}.'.format(ag.getName(), self._name))
        self._sel = None
        self._indices = None
        
    def getSelection(self):
        """Return the current selection. If ``None`` is returned, it means
        that all atoms are selected."""
        
        return self._sel
    
    def _getSelIndices(self):
        return self._indices 
    
    def select(self, selstr):
        """Select a subset atoms. When a subset of atoms are selected, their 
        coordinates will be evaluated in, for example, RMSD calculations. 
        If *selstr* results in selecting no atoms, all atoms will be 
        considered. For more information on atom selections see 
        :ref:`selections`."""
        
        if selstr is None:
            self._sel = None
            self._indices = None
        else:
            if self._ag is None:
                raise AttributeError('instance needs to be associated with an '
                                     'AtomGroup for making selections')
            sel = self._ag.select(selstr)
            if sel is not None:
                self._indices = sel.getIndices()
            self._sel = sel
            return sel
    
    def getCoordinates(self):
        """Return a copy of reference coordinates of selected atoms."""
        
        if self._coords is None:
            return None
        if self._sel is None:
            return self._coords.copy()
        return self._coords[self._indices]
    
    def _getCoordinates(self):
        """Return a view of reference coordinates of selected atoms."""

        if self._coords is None:
            return None
        if self._sel is None:
            return self._coords
        return self._coords[self._indices]

    def setCoordinates(self, coords):
        """Set reference coordinates."""

        if not isinstance(coords, np.ndarray):
            try:
                coords = coords.getCoordinates()
            except AttributeError:
                raise TypeError('coords must be a Numpy array or must have '
                                'getCoordinates attribute')
        self._coords = checkCoordsArray(coords, arg='coords', 
                                        n_atoms=self._n_atoms, cset=False)
        
    def getWeights(self):
        """Return a copy of weights of selected atoms."""
        
        if self._weights is None:
            return None
        if self._sel is None:
            return self._weights.copy()
        if self.weights.ndim == 2:
            return self._weights[self._indices]
        else:
            return self._weights[:, self._indices]
    
    def _getWeights(self):

        if self._weights is None:
            return None
        if self._sel is None:
            return self._weights
        if self.weights.ndim == 2:
            return self._weights[self._indices]
        else:
            return self._weights[:, self._indices]

    
    def setWeights(self, weights):
        """Set atomic weights."""
        
        if self._n_atoms == 0:
            raise AttributeError('first set reference coordinates')
        self._weights = checkWeightsArray(weights, self._n_atoms, None)


class Ensemble(EnsembleBase):
    
    """A class for analysis of arbitrary conformational ensembles. 
    
    Indexing returns a :class:`Conformation` instance, which corresponds to
    a coordinate set. Slicing returns an :class:`Ensemble` instance that 
    contains subset of conformations (coordinate sets). The ensemble obtained 
    by slicing will have a copy of the reference coordinates.

    """

    def __init__(self, name='Unnamed'):
        """Instantiate with a name.
        
        .. versionchanged:: 0.6
           At instantiation, :class:`~prody.atomic.Atomic` instances are 
           accepted as *name* argument. All coordinate sets from *name* will be
           added to the ensemble automatically. 
           
        .. versionchanged:: 0.7
           When an empty string is passed as *name* argument, Ensemble instance
           is called "Unnamed". 
          
        :arg name: A name (:class:`str`) or an :class:`~prody.atomic.Atomic`
            instance.
        
        """
        EnsembleBase.__init__(self, name)
        self._confs = None       # coordinate sets
        
        if isinstance(name, (prody.Atomic, prody.Ensemble)):
            self.setCoordinates(name.getCoordinates())
            self.addCoordset(name)
        
    def __getitem__(self, index):
        """Return a conformation at given index."""
        if self._confs is None:
            return None
        if isinstance(index, int):
            return self.getConformation(index) 
        elif isinstance(index, slice):
            ens = Ensemble('{0:s} ({1[0]:d}:{1[1]:d}:{1[2]:d})'.format(
                                self._name, index.indices(len(self))))
            ens.setCoordinates(self.getCoordinates())
            ens.addCoordset(self.getCoordsets(index))
            if self._weights is not None:
                ens.setWeights(self.getWeights())
            return ens
        elif isinstance(index, (list, np.ndarray)):
            ens = Ensemble('Conformations of {0:s}'.format(self._name))
            ens.setCoordinates(self.getCoordinates())
            ens.addCoordset(self.getCoordsets(index))
            if self._weights is not None:
                ens.setWeights(self.getWeights())
            return ens
        else:
            raise IndexError('invalid index')
            
    
    def __add__(self, other):
        """Concatenate ensembles. The reference coordinates and weights of 
        *self* is used in the resulting ensemble."""
        
        if not isinstance(other, Ensemble):
            raise TypeError('an Ensemble instance cannot be added to an {0:s} '
                            'instance'.format(type(other)))
        elif self.getNumOfAtoms() != other.getNumOfAtoms():
            raise ValueError('Ensembles must have same number of atoms.')
    
        ensemble = Ensemble('{0:s} + {1:s}'.format(self.getName(), 
                                                   other.getName()))
        ensemble.setCoordinates(self._coords.copy())
        ensemble.addCoordset(self._confs.copy())
        ensemble.addCoordset(other.getCoordsets())
        if self._weights is not None: 
            LOGGER.info('Atom weights from "{0:s}" are used in "{1:s}".'
                        .format(self._name, ensemble.getName()))
            ensemble.setWeights(self._weights)
        return ensemble
    
    def __iter__(self):
        n_csets = self._n_csets
        for i in range(n_csets):
            if n_csets != self._n_csets:
                raise RuntimeError('number of conformations in the ensemble '
                                   'changed during iteration')
            yield Conformation(self, i)
    
    def __repr__(self):
        return ('<Ensemble: {0:s} ({1:d} conformations, {2:d} atoms, {3:d} '
               'selected)>').format(self._name, len(self), self._n_atoms, 
                                    self.getNumOfSelected())

    def __str__(self):
        return 'Ensemble {0:s}'.format(self._name)

    def getNumOfConfs(self):
        """Return number of conformations."""

        return self._n_csets

    def addCoordset(self, coords, allcoordsets=True):
        """Add coordinate set(s) as conformation(s).
        
        :class:`~prody.atomic.Atomic` instances are accepted as *coords* 
        argument. If *allcoordsets* is ``True``, all coordinate sets from
        the :class:`~prody.atomic.Atomic` instance will be appended to the 
        ensemble. Otherwise, only the active coordinate set will be appended.
        
        """
        
        assert isinstance(allcoordsets, bool), 'allcoordsets must be boolean'
        if not isinstance(coords, np.ndarray):
            if isinstance(coords, (prody.Atomic, prody.Ensemble)):
                atoms = coords
                if allcoordsets:
                    coords = atoms.getCoordsets()
                else:
                    coords = atoms.getCoordinates()
                if coords is None:
                    raise ValueError('{0:s} must contain coordinate data'
                                     .format(atoms))
            else:
                raise TypeError('coords must be a Numpy array or '
                                'ProDy Atomic or Ensemble instance')
            
        
        coords = checkCoordsArray(coords, arg='coords', cset=True, 
                                  n_atoms=self._n_atoms, reshape=True)
        if self._n_atoms == 0:
            self._n_atoms = coords.shape[-2]
        n_atoms = self._n_atoms
        n_confs = coords.shape[0]
            
        if self._confs is None: 
            self._confs = coords
        else:
            self._confs = np.concatenate((self._confs, coords), axis=0)
        self._n_csets += n_confs

    def getCoordsets(self, indices=None):
        """Return a copy of coordinate sets at given indices.
        
        *indices* may be an integer, a list of integers or ``None``. ``None``
        returns all coordinate sets. 
    
        For reference coordinates, use :meth:`getCoordinates` method.

        """
        
        if self._confs is None:
            return None
        elif self._indices is None:
            if indices is None:
                return self._confs.copy()
            elif isinstance(indices, (int, long, slice)): 
                return self._confs[indices].copy()
            elif isinstance(indices, (list, np.ndarray)):        
                return self._confs[indices]
            else:
                raise IndexError('indices must be an integer, a list/array of '
                                 'integers, a slice, or None')
        else:
            selids = self._indices
            if indices is None:
                return self._confs[:,selids]
            elif isinstance(indices, (int, long, slice)): 
                return self._confs[indices, selids]
            elif isinstance(indices, (list, np.ndarray)):        
                return self._confs[indices, selids]
            else:
                raise IndexError('indices must be an integer, a list/array of '
                                 'integers, a slice, or None')

    def _getCoordsets(self, indices=None):

        if self._confs is None:
            return None
        elif self._indices is None:
            if indices is None:
                return self._confs
            elif isinstance(indices, (int, long, slice)): 
                return self._confs[indices]
            elif isinstance(indices, (list, np.ndarray)):        
                return self._confs[indices]
            else:
                raise IndexError('indices must be an integer, a list/array of '
                                 'integers, a slice, or None')
        else:
            selids = self._indices
            if indices is None:
                return self._confs[:,selids]
            elif isinstance(indices, (int, long, slice)): 
                return self._confs[indices, selids]
            elif isinstance(indices, (list, np.ndarray)):        
                return self._confs[indices, selids]
            else:
                raise IndexError('indices must be an integer, a list/array of '
                                 'integers, a slice, or None')
    
    def delCoordset(self, index):
        """Delete a coordinate set from the ensemble."""
        
        if isinstance(index, int):
            index = [index]
        else:
            index = list(index)
        length = self._n_csets
        which = np.ones(length, np.bool)
        which[index] = False
        if which.sum() == 0:
            self._confs = None
            self._weights = None
        else:
            self._confs = self._confs[which]
            if self._weights is not None:
                self._weights = self._weights[which]
        self._n_csets -= len(index)

    def iterCoordsets(self):
        """Iterate over coordinate sets. A copy of each coordinate set for
        selected atoms is returned. Reference coordinates are not included."""
        
        if self._sel is None:
            for conf in self._confs:
                yield conf.copy()
        else:
            indices = self._getSelIndices()        
            for conf in self._confs:
                yield conf[indices].copy()
    
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
            return Conformation(self, index)
        else:
            raise IndexError('conformation index out of range')
            
    def superpose(self):
        """Superpose the ensemble onto the reference coordinates."""
        
        if self._coords is None:
            raise AttributeError('coordinates are not set, '
                                 'use setCoordinates() method to set it.')
        if self._confs is None or len(self._confs) == 0: 
            raise AttributeError('conformations are not set, '
                                 'use addCoordset() method to set it.')
        LOGGER.info('Superposing structures.')
        start = time()
        self._superpose()
        LOGGER.info(('Superposition is completed in {0:.2f} '
                           'seconds.').format((time() - start)))
        
    def _superpose(self):
        """Superpose conformations and update coordinates."""
        
        indices = self._indices
        if indices is None:
            measure._superposeTraj(self._confs, self._coords, self._weights)
        else:
            weights = None
            if self._weights is not None:
                weights = self._weights[indices]
            measure._superposeTraj(self._confs[:,indices], 
                               self._coords[indices], weights,
                               self._confs)
            
    def iterpose(self, rmsd=0.0001):
        """Iteratively superpose the ensemble until convergence.
        
        Initially, all conformations are aligned with the reference 
        coordinates. Then mean coordinates are calculated, and are set
        as the new reference coordinates. This is repeated until 
        reference coordinates do not change. This is determined by
        the value of RMSD between the new and old reference coordinates.        
        
        :arg rmsd: RMSD (A) between old and new reference coordinates 
                     to converge
        :type rmsd: float, default is 0.0001
            
        """
        
        if self._coords is None:
            raise AttributeError('coordinates are not set, '
                                 'use setCoordinates() method to set it.')
        if self._confs is None or len(self._confs) == 0: 
            raise AttributeError('conformations are not set, '
                                 'use addCoordset() method to set it.')
        LOGGER.info('Starting iterative superposition')
        start = time()
        rmsdif = 1
        step = 0
        weights = self._weights
        if weights is not None and weights.ndim == 3:
            weightsum = weights.sum(axis=0)
        length = len(self)
        while rmsdif > rmsd:
            self._superpose()
            if weights is None:
                newxyz = self._confs.sum(0) / length
            else:
                newxyz = (self._confs * weights).sum(0) / weightsum
            rmsdif = measure._calcRMSD(self._coords, newxyz)
            self._coords = newxyz
            step += 1
            LOGGER.info(('Step #{0:d}: RMSD difference = '
                               '{1:.4e}').format(step, rmsdif))
        LOGGER.info('Iterative superposition completed in {0:.2f}s.'
                    .format((time() - start)))

    def getMSFs(self):
        """Calculate and return mean square fluctuations (MSFs). 
        Note that you might need to align the conformations using 
        :meth:`superpose` or :meth:`iterpose` before calculating MSFs."""
        
        if self._confs is None: 
            return
        indices = self._indices
        if indices is None:
            mean = self._confs.mean(0)
            ssqf = np.zeros(mean.shape)
            for conf in self._confs:
                ssqf += (conf - mean) ** 2
        else:
            mean = self._confs[:, indices].mean(0)
            ssqf = np.zeros(mean.shape)
            for conf in self._confs[:, indices]:
                ssqf += (conf - mean) ** 2
        return ssqf.sum(1) / self._n_csets
    
    def getRMSFs(self):
        """Calculate and return root mean square fluctuations (RMSFs). 
        Note that you might need to align the conformations using 
        :meth:`superpose` or meth:`iterpose` before calculating RMSFs.
        
        .. versionadded:: 0.8
        
        """

        return self.getMSFs() ** 0.5
            
    def getDeviations(self):
        """Return deviations from reference coordinates. Note that you
        might need to align the conformations using :meth:`superpose` or 
        :meth:`iterpose` before calculating deviations."""
        
        if not isinstance(self._confs, np.ndarray):
            LOGGER.warning('Conformations are not set.')
            return None
        if not isinstance(self._coords, np.ndarray):
            LOGGER.warning('Coordinates are not set.')
            return None
        
        return self._getCoordsets() - self._coords 
        
    def getRMSDs(self):
        """Calculate and return root mean square deviations (RMSDs). Note that 
        you might need to align the conformations using :meth:`superpose` or 
        :meth:`iterpose` before calculating RMSDs."""
        
        if self._confs is None or self._coords is None: 
            return None
        if self._indices is None:
            return measure._calcRMSD(self._coords, self._confs, self._weights)
        else:
            indices = self._indices
            if self._weights is None:
                return measure._calcRMSD(self._coords[indices], 
                                         self._confs[:,indices])
            else:
                return measure._calcRMSD(self._coords[indices], 
                                         self._confs[:,indices],
                                         self._weights[indices])
                

class PDBEnsemble(Ensemble):
    
    """This class enables handling coordinates for heterogeneous structural 
    datasets and stores identifiers for individual conformations.
    
    |example| See usage usage in :ref:`pca-xray`, :ref:`pca-dimer`, and 
    :ref:`pca-blast`.
    
    .. versionadded:: 0.8
    
    .. note:: This class is designed to handle conformations with missing
       coordinates, e.g. atoms that are note resolved in an X-ray structure.
       For unresolved atoms, the coordinates of the reference structure is
       assumed in RMSD calculations and superpositions.
    
    >>> ensemble
    <PDB Ensemble: p38 X-ray (75 conformations, 321 atoms, 321 selected)>

    """

    def __init__(self, name='Unnamed'):
        self._identifiers = []
        Ensemble.__init__(self, name)
        
    def __repr__(self):
        return '<PDB ' + Ensemble.__repr__(self)[1:]
    
    def __str__(self):
        return 'PDB ' + Ensemble.__str__(self)
    
    def __add__(self, other):
        """Concatenate two ensembles. The reference coordinates of *self* is 
        used in the result."""
        
        if not isinstance(other, Ensemble):
            raise TypeError('an Ensemble instance cannot be added to an {0:s} '
                            'instance'.format(type(other)))
        elif self.getNumOfAtoms() != other.getNumOfAtoms():
            raise ValueError('Ensembles must have same number of atoms.')
    
        ensemble = PDBEnsemble('{0:s} + {1:s}'.format(self.getName(), 
                                                   other.getName()))
        ensemble.setCoordinates(self._coords.copy())
        ensemble.addCoordset(self._confs.copy(), self._weights.copy())
        if other._weights is None:
            ensemble.addCoordset(other.getCoordsets())
        else:
            ensemble.addCoordset(other._confs.copy(), other._weights.copy())
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
                                self._name, index.indices(len(self))))
            ens.setCoordinates(self.getCoordinates())
            ens.addCoordset(self._confs[index].copy(), 
                            self._weights[index].copy())
            return ens
        elif isinstance(index, (list, np.ndarray)):
            ens = PDBEnsemble('Conformations of {0:s}'.format(self._name))
            ens.setCoordinates(self.getCoordinates())
            ens.addCoordset(self._confs[index].copy(), 
                            self._weights[index].copy())
            return ens
        else:
            raise IndexError('invalid index')
            
    def _superpose(self):
        """Superpose conformations and return new coordinates."""

        calcT = measure._calcTransformation
        applyT = measure._applyTransformation
        if self._sel is None:
            weights = self._weights
            coords = self._coords
            confs = self._confs
            for i, conf in enumerate(confs):
                confs[i] = applyT(calcT(conf, coords, weights[i]), confs[i])
        else:            
            indices = self._getSelIndices()
            weights = self._weights[:, indices]
            coords = self._coords[indices]
            confs_selected = self._confs[:,indices]
            confs = self._confs
            for i, conf in enumerate(confs_selected):
                confs[i] = applyT(calcT(conf, coords, weights[i]), confs[i]) 

    def addCoordset(self, coords, weights=None, allcoordsets=True):
        """Add coordinate set(s) as conformation(s).
        
        :class:`~prody.atomic.Atomic` instances are accepted as *coords* 
        argument. If *allcoordsets* is ``True``, all coordinate sets from
        the :class:`~prody.atomic.Atomic` instance will be appended to the 
        ensemble. Otherwise, only the active coordinate set will be appended.

        *weights* is an optional argument. If provided, its length must
        match number of atoms. Weights of missing (not resolved) atoms 
        must be equal to ``0`` and weights of those that are resolved
        can be anything greater than ``0``. If not provided, weights of 
        atoms in this coordinate set will be set equal to ``1``."""
        
        assert isinstance(allcoordsets, bool), 'allcoordsets must be boolean'
        if weights is not None:
            assert isinstance(weights, np.ndarray), 'weights must be ndarray'
            
        ag = None
        if isinstance(coords, prody.Atomic):
            atoms = coords
            if isinstance(coords, prody.AtomGroup):
                ag = atoms
            else:
                ag = atoms.getAtomGroup()
            if allcoordsets:
                coords = atoms.getCoordsets()
            else: 
                coords = atoms.getCoordinates()
            name = ag.getName()
        elif isinstance(coords, np.ndarray):
            name = 'Unnamed'
        else:
            name = str(coords)
            try:
                if allcoordsets:
                    coords = coords.getCoordsets()
                else: 
                    coords = coords.getCoordinates()
            except AttributeError:            
                raise TypeError('coords must be a Numpy array or must have '
                                'getCoordinates attribute')

        coords = checkCoordsArray(coords, 'coords', cset=True, 
                                  n_atoms=self._n_atoms, reshape=True)
        n_csets, n_atoms, _ = coords.shape
        if self._n_atoms == 0:
            self._n_atoms = n_atoms
        if weights is None:
            weights = np.ones((n_csets, n_atoms, 1), dtype=float)
        else:
            weights = checkWeightsArray(weights, n_atoms, n_csets)

        while '  ' in name:
            name = name.replace('  ', ' ')
        name = name.replace(' ', '_')
        
        if n_csets > 1:
            self._identifiers += ['{0:s}_{1:d}'
                                  .format(name, i+1) for i in range(n_csets)]
        else:
            if ag is not None and ag.getNumOfCoordsets() > 1:
                self._identifiers.append('{0:s}_{1:d}'.format(name, 
                                         atoms.getActiveCoordsetIndex()))
            else:                
                self._identifiers.append(name)
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

    def getIdentifiers(self):
        """Return identifiers of the conformations in the ensemble.
        
        .. versionadded:: 0.8.3
        
        """
        
        return list(self._identifiers)
    
    def getCoordsets(self, indices=None):
        """Return a copy of coordinate sets at given *indices* for selected 
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
            selids = self._getSelIndices()
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
            yield conf.getCoordinates()
   
    def delCoordset(self, index):
        """Delete a coordinate set from the ensemble."""
        
        Ensemble.delCoordset(self, index)
        if isinstance(index, int):
            index = [index]
        else:
            index = list(index)
        index.sort(reverse=True)
        for i in index:
            self._identifiers.pop(i)
            
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
        :meth:`iterpose` before calculating RMSDs.
        
        >>> rmsd = ensemble.getRMSDs().round(2)
        >>> print( rmsd[0] )
        0.74
        >>> print( rmsd )
        [ 0.74  0.53  0.58  0.6   0.61  0.72  0.62  0.74  0.69  0.65  0.48  0.54
          0.48  0.75  0.56  0.76  0.84  0.49  0.69  0.74  0.69  0.49  0.69  0.61
          0.73  0.64  0.52  0.51  0.65  0.84  0.77  0.69  0.82  1.19  0.6   1.12
          0.71  0.61  0.73  0.57  0.99  0.94  0.85  0.98  0.58  0.61  0.64  0.89
          0.82  0.95  0.88  0.86  1.09  0.7   0.72  0.86  0.76  0.82  0.88  0.95
          0.63  0.92  1.08  0.44  0.43  0.49  0.64  0.88  0.72  0.9   0.96  1.23
          0.58  0.66  0.83]
          
        """
        
        if self._confs is None or self._coords is None: 
            return None
    
        if self._sel is None:
            return measure._calcRMSD(self._coords, self._confs, self._weights)
        else:
            indices = self._indices
            return measure._calcRMSD(self._coords[indices], 
                                     self._confs[:,indices],
                                     self._weights[:, indices])

    def setWeights(self, weights):
        """Set atomic weights."""
        
        if self._n_atoms == 0:
            raise AttributeError('coordinates are not set')
        elif not isinstance(weights, np.ndarray): 
            raise TypeError('weights must be an ndarray instance')
        elif weights.shape[:2] != (self._n_csets, self._n_atoms):
            raise ValueError('shape of weights must (n_confs, n_atoms[, 1])')
        if weights.dtype not in (np.float32, np.float64):
            try:
                weights = weights.astype(np.float64)
            except ValueError:
                raise ValueError('coords array cannot be assigned type '
                                 '{0:s}'.format(np.float64))
        if np.any(weights < 0):
            raise ValueError('weights must greater or equal to 0')
            
        if weights.ndim == 2:
            weights = weights.reshape((self._n_csets, self._n_atoms, 1))
        self._weights = weights


def saveEnsemble(ensemble, filename=None):
    """Save *ensemble* model data as :file:`filename.ens.npz`. 
    
    If *filename* is ``None``, name of the *ensemble* will be used as 
    the filename, after " " (blank spaces) in the name are replaced with "_" 
    (underscores).  
    
    Extension is :file:`.ens.npz`.
    
    Upon successful completion of saving, filename is returned.
    
    This function makes use of :func:`numpy.savez` function.
    
    """
    
    if not isinstance(ensemble, Ensemble):
        raise TypeError('invalid type for ensemble, {0:s}'
                        .format(type(ensemble)))
    if len(ensemble) == 0:
        raise ValueError('ensemble instance does not contain data')
    
    dict_ = ensemble.__dict__
    attr_list = ['_name', '_confs', '_weights', '_coords']
    if isinstance(ensemble, PDBEnsemble):
        attr_list.append('_identifiers')
    if filename is None:
        filename = ensemble.getName().replace(' ', '_')
    attr_dict = {}
    for attr in attr_list:
        value = dict_[attr]
        if value is not None:
            attr_dict[attr] = value
    filename += '.ens.npz'
    np.savez(filename, **attr_dict)
    return filename

def loadEnsemble(filename):
    """Return ensemble instance after loading it from file (*filename*).
    
    .. seealso: :func:`saveEnsemble`
    
    This function makes use of :func:`numpy.load` function.
    
    """
    
    attr_dict = np.load(filename)
    weights = attr_dict['_weights']
    isPDBEnsemble = False
    if weights.ndim == 3:
        isPDBEnsemble = True
        ensemble = PDBEnsemble(str(attr_dict['_name']))
    else:
        ensemble = Ensemble(str(attr_dict['_name']))
    ensemble.setCoordinates(attr_dict['_coords'])
    if isPDBEnsemble:
        ensemble.addCoordset(attr_dict['_confs'], weights)
        if '_identifiers' in attr_dict.files:
            ensemble._identifiers = list(attr_dict['_identifiers'])
    else:
        ensemble.addCoordset(attr_dict['_confs'])
        if weights != np.array(None): 
            ensemble.addCoordset(weights)
    return ensemble

class ConformationBase(object):

    """Base class for :class:`Conformation` and :class:`Frame`."""

    __slots__ = ['_ensemble', '_index', '_sel', '_indices']

    def __init__(self, ensemble, index):
        self._ensemble = ensemble
        self._index = index
        self._sel = ensemble.getSelection()
        self._indices = ensemble._getSelIndices()
        
    def __repr__(self):
        return ('<{0:s}: {1:d} from {2:s} (selected {3:d} of {4:d} atoms)>'
               ).format(self.__class__.__name__, self._index, 
                        self._ensemble.getName(), self.getNumOfSelected(), 
                        self._ensemble.getNumOfAtoms())

    def __str__(self):
        return '{0:s} {1:d} from {2:s}'.format(
                    self._index, self._ensemble.getName())

    def getNumOfAtoms(self):
        """Return number of atoms."""
        
        return self._ensemble.getNumOfAtoms()
    
    def getNumOfSelected(self):
        """Return number of selected atoms."""
        
        if self._sel is None:
            return self._ensemble.getNumOfAtoms()
        else:
            return len(self._indices)
    
    def getIndex(self):
        """Return index."""
        
        return self._index
    
    def getWeights(self):
        """Return coordinate weights for selected atoms."""
        
        if self._sel is None:
            return self._ensemble.getWeights()
        else:
            return self._ensemble.getWeights()[self._indices]

    def _getWeights(self):
        
        if self._sel is None:
            return self._ensemble._getWeights()
        else:
            return self._ensemble._getWeights()[self._indices]


class Conformation(ConformationBase):
    
    """A class to provide methods on a conformation in an ensemble.  
    Instances of this class do not keep coordinate and weights data.
    
    """
    
    def __init__(self, ensemble, index):
        """Instantiate with an ensemble instance, and an index."""
        ConformationBase.__init__(self, ensemble, index)
        
    def getEnsemble(self):
        """Return the ensemble that this conformation belongs to."""
        
        return self._ensemble
    
    def getCoordinates(self):
        """Return a copy of the coordinates of the conformation. If a subset
        of atoms are selected in the ensemble, coordinates for selected
        atoms will be returned."""
        
        if self._ensemble._confs is None:
            return None
        indices = self._indices
        if indices is None:
            return self._ensemble._confs[self._index].copy()
        else:
            return self._ensemble._confs[self._index, indices].copy()
    
    def _getCoordinates(self):

        if self._ensemble._confs is None:
            return None
        indices = self._indices
        if indices is None:
            return self._ensemble._confs[self._index]
        else:
            return self._ensemble._confs[self._index, indices]

    
    def getDeviations(self):
        """Return deviations from the ensemble reference coordinates. 
        Deviations are calculated for selected atoms."""
        
        ensemble = self._ensemble 
        if ensemble._confs is None:
            return None
        indices = ensemble._indices
        if indices is None:
            return ensemble._confs[self._index] - ensemble._coords 
        else:
            return (ensemble._confs[self._index, indices].copy() - 
                    ensemble._coords[indices])

    def getRMSD(self):
        """Return RMSD from the ensemble reference coordinates. RMSD is
        calculated for selected atoms."""
        
        ensemble = self._ensemble 
        indices = self._indices
        if indices is None:
            return measure._calcRMSD(ensemble._coords,
                                     ensemble._confs[self._index], 
                                     self.getWeights())[0]
        else:
            return measure._calcRMSD(ensemble._coords[indices],
                                     ensemble._confs[self._index, indices], 
                                     self.getWeights())[0]
    
class PDBConformation(Conformation):
    
    """This class is the same as :class:`Conformation`, except that the 
    conformation has a name (or identifier), e.g. PDB identifier.
    
    .. versionadded:: 0.8

    >>> conf = ensemble[0] 
    >>> conf
    <PDB Conformation: 1a9u_ca from p38 X-ray (index: 0; selected 321 of 321 atoms)>

    """
    
    def __repr__(self):
        return ('<PDB Conformation: {0:s} from {1:s} (index: {2:d}; '
                'selected {3:d} of {4:d} atoms)>').format(
                    self._ensemble._identifiers[self._index], 
                    self._ensemble.getName(), self._index, 
                    self.getNumOfSelected(), self.getNumOfAtoms())
    
    def __str__(self):
        return 'PDB Conformation {0:s} from {1:s}'.format(
                    self._ensemble._identifiers[self._index], 
                    self._ensemble.getName())
    
    def getIdentifier(self):
        """Return the identifier of the conformation instance.
        
        >>> print( conf.getIdentifier() )
        1a9u_ca
        
        """
        
        return self._ensemble._identifiers[self._index]
    
    def setIdentifier(self, identifier):
        """Set the identifier of the conformation instance.
        
        >>> conf.setIdentifier('1a9u')
        >>> print( conf.getIdentifier() )
        1a9u
        
        """
        
        self._ensemble._identifiers[self._index] = str(identifier)
        
    def getCoordinates(self):
        """Return a copy of the coordinates of the conformation. If a subset
        of atoms are selected in the ensemble, coordinates for selected
        atoms will be returned.
        
        .. warning:: When there are atoms with weights equal to zero (0),
           their coordinates will be replaced with the coordinates of the
           ensemble reference coordinate set.

        """
        
        ensemble = self._ensemble
        if ensemble._confs is None:
            return None
        indices = ensemble._indices
        index = self._index
        if indices is None:
            coords = ensemble._confs[index].copy()
            which = ensemble._weights[index].flatten()==0
            coords[which] = ensemble._coords[which]
        else: 
            coords = ensemble._confs[index, indices].copy()
            which = ensemble._weights[index, indices].flatten()==0
            coords[which] = ensemble._coords[indices][which]
        return coords
    
    _getCoordinates = getCoordinates
    
    def getDeviations(self):
        """Return deviations from the ensemble reference coordinates. 
        Deviations are calculated for selected atoms."""
        
        indices = self._indices
        if indices is None:
            return self.getCoordinates() - self._ensemble._coords
        else:
            return self.getCoordinates() - self._ensemble._coords[indices]
    
    def getRMSD(self):
        """Return RMSD from the ensemble reference coordinates. RMSD is
        calculated for selected atoms.
        
        >>> print( conf.getRMSD().round(2) )
        0.74

        """
        
        ensemble = self._ensemble
        index = self._index
        indices = ensemble._indices
        if indices is None:
            return measure._calcRMSD(ensemble._coords,
                                     ensemble._confs[index], 
                                     ensemble._weights[index])
        else:
            return measure._calcRMSD(ensemble._coords[indices],
                                     ensemble._confs[index, indices], 
                                     ensemble._weights[index, indices])
    
    def getWeights(self):
        """Return coordinate weights for selected atoms."""
        
        ensemble = self._ensemble
        indices = ensemble._indices
        if indices is None:
            return ensemble._weights[self._index].copy()
        else:
            return ensemble._weights[self._index, indices]
    
    def _getWeights(self):
        
        ensemble = self._ensemble
        indices = ensemble._indices
        if indices is None:
            return ensemble._weights[self._index]
        else:
            return ensemble._weights[self._index, indices]


class Frame(ConformationBase):
    
    """A class to provide methods on a frame in a trajectory.
    
    """
    
    __slots__ = ['_ensemble', '_index', '_coords', '_indices', '_sel', 
                 '_unitcell']

    def __init__(self, trajectory, index, coords, unitcell=None):
        """Instantiate with an trajectory instance, index, and a name."""
        ConformationBase.__init__(self, trajectory, index)
        self._coords = coords
        self._unitcell = unitcell
        
    def getTrajectory(self):
        """Return the trajectory that this frame belongs to."""
        
        return self._ensemble
    
    def getCoordinates(self):
        """Return a copy of coordinates for selected atoms."""
        
        return self._coords.copy()
    
    def _getCoordinates(self):
        """Return coordinates for selected atoms."""
        
        return self._coords
    
    def getUnitcell(self):
        """Return a copy of unitcell array."""
        
        if self._unitcell is not None:
             return self._unitcell.copy()
    
    def _getUnitcell(self):
        return self._unitcell
    
    def getDeviations(self):
        """Return deviations from the trajectory reference coordinates."""

        indices = self._indices 
        if indices is None:
            return self._coords - ensemble._coords
        else:
            return self._coords - ensemble._coords[indices]

    def getRMSD(self):
        """Return RMSD from the ensemble reference coordinates."""
        
        indices = self._indices 
        ensemble = self._ensemble
        ensemble = self._ensemble
        if indices is None:
            return measure._calcRMSD(self._coords, ensemble._coords, 
                                                    ensemble._weights)
        else:
            if ensemble._weights is None:
                return measure._calcRMSD(self._coords, 
                                         ensemble._coords[indices])
            else:
                return measure._calcRMSD(self._coords, 
                                         ensemble._coords[indices], 
                                         ensemble._weights[indices])
        

    def superpose(self):
        """Superpose frame coordinates onto the trajectory reference 
        coordinates."""
        
        indices = self._indices 
        ensemble = self._ensemble
        if indices is None:
            self._coords, t = measure.superpose(self._coords, 
                                                ensemble._coords, 
                                                ensemble._weights)
        else:
            if ensemble._weights is None:
                measure._superpose(self._coords, ensemble._coords[indices])
            else:
                measure._superpose(self._coords, ensemble._coords[indices], 
                                                 ensemble._weights[indices])
    
def trimEnsemble(pdbensemble, **kwargs):
    """Return a PDB ensemble obtained by trimming given *pdbensemble*.
    
    .. versionadded:: 0.5.3
    
    This function helps selecting atoms in a pdb ensemble based on one of the 
    following criteria, and returns them in a new :class:`PDBEnsemble` 
    instance.
        
    **Occupancy**
    
    If weights in the ensemble correspond to atomic occupancies, then this 
    option may be used to select atoms with average occupancy values higher
    than the argument *occupancy*.  Function will calculate average occupancy 
    by dividing the sum of weights for each atom to the number of conformations
    in the ensemble.
    
    :arg occupancy: average occupancy for selection atoms in a pdb ensemble, 
                    must be 0 < *occupancy* <= 1
    :type occupancy: float
    
    """
    
    if not isinstance(pdbensemble, PDBEnsemble):
        raise TypeError('pdbensemble argument must be a PDBEnsemble')
    if pdbensemble.getNumOfConfs() == 0 or pdbensemble.getNumOfAtoms() == 0:
        raise ValueError('coordinates or conformations must be set for '
                         'pdbensemble')
    
    if 'occupancy' in kwargs:
        occupancy = float(kwargs['occupancy'])
        assert 0 < occupancy <=1, ('occupancy is not > 0 and <= 1: '
                                   '{0:s}'.format(repr(occupancy)))
        n_confs = pdbensemble.getNumOfConfs()
        assert n_confs > 0, 'pdbensemble does not contain any conformations'
        weights = calcSumOfWeights(pdbensemble)
        assert weights is not None, 'weights must be set for pdbensemble'
        weights = weights.flatten()
        mean_weights = weights / n_confs
        
        torf = mean_weights >= occupancy
        
    else:
        return None
    
    trimmed = PDBEnsemble(pdbensemble.getName())
    coords = pdbensemble.getCoordinates()
    if coords is not None:
        trimmed.setCoordinates( coords[torf] )
    confs = pdbensemble.getCoordsets()
    if confs is not None:
        weights = pdbensemble.getWeights()
        trimmed.addCoordset( confs[:, torf], weights[:, torf] )
    return trimmed

def calcSumOfWeights(pdbensemble):
    """Return sum of weights from a PDB ensemble.
    
    Weights are summed for each atom over conformations in the ensemble.
    Size of the plotted array will be equal to the number of atoms.
    
    When analyzing an ensemble of X-ray structures, this function can be used 
    to see how many times a residue is resolved.
    
    >>> print( calcSumOfWeights(ensemble) ) # doctest: +ELLIPSIS
    [ 74.  75.  75.  75.  75.  75.  75.  75.  75.  73.  73.  74.  75.  75.  75.
      75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  70.  73.  75.  75.
      ...
      75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.  75.
      75.  75.  75.  75.  75.  75.]
            
    Each number in the above example corresponds to a residue (or atoms) and 
    shows the number of structures in which the corresponding residue is 
    resolved. 
    
    """
    
    if not isinstance(pdbensemble, PDBEnsemble):
        raise TypeError('pdbensemble must be a PDBEnsemble instance')
    
    weights = pdbensemble.getWeights()
    
    if weights is None:
        return None
    
    return weights.sum(0).flatten()
    
    
def showSumOfWeights(pdbensemble, *args, **kwargs):
    """Show sum of weights for a PDB ensemble using 
    :func:`~matplotlib.pyplot.plot`.
    
    Weights are summed for each atom over conformations in the ensemble.
    Size of the plotted array will be equal to the number of atoms.
    
    When analyzing an ensemble of X-ray structures, this function can be used 
    to see how many times a residue is resolved.
    
    """
    """
    *indices*, if given, will be used as X values. Otherwise, X axis will
    start from 0 and increase by 1 for each atom. 
    
    """
    
    if plt is None: prody.importPyPlot()
    if not plt: return None
    if not isinstance(pdbensemble, PDBEnsemble):
        raise TypeError('pdbensemble must be a PDBEnsemble instance')
    weights = calcSumOfWeights(pdbensemble)
    if weights is None:
        return None
    show = plt.plot(weights, *args, **kwargs)
    axis = list(plt.axis())
    axis[2] = 0
    axis[3] += 1
    plt.axis(axis)
    plt.xlabel('Atom index')
    plt.ylabel('Sum of weights')
    return show


RECSCALE32BIT = 1
RECSCALE64BIT = 2

class TrajectoryBase(EnsembleBase):
    
    """Base class for :class:`Trajectory` and :class:`TrajectoryFile`.
    Derived classes must implement functions described in this class.
    
    """
    
    def __init__(self, name):
        EnsembleBase.__init__(self, name)
        self._nfi = 0
        self._closed = False
    
    def __iter__(self):
        if not self._closed:
            while self._nfi < self._n_csets: 
                yield self.next()
    
    def __getitem__(self, index):
        if isinstance(index, int):
            return self.getFrame(index)
        elif isinstance(index, (slice, list, np.ndarray)):
            if isinstance(index, slice):
                ens = Ensemble('{0:s} ({1[0]:d}:{1[1]:d}:{1[2]:d})'.format(
                                    self._name, index.indices(len(self))))
            else:
                ens = Ensemble('{0:s} slice'.format(self._name))
            ens.setCoordinates(self.getCoordinates())
            if self._weights is not None:
                ens.setWeights(self._weights.copy())
            ens.addCoordset(self.getCoordsets(index))
            return ens
        else:
            raise IndexError('invalid index')
    
    def getNumOfFrames(self):
        """Return number of frames."""
        
        return self._n_csets
    
    def getNextFrameIndex(self):
        """Return the index of the next frame."""
        
        return self._nfi
    
    def iterCoordsets(self):
        """Iterate over coordinate sets. Coordinates for selected atoms are 
        returned. Reference coordinates are not included. Iteration starts
        from the current position in the trajectory."""

        if not self._closed:
            while self._nfi < self._n_csets: 
                yield self.nextCoordset()
    
    def getCoordsets(self, indices=None):
        """Returns coordinate sets at given *indices*. *indices* may be an 
        integer, a list of ordered integers or ``None``. ``None`` returns all 
        coordinate sets. If a list of indices is given, unique numbers will
        be selected and sorted. That is, this method will always return unique 
        coordinate sets in the order they appear in the trajectory file.
        Shape of the coordinate set array is (n_sets, n_atoms, 3)."""
        pass
    
    def getFrame(self, index):
        """Return frame at given *index*."""
        pass

    def nextCoordset(self):
        """Return next coordinate set."""
        pass
    
    def next(self):
        """Return next frame."""
        pass

    def goto(self, n):
        """Go to the frame at index *n*. ``n=0`` will rewind the trajectory
        to the beginning. ``n=-1`` will go to the last frame."""
        pass

    def skip(self, n):
        """Skip *n* frames. *n* must be a positive integer."""
        pass

    def reset(self):
        """Go to first frame whose index is 0."""
        pass

    def close(self):
        """Close trajectory file."""
        pass
    
    def hasUnitcell(self):
        """Return ``True`` if trajectory has unitcell data."""
        pass
    

class TrajectoryFile(TrajectoryBase):
    
    """A base class for providing a consistent interface over trajectories in 
    different formats. 
    
    .. versionadded:: 0.8
    
    """
    
    
    def __init__(self, filename):
        """Instantiate with a trajectory *filename*. The file will be 
        automatically opened for reading at instantiation. 
        Use :meth:`addFile` for appending files to the trajectory."""
        
        if not os.path.isfile(filename):
            raise IOError("[Errno 2] No such file or directory: '{0:s}'"
                          .format(filename))
        self._filename = filename
        self._file = open(filename, 'rb')
        name = os.path.splitext(os.path.split(filename)[1])[0]
        TrajectoryBase.__init__(self, name)
        self._bytes_per_frame = None
        self._first_byte = None
        self._dtype = np.float32
        
        self._timestep = 1
        self._first_ts = 0
        self._framefreq = 1
        self._n_fixed = 0
        
    
    def __repr__(self):
        if self._closed:
            return ('<{0:s}: {1:s} (closed)>').format(
                        self.__class__.__name__, self._name)
        else:
            return ('<{0:s}: {1:s} (next {2:d} of {3:d} frames, '
                    'selected {4:d} of {5:d} atoms)>').format(
                    self.__class__.__name__, self._name, 
                    self._nfi, self._n_csets, self.getNumOfSelected(),
                    self._n_atoms)
    
    def __str__(self):
        return '{0:s} {1:s}'.format(self.__class__.__name__, self._name)
    
       
    def getFilename(self, absolute=False):
        """Return relative path to the current file. For absolute path,
        pass ``absolute=True`` argument."""
        
        if absolute:
            return os.path.abspath(self._filename)    
        return prody.relpath(self._filename)
    
    def getFrame(self, index):
        """Return frame at given *index*."""
        
        if self._closed:
            return None
        if not isinstance(index, (int, long)):
            raise IndexError('index must be an integer')
        if not 0 <= index < self._n_csets:
            raise IndexError('index must be greater or equal to 0 and less '
                             'than number of frames')
        nfi = self._nfi
        if index > nfi:
            self.skip(index - nfi)
        elif index < nfi:
            self.reset()
            if index > 0:
                self.skip(index)
        return self.next()
    
    getFrame.__doc__ = TrajectoryBase.getFrame.__doc__
                
    def getCoordsets(self, indices=None):
        
        if indices is None:
            indices = np.arange(self._n_csets)
        elif isinstance(indices, (int, long)):
            indices = np.array([indices])
        elif isinstance(indices, slice):
            indices = np.arange(*indices.indices(self._n_csets))
            indices.sort()
        elif isinstance(indices, (list, np.ndarray)):
            indices = np.unique(indices)
        else:
            raise TypeError('indices must be an integer or a list of integers')

        nfi = self._nfi
        self.reset()

        n_atoms = self.getNumOfSelected() 
        coords = np.zeros((len(indices), n_atoms, 3), self._dtype)

        prev = 0
        next = self.nextCoordset
        for i, index in enumerate(indices):
            diff = index - prev
            if diff > 1:
                self.skip(diff-1)
            xyz = next()
            if xyz is None:         
                LOGGER.warning('Expected {0:d} frames, but parsed {1:d}.'
                               .format(len(indices), i))
                self.goto(nfi)
                return coords[:i]
            coords[i] = xyz 
            prev = index

        self.goto(nfi)
        return coords
    
    getCoordsets.__doc__ = TrajectoryBase.getCoordsets.__doc__
    
    def skip(self, n):
     
        if not isinstance(n, (int, long)):
            raise ValueError('n must be an integer')
        if not self._closed and n > 0:
            left = self._n_csets - self._nfi
            if n > left:
                n = left
            self._file.seek(n * self._bytes_per_frame, 1)                
            self._nfi += n
            
    skip.__doc__ = TrajectoryBase.skip.__doc__
    
    def goto(self, n):
        
        if self._closed:
            return None
        if not isinstance(n, (int, long)):
            raise ValueError('n must be an integer')
        n_csets = self._n_csets
        if n == 0:
            self.reset()
        else:
            if n < 0:
                n = n_csets + n
            if n < 0:
                n = 0
            elif n > n_csets: 
                n = n_csets
            self._file.seek(self._first_byte + n * self._bytes_per_frame)
            self._nfi = n
            
    goto.__doc__ = TrajectoryBase.goto.__doc__  
    
    def reset(self):

        if not self._closed:
            self._file.seek(self._first_byte)
            self._nfi = 0
            
    reset.__doc__ = TrajectoryBase.reset.__doc__  
    
    def close(self):
       
        self._file.close()
        self._nfi = 0
        self._closed = True
    
    close.__doc__ = TrajectoryBase.close.__doc__
    
    def getTimestep(self):
        """Return timestep size."""
        
        return self._timestep
    
    def getFirstTimestep(self):
        """Return first timestep value."""
        
        return self._first_ts
    
    def getFrameFreq(self):
        """Return timesteps between frames."""
        
        return self._framefreq
    
    def getNumOfFixed(self):
        """Return number of fixed atoms."""
        
        return self._n_fixed

DEBUG = False

class DCDFile(TrajectoryFile):
    
    """A class for reading DCD files.
    
    .. versionadded:: 0.8"""
    
    def __init__(self, filename):
        """Instantiate with a DCD filename. DCD header and first frame is 
        parsed at instantiation. Coordinates from the first frame is set 
        as the reference coordinates."""
        
        TrajectoryFile.__init__(self, filename)
        self._parseHeader()
        
    def _parseHeader(self):
        """Read the header information from a dcd file.
        Input: fd - a file struct opened for binary reading.
        Output: 0 on success, negative error code on failure.
        Side effects: *natoms set to number of atoms per frame
                      *nsets set to number of frames in dcd file
                      *istart set to starting timestep of dcd file
                      *nsavc set to timesteps between dcd saves
                      *delta set to value of trajectory timestep
                      *nfixed set to number of fixed atoms 
                      *freeind may be set to heap-allocated space
                      *reverse set to one if reverse-endian, zero if not.
                      *charmm set to internal code for handling charmm data.
        """
        
        dcd = self._file
        endian = '' #'=' # native endian
        rec_scale = RECSCALE32BIT
        charmm = None
        dcdcordmagic = unpack(endian+'i', 'CORD')[0]
        # Check magic number in file header and determine byte order
        bits = dcd.read(calcsize('ii'))
        temp = unpack(endian+'ii', bits)
        if DEBUG: print len(temp), temp
        if temp[0] + temp[1] == 84:
            LOGGER.info('Detected CHARMM -i8 64-bit DCD file of native '
                        'endianness.')
            rec_scale = RECSCALE64BIT
        elif temp[0] == 84 and temp[1] == dcdcordmagic:
            LOGGER.info('Detected standard 32-bit DCD file of native '
                        'endianness.')
        else:
            if unpack('>ii', bits) == temp:
                endian = '>'
            else:
                endian = '<'
            temp = unpack(endian+'ii', bits)
            if temp[0] + temp[1] == 84:
                rec_scale = RECSCALE64BIT
                LOGGER.info('Detected CHARMM -i8 64-bit DCD file of opposite '
                            'endianness.')
            else:
                endian = ''
                temp = unpack(endian+'ii', bits)
                if temp[0] == 84 and temp[1] == dcdcordmagic:
                    LOGGER.info('Detected standard 32-bit DCD file of '
                                'opposite endianness.')
                else:
                    raise IOError('Unrecognized DCD header or unsupported '
                                  'DCD format.')
                    
        
        # check for magic string, in case of long record markers
        if rec_scale == RECSCALE64BIT:
            raise IOError('CHARMM 64-bit DCD files are not yet supported.');
            temp = unpack('I', dcd.read(calcsize('I')))
            if temp[0] != dcdcordmagic: 
                raise IOError('Failed to find CORD magic in CHARMM -i8 64-bit '
                              'DCD file.');
        
        # Buffer the entire header for random access
        bits = dcd.read(80)
        # CHARMm-genereate DCD files set the last integer in the
        # header, which is unused by X-PLOR, to its version number.
        # Checking if this is nonzero tells us this is a CHARMm file
        # and to look for other CHARMm flags.
        temp = unpack(endian + 'i'*20 , bits)
        if DEBUG: print len(temp), temp
        if temp[-1] != 0:
            charmm = True

        if charmm:
            LOGGER.info('CHARMM format DCD file (also NAMD 2.1 and later).')
            temp = unpack(endian + 'i'*9 + 'f' + 'i'*10 , bits)
        else:
            LOGGER.info('X-PLOR format DCD file (also NAMD 2.0 and earlier) '
                        'is not supported.')
            return None
        
        # Store the number of sets of coordinates (NSET)
        self._n_csets = temp[0]
        # Store ISTART, the starting timestep
        self._first_ts = temp[1]
        # Store NSAVC, the number of timesteps between dcd saves
        self._framefreq = temp[2]
        # Store NAMNF, the number of fixed atoms
        self._n_fixed = temp[8]
        
        if self._n_fixed > 0:
            raise IOError('DCD files with fixed atoms is not yet supported.')
        
        # Read in the timestep, DELTA
        # Note: DELTA is stored as double with X-PLOR but as float with CHARMm
        self._timestep = temp[9]
        self._unitcell = temp[10] == 1
        
        # Get the end size of the first block
        if unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))[0] != 84:
            raise IOError('Unrecognized DCD format.')
        
        # Read in the size of the next block
        temp = unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))
        if DEBUG: print len(temp), temp
        if temp[0] != 164:
            raise IOError('Unrecognized DCD format.')

        # Read NTITLE, the number of 80 character title strings there are
        temp = unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))
        if DEBUG: print len(temp), temp
        self._title = dcd.read(80)
        if DEBUG: print self._title
        self._remarks = dcd.read(80)
        if DEBUG: print self._remarks
        # Get the ending size for this block
        temp = unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))
        if DEBUG: print len(temp), temp
        if temp[0] != 164:
            raise IOError('Unrecognized DCD format.')


        # Read in an integer '4'
        if unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))[0] != 4:
            raise IOError('Unrecognized DCD format.')

        # Read in the number of atoms
        self._n_atoms = unpack(endian+'i',dcd.read(rec_scale*calcsize('i')))[0]
        # Read in an integer '4'
        if unpack(endian+'i', dcd.read(rec_scale * calcsize('i')))[0] != 4:
            raise IOError('Bad DCD format.')

        self._is64bit = rec_scale == RECSCALE64BIT
        self._endian = endian
        self._n_floats = (self._n_atoms + 2) * 3
        
        if self._is64bit:
            if self._unitcell:
                self._bytes_per_frame = 56 + self._n_floats * 8
            else:
                self._bytes_per_frame = self._n_floats * 8
            LOGGER.warning('Reading of 64 bit DCD files has not been tested. '
                           'Please report any problems that you may find.')
            self._dtype = np.float64
        else: 
            if self._unitcell:
                self._bytes_per_frame = 56 + self._n_floats * 4
            else:
                self._bytes_per_frame = self._n_floats * 4
            self._dtype = np.float32
        
        self._first_byte = self._file.tell()
        n_csets = (os.path.getsize(self._filename) - self._first_byte
                    ) / self._bytes_per_frame
        if n_csets != self._n_csets: 
            LOGGER.warning('DCD is corrupt, header indicates {0:d} '
                           'frames, file contains {1:d}.'
                           .format(self._n_csets, n_csets))
            self._n_csets = n_csets
        self._coords = self.nextCoordset()
        self._file.seek(self._first_byte)
        self._nfi = 0
   
    def hasUnitcell(self):
        
        return self._unitcell
    
    hasUnitcell.__doc__ = TrajectoryBase.hasUnitcell.__doc__ 
   
    def getTitle(self):
        """Return title parsed from DCD file."""
        
        return self._title
    
    def getRemarks(self):
        """Return remarks parsed from DCD file."""
        
        return self._remarks
        
    def next(self):
        
        nfi = self._nfi
        if not self._closed and nfi < self._n_csets:
            unitcell = self._nextUnitcell()
            coords = self._nextCoordset()
            frame = Frame(self, nfi, coords, unitcell)
            return frame
    
    next.__doc__ = TrajectoryBase.next.__doc__  
        
    def nextCoordset(self):
        """Return next coordinate set."""
        
        if not self._closed and self._nfi < self._n_csets:
            #Skip extended system coordinates (unit cell data)
            if self._unitcell:
                self._file.seek(56, 1)
            return self._nextCoordset()
            
    def _nextCoordset(self):
    
            n_floats = self._n_floats
            n_atoms = self._n_atoms
            xyz = np.fromfile(self._file, dtype=self._dtype, count=n_floats)
            if len(xyz) != n_floats:
                return None
            xyz = xyz.reshape((3, n_atoms+2)).T[1:-1,:]
            xyz = xyz.reshape((n_atoms, 3))
            self._nfi += 1
            if self._sel is None:
                return xyz
            else:
                return xyz[self._indices]

    nextCoordset.__doc__ = TrajectoryBase.nextCoordset.__doc__  

    def _nextUnitcell(self):
        
        if self._unitcell:
            self._file.read(4)
            unitcell = np.fromfile(self._file, dtype=np.float64, count=6)
            unitcell = unitcell[[0,2,5,1,3,4]]
            if np.all(abs(unitcell[3:]) <= 1):
                # This file was generated by CHARMM, or by NAMD > 2.5, with the angle */
                # cosines of the periodic cell angles written to the DCD file.        */ 
                # This formulation improves rounding behavior for orthogonal cells    */
                # so that the angles end up at precisely 90 degrees, unlike acos().   */
                unitcell[3:] = 90. - np.arcsin(unitcell[3:]) * 90 / PISQUARE  
            self._file.read(4)
            return unitcell

    def getCoordsets(self, indices=None):
        """Returns coordinate sets at given *indices*. *indices* may be an 
        integer, a list of integers or ``None``. ``None`` returns all 
        coordinate sets."""
                
        if self._indices is None and \
            (indices is None or indices == slice(None)):
            nfi = self._nfi
            self.reset()
            n_floats = self._n_floats + 14
            n_atoms = self._n_atoms
            n_csets = self._n_csets
            data = np.fromfile(self._file, self._dtype, 
                               n_floats * n_csets)
            if len(data) > n_floats * n_csets:
                n_csets = len(data)/n_floats
                data = data[:n_csets]
                LOGGER.warning('DCD is corrupt, {0:d} out of {1:d} frames '
                               'were parsed.'.format(n_csets, self._n_csets))
            data = data.reshape((n_csets, n_floats))
            data = data[:, 14:]
            data = data.reshape((n_csets, 3, n_atoms+2))
            data = data[:, :, 1:-1]
            data = data.transpose(0, 2, 1)
            self.goto(nfi)
            return data
        else:            
            return TrajectoryFile.getCoordsets(self, indices)
    
        getCoordsets.__doc__ = TrajectoryBase.getCoordsets.__doc__


class Trajectory(TrajectoryBase):
    
    """A class for handling trajectories in multiple files.
    
    .. versionadded:: 0.8"""
        
    def __init__(self, name):
        """Trajectory can be instantiated with a *name* or a filename. When
        name is a valid path to a trajectory file it will be opened for 
        reading."""
        
        TrajectoryBase.__init__(self, name)
        self._trajectory = None
        self._trajectories = []
        self._filenames = set()
        self._n_files = 0
        self._cfi = 0 # current file index
        if os.path.isfile(name):
            self.addFile(name)
        
        
    def __repr__(self):
        if self._closed:
            return ('<Trajectory: {0:s} (closed)>').format(self._name)
        else:
            return ('<Trajectory: {0:s} ({1:d} files, next {2:d} of {3:d} '
                    'frames, selected {4:d} of {5:d} atoms)>').format(
                    self._name, self._n_files, self._nfi, 
                    self._n_csets, self.getNumOfSelected(), self._n_atoms)
    
    def __str__(self):
        return '{0:s} {1:s}'.format(self.__class__.__name__, self._name)

    def _nextFile(self):
        self._cfi += 1
        if self._cfi < self._n_files: 
            self._trajectory = self._trajectories[self._cfi]
            if self._trajectory.getNextFrameIndex() > 0:
                self._trajectory.reset()

    def _gotoFile(self, i):
        if i < self._n_files:
            self._cfi = i
            self._trajectory = self._trajectories[i]
            if self._trajectory.getNextFrameIndex() > 0:
                self._trajectory.reset()
        
    def addFile(self, filename):
        """Add a file to the trajectory instance. Currently only DCD files
        are supported."""
        
        if not isinstance(filename, str):
            raise ValueError('filename must be a string')
        if os.path.abspath(filename) in self._filenames:        
            raise IOError('{0:s} is already added to the trajectory'
                          .format(filename))
        ext = os.path.splitext(filename)[1]
        if ext.lower() == '.dcd':
            traj = DCDFile(filename)
        else: 
            raise ValueError('Trajectory file type "{0:s}" is not recognized.'
                             .format(ext))
        
        n_atoms = self._n_atoms
        if n_atoms != 0 and n_atoms != traj.getNumOfAtoms():
            raise IOError('{0:s} must have same number of atoms as previously '
                          'loaded files'.format(traj.getName()))
         
        if self._n_files == 0:
            self._trajectory = traj                
            self._name = traj.getName()
        if n_atoms == 0:
            self._n_atoms = traj.getNumOfAtoms()
            self._coords = traj._coords
        self._trajectories.append(traj)
        self._n_csets += traj.getNumOfFrames()
        self._n_files += 1
   
    def getNumOfFiles(self):
        """Return number of open trajectory files."""
        
        return self._n_files

    def getFilenames(self, absolute=False):
        """Return list of filenames opened for reading."""
        
        return [traj.getFilename(absolute) for traj in self._trajectories]
        
    def getFrame(self, index):
        
        self.goto(index)
        return self.next()

    def getCoordsets(self, indices=None):
        
        if indices is None:
            indices = np.arange(self._n_csets)
        elif isinstance(indices, (int, long)):
            indices = np.array([indices])
        elif isinstance(indices, slice):
            indices = np.arange(*indices.indices(self._n_csets))
            indices.sort()
        elif isinstance(indices, (list, np.ndarray)):
            indices = np.unique(indices)
        else:
            raise TypeError('indices must be an integer or a list of integers')

        nfi = self._nfi
        self.reset()
        coords = np.zeros((len(indices), self.getNumOfSelected(), 3), 
                          self._trajectories[0]._dtype)
        prev = 0
        next = self.nextCoordset
        for i, index in enumerate(indices):
            diff = index - prev
            if diff > 1:
                self.skip(diff)
            coords[i] = next()
            prev = index
        self.goto(nfi)
        return coords
        
    getCoordsets.__doc__ = TrajectoryBase.getCoordsets.__doc__
    
    def next(self):
        nfi = self._nfi
        if not self._closed and nfi < self._n_csets:
            traj = self._trajectory
            while traj._nfi == traj._n_csets:
                self._nextFile()
                traj = self._trajectory
            unitcell = traj._nextUnitcell()
            if self._indices is None: 
                coords = traj._nextCoordset()
            else:
                coords = traj._nextCoordset()[self._indices]
            
            frame = Frame(self, nfi, coords, unitcell)
            self._nfi += 1
            return frame

    next.__doc__ = TrajectoryBase.next.__doc__
    
    def nextCoordset(self):
        """Return next coordinate set."""
        
        if not self._closed and self._nfi < self._n_csets:
            traj = self._trajectory
            while traj._nfi == traj._n_csets:
                self._nextFile()
                traj = self._trajectory
            self._nfi += 1
            if self._indices is None: 
                return traj.nextCoordset()
            else:
                return traj.nextCoordset()[self._indices]

    nextCoordset.__doc__ = TrajectoryBase.nextCoordset.__doc__
    
    def goto(self, n):
        
        if self._closed:
            return None
        if not isinstance(n, (int, long)):
            raise ValueError('n must be an integer')
        n_csets = self._n_csets
        if n == 0:
            self.reset()
        else:
            if n < 0:
                n = n_csets + n
            if n < 0:
                n = 0
            elif n > n_csets: 
                n = n_csets
            nfi = n
            for which, traj in enumerate(self._trajectories):
                if traj._n_csets >= nfi:
                    break
                else:
                    nfi -= traj._n_csets
            self._gotoFile(which)
            # print nfi
            self._trajectory.goto(nfi)
            self._nfi = n
    
    goto.__doc__ = TrajectoryBase.goto.__doc__
    
    def skip(self, n):
        
        if not isinstance(n, (int, long)):
            raise ValueError('n must be an integer')
        left = self._n_csets - self._nfi
        if n > left:
            n = left
        while not self._closed and self._nfi < self._n_csets and n > 0:
            traj = self._trajectory
            skip = min(n, traj.getNumOfFrames() - traj.getNextFrameIndex())
            traj.skip(skip)
            if n > skip:
                self._nextFile()
            self._nfi += skip
            n -= skip
            
    skip.__doc__ = TrajectoryBase.skip.__doc__
    
    def reset(self):

        if not self._closed and self._trajectories:
            for traj in self._trajectories:
                traj.reset()
            self._trajectory = self._trajectories[0]
            self._cfi = 0
            self._nfi = 0

    reset.__doc__ = TrajectoryBase.reset.__doc__

    def close(self):
        
        for traj in self._trajectories:
            traj.close()
        self._closed = True

    close.__doc__ = TrajectoryBase.close.__doc__
    
    def hasUnitcell(self):
        
        return np.all([traj.hasUnitcell() for traj in self._trajectories])
    
    hasUnitcell.__doc__ = TrajectoryBase.hasUnitcell.__doc__
    
    def getTimestep(self):
        """Return a list timestep sizes, one from each file."""
        
        return [traj.getTimestep() for traj in self._trajectories]
    
    def getFirstTimestep(self):
        """Return a list first timestep values, one from each file."""
        
        return [traj.getFirstTimestep() for traj in self._trajectories]
    
    def getFrameFreq(self):
        """Return a list timesteps between frames, one from each file."""
        
        return [traj.getFrameFreq() for traj in self._trajectories]
    
    def getNumOfFixed(self):
        """Return a list of fixed atom numbers, one from each file."""
        
        return [traj.getNumOfFixed() for traj in self._trajectories]
    
def parseDCD(filename, start=None, stop=None, step=None):
    """Parse CHARMM format DCD files (also NAMD 2.1 and later).
    
    .. versionadded:: 0.7.2
    
    .. versionchanged:: 0.8
       Returns an :class:`Ensemble` instance. Conformations in the ensemble
       will be ordered as they appear in the trajectory file. 
       *indices* argument is removed. Use :class:`DCDFile` class for parsing 
       coordinates of a subset of atoms.
    
    :arg filename: DCD filename
    :type filename: str
    
    :arg start: index of first frame to read
    :type start: int
        
    :arg stop: index of the frame that stops reading
    :type stop: int
        
    :arg step: steps between reading frames, default is 1 meaning every frame
    :type step: int
    
    """
    
    dcd = DCDFile(filename)
    time_ = time()
    n_frames = dcd.getNumOfFrames()
    LOGGER.info('DCD file contains {0:d} coordinate sets for {1:d} atoms.'
                .format(n_frames, dcd.getNumOfAtoms()))
    ensemble = dcd[slice(start,stop,step)]    
    dcd.close()
    time_ = time() - time_
    dcd_size = 1.0 * dcd.getNumOfFrames() * dcd._bytes_per_frame / (1024*1024)
    LOGGER.info('DCD file was parsed in {0:.2f} seconds.'.format(time_))
    LOGGER.info('{0:.2f} MB parsed at input rate {1:.2f} MB/s.'
                .format(dcd_size, dcd_size/time_))
    LOGGER.info('{0:d} coordinate sets parsed at input rate {1:d} frame/s.'
                .format(n_frames, int(n_frames/time_)))
    return ensemble



def writeDCD(filename, trajectory, start=None, stop=None, step=None, 
             align=False):
    """Write 32-bit CHARMM format DCD file (also NAMD 2.1 and later).
    *trajectory can be an :class:`Trajectory`, :class:`DCDFile`, or 
    :class:`Ensemble` instance. *filename* is returned upon successful
    output of file.
    
    .. versionadded:: 0.8"""
    
    if not isinstance(trajectory, EnsembleBase):
        raise TypeError('{0:s} is not a valid type for trajectory'
                        .format(type(trajectory)))
    
    irange = range(*slice(start, stop, step).indices(len(trajectory)))
    n_csets = len(irange)
    if n_csets == 0:
        raise ValueError('trajectory does not have any coordinate sets, or '
                         'no coordinate sets are selected')
    n_atoms = trajectory.getNumOfSelected()
    if n_atoms == 0:
        raise ValueError('no atoms are selected in the trajectory')
    if isinstance(trajectory, TrajectoryBase):
        isTrajectory = True
        unitcell = trajectory.hasUnitcell()
        nfi = trajectory.getNextFrameIndex() 
        trajectory.reset()
        pack_i_48 = pack('i', 48)
        if isinstance(trajectory, Trajectory):
            timestep = trajectory.getTimestep()[0]
            first_ts = trajectory.getFirstTimestep()[0]
            framefreq = trajectory.getFrameFreq()[0]
            n_fixed = trajectory.getNumOfFixed()[0]
        else:
            timestep = trajectory.getTimestep()
            first_ts = trajectory.getFirstTimestep()
            framefreq = trajectory.getFrameFreq()
            n_fixed = trajectory.getNumOfFixed()
    else:
        isTrajectory = False
        unitcell = False
        frame = trajectory[0]
        timestep = 1
        first_ts = 0
        framefreq = 1
        n_fixed = 0
    pack_i_0 = pack('i', 0)
    pack_ix4_0x4 = pack('i'*4, 0, 0, 0, 0)
    pack_i_1 = pack('i', 1)
    pack_i_2 = pack('i', 2)
    pack_i_4 = pack('i', 4)
    pack_i_84 = pack('i', 84)
    pack_i_164 = pack('i', 164)
    pack_i_4N = pack('i', n_atoms * 4)
    time_ = time()
    dcd = open(filename, 'wb')
    dcd.write(pack_i_84)
    dcd.write('CORD')
    dcd.write(pack_i_0) # 0 Number of frames in file, none written yet
    dcd.write(pack('i', first_ts)) # 1 Starting timestep
    dcd.write(pack('i', framefreq)) # 2 Timesteps between frames written to the file
    dcd.write(pack('i', n_csets)) # 3 Number of timesteps in simulation
    dcd.write(pack_i_0) # 4 NAMD writes NSTEP or ISTART - NSAVC here?
    dcd.write(pack_ix4_0x4) # 5, 6, 7, 8
    dcd.write(pack('f', timestep)) # 9 timestep
    dcd.write(pack('i', int(unitcell))) # 10 with unitcell
    dcd.write(pack_ix4_0x4) # 11, 12, 13, 14
    dcd.write(pack_ix4_0x4) # 15, 16, 17, 18
    dcd.write(pack('i', 24)) # 19 Pretend to be CHARMM version 24
    dcd.write(pack_i_84)
    dcd.write(pack_i_164)
    dcd.write(pack_i_2)
    dcd.write('{0:80s}'.format('Created by ProDy'))
    dcd.write('{0:80s}'.format('REMARKS Created ' + 
                        datetime.datetime.now().strftime('%d %B, %Y at %R')))
    dcd.write(pack_i_164)
    
    dcd.write(pack_i_4)
    dcd.write(pack('i', n_atoms))
    dcd.write(pack_i_4)
    
    LOGGER.progress(len(irange))
    prev = -1
    unitcell = pack('d'*6, *(0,0,0,0,0,0))
    for j, i in enumerate(irange):
        diff = i - prev
        if diff > 1:
            trajectory.skip(diff-1)
        prev = i
        if isTrajectory:
            frame = trajectory.next()
            if frame is None:
                break
            if unitcell:
                uc = frame._getUnitcell()
                uc[3:] = np.sin((PISQUARE/90) * (90-uc[3:]))
                uc = uc[[0,3,1,4,5,2]]
                dcd.write(pack_i_48)
                uc.tofile(dcd)
                dcd.write(pack_i_48)
        else:
            frame._index = i
        if align:
            frame.superpose()
        coords = frame._getCoordinates().T
        dcd.write(pack_i_4N)
        coords[0].tofile(dcd)
        dcd.write(pack_i_4N)
        dcd.write(pack_i_4N)
        coords[1].tofile(dcd)
        dcd.write(pack_i_4N)
        dcd.write(pack_i_4N)
        coords[2].tofile(dcd)
        dcd.write(pack_i_4N)
        dcd.seek(8)
        dcd.write(pack('i', j+1))
        dcd.seek(0, 2)
        LOGGER.report(i)
    j += 1
    LOGGER.clear()
    dcd.close()
    time_ = time() - time_
    dcd_size = 1.0 * (56 + (n_atoms * 3 + 6) * 4 ) * n_csets / (1024*1024)
    LOGGER.info('DCD file was written in {0:.2f} seconds.'.format(time_))
    LOGGER.info('{0:.2f} MB written at input rate {1:.2f} MB/s.'
                .format(dcd_size, dcd_size/time_))
    LOGGER.info('{0:d} coordinate sets written at output rate {1:d} frame/s.'
                .format(n_csets, int(n_csets/time_)))
    if j != n_csets:
        LOGGER.warning('Warning: {0:d} frames expected, {1:d} written.'
                       .format(n_csets, j))
    if isTrajectory:
        trajectory.goto(nfi)
    return filename
        
  
if __name__ == '__main__':
    import prody
    dcd = DCDFile('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd')
    writeDCD('/home/abakan/dene.dcd', dcd)
    print dcd.getTitle()
    print dcd.getFrame(852).getUnitcell()
    new = DCDFile('/home/abakan/dene.dcd')
    print new.getTitle()
    print new.getFrame(852).getUnitcell()
    stop
    ens = parseDCD('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd')
    ag = prody.parsePDB('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi.pdb')
    ens.setAtomGroup( ag )
    ens.select('calpha')
    ens.superpose()
    stop
    ag.setTrajectory('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd')
    dcd = prody.DCDFile('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd')
    dcd.setAtomGroup( ag )
    dcd.select( 'calpha' )
    pca = prody.PCA()
    pca.buildCovariance(dcd)
    #traj = Trajectory('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/eq1.dcd')
    #traj.addFile('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd')
    #traj.setAtomGroup( ag )
    #dcd = parseDCD('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/eq1.dcd')
    #dcd = parseDCD('/home/abakan/research/bcianalogs/mdsim/nMbciR/mkp3bcirwi_sim/sim.dcd', indices=np.arange(1000), stride=10)
    #dcd = parseDCD('/home/abakan/research/mkps/dynamics/mkp3/MKP3.dcd', indices=np.arange(1000), stride=10)
    
    
    
