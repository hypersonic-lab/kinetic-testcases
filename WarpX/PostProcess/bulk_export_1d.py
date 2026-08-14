#!/usr/bin/env python3

import sys
import os

import pandas as pd 
import matplotlib.pyplot as plt
import yt
import numpy as np
from unyt import matplotlib_support
from openpmd_viewer import OpenPMDTimeSeries

def get_diag_prefixes(this_case_inputs = './warp_used_inputs'):
    diag_timeAveraged = 'none'
    diag_scraping = 'none'

    try:
        # Get diagnostic names and species
        with open(this_case_inputs, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if '.diag_type = TimeAveraged' in processed_line:
                    split_tmp = processed_line.split('.')
                    diag_timeAveraged = split_tmp[0]
                if '.diag_type = BoundaryScraping' in processed_line:
                    split_tmp = processed_line.split('.')
                    diag_scraping = split_tmp[0]
    except FileNotFoundError:
        print(f"Error: The file '{this_case_inputs}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return diag_timeAveraged, diag_scraping

def get_particles(input_file):
    particle_list = []

    try:
        # Get diagnostic names and species
        with open(input_file, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if 'particles.species_names = ' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    particle_list = split_tmp2
                    break
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return particle_list


def extract_scrape_data(input_file, diags_folder, output_file_name):
    data_out = {}

    # Get Particles
    particle_list = get_particles(input_file)

    boundary_loc = ['/particles_at_zhi', '/particles_at_zlo']
    bound_loc = ['zhi','zlo']

    for boundi in range(2):
        # First load zlo
        fn = diags_folder + boundary_loc[boundi]

        print(f"Opening {fn} Disgnostic")

        # Read Data
        ts = OpenPMDTimeSeries(fn)
        
        times = ts.t
        
        # Find time for each bulk iteration
        if len(times) <= 1:
            dt = times[0]
        else:
            dt = times[1]-times[0]

        for pari in range(len(particle_list)):
            ws=[] # holding array for particle weights each iteration
            wspt = [] # holding array for particle flux per iteration
            
            # Extract time information from each iteration
            try:
                for it in ts.iterations:
                    [w,stepScraped] = ts.get_particle(var_list=['w','stepScraped'],species=particle_list[pari],iteration=it)

                    ws.append(w)
                    wspt.append(np.sum(w)/dt)
            except Exception as e:
                print(e)

            data_out[f"{bound_loc[boundi]}_{particle_list[pari]}"] = np.array(wspt)

    data_out['time'] = np.array(times)

    file_name = 'density_data'

    df = pd.DataFrame(data_out)
    df.to_csv(f'{output_file_name}.csv', index=False)
    df.to_csv(f'{output_file_name}.txt', index=False)

def get_fields(input_file, diag_prefix):
    fields_list = []
    
    try:
        # Get diagnostic names and species
        with open(input_file, 'r') as file:
            for line in file:
                processed_line = line.strip()
                if f'{diag_prefix}.fields_to_plot' in processed_line:
                    split_tmp = processed_line.split('=')
                    split_tmp2 = split_tmp[-1].split()
                    fields_list = split_tmp2
                    break
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return fields_list

def extract_timeAveraged_field_data(input_file, diag_folder, diag_prefix, output_file_name):
    data_out = {}

    # Get Fields
    fields_list = get_fields(input_file, diag_prefix)

    # List directories in diags and select newest and latest iteration
    diaglist = os.listdir(diag_folder)
    filteredList = []
    filteredNumb = []

    for s in diaglist:
        # Check if starts with diagnostics name (not some other file)
        if diag_prefix in s:
            # Check if old
            if "." not in s:
                filteredList.append(s)
                filteredNumb.append(float(s[4:]))

    # Select diags file to use
    sortedNumb = np.argsort(filteredList)
    fn = diag_folder+filteredList[sortedNumb[-1]]

    print('Processing Newest Diagnostics: '+ fn)
    print('Plotting along x-axis')
    
    ds = yt.load(fn)
    ax = 0  # take a line cut along the x axis

    # cutting through the y0,z0 such that we hit the max density
    ray = ds.ortho_ray(ax, (0, 0))

    # Sort the ray values by 'x' so there are no discontinuities
    # in the line plot
    srt = np.argsort(ray["index", "x"])
    ray["x"].name = "X-Axis"

    ad = ds.all_data()

    for field in fields_list:
        print(f"Plotting '{field}'")
        ray[field].name = field

        data_out[f'{field}'] = ray[field][srt]

    data_out['x'] = ray["x"][srt].to('m')

    df = pd.DataFrame(data_out)
    df.to_csv(f'{output_file_name}.csv', index=False)
    df.to_csv(f'{output_file_name}.txt', index=False)

# User's Input
cases_path = sys.argv[1]
files_in   = os.listdir(cases_path)  
files_in.sort() 

case_inputs = 'warpx_used_inputs'

# Cycle through scenarios
for count, val in enumerate(files_in):

    # Skip if not a directory
    this_case_path = os.path.join(cases_path, val)
    if os.path.isdir(this_case_path) == False:
        continue

    case_name = val

    diags_path = os.path.join(this_case_path, 'diags/')

    # Skip if ./diags does not exist (no outputs)
    if not os.path.isdir(diags_path):
        continue

    this_case_inputs = os.path.join(this_case_path, case_inputs)

    # Find diag for TimeAveraged and Boundary Scraping from warpx_used_inputs
    diag_timeAveraged, diag_scraping = get_diag_prefixes(this_case_inputs)

    # Export Scraping Data
    scrape_output_file = f"{case_name}_scrape"
    extract_scrape_data(this_case_inputs, os.path.join(diags_path, diag_scraping), scrape_output_file)

    # Export Time Averaged Field Data
    tafields_output_file = f"{case_name}_timeAve_fields"
    extract_timeAveraged_field_data(this_case_inputs, diags_path, diag_timeAveraged, tafields_output_file)