#!/usr/bin/env python
# -*- coding: utf-8 -*-

# analysis functions

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error, mean_absolute_error
import seaborn as sns
import subprocess
import json
import glob
import os


def format_pmf_ax(dir,directory, fig, ax, hills, last_fes):

    """
    Axes format fro PMF graphs
    """
    ax.set_title(f"{directory} simulation's PMF", fontsize=30)
    ax.set_xlabel(" Distance (nm)", fontsize=26)
    ax.set_ylabel(" Free Energy (kJ/mol)", fontsize=26)
    ax.set_xlim(np.min(hills), np.max(hills))
    ax.set_ylim(0)
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=22)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"PMF_{last_fes}_{directory}.png"))


def format_colvar_ax(dir,directory, fig, ax, w, cv, n):

    """
    Axes format for COLVAR graphs
    """
    ax.set_title(f"walker {n}" , fontsize = 22) #  initial distance = {cv[n]}", fontsize = 22)
    ax.set_ylabel("Projection", fontsize = 21)
    ax.set_xlabel("Time (ns)", fontsize = 21)
    ax.set_ylim(-1,8)
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=20)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    #plt.suptitle(f"{directory} simulation, {w} walkers", fontsize=39, y=1.00)  
    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"COLVAR_{directory}.png"))
  
def format_deltapmf_ax(dir, dir_name, fig, ax, method):

    """
    Axes format fro PMF graphs
    """
    ax.set_title(f"{method} Difference Between PMFs and last PMF", fontsize=30)
    ax.set_xlabel(" Distance (nm)", fontsize=26)
    ax.set_ylabel(f"{method}  (kJ/mol)", fontsize=26)
    ax.tick_params(direction='in', axis='both', which='major', length=12, width=1.5, labelsize=22)
    ax.tick_params(direction='in', axis='both', which='minor', length=6, width=0.75)
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')
    ax.minorticks_on()

    plt.tight_layout()

    fig.savefig(os.path.join(dir,f"DeltaPMF_{dir_name}.png"))


class argparse_plot():
    def __init__(self, 
                 directory= None):
        
        self.directory = directory

    def PMF(self,last_fes, get_fes):
        """ 
        Create PMF graph from data of directory,

        Args:
            directory (str/path): Directory path from the directory data.
            last_fes (bool): Default (False) change to True if want only the last PMF.
        Returns:    
            None
        """
        try:
            with open(os.path.join(self.directory, "config.json"), "r") as f:
                config = json.load(f)

            dir_name = config.get("dir_name", "test")
            environment = config.get("environment", "/mnt/netapp2/Store_uni/home/empresa/mdu/rga/conda/envs/myenv/bin/python")
        except FileNotFoundError:
            print(">>> ERROR: config.json file not found in the directory")
            environment = "/mnt/netapp2/Store_uni/home/empresa/mdu/rga/conda/envs/myenv/bin/python"
            dir_name = "test"

        
        os.chdir(self.directory)
        
        fig, ax = plt.subplots(1,1 , figsize = (15,10))
        
        if last_fes == True:
            if get_fes == True:
                try:
                    subprocess.run([f"{environment} ../../../../../src/analysis/FES_from_State.py \
                                    -f STATE --temp 298 --bin 1000"], 
                                    shell=True, executable="/bin/bash", check = True)
                except subprocess.CalledProcessError:
                    print(">>> ERROR CREATING FES FILE")

            else:
                print(">>> OBTAINING FES FILES...")

            HILLS_opes = np.loadtxt(os.path.join(self.directory, "fes.dat"), comments=("#"))  
            ax.plot(HILLS_opes[:,0],HILLS_opes[:,1], color = "dodgerblue", alpha =1, linewidth = 3)
            format_pmf_ax(self.directory, dir_name, fig, ax, HILLS_opes[:,0], last_fes)

        
        else:
            if get_fes == True:
                try:
                    subprocess.run([f"{environment} ../../../../../src/analysis/FES_from_State.py \
                        -f STATE --temp 298 --all_stored --bin 1000"], 
                        shell=True, executable="/bin/bash", check = True)
                except subprocess.CalledProcessError:
                    print(">>> ERROR CREATING FES FILE")
            else:
                print(">>> OBTAINING FES FILES...")
          
            files = sorted(glob.glob("fes_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
            colors = sns.color_palette("Spectral_r", n_colors=len(files) - 1)
            for i in range(2, len(files)):
                HILLS_opes = np.loadtxt(files[i], comments=("#"))
                ax.plot(HILLS_opes[:,0], HILLS_opes[:,1], color=colors[i - 1])
                
            sm = plt.cm.ScalarMappable(cmap='Spectral_r', norm=plt.Normalize(vmin=0, vmax=len(files)-2))
            cbar = plt.colorbar(sm, ax=ax)
            cbar.set_label("FES INDEX")

            format_pmf_ax(self.directory, dir_name, fig, ax, HILLS_opes[:,0], last_fes)


    def COLVAR(self):

        """ 
        Create COLVAR graph from data of directory

        Args:
            directory (str/path): Directory path from the directory data
            
        Returns:    
            None
        """
        try:
            with open(os.path.join(self.directory, "config.json"), "r") as f:
                config = json.load(f)

            cv = config.get("cv", [0])
            n_walkers = len(cv)
            dir_name = config.get("dir_name", "test")
        except FileNotFoundError:
            print(">>> ERROR: config.json file not found in the directory")
            cv = [1,2,3,4,5,6]
            n_walkers = len(cv)
            dir_name = "test"
    


        os.chdir(self.directory)

        n_rows = int(np.sqrt(n_walkers))
        fig, ax = plt.subplots(n_rows, n_rows + 1, figsize = (15,10))
        a = False
        for n, ax in enumerate(ax.ravel()):
            try:
                colvar_data = np.loadtxt(os.path.join(self.directory, f"w_{n+1}", f"COLVAR.{n}"), comments=("#"), usecols=(0,1))  
            except OSError:
                a = True
                continue
            ax.plot(colvar_data[:,0]/1000,colvar_data[:,1], color = "dodgerblue")
        
            format_colvar_ax(self.directory, dir_name, fig , ax, n_walkers, cv, n+1)
            if a:
                ax[n,n].axis('off')
            a = False
    


    def delta_PMF(self, method, get_fes):

        try:
            with open(os.path.join(self.directory, "config.json"), "r") as f:
                config = json.load(f)

            dir_name = config.get("dir_name", "test")
            environment = config.get("environment", "/mnt/netapp2/Store_uni/home/empresa/mdu/rga/conda/envs/myenv/bin/python")
        except FileNotFoundError:
            print(">>> ERROR: config.json file not found in the directory")
            environment = "/mnt/netapp2/Store_uni/home/empresa/mdu/rga/conda/envs/myenv/bin/python"
            dir_name = "test"


            
        os.chdir(self.directory)

        if get_fes == True:
            try:
                subprocess.run([f"{environment} ../../../../../src/analysis/FES_from_State.py \
                    -f STATE --temp 298 --all_stored --bin 1000"], 
                    shell=True, executable="/bin/bash", check = True)
            except subprocess.CalledProcessError:
                print(">>> ERROR CREATING FES FILE")
        else:
            print(">>> OBTAINING FES FILES...")

        files = sorted(glob.glob("fes_*.dat"), key=lambda x: int(x.split("_")[1].split(".")[0]))
        fig, ax = plt.subplots(1,1 , figsize = (15,10))

        
        last_file = int(files[-1].split("_")[1].split(".")[0])
        n_last_file = int(files[-1].split("_")[1].split(".")[0][-1:])
        diff_val = []
        last_col = np.loadtxt(files[-1], comments=("#"))[:, 1]
        for i in range(n_last_file-1, len(files), 25):
            curr_col = np.loadtxt(files[i], comments=("#"))[:, 1]
            if method == "MAE":
                diff_val.append(mean_absolute_error(curr_col, last_col))
            elif method == "MSE":
                diff_val.append(mean_squared_error(curr_col, last_col))
            else:
                raise ValueError("Invalid method. Please choose either 'MAE' or 'MSE'.")
            
        time_ns = [(n_last_file + 25*i)*(134.6/last_file) for i in range(len(diff_val))]
        ax.plot(time_ns, diff_val, color= "dodgerblue", marker = ".", markersize = 10)
        format_deltapmf_ax(self.directory, dir_name, fig, ax, method)
            