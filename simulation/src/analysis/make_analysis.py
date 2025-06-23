#!/usr/bin/env python
# -*- coding: utf-8 -*-

# script for getting the PMF and the COLVAR of the simulations

import sys
from analysis_functions import PMF, COLVAR, delta_PMF

def main():

    try:
        directory = sys.argv[1]
        print(">>> Directory detected")
    except IndexError:
        print(">>> ERROR: No directory provided")
        sys.exit(1)

    
    last_fes = True
    PMF(directory, last_fes = last_fes, d = 500)
    COLVAR(directory)

    if last_fes:
        delta_PMF(directory)
    print("finished")

    
if __name__ == "__main__":
    main()