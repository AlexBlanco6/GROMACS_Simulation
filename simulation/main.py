#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
from src.utils import  save_config, load_data, find_molecules_files
from src.files_creation_functions import add_plumed_file, create_plumed_run_file, create_run_file,  minim_sim_run_file
from src.modify_gromacs_files import same_waters

start = time.time()

# Load data from json file
config, cv, n, dir_name, data_dir, ligand, em_file, prod_file, topology_file, host, orientation, direction, meta_file, barrier, height, time_sim, environment, small_run, plumed_enabled, small_run_file = load_data("config.json")

# get molecules structure files (.pdb or .gro)
host_ext = find_molecules_files(data_dir, host)
ligand_ext= find_molecules_files(data_dir, ligand)

# get directory paths
output_dir = os.path.join(data_dir, "output", f"orientation_{orientation}", direction)
path = os.path.join(output_dir, dir_name)


######## SYSTEM CREATION (MERGE/MOVE MOLECULES, SOLVATE...) #######

# First step, create, merge and solvate system
for i,j in enumerate(cv):
    try:
        meta_name = f"{i}"
        subprocess.run(["./src/first_plumed.sh", host, ligand, dir_name, meta_name, f"{j}", topology_file, output_dir, data_dir, f"{orientation}", direction, host_ext, ligand_ext], check=True)
    except subprocess.CalledProcessError as e:
        print(">>> Error in first process")


# Second step, change the number of water molecules in order to have the same in all walkers and run minimization 
for i, _ in enumerate(cv):
    try:
        meta_name = f"{i}"
        n_atoms = same_waters(output_dir, dir_name, n, "merged_solv.gro", "topol")  # get the number of total atoms
        subprocess.run(["sbatch", "src/exec_prod.sh", output_dir, data_dir, dir_name, meta_name, em_file], check = True)
    except subprocess.CalledProcessError as e:
        print(">>> Error adding waters or sending minimization file")



######## FILES CREATION (PLUMED, RUN FILES) #######

# Create plumed and run.sh files for simulation, two cases: 1 and > 1 walkers.
if n != 1:
    plumed_file = add_plumed_file(output_dir, dir_name,  data_dir, barrier, height, meta_file, orientation)
    create_plumed_run_file(output_dir, n, plumed_file, dir_name, time_sim, environment)
    if small_run == True:
        minim_sim_run_file(output_dir, dir_name, n)
    else: 
        pass
else:
    if plumed_enabled == True:
        plumed_file = add_plumed_file(output_dir, dir_name,  data_dir, barrier, height, meta_file, orientation)
    else:
        pass
    create_run_file(output_dir, dir_name, ["test","test"], plumed_enabled)


# save json in the directory to store data
save_config(output_dir, config, dir_name)


# makeindex_command = [
#     f"echo -e 'a 1-{n_atoms}\\n"
#     "name 0 System\\n"
#     "q' | "
#     "/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx make_ndx -f merged_solv_ions2.gro -n newindex.ndx -o newindex.ndx"
# ]



######## PRODUCTION #######


# production commnad without small run 
prod_command = [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
     grompp -f {data_dir}/mdp_files/{prod_file}.mdp -c em.gro -p topol2.top -o topol.tpr -maxwarn 2 -r em.gro"]# -n newindex.ndx"]


# commands for production with small run minimization
minim_command = [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
     grompp -f {data_dir}/mdp_files/{small_run_file}.mdp -c em.gro -p topol2.top -o topol_min.tpr -maxwarn 2 -r em.gro"] # -n newindex.ndx"]

prod_command_min = [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
     grompp -f {data_dir}/mdp_files/{prod_file}.mdp -c topol_min.gro -p topol2.top -o topol.tpr -maxwarn 2 -r topol_min.gro"] # -n newindex.ndx"]


# Send production or/and small run if chosen
for i, _ in enumerate(cv):
    em_path = os.path.join(path, f"{i}", "em.gro")
    while not os.path.isfile(em_path): # wait while the minimization from the second step is not finished for each walker
        print(f"Waiting for em.gro file in directory {i}")
        time.sleep(60)             # wait 1 minute before checking again, you can change to more or less time 
                                   # depends on CESGAs queues

    print(f"Found em.gro file in {dir_name} directory")    
    try:
        os.chdir(os.path.join(path, f"{i}"))      # when foun, execute production 

        if small_run == True: # run small minimization before production

            subprocess.run(minim_command, shell=True, executable="/bin/bash")
            subprocess.run(["sbatch","minim_sim.sh"], check = True)
           
        else:

            subprocess.run(prod_command, shell=True, executable="/bin/bash") # run production directly when no small run is activated

    except subprocess.CalledProcessError as e:
        print(">>> Error minimizing")


# wait until the small run is finished for all walkers and start production
if small_run == True:
    for i, _ in enumerate(cv):
        topol_path = os.path.join(path, f"{i}", "topol_min.gro")
        while not os.path.isfile(topol_path): # wait while the minimization from the second step is not finished for each walker
            print(f"Waiting for topol.gro file in directory {i}")
            time.sleep(120)             # wait 1 minute before checking again, you can change to more or less time 
                                    # depending on CESGAs queues

        print(f"Found topol.gro file in {dir_name} directory")    
        try:
            os.chdir(os.path.join(path, f"{i}"))      # when found, execute production 
            subprocess.run(prod_command_min, shell=True, executable="/bin/bash")
    
        except subprocess.CalledProcessError as e:
            print(">>> Error in inter minimization")



######## SIMULATION #######

# go to the output directory, depens on the number of walkers, 1 or > 1
if n != 1:
    os.chdir(path)
else:
    os.chdir(os.path.join(path, f"{0}"))

# print(path)


# send the simulation with sbatch run.sh
try:
    print(">>> Sending run file...")
    subprocess.run(["sbatch","run.sh"], check = True)
except subprocess.CalledProcessError as e:
    print(">>> Run file not executed")

# print elapsed time of all process
print(f">>> Finished, elapsed time: {time.time()-start}")
