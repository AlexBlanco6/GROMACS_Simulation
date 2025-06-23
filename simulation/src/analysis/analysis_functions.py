#!/usr/bin/env python
# -*- coding: utf-8 -*-

# analysis functions

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import subprocess
import time
import json
import glob
import os



def format_pmf_ax(dir,directory, fig, ax, hills):

    """
    Axes format fro PMF graphs
    """
    iqr = hills[(int(len(hills)*0.25)):(int(len(hills)*0.75))]
    ax.set_title(f"{directory} simulation's PMF", fontsize=30)
    ax.set_xlabel(" Distance (nm)", fontsize=26)
    ax.set_ylabel(" Free Energy (kJ/mol)", fontsize=26)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0)
    ax.legend(loc='upper left', fontsize=20)  # You can uncomment bbox_to_anchor if needed
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=22)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"PMF_{directory}.png"))


def format_colvar_ax(dir,directory, fig, ax, w, cv, n):

    """
    Axes format for COLVAR graphs
    """
    ax.set_title(f"walker {n}, initial distance = {cv[n]}", fontsize = 20)
    ax.set_ylabel("Projection", fontsize = 22)
    ax.set_xlabel("Time (ns)", fontsize = 22)
    ax.set_ylim(-2.4,2.4)
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=22)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    plt.suptitle(f"{directory} simulation, {w} walkers", fontsize=39, y=1.00)  
    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"COLVAR_{directory}.png"))


def format_deltapmf_ax(dir,directory, fig, ax):

    """
    Axes format fro PMF graphs
    """
    ax.set_title(f"{directory} simulation's Absolute Difference Between Consecutive PMFs", fontsize=30)
    ax.set_xlabel(" Distance (nm)", fontsize=26)
    ax.set_ylabel(" ΔPMF (kJ/mol)", fontsize=26)
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0)
    ax.legend(loc='upper left', fontsize=20)  # You can uncomment bbox_to_anchor if needed
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=22)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"DeltaPMF_{directory}.png"))



def PMF(directory, last_fes = False):  

    """ 
    Create PMF graph from data of directory,

    Args:
        directory (str/path): Directory path from the directory data.
        last_fes (bool): Default (False) change to True if want only the last PMF.
    Returns:    
        None
    """


    start = time.time()
    
    
    with open(os.path.join(directory, "config.json"), "r") as f:
        config = json.load(f)

    n_walkers = len(config["cv"])
    method = config["plumed"]["method"]
    dir_name = config ["dir_name"]

    os.chdir(directory)
    
    fig, ax = plt.subplots(1,1 , figsize = (15,10))
    if method == "meta":
        if last_fes == True:
            try:
                subprocess.run([f"/opt/cesga/2020/software/MPI/gcc/system/openmpi/4.0.5_ft3_cuda/plumed/2.8.0/bin/plumed \
                                sum_hills --hills HILLS --mintozero --bin 1000"], 
                                shell=True, executable="/bin/bash")
            
                HILLS_meta = np.loadtxt(os.path.join(directory, "fes.dat"), comments=("#"))  
                ax.plot(HILLS_meta[:,0],HILLS_meta[:,1], color = "orangered", alpha =1, linewidth = 3)
                format_pmf_ax(directory, dir_name, fig, ax, HILLS_meta[:,1])
            except subprocess.CalledProcessError:
                print(">>> ERROR CREATING FES FILE")
        else:
            try:
                with open("HILLS", "r") as f:
                    lines = f.readlines()

                step = 10000      # stride in ps (10 ns)
    
                for i in range(1,31):

                    max_time = i * step
                    script= []
                    for line in lines:
                        if  line.startswith('#'):
                            script.append(line)
                        else:
                            if float(line.split()[0]) >= max_time:
                                break
                            else:
                                script.append(line)
             
                        with open("HILLS_tmp", "w") as temp:
                            temp.writelines(script)

                    subprocess.run([f"plumed sum_hills --hills HILLS_tmp --outfile  fes_{i}.dat --mintozero --bin 1000"],
                                    shell=True, executable="/bin/bash")

                files = sorted(glob.glob("fes_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
                colors = sns.color_palette("Spectral_r", n_colors=len(files))
                
                for i in range(2, len(files)):
                    data_prev = np.loadtxt(files[i], comments=("#"))
                    ax.plot(data_prev[:,0], data_prev[:,1], color=colors[i - 1], alpha = 0.9)

                sm = plt.cm.ScalarMappable(cmap='Spectral_r', norm=plt.Normalize(vmin=0, vmax=len(files)))
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label("FES INDEX")
                format_pmf_ax(directory, dir_name, fig, ax, HILLS_meta[:,1])
            except subprocess.CalledProcessError:
                print(">>> ERROR CREATING FES FILE")
    else:
        f = None
        if last_fes == True:
            try:
                subprocess.run([f"python ../../../src/analysis/FES_from_State.py \
                                -f STATE --temp 298 --bin 1000"], 
                                shell=True, executable="/bin/bash")
                HILLS_opes = np.loadtxt(os.path.join(directory, "fes.dat"), comments=("#"))  
                ax.plot(HILLS_opes[:,0],HILLS_opes[:,1], color = "orangered", alpha =1, linewidth = 3)
                format_pmf_ax(directory, dir_name, fig, ax, HILLS_opes[:,1])
            except subprocess.CalledProcessError:
                    print(">>> ERROR CREATING HILLS FILE")
           
        else:
            try:
                subprocess.run([f"python ../../../src/analysis/FES_from_State.py \
                                -f STATE --temp 298 --all_stored --bin 1000"], 
                                shell=True, executable="/bin/bash")
            except subprocess.CalledProcessError:
                    print(">>> ERROR CREATING HILLS FILE")
            files = sorted(glob.glob("fes_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
            colors = sns.color_palette("Spectral_r", n_colors=len(files) - 1)
            
            sm_values = []
            for i in range(2, len(files)):
                data_prev = np.loadtxt(files[i], comments=("#"))
                
                
                ax.plot(data_prev[:,0], data_prev[:,1], color=colors[i - 1])
                sm_values.append(i)

            sm = plt.cm.ScalarMappable(cmap='Spectral_r', norm=plt.Normalize(vmin=0, vmax=len(files)-2))
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label("FES INDEX")

            format_pmf_ax((directory, dir_name, fig, ax, HILLS_opes[:,1]))
    print(f">>> Execution time {time.time()-start}")



def COLVAR(directory):

    """ 
    Create COLVAR graph from data of directory

    Args:
        directory (str/path): Directory path from the directory data
        
    Returns:    
        None
    """
    start = time.time()

    with open(os.path.join(directory, "config.json"), "r") as f:
        config = json.load(f)

    cv = config["cv"]
    n_walkers = len(cv)
    method = config["plumed"]["method"]
    dir_name = config ["dir_name"]
    
    os.chdir(directory)

    n_rows = int(np.sqrt(n_walkers))
    fig, ax = plt.subplots(n_rows, n_rows + 1, figsize = (15,10))

    for n, ax in enumerate(ax.ravel()):
        if method=="meta":
            colvar_data = np.loadtxt(os.path.join(directory, f"{n}", f"COLVAR.{n}"), comments=("#"), usecols=(0,2))  
            ax.plot(colvar_data[:,0]/1000,colvar_data[:,1], color = "orangered")
        else:
            colvar_data = np.loadtxt(os.path.join(directory, f"{n}", f"COLVAR.{n}"), comments=("#"), usecols=(0,2))  
            ax.plot(colvar_data[:,0]/1000,colvar_data[:,1], color = "dodgerblue")
          
        
        format_colvar_ax(directory, dir_name, fig , ax, n_walkers, cv, n)

    print(f">>> Execution time {time.time()-start}")

def delta_PMF(directory):

    os.chdir(directory)

    with open(os.path.join(directory, "config.json"), "r") as f:
        config = json.load(f)
    
    dir_name = config ["dir_name"]

    files = sorted(glob.glob("fes_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
    colors = sns.color_palette("coolwarm", n_colors=len(files) - 2)
    fig, ax = plt.subplots(1,1 , figsize = (15,10))

    sm_values = []
    for i in range(1, len(files),10):
        data_prev = np.loadtxt(files[i-1], comments=("#"))
        data_curr = np.loadtxt(files[i], comments=("#"))
        col_prev = data_prev[:, 1]
        col_curr = data_curr[:, 1]
        diff_val = np.abs(col_curr - col_prev)
        ax.scatter(data_prev[:,0], diff_val, color=colors[i - 1], label=f"{files[i-1]} - {files[i]}")
        sm_values.append(i)

    sm = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(vmin=0, vmax=len(files)-2))
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label("File comparison index")
 
    format_deltapmf_ax(directory, dir_name, fig, ax)
