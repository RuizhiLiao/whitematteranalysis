import glob
import os

import whitematteranalysis as wma

from joblib import Parallel, delayed

# this code should migrate into the wma package
execfile('/Users/odonnell/Dropbox/Coding/Python/WhiteMatterAnalysis/bin/miccai-stats-paper/test_compute_FA.py')

#outdir = '.'
indir = '/Users/odonnell/Dropbox/Work/Publications/Results/2012_MICCAI_reg_results/test_nL_reg_N26/iteration_4/'

input_mask = "{0}/*.vtk".format(indir)
input_poly_datas = glob.glob(input_mask)

print input_poly_datas

# this is to produce the files with scalars
def process_input(fname):
    print fname
    pd = wma.io.read_polydata(fname)
    pd = compute_scalar_measures(pd)

    pd = compute_mean_array_along_lines(pd, 'FA', 'mean_FA')
    pd = compute_mean_array_along_lines(pd, 'MD', 'mean_MD')
    pd = compute_mean_array_along_lines(pd, 'perpendicular_diffusivity', 'mean_perpendicular_diffusivity')
    pd = compute_mean_array_along_lines(pd, 'parallel_diffusivity', 'mean_parallel_diffusivity')
 
    fname2 =  'scalars_' + os.path.basename(fname)
    wma.io.write_polydata(pd, fname2)

ret = Parallel(n_jobs = 30, verbose = 0)(
    delayed(process_input)(fname) for fname in input_poly_datas)

