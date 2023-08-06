#!/usr/bin/env python

'''
This module define the various drones used to assimilate data.
'''

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Mar 18, 2012"

import abc
import os
import re
import glob
import logging

from pymatgen.io.vaspio import Vasprun
from pymatgen.entries.computed_entries import ComputedEntry, ComputedStructureEntry

logger = logging.getLogger(__name__)

class AbstractDrone(object):
    """
    Abstract drone class that defines the various methods that must be implemented
    by drones. Because of the quirky nature of Python's multiprocessing, the 
    representations has to be in the form of python primitives. This can then
    be reverted to the original object with drone.get_object.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def assimilate(self, path):
        '''
        Assimilate data in a directory path into a dict representation of
        a pymatgen object.
        
        Args:
            path:
                directory path
                
        Returns:
            Dict representation of an assimilated object
        '''
        return

    @abc.abstractmethod
    def is_valid_path(self, path):
        """
        Checks if path contains valid data for assimilation. For example, if you
        are assimilating VASP runs, you are only interested in directories containing
        vasprun.xml files.
        
        Args:
            path:
                directory path as a tuple generated from os.walk
                
        Returns:
            True if directory contains valid data, False otherwise.
        """
        return

    @abc.abstractmethod
    def convert(self, d):
        """
        Convert a dict generated from assimilate into an actual pymatgen object.
        """

    @abc.abstractproperty
    def to_dict(self):
        """
        All drones must support a json serializable dict representation
        """
        return


class VaspToComputedEntryDrone(AbstractDrone):
    """
    VaspToEntryDrone assimilates directories containing vasp input to 
    ComputedEntry/ComputedStructureEntry objects. There are some restrictions
    on the valid directory structures:
    
    1. There can be only one vasp run in each directory.
    2. Directories designated "relax1", "relax2" are considered to be 2 parts of
       an aflow style run, and only "relax2" is parsed.
       
    """

    def __init__(self, inc_structure = False, parameters = None, data = None):
        """
        Args:
            inc_structure:
                Set to True if you want ComputedStructureEntries to be returned
                instead of ComputedEntries.
            parameters:
                Input parameters to include. It has to be one of the properties
                supported by the Vasprun object. See pymatgen.io.vaspio Vasprun.
                The parameters have to be one of python's primitive types,
                i.e. list, dict of strings and integers. Complex objects such as
                dos are not supported at this point.
            data:
                Output data to include. Has to be one of the properties supported
                by the Vasprun object. The parameters have to be one of python's 
                primitive types, i.e. list, dict of strings and integers. Complex 
                objects such as dos are not supported at this point.
        """
        self._inc_structure = inc_structure
        self._parameters = parameters if parameters else []
        self._data = data if data else []

    def assimilate(self, path):
        files = os.listdir(path)
        if 'relax1' in files and 'relax2' in files:
            filepath = glob.glob(os.path.join(path, "relax2", "vasprun.xml*"))[0]
        else:
            vasprun_files = glob.glob(os.path.join(path, "vasprun.xml*"))
            filepath = None
            if len(vasprun_files) == 1:
                filepath = vasprun_files[0]
            elif len(vasprun_files) > 1:
                """
                This is a bit confusing, since there maybe be multi-steps. By 
                default, assimilate will try to find a file simply named 
                vasprun.xml, vasprun.xml.bz2, or vasprun.xml.gz.  Failing which
                it will try to get a relax2 from an aflow style run if possible.
                Or else, a randomly chosen file containing vasprun.xml is chosen.
                """
                for fname in vasprun_files:
                    if os.path.basename(fname) in ["vasprun.xml", "vasprun.xml.gz", "vasprun.xml.bz2"]:
                        filepath = fname
                        break
                    if re.search("relax2", fname):
                        filepath = fname
                        break
                    filepath = fname

        try:
            vasprun = Vasprun(filepath)
        except Exception as ex:
            logger.debug("error in {}: {}".format(filepath, ex))
            return None
        param = {}
        for p in self._parameters:
            param[p] = getattr(vasprun, p)
        data = {}
        for d in self._data:
            data[d] = getattr(vasprun, d)
        if self._inc_structure:
            entry = ComputedStructureEntry(vasprun.final_structure,
                                   vasprun.final_energy, parameters = param, data = data)
        else:
            entry = ComputedEntry(vasprun.final_structure.composition,
                                   vasprun.final_energy, parameters = param, data = data)
        return entry.to_dict

    def is_valid_path(self, path):
        (parent, subdirs, files) = path
        if 'relax1' in subdirs and 'relax2' in subdirs:
            return True
        if (not parent.endswith('/relax1')) and (not parent.endswith('/relax2')) and len(glob.glob(os.path.join(parent, "vasprun.xml*"))) > 0:
            return True
        return False

    def convert(self, d):
        if 'structure' in d:
            return ComputedStructureEntry.from_dict(d)
        else:
            return ComputedEntry.from_dict(d)

    def __str__(self):
        return "VaspToEntryDrone"

    @property
    def to_dict(self):
        init_args = {'inc_structure' : self._inc_structure,
                     "parameters": self._parameters,
                     "data": self._data}
        output = {'name' : self.__class__.__name__, 'init_args': init_args, 'version': __version__ }
        return output

def drone_from_dict(d):
    """
    A helper function that returns a drone from a dict representation.
    
    Arguments:
        d:
            A dict representation of a drone with init args.
    
    Returns:
        A properly initialized Drone object
    """
    mod = __import__('pymatgen.borg.hive', globals(), locals(), [d['name']], -1)
    if hasattr(mod, d['name']):
        drone = getattr(mod, d['name'])
        return drone(**d['init_args'])
    raise ValueError("Invalid Drone Dict")
