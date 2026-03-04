#!/opt/homebrew/bin/python3
'''
    Date:   12/12/2022
    Author: Martin E. Liza
    File:   main.py
    Def:    Creates multiple SU2 cases with different AoA and 
            Mach numbers and runs them in an HPC.

    Author		    Date		Revision
    --------------------------------------------------------
    Martin E. Liza	09/13/2022	Initial version.
    Martin E. Liza  12/12/2022  Cleaned up and add comments.
    Finn E. O'Brien 03/04/2026  Ported to WarpX
'''
import run_simulations 
import argparse
import os 

# User inputs 
voltage         = [2, 3]                   #[V]
domainLength    = 0.0011                   #[m] Domain Length

input_main      = 'inputs_1d_HH_test'           #main input file to copy 
abs_path        = '/scratch/gautschi/obrienf/HaraHanquist/bulk_trial'  #path were cases are created

# Loads argparse class 
parser = argparse.ArgumentParser() 


'''
 Iterates through mach numebrs and AoA. To iterate through 
 temperature and pressure two additional for loops will need to be added. 
'''
for i in voltage:
        # Load classes 
    args   = parser.parse_args() 

    # Set attibuts 
    setattr(args, 'voltage', [i])  
    setattr(args, 'outName', [f'V{i}']) 
    setattr(args, 'domainLength', [domainLength])
    setattr(args, 'absOutPath', [abs_path]) 
    setattr(args, 'inputMain', [input_main]) 

    # Create cases and modify SU2 input files (*.cfg) 
    run_simulations.create_case(args) 

    #  Modify slurm or pbs scripts   
    run_simulations.mod_run_HPC(args, abs_path=abs_path)

    # Run simulations using a pbs or slurm file  
    run_simulations.run_CFD(args, local_flag=False, hpc_flag='slurm') 

    # Destructures, free memory  
    del args 
