import meep as mp
import argparse
import os
import sys
from matplotlib import pyplot as plt
import pandas as pd

def simulation(params):
    """
    define the geometry of the photonic crystal cavity and parameters for Simulation
    then run the simulation   [[!!  units in microns (um) !!]]
    """

    ## settings   ############################################################
    resolution = int(params['Resolution']) # pixels/um
                   # (start with ~50 nanometer mesh for testing)
                   # (~10 nanometer mesh is a typical value for testing)
                   # (~2 nanometer mesh is a typical value for publication)
    ## variable parameters ###################################################
    a_0 = params['a']               # lattice constant (try 0.330 um)
    w = params['width']             # width of the nanobeam in unit of a
    lambda_min = params['Lam_ss']   # source minimum wavelength
    lambda_max = params['Lam_us']   # source maximum wavelength
    sim_time = params['Times']      # simulation time after source
    animate = params['Animate']     # bool value, true generates animation
    leng_Nwvg = params['leng_Nwvg'] # length of the nanobeam in unit of nwvg
    nwvg = params['Nwvg']   # number of waveguide holes in nanobeam

    NULL = params['NULL']   # bool value, false simulates with no holes
                              # (for the purpose of normalizing the flux plot)


    r_inc = 0.02      # increment of r/a      (try 0.02 um)
    r_0 = 0.35        # hole radius in unit of periodicity (try 0.35)
    h = 0.14          # waveguide height      (try 0.140 um) (exp 0.130 um)

    dair = 1.00       # air padding   # can try to reduce,
                       # should be longer than half-wavelength,
                       # one-wavelength or longer is desired
    dpml = 1.00       # PML thickness (should fix at 1 um)
    Ndef = 4          # number of defect periods   (try 4)

    ## geometry of the device ################################################
    a_taper = []    # distance between the holes in taper
    r_taper = []    # radius of the holes in the taper
    x_taper = []    # x-position of the center of the holes in the tpaer
    for i in range(Ndef+1):
        r_i = (r_0 - r_inc * (Ndef-i)) * a_0
        a_i = r_i / r_0
        a_taper.append(a_i)
        r_taper.append(r_i)
        x_taper.append(sum(a_taper)-(a_taper[i]/2))

    ## Old Design ############################
    # for i in range(Ndef+1):
    #     if i == 0:
    #         a_i = a_0
    #     else:
    #         a_i =  r_taper[-1] / 0.35
    #     r_i = (r-taper_inc*i) * a_i
    #     r_taper.append(r_i)
    #     a_taper.append(a_i)
    #########################################



    ## size of the computation cell
    sx = 2*sum(a_taper)+2*(leng_Nwvg)*a_0+a_0 # length of cell
    sy = dpml+dair+(w*a_0)+dair+dpml        # width of the simulation cell
    sz = dpml+dair+h+dair+dpml              # height of the simulation cell
    cell_size = mp.Vector3(sx,sy,sz)
    boundary_layers = [mp.PML(dpml)]

    ## material used
    nSiN = 2      # refraction index of the material, use n=2 for SiN
    SiN = mp.Medium(index=nSiN)

    ## create the band
    geometry = [mp.Block(material=SiN, center=mp.Vector3(), size=mp.Vector3(mp.inf,w*a_0,h))]

    ## add holes (waveguide) to the band
    if (NULL):
        for mm in range(nwvg):
            geometry.append(mp.Cylinder(material=mp.air, radius=r_0*a_0, height=mp.inf,
                                        center=mp.Vector3(+sum(a_taper)-a_taper[-1]/2+mm*a_0,0,0)))
            geometry.append(mp.Cylinder(material=mp.air, radius=r_0*a_0, height=mp.inf,
                                        center=mp.Vector3(-sum(a_taper)+a_taper[-1]/2-mm*a_0,0,0)))
        ## add holes (taper) to the band
        for mm in range(Ndef):
            geometry.append(mp.Cylinder(material=mp.air, radius=r_taper[mm], height=mp.inf,
                                        center=mp.Vector3(+x_taper[mm],0,0)))
            geometry.append(mp.Cylinder(material=mp.air, radius=r_taper[mm], height=mp.inf,
                                        center=mp.Vector3(-x_taper[mm],0,0)))

    ## define the source ####################################################
    fmin = 1/lambda_max
    fmax = 1/lambda_min
    fcen = 0.5*(fmin+fmax)
    df = fmax-fmin

    sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ey, center=mp.Vector3())]

    ## symmetry of the system ###############################################
    symmetries = [mp.Mirror(mp.X,+1), mp.Mirror(mp.Y,-1), mp.Mirror(mp.Z,+1)]
    
    ## define the simulation and detector objects ###########################
    sim = mp.Simulation(resolution=resolution,
                        cell_size=cell_size,
                        boundary_layers=boundary_layers,
                        geometry=geometry,
                        sources=sources,
                        dimensions=3,
                        symmetries=symmetries)

    ## for flux diagram
    freq_cavity = mp.FluxRegion(center=mp.Vector3(+sum(a_taper)+8*a_0, 0, 0),
                                size=mp.Vector3(0, (w*a_0), h))
    nfreq = 500 # number of frequencies at which to compute flux
    trans_cavity = sim.add_flux(fcen, df, nfreq, freq_cavity)
                        
                        
    ## for animation
    if (animate):
        figure = plt.figure(dpi=100)
        Animate = mp.Animate2D(fields=mp.Ey, f=figure, 
                               realtime=False, normalize=False,
                               output_plane=mp.Volume(center=mp.Vector3(),
                                                      size=mp.Vector3(sx,sy,0)))

        ## run the simulation and save the data #############################
        sim.run(mp.in_volume(mp.Volume(center=mp.Vector3(), 
                             size=mp.Vector3(sx,sy,0)),
                             mp.at_end(mp.output_epsilon, mp.output_efield_y)),
                mp.at_every(1, Animate),
                mp.after_sources(mp.Harminv(mp.Ey, mp.Vector3(), fcen, df)),
                until_after_sources=sim_time) 
        
        # save the animation
        filename = ("output/animation/animation["+str(lambda_max)+','
                                                 +str(lambda_min)+','
                                                 +str(NULL)+"].mp4")
        Animate.to_mp4(10, filename)
    else:
        ## run the simulation and save the data ##############################
        sim.run(mp.in_volume(mp.Volume(center=mp.Vector3(), 
                             size=mp.Vector3(sx,sy,0)),
                             mp.at_end(mp.output_epsilon, mp.output_efield_y)),
                mp.after_sources(mp.Harminv(mp.Ey, 
                                            mp.Vector3(0, -(w*a_0+sep)/2, 0), 
                                            fcen, df)),
                mp.after_sources(mp.Harminv(mp.Ey, 
                                            mp.Vector3(0, +(w*a_0+sep)/2, 0), 
                                            fcen, df)),
                until_after_sources=sim_time) 

    # for flux plot 
    # print out the flux spectrum
    sim.display_fluxes(trans_cavity)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-params', type=str, 
                        default='[60,0.05,0.6,0.85,True,300,3,10]',
                        help='a python string that contains the parameters')
    args = parser.parse_args()
    params_csv = pd.read_csv('parameters.csv', index_col=0)
    params = params_csv.loc[args.params]
    simulation(params)


"""
lattice constant a = 330 nm

width = 1.4a
radius = 0.35a
increment of 0.02 for the taper
update a for the taper to maintain the ratio of r/a=0.35

edge to edge distance between two bands:
50 nanometers as minimum for practical purpose
75 nanometers as minimum for practical purpose
100 nanometers should have some coupling effect
"""
