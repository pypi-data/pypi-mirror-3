#!/usr/bin/env python

'''
Created on Jul 22, 2012
'''

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "0.1"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__date__ = "Jul 22, 2012"

import unittest
import os

from nose.exc import SkipTest

from pymatgen.command_line.enumlib_caller import EnumlibAdaptor
from pymatgen import __file__, Element, Structure
from pymatgen.io.cifio import CifParser
from pymatgen.transformations.standard_transformations import SubstitutionTransformation
from pymatgen.util.io_utils import which


if which('multienum.x') and which('makestr.x'):
    enumlib_present = True
else:
    enumlib_present = False


class EnumlibAdaptorTest(unittest.TestCase):

    def test_init(self):
        if not enumlib_present:
            raise SkipTest("enumlib not present. Skipping...")
        test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'test_files')

        parser = CifParser(os.path.join(test_dir, "LiFePO4.cif"))
        struct = parser.get_structures(False)[0]
        subtrans = SubstitutionTransformation({'Li':{'Li':0.5}})
        adaptor = EnumlibAdaptor(subtrans.apply_transformation(struct), 1, 2)
        adaptor.run()
        structures = adaptor.structures
        self.assertEqual(len(structures), 46)
        for s in structures:
            self.assertAlmostEqual(s.composition.get_atomic_fraction(Element("Li")), 0.5 / 6.5)

        subtrans = SubstitutionTransformation({'Li':{'Li':0.25}})
        adaptor = EnumlibAdaptor(subtrans.apply_transformation(struct), 1, 1)
        adaptor.run()
        structures = adaptor.structures
        self.assertEqual(len(structures), 1)
        for s in structures:
            self.assertAlmostEqual(s.composition.get_atomic_fraction(Element("Li")), 0.25 / 6.25)

        #Make sure it works for completely disordered structures.
        struct = Structure([[10, 0, 0], [0, 10, 0], [0, 0, 10]], [{'Fe':0.5}],
                           [[0, 0, 0]])
        adaptor = EnumlibAdaptor(struct, 1, 2)
        adaptor.run()
        self.assertEqual(len(adaptor.structures), 3)


if __name__ == '__main__':
    unittest.main()

