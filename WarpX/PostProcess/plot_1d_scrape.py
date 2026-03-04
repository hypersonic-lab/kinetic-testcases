#!/usr/bin/env python3

import sys
import os

import matplotlib.pyplot as plt
import yt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries
from unyt import matplotlib_support


def plot_1d_scrape():

    print('------------Starting PostProcessing---------------')
    
    # Check to see if ./diags exists
    if not os.path.isdir('./diags'):
        raise RuntimeError("No Diags folder created!!")

    # Find Fields to plot from input file
    input_file_path = sys.argv[1]

    diagnostic_names = []
    particles = []
    particleBoundary = []
    
    try:
        # Get diagnostic names and species
        with open(input_file_path, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if 'diags_names' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    diagnostic_names.append(split_tmp2[1])
                if 'species_names' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    for s in split_tmp2:
                        particles.append(s)
    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    particleBoundary = list(particles) #0 = lo ; 1 = hi
    temp_part_list = list(particles)
    
    try:
        # Get diagnostic names and species
        with open(input_file_path, 'r') as file:
            # Get which species is at which boundary
            for line2 in file:
                processed_line = line2.strip()
                for par in temp_part_list:
                    if par in processed_line:
                        if 'save_particles_at_zlo' in processed_line:
                            print(f"{par}_save_at_zlo")
                            idx = temp_part_list.index(par)
                            if particleBoundary[idx] == 1: #If also had a zhi, add another
                                particleBoundary.append(0)
                                particles.append(temp_part_list[idx])
                            else:
                                particleBoundary[idx] = 0
                            print(particleBoundary)
                        if 'save_particles_at_zhi' in processed_line:
                            print(f"{par}_save_at_zhi")
                            idx = temp_part_list.index(par)
                            if particleBoundary[idx] == 0: #If also had a zlo, add another
                                particleBoundary.append(1)
                                particles.append(temp_part_list[idx])
                            else:
                                particleBoundary[idx] = 1
                            print(particleBoundary)
    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    print(f"Diagnostics files named: '{diagnostic_names}'")
    
    # List directories in diags and select newest and latest iteration
    diaglist = os.listdir(path='./diags')
    filteredList = []
    filteredNumb = []
    
    for s in diaglist:
        # Check if starts with diagnostics name (not some other file)
        if diagnostic_names[0] in s:
            # Check if old
            if "." not in s:
                filteredList.append(s)
                filteredNumb.append(float(s[4:]))

    # Select diags file to use
    sortedNumb = np.argsort(filteredList)

    fnbase = './diags/'+filteredList[sortedNumb[-1]]

    print(particles)

    # Print Data for each Particle
    for pari in range(len(particles)):
        if particleBoundary[pari] == 1: #hi boundary
            fn = fnbase + '/particles_at_zhi'
            boundary = 'zhi'
        else: # Lo boundary
            fn = fnbase + '/particles_at_zlo'
            boundary = 'zlo'
            
        print(f"Opening {fn} Diagnostic")
        
        # Read Data
        ts = OpenPMDTimeSeries(fn)
        
        times = ts.t
        bulkIterations = ts.iterations
        
        # Find time for each bulk iteration
        dt = times[1]-times[0]
        diteration = bulkIterations[1]-bulkIterations[0]
        
        ws=[] # holding array for particle weights
        stepScrapeds = [] # holding array for timesteps
        stepTimes = [] # Holding array for time of steps
        
        # Extract time information from each iteration
        for it in ts.iterations:
            [w,stepScraped] = ts.get_particle(var_list=['w','stepScraped'],species=particles[pari],iteration=it)
            stepTime = stepScraped * dt / diteration # Convert steps to times

            ws.append(w)
            stepScrapeds.append(stepScraped)
            stepTimes.append(stepTime)

        # Format properly
        scrapItr = np.concatenate((stepScrapeds))
        ws = np.concatenate((ws))
        stepts = np.concatenate((stepTimes))
        
        plot_times = np.linspace(0,times[-1])
        plot_tstep = plot_times[1]-plot_times[0]
        
        # Get rate information
        nwin = np.zeros((len(plot_times)-1,))
        for i in range(len(nwin)):
            idx = (stepts >= plot_times[i]) & (stepts < plot_times[i+1])
            nwin[i] = np.sum(ws[idx])/plot_tstep
            
        # Plot rate information
        fig, ax = plt.subplots()
        ax.scatter(plot_times[0:-1],nwin)
        ax.minorticks_on()
        ax.grid(True)
        ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
        ax.set_title(f"'{particles[pari]}' Particle Flux Through Boundary")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Particle Flux [#/s]")
                
        fig.savefig(f"particle_flux_{boundary}_{particles[pari]}.png")
        
        #fig, ax = plt.subplots()
        #ax.scatter(scrapItr,ws)
        #fig.savefig(f"test2.png")
    
   

if __name__ == "__main__":
    plot_1d_scrape()
