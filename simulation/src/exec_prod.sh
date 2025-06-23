#!/bin/bash
#SBATCH -J walker_em       # Job name
#SBATCH -t 0:02:00         # Time limit
#SBATCH --mem=500MB           # Memory per node
#SBATCH -c 64              # Number of cores
#SBATCH -o out_prod_%j.out   # Output log


module purge
#module load cesga/2022 gcc/system openmpi/4.1.4 gromacs/2024.2-PLUMED-2.9.2
module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

cd "$1/$3/$4"


echo "Running EM in directory: $4"

# Minimize system
srun gmx grompp -f "$2/mdp_files/$5.mdp" -c merged_solv_ions2.gro -p topol2.top -o em.tpr -maxwarn 1  -r merged_solv_ions2.gro
srun gmx_mpi mdrun -v -deffnm em