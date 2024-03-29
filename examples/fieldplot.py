#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#    Copyright (C) 2009-2015 Ovidio Peña Rodríguez <ovidio@bytesfall.com>
#    Copyright (C) 2013-2015  Konstantin Ladutenko <kostyfisik@gmail.com>
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

# Several functions to plot field and streamlines (power flow lines).

import scattnlay
from scattnlay import fieldnlay
from scattnlay import scattnlay
import numpy as np
import cmath


def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    angle = np.arccos(np.dot(v1_u, v2_u))
    if np.isnan(angle):
        if (v1_u == v2_u).all():
            return 0.0
        else:
            return np.pi
    return angle
###############################################################################
def GetFlow3D(x0, y0, z0, max_length, max_angle, x, m, pl):
    # Initial position
    flow_x = [x0]
    flow_y = [y0]
    flow_z = [z0]
    max_step = x[-1]/3
    min_step = x[0]/2000
#    max_step = min_step
    step = min_step*2.0
    if max_step < min_step:
        max_step = min_step
    coord = np.vstack(([flow_x[-1]], [flow_y[-1]], [flow_z[-1]])).transpose()
    terms, E, H = fieldnlay(np.array([x]), np.array([m]), coord,pl=pl)
    Ec, Hc = E[0, 0, :], H[0, 0, :]
    S = np.cross(Ec, Hc.conjugate()).real
    Snorm_prev = S/np.linalg.norm(S)
    Sprev = S
    length = 0
    dpos = step
    count = 0
    while length < max_length:
        count = count + 1
        if (count>3000): # Limit length of the absorbed power streamlines
            break
        if step<max_step:
                step = step*2.0
        r = np.sqrt(flow_x[-1]**2 + flow_y[-1]**2 + flow_z[-1]**2)
        while step > min_step:
            #Evaluate displacement from previous poynting vector
            dpos = step
            dx = dpos*Snorm_prev[0];
            dy = dpos*Snorm_prev[1];
            dz = dpos*Snorm_prev[2];
            #Test the next position not to turn\chang size for more than max_angle
            coord = np.vstack(([flow_x[-1]+dx], [flow_y[-1]+dy], [flow_z[-1]+dz])).transpose()
            terms, E, H = fieldnlay(np.array([x]), np.array([m]), coord,pl=pl)
            Ec, Hc = E[0, 0, :], H[0, 0, :]
            Eth = max(np.absolute(Ec))/1e10
            Hth = max(np.absolute(Hc))/1e10
            for i in xrange(0,len(Ec)):
                if abs(Ec[i]) < Eth:
                    Ec[i] = 0+0j
                if abs(Hc[i]) < Hth:
                    Hc[i] = 0+0j
            S = np.cross(Ec, Hc.conjugate()).real
            if not np.isfinite(S).all():
                break
            Snorm = S/np.linalg.norm(S)
            diff = (S-Sprev)/max(np.linalg.norm(S), np.linalg.norm(Sprev))
            if np.linalg.norm(diff)<max_angle:
            # angle = angle_between(Snorm, Snorm_prev)
            # if abs(angle) < max_angle:
                break
            step = step/2.0
        #3. Save result
        Sprev = S
        Snorm_prev = Snorm
        dx = dpos*Snorm_prev[0];
        dy = dpos*Snorm_prev[1];
        dz = dpos*Snorm_prev[2];
        length = length + step
        flow_x.append(flow_x[-1] + dx)
        flow_y.append(flow_y[-1] + dy)
        flow_z.append(flow_z[-1] + dz)
    return np.array(flow_x), np.array(flow_y), np.array(flow_z)


###############################################################################
def GetField(crossplane, npts, factor, x, m, pl):
    """
    crossplane: XZ, YZ, XY
    npts: number of point in each direction
    factor: ratio of plotting size to outer size of the particle
    x: size parameters for particle layers
    m: relative index values for particle layers
    """
    scan = np.linspace(-factor*x[-1], factor*x[-1], npts)
    zero = np.zeros(npts*npts, dtype = np.float64)

    if crossplane=='XZ':
        coordX, coordZ = np.meshgrid(scan, scan)
        coordX.resize(npts*npts)
        coordZ.resize(npts*npts)
        coordY = zero
        coordPlot1 = coordX
        coordPlot2 = coordZ
    elif crossplane=='YZ':
        coordY, coordZ = np.meshgrid(scan, scan)
        coordY.resize(npts*npts)
        coordZ.resize(npts*npts)
        coordX = zero
        coordPlot1 = coordY
        coordPlot2 = coordZ
    elif crossplane=='XY':
        coordX, coordY = np.meshgrid(scan, scan)
        coordX.resize(npts*npts)
        coordY.resize(npts*npts)
        coordZ = zero
        coordPlot1 = coordY
        coordPlot2 = coordX
        
    coord = np.vstack((coordX, coordY, coordZ)).transpose()
    terms, E, H = fieldnlay(np.array([x]), np.array([m]), coord, pl=pl)
    Ec = E[0, :, :]
    Hc = H[0, :, :]
    P=[]
    P = np.array(map(lambda n: np.linalg.norm(np.cross(Ec[n], np.conjugate(Hc[n]))).real, range(0, len(E[0]))))

    # for n in range(0, len(E[0])):
    #     P.append(np.linalg.norm( np.cross(Ec[n], np.conjugate(Hc[n]) ).real/2 ))
    return Ec, Hc, P, coordPlot1, coordPlot2
###############################################################################
def fieldplot(x,m, WL, comment='', WL_units=' ', crossplane='XZ', field_to_plot='Pabs',npts=101, factor=2.1, flow_total=11, is_flow_extend=True, pl=-1, outline_width=1):
    Ec, Hc, P, coordX, coordZ = GetField(crossplane, npts, factor, x, m, pl)
    Er = np.absolute(Ec)
    Hr = np.absolute(Hc)
    try:
        import matplotlib.pyplot as plt
        from matplotlib import cm
        from matplotlib.colors import LogNorm
        if field_to_plot == 'Pabs':
            Eabs_data = np.resize(P, (npts, npts)).T 
            label = r'$\operatorname{Re}(E \times H^*)$'
        elif field_to_plot == 'Eabs':
            Eabs = np.sqrt(Er[ :, 0]**2 + Er[ :, 1]**2 + Er[ :, 2]**2)
            Eabs_data = np.resize(Eabs, (npts, npts)).T 
            label = r'$|E|$'
        elif field_to_plot == 'Habs':
            Habs= np.sqrt(Hr[ :, 0]**2 + Hr[ :, 1]**2 + Hr[ :, 2]**2)
            Eabs_data = np.resize(Habs, (npts, npts)).T 
            label = r'$|H|$'
        elif field_to_plot == 'angleEx':
            Eangle = np.angle(Ec[ :, 0])/np.pi*180
            Eabs_data = np.resize(Eangle, (npts, npts)).T 
            label = r'$arg(E_x)$'
        elif field_to_plot == 'angleHy':
            Hangle = np.angle(Hc[ :, 1])/np.pi*180
            Eabs_data = np.resize(Hangle, (npts, npts)).T 
            label = r'$arg(H_y)$'

        fig, ax = plt.subplots(1,1)
        # Rescale to better show the axes
        scale_x = np.linspace(min(coordX)*WL/2.0/np.pi, max(coordX)*WL/2.0/np.pi, npts)
        scale_z = np.linspace(min(coordZ)*WL/2.0/np.pi, max(coordZ)*WL/2.0/np.pi, npts)

        # Define scale ticks
        min_tick = np.amin(Eabs_data[~np.isnan(Eabs_data)])
        max_tick = np.amax(Eabs_data[~np.isnan(Eabs_data)])
        scale_ticks = np.linspace(min_tick, max_tick, 6)

        # Interpolation can be 'nearest', 'bilinear' or 'bicubic'
        ax.set_title(label)
        my_cmap = cm.jet
        if not (field_to_plot == 'angleEx' or field_to_plot == 'angleHy'):
            my_cmap.set_under('w')
        cax = ax.imshow(Eabs_data, interpolation = 'nearest', cmap = my_cmap,
                        origin = 'lower'
                        , vmin = min_tick+max_tick*1e-15, vmax = max_tick
                        , extent = (min(scale_x), max(scale_x), min(scale_z), max(scale_z))
                        #,norm = LogNorm()
                        )
        ax.axis("image")

        # Add colorbar
        cbar = fig.colorbar(cax, ticks = [a for a in scale_ticks])
        cbar.ax.set_yticklabels(['%5.3g' % (a) for a in scale_ticks]) # vertically oriented colorbar
        pos = list(cbar.ax.get_position().bounds)
        #fig.text(pos[0] - 0.02, 0.925, '|E|/|E$_0$|', fontsize = 14)
        if crossplane=='XZ':
            plt.xlabel('Z, '+WL_units)
            plt.ylabel('X, '+WL_units)
        elif crossplane=='YZ':
            plt.xlabel('Z, '+WL_units)
            plt.ylabel('Y, '+WL_units)
        elif crossplane=='XY':
            plt.xlabel('Y, '+WL_units)
            plt.ylabel('X, '+WL_units)


        # # This part draws the nanoshell
        from matplotlib import patches
        from matplotlib.path import Path
        x_edge = (x[-1], x[0])
        for xx in x_edge:
            r= xx*WL/2.0/np.pi
            s1 = patches.Arc((0, 0), 2.0*r, 2.0*r,  angle=0.0, zorder=1.8,
                             theta1=0.0, theta2=360.0, linewidth=outline_width, color='black')
            ax.add_patch(s1)
        if (crossplane=='XZ' or crossplane=='YZ') and flow_total>0:

            from matplotlib.path import Path
            scanSP = np.linspace(-factor*x[-1], factor*x[-1], npts)
            min_SP = -factor*x[-1]
            step_SP = 2.0*factor*x[-1]/(flow_total-1)
            x0, y0, z0 = 0, 0, 0
            max_length=factor*x[-1]*8
            #max_length=factor*x[-1]*4
            max_angle = np.pi/160
            if is_flow_extend:
                rg = range(0,flow_total*2+1)
            else:
                rg = range(0,flow_total)
            for flow in rg:
                if crossplane=='XZ':
                    if is_flow_extend:
                        x0 = min_SP*2 + flow*step_SP
                    else:
                        x0 = min_SP + flow*step_SP
                    z0 = min_SP
                    #y0 = x[-1]/20 
                elif crossplane=='YZ':
                    if is_flow_extend:
                        y0 = min_SP*2 + flow*step_SP
                    else:
                        y0 = min_SP + flow*step_SP
                    z0 = min_SP
                    #x0 = x[-1]/20
                flow_xSP, flow_ySP, flow_zSP = GetFlow3D(x0, y0, z0, max_length, max_angle, x, m,pl)
                if crossplane=='XZ':
                    flow_z_plot = flow_zSP*WL/2.0/np.pi
                    flow_f_plot = flow_xSP*WL/2.0/np.pi
                elif crossplane=='YZ':
                    flow_z_plot = flow_zSP*WL/2.0/np.pi
                    flow_f_plot = flow_ySP*WL/2.0/np.pi

                verts = np.vstack((flow_z_plot, flow_f_plot)).transpose().tolist()
                codes = [Path.LINETO]*len(verts)
                codes[0] = Path.MOVETO
                path = Path(verts, codes)
                #patch = patches.PathPatch(path, facecolor='none', lw=0.2, edgecolor='white',zorder = 2.7)
                patch = patches.PathPatch(path, facecolor='none', lw=1.5, edgecolor='white',zorder = 1.9)
                ax.add_patch(patch)
                #ax.plot(flow_z_plot, flow_f_plot, 'x',ms=2, mew=0.1, linewidth=0.5, color='k', fillstyle='none')

        plt.savefig(comment+"-R"+str(int(round(x[-1]*WL/2.0/np.pi)))+"-"+crossplane+"-"
#                    +field_to_plot+".png")
                    +field_to_plot+".pdf")
        plt.draw()

    #    plt.show()

        plt.clf()
        plt.close()
    finally:
        terms, Qext, Qsca, Qabs, Qbk, Qpr, g, Albedo, S1, S2 = scattnlay(np.array([x]),
                                                                         np.array([m]))
        print("Qabs = "+str(Qabs));
    #


