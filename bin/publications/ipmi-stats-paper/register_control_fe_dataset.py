#!/Library/Frameworks/EPD64.framework/Versions/Current/bin/ipython

import os
import glob
import matplotlib.pyplot as plt
import numpy

import vtk
#tmp = vtk.vtkVersion()
#vtk_version = tmp.GetVTKMajorVersion()

import whitematteranalysis as wma
from joblib import Parallel, delayed

import multiprocessing
parallel_jobs = multiprocessing.cpu_count()
print 'CPUs detected:', parallel_jobs
#parallel_jobs *= 3
#parallel_jobs = 101
#parallel_jobs = 15
parallel_jobs = 20
print 'Using N jobs:', parallel_jobs

indir1 = '/Volumes/brage-raid/odonnell/TBI_FE_CONTROLS_PNL/Tracts/controls'
indir2 = '/Volumes/brage-raid/odonnell/TBI_FE_CONTROLS_PNL/Tracts/fe-sz-patients'
outdir = '/Users/odonnell/Dropbox/Coding/OUTPUTS/Dec2012/ipmi-reg-fe'


input_mask1 = "{0}/*.vtk".format(indir1)
input_mask2 = "{0}/*.vtk".format(indir2)
input_poly_datas = glob.glob(input_mask1) + glob.glob(input_mask2)


#input_mask_original = "{0}/*.vtk".format(indir_original)
#input_poly_datas_original = glob.glob(input_mask_original)
input_poly_datas_original = input_poly_datas

#input_poly_datas = input_poly_datas[0:3]

print input_poly_datas


def run_registration(input_poly_datas, outdir, number_of_fibers=150,
                     number_of_fibers_per_step=[75, 75, 75],
                     parallel_jobs=2,
                     points_per_fiber=5,
                     sigma_per_step=[30, 10, 5],
                     maxfun=150,
                     distance_method='Hausdorff'):

    minimum_length = 40
    number_of_fibers_step_one = number_of_fibers_per_step[0]
    number_of_fibers_step_two = number_of_fibers_per_step[1]
    number_of_fibers_step_three = number_of_fibers_per_step[2]

    sigma_step_one = sigma_per_step[0]
    sigma_step_two = sigma_per_step[1]
    sigma_step_three = sigma_per_step[2]

    print 'Read and preprocess'
    input_pds = list()
    for fname in input_poly_datas:
        print fname
        pd = wma.io.read_polydata(fname)
    #    #pd2 = wma.filter.preprocess(pd, 60)
        pd2 = wma.filter.preprocess(pd, minimum_length)
        pd3 = wma.filter.downsample(pd2, number_of_fibers)
        input_pds.append(pd3)

    #input_pds_unprocessed = Parallel(n_jobs=parallel_jobs)(delayed(wma.io.read_polydata)(fname) for fname in input_poly_datas)
    #for pd in input_pds_unprocessed:
    #    pd2 = wma.filter.preprocess(pd, minimum_length)
    #    pd3 = wma.filter.downsample(pd2, number_of_fibers)
    #    input_pds.append(pd3)

    # view input data
    #ren = wma.registration_functions.view_polydatas(input_pds)

    # create registration object and apply settings
    register = wma.congeal.CongealTractography()
    register.parallel_jobs = parallel_jobs
    register.threshold = 0
    register.points_per_fiber = points_per_fiber
    register.distance_method = distance_method
    register.maxfun = maxfun
    
    # add inputs to the registration
    for pd in input_pds:
        register.add_subject(pd)

    # view output data from this big iteration
    outdir_current = os.path.join(outdir, 'iteration_0')
    if not os.path.exists(outdir_current):
        os.makedirs(outdir_current)
    output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
    ren = wma.registration_functions.view_polydatas(output_pds)
    ren.save_views(outdir_current)
    #wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
    
    # STEP ONE
    # run the basic iteration of translate, rotate, scale
    register.fiber_sample_size = number_of_fibers_step_one
    register.sigma = sigma_step_one
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    # Don't scale at the first step
    #register.scale_only()
    #register.compute()

    # view output data from this big iteration
    outdir_current = os.path.join(outdir, 'iteration_1')
    if not os.path.exists(outdir_current):
        os.makedirs(outdir_current)
    output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
    ren = wma.registration_functions.view_polydatas(output_pds)
    ren.save_views(outdir_current)
    #wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
    wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
    plt.figure()   # to avoid all results on same plot
    #plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
    plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
    plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))

    # STEP TWO
    # run the basic iteration of translate, rotate, scale AGAIN
    register.fiber_sample_size = number_of_fibers_step_two
    register.sigma = sigma_step_two
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    register.scale_only()
    register.compute()
    register.shear_only()
    register.compute()

    # view output data from this big iteration
    outdir_current = os.path.join(outdir, 'iteration_2')
    if not os.path.exists(outdir_current):
        os.makedirs(outdir_current)
    output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
    ren = wma.registration_functions.view_polydatas(output_pds)
    ren.save_views(outdir_current)
    #wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
    wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
    plt.figure()   # to avoid all results on same plot
    #plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
    plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
    plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))

    #if 0:
    # STEP THREE
    # run the basic iteration of translate, rotate, scale AGAIN
    register.fiber_sample_size = number_of_fibers_step_three
    register.sigma = sigma_step_three
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    register.scale_only()
    register.compute()
    register.shear_only()
    register.compute()

    # view output data from this big iteration
    outdir_current = os.path.join(outdir, 'iteration_3')
    if not os.path.exists(outdir_current):
        os.makedirs(outdir_current)
    output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
    ren = wma.registration_functions.view_polydatas(output_pds)
    ren.save_views(outdir_current)
    #wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
    wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
    plt.figure()   # to avoid all results on same plot
    #plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
    plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
    plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))

    # STEP FOUR
    # run the basic iteration of translate, rotate, scale AGAIN
    register.fiber_sample_size = number_of_fibers_step_three
    register.sigma = sigma_step_three
    register.translate_only()
    register.compute()
    register.rotate_only()
    register.compute()
    register.scale_only()
    register.compute()
    register.shear_only()
    register.compute()
    
    # view output data from this big iteration
    outdir_current = os.path.join(outdir, 'iteration_4')
    if not os.path.exists(outdir_current):
        os.makedirs(outdir_current)
    output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
    ren = wma.registration_functions.view_polydatas(output_pds)
    ren.save_views(outdir_current)
    wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
    wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
    plt.figure()   # to avoid all results on same plot
    #plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
    plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
    plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))

    return register

## run the registration ONCE and output result to disk
number_of_fibers = 350
#number_of_fibers = 100
points_per_fiber = 5
#number_of_fibers_per_step = [25, 50, 75]
number_of_fibers_per_step = [25, 30, 50]
sigma_per_step = [30, 10, 10]
#maxfun = 600
maxfun = 300
# output location
if not os.path.exists(outdir):
    os.makedirs(outdir)
#  smoothing

# registration
register = run_registration(input_poly_datas, outdir, 
                            number_of_fibers=number_of_fibers,
                            points_per_fiber=points_per_fiber,
                            parallel_jobs=parallel_jobs,
                            number_of_fibers_per_step=number_of_fibers_per_step,
                            sigma_per_step=sigma_per_step,
                            maxfun=maxfun)

# STEP FIVE
# run the basic iteration of translate, rotate, scale AGAIN
#register.fiber_sample_size = number_of_fibers_step_three
register.sigma = 5.0
register.translate_only()
register.compute()
register.rotate_only()
register.compute()
register.scale_only()
register.compute()
register.shear_only()
register.compute()

# view output data from this big iteration
outdir_current = os.path.join(outdir, 'iteration_5')
if not os.path.exists(outdir_current):
    os.makedirs(outdir_current)
input_pds = list()
for fname in input_poly_datas:
    print fname
    pd = wma.io.read_polydata(fname)
    #pd2 = wma.filter.preprocess(pd, 60)
    pd2 = wma.filter.preprocess(pd, 40)
    pd3 = wma.filter.downsample(pd2, number_of_fibers)
    input_pds.append(pd3)

output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
ren = wma.registration_functions.view_polydatas(output_pds)
ren.save_views(outdir_current)
wma.registration_functions.transform_polydatas_from_disk(input_poly_datas, register, outdir_current)
wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
plt.figure()   # to avoid all results on same plot
#plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))



# STEP SIX
# run the basic iteration of translate, rotate, scale AGAIN
#register.fiber_sample_size = number_of_fibers_step_three
register.sigma = 5.0
register.translate_only()
register.compute()
register.rotate_only()
register.compute()
register.scale_only()
register.compute()
register.shear_only()
register.compute()

# view output data from this big iteration
outdir_current = os.path.join(outdir, 'iteration_6')
if not os.path.exists(outdir_current):
    os.makedirs(outdir_current)
input_pds = list()
for fname in input_poly_datas:
    print fname
    pd = wma.io.read_polydata(fname)
    #pd2 = wma.filter.preprocess(pd, 60)
    pd2 = wma.filter.preprocess(pd, 40)
    pd3 = wma.filter.downsample(pd2, number_of_fibers)
    input_pds.append(pd3)

output_pds = wma.registration_functions.transform_polydatas(input_pds, register)
ren = wma.registration_functions.view_polydatas(output_pds)
ren.save_views(outdir_current)
wma.registration_functions.transform_polydatas_from_disk(input_poly_datas_original, register, outdir_current)
wma.registration_functions.write_transforms_to_itk_format(register.convert_transforms_to_vtk(), outdir_current)
    
plt.figure()   # to avoid all results on same plot
#plt.plot(range(len(register.objective_function_values)), numpy.log(register.objective_function_values))
plt.plot(range(len(register.objective_function_values)), register.objective_function_values)
plt.savefig(os.path.join(outdir_current, 'objective_function.pdf'))



