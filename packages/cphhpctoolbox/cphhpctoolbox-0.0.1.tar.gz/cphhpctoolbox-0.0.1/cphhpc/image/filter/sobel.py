#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# Sobel - Sobel 2-dimensional convolution filter
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

"""Sobel 2-dimensional convolution filter"""

from numpy import array, zeros, sqrt, integer, uint64, int64


from cphhpc.signal.convolution.kernel import _separate2d, \
    _convolve2d_separate

# Globals

_cache = {}


def init(input_shape, data_type=int64):
    """
    Initializes the data structures needed for the Sobel filtering
    
    Parameters
    ----------
    input_shape : (int,int)
        Shape of input (rows,cols)
    data_type : data-type, optional
        The precision of the data structures needed for the Sobel filtering
    """

    # Init cache

    _cache.clear()

    sobel_matrices = _generate_sobel_matrices(data_type)

    _cache['sobel_vectors'] = (_separate2d(sobel_matrices[0]),
                               _separate2d(sobel_matrices[1]))

    _cache['sobel_window_radius'] = (1, 1)

    _cache['input_shape'] = input_shape

    _cache['zero_padded_shape'] = (input_shape[0] + 2
                                   * _cache['sobel_window_radius'][0],
                                   input_shape[1] + 2
                                   * _cache['sobel_window_radius'][1])

    _cache['zero_padded_input'] = zeros(_cache['zero_padded_shape'],
            dtype=data_type)
    _cache['tmp_col_result'] = zeros((_cache['input_shape'][0],
            _cache['zero_padded_shape'][1]), dtype=data_type)
    _cache['tmp_result'] = zeros(_cache['input_shape'], dtype=data_type)
    _cache['sobel_x'] = zeros(_cache['input_shape'], dtype=data_type)
    _cache['sobel_y'] = zeros(_cache['input_shape'], dtype=data_type)


def free():
    """
    Free up the internal data structures needed for the Sobel filtering
    """

    _cache.clear()


def _generate_sobel_matrices(data_type=int64):
    """
    Returns a Sobel filter matrix:
    http://en.wikipedia.org/wiki/Sobel_operator
    
    Parameters
    ----------
    data_type : data-type, optional
        The precision of filter matrix
        (numpy.int8/numpy.int16/numpy.int32/numpy.int64)

    Returns
    -------
    output : Two tuple of ndarrays
        Sobel (horizontal,vertical) convolution matrices
        with the given data_type.

    """

    sobel_window_x = array([[-1, 0, 1], [-2, 0, 2], [-1, 0,
                           1]]).astype(data_type)

    sobel_window_y = array([[-1, -2, -1], [0, 0, 0], [1, 2,
                           1]]).astype(data_type)

    return (sobel_window_x, sobel_window_y)


def filter_kernel(input, out=None):
    """
    Returns a 2d Sobel filtered array based on `convulution
    <http://www.songho.ca/dsp/convolution/convolution.html>`_.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must be a 2d integer matrix. Values that exceeds the 
        the precision of *out* is set to the maximum supported value.
           
    Returns
    -------
    output : ndarray
        2d Sobel filtered version of *input*, 
        if *out* is given, then it's returned, if not *output* is created with
        shape and type equivalent to *input*. Values that exceeds the 
        the precision of *output* is set to the maximum supported value.
        
    Raises
    ------
    ValueError
        If Sobel wasn't initialized or if the shape and dtype of *input*
        (and *out*) don't match the ones given to the init function.
    """

    if not _cache:
        msg = 'Sobel is not initialized'
        raise ValueError(msg)

    input_shape = _cache['input_shape']
    zero_padded_input = _cache['zero_padded_input']
    sobel_vectors = _cache['sobel_vectors']
    sobel_window_radius = _cache['sobel_window_radius']
    tmp_col_result = _cache['tmp_col_result']
    tmp_result = _cache['tmp_result']
    sobel_x = _cache['sobel_x']
    sobel_y = _cache['sobel_y']

    # If pre-allocated output matrix provided, check shape and types

    if input.shape != input_shape:
        msg = 'input.shape: %s differs from init shape %s' \
            % (str(input.shape), str(input_shape))
        raise ValueError(msg)

    if out != None:
        if out.shape != input_shape:
            msg = 'out.shape: %s differs from init shape %s' \
                % (str(out.shape), str(input_shape))
            raise ValueError(msg)
    else:

        # If no pre-allocated output matrix provided, allocate data

        out = zeros(input.shape, dtype=input.dtype)

    sobel_x = _convolve2d_separate(
        input,
        sobel_vectors[0],
        sobel_window_radius,
        zero_padded_input,
        tmp_col_result,
        tmp_result,
        sobel_x,
        )

    sobel_y = _convolve2d_separate(
        input,
        sobel_vectors[1],
        sobel_window_radius,
        zero_padded_input,
        tmp_col_result,
        tmp_result,
        sobel_y,
        )

    tmp = sqrt(sobel_x ** 2 + sobel_y ** 2)

    # Make result fit with out data_type

    if isinstance(out.dtype.type(0), integer):
        if out.dtype.name[0:4] == 'uint':
            minval = 0
            maxval = (1 << out.itemsize * 8) - 1
            tmp = uint64(tmp)
        else:
            minval = -(1 << out.itemsize * 8) / 2
            maxval = (1 << out.itemsize * 8) / 2 - 1
            tmp = int64(tmp)

        tmp[tmp < minval] = minval
        tmp[tmp > maxval] = maxval

    out[:] = tmp

    return out


def filter(input, out=None, data_type=int64):
    """
    This performs a one-shot filtering: *init(...)*, *filter_kernel(...)* and
    *free(...)*
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must be a 2d integer matrix. Values that exceeds the 
        the precision of *out* is set to the maximum supported value.
    data_type : data-type, optional
        The precision of the internal data structures needed for the Sobel
        filtering

    Returns
    -------
    output : ndarray
    2d Sobel filtered version of *input*, 
        if *out* is given, then it's returned, if not *output* is created with
        shape and type equivalent to *input*. Values that exceeds the 
        the precision of *output* is set to the maximum supported value.
    """

    # Initialize

    init(input.shape, data_type)

    # Perform filtering

    out = filter_kernel(input, out)

    # Free up resources

    free()

    return out


