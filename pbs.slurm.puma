#!/bin/bash
#SBATCH --job-name=WarpX
#SBATCH --account=hanquist
#SBATCH --partition=standard
#SBATCH --mail-type=FAIL,END
#SBATCH -o %X.out
#SBATCH -e %X.err
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem-per-cpu=5gb
#SBATCH --time 1:00:00
cd $SLURM_SUBMIT_DIR
date
module load contrib
module load hpcteam/pywarpx/25.03
/contrib/hpcteam/pywarpx/env/bin/warpx.1d.MPI.OMP.DP.PDP.OPMD.EB.QED inputs_test_1d_scrape
date
