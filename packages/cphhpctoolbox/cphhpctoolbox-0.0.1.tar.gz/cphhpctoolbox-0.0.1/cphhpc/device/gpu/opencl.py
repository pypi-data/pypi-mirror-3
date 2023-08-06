#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# opencl - Helper module for pyopencl
# Copyright (C) 2011-2012  The CPHHPC Project lead by Brian Vinter
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

"""opencl - Helper module for pyopencl"""

import sys
import pyopencl as cl

from numpy import sqrt

# Global vars for GPU device,
# we only support one device pr. process at the moment

_platform = None
_context = None
_device = None
_queue = None


def _nextpow2(i):
    """
    Returns the next power of two.
    
    Parameters
    ----------
    i : int
        Value which is raised to the next power of two.
        
    Returns
    -------
    output : int
        The next power of two of *i*.
    """

    n = 2
    while n < i:
        n = n * 2
    return n


def exit(exit_code):
    """
    Exit cleanly releasing the OpenCL GPU device before calling sys.exit(...).
   
    Parameters
    ----------
    exit_code : int
        Exit code passed to sys.exit(...).
    """

    free()
    sys.exit(exit_code)


def show_platform_info():
    """
    Prints information about the active OpenCL platform.
    
    Raises
    ------
    ValueError
       If the OpenCL platform isn't initialized.
    """

    if _platform == None:
        msg = 'OpenCL platform uninitialized'
        raise ValueError(msg)

    print '---------------------------------------------------------------'
    print 'Platform'
    print '---------------------------------------------------------------'
    print 'Name: %s' % _platform.name
    print 'Profile: %s' % _platform.profile
    print 'Vendor: %s' % _platform.vendor
    print 'Version: %s' % _platform.version


def show_device_info():
    """
    Prints information about the active OpenCL device.
    
    Raises
    ------
    ValueError
       If the OpenCL device isn't initialized.
    """

    if _device == None:
        msg = 'OpenCL device uninitialized'
        raise ValueError(msg)

    print _device
    print '---------------------------------------------------------------'
    print 'Device: %s' % _device
    print '---------------------------------------------------------------'
    print 'Name: %s' % _device.name
    print 'Type: %s' % cl.device_type.to_string(_device.type)
    print 'Global memory: %s MB' % (_device.global_mem_size / 1024
                                    / 1024)
    print 'Local memory: %s KB' % (_device.local_mem_size / 1024)
    print 'Max alloc size: %s MB' % (_device.max_mem_alloc_size / 1024
            / 1024)
    print 'Max clock speed: %s Mhz' % _device.max_clock_frequency
    print 'compute units: %s ' % _device.max_compute_units
    print 'Max work group size: %s' % _device.max_work_group_size
    print 'Max work item dimensions: %s' \
        % _device.max_work_item_dimensions
    print 'Max work item sizes: %s' % _device.max_work_item_sizes

    if 'NVIDIA' in _device.vendor:
        print 'Registers per block nv: %s' \
            % _device.registers_per_block_nv


def show_context_info():
    """
    Prints information about the active OpenCL context.
    
    Raises
    ------
    ValueError
       If the OpenCL context isn't initialized.
    """

    if _context == None:
        msg = 'OpenCL context uninitialized'
        raise ValueError(msg)

    print '---------------------------------------------------------------'
    print 'Context'
    print '---------------------------------------------------------------'
    print 'Number of devices: %s' % _context.num_devices
    print 'Devices: %s' % _context.devices
    print 'Properties: %s' % _context.properties
    print 'Reference count: %s' % _context.reference_count


def show_queue_info():
    """
    Prints information about the active OpenCL queue.
    
    Raises
    ------
    ValueError
       If the OpenCL queue isn't initialized.
    """

    if _queue == None:
        msg = 'OpenCL queue uninitialized'
        raise ValueError(msg)

    print '---------------------------------------------------------------'
    print 'Queue'
    print '---------------------------------------------------------------'
    print 'Properties: %s' % _queue.properties
    print 'Reference count: %s' % _queue.reference_count

    print '---------------------------------------------------------------'


def show_info():
    """
    Prints information about the active OpenCL environment.
    """

    print '==============================================================='
    show_queue_info()
    show_context_info()
    show_device_info()
    print '==============================================================='


def _initialize_gpu_device(deviceid):
    """
    Find GPU device and associate it with _platform and _device.
    
    Parameters:
    deviceid : int
        Id of the GPU device to initialize, if *-1* the first GPU in the list
        is chosen.
        
    Raises
    ------
    ValueError
        If no GPU device with *deviceid* is present on the system.
    """

    global _platform
    global _device

    device_counter = 0
    platforms = cl.get_platforms()

    for device_platform in platforms:
        try:
            gpu_devices = \
                device_platform.get_devices(device_type=cl.device_type.GPU)
        except Exception:
            gpu_devices = []

        for gpu_device in gpu_devices:
            if deviceid == -1 or deviceid == device_counter:
                _platform = device_platform
                _device = gpu_device
            device_counter += 1

    if device_counter <= deviceid:
        msg = \
            'Invalid GPU deviceid: %s, total devices on the system: %s' \
            % (deviceid, device_counter)
        raise ValueError(msg)


def _create_gpu_context(deviceid):
    """
    Creates a GPU OpenCL context.

    Parameters
    ----------
    deviceid : int
        Id of the GPU device to initialize.

    Raises
    ------
    ValueError
       If no GPU device with *deviceid* is present on the system.
    """

    global _context
    _initialize_gpu_device(deviceid)
    _context = cl.Context([_device])


def initialize(deviceid):
    """
    Initializes the OpenCL GPU device.

    Parameters
    ----------
    deviceid : int
        Id of the GPU device to initialize, If set to *-1* any GPU is chosen.

    Raises
    ------
    ValueError
       If no GPU device with *deviceid* is present on the system.
    """

    global _queue

    _create_gpu_context(deviceid)
    _queue = cl.CommandQueue(_context)


def free():
    """
    Frees up the OpenCL GPU device
    """

    global _platform
    global _context
    global _device
    global _queue

    if _queue != None:
        _queue.finish()

    _platform = None
    _context = None
    _device = None
    _queue = None


def get_work_group_shape(grid_shape, max_work_items_pr_group=0):
    """
    Get work group shape based on *grid_shape* and the number of
    *max_work_items_pr_group*. We aim at square shapes.
   
    Parameters
    ----------
    grid_shape : (int,int)
        The GPU grid shape (rows,cols)
    max_work_items_pr_group : int, optional
        The maximum number of work items pr work group, if not given the one
        specified by the hardware is used.
       
    Returns
    -------
    output : (int,int)
        Tuple containing the work group shape (height, width).
       
    Raises
    ------
    ValueError
        If impossible to generate a valid work group shape from *grid_shape*
        and *max_work_items_pr_group*.
      
   """

    if max_work_items_pr_group > 0:
        gpu_threads_pr_group = float(max_work_items_pr_group)
    else:
        gpu_threads_pr_group = float(_device.max_work_group_size)

    image_height = float(grid_shape[0])
    image_width = float(grid_shape[1])

   # Select x dim to be close to square thread block dimension

    group_xdim = _nextpow2(int(sqrt(gpu_threads_pr_group)))

   # Increase until we do have enough rows, though

    while group_xdim <= gpu_threads_pr_group and gpu_threads_pr_group \
        / group_xdim > image_height:
        group_xdim *= 2

    while image_width % group_xdim != 0 and group_xdim > 1.0:
        group_xdim /= 2

    if group_xdim < 1.0:
        msg = \
            "Width of grid_shape: %s and \
               max_work_items_pr_group: %s don't match" \
            % (str(grid_shape), gpu_threads_pr_group)
        raise ValueError(msg)

    if image_width % group_xdim != 0:
        msg = \
            "Width of grid_shape: %s and \
             max_work_items_pr_group: %s don't match" \
            % (str(grid_shape), gpu_threads_pr_group)
        raise ValueError(msg)

    group_ydim = gpu_threads_pr_group / group_xdim
    while image_height % group_ydim != 0 and group_ydim > 1.0:
        group_ydim /= 2

    if group_ydim < 1.0:
        msg = \
            "Height of grid_shape: %s and \
             max_work_items_pr_group: %s don't match" \
            % (str(grid_shape), gpu_threads_pr_group)
        raise ValueError(msg)

    if image_height % group_ydim != 0:
        msg = \
            "Height of grid_shape: %s and \
             max_work_items_pr_group: %s don't match" \
            % (str(grid_shape), gpu_threads_pr_group)
        raise ValueError(msg)

    return (int(group_ydim), int(group_xdim))


def get_compiled_kernel(kernel_source):
    """ 
    Returns a compiled OpenCL kernel
    
    Parameters
    ----------
    kernel_source : str
        A string representing the OpenCL kernel source
        
    Returns
    -------
        output : Compiled OpenCL kernel
    
    Raises
    ------
    ValueError
       If the OpenCL device and context isn't initialized.
       
    """

    if _device == None:
        msg = 'OpenCL device uninitialized'
        raise ValueError(msg)

    if _context == None:
        msg = 'OpenCL device uninitialized'
        raise ValueError(msg)

    if 'NVIDIA' in _device.vendor:
        options = '-cl-mad-enable -cl-fast-relaxed-math'
    else:
        options = ''

    return cl.Program(_context, kernel_source).build(options=options)


