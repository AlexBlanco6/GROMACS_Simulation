#!/usr/bin/env python
# -*- coding: utf-8 -*-

# script for getting the PMF and the COLVAR of the simulations

import sys
from analysis_functions import  argparse_plot


def main():

    try:
        directory = sys.argv[1]
        print(">>> Directory detected")
    except IndexError:
        print(">>> ERROR: No directory provided")
        sys.exit(1)

    print (">>> Starting analysis...")
    sim = argparse_plot(directory)
    sim.PMF(last_fes= False, get_fes= False)
    # # sim.PMF(last_fes= True, get_fes= False)
    # sim.delta_PMF(method = "MSE", get_fes= False)
    sim.COLVAR()

    print(">>> Finished")

    
if __name__ == "__main__":
    main()
