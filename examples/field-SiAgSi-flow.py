#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#    Copyright (C) 2009-2015 Ovidio Peña Rodríguez <ovidio@bytesfall.com>
#
#    This file is part of python-scattnlay
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    The only additional remark is that we expect that all publications
#    describing work using this software, or all commercial products
#    using it, cite the following reference:
#    [1] O. Pena and U. Pal, "Scattering of electromagnetic radiation by
#        a multilayered sphere," Computer Physics Communications,
#        vol. 180, Nov. 2009, pp. 2348-2354.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This test case calculates the electric field in the 
# E-k plane, for an spherical Si-Ag-Si nanoparticle. Core radius is 17.74 nm,
# inner layer 23.31nm, outer layer 22.95nm. Working wavelength is 800nm, we use
# silicon epsilon=13.64+i0.047, silver epsilon= -28.05+i1.525

import scattnlay
from scattnlay import fieldnlay
from scattnlay import scattnlay
import numpy as np
import cmath


def get_index(array,value):
    idx = (np.abs(array-value)).argmin()
    return idx

#Ec = np.resize(Ec, (npts, npts)).T


def GetFlow(scale_x, scale_z, Ec, Hc, a, b, nmax):
    # Initial position
    flow_x = [a]
    flow_z = [b]
    for n in range(0, nmax):
        #Get the next position
        #1. Find Poynting vector and normalize it
        x_pos = flow_x[-1]
        z_pos = flow_z[-1]
        x_idx = get_index(scale_x, x_pos)
        z_idx = get_index(scale_z, z_pos)
        S=np.cross(Ec[npts*z_idx+x_idx], np.conjugate(Hc[npts*z_idx+x_idx]) ).real
        Snorm=S/np.linalg.norm(S)
        #2. Evaluate displacement = half of the discrete and new position
        dpos = abs(scale_z[0]-scale_z[1])/4.0
        dx = dpos*Snorm[0]
        dz = dpos*Snorm[2]
        x_pos = x_pos+dx
        z_pos = z_pos+dz
        #3. Save result
        flow_x.append(x_pos)
        flow_z.append(z_pos)
    return flow_x, flow_z



epsilon_Si = 13.64 + 0.047j
epsilon_Ag = -28.05 + 1.525j

# epsilon_Si = 2.0 + 0.047j
# epsilon_Ag = -2.0 + 1.525j

# air = 1
# epsilon_Si = air*2
# epsilon_Ag = air*2


index_Si = np.sqrt(epsilon_Si)
index_Ag = np.sqrt(epsilon_Ag)

print(index_Si)
print(index_Ag)
# # Values for 800 nm, taken from http://refractiveindex.info/
# index_Si = 3.69410 + 0.0065435j
# index_Ag = 0.18599 + 4.9886j

WL=800 #nm
core_width = 17.74 #nm Si
inner_width = 23.31 #nm Ag
outer_width = 22.95 #nm  Si

core_r = core_width
inner_r = core_r+inner_width
outer_r = inner_r+outer_width

# n1 = 1.53413
# n2 = 0.565838 + 7.23262j
nm = 1.0

x = np.ones((1, 3), dtype = np.float64)
x[0, 0] = 2.0*np.pi*core_r/WL
x[0, 1] = 2.0*np.pi*inner_r/WL
x[0, 2] = 2.0*np.pi*outer_r/WL

m = np.ones((1, 3), dtype = np.complex128)
m[0, 0] = index_Si/nm
m[0, 1] = index_Ag/nm
m[0, 2] = index_Si/nm

print "x =", x
print "m =", m

npts = 241

factor=2.2
scan = np.linspace(-factor*x[0, 2], factor*x[0, 2], npts)

coordX, coordZ = np.meshgrid(scan, scan)
coordX.resize(npts*npts)
coordZ.resize(npts*npts)
coordY = np.zeros(npts*npts, dtype = np.float64)

coord = np.vstack((coordX, coordY, coordZ)).transpose()

terms, Qext, Qsca, Qabs, Qbk, Qpr, g, Albedo, S1, S2 = scattnlay(x, m)
terms, E, H = fieldnlay(x, m, coord)
Er = np.absolute(E)
Hr = np.absolute(H)

# |E|/|Eo|
Eabs = np.sqrt(Er[0, :, 0]**2 + Er[0, :, 1]**2 + Er[0, :, 2]**2)
Ec = E[0, :, :]
Hc = H[0, :, :]
Eangle = np.angle(E[0, :, 0])/np.pi*180

P=[]
for n in range(0, len(E[0])):
    P.append(np.linalg.norm( np.cross(Ec[n], np.conjugate(Hc[n]) ).real/2 ))

Habs= np.sqrt(Hr[0, :, 0]**2 + Hr[0, :, 1]**2 + Hr[0, :, 2]**2)
Hangle = np.angle(H[0, :, 1])/np.pi*180



try:
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import LogNorm

    min_tick = 0.0
    max_tick = 1.0

    # Eabs_data = np.resize(P, (npts, npts)).T
    Eabs_data = np.resize(Eabs, (npts, npts)).T
    # Eangle_data = np.resize(Eangle, (npts, npts)).T
    # Habs_data = np.resize(Habs, (npts, npts)).T
    # Hangle_data = np.resize(Hangle, (npts, npts)).T

    fig, ax = plt.subplots(1,1)#, sharey=True, sharex=True)
    #fig.tight_layout()
    # Rescale to better show the axes
    scale_x = np.linspace(min(coordX)*WL/2.0/np.pi/nm, max(coordX)*WL/2.0/np.pi/nm, npts)
    scale_z = np.linspace(min(coordZ)*WL/2.0/np.pi/nm, max(coordZ)*WL/2.0/np.pi/nm, npts)

    # Define scale ticks
    min_tick = min(min_tick, np.amin(Eabs_data))
    max_tick = max(max_tick, np.amax(Eabs_data))
    #max_tick = 5
    # scale_ticks = np.power(10.0, np.linspace(np.log10(min_tick), np.log10(max_tick), 6))
    scale_ticks = np.linspace(min_tick, max_tick, 11)

    # Interpolation can be 'nearest', 'bilinear' or 'bicubic'
    ax.set_title('Eabs')
    cax = ax.imshow(Eabs_data, interpolation = 'nearest', cmap = cm.jet,
                    origin = 'lower'
                    , vmin = min_tick, vmax = max_tick
                    , extent = (min(scale_x), max(scale_x), min(scale_z), max(scale_z))
                    #,norm = LogNorm()
                    )
    ax.axis("image")

    # Add colorbar
    cbar = fig.colorbar(cax, ticks = [a for a in scale_ticks])
    cbar.ax.set_yticklabels(['%5.3g' % (a) for a in scale_ticks]) # vertically oriented colorbar
    pos = list(cbar.ax.get_position().bounds)
    fig.text(pos[0] - 0.02, 0.925, '|E|/|E$_0$|', fontsize = 14)

    plt.xlabel('Z, nm')
    plt.ylabel('X, nm')

    # This part draws the nanoshell
    from matplotlib import patches
    s1 = patches.Arc((0, 0), 2.0*core_r, 2.0*core_r,  angle=0.0, zorder=2,
                     theta1=0.0, theta2=360.0, linewidth=1, color='black')
    s2 = patches.Arc((0, 0), 2.0*inner_r, 2.0*inner_r, angle=0.0, zorder=2,
                     theta1=0.0, theta2=360.0, linewidth=1, color='black')
    s3 = patches.Arc((0, 0), 2.0*outer_r, 2.0*outer_r, angle=0.0, zorder=2,
                     theta1=0.0, theta2=360.0, linewidth=1, color='black')
    ax.add_patch(s1)
    ax.add_patch(s2) 
    ax.add_patch(s3) 

    from matplotlib.path import Path
    #import matplotlib.patches as patches

    flow_total = 21
    for flow in range(0,flow_total):
        flow_x, flow_z = GetFlow(scale_x, scale_z, Ec, Hc,
                                 min(scale_x)+flow*(scale_x[-1]-scale_x[0])/(flow_total-1),
                                                    min(scale_z), npts*12)
        verts = np.vstack((flow_z, flow_x)).transpose().tolist()
        codes = [Path.CURVE4]*len(verts)
        #codes = [Path.LINETO]*len(verts)
        codes[0] = Path.MOVETO
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor='none', lw=1, edgecolor='white')
        ax.add_patch(patch)

 
    plt.savefig("SiAgSi-flow.png")
    plt.draw()

    plt.show()

    plt.clf()
    plt.close()
finally:
    print("Qabs = "+str(Qabs));
#


