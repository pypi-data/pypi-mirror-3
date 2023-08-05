#!/usr/bin/env python

"""
This module defines PDEntry, which wraps information (composition and energy) necessary to create
phase diagrams. 
"""

from __future__ import division

__author__="Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__date__ ="$Sep 23, 2011M$"

import re

from pymatgen.core.structure import Composition
from pymatgen.core.periodic_table import Element

class PDEntry (object):
    """
    An object encompassing all relevant data for phase
    diagrams.
    Author: Shyue
    """
    def __init__(self, comp, finalenergy, name = None):
        self._finalenergy = float(finalenergy)
        self._composition = comp
        if name == None:
            self._name = comp.reduced_formula
        else:
            self._name = name

    @property
    def energy(self):
        """
        Returns the final energy.
        """
        return self._finalenergy

    @property
    def energy_per_atom(self):
        """
        Returns the final energy per atom.
        """
        return self.energy/self.composition.num_atoms
    
    @property
    def name(self):
        """
        Returns the name for an entry.
        """
        return self._name

    @property
    def composition(self):
        """
        Returns the composition, which is an dict of element-number.
        """
        return self._composition

    @property
    def is_element(self):
        """
        True if the entry is an element.
        """
        return self._composition.is_element
    
    def __repr__(self):
        return "PDEntry with composition %s, energy = %.4f" % (self.composition.__str__(), self.energy)
    
    def __str__(self):
        return "PDEntry : " + self.composition.__str__()


class GrandPotPDEntry (PDEntry):
    """
    A grand potential pd entry object encompassing all relevant data for phase
    diagrams.  Chemical potentials are given as a element-chemical potential dict.
    Author: Shyue
    """
    def __init__(self, entry, chempots, name=None):
        comp = entry.composition
        self._original_entry = entry
        self._original_comp = comp
        grandpot = entry.energy - sum([comp[el] * pot for el, pot in chempots.items()])
        self.chempots = chempots
        new_comp_map = dict()
        for el in comp.elements:
            if el not in chempots:
                new_comp_map[el] = comp[el]
        newcomposition = Composition(new_comp_map)
        super(GrandPotPDEntry,self).__init__(newcomposition,grandpot,entry.name)

    @property
    def original_entry(self):
        return self._original_entry

    @property
    def name(self):
        """
        Returns the name for an entry.
        """
        return self._original_comp.reduced_formula

    @property
    def is_element(self):
        """
        True if the entry is an element.
        """
        return self._original_comp.is_element

    def __repr__(self):
        return "GrandPotPDEntry with original composition %s, energy = %.4f, %s" % (str(self.original_entry.composition), self.original_entry.energy, ' '.join(["mu_%s = %.4f" % (el,mu) for el,mu in self.chempots.items()]))

    def __str__(self):
        return "GrandPotPDEntry with original composition " + str(self.original_entry.composition) + " and " + ' '.join(["mu_%s = %.4f" % (el,mu) for el,mu in self.chempots.items()])

class PDEntryIO(object):
    """
    Utility class to export and import PDEntry to and from csv files, as well as to and from json.
    """

    @staticmethod
    def to_csv(filename, entries, latexify_names = False):
        import csv
        elements = set()
        map(elements.update, [entry.composition.elements for entry in entries])
        elements = sorted(list(elements), key=lambda a: a.X)
        writer = csv.writer(open(filename, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Name']+elements+['Energy'])
        for entry in entries:
            row = [entry.name if not latexify_names else re.sub(r"([0-9]+)", r"_{\1}", entry.name)]
            row.extend([entry.composition[el] for el in elements])
            row.append(entry.energy)
            writer.writerow(row)

    @staticmethod
    def from_csv(filename):
        import csv
        reader = csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        entries = list()
        header_read = False
        for row in reader:
            if not header_read:
                elements = row[1:(len(row)-1)]
                header_read = True
            else:
                name = row[0]
                finalenergy = float(row[-1])
                comp = dict()
                for ind in range(1,len(row)-1):
                    if float(row[ind]) >0:
                        comp[Element(elements[ind-1])] = float(row[ind])
                entries.append(PDEntry(Composition(comp),finalenergy,name))
        elements = [Element(el) for el in elements]
        return (elements,entries)
    
    @staticmethod
    def to_json(python_object):
        if isinstance(python_object, PDEntry):
            jsonentry = dict()
            jsonentry['name'] = python_object.name
            jsonentry['energy'] = python_object.energy
            jsonentry['formulasum'] = python_object.composition.formula
            return {'__class__': 'PDEntry',
                    '__value__': jsonentry}
        raise TypeError(repr(python_object) + ' is not JSON serializable')
    
    @staticmethod    
    def from_json(json_object):
        if '__class__' in json_object:
            if json_object['__class__'] == 'PDEntry':
                entrydef = json_object['__value__']
                name = entrydef['name']
                energy = entrydef['energy']
                comp = Composition.from_formula(entrydef['formulasum'])
                return PDEntry(comp,energy,name)
        return json_object

