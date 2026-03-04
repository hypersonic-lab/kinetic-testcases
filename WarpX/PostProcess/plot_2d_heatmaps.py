#!/usr/bin/env python3

import sys
import os

import matplotlib.pyplot as plt
import yt
import numpy as np
from unyt import matplotlib_support


def plot_2d_heatmaps():

    print('------------Starting PostProcessing---------------')
    
    # Check to see if ./diags exists
    if not os.path.isdir('./diags'):
        raise RuntimeError("No Diags folder created!!")

    # Find Fields to plot from input file
    input_file_path = sys.argv[1]

    diagnostic_names = []
    fields = []
    particles = []

    try:
        with open(input_file_path, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if 'diags_names' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    print(split_tmp2)
                    diagnostic_names.append(split_tmp2[0])
                if 'species_names' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    for s in split_tmp2:
                        particles.append(s)
                if 'fields_to_plot' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    for s in split_tmp2:
                        fields.append(s)
                    #diagnostic_names.append(splot_tmp)
                # You can assign parts of the line to variables here
    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"Diagnostics files named: '{diagnostic_names}'")
    print(f"Fields to plot: '{fields}'")

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
    fn = './diags/'+filteredList[sortedNumb[-1]]

    print('Processing Newest Diagnostics: '+ fn)
    print('Plotting along x-axis')
    
    ds = yt.load(fn)
    ax = 1  # take a line cut along the x axis

    # cutting through the y0,z0 such that we hit the max density
    ray = ds.ortho_ray(ax, (0, 0))

    # Sort the ray values by 'y' (z-axis in2d) so there are no discontinuities
    # in the line plot
    srt = np.argsort(ray["index", "y"])
    ray["y"].name = "z-Axis"

    ad = ds.all_data()

    with matplotlib_support:
        # Loop over each Field and plot them
        #for field in fields:
            slc = yt.SlicePlot(ds, "z", ('boxlib', 'phi'),center=[2.5e-5, 2e-4, .5])
            slc.set_log(('boxlib', 'phi'),False)
            slc.save()


if __name__ == "__main__":
    plot_2d_heatmaps()
