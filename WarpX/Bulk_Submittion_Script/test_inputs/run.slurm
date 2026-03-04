#!/bin/bash
#SBATCH --job-name testHH
#SBATCH --account=hanquist
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=8
#SBATCH --partition=cpu
#SBATCH --qos=normal
#SBATCH --time=5:00:00
cd $SLURM_SUBMIT_DIR
source ~/.bashrc
date
echo "Total MPI tasks: $SLURM_NTASKS"
echo $SLURM_SUBMIT_DIR

# Add pywarpx site-packages to PYTHONPATH
pip install --user numpy matplotlib periodictable picmistandard yt unyt openpmd_viewer openpmd-api

# This line is needed if you are running WarpX with a python file
export PYTHONPATH=$HOME/WarpX/build/lib/site-packages:$PYTHONPATH

# This line is needed if you are running WarpX with an input file as below
export PATH=$HOME/WarpX/build/bin:$PATH

# You will need to updated the executable if you run 2d/3d/RZ, change the inputs file name or run a python script (see commented out line below)
srun -n $SLURM_NTASKS warpx.1d.MPI.OMP.DP.PDP.OPMD.EB.QED inputs_1d_HH
#srun -n $SLURM_NTASKS python inputs_test_rz_secondary_ion_emission_picmi.py

date
