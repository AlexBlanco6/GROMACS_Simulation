#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os 
import json

def add_plumed_file(out, output_dir, config):

    """ 
    Modify and add plumed file to the simulation from path/data/files

    Args:
        out (str): The base directory where the output folder will be created.
        output_dir (str): The name of the directory we chose.
        config (dir): Directory with the data we provided on the json file.
    Returns:    
        list: With the plumed files names ex. [metadynamics.dat, metadynamicsrestart.dat]
    """
    
    output_path = os.path.join(out, output_dir)
    restart = ("NO", "YES")
    
    with open("config.json", "r") as f:
        config = json.load(f)

    path = os.path.join(config["data_dir"], "files")
    bias = config["bias"]
    height = config["height"]
    meta_file = config["plumed"]["method"]
    file_name = [meta_file + ".dat", meta_file + "restart.dat"]
    file_path = os.path.join(path, file_name[0])

    for ff, restart_t in zip(file_name,restart):
        
        replacements = {
                "FILE=":         f"FILE={output_path}/HILLS",
                "STATE_WFILE=":  f"STATE_WFILE={output_path}/STATE",
                "RESTART=":      f"RESTART={restart_t}",
                "BIAS=":         f"BIAS={bias}",
                "HEIGHT=":       f"HEIGHT={height}",
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

def create_plumed_run_file(out, n_mpi, method_files, output_dir, config):

    """ 
    Create .sh files to run simulation, run.sh and run_restart.sh

    Args:
        out (str): The base directory where the output folder will be created.
        n_mpi (float/int): Number of walkers
        method_files (list): plumed files names list
        output_dir (str): The name of the directory we chose.
        config (dir): Directory with the data we provided on the json file.
    Returns:    
        None:The function creates two .sh files to run the simulation
    """

    n_mpi = 2 if n_mpi == 1 else n_mpi

    run_file = ["run.sh" , "run_restart.sh"]
    for (i,r_file) , file_ in zip(enumerate(run_file),method_files):
        output_file = os.path.join(out, output_dir, r_file)
        sequence = " ".join(str(i) for i in range(n_mpi))
            
        sbatch_script = f"""#!/bin/bash
#SBATCH -J  {config["dir_name"]}  # Job name
#SBATCH -t {config["time"]}        # Maximum execution time (e.g., 1 hour) - ADJUST
#SBATCH --mem=2G         # Memory 
#SBATCH --nodes={int(n_mpi/2)}   
#SBATCH --ntasks-per-node=2  
#SBATCH -n {int(n_mpi)}               # Number of MPI tasks (1 is sufficient for this small system)
#SBATCH -c 32               # Number of cores per task (OpenMP threads)
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
    {config["environment"]} ../../../src/analysis/make_analysis.py "$(pwd)"
fi
"""
        
        with open(output_file, "w") as f:
            f.write(sbatch_script)

def create_run_file(out,n_mpi, output_dir, method_files, config):

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
    
        if config["plumed"]["enabled"] == True:
            sbatch_script+= f"""\nsrun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -plumed ../{file_} -ntomp ${{SLURM_CPUS_PER_TASK:-1}}"""
        else:
            sbatch_script+= """\nsrun gmx_mpi mdrun -v -cpi topol.cpt -deffnm topol -ntomp ${{SLURM_CPUS_PER_TASK:-1}}"""

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

def save_config(out, config, output_dir):

    """ 
    Create an output file with the parameters used in simulation.

    Args:
        config (dir): A dictionary containing simulation parameters.
    Returns:    
        None: The function creates a json output file stored in the output directory with the simulation parameters.
    """

    output_json = os.path.join(out, output_dir, "config.json")
    output_dict = json.dumps(config, indent=4)

    with open(output_json, "w") as file:
        file.write(output_dict)

def load_data(config_file):
     
    """ 
    Load data from config file with the parameters for the simulation.

    Args:
        config (str): A string containing the name of the config.json file.
    Returns:    
        config (dir): A directory containing all the parameters.
        Rest of the parameters loaded on variables.
    """


    with open(config_file, "r") as f:
        config = json.load(f)


    cv = config["cv"]          # distance on the x axis from the center of the ligand to the center of the host
    n = len(cv)                   # number of walkers == number of distances
    dir_name = config["dir_name"]              # name of the output directory
    data_dir = config["data_dir"]                # data directory, contains mdp files, .top, inputs, outputs...
    output_dir = os.path.join(data_dir, "output")  # path of the output directory
    ligand = config["ligand"]                # ligand molecule
    em_file = config["em_file"]            # minimize mdp file
    prod_file = config["prod_file"]        # production mdp file
    topology_file = config["topol"]        # topology file .top
    host = config["host"]              # host molecule

    return config, cv, n, dir_name, data_dir, output_dir, ligand, em_file, prod_file, topology_file, host