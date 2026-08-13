#!/usr/bin/env python3

import sys
import os

import matplotlib.pyplot as plt
import yt
import numpy as np
import pandas as pd
from unyt import matplotlib_support


def export_density_data():

    print('------------Extracting Field Data---------------')
    
    # Check to see if ./diags exists
    if not os.path.isdir('./diags'):
        raise RuntimeError("No Diags folder created!!")

    # Find Fields to plot from input file
    input_file_path = sys.argv[1]
    if len(sys.argv) > 2:
        diag_path = sys.argv[2]

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
    print(f"Fields to extract: '{fields}'")
    print(f"Species: {particles}")

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
    if len(sys.argv) > 2:
        fn = diag_path

    print('Processing Newest Diagnostics: '+ fn)
    
    ds = yt.load(fn)
    ax = 0  # take a line cut along the x axis

    # cutting through the y0,z0 such that we hit the max density
    ray = ds.ortho_ray(ax, (0, 0))

    # Sort the ray values by 'x' so there are no discontinuities
    # in the line plot
    srt = np.argsort(ray["index", "x"])
    ray["x"].name = "X-Axis"

    fields_out = ['x']+particles
    print(fields_out)

    data_out = np.zeros((len(fields_out),len(ray["x"])))
    data_out[0] = ray["x"][srt].to('m')

    qe = 1.60217663E-19 #elementary charge
    #ion data
    for i in range(len(particles)):
        try:
            data_out[i+1] = np.abs(ray[f'rho_{particles[i]}'][srt]) / qe
            fields_out[i+1] = particles[i]
        except Exception as e:
            print(e)


    if len(sys.argv) > 3:
        file_name = f"density_data_{sys.argv[3]}"
    else:
        file_name = 'density_data'

    df = pd.DataFrame(data_out.T, columns=fields_out)
    df.to_csv(f'{file_name}.csv', index=False)
    df.to_csv(f'{file_name}.txt', index=False)


if __name__ == "__main__":
    export_density_data()
