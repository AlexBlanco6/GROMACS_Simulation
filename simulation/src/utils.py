#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os 
import json
import glob


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


    cv = config.get("cv")          # distance on the x axis from the center of the ligand to the center of the host
    n = len(cv)                # number of walkers == number of distances
    dir_name = config.get("dir_name", "TEST")   # name of the output directory
    data_dir = config.get("data_dir", "./data")   # data directory
    ligand = config.get("ligand", "0GB_GMX")                     # ligand molecule name
    em_file = config.get("em_file", "em")      # minimize mdp file
    prod_file = config.get("prod_file", "production")    # production mdp file
    topology_file = config.get("topol", "topol_GMX")      # topology file .top
    host = config.get("host", "MOL_GMX")                     # host molecule name
    orientation = str(config.get("orientation", str(1)))   # orientation of the ligand in the host, 1, 2 or 3
    direction = config.get("direction", "up")
    meta_file = config.get("plumed", {}).get("method", "plumed") # get plumed method file
    barrier = config.get("barrier", 1.0)   # barrier height for metadynamics
    time_sim = config.get("time", "6:00:00")  # time for the simulation
    environment = config.get("environment", "python")  # environment to run the analysis script
    small_run = config.get("small_run_minimization", {}).get("enabled", "false") # if we want to run a small minimization before the production
    small_run_file = config.get("small_run_minimization", {}).get("file", "minim_inter") # name of the small minimization file
    plumed_enabled = config.get("plumed", {}).get("enabled", "false") #

    assert direction == "up" or direction == "down", "Direction must be up or down"

    return config, cv, n, dir_name, data_dir, ligand, em_file, prod_file, topology_file, host, orientation, direction, meta_file, barrier, time_sim, environment, small_run, plumed_enabled, small_run_file



def find_molecules_files(data_dir, molecule):
    """Find the first available structure file (.gro preferred over .pdb)"""
    # Look for .gro files first
    gro_files = glob.glob(f"{data_dir}/input/{molecule}/*.gro")
    if gro_files:
        return ".gro"
    
    # If no .gro, look for .pdb files
    pdb_files = glob.glob(f"{data_dir}/input/{molecule}/*.pdb")
    if pdb_files:
        return  ".pdb"
    raise FileNotFoundError("No .gro or .pdb files found in the current directory.")
    
