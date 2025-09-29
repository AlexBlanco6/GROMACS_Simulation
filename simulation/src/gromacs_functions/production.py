#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import os
import subprocess



######## PRODUCTION  COMMANDS #######


# production commnad without small run
def prod_command(data_dir, prod_file):
    return [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
         grompp -f {data_dir}/mdp_files/{prod_file}.mdp -c em.gro -p topol2.top -o topol.tpr -maxwarn 2 -r em.gro"]# -n newindex.ndx"]



# commands for production with small run minimization
def minim_command(data_dir, small_run_file):
    return [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
         grompp -f {data_dir}/mdp_files/{small_run_file}.mdp -c em.gro -p topol2.top -o topol_min.tpr -maxwarn 2 -r em.gro"] # -n newindex.ndx"]


def prod_command_min(data_dir, prod_file):
    return [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
         grompp -f {data_dir}/mdp_files/{prod_file}.mdp -c topol_min.gro -p topol2.top -o topol.tpr -maxwarn 2 -r topol_min.gro"] # -n newindex.ndx"]


# create index file with all atoms, rigid atoms (central heavy atoms ,from hexagons) and other (host + ligand)
def makeindex_command(n_atoms):
    return [ f"echo -e 'a 1-{n_atoms} \\n" 
    "name 0 System \\n"
    " a 3 4 5 8 25 28 47 48 51 56 59 80 \\n"
    " name 1 rigidatoms \\n "
    "! r SOL \\n"
    " name 2 Other \\n"
    "q' |" 
    "/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx make_ndx -f merged_solv_ions2.gro -n newindex.ndx -o newindex.ndx"]

