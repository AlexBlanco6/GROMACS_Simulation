#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
from src.utils import add_plumed_file, save_config, create_plumed_run_file, create_run_file, load_data
from src.modify_gromacs_files import same_waters

start = time.time()

# Load data from json file
config, cv, n, dir_name, data_dir, output_dir, ligand, em_file, prod_file, topology_file, host = load_data("config.json")

# First step, create, merge and solvate system
for i,j in enumerate(cv):
    try:
        meta_name = f"{i}"
        subprocess.run(["./src/first_plumed.sh", host, ligand, dir_name, meta_name, f"{j}", topology_file, output_dir, data_dir], check=True)
    except subprocess.CalledProcessError as e:
        print("Error in first process")

# Second step, change the number of water molecules in order to have the same in all walkers and run minimization 
for i, _ in enumerate(cv):
    try:
        meta_name = f"{i}"
        same_waters(output_dir, dir_name, n, "merged_solv.gro", "topol")
        subprocess.run(["sbatch", "src/exec_prod.sh", output_dir, data_dir, dir_name, meta_name, em_file], check = True)
    except subprocess.CalledProcessError as e:
        print("Error adding waters or sending minimization sh")

# get directory path
path = os.path.join(output_dir, dir_name)

# Create plumed and run.sh files for simulation, two cases: 1 and > 1 walkers.
if n != 1:
    plumed_file = add_plumed_file(output_dir, dir_name, config)
    create_plumed_run_file(output_dir, n, plumed_file, dir_name, config)
else:
    plumed_file = add_plumed_file(output_dir, dir_name, config)
    create_run_file(output_dir, n, dir_name, plumed_file, config)

# save json in the directory to store data
save_config(output_dir, config, dir_name)

# command for running production and getting the .tpr
prod_command = [f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/gromacs/2021.4-plumed-2.8.0/bin/gmx \
     grompp -f {data_dir}/mdp_files/{prod_file}.mdp -c em.gro -p topol2.top -o topol.tpr -maxwarn 2 -r em.gro"]


for i, _ in enumerate(cv):
    em_path = os.path.join(path, f"{i}", "em.gro")
    while not os.path.isfile(em_path): # wait while the minimization from the second step is not finished for each walker
        print(f"Waiting for em.gro file in directory {i}")
        time.sleep(60)             # wait 1 minute before checking again, you can change to more or less time 
                                   # depending on CESGAs queues

    print(f"Found em.gro file in {dir_name} directory")    
    try:
        os.chdir(os.path.join(path, f"{i}"))      # when foun, execute production 
        subprocess.run(prod_command, shell=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print("Error minimizing")


# delete output files from minimization
try:
    print(">>> Deleting output files...")  
    subprocess.run("find . -type f -name 'out*' -exec rm -f {} \;", shell=True,check=True)
except subprocess.CalledProcessError as e:
    print("Files not deleted")

# go to the output directory, depens on the number of walkers, 1 or > 1
if n != 1:
    os.chdir(path)
else:
    os.chdir(os.path.join(path, f"{0}"))
    
# send the simulation with sbatch run.sh
try:
    print(">>> Sending run file...")
    subprocess.run(["sbatch","run.sh"], check = True)
except subprocess.CalledProcessError as e:
    print("Run file not executed")

# print elapsed time of all process
print(f">>> Finished, elapsed time: {time.time()-start}")
