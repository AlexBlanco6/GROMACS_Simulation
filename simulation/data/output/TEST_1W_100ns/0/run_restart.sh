#!/bin/bash
#SBATCH -J TEST_1W_100ns      # Job name
#SBATCH -t 6:00:00        # Maximum execution time (e.g., 1 hour) - ADJUST
#SBATCH --mem=2G         # Memory 
#SBATCH -n 1              # Number of MPI tasks (1 is sufficient for this small system)
#SBATCH -c 64               # Number of cores per task (OpenMP threads)
#SBATCH --output=metad_%j.log # Standard output/error file
#SBATCH --signal=TERM@120

# Load necessary modules
module purge

module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

srun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -plumed ../plumedrestart.dat -ntomp ${SLURM_CPUS_PER_TASK:-1}

if ! [ -f topol.gro ]; then
    module purge
    sbatch -d singleton run_restart.sh
fi 
