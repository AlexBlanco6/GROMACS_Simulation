#!/usr/bin/env python
# -*- coding: utf-8 -*-

# script for getting the PMF and the COLVAR of the simulations

import sys
from analysis_functions import  argparse_plot
import subprocess
import os 
import glob

lista = ["/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/test_1509_posre_8",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_2/up/test_1509_posre_2_16",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_3/up/test_1109_posre_3",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_2/up/test_1109_posre_2",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/test_1909_1",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/test_1109_posre",
         "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/test_1109_posre_1_2"
         ]

lista2q = ["/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_3/up/test_2409_3_8",
          "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_3/up/test_2509_3_bound",
          "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_2/up/test_2509_2_bound",
          "/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/test_2609_1_proj"]


a =glob.glob("/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_1/up/*")
b = glob.glob("/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_2/up/*")
c = glob.glob("/mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/data/output/orientation_3/up/*")
b.pop(1)
lista2 = a + b + c

def main():

    for directory in lista2:
        print(">>> Directory detected:", directory)
        print (">>> Starting analysis...")
        # os.chdir(directory)
        sim = argparse_plot(directory)
        # subprocess.run(["/mnt/netapp2/Store_uni/home/empresa/mdu/rga/conda/envs/myenv/bin/python /mnt/lustre/scratch/nlsas/home/empresa/mdu/rga/z/simulation/src/analysis/FES_from_State.py \
        #         -f STATE --temp 298 --bin 1000"], 
        #         shell=True, executable="/bin/bash", check = True)
        sim.PMF(last_fes= False, get_fes= False)
        # # sim.PMF(last_fes= True, get_fes= False)
        # sim.delta_PMF(method = "MSE", get_fes= False)
        # sim.COLVAR()
    print("finished")

    
if __name__ == "__main__":
    main()
