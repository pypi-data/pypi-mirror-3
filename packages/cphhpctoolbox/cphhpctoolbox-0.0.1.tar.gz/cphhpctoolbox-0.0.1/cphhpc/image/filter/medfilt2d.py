#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# medfilt2d - 2-dimensional Median filter
# Copyright (C) 2011  The CPHHPC Project lead by Brian Vinter
#
# This file is part of CPHHPC Toolbox.
#
# CPHHPC Toolbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# CPHHPC Toolbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
#
# -- END_HEADER ---
#

"""2-dimensional Median filter"""

import pyopencl.array as cl_array
import cphhpc.device.gpu.opencl as gpu_device

from numpy import zeros, dtype, uint16, uint32

# Globals

_ALLOWED_DATA_TYPES = (uint16, uint32)
_cache = {}


def get_kernel_header_template():
    """
    Returns the OpenCL kernel header template,
    where constants and macros are defined.
    """

    return """
    #pragma OPENCL EXTENSION cl_khr_fp64 : enable
    #define DATA_TYPE_%(DATA_TYPE)s
    #define INIT_MAXVAL %(INIT_MAXVAL)i
    #define ITERATIONS %(ITERATIONS)i
    #define FILTER_HALF_Y_SIZE %(FILTER_HALF_Y_SIZE)i
    #define FILTER_HALF_Y_SIZE_PLUS_ONE %(FILTER_HALF_Y_SIZE_PLUS_ONE)i
    #define FILTER_HALF_X_SIZE %(FILTER_HALF_X_SIZE)i
    #define FILTER_HALF_X_SIZE_PLUS_ONE %(FILTER_HALF_X_SIZE_PLUS_ONE)i
    #define MEDIAN_PIVOT_SIZE %(MEDIAN_PIVOT_SIZE)i
    #define SHARED_WINDOW_WIDTH %(SHARED_WINDOW_WIDTH)i
    #define SHARED_WINDOW_HEIGHT %(SHARED_WINDOW_HEIGHT)i
    #define DATA_W %(DATA_W)i
    #define DATA_H %(DATA_H)i
    #define WORK_GROUP_W %(WORK_GROUP_W)i
    #define WORK_GROUP_H %(WORK_GROUP_H)i

    #define SHARED_WINDOW(y,x)  shared_window[(y)+FILTER_HALF_Y_SIZE][(x)+FILTER_HALF_X_SIZE]
    #define INPUT(y,x)          input[(y)*DATA_W + (x)]
    #define RESULT(y,x)         result[(y)*DATA_W + (x)]
    
    """


def get_kernel_source_template():
    """
    Returns the OpenCL 2D median kernel source based on `Viola et al. 2003
    <http://dk.migrid.org/vgrid/eScience/Tools/Python/litterature/
    cphhpctoolbox/cphhpc/image/filter/Viola-2003.pdf>`_ section 4.2.1: 
    """

    return """

#ifdef DATA_TYPE_UINT16
    __kernel void medfilt2d(__global unsigned short *result, 
                            __global unsigned short *input) {

                            
       __local unsigned short shared_window[SHARED_WINDOW_HEIGHT][SHARED_WINDOW_WIDTH];
       
#elif defined DATA_TYPE_UINT32
    __kernel void medfilt2d(__global unsigned int *result, 
                            __global unsigned int *input) {

                            
       __local unsigned int shared_window[SHARED_WINDOW_HEIGHT][SHARED_WINDOW_WIDTH];
#endif


       int x = get_global_id(0);
       int y = get_global_id(1);
       
       int tx = get_local_id(0);
       int ty = get_local_id(1);
        
       int tx_top = tx-FILTER_HALF_X_SIZE;
       int tx_bottom = tx+FILTER_HALF_X_SIZE;
        
       int ty_top = ty-FILTER_HALF_Y_SIZE;
       int ty_bottom = ty+FILTER_HALF_Y_SIZE;
       
       /* 
       * zero pad block borders 
       */
       SHARED_WINDOW(ty, tx_top) = 0;
       SHARED_WINDOW(ty, tx_bottom) = 0;
       SHARED_WINDOW(ty_top, tx) = 0;
       SHARED_WINDOW(ty_top, tx_top) = 0;
       SHARED_WINDOW(ty_top, tx_bottom) = 0;
       SHARED_WINDOW(ty_bottom, tx) = 0;
       SHARED_WINDOW(ty_bottom, tx_top) = 0;
       SHARED_WINDOW(ty_bottom, tx_bottom) = 0;
      
       /*
       * As above zero pad pads non-border indexes (center threads)
       * we need to sync before proceed fetching data
       * NOTE: this is more efficient than checking if we are at a border
       */
       barrier(CLK_LOCAL_MEM_FENCE);
 
       /*
       * guards: is at boundary and still more image?
       */
       bool is_x_top = (tx_top<0);
       bool is_y_top = (ty_top<0);
       bool is_x_bot = (tx_bottom>WORK_GROUP_W-1);
       bool is_y_bot = (ty_bottom>WORK_GROUP_H-1);
       
       int x_top = x-FILTER_HALF_X_SIZE;
       int x_bottom = x+FILTER_HALF_X_SIZE;
       
       int y_top = y-FILTER_HALF_Y_SIZE;
       int y_bottom = y+FILTER_HALF_Y_SIZE;
       
       is_x_top = (x_top >= 0);
       is_y_top = (y_top >= 0);
       is_x_bot = (x_bottom<DATA_W);
       is_y_bot = (y_bottom<DATA_H);
       
       /*
       * Each thread pulls from image
       */
      
       // Self 
       SHARED_WINDOW(ty,tx) = INPUT(y,x);
       
       // Borders
       if (is_x_top) {
          SHARED_WINDOW(ty, tx_top) = INPUT(y, x_top);
       }
       
       if (is_x_bot) {
          SHARED_WINDOW(ty, tx_bottom) = INPUT(y, x_bottom);
       }

       if (is_y_top) {
          SHARED_WINDOW(ty_top, tx) = INPUT(y_top, x);
          if (is_x_top) {
             SHARED_WINDOW(ty_top, tx_top) = INPUT(y_top, x_top);
          }
          if (is_x_bot) {
             SHARED_WINDOW(ty_top, tx_bottom) = INPUT(y_top, x_bottom);
          }
       }
       if (is_y_bot) {
          SHARED_WINDOW(ty_bottom, tx) = INPUT(y_bottom, x);
          
          if (is_x_top) {
             SHARED_WINDOW(ty_bottom, tx_top) = INPUT(y_bottom, x_top);
          }
         
          if (is_x_bot) {
             SHARED_WINDOW(ty_bottom, tx_bottom) = INPUT(y_bottom, x_bottom);
          }
       }
      
       /*
        * Wait for threads to finish data fetch
       */ 
       barrier(CLK_LOCAL_MEM_FENCE);

       /*
        * With UINT32 float is _NOT_precise enough
       */
#ifdef DATA_TYPE_UINT16
       float minval = 0.0f;
       float maxval = convert_float(INIT_MAXVAL);
       float pivot = maxval/2.0f;
       
#elif defined DATA_TYPE_UINT32
       double minval = 0.0;
       double maxval = convert_double(INIT_MAXVAL);
       double pivot = maxval/2.0;
#endif

       unsigned short count = 0;
       
       short pos_x;
       short start_x = tx-FILTER_HALF_X_SIZE;
       short end_x = tx+FILTER_HALF_X_SIZE_PLUS_ONE;
      
       short pos_y;
       short start_y = ty-FILTER_HALF_Y_SIZE;
       short end_y = ty+FILTER_HALF_Y_SIZE_PLUS_ONE;
       
       for (unsigned short i=0; i<ITERATIONS; i++) {
          count = 0;
       
          for (pos_y=start_y; pos_y<end_y; pos_y++) {
             for (pos_x=start_x; pos_x<end_x; pos_x++) {
                count = (SHARED_WINDOW(pos_y, pos_x) > pivot)?count+1:count;
             }
          }

          maxval = (count < MEDIAN_PIVOT_SIZE)?floor(pivot):maxval;
          minval = (count >= MEDIAN_PIVOT_SIZE)?ceil(pivot):minval;
          pivot = (minval + maxval)/2.0f;

       }
       RESULT(y,x) = ceil(pivot);

    }
    """


def get_opencl_kernel(
    input_shape,
    filter_shape,
    work_group_shape,
    data_type,
    ):
    """
    Compiles the 2D median filter kernel, based on the provided parameters.
    
    Parameters
    ----------
    input_shape : (int,int)
        Shape of input (rows,cols)
    filter_shape : (int,int)
        Shape of filter  (rows,cols), must be odd
    work_group_shape : (int,int)
        Shape of GPU work groups (rows,cols)
    
    Returns
    -------
    output : OpenCL kernel
    """

    kernel_header_template = get_kernel_header_template()
    kernel_source_template = get_kernel_source_template()

    if data_type == uint16:
        iterations = 16
    elif data_type == uint32:
        iterations = 32

    kernel_header = kernel_header_template % {
        'DATA_TYPE': dtype(data_type).name.upper(),
        'ITERATIONS': iterations,
        'INIT_MAXVAL': (1 << iterations) - 1,
        'FILTER_HALF_Y_SIZE': filter_shape[0] / 2,
        'FILTER_HALF_Y_SIZE_PLUS_ONE': filter_shape[0] / 2 + 1,
        'FILTER_HALF_X_SIZE': filter_shape[1] / 2,
        'FILTER_HALF_X_SIZE_PLUS_ONE': filter_shape[1] / 2 + 1,
        'MEDIAN_PIVOT_SIZE': (filter_shape[0] * filter_shape[1] + 1) \
            / 2,
        'SHARED_WINDOW_HEIGHT': work_group_shape[0] + 2 \
            * (filter_shape[0] / 2),
        'SHARED_WINDOW_WIDTH': work_group_shape[1] + 2 \
            * (filter_shape[1] / 2),
        'DATA_H': input_shape[0],
        'DATA_W': input_shape[1],
        'WORK_GROUP_H': work_group_shape[0],
        'WORK_GROUP_W': work_group_shape[1],
        }

    kernel_source = kernel_header + kernel_source_template

    return gpu_device.get_compiled_kernel(kernel_source)


def init(
    input_shape,
    filter_shape,
    data_type=uint16,
    gpu_deviceid=-1,
    ):
    """
    Allocates a GPU device and initiates the data structures needed for the 2D
    median filter, 
    
    Parameters
    ----------
    input_shape : (int,int)
        Shape of input (rows,cols)
    filter_shape : (int,int)
        Shape of filter  (rows,cols), must be odd
    data_type : data-type, optional
        The precision of the input and output array
    gpu_deviceid: optional
        The id of the GPU device if multiple present on the system

    Raises
    ------
    ValueError
        If *filter_shape* values are even, *data_type* is unsupported, 
        no GPU device with *gpu_deviceid* is present on the system 
        or *filter_shape* too big for the system GPU        
    """

    # Init cache

    _cache.clear()

    # Check if filter_shape is odd

    if filter_shape[0] % 2 == 0 or filter_shape[1] % 2 == 0:
        msg = 'filter_shape: %s is _NOT_ odd' % str(filter_shape)
        raise ValueError(msg)

    # Check if data type is correct

    if not data_type in _ALLOWED_DATA_TYPES:
        msg = 'Unsupported data_type: %s, allowed data types: %s\n' \
            % (data_type, _ALLOWED_DATA_TYPES)
        raise ValueError(msg)

    # Try to allocate GPU with gpu_deviceid

    gpu_device.initialize(gpu_deviceid)

    _cache['input_shape'] = input_shape
    _cache['gpu_work_group_shape'] = \
        gpu_device.get_work_group_shape(input_shape)

    # Check if the 2D median filter shape fits on the current GPU

    max_gpu_y = _cache['gpu_work_group_shape'][0] * 2 + 1
    max_gpu_x = _cache['gpu_work_group_shape'][1] * 2 + 1

    if max_gpu_y < filter_shape[0] or max_gpu_x < filter_shape[1]:
        msg = \
            'filter: %s to big for this GPU, max filter shape: (%s, %s)\n' \
            % (str(filter_shape), max_gpu_y, max_gpu_x)
        free()
        raise ValueError(msg)

    # Get GPU kernel based on the parameters given to init

    _cache['gpu_kernel'] = get_opencl_kernel(input_shape, filter_shape,
            _cache['gpu_work_group_shape'], data_type)

    # Allocate data on the GPU for the result image

    output = zeros(input_shape, dtype=data_type)
    _cache['gpu_output'] = cl_array.to_device(gpu_device._queue, output)


def free():
    """
    This function frees the GPU device and the datastructures associated
    allocated in init
    """

    gpu_device.free()
    _cache.clear()


def filter_kernel(input):
    """
    Moves the input data to the GPU, performs the filtering and returns the
    filtered image
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array

    Returns
    -------
    output : ndarray
        2d median filtered version of *input*,
        
    Raises
    ------
    ValueError
        If median2d wasn't initialized or if input.shape don't match the
        initialized shape
    """

    if not _cache:
        msg = 'medfilt2d is not initialized, try init(...)'
        raise ValueError(msg)

    input_shape = _cache['input_shape']
    gpu_kernel = _cache['gpu_kernel']
    gpu_work_group_shape = _cache['gpu_work_group_shape']
    gpu_output = _cache['gpu_output']

    if input.shape != input_shape:
        msg = 'input.shape: %s differs from init shape %s' \
            % (str(input.shape), str(input_shape))
        raise ValueError(msg)

    # Move input array to GPU

    gpu_input = cl_array.to_device(gpu_device._queue, input)

    # Invoke OpenCL kernel (queue, global_shape, local_shape, data)

    event = gpu_kernel.medfilt2d(gpu_device._queue, input.shape,
                                 gpu_work_group_shape, gpu_output.data,
                                 gpu_input.data)

    # Wait for kernel to finish

    event.wait()

    # Return result

    return gpu_output.get()


def filter(
    input,
    filter_shape,
    data_type=uint16,
    gpu_deviceid=-1,
    ):
    """
    This performs a one-shot filtering: *init(...)*, *filter_kernel(...)* and
    *free(...)*

    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    filter_shape : (int,int)
        Shape of filter  (rows,cols), must be odd
    gpu_deviceid: optional
        The id of the GPU device if multiple present on the system
    data_type : data-type, optional
        The precision of the input and output array
        
    Returns
    -------
    output : ndarray
        2d median filtered version of *input*,
        
    Raises
    ------
    ValueError
        If *filter_shape* values are even, *data_type* is unsupported, 
        no GPU device with *gpu_deviceid* is present on the system 
        or *filter_shape* to big for the system GPU        
    """

    # Initialize

    init(input.shape, filter_shape, data_type, gpu_deviceid)

    # Perform filtering

    output = filter_kernel(input)

    # Free up resources

    free()

    return output


