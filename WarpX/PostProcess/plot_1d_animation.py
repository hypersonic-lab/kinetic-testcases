#!/usr/bin/env python3

import sys
import os

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import yt
import numpy as np
from unyt import matplotlib_support


def plot_1d_animation():

    print('------------Starting PostProcessing---------------')
    
    # Check to see if ./diags exists
    if not os.path.isdir('./diags'):
        raise RuntimeError("No Diags folder created!!")

    # Find Fields to plot from input file
    input_file_path = sys.argv[1]

    diagnostic_names = []
    fields = []

    try:
        with open(input_file_path, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if 'diags_names' in processed_line:
                    split_tmp = processed_line.split()
                    diagnostic_names.append(split_tmp[-1])
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
                # Check if not just called 'diag1' or whatever
                if s != diagnostic_names[0]:
                    filteredList.append(s)
                    filteredNumb.append(float(s[4:]))

    # Select diags file to use
    sortedNumb = np.argsort(filteredList)

    # Create an animation for each field
    for field in fields:
        print(f"Gathering Time Data for '{field}'")

        fieldtdata = []
        xtdata = []
        tdata = []
        for diagt in sortedNumb:
            # Extract time data for field
            fn = './diags/'+filteredList[diagt]

            print('Processing Diagnostics: '+ fn)
            
            ds = yt.load(fn)

            tdata.append(ds.current_time.to('s'))
            
            # cutting through the y0,z0 such that we hit the max density
            ax = 0  # take a line cut along the x axis
            ray = ds.ortho_ray(ax, (0, 0))

            # Sort the ray values by 'x' so there are no discontinuities
            # in the line plot
            srt = np.argsort(ray["index", "x"])
            ray["x"].name = "X-Axis"
            ray[field].name = field

            # Store x and field data
            xtdata.append(ray["x"][srt].to('cm'))
            fieldtdata.append(ray[field][srt])

        ylim = [np.min(fieldtdata),np.max(fieldtdata)]
        # Make an animation
        with matplotlib_support:
            fig, ax = plt.subplots(figsize=(12, 8))

            def animate(i):
                data = fieldtdata[i]
                x = xtdata[i]
                ax.clear()
                ax.plot(x,data,color='tab:blue',label=f"T = {tdata[i]:.2E}")

                ax.set_ylim(ylim[0],ylim[1])
                ax.minorticks_on()
                ax.grid(True)
                ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
                ax.set_title(field)
                ax.set_xlim(np.min(ray["x"][srt]),np.max(ray["x"][srt]))
                ax.legend()                    

            ani = animation.FuncAnimation(fig,animate,frames=len(xtdata),interval=400)

            ani.save(filename=f"v1D_{field}_xweep.gif", writer="pillow")
            print(f"Saved as v1D_{field}_xweep.gif")
            
if __name__ == "__main__":
    plot_1d_animation()
