#!/usr/bin/env python

"""
This module provides classes used to define a structure, such as 
Site, PeriodicSite, Structure, and Composition.
"""

from __future__ import division

__author__="Shyue Ping Ong"
__copyright__ = "Copyright 2011, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Shyue Ping Ong"
__email__ = "shyue@mit.edu"
__status__ = "Production"
__date__ ="Sep 23, 2011"

import re
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
    A generalized *non-periodic* site. Atoms and occupancies should be a dictionary of element:occupancy
    or an element, in which case the occupancy default to 1.
    Coords are given in standard cartesian coordinates, NOT fractional coords.
    '''
    
    def __init__(self, atoms_n_occu, coords):
        """
        Create a *non-periodic* site.
        
        Arguments:
            atoms_n_occu: 
                dict of elements or species and occupancies. Elements can be specified as 
                symbols (Fe), atomic numbers (27), or actual Element objects.  Specie can
                be specified as Specie objects, or strings (Fe2+).
            coords: 
                Cartesian coordinates of site.
        """
        
        if isinstance(atoms_n_occu,dict):
            self._species = {smart_element_or_specie(k) : v for k, v in atoms_n_occu.items()}
            totaloccu = sum(self._species.values())
            if totaloccu > 1:
                raise ValueError("Species occupancies sum to more than 1!")
            self._is_ordered = (totaloccu == 1 and len(self._species) == 1)
        else:
            self._species = {smart_element_or_specie(atoms_n_occu):1}
            self._is_ordered = True
        self._coords = coords
        
    def distance(self, other):
        """
        Get distance between two sites.
        
        Args:
            other:
                Other site.
        """
        return np.linalg.norm(other.coords-self.coords)

    def distance_from_point(self, pt):
        """
        Returns distance between the site and a point in space.
        
        Args:
            pt:
                cartesian coordinates of point.
        """
        return np.linalg.norm(pt-self._coords)

    @property
    def species_string(self):
        """
        String representation of species on the site.
        """
        if self._is_ordered:
            return str(self._species.keys()[0])
        else:
            return ', '.join(["%s:%.3f" % (str(atom),occu) for atom,occu in self._species.items()])

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
            
        The Specie/Element at the site. Only works for ordered sites.  Otherwise an AttributeError is raised.
        Use this property sparingly.  Robust design should make use of the property species_and_occu instead.
        
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
        """True if site is an ordered site, i.e., with a single species with occupancy 1"""
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
    
    def __getitem__(self,el):
        '''
        Get the occupancy for element
        '''
        return self._species[el]
    
    def __eq__(self, other):
        """Site is equal to another site if the species and occupancies are the same, and the coordinates
        are the same to some tolerance.  numpy function `allclose` is used to determine if coordinates are close."""
        if other == None:
            return False
        return self._species == other._species and np.allclose(self._coords, other._coords)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __hash__(self):
        '''
        Minimally effective hash function that just distinguishes between Sites with different elements.
        '''
        hashcode = 0
        for el in self._species.keys():
            #Ignore elements with zero amounts.
            if self[el] != 0:
                hashcode += el.Z 
        return hashcode
    
    def __contains__(self,el):
        return el in self._species
    
    def __len__(self):
        return len(self._species)
    
    def __iter__(self):
        return self._species.__iter__()
    
    def __repr__(self):
        outs = []
        outs.append("Non-periodic Site")
        outs.append("xyz        : (%0.4f, %0.4f, %0.4f)" % tuple(self.coords))
        for k,v in self._species.items():
            outs.append("element    : %s" % k.symbol)
            outs.append("occupation : %0.2f" % v)
        return "\n".join(outs)

    def __cmp__(self, other):
        '''
        Sets a default sort order for atomic species by electronegativity.  Very
        useful for getting correct formulas.  For example, FeO4PLi is automatically
        sorted in LiFePO4.
        '''
        def avg_electroneg(sps):
            return sum([sp.X * occu for sp, occu in sps.items()])
        
        if avg_electroneg(self._species) < avg_electroneg(other._species):
            return -1
        if avg_electroneg(self._species) > avg_electroneg(other._species):
            return 1
        return 0

    def __str__(self):
        return "%s %s" %(self._coords, ','.join(["%s %.4f" % (str(atom),occu) for atom,occu in self._species.items()]))

    @property
    def to_dict(self):
        """A dictionary representation for Site that is json serializable."""
        species_list = []
        for spec, occu in self._species.items():
            if isinstance(spec, Specie):
                species_list.append({'element': spec.symbol, 'occu': occu, 'oxidation_state': spec.oxi_state})
            elif isinstance(spec, Element):
                species_list.append({'element': spec.symbol, 'occu': occu})
        return {'name': self.species_string, 'species': species_list, 'occu': occu, 'xyz':list(self._coords)}

class PeriodicSite(Site):
    """
    Extension of generic Site object to periodic systems.
    PeriodicSite includes a lattice system.
    """

    def __init__(self, atoms_n_occu, coords, lattice, to_unit_cell = False, coords_are_cartesian = False):
        """
        Create a periodic site.
        
        Args:
            atoms_n_occu:
                dict of elements and occupancies
            coords:
                coordinates of site as fractional coordinates or cartesian coordinates
            lattice:
                Lattice associated with the site
            to_unit_cell:
                translates fractional coordinate to the basic unit cell, i.e. all fractional coordinates satisfy 0 <= a < 1.
                Defaults to False.
            coords_are_cartesian:
                Set to True if you are providing cartesian coordinates.  Defaults to False.
        """
        self._lattice = lattice
        self._fcoords = lattice.get_fractional_coords(coords) if coords_are_cartesian else coords
        
        if to_unit_cell:
            for i in xrange(len(self._fcoords)):
                self._fcoords[i] = self._fcoords[i] - math.floor(self._fcoords[i]) 
                
        c_coords = lattice.get_cartesian_coords(self._fcoords)
        Site.__init__(self,atoms_n_occu,c_coords)

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
        """Copy of PeriodicSite translated to the unit cell."""
        fcoords = [i - math.floor(i) for i in self._fcoords]
        return PeriodicSite(self._species, fcoords, self._lattice)
    
    def is_periodic_image(self, other, tolerance = 1e-8):
        """
        Returns True if sites are periodic images of each other.
        """
        if self.lattice != other.lattice:
            return False
        return  (abs(self._fcoords - other._fcoords) % 1 < tolerance).all()
    
    def __eq__(self, other):
        return self._species == other._species and self._lattice == other._lattice and np.allclose(self._coords, other._coords)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def distance_and_image_old(self,other,jimage=None):
        """
        .. deprecated:: 1.0
            Use :func:`distance_and_image` instead. This code is kept for information reasons. 
            A new version has been written which is more accurate, but at a higher computational cost.
        
        Gets distance between two sites assuming periodic boundary conditions.
        If the index jimage of two sites atom j is not specified it selects the j image nearest to the i atom
        and returns the distance and jimage indices in terms of lattice vector translations.
        if the index jimage of atom j is specified it returns the distance between
        the i atom and the specified jimage atom, the given jimage is also returned.
        
        Arguments:
            other:
                other site to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one a-lattice vector away.
                if jimage == None, the image that is nearest to the site is found.
        
        Returns:
            (distance, jimage)
                distance and periodic lattice translations of the other site for which the distance applies.
        
        .. note::
            Assumes the primitive cell vectors are sufficiently not skewed such that the condition
            \|a\|cos(ab_angle) < \|b\| for all possible cell vector pairs
            ** this method does not check this condition **
        """
        if jimage == None:
            #Old algorithm
            jimage = - np.array(np.around(other._fcoords-self._fcoords),int)
        return np.linalg.norm(self.lattice.get_cartesian_coords(jimage + other._fcoords - self._fcoords)), jimage
    
    def distance_and_image_from_frac_coords(self, fcoords, jimage=None):
        """
        Gets distance between site and a fractional coordinate assuming periodic boundary conditions.
        If the index jimage of two sites atom j is not specified it selects the j image nearest to the i atom
        and returns the distance and jimage indices in terms of lattice vector translations.
        if the index jimage of atom j is specified it returns the distance between
        the i atom and the specified jimage atom, the given jimage is also returned.
        
        Arguments:
            fcoords:
                fcoords to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one a-lattice vector away.
                if jimage == None, the image that is nearest to the site is found.
        
        Returns:
            (distance, jimage):
                distance and periodic lattice translations of the other site for which the distance applies.
        
        """
        if jimage == None:
            adj1 = np.array([- math.floor(i) for i in self._fcoords])
            adj2 = np.array([- math.floor(i) for i in fcoords])
            mindist = float('inf')
            coord1 = self._fcoords + adj1
            coord2 = fcoords + adj2
            test_set = [[-1,0] if coord1[i] < coord2[i] else [0,1] for i in xrange(3)]
            for image in itertools.product(*test_set):
                dist = np.linalg.norm(self._lattice.get_cartesian_coords(coord2 + image - coord1))
                if dist < mindist:
                    mindist = dist
                    jimage = adj2 - adj1 + image
            return mindist, jimage        
        return np.linalg.norm(self.lattice.get_cartesian_coords(jimage + fcoords - self._fcoords)), jimage

    def distance_and_image(self, other, jimage=None):
        """
        Gets distance and instance between two sites assuming periodic boundary conditions.
        If the index jimage of two sites atom j is not specified it selects the j image nearest to the i atom
        and returns the distance and jimage indices in terms of lattice vector translations.
        if the index jimage of atom j is specified it returns the distance between
        the i atom and the specified jimage atom, the given jimage is also returned.
        
        Arguments:
            other:
                other site to get distance from.
            jimage:
                specific periodic image in terms of lattice translations, 
                e.g., [1,0,0] implies to take periodic image that is one a-lattice vector away.
                if jimage == None, the image that is nearest to the site is found.
        
        Returns:
            (distance, jimage):
                distance and periodic lattice translations of the other site for which the distance applies.
        """
        return self.distance_and_image_from_frac_coords(other._fcoords, jimage)

    def distance(self, other, jimage=None):
        """
        Get distance between two sites assuming periodic boundary conditions.
        
        Arguments:
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
        for k,v in self._species.items():
            outs.append("element    : %s" % k.symbol)
            outs.append("occupation : %0.2f" % v)
        return "\n".join(outs)

    @property
    def to_dict(self):
        species_list = []
        for spec, occu in self._species.items():
            if isinstance(spec, Specie):
                species_list.append({'element': spec.symbol, 'occu': occu, 'oxidation_state': spec.oxi_state})
            elif isinstance(spec, Element):
                species_list.append({'element': spec.symbol, 'occu': occu})
        return {'label': self.species_string, 'species': species_list, 'occu': occu, 'xyz':list(self._coords), 'abc':list(self._fcoords)}

class Structure(collections.Sequence, collections.Hashable):
    """
    Basic Structure object with periodicity. Essentially a sequence of sites having a common lattice.
    Structure is made to be immutable so that they can function as keys in a dictionary.  
    Modifications should be done by making a new Structure using the structure_modifier module or your own methods.
    Structure extends Sequence and Hashable, which means that in many cases, it can be used like any Python sequence.
    """
    
    DISTANCE_TOLERANCE = 0.01
    
    def __init__(self, lattice, atomicspecies, coords, validate_proximity = False, to_unit_cell = False, coords_are_cartesian = False):
        """
        Create a periodic structure.
        
        Arguments:
            lattice:
                pymatgen.core.lattice Lattice object signify the lattice.
            atomicspecies:
                list of atomic species.  dict of elements and occupancies.
            fractional_coords:
                list of fractional coordinates of each species.
            validate_proximity:
                Whether to check if there are sites that are less than 1 Ang apart. Defaults to false.
            coords_are_cartesian:
                Set to True if you are providing coordinates in cartesian coordinates. Defaults to false.
        """
        if len(atomicspecies) != len(coords):
            raise StructureError("The list of atomic species must be of the same length as the list of fractional coordinates.")
           
        if isinstance(lattice,Lattice):
            self._lattice = lattice
        else:
            self._lattice = Lattice(lattice)
        
        self._sites = [PeriodicSite(atomicspecies[i],coords[i],self._lattice, to_unit_cell, coords_are_cartesian) for i in xrange(len(atomicspecies))]
        if validate_proximity:
            for (s1, s2) in itertools.combinations(self._sites, 2):
                if s1.distance(s2) < Structure.DISTANCE_TOLERANCE:
                    raise StructureError("Structure contains sites that are less than 0.01 Angstrom apart!")
    
    @property
    def lattice(self):
        """
        Lattice of the structure.
        """
        return self._lattice
    
    @property
    def species(self):
        """
        List of species at each site of the structure.
        Only works for ordered structures.
        Disordered structures will raise an AttributeError.
        """
        return [site.specie for site in self._sites]
    
    @property
    def species_and_occu(self):
        """
        List of species and occupancies at each site of the structure.
        """
        return [site.species_and_occu for site in self._sites]
    
    @property
    def sites(self):
        """
        Returns an iterator for the sites in the Structure. 
        """
        for site in self._sites:
            yield site

    def __contains__(self, site):
        return site in self._sites
    
    def __iter__(self):
        return self._sites.__iter__()

    def __getitem__(self, ind):
        return self._sites[ind]

    def __len__(self):
        return len(self._sites)
    
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
    def num_sites(self):
        """
        Number of sites in the structure.
        """
        return len(self._sites)
    
    @property
    def frac_coords(self):
        '''
        Returns the fractional coordinates.
        '''
        return [site.frac_coords for site in self._sites]

    @property
    def cart_coords(self):
        '''
        Returns a list of the cartesian coordinates of sites in the structure.
        '''
        return [site.coords for site in self._sites]

    @property
    def volume(self):
        '''
        Returns the volume of the structure.
        '''
        return self._lattice.volume
   
    @property
    def density(self):
        '''
        Returns the density in units of g/cc
        '''
        constant = 1.660468
        return self.composition.weight/self.volume*constant
    
    def get_distance(self,i,j,jimage=None):
        """
        get distance between site i and j assuming periodic boundary conditions
        if the index jimage of two sites atom j is not specified it selects the j image nearest to the i atom
        and returns the distance and jimage indices in terms of lattice vector translations
        if the index jimage of atom j is specified it returns the distance between
        the i atom and the specified jimage atom, the given jimage is also returned.
        """
        return self[i].distance(self[j], jimage)
    
    def get_sites_in_sphere(self, pt, r):
        '''
        Find all sites within a sphere from the structure. This includes sites in other periodic images.
        
        Algorithm: 
        
        1. place sphere of radius r in crystal and determine minimum supercell (parallelpiped) which would
           contain a sphere of radius r. for this we need the projection of a_1 on a unit vector perpendicular 
           to a_2 & a_3 (i.e. the unit vector in the direction b_1) to determine how many a_1's it will
           take to contain the sphere. 
           
           Nxmax = r * length_of_b_1 / (2 Pi)
        
        2. keep points falling within r.
        
        Arguments:
            pt:
                cartesian coordinates of center of sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing requires the distance.
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
        for image in itertools.product(xrange(nxmin, nxmax+1), xrange(nymin, nymax+1), xrange(nzmin, nzmax+1)):
            submat = [image] * n
            fcoords = site_fcoords + submat
            coords = self._lattice.get_cartesian_coords(fcoords)
            dists = (coords - pts) ** 2
            dists = np.sqrt(dists.sum(axis = 1))
            withindists = (dists <= r)
            for i in xrange(n):
                if withindists[i]:
                    neighbors.append((PeriodicSite(self._sites[i].species_and_occu, fcoords[i], self._lattice), dists[i]))
        
        return neighbors
       
    def get_neighbors(self, site, r):
        """
        Get all neighbors to a site within a sphere of radius r.  Excludes the site itself.
        
        Arguments:
            site:
                site, which is the center of the sphere.
            r:
                radius of sphere.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing requires the distance.
        """
        return [(s, dist) for (s, dist) in self.get_sites_in_sphere(site.coords, r) if site != s]
    
    def get_all_neighbors(self, r):
        """
        Get neighbors for each atom in the unit cell, out to a distance r
        Returns a list of list of neighbors for each site in structure.
        Use this method if you are planning on looping over all sites in the
        crystal. If you only want neighbors for a particular site, use the method
        get_neighbors as it may not have to build such a large supercell
        However if you are looping over all sites in the crystal, this method is
        more efficient since it only performs *one* pass over a large enough 
        supercell to contain all possible atoms out to a distance r.
        The return type is a [(site, dist) ...] since most of the time, subsequent 
        processing requires the distance.
        
        Arguments:
            r:
                radius of sphere.
        
        Returns:
            A list of a list of nearest neighbors for each site, i.e., [[(site, dist) ...], ..] 
        
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
        for image in itertools.product(xrange(nxmin, nxmax+1), xrange(nymin, nymax+1), xrange(nzmin, nzmax+1)):
            for site in unit_cell_sites:
                fcoords = site.frac_coords + np.array(image)
                coords = self.lattice.get_cartesian_coords(fcoords)
                submat = [coords] * n
                dists = (site_coords - submat) ** 2
                dists = np.sqrt(dists.sum(axis = 1))
                withindists = (dists <= r) * (dists > 1e-8)
                for i in xrange(n):
                    if withindists[i]:
                        neighbors[i].append((PeriodicSite(site.species_and_occu,fcoords, site.lattice), dists[i]))
                
        return neighbors
    
    
    def get_neighbors_in_shell(self, origin, r, dr):
        """
        Returns all sites in a shell centered on origin (coords) between radii r-dr and r+dr.
        
        Arguments:
            origin:
                cartesian coordinates of center of sphere.
            r:
                inner radius of shell.
            dr: 
                width of shell.
        
        Returns:
            [(site, dist) ...] since most of the time, subsequent processing requires the distance.
        
        """
        outer = self.get_sites_in_sphere(origin, r + dr)
        inner = r - dr
        return [(site, dist) for (site, dist) in outer if dist > inner]
    
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
        elmap = dict()
        for site in self._sites:
            for species, occu in site.species_and_occu.items():
                if species in elmap:
                    elmap[species] += occu
                else:
                    elmap[species] = occu
        return Composition(elmap)

    def get_sorted_structure(self):
        """
        Get a sorted copy of the structure.
        Sites are sorted by the electronegativity of the species.
        """
        sortedsites = sorted(self.sites)
        return Structure(self._lattice,[site.species_and_occu for site in sortedsites],[site.frac_coords for site in sortedsites])

    def interpolate(self, end_structure, nimages = 10):
        '''
        Interpolate between this structure and end_structure. Useful for construction
        NEB inputs.
        
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
        if not ((abs(self.lattice.matrix-end_structure.lattice.matrix) < 0.01)).all():
            raise ValueError("You are interpolating structures with different lattices!")
        
        #Check that both structures have the same species
        for i in xrange(0,len(self)):
            if self[i].species_and_occu != end_structure[i].species_and_occu:
                raise ValueError("You are interpolating different structures!\nStructure 1:\n" + str(self) + "\nStructure 2\n"+str(end_structure))
        
        start_coords = np.array(self.frac_coords)
        end_coords = np.array(end_structure.frac_coords)

        jimage=-np.array(np.around(end_coords-start_coords),int)
        vec = end_coords - start_coords + jimage
        intStructs = [Structure(self.lattice,[site.species_and_occu for site in self._sites],start_coords + float(x)/float(nimages) * vec) for x in xrange(0,nimages+1)]
        return intStructs;
    
    @property
    def is_ordered(self):
        """
        Checks if structure is ordered, meaning no partial occupancies in any of the sites. 
        """
        for site in self._sites:
            if not site.is_ordered:
                return False
        return True

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
        outs.append("Sites ({i})".format(i = len(self)))
        for i, site in enumerate(self):
            outs.append(" ".join([str(i+1), site.specie.symbol, " ".join([to_s(j).rjust(12) for j in site.frac_coords])]))
        return "\n".join(outs)
    
    @property
    def to_dict(self):
        """Json-friendly, dict representation of Structure"""
        d = {}
        d['lattice'] = self._lattice.to_dict
        d['sites'] = [site.to_dict for site in self]
        return d
    
    @staticmethod
    def from_dict(structure_dict):
        """Reconstitute a Structure object from a dict representation of Structure created using to_dict.
        
        Arguments:
            structure_dict: 
                dict representation of structure.
        
        Returns:
            Structure object
        """
        lattice = Lattice(structure_dict['lattice']['matrix'])
        species = []
        coords = []
            
        for site_dict in structure_dict['sites']:
            sp = site_dict['species'] 
            species.append({ Specie(sp['element'], sp['oxidation_state']) if 'oxidation_state' in sp else Element(sp['element'])  : sp['occu'] for sp in site_dict['species']} )
            coords.append(site_dict['abc'])
        return Structure(lattice, species, coords)

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
    Represents a Composition, which is essentially a {element:amount} dictionary.
    
    Works almost completely like a standard python dictionary, except that __getitem__
    is overridden to return 0 when an element is not found.
    
    Also adds more convenience methods relevant to compositions, e.g., get_fraction.
    
    >>> comp = Composition.from_formula("LiFePO4")
    >>> comp.get_atomic_fraction("Li")
    0.0
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
    special_formulas = {'LiO':'Li2O2','NaO':'Na2O2','KO':'K2O2','HO':'H2O2', 'O':'O2','F':'F2','N':'N2','Cl':'Cl2', 'H':'H2'}
    
    def __init__(self, elmap):
        """
        Args:
            elmap: 
                a dict of {Element/Specie: float} representing amounts of each element or specie.
        """
        if any([e < 0 for e in elmap.values()]):
            raise ValueError("Amounts in Composition cannot be negative!")
        if not any([isinstance(e, (Element,Specie)) for e in elmap.keys()]):
            raise TypeError("Keys must be instances of Element or Specie!")
        self._elmap = elmap.copy()
        self._natoms = sum(self._elmap.values())

    @property
    def is_element(self):
        '''
        True if composition is for an element
        '''
        return len(self._elmap)==1

    def __getitem__(self,el):
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
        Adds two compositions.
        For example, an Fe2O3 composition + an FeO composition gives a Fe3O4 composition.
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
        Subtracts two compositions.
        For example, an Fe2O3 composition - an FeO composition gives an FeO2 composition.
        raises a ValueError if the subtracted composition is greater than the original composition
        in any of its elements.
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
        return Composition({el:self[el]*other for el in self})

    def __hash__(self):
        '''
        Minimally effective hash function that just distinguishes between Compositions with different elements.
        '''
        hashcode = 0
        for el in self._elmap.keys():
            #Ignore elements with zero amounts.
            if self[el] > self.amount_tolerance:
                hashcode += el.Z 
        return hashcode
    
    def __contains__(self,el):
        return el in self._elmap
    
    def __len__(self):
        return len(self._elmap)
    
    def __iter__(self):
        return self._elmap.__iter__()
    
    def copy(self):
        return Composition(self._elmap)

    @property
    def formula(self):
        '''
        Returns a formula string, e.g. Li4 Fe4 P4 O16.
        '''
        elements = self._elmap.keys()
        elements = sorted(elements,key=lambda el: el.X)
        formula = []
        for el in elements:
            if self[el] != 0:
                formula.append(el.symbol+formula_double_format(self[el], False))
        return ' '.join(formula)
    
    def get_reduced_formula_and_factor(self):
        '''
        Returns a pretty normalized formula and a multiplicative factor, i.e., Li4Fe4P4O16 returns (LiFePO4, 4).
        '''
        
        elements = self._elmap.keys()
        elements = sorted(elements,key=lambda el: el.X)
        elements = filter(lambda el: self[el] != 0, elements)
        num_el = len(elements)
        contains_polyanion = False
        if num_el >= 3:
            contains_polyanion = (elements[num_el-1].X - elements[num_el-2].X < 1.65)
        
        factor = reduce(gcd,self._elmap.values())

        reduced_form = ''
        n = num_el
        if contains_polyanion:
            n -= 2
        
        for i in xrange(0,n):
            el = elements[i]
            normamt = self._elmap[el] *1.0 / factor
            reduced_form += el.symbol + formula_double_format(normamt) 

        if contains_polyanion:
            polyamounts = list()
            polyamounts.append(self._elmap[elements[num_el - 2]] / factor)
            polyamounts.append(self._elmap[elements[num_el - 1]] / factor)
            polyfactor = reduce(gcd,polyamounts)
            for i in xrange(n,num_el):
                el = elements[i]
                normamt = self._elmap[el] / factor / polyfactor
                if normamt != 1.0:
                    if normamt != int(normamt):
                        polyfactor = 1;
                        break;
            
            poly_form = ""
            
            for i in xrange(n,num_el):
                el = elements[i]
                normamt = self._elmap[el] / factor / polyfactor
                poly_form += el.symbol + formula_double_format(normamt);

            if polyfactor != 1:
                reduced_form += "("+poly_form+ ")"+ str(int(polyfactor))
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
        Arguments:
            el:
                Element
        Returns:
            Atomic fraction for element el in Composition
        '''
        return self[el]/self._natoms
    
    def get_wt_fraction(self, el):
        '''
        Arguments:
            el:
                Element
        Returns:
            Weight fraction for element el in Composition
        '''
        return el.atomic_mass*self[el]/self.weight
   
    @staticmethod
    def from_formula(formula):
        '''
        Arguments:
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
            return sym_dict
        m = re.search(r"\(([^\(\)]+)\)([\.\d]*)", formula)
        if m:
            factor = 1
            if m.group(2) != "":
                factor = float(m.group(2))
            unit_sym_dict = get_sym_dict(m.group(1), factor)
            expanded_formula = formula.replace(m.group(), "".join([el+str(amt) for el, amt in unit_sym_dict.items()]))
            return Composition.from_formula(expanded_formula)
        return Composition.from_dict(get_sym_dict(formula, 1))
    
    
    def __repr__(self):
        return "Comp: " + self.formula
        
    @staticmethod
    def from_dict(sym_dict):
        '''
        Arguments:
            sym_dict:
                A element symbol: amount dict, e.g. {"Fe":2, "O":3}
        Returns:
            Composition with that formula.
        '''
        return Composition( {Element(sym) : amt for sym, amt in sym_dict.items()})
    
    @property
    def to_dict(self):
        '''
        Returns:
            dict with element symbol and (unreduced) amount e.g. {"Fe": 4.0, "O":6.0}
        '''
        return {e.symbol: a for e, a in self.items()}
    
    @property
    def to_reduced_dict(self):
        '''
        Returns:
            dict with element symbol and reduced amount e.g. {"Fe": 2.0, "O":3.0}
        '''
        reduced_formula = self.reduced_formula
        c = Composition.from_formula(reduced_formula)
        return c.to_dict

if __name__ == "__main__":
    import doctest
    doctest.testmod()