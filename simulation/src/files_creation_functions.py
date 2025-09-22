#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os 


def add_plumed_file(out, output_dir, data_dir, barrier, meta_file, orientation):

    """ 
    Modify and add plumed file to the simulation from path/data/files

    Args:
        out (str): The base directory where the output folder will be created.
        output_dir (str): The name of the directory we chose.
        data_dir (str): The base directory where the data folder is located.
        barrier (float): Barrier height for metadynamics.
        meta_file (str): The plumed method we want to use.
        orientation (str): The orientation we want to use.
    Returns:    
        list: With the plumed files names ex. [metadynamics.dat, metadynamicsrestart.dat]
    """
    
    output_path = os.path.join(out, output_dir)
    restart = ("NO", "YES")
    
    path = os.path.join(data_dir, "files")
    file_name = [meta_file + "_" + orientation + ".dat", meta_file + "_" + orientation + "restart.dat"]
    file_path = os.path.join(path, file_name[0])

    for ff, restart_t in zip(file_name,restart):
        
        replacements = {
                "FILE=":         f"FILE={output_path}/HILLS",
                "STATE_WFILE=":  f"STATE_WFILE={output_path}/STATE",
                "RESTART=":      f"RESTART={restart_t}",
                "BARRIER=":         f"BARRIER={barrier}",
            }
        script = """"""
        with open(file_path, "r") as file:
            for line in file:
                if line.strip().startswith("METAD") or line.strip().startswith("opes"):
                    parts = line.split()
                    new_parts = []
                    for part in parts:
                        for key, replacement in replacements.items():
                            if part.startswith(key):
                                new_parts.append(replacement)
                                break
                        else:
                            new_parts.append(part)
                    
                    new_line = " ".join(new_parts) + "\n"
                    script += new_line
                else:
                    script += line

        with open(os.path.join(output_path, ff), "w") as f:
            f.write(script)

    return file_name

def create_plumed_run_file(out, n_mpi, method_files, dir_name, time, environment):

    """ 
    Create .sh files to run simulation, run.sh and run_restart.sh

    Args:
        out (str): The base directory where the output folder will be created.
        n_mpi (float/int): Number of walkers
        method_files (list): plumed files names list
        dir_name (str): The name of the directory we chose.
        time (str): Time for the simulation.
        environment (str): Environment to run the analysis script.
    Returns:    
        None:The function creates two .sh files to run the simulation
    """

    n_mpi = 2 if n_mpi == 1 else n_mpi

    run_file = ["run.sh" , "run_restart.sh"]
    for (i,r_file) , file_ in zip(enumerate(run_file),method_files):
        output_file = os.path.join(out, dir_name, r_file)
        sequence = " ".join(str(i) for i in range(n_mpi))
            
        sbatch_script = f"""#!/bin/bash
#SBATCH -J  {dir_name}  # Job name
#SBATCH -t {time}        # Maximum execution time (e.g., 1 hour) - ADJUST
#SBATCH --mem=8G         # Memory 
#SBATCH --nodes= {n_mpi/2}   
#SBATCH --ntasks-per-node= 4 
#SBATCH -n   {int(n_mpi)}             # Number of MPI tasks (1 is sufficient for this small system)
#SBATCH -c 16               # Number of cores per task (OpenMP threads)
#SBATCH --output=metad_%j.log # Standard output/error file
#SBATCH --signal=TERM@120

# Load necessary modules
module purge

module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

srun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -multidir {sequence} -plumed ../{file_} -ntomp ${{SLURM_CPUS_PER_TASK:-1}}
"""

        if i == 0:
            sbatch_script +="\nmodule purge\nsbatch -d singleton run_restart.sh"
        else:
            sbatch_script += f"""
\nif ! [ -f {int(n_mpi-1)}/topol.gro ]; then
    module purge
    sbatch -d singleton run_restart.sh
fi 

\nif [ -f {int(n_mpi-1)}/topol.gro ]; then
    {environment} ../../../../../src/analysis/make_analysis.py "$(pwd)"
fi
"""
        
        with open(output_file, "w") as f:
            f.write(sbatch_script)


def create_run_file(out, output_dir, method_files, plumed_enabled):

    """ 
    Create .sh files to run simulation, run.sh and run_restart.sh, the same but for 1 walker

    Args:
        out (str): The base directory where the output folder will be created.
        n_mpi (float/int): Number of walkers
        method_files (list): plumed files names list
        output_dir (str): The name of the directory we chose.
        config (dir): Directory with the data we provided on the json file.
    Returns:    
        None:The function creates two .sh files to run the simulation
    """

    
    run_file = ["run.sh" , "run_restart.sh"]
    for (i,r_file) , file_ in zip(enumerate(run_file),method_files):
        output_file = os.path.join( out, output_dir, "0", r_file)
        sbatch_script = f"""#!/bin/bash
#SBATCH -J {output_dir}      # Job name
#SBATCH -t 6:00:00        # Maximum execution time (e.g., 1 hour) - ADJUST
#SBATCH --mem=2G         # Memory 
#SBATCH -n 1              # Number of MPI tasks (1 is sufficient for this small system)
#SBATCH -c 64               # Number of cores per task (OpenMP threads)
#SBATCH --output=metad_%j.log # Standard output/error file
#SBATCH --signal=TERM@120

# Load necessary modules
module purge

module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0
"""
    
        if plumed_enabled == True:
            sbatch_script+= f"""\nsrun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -plumed ../{file_} -ntomp ${{SLURM_CPUS_PER_TASK:-1}}"""
        else:
            sbatch_script+= f"""\nsrun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -ntomp ${{SLURM_CPUS_PER_TASK:-1}}"""

        if i == 0:
            sbatch_script +="\nmodule purge\nsbatch -d singleton run_restart.sh"
        else:
            sbatch_script += f"""
\nif ! [ -f topol.gro ]; then
    module purge
    sbatch -d singleton run_restart.sh
fi 
"""
        with open(output_file, "w") as f:
            f.write(sbatch_script)

def minim_sim_run_file(out, output_dir, n):

    """ 
    Create .sh files to run simulation, run.sh and run_restart.sh

    Args:
        out (str): The base directory where the output folder will be created.
        n_mpi (float/int): Number of walkers
        method_files (list): plumed files names list
        output_dir (str): The name of the directory we chose.
        n (int): Number of walkers
    Returns:    
        None:The function creates two .sh files to run the simulation
    """

    for i in range(n):
        output_file = os.path.join(out, output_dir, f"{i}", "minim_sim.sh")
    
            
        sbatch_script = f"""#!/bin/bash
#SBATCH -J  {i}  # Job name
#SBATCH -t 0:06:00       # Maximum execution time (e.g., 1 hour) - ADJUST
#SBATCH --mem=500MB         # Memory 
#SBATCH --ntasks-per-node=1  
#SBATCH -n 1              # Number of MPI tasks (1 is sufficient for this small system)
#SBATCH -c 32               # Number of cores per task (OpenMP threads)
#SBATCH --output=inter_%j.log # Standard output/error file


# Load necessary modules
module purge

module load cesga/2020 gcc/system openmpi/4.0.5_ft3_cuda gromacs/2021.4-plumed-2.8.0

srun gmx_mpi mdrun -v -cpi topol_min.cpt -deffnm topol_min 

nmodule purge
sbatch -d singleton run_restart.sh"
"""
        
        with open(output_file, "w") as f:
            f.write(sbatch_script)
            