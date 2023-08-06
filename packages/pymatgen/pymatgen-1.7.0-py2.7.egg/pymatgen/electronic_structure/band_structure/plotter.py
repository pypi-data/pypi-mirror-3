#!/usr/bin/env python
"""
This module provides classes and utilities to plot band structures
"""

__author__ = "Geoffroy Hautier, Shyue Ping Ong, Michael Kocher"
__copyright__ = "Copyright 2012, The Materials Project"
__version__ = "1.0"
__maintainer__ = "Geoffroy Hautier"
__email__ = "geoffroy@uclouvain.be"
__status__ = "Development"
__date__ = "March 14, 2012"

import logging

log = logging.getLogger('BSPlotter')


class BSPlotter(object):

    """
    class used to plot or get data to facilitate the plot of band structure line objects
    """

    def __init__(self, bs):
        """
        Arguments:
            bs:
                A Bandstructure_line object.
        """
        self._bs = bs
        self._nb_bands = bs._nb_bands

    @property
    def bs_plot_data(self):

        """
        Get the data nicely formatted for a plot
        
        Returns:
            A dict of the following format:
                'ticks': a dictionary with the 'distances' at which there is a 
                kpoint (the x axis) and the labels (None if no label)
                'energy': an array (one element for each band) of energy for 
                each kpoint
        """

        energy = []
        distance = [self._bs._distance[j] for j in range(len(self._bs._kpoints))]
        ticks = self.get_ticks()
        for i in range(self._nb_bands):
            #pylab.plot([self._distance[j] for j in range(len(self._kpoints))],[self._bands[i]['energy'][j] for j in range(len(self._kpoints))],'b-',linewidth=5)
            energy.append([self._bs._bands[i]['energy'][j] for j in range(len(self._bs._kpoints))])

        return {'ticks': ticks, 'distances': distance, 'energy': energy}

    def show(self, file_name=None, zero_to_efermi=True):
        """
        Show the bandstrucure plot.
        
        Args:
            file_name:
                File name to write image to (e.g., plot.eps). If None no image is created
            zero_to_efermi:
                Automatically subtract off the Fermi energy from the eigenvalues and plot (E-Ef)
        """
        import pylab
        from matplotlib import rc

        #rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica'], 'size': 20})
        rc('text', usetex=True)

        #main internal config options
        e_min = -8
        e_max = 8
        band_linewidth = 1

        pylab.figure
        data = self.bs_plot_data

        for i in range(self._nb_bands):
            if zero_to_efermi:
                pylab.plot(data['distances'], [e - self._bs.efermi for e in data['energy'][i]], 'b-', linewidth=band_linewidth)
            else:
                pylab.plot(data['distances'], data['energy'][i], 'b-', linewidth=band_linewidth)

        ticks = self.get_ticks()
        # ticks is dict wit keys: distances (array floats), labels (array str)
        log.debug("ticks {t}".format(t=ticks))
        log.debug("ticks has {n} distances and {m} labels".format(n=len(ticks['distance']), m=len(ticks['label'])))
        # Draw lines for BZ boundries
        for i in range(len(ticks['label'])):
            if ticks['label'][i] is not None:
                # don't print the same label twice
                if i != 0:
                    if (ticks['label'][i] == ticks['label'][i - 1]):
                        log.debug("already print label... skipping label {i}".format(i=ticks['label'][i]))
                    else:
                        log.debug("Adding a line at {d} for label {l}".format(d=ticks['distance'][i], l=ticks['label'][i]))
                        pylab.axvline(ticks['distance'][i], color='k')
                else:
                    log.debug("Adding a line at {d} for label {l}".format(d=ticks['distance'][i], l=ticks['label'][i]))
                    pylab.axvline(ticks['distance'][i], color='k')

        #Sanitize only plot the uniq values
        uniq_d = []
        uniq_l = []
        temp_ticks = zip(ticks['distance'], ticks['label'])
        for i in xrange(len(temp_ticks)):
            if i == 0:
                uniq_d.append(temp_ticks[i][0])
                uniq_l.append(temp_ticks[i][1])
                log.debug("Adding label {l} at {d}".format(l=temp_ticks[i][0], d=temp_ticks[i][1]))
            else:
                if temp_ticks[i][1] == temp_ticks[i - 1][1]:
                    log.debug("Skipping label {i}".format(i=temp_ticks[i][1]))
                else:
                    log.debug("Adding label {l} at {d}".format(l=temp_ticks[i][0], d=temp_ticks[i][1]))
                    uniq_d.append(temp_ticks[i][0])
                    uniq_l.append(temp_ticks[i][1])

        log.debug("Unique labels are {i}".format(i=zip(uniq_d, uniq_l)))
        #pylab.gca().set_xticks(ticks['distance'])
        #pylab.gca().set_xticklabels(ticks['label'])
        pylab.gca().set_xticks(uniq_d)
        pylab.gca().set_xticklabels(uniq_l)

        #Main X and Y Labels
        pylab.xlabel(r'$\mathrm{Wave\ Vector}$', fontsize='large')
        ylabel = r'$\mathrm{E\ -\ E_f\ (eV)}$' if zero_to_efermi else r'$\mathrm{Energy\ (eV)}$'
        pylab.ylabel(ylabel, fontsize='large')

        # Draw Fermi energy
        ef = 0.0 if zero_to_efermi else self._bs.efermi
        pylab.axhline(ef, linewidth=2, color='k')

        # X range (K)
        #last distance point
        x_max = data['distances'][-1]
        pylab.xlim(0, x_max)

        if self._bs.is_metal():
            # Plot A Metal
            pylab.ylim(self._bs.efermi + e_min, self._bs._efermi + e_max)
        else:
            # Semiconductor, or Insulator
            # cbm, vbm are dict with keys: kpoint, energy, is_direct
            vbm = self._bs.get_vbm()
            cbm = self._bs.get_cbm()

            e_cbm = cbm['energy'] - self._bs.efermi if zero_to_efermi else cbm['energy']
            e_vbm = cbm['energy'] - self._bs.efermi if zero_to_efermi else vbm['energy']

            print cbm['kpoint']
            if cbm['kpoint'].label is not None:
                for i in range(len(self._bs._kpoints)):
                    if(self._bs._kpoints[i].label == cbm['kpoint'].label):
                        pylab.scatter(self._bs._distance[i], e_cbm, color='r', marker='o', s=100)
                        #only draw one point
                        break
            else:
                pylab.scatter(self._bs._distance[cbm['kpoint_index']], e_cbm, color='r', marker='o', s=100)

            if vbm['kpoint'].label is not None:
                for i in range(len(self._bs._kpoints)):
                    if(self._bs._kpoints[i].label == vbm['kpoint'].label):
                        e_vbm = cbm['energy'] - self._bs.efermi if zero_to_efermi else vbm['energy']
                        pylab.scatter(self._bs._distance[i], e_vbm, color='G', marker='o', s=100)
                        #only draw one point
                        break
            else:
                pylab.scatter(self._bs._distance[vbm['kpoint_index']], e_vbm, color='g', marker='o', s=100)

            pylab.ylim(e_vbm + e_min, e_cbm + e_max)

        pylab.legend()
        if file_name is not None:
            pylab.plot()
            pylab.savefig(file_name)
        else:
            pylab.show()

    def get_ticks(self):
        """
        get all ticks and labels for a band structure plot
        """
        tick_distance = []
        tick_labels = []
        previous_label = self._bs._kpoints[0].label
        previous_branch = self._bs.get_branch_name(0)
        for i in range(len(self._bs._kpoints)):
            c = self._bs._kpoints[i]
            if(c.label != None):
                tick_distance.append(self._bs._distance[i])
                if(c.label != previous_label and previous_branch != self._bs.get_branch_name(i)):
                    label1 = c.label
                    if(label1.startswith("\\") or label1.find("_") != -1):
                        label1 = "$" + label1 + "$"
                    label0 = previous_label
                    if(label0.startswith("\\") or label0.find("_") != -1):
                        label0 = "$" + label0 + "$"
                    tick_labels.pop()
                    tick_distance.pop()
                    tick_labels.append(label0 + "$|$" + label1)
                    #print label0+","+label1
                else:
                    if(c.label.startswith("\\") or c.label.find("_") != -1):
                        tick_labels.append("$" + c.label + "$")
                    else:
                        tick_labels.append(c.label)
                previous_label = c.label
                previous_branch = self._bs.get_branch_name(i)
        return {'distance': tick_distance, 'label': tick_labels}

    def plot_compare(self, other_plotter):
        """
        plot two band structure for comparison.
        TODO: still a lot of work to do that nicely!
        """
        import pylab
        data = self.bs_plot_data
        data_other = other_plotter.bs_plot_data
        for i in range(self._nb_bands):
            pylab.plot(data['distances'], data['energy'][i], 'b-', linewidth=3)

        for i in range(self._nb_bands):
            pylab.plot(data['distances'], data_other['energy'][i], 'r--', linewidth=3)


        ticks = self.get_ticks()

        pylab.gca().set_xticks(ticks['distance'])
        pylab.gca().set_xticklabels(ticks['label'])
        pylab.xlabel('Kpoints', fontsize='large')
        pylab.ylabel('Energy(eV)', fontsize='large')
        #pylab.ylim(vbm-4,cbm+4)
        for i in range(len(ticks['label'])):
            if(ticks['label'][i] != None):
                pylab.axvline(ticks['distance'][i], color='k')
        pylab.show()
        pylab.legend()

    def plot_brillouin(self):
        import pylab as plt
        import pymatgen.command_line.qhull_caller
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(8, 8))
        ax = Axes3D(fig)
        vec1 = self._bs._lattice_rec.matrix[0]
        vec2 = self._bs._lattice_rec.matrix[1]
        vec3 = self._bs._lattice_rec.matrix[2]
        #ax.plot([0,vec1[0]],[0,vec1[1]],[0,vec1[2]],color='k')
        #ax.plot([0,vec2[0]],[0,vec2[1]],[0,vec2[2]],color='k')
        #ax.plot([0,vec3[0]],[0,vec3[1]],[0,vec3[2]],color='k')

        #make the grid
        max_x = -1000
        max_y = -1000
        max_z = -1000
        min_x = 1000
        min_y = 1000
        min_z = 1000
        list_k_points = []
        for i in[-1, 0, 1]:
            for j in [-1, 0, 1]:
                for k in [-1, 0, 1]:
                    list_k_points.append(i * vec1 + j * vec2 + k * vec3)
                    if(list_k_points[-1][0] > max_x):
                        max_x = list_k_points[-1][0]
                    if(list_k_points[-1][1] > max_y):
                        max_y = list_k_points[-1][1]
                    if(list_k_points[-1][2] > max_z):
                        max_z = list_k_points[-1][0]

                    if(list_k_points[-1][0] < min_x):
                        min_x = list_k_points[-1][0]
                    if(list_k_points[-1][1] < min_y):
                        min_y = list_k_points[-1][1]
                    if(list_k_points[-1][2] < min_z):
                        min_z = list_k_points[-1][0]

                    #ax.scatter([list_k_points[-1][0]],[list_k_points[-1][1]],[list_k_points[-1][2]])
        #plt.show()
        vertex = pymatgen.command_line.qhull_caller.qvertex_target(list_k_points, 13)
        #print vertex
        lines = pymatgen.command_line.qhull_caller.get_lines_voronoi(vertex)
        #[vertex[i][0] for i in range(len(vertex))],[vertex[i][1] for i in range(len(vertex))]+" "+str(vertex[i][2])
        #ax.scatter([vertex[i][0] for i in range(len(vertex))],[vertex[i][1] for i in range(len(vertex))],[vertex[i][2] for i in range(len(vertex))],color='r')
        for i in range(len(lines)):
            vertex1 = lines[i]['start']
            vertex2 = lines[i]['end']
            ax.plot([vertex1[0], vertex2[0]], [vertex1[1], vertex2[1]], [vertex1[2], vertex2[2]], color='k')


        for b in self._bs._branches:
            vertex1 = self._bs._kpoints[b['start_index']].cart_coords
            vertex2 = self._bs._kpoints[b['end_index']].cart_coords
            ax.plot([vertex1[0], vertex2[0]], [vertex1[1], vertex2[1]], [vertex1[2], vertex2[2]], color='r', linewidth=3)
        #plot the labelled points    

        for k in self._bs._kpoints:
            if k.label:
                label = k.label
                if k.label.startswith("\\") or k.label.find("_") != -1:
                    label = "$" + k.label + "$"
                off = 0.01
                ax.text(k.cart_coords[0] + off, k.cart_coords[1] + off, k.cart_coords[2] + off, label, color='b', size='25')
                ax.scatter([k.cart_coords[0]], [k.cart_coords[1]], [k.cart_coords[2]], color='b')

        # make ticklabels and ticklines invisible
        for a in ax.w_xaxis.get_ticklines() + ax.w_xaxis.get_ticklabels():
            a.set_visible(False)
        for a in ax.w_yaxis.get_ticklines() + ax.w_yaxis.get_ticklabels():
            a.set_visible(False)
        for a in ax.w_zaxis.get_ticklines() + ax.w_zaxis.get_ticklabels():
            a.set_visible(False)

        #ax.set_xlim3d(0.5*min_x, 0.5*max_x) 
        #ax.set_ylim3d(0.5*min_y, 0.5*max_y) 
        #ax.set_zlim3d(0.5*min_z, 0.5*max_z) 
        ax.grid(False)
        plt.show()
