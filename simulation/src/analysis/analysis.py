#!/usr/bin/env python
# -*- coding: utf-8 -*-

from analysis_functions import argparse_plot
import argparse
### Parser stuff ###
parser = argparse.ArgumentParser(description='Obtain PLOTS from metadynamics data')
# files
parser.add_argument('--directory', '-d', dest='directory', type=str, help='directory with fes files stored')
parser.add_argument('--output', '-o', dest='output', type=str, help='ouput directory where plots will be stored')

# plots
parser.add_argument('--PMF',dest='PMF', action='store_true', required=False, help='return PMF graph')
parser.add_argument('--last_fes', dest='last_fes', action='store_true', default = False, required=False, help="plot only last PMF")
parser.add_argument('--COLVAR',dest='COLVAR',action='store_true',required=False, help='return COLVAR graph')
parser.add_argument('--delta', dest='delta_PMF', type = str, choices=['MAE', 'MSE'], required=False, help='return PMF gdelta graph')
parser.add_argument('--no_get_fes', dest='get_fes', action='store_false', help="Do not get the FES files")
parser.set_defaults(get_fes=True)


args=parser.parse_args()
directory = args.directory
get_fes = args.get_fes
data = argparse_plot(directory)
if args.PMF:
    data.PMF(args.last_fes, get_fes)
if args.COLVAR:
    data.COLVAR()
if args.delta_PMF:
    data.delta_PMF(args.delta_PMF, get_fes)

