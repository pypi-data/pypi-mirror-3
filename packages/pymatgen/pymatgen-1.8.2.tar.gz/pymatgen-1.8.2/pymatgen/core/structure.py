#!/usr/bin/env python

"""
This module provides classes used to define a structure, such as Site,
PeriodicSite, Structure, and Composition.
"""

from __future__ import division

__author__ = "Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "2.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__date__ = "Sep 23, 2011"

import re
import abc
import math
import collections
import itertools
from fractions import gcd

import numpy as np
from pymatgen.core.lattice import Lattice
from pymatgen.core.periodic_table import Element, Specie, smart_element_or_specie
from pymatgen.util.string_utils import formula_double_format


class Site(collections.Mapping, collections.Hashable):
    '''
    A generalized *non-periodic* site. Atoms and occupancies should be a dict
    of element:occupancy or an element, in which case the occupancy default to 
    1. Coords are given in standard cartesian coordinates.
    '''

    supported_properties = ('magmom', 'charge')

    def __init__(self, atoms_n_occu, coords, properties=None):
        """
        Create a *non-periodic* site.
        
        Args:
            atoms_n_occu: 
                dict of elements or species and occupancies. Elements can be 
                specified as symbols (Fe), atomic numbers (27), or actual 
                Element objects.  Specie can be specified as Specie objects, 
                or strings (Fe2+).
            coords: 
                Cartesian coordinates of site.
            properties:
                Properties associated with the site as a dict, e.g. 
                {'magmom':5}. Defaults to None.
        """

        if isinstance(atoms_n_occu, dict):
            self._species = {smart_element_or_specie(k): v for k, v in atoms_n_occu.items()}
            totaloccu = sum(self._species.values())
            if totaloccu > 1:
                raise ValueError("Species occupancies sum to more than 1!")
            self._is_ordered = (totaloccu == 1 and len(self._species) == 1)
        else:
            self._species = {smart_element_or_specie(atoms_n_occu):1}
            self._is_ordered = True
        self._coords = coords
        self._properties = properties if properties else {}
        for k in self._properties.keys():
            if k not in Site.supported_properties:
                raise ValueError("{} is not a supported Site property".format(k))

    @property
    def properties(self):
        """
        Returns a view of properties as a dict.
        """
        return {k:v for k, v in self._properties.items()}

    def __getattr__(self, a):
        if a in self._properties:
            return self._properties[a]
        raise AttributeError(a)

    def distance(self, other):
        """
        Get distance between two sites.
        
        Args:
            other:
                Other site.
        """
        return np.linalg.norm(other.coords - self.coords)

    def distance_from_point(self, pt):
        """
        Returns distance between the site and a point in space.
        
        Args:
            pt:
                cartesian coordinates of point.
        """
        return np.linalg.norm(np.array(pt) - np.array(self._coords))

    @property
    def species_string(self):
        """
        String representation of species on the site.
        """
        if self._is_ordered:
            return str(self._species.keys()[0])
        else:
            sorted_species = sorted(self._species.keys())
            return ', '.join(["%s:%.3f" % (str(sp), self._species[sp]) for sp in sorted_species])

    @property
    def species_and_occu(self):
        """
        The species at the site, i.e., a dict of element and occupancy
        """
        return self._species

    @property
    def specie(self):
        """
        .. deprecated:: 1.0
            Use :func:`species_and_occu` instead.
            
        The Specie/Element at the site. Only works for ordered sites. Otherwise 
        an AttributeError is raised. Use this property sparingly.  Robust
        design should make use of the property species_and_occu instead.
        
        Raises:
            AttributeError if Site is not ordered.
        """
        if not self._is_ordered:
            raise AttributeError("specie property only works for ordered sites!")
        return self._species.keys()[0]

    @property
    def coords(self):
        """
        A copy of the cartesian coordinates of the site as a numpy array.
        """
        return np.copy(self._coords)

    @property
    def is_ordered(self):
        """
        True if site is an ordered site, i.e., with a single species with 
        occupancy 1.
        """
        return self._is_ordered

    @property
    def x(self):
        """
        Cartesian x coordinate
        """
        return self._coords[0]

    @property
    def y(self):
        """
        Cartesian y coordinate
        """
        return self._coords[1]

    @property
    def z(self):
        """
        Cartesian z coordinate
        """
        return self._coords[2]

    def __getitem__(self, el):
        '''
        Get the occupancy for element
        '''
        return self._species[el]

    def __eq__(self, other):
        """
        Site is equal to another site if the species and occupancies are the 
        same, and the coordinates are the same to some tolerance.  numpy
        function `allclose` is used to determine if coordinates are close.
        """
        if other == None:
            return False
        return self._species == other._species and np.allclose(self._coords, other._coords)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        '''
        Minimally effective hash function that just distinguishes between Sites 
        with different elements.
        '''
        hashcode = 0
        for el in self._species.keys():
            #Ignore elements with zero amounts.
            if self[el] != 0:
                hashcode += el.Z
        return hashcode

    def __contains__(self, el):
        return el in self._species

    def __len__(self):
        return len(self._species)

    def __iter__(self):
        return self._species.__iter__()

    def __repr__(self):
        outs = []
        outs.append("Non-periodic Site")
        outs.append("xyz        : (%0.4f, %0.4f, %0.4f)" % tuple(self.coords))
        for k, v in self._species.items():
            outs.append("element    : %s" % k.symbol)
            outs.append("occupation : %0.2f" % v)
        return "\n".join(outs)

    def __cmp__(self, other):
        '''
        Sets a default sort order for atomic species by electronegativity. Very
        useful for getting correct formulas.  For example, FeO4PLi is 
        automatically sorted in LiFePO4.
        '''
        def avg_electroneg(sps):
            return sum([sp.X * occu for sp, occu in sps.items()])

        if avg_electroneg(self._species) < avg_electroneg(other._species):
            return -1
        if avg_electroneg(self._species) > avg_electroneg(other._species):
            return 1
        return 0

    def __str__(self):
        return "%s %s" % (self._coords, ','.join(["%s %.4f" % (str(atom), occu) for atom, occu in self._species.items()]))

    @property
    def to_dict(self):
        """
        Json-serializable dict representation for Site.
        """
        species_list = []
        for spec, occu in self._species.items():
            if isinstance(spec, Element):
                species_list.append({'element': spec.symbol, 'occu': occu})
            elif isinstance(spec, Specie):
                d = spec.to_dict
                d['occu'] = occu
                species_list.append(d)
                species_list.append({'element': spec.symbol, 'occu': occu, 'oxidation_state': spec.oxi_state})
        return {'name': self.species_string, 'species': species_list, 'occu': occu, 'xyz':[float(c) for c in self._coords], 'properties': self._properties}

    @staticmethod
    def from_dict(d):
        """
        Create Site from dict representation
        """
        atoms_n_occu = {}
        for sp_occu in d['species']:
            sp = Specie.from_dict(sp_occu) if 'oxidation_state' in sp_occu else Element(sp_occu['element'])
            atoms_n_occu[sp] = sp_occu['occu']
        props = d.get('properties', None)
        return Site(atoms_n_occu, d['xyz'], properties=props)


class PeriodicSite(Site):
    """
    Extension of generic Site object to periodic systems.
    PeriodicSite includes a lattice system.
    """

    def __init__(self, atoms_n_occu, coords, lattice, to_unit_cell=False,
                 coords_are_cartesian=False, properties=None):
        """
        Create a periodic site.
        
        Args:
            atoms_n_occu:
                dict of elements and occupancies
            coords:
                coordinates of site as fractional coordinates or cartesian 
                coordinates.
            lattice:
                Lattice associated with the site
            to_unit_cell:
                translates fractional coordinate to the basic unit cell, i.e. 
                all fractional coordinates satisfy 0 <= a < 1. Defaults to 
                False.
            coords_are_cartesian:
                Set to True if you are providing cartesian coordinates. 
                Defaults to False.
            properties:
                Properties associated with the PeriodicSite as a dict, e.g. 
                {'magmom':5}. Defaults to None.
        """
        self._lattice = lattice
        self._fcoords = self._lattice.get_fractional_coords(coords) if coords_are_cartesian else coords

        if to_unit_cell:
            for i in range(len(self._fcoords)):
                self._fcoords[i] = self._fcoords[i] - math.floor(self._fcoords[i])

        c_coords = self._lattice.get_cartesian_coords(self._fcoords)
        Site.__init__(self, atoms_n_occu, c_coords, properties)

    @property
    def lattice(self):
        """
        The lattice associated with the site.
        """
        return self._lattice

    @property
    def frac_coords(self):
        """
        The fractional coordinates of the site as a tuple.
        """
        return np.copy(self._fcoords)

    @property
    def a(self):
        """
        Fractional a coordinate
        """
        return self._fcoords[0]

    @property
    def b(self):
        """
        Fractional b coordinate
        """
        return self._fcoords[1]

    @property
    def c(self):
        """
        Fractional c coordinate
        """
        return self._fcoords[2]

    @property
    def to_unit_cell(self):
        """
        Copy of PeriodicSite translated to the unit cell.
        """
        fcoords = [i - math.floor(i) for i in self._fcoords]
        return PeriodicSite(self._species, fcoords, self._lattice)

    def is_periodic_image(self, other, tolerance=1e-8):
        """
        Returns True if sites are periodic images of each other.
        """
        if self.lattice != other.lattice:
            return False
        frac_diff = abs(self._fcoords - other._fcoords) % 1
        frac_diff = [abs(a) < tolerance or abs(a) > 1 - tolerance for a in frac_diff]
        return  all(frac_diff)

    def __eq__(self, other):
        return self._species == other._species and self._lattice == other._lattice and np.allclose(self._coords, other._coords)

    def __ne__(self, other):
        return not self.__eq__(other)

    def distance_and_image_old(self, other, jimage=None):
        """
        .. deprecated:: 1.0
            Use :func:`distance_and_image` instead. This code is kept for 
            information reasons. A new version has been written which is more 
            accurate, but at a higher computational cost.
        
        Gets distance between two sites assuming periodic boundary conditions.
        If the index jimage of two sites atom j is not specified it selects the 
        j image nearest to the i atom and returns the distance and jimage
        indices in terms of lattice vector translations. If the index jimage of
        atom j is specified it returns the distance between the i atom and the
        specified jimage atom, the given jimage is also returned.
        
        Args:
            other:
                other site to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one 
                a-lattice vector away. If jimage == None, the image that is 
                nearest to the site is found.
        
        Returns:
            (distance, jimage):
                distance and periodic lattice translations of the other site 
                for which the distance applies.
        
        .. note::
            Assumes the primitive cell vectors are sufficiently not skewed such 
            that the condition \|a\|cos(ab_angle) < \|b\| for all possible cell
            vector pairs. ** this method does not check this condition **
        """
        if jimage == None:
            #Old algorithm
            jimage = -np.array(np.around(other._fcoords - self._fcoords), int)
        return np.linalg.norm(self.lattice.get_cartesian_coords(jimage + other._fcoords - self._fcoords)), jimage

    def distance_and_image_from_frac_coords(self, fcoords, jimage=None):
        """
        Gets distance between site and a fractional coordinate assuming 
        periodic boundary conditions. If the index jimage of two sites atom j 
        is not specified it selects the j image nearest to the i atom and
        returns the distance and jimage indices in terms of lattice vector 
        translations. If the index jimage of atom j is specified it returns the
        distance between the i atom and the specified jimage atom, the given 
        jimage is also returned.
        
        Args:
            fcoords:
                fcoords to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one 
                a-lattice vector away. If jimage == None, the image that is
                nearest to the site is found.
        
        Returns:
            (distance, jimage):
                distance and periodic lattice translations of the other site
                for which the distance applies.
        """
        if jimage == None:
            adj1 = np.array([-math.floor(i) for i in self._fcoords])
            adj2 = np.array([-math.floor(i) for i in fcoords])
            mindist = float('inf')
            coord1 = self._fcoords + adj1
            coord2 = fcoords + adj2
            test_set = [[-1, 0] if coord1[i] < coord2[i] else [0, 1] for i in range(3)]
            for image in itertools.product(*test_set):
                dist = np.linalg.norm(self._lattice.get_cartesian_coords(coord2 + image - coord1))
                if dist < mindist:
                    mindist = dist
                    jimage = adj2 - adj1 + image
            return mindist, jimage
        return np.linalg.norm(self.lattice.get_cartesian_coords(jimage + fcoords - self._fcoords)), jimage

    def distance_and_image(self, other, jimage=None):
        """
        Gets distance and instance between two sites assuming periodic boundary 
        conditions. If the index jimage of two sites atom j is not specified it
        selects the j image nearest to the i atom and returns the distance and 
        jimage indices in terms of lattice vector translations. If the index
        jimage of atom j is specified it returns the distance between the ith
        atom and the specified jimage atom, the given jimage is also returned.
        
        Args:
            other:
                other site to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one 
                a-lattice vector away. If jimage == None, the image that is 
                nearest to the site is found.
        
        Returns:
            (distance, jimage):
                distance and periodic lattice translations of the other site 
                for which the distance applies.
        """
        return self.distance_and_image_from_frac_coords(other._fcoords, jimage)

    def distance(self, other, jimage=None):
        """
        Get distance between two sites assuming periodic boundary conditions.
        
        Args:
            other:
                other site to get distance from.
            jimage:   
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one a-lattice vector away.
                if jimage == None, the image that is nearest to the site is found.
        
        Returns:
            distance:
                distance between the two sites
        
        """
        return self.distance_and_image(other, jimage)[0]

    def __repr__(self):
        outs = []
        outs.append("Periodic Site")
        outs.append("abc : (%0.4f, %0.4f, %0.4f)" % tuple(self._fcoords))
        for k, v in self._species.items():
            outs.append("element    : %s" % k.symbol)
            outs.append("occupation : %0.2f" % v)
        return "\n".join(outs)

    @property
    def to_dict(self):
        """
        Json-serializable dict representation of PeriodicSite.
        """
        species_list = []
        for spec, occu in self._species.items():
            if isinstance(spec, Element):
                species_list.append({'element': spec.symbol, 'occu': occu})
            else:
                d = spec.to_dict
                d['occu'] = occu
                species_list.append(d)
        return {'label': self.species_string, 'species': species_list,
                'occu': occu, 'xyz':[float(c) for c in self._coords],
                'abc':[float(c) for c in self._fcoords],
                'lattice': self._lattice.to_dict,
                'properties': self._properties}

    @staticmethod
    def from_dict(d, lattice=None):
        """
        Create PeriodicSite from dict representation.
        
        Args:
            d:
                dict representation of PeriodicSite
            lattice:
                Optional lattice to override lattice specified in d. Useful for
                ensuring all sites in a structure share the same lattice.
        """
        atoms_n_occu = {}
        for sp_occu in d['species']:
            sp = Specie.from_dict(sp_occu) if 'oxidation_state' in sp_occu else Element(sp_occu['element'])
            atoms_n_occu[sp] = sp_occu['occu']
        props = d.get('properties', None)
        lattice = lattice if lattice else Lattice.from_dict(d['lattice'])
        return PeriodicSite(atoms_n_occu, d['abc'], lattice, properties=props)


class SiteCollection(collections.Sequence, collections.Hashable):
    __metaclass__ = abc.ABCMeta

    """
    Basic SiteCollection. Essentially a sequence of Sites or PeriodicSites.
    This serves as a base class for Molecule (a collection of Site, i.e., no
    periodicity) and Structure (a collection of PeriodicSites, i.e., 
    periodicity). Not meant to be instantiated directly.
    """

    DISTANCE_TOLERANCE = 0.01

    @abc.abstractproperty
    def sites(self):
        """
        Returns an iterator for the sites in the Structure. 
        """
        for site in self._sites:
            yield site

    @abc.abstractmethod
    def get_distance(self, i, j):
        """
        Returns distance between sites at index i and j.
        """
        return

    @property
    def distance_matrix(self):
        """
        Returns the distance matrix between all sites in the structure. For
        periodic structures, this should return the nearest image distance.
        """
        nsites = self.num_sites
        distmatrix = np.zeros((nsites, nsites))
        for i, j in itertools.combinations(xrange(nsites), 2):
            dist = self.get_distance(i, j)
            distmatrix[i, j] = dist
            distmatrix[j, i] = dist
        return distmatrix

    @property
    def species(self):
        """
        List of species at each site of the structure.
        Only works for ordered structures.
        Disordered structures will raise an AttributeError.
        """
        return [site.specie for site in self.sites]

    @property
    def species_and_occu(self):
        """
        List of species and occupancies at each site of the structure.
        """
        return [site.species_and_occu for site in self.sites]

    @property
    def site_properties(self):
        """
        Returns the site properties as a dict of sequences. E.g., 
        {'magmom': (5,-5), 'charge': (-4,4)}.
        """
        props = collections.defaultdict(list)
        for site in self.sites:
            for k, v in site.properties.items():
                props[k].append(v)
        return props

    def __contains__(self, site):
        return site in self.sites

    def __iter__(self):
        return self.sites.__iter__()

    def __getitem__(self, ind):
        return self.sites[ind]

    def __len__(self):
        return len(tuple(self.sites))

    def __hash__(self):
        #for now, just use the composition hash code.
        return self.composition.__hash__()

    @property
    def num_sites(self):
        """
        Number of sites.
        """
        return len(self.sites)

    @property
    def cart_coords(self):
        '''
        Returns a list of the cartesian coordinates of sites in the structure.
        '''
        return [site.coords for site in self.sites]

    @property
    def formula(self):
        """
        Returns the formula.
        """
        return self.composition.formula

    @property
    def composition(self):
        """
        Returns the composition
        """
        elmap = collections.defaultdict(float)
        for site in self.sites:
            for species, occu in site.species_and_occu.items():
                elmap[species] += occu
        return Composition(elmap)

    @property
    def charge(self):
        '''
        Returns the net charge of the structure based on oxidation states. If
        Elements are found, a charge of 0 is assumed.
        '''
        charge = 0
        for site in self.sites:
            for specie, amt in site.species_and_occu.items():
                charge += getattr(specie, 'oxi_state', 0) * amt
        return charge

    @property
    def is_ordered(self):
        """
        Checks if structure is ordered, meaning no partial occupancies in any 
        of the sites. 
        """
        for site in self.sites:
            if not site.is_ordered:
                return False
        return True

    def get_angle(self, i, j, k):
        """
        Returns angle specified by three sites.
         
        Args:
            i:
                Index of first site
            j:
                Index of second site
            k:
                Index of third site
        
        Returns:
            Angle in degrees.
        """
        v1 = self.sites[i].coords - self.sites[j].coords
        v2 = self.sites[k].coords - self.sites[j].coords
        ans = np.dot(v1, v2) / np.linalg.norm(v1) / np.linalg.norm(v2)
        """
        Corrects for stupid numerical error which may result in acos being
        operated on a number with absolute value larger than 1
        """
        if ans > 1:
            ans = 1
        elif ans < -1:
            ans = -1
        return math.acos(ans) * 180 / math.pi

    def get_dihedral(self, i, j, k, l):
        """
        Returns dihedral angle specified by four sites.
         
        Args:
            i:
                Index of first site
            j:
                Index of second site
            k:
                Index of third site
            l:
                Index of fourth site
                
        Returns:
            Dihedral angle in degrees.
        """
        v1 = self.sites[k].coords - self.sites[l].coords
        v2 = self.sites[j].coords - self.sites[k].coords
        v3 = self.sites[i].coords - self.sites[j].coords
        v23 = np.cross(v2, v3)
        v12 = np.cross(v1, v2)
        return math.atan2(np.linalg.norm(v2) * np.dot(v1, v23), np.dot(v12, v23)) * 180 / math.pi


class Structure(SiteCollection):
    """
    Basic Structure object with periodicity. Essentially a sequence of 
    PeriodicSites having a common lattice. Structure is made to be immutable 
    so that they can function as keys in a dict. Modifications should be done 
    by making a new Structure using the structure_modifier module or your own 
    methods. Structure extends Sequence and Hashable, which means that in many 
    cases, it can be used like any Python sequence. Iterating through a 
    structure is equivalent to going through the sites in sequence.
    """

    def __init__(self, lattice, atomicspecies, coords, validate_proximity=False,
                 to_unit_cell=False, coords_are_cartesian=False,
                 site_properties=None):
        """
        Create a periodic structure.
        
        Args:
            lattice:
                pymatgen.core.lattice Lattice object signify the lattice.
            atomicspecies:
                list of atomic species. Possible kinds of input include a list 
                of dict of elements/species and occupancies, a List of 
                elements/specie specified as actual Element/Specie, Strings 
                ("Fe", "Fe2+") or atomic numbers (1,56).
            fractional_coords:
                list of fractional coordinates of each species.
            validate_proximity:
                Whether to check if there are sites that are less than 1 Ang 
                apart. Defaults to False.
            coords_are_cartesian:
                Set to True if you are providing coordinates in cartesian 
                coordinates. Defaults to False.
            site_properties:
                Properties associated with the sites as a dict of sequences, 
                e.g., {'magmom':[5,5,5,5]}. The sequences have to be the same
                length as the atomic species and fractional_coords.
                Defaults to None for no properties.
        """
        if len(atomicspecies) != len(coords):
            raise StructureError("The list of atomic species must be of the same length as the list of fractional coordinates.")

        if isinstance(lattice, Lattice):
            self._lattice = lattice
        else:
            self._lattice = Lattice(lattice)

        self._sites = []
        for i in xrange(len(atomicspecies)):
            prop = None
            if site_properties:
                prop = {k:v[i] for k, v in site_properties.items()}
            self._sites.append(PeriodicSite(atomicspecies[i], coords[i], self._lattice, to_unit_cell, coords_are_cartesian, properties=prop))

        if validate_proximity:
            for (s1, s2) in itertools.combinations(self._sites, 2):
                if s1.distance(s2) < SiteCollection.DISTANCE_TOLERANCE:
                    raise StructureError("Structure contains sites that are less than 0.01 Angstrom apart!")

        self._sites = tuple(self._sites)

    @property
    def sites(self):
        """
        Returns the sites in the Structure. 
        """
        return self._sites

    @property
    def lattice(self):
        """
        Lattice of the structure.
        """
        return self._lattice

    @property
    def density(self):
        '''
        Returns the density in units of g/cc
        '''
        constant = 1.660468
        return self.composition.weight / self.volume * constant

    def __eq__(self, other):
        if other == None:
            return False
        if len(self) != len(other):
            return False
        for site in self:
            if site not in other:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        #for now, just use the composition hash code.
        return self.composition.__hash__()

    @property
    def frac_coords(self):
        '''
        Returns the fractional coordinates.
        '''
        return [site.frac_coords for site in self._sites]

    @property
    def volume(self):
        '''
        Returns the volume of the structure.
        '''
        return self._lattice.volume

    def get_distance(self, i, j, jimage=None):
        """
        Get distance between site i and j assuming periodic boundary conditions.
        If the index jimage of two sites atom j is not specified it selects the 
        j image nearest to the i atom and returns the distance and jimage 
        indices in terms of lattice vector translations if the index jimage of 
        atom j is specified it returns the distance between the i atom and the 
        specified jimage atom.
        
        Args:
            i:
                Index of first site
            j:
                Index of second site
            jimage:
                Number of lattice translations in each lattice direction. 
                Default is None for nearest image.
        
        Returns:
            distance
        """
        return self[i].distance(self[j], jimage)

    def get_sites_in_sphere(self, pt, r):
        '''
        Find all sites within a sphere from the point. This includes sites 
        in other periodic images.
        
        Algorithm: 
        
        1. place sphere of radius r in crystal and determine minimum supercell 
           (parallelpiped) which would contain a sphere of radius r. for this 
           we need the projection of a_1 on a unit vector perpendicular 
           to a_2 & a_3 (i.e. the unit vector in the direction b_1) to determine 
           how many a_1's it will take to contain the sphere. 
           
           Nxmax = r * length_of_b_1 / (2 Pi)
        
        2. keep points falling within r.
        
        Args:
            pt:
                cartesian coordinates of center of sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        '''
        recp_len = self._lattice.reciprocal_lattice.abc
        sr = r + 0.15
        nmax = [sr * l / (2 * math.pi) for l in recp_len]
        pcoords = self._lattice.get_fractional_coords(pt)
        nxmax = int(math.floor(pcoords[0] + nmax[0]))
        nxmin = int(math.floor(pcoords[0] - nmax[0]))
        nymax = int(math.floor(pcoords[1] + nmax[1]))
        nymin = int(math.floor(pcoords[1] - nmax[1]))
        nzmax = int(math.floor(pcoords[2] + nmax[2]))
        nzmin = int(math.floor(pcoords[2] - nmax[2]))
        neighbors = []
        n = len(self._sites)
        site_fcoords = np.array([site.to_unit_cell.frac_coords for site in self._sites])
        pts = [pt] * n
        for image in itertools.product(range(nxmin, nxmax + 1), range(nymin, nymax + 1), range(nzmin, nzmax + 1)):
            submat = [image] * n
            fcoords = site_fcoords + submat
            coords = self._lattice.get_cartesian_coords(fcoords)
            dists = (coords - pts) ** 2
            dists = np.sqrt(dists.sum(axis=1))
            withindists = (dists <= r)
            for i in range(n):
                if withindists[i]:
                    neighbors.append((PeriodicSite(self._sites[i].species_and_occu, fcoords[i], self._lattice, properties=self._sites[i].properties), dists[i]))

        return neighbors

    def get_neighbors(self, site, r):
        """
        Get all neighbors to a site within a sphere of radius r.  Excludes the 
        site itself.
        
        Args:
            site:
                site, which is the center of the sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        """
        return [(s, dist) for (s, dist) in self.get_sites_in_sphere(site.coords, r) if site != s]

    def get_all_neighbors(self, r, include_index=False):
        """
        Get neighbors for each atom in the unit cell, out to a distance r
        Returns a list of list of neighbors for each site in structure.
        Use this method if you are planning on looping over all sites in the
        crystal. If you only want neighbors for a particular site, use the 
        method get_neighbors as it may not have to build such a large supercell
        However if you are looping over all sites in the crystal, this method
        is more efficient since it only performs one pass over a large enough 
        supercell to contain all possible atoms out to a distance r.
        The return type is a [(site, dist) ...] since most of the time,
        subsequent processing requires the distance.
        
        Args:
            r:
                radius of sphere. 
            include_index:
                boolean that determines whether the non-supercell site index
                is included in the returned data
        
        Returns:
            A list of a list of nearest neighbors for each site, i.e.,
            [[(site, dist, index) ...], ..] 
            Index only supplied if include_index = true
            The index is the index of the site in the original (non-supercell)
            structure. This is needed for ewaldmatrix by keeping track of which
            sites contribute to the ewald sum.
        """

        #use same algorithm as getAtomsInSphere to determine supercell but
        #loop over all atoms in crystal
        recp_len = self.lattice.reciprocal_lattice.abc
        sr = r + 0.15
        nmax = [sr * l / (2 * math.pi) for l in recp_len]
        site_nminmax = []
        unit_cell_sites = [site.to_unit_cell for site in self._sites]
        #unit_cell_coords = [site.frac_coords for site in unit_cell_sites]

        for site in self._sites:
            pcoords = site.frac_coords
            inxmax = int(math.floor(pcoords[0] + nmax[0]))
            inxmin = int(math.floor(pcoords[0] - nmax[0]))
            inymax = int(math.floor(pcoords[1] + nmax[1]))
            inymin = int(math.floor(pcoords[1] - nmax[1]))
            inzmax = int(math.floor(pcoords[2] + nmax[2]))
            inzmin = int(math.floor(pcoords[2] - nmax[2]))
            site_nminmax.append(((inxmin, inxmax), (inymin, inymax), (inzmin, inzmax)))

        nxmin = min([i[0][0] for i in site_nminmax])
        nxmax = max([i[0][1] for i in site_nminmax])
        nymin = min([i[1][0] for i in site_nminmax])
        nymax = max([i[1][1] for i in site_nminmax])
        nzmin = min([i[2][0] for i in site_nminmax])
        nzmax = max([i[2][1] for i in site_nminmax])

        neighbors = [list() for i in range(len(self._sites))]

        site_coords = np.array(self.cart_coords)
        n = len(self._sites)
        for image in itertools.product(range(nxmin, nxmax + 1), range(nymin, nymax + 1), range(nzmin, nzmax + 1)):
            for j in range(len(unit_cell_sites)):
            #for site in unit_cell_sites:
                site = unit_cell_sites[j]
                fcoords = site.frac_coords + np.array(image)
                coords = self.lattice.get_cartesian_coords(fcoords)
                submat = [coords] * n
                dists = (site_coords - submat) ** 2
                dists = np.sqrt(dists.sum(axis=1))
                withindists = (dists <= r) * (dists > 1e-8)
                for i in range(n):
                    if include_index & withindists[i]:
                        neighbors[i].append((PeriodicSite(site.species_and_occu, fcoords, site.lattice, properties=site.properties), dists[i], j))
                    elif withindists[i]:
                        neighbors[i].append((PeriodicSite(site.species_and_occu, fcoords, site.lattice, properties=site.properties), dists[i]))
        return neighbors

    def get_neighbors_in_shell(self, origin, r, dr):
        """
        Returns all sites in a shell centered on origin (coords) between radii 
        r-dr and r+dr.
        
        Args:
            origin:
                cartesian coordinates of center of sphere.
            r:
                inner radius of shell.
            dr: 
                width of shell.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        """
        outer = self.get_sites_in_sphere(origin, r + dr)
        inner = r - dr
        return [(site, dist) for (site, dist) in outer if dist > inner]

    def get_sorted_structure(self):
        """
        Get a sorted copy of the structure.
        Sites are sorted by the electronegativity of the species.
        """
        sortedsites = sorted(self.sites)
        return Structure(self._lattice, [site.species_and_occu for site in sortedsites], [site.frac_coords for site in sortedsites])

    def interpolate(self, end_structure, nimages=10):
        '''
        Interpolate between this structure and end_structure. Useful for
        construction of NEB inputs.
        
        Args:
            end_structure:
                structure to interpolate between this structure and end.
            nimages:
                number of interpolation images. Defaults to 10 images.
        
        Returns:
            List of interpolated structures.
        '''
        #Check length of structures
        if len(self) != len(end_structure):
            raise ValueError("You are interpolating structures with different lengths!")

        #Check that both structures have the same lattice
        if not ((abs(self.lattice.matrix - end_structure.lattice.matrix) < 0.01)).all():
            raise ValueError("You are interpolating structures with different lattices!")

        #Check that both structures have the same species
        for i in range(0, len(self)):
            if self[i].species_and_occu != end_structure[i].species_and_occu:
                raise ValueError("You are interpolating different structures!\nStructure 1:\n" + str(self) + "\nStructure 2\n" + str(end_structure))

        start_coords = np.array(self.frac_coords)
        end_coords = np.array(end_structure.frac_coords)

        vec = end_coords - start_coords #+ jimage
        intStructs = [Structure(self.lattice, [site.species_and_occu for site in self._sites], start_coords + float(x) / float(nimages) * vec) for x in range(0, nimages + 1)]
        return intStructs

    def __repr__(self):
        outs = []
        outs.append("Structure Summary")
        outs.append(repr(self.lattice))
        for s in self.sites:
            outs.append(repr(s))
        return "\n".join(outs)

    def __str__(self):
        outs = ["Structure Summary ({s})".format(s=str(self.composition))]
        outs.append("Reduced Formula: " + str(self.composition.reduced_formula))
        to_s = lambda x : "%0.6f" % x
        outs.append('abc   : ' + " ".join([to_s(i).rjust(10) for i in self.lattice.abc]))
        outs.append('angles: ' + " ".join([to_s(i).rjust(10) for i in self.lattice.angles]))
        outs.append("Sites ({i})".format(i=len(self)))
        for i, site in enumerate(self):
            outs.append(" ".join([str(i + 1), site.species_string, " ".join([to_s(j).rjust(12) for j in site.frac_coords])]))
        return "\n".join(outs)

    @property
    def to_dict(self):
        """
        Json-serializable dict representation of Structure
        """
        d = {}
        d['lattice'] = self._lattice.to_dict
        d['sites'] = [site.to_dict for site in self]
        return d

    @staticmethod
    def from_dict(d):
        """
        Reconstitute a Structure object from a dict representation of Structure 
        created using to_dict.
        
        Args:
            d: 
                dict representation of structure.
        
        Returns:
            Structure object
        """
        lattice = Lattice(d['lattice']['matrix'])
        species = []
        coords = []
        props = {}

        for site_dict in d['sites']:
            site = PeriodicSite.from_dict(site_dict, lattice)
            species.append(site.species_and_occu)
            coords.append(site.frac_coords)
            siteprops = site.properties
            for k, v in siteprops.items():
                if k not in props:
                    props[k] = [v]
                else:
                    props[k].append(v)
        return Structure(lattice, species, coords, site_properties=props)


class Molecule(SiteCollection):
    """
    Basic Molecule object without periodicity. Essentially a sequence of sites. 
    Molecule is made to be immutable so that they can function as keys in a 
    dict. Modifications should be done by making a new Molecule.
    Molecule extends Sequence and Hashable, which means that in many cases, 
    it can be used like any Python sequence. Iterating through a molecule is
    equivalent to going through the sites in sequence.
    """
    def __init__(self, atomicspecies, coords, validate_proximity=False,
                 site_properties=None):
        """
        Creates a Molecule.
        
        Args:
            atomicspecies:
                list of atomic species. Possible kinds of input include a list
                of dict of elements/species and occupancies, a List of 
                elements/specie specified as actual Element/Specie, Strings 
                ("Fe", "Fe2+") or atomic numbers (1,56).
            coords:
                list of cartesian coordinates of each species.
            validate_proximity:
                Whether to check if there are sites that are less than 1 Ang 
                apart. Defaults to False.
            site_properties:
                Properties associated with the sites as a dict of sequences, 
                e.g., {'magmom':[5,5,5,5]}. The sequences have to be the same
                length as the atomic species and fractional_coords.
                Defaults to None for no properties.
        """
        if len(atomicspecies) != len(coords):
            raise StructureError("The list of atomic species must be of the same length as the list of fractional coordinates.")

        self._sites = []
        for i in xrange(len(atomicspecies)):
            prop = None
            if site_properties:
                prop = {k:v[i] for k, v in site_properties.items()}
            self._sites.append(Site(atomicspecies[i], coords[i], properties=prop))

        if validate_proximity:
            for (s1, s2) in itertools.combinations(self._sites, 2):
                if s1.distance(s2) < Structure.DISTANCE_TOLERANCE:
                    raise StructureError("Molecule contains sites that are less than 0.01 Angstrom apart!")

        self._sites = tuple(self._sites)

    @property
    def sites(self):
        """
        Returns the sites in the Molecule. 
        """
        return self._sites

    def __repr__(self):
        outs = []
        outs.append("Molecule Summary")
        for s in self.sites:
            outs.append(repr(s))
        return "\n".join(outs)

    def __str__(self):
        outs = ["Molecule Summary ({s})".format(s=str(self.composition))]
        outs.append("Reduced Formula: " + str(self.composition.reduced_formula))
        to_s = lambda x : "%0.6f" % x
        outs.append("Sites ({i})".format(i=len(self)))
        for i, site in enumerate(self):
            outs.append(" ".join([str(i + 1), site.species_string, " ".join([to_s(j).rjust(12) for j in site.coords])]))
        return "\n".join(outs)

    @property
    def to_dict(self):
        """
        Json-serializable dict representation of Molecule
        """
        d = {}
        d['sites'] = [site.to_dict for site in self]
        return d

    @staticmethod
    def from_dict(d):
        """
        Reconstitute a Molecule object from a dict representation created using
        to_dict.
        
        Args:
            d: 
                dict representation of Molecule.
        
        Returns:
            Molecule object
        """
        species = []
        coords = []
        props = {}

        for site_dict in d['sites']:
            sp = site_dict['species']
            species.append({ Specie(sp['element'], sp['oxidation_state']) if 'oxidation_state' in sp else Element(sp['element'])  : sp['occu'] for sp in site_dict['species']})
            coords.append(site_dict['xyz'])
            siteprops = site_dict.get('properties', {})
            for k, v in siteprops.items():
                if k not in props:
                    props[k] = [v]
                else:
                    props[k].append(v)
        return Molecule(species, coords, site_properties=props)

    def get_distance(self, i, j):
        """
        Get distance between site i and j.
        
        Args:
            i:
                Index of first site
            j:
                Index of second site
        
        Returns:
            Distance between the two sites.
        """
        return self[i].distance(self[j])

    def get_sites_in_sphere(self, pt, r):
        '''
        Find all sites within a sphere from a point.
                
        Args:
            pt:
                cartesian coordinates of center of sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        '''
        neighbors = []
        for site in self._sites:
            dist = site.distance_from_point(pt)
            if dist <= r:
                neighbors.append((site, dist))
        return neighbors

    def get_neighbors(self, site, r):
        """
        Get all neighbors to a site within a sphere of radius r.  Excludes the 
        site itself.
        
        Args:
            site:
                site, which is the center of the sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        """
        return [(s, dist) for (s, dist) in self.get_sites_in_sphere(site.coords, r) if site != s]

    def get_neighbors_in_shell(self, origin, r, dr):
        """
        Returns all sites in a shell centered on origin (coords) between radii 
        r-dr and r+dr.
        
        Args:
            origin:
                cartesian coordinates of center of sphere.
            r:
                inner radius of shell.
            dr: 
                width of shell.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing
            requires the distance.
        """
        outer = self.get_sites_in_sphere(origin, r + dr)
        inner = r - dr
        return [(site, dist) for (site, dist) in outer if dist > inner]

    def get_boxed_structure(self, a, b, c):
        """
        Creates a Structure from a Molecule by putting the Molecule in a box.
        Useful for creating Structure for calculating molecules using periodic
        codes.
        
        Args:
            a:
                a-lattice parameter.
            b:
                b-lattice parameter.
            c:
                c-lattice parameter.
                
        Returns:
            Structure containing molecule in a box.
        """
        coords = np.array(self.cart_coords)
        x_range = max(coords[:, 0]) - min(coords[:, 0])
        y_range = max(coords[:, 1]) - min(coords[:, 1])
        z_range = max(coords[:, 2]) - min(coords[:, 2])
        if a <= x_range or b <= y_range or c <= z_range:
            raise ValueError("Box is not big enough to contain Molecule.")
        lattice = Lattice.from_parameters(a, b, c, 90, 90, 90)
        return Structure(lattice, self.species, self.cart_coords, coords_are_cartesian=True, site_properties=self.site_properties)

class StructureError(Exception):
    '''
    Exception class for Structure.
    Raised when the structure has problems, e.g., atoms that are too close.
    '''

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return "Structure Error : " + self.msg


class Composition (collections.Mapping, collections.Hashable):
    """
    Represents a Composition, which is essentially a {element:amount} dict. 
    Note that the key can be either an Element or a Specie. Elements and Specie
    are treated differently. i.e., a Fe2+ is not the same as a Fe3+ Specie and
    would be put in separate keys. This differentiation is deliberate to
    support using Composition to determine the fraction of a particular Specie.
    
    Works almost completely like a standard python dictionary, except that
    __getitem__ is overridden to return 0 when an element is not found 
    (somewhat like a defaultdict, except it is immutable).
    
    Also adds more convenience methods relevant to compositions, e.g., 
    get_fraction.
    
    >>> comp = Composition("LiFePO4")
    >>> comp.get_atomic_fraction(Element("Li"))
    0.14285714285714285
    >>> comp.num_atoms
    7.0
    >>> comp.reduced_formula
    'LiFePO4'
    >>> comp.formula
    'Li1 Fe1 P1 O4'
    >>> comp.get_wt_fraction(Element("Li"))
    0.04399794666951898
    >>> comp.num_atoms
    7.0
    """

    """
    Tolerance in distinguishing different composition amounts.
    1e-8 is fairly tight, but should cut out most floating point arithmetic errors.
    """
    amount_tolerance = 1e-8

    """
    Special formula handling for peroxides and certain elements. This is so that 
    formula output does not write LiO instead of Li2O2 for example.
    """
    special_formulas = {'LiO':'Li2O2', 'NaO':'Na2O2', 'KO':'K2O2', 'HO':'H2O2', 'O':'O2', 'F':'F2', 'N':'N2', 'Cl':'Cl2', 'H':'H2'}

    def __init__(self, *args, **kwargs):
        """
        Very flexible Composition construction, similar to the built-in Python
        dict(). Also extended to allow simple string init.
        
        Args:
            Any form supported by the Python built-in dict() function.
            
            1. A dict of either {Element/Specie: amount}, {string symbol:amount}, 
               or {atomic number:amount} or any mixture of these. E.g., 
               {Element("Li"):2 ,Element("O"):1}, {"Li":2, "O":1}, {3:2, 8:1}
               all result in a Li2O composition.
            2. Keyword arg initialization, similar to a dict, e.g., 
               Compostion(Li = 2, O = 1)
               
            In addition, the Composition constructor also allows a single string
            as an input formula. E.g., Composition("Li2O").
        """
        if len(args) == 1 and isinstance(args[0], basestring):
            elmap = self._parse_formula(args[0])
        else:
            elmap = dict(*args, **kwargs)
        if any([e < 0 for e in elmap.values()]):
            raise ValueError("Amounts in Composition cannot be negative!")
        self._elmap = {smart_element_or_specie(k): v for k, v in elmap.items()}
        self._natoms = sum(self._elmap.values())

    def __getitem__(self, el):
        '''
        Get the amount for element.
        '''
        return self._elmap.get(el, 0)

    def __eq__(self, other):
        for el in self.elements:
            if self[el] != other[el]:
                return False
        for el in other.elements:
            if self[el] != other[el]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        """
        Adds two compositions. For example, an Fe2O3 composition + an FeO 
        composition gives a Fe3O4 composition.
        """
        new_el_map = {el:self[el] for el in self}
        for k in other.keys():
            el = smart_element_or_specie(k)
            if el in self:
                new_el_map[el] += other[k]
            else:
                new_el_map[el] = other[k]
        return Composition(new_el_map)

    def __sub__(self, other):
        """
        Subtracts two compositions. For example, an Fe2O3 composition - an FeO 
        composition gives an FeO2 composition.
        
        Raises:
            ValueError if the subtracted composition is greater than the 
            original composition in any of its elements.
        """
        new_el_map = {el:self[el] for el in self}
        for k in other.keys():
            el = smart_element_or_specie(k)
            if el in self and other[k] <= self[el]:
                new_el_map[el] -= other[k]
            else:
                raise ValueError("All elements in subtracted composition must exist in original composition in equal or lesser amount!")
        return Composition(new_el_map)

    def __mul__(self, other):
        """
        Multiply a Composition by an integer or a float.
        Fe2O3 * 4 -> Fe8O12
        """
        if not (isinstance(other, int) or isinstance(other, float)):
            raise ValueError("Multiplication of composition can only be done for integers or floats!")
        return Composition({el:self[el] * other for el in self})

    def __hash__(self):
        '''
        Minimally effective hash function that just distinguishes between 
        Compositions with different elements.
        '''
        hashcode = 0
        for el in self._elmap.keys():
            #Ignore elements with zero amounts.
            if self[el] > self.amount_tolerance:
                hashcode += el.Z
        return 7

    def __contains__(self, el):
        return el in self._elmap

    def __len__(self):
        return len(self._elmap)

    def __iter__(self):
        return self._elmap.__iter__()

    @property
    def is_element(self):
        '''
        True if composition is for an element.
        '''
        positive_amts = [amt for amt in self._elmap.values() if amt > self.amount_tolerance]
        return len(positive_amts) == 1

    def copy(self):
        return Composition(self._elmap)

    @property
    def formula(self):
        '''
        Returns a formula string, with elements sorted by electronegativity,
        e.g., Li4 Fe4 P4 O16.
        '''
        sym_amt = self.to_dict
        syms = sorted(sym_amt.keys(), key=lambda s: Element(s).X)
        formula = []
        for s in syms:
            if sym_amt[s] != 0:
                formula.append(s + formula_double_format(sym_amt[s], False))
        return ' '.join(formula)

    @property
    def alphabetical_formula(self):
        '''
        Returns a formula string, with elements sorted by alphabetically 
        e.g. Fe4 Li4 O16 P4.
        '''
        sym_amt = self.to_dict
        syms = sorted(sym_amt.keys())
        formula = []
        for s in syms:
            if sym_amt[s] != 0:
                formula.append(s + formula_double_format(sym_amt[s], False))
        return ' '.join(formula)

    def get_reduced_composition_and_factor(self):
        '''
        Returns a normalized composition and a multiplicative factor, 
        i.e., Li4Fe4P4O16 returns (LiFePO4, 4).
        '''
        (formula, factor) = self.get_reduced_formula_and_factor()
        return (Composition.from_formula(formula), factor)

    def get_reduced_formula_and_factor(self):
        '''
        Returns a pretty normalized formula and a multiplicative factor, i.e., 
        Li4Fe4P4O16 returns (LiFePO4, 4).
        '''
        is_int = lambda x: x == int(x)
        all_int = all([is_int(x) for x in self._elmap.values()])
        if not all_int:
            return (re.sub("\s", "", self.formula), 1)

        sym_amt = self.to_dict
        syms = sorted(sym_amt.keys(), key=lambda s: Element(s).X)

        syms = filter(lambda s: sym_amt[s] != 0, syms)
        num_el = len(syms)
        contains_polyanion = False
        if num_el >= 3:
            contains_polyanion = (Element(syms[num_el - 1]).X - Element(syms[num_el - 2]).X < 1.65)

        factor = reduce(gcd, self._elmap.values())
        reduced_form = ''
        n = num_el
        if contains_polyanion:
            n -= 2

        for i in range(0, n):
            s = syms[i]
            normamt = sym_amt[s] * 1.0 / factor
            reduced_form += s + formula_double_format(normamt)

        if contains_polyanion:
            polyamounts = list()
            polyamounts.append(sym_amt[syms[num_el - 2]] / factor)
            polyamounts.append(sym_amt[syms[num_el - 1]] / factor)
            polyfactor = reduce(gcd, polyamounts)
            for i in range(n, num_el):
                s = syms[i]
                normamt = sym_amt[s] / factor / polyfactor
                if normamt != 1.0:
                    if normamt != int(normamt):
                        polyfactor = 1;
                        break;

            poly_form = ""

            for i in range(n, num_el):
                s = syms[i]
                normamt = sym_amt[s] / factor / polyfactor
                poly_form += s + formula_double_format(normamt);

            if polyfactor != 1:
                reduced_form += "({}){}".format(poly_form, int(polyfactor))
            else:
                reduced_form += poly_form

        if reduced_form in Composition.special_formulas:
            reduced_form = Composition.special_formulas[reduced_form]
            factor = factor / 2

        return (reduced_form, factor)

    @property
    def reduced_formula(self):
        '''
        Returns a pretty normalized formula, i.e., LiFePO4 instead of Li4Fe4P4O16.
        '''
        return self.get_reduced_formula_and_factor()[0]

    @property
    def elements(self):
        '''
        Returns view of elements in Composition.
        '''
        return self._elmap.keys()

    def __str__(self):
        return self.formula

    @property
    def num_atoms(self):
        '''
        Total number of atoms in Composition
        '''
        return self._natoms

    @property
    def weight(self):
        '''
        Total molecular weight of Composition
        '''
        return sum([amount * el.atomic_mass for el, amount in self._elmap.items()])

    def get_atomic_fraction(self, el):
        '''
        Args:
            el:
                Element
        
        Returns:
            Atomic fraction for element el in Composition
        '''
        return self[el] / self._natoms

    def get_wt_fraction(self, el):
        '''
        Args:
            el:
                Element
        
        Returns:
            Weight fraction for element el in Composition
        '''
        return el.atomic_mass * self[el] / self.weight

    def _parse_formula(self, formula):
        '''
        Args:
            formula:
                A string formula, e.g. Fe2O3, Li3Fe2(PO4)3
        
        Returns:
            Composition with that formula.
        '''
        def get_sym_dict(f, factor):
            sym_dict = {}
            for m in re.finditer(r"([A-Z][a-z]*)([\.\d]*)", f):
                el = m.group(1)
                amt = 1
                if m.group(2).strip() != "":
                    amt = float(m.group(2))
                if el in sym_dict:
                    sym_dict[el] += amt * factor
                else:
                    sym_dict[el] = amt * factor
                f = f.replace(m.group(), "", 1)
            if f.strip():
                raise ValueError("{} is an invalid formula!".format(f))
            return sym_dict
        m = re.search(r"\(([^\(\)]+)\)([\.\d]*)", formula)
        if m:
            factor = 1
            if m.group(2) != "":
                factor = float(m.group(2))
            unit_sym_dict = get_sym_dict(m.group(1), factor)
            expanded_formula = formula.replace(m.group(), "".join([el + str(amt) for el, amt in unit_sym_dict.items()]))
            return self._parse_formula(expanded_formula)
        return get_sym_dict(formula, 1)


    @staticmethod
    def from_formula(formula):
        '''
        .. deprecated:: 1.6.1
        
        Use Composition(formula) instead.
        '''
        return Composition(formula)

    @property
    def anonymized_formula(self):
        """
        An anonymized formula. Unique species are arranged in ordering of 
        increasing amounts and assigned ascending alphabets. Useful for 
        prototyping formulas. For example, all stoichiometric perovskites have
        anonymized_formula ABC3.
        """
        reduced_comp = self.get_reduced_composition_and_factor()[0]
        els = sorted(reduced_comp.elements, key=lambda e: reduced_comp[e])
        ascii_code = 65
        anon_formula = []
        for e in els:
            amt = reduced_comp[e]
            if amt > 0:
                if amt == 1:
                    amt_str = ''
                elif abs(amt % 1) < 1e-8:
                    amt_str = str(int(amt))
                else:
                    amt_str = str(amt)
                anon_formula.append('{}{}'.format(chr(ascii_code), amt_str))
                ascii_code += 1
        return "".join(anon_formula)

    def __repr__(self):
        return "Comp: " + self.formula

    @staticmethod
    def from_dict(d):
        '''
        Creates a composition from a dict generated by to_dict. Strictly not 
        necessary given that the standard constructor already takes in such an
        input, but this method preserves the standard pymatgen API of having
        from_dict methods to reconstitute objects generated by to_dict. Allows
        for easier introspection.
        
        Args:
            d:
                {symbol: amount} dict.
        '''
        return Composition(d)

    @property
    def to_dict(self):
        '''
        Returns:
            dict with element symbol and (unreduced) amount e.g. {"Fe": 4.0, "O":6.0}
        '''
        d = {}
        for e, a in self.items():
            if e.symbol in d:
                d[e.symbol] += a
            else:
                d[e.symbol] = a
        return d

    @property
    def to_reduced_dict(self):
        '''
        Returns:
            dict with element symbol and reduced amount e.g. {"Fe": 2.0, "O":3.0}
        '''
        reduced_formula = self.reduced_formula
        c = Composition.from_formula(reduced_formula)
        return c.to_dict

    @staticmethod
    def ranked_compositions_from_indeterminate_formula(fuzzy_formula, lock_if_strict=True):
        '''
        Takes in a formula where capitilization might not be correctly entered, 
        and suggests a ranked list of potential Composition matches.
        Author: Anubhav Jain
        
        Args:
            fuzzy_formula:
                A formula string, such as 'co2o3' or 'MN', that may or may not 
                have multiple interpretations
            lock_if_strict:
                If true, a properly entered formula will only return the one 
                correct interpretation. For example, 'Co1' will only return 
                'Co1' if true, but will return both 'Co1' and 'C1 O1' if false.
        
        Returns:
            A ranked list of potential Composition matches
        '''

        #if we have an exact match and the user specifies lock_if_strict, just return the exact match!
        if lock_if_strict:
            #the strict composition parsing might throw an error, we can ignore it and just get on with fuzzy matching
            try:
                comp = Composition.from_formula(fuzzy_formula)
                return [comp]
            except:
                pass

        all_matches = Composition._recursive_compositions_from_fuzzy_formula(fuzzy_formula)
        #remove duplicates
        all_matches = list(set(all_matches))
        #sort matches by rank descending
        all_matches = sorted(all_matches, key=lambda match:match[1], reverse=True)
        all_matches = [m[0] for m in all_matches]
        return all_matches

    @staticmethod
    def _recursive_compositions_from_fuzzy_formula(fuzzy_formula, m_dict={}, m_points=0, factor=1):
        '''
        A recursive helper method for formula parsing that helps in interpreting 
        and ranking indeterminate formulas.
        Author: Anubhav Jain
        
        Arguments:
            fuzzy_formula:
                A formula string, such as 'co2o3' or 'MN', that may or may not 
                have multiple interpretations.
            m_dict:
                A symbol:amt dictionary from the previously parsed formula
            m_points:
                Number of points gained from the previously parsed formula
            factor:
                Coefficient for this parse, e.g. (PO4)2 will feed in PO4 as the 
                fuzzy_formula with a coefficient of 2
        
        Returns:
            A list of tuples, with the first element being a Composition and 
            the second element being the number of points awarded that Composition intepretation
        '''

        def _parse_chomp_and_rank(m, f, m_dict, m_points):
            '''
            A helper method for formula parsing that helps in interpreting and ranking indeterminate formulas
            Author: Anubhav Jain
            
            Arguments:
                m:
                    a regex match, with the first group being the element and the second group being the amount
                f:
                    The formula part containing the match
                m_dict:
                    A symbol:amt dictionary from the previously parsed formula
                m_points:
                    Number of points gained from the previously parsed formula
            Returns:
                A tuple of (f, m_dict, points) where m_dict now contains data from the match and the match has been removed (chomped) from the formula f. The 'goodness'
                of the match determines the number of points returned for chomping. Returns (None, None, None) if no element could be found...
            '''

            points = 0
            points_first_capital = 100  # points awarded if the first element of the element is correctly specified as a capital
            points_second_lowercase = 100  # points awarded if the second letter of the element is correctly specified as lowercase

            #get element and amount from regex match
            el = m.group(1)
            if len(el) > 2 or len(el) < 1:
                raise ValueError("Invalid element symbol entered!")
            amt = float(m.group(2)) if m.group(2).strip() != "" else 1

            #convert the element string to proper [uppercase,lowercase] format and award points if it is already in that format
            char1 = el[0]
            char2 = el[1] if len(el) > 1 else ''

            if char1 == char1.upper():
                points += points_first_capital
            if char2 and char2 == char2.lower():
                points += points_second_lowercase

            el = char1.upper() + char2.lower()

            #if it's a valid element, chomp and add to the points
            if Element.is_valid_symbol(el):
                if el in m_dict:
                    m_dict[el] += amt * factor
                else:
                    m_dict[el] = amt * factor
                return (f.replace(m.group(), "", 1), m_dict, m_points + points)

            #else return None
            return (None, None, None)

        fuzzy_formula = fuzzy_formula.strip()

        if len(fuzzy_formula) == 0:
            #the entire formula has been parsed into m_dict. Return the corresponding Composition and number of points
            if m_dict:
                yield (Composition.from_dict(m_dict), m_points)
        else:
            #if there is a parenthesis, remove it and match the remaining stuff with the appropriate factor
            for mp in re.finditer(r"\(([^\(\)]+)\)([\.\d]*)", fuzzy_formula):
                mp_points = m_points
                mp_form = fuzzy_formula
                mp_dict = dict(m_dict)
                mp_factor = 1 if mp.group(2) == "" else float(mp.group(2))
                #match the stuff inside the parenthesis with the appropriate factor
                for match in Composition._recursive_compositions_from_fuzzy_formula(mp.group(1), mp_dict, mp_points, factor=mp_factor):
                    only_me = True
                    #match the stuff outside the parentheses and return the sum
                    for match2 in Composition._recursive_compositions_from_fuzzy_formula(mp_form.replace(mp.group(), " ", 1), mp_dict, mp_points, factor=1):
                        only_me = False
                        yield (match[0] + match2[0], match[1] + match2[1])
                    #if the stuff inside the parenthesis is nothing, then just return the stuff inside the parentheses
                    if only_me:
                        yield match
                return

            #try to match the single-letter elements
            m1 = re.match(r"([A-z])([\.\d]*)", fuzzy_formula)
            if m1:
                m_points1 = m_points
                m_form1 = fuzzy_formula
                m_dict1 = dict(m_dict)
                (m_form1, m_dict1, m_points1) = _parse_chomp_and_rank(m1, m_form1, m_dict1, m_points1)
                if m_dict1:
                    #there was a real match
                    for match in Composition._recursive_compositions_from_fuzzy_formula(m_form1, m_dict1, m_points1, factor):
                        yield match

            #try to match two-letter elements
            m2 = re.match(r"([A-z]{2})([\.\d]*)", fuzzy_formula)
            if m2:
                m_points2 = m_points
                m_form2 = fuzzy_formula
                m_dict2 = dict(m_dict)
                (m_form2, m_dict2, m_points2) = _parse_chomp_and_rank(m2, m_form2, m_dict2, m_points2)
                if m_dict2:
                    #there was a real match
                    for match in Composition._recursive_compositions_from_fuzzy_formula(m_form2, m_dict2, m_points2, factor):
                        yield match

if __name__ == "__main__":
    import doctest
    doctest.testmod()
