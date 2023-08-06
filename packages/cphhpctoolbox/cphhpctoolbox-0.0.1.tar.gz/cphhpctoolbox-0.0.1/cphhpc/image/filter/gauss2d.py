#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# gauss2d - Gauss 2-dimensional convolution filter
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

"""Gauss 2-dimensional convolution filter"""

from numpy import zeros, float32, exp, dot
from cphhpc.signal.convolution.kernel import _separate2d, \
    _convolve2d_separate

# Globals

_cache = {}


def init(
    input_shape,
    filter_shape,
    sigma,
    data_type=float32,
    ):
    """
    Initializes the data structures needed for the gauss2d filtering
    
    Parameters
    ----------
    input_shape : (int,int)
        Shape of input (rows,cols)
    filter_shape : (int,int)
        Filter window shape (rows,cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window 
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    data_type : data-type, optional
        The precision of the data structures needed for the gauss2d filtering
                
    Raises
    ------
    ValueError
        If *filter_shape* values are even
        
    """

    # Init cache

    _cache.clear()

    gauss_matrix = _generate_gauss_matrix(filter_shape, sigma,
            data_type)

    _cache['gauss_vectors'] = _separate2d(gauss_matrix)

    _cache['gauss_window_radius'] = (len(_cache['gauss_vectors'][0])
            / 2, len(_cache['gauss_vectors'][1]) / 2)

    _cache['input_shape'] = input_shape

    _cache['zero_padded_shape'] = (input_shape[0] + 2
                                   * _cache['gauss_window_radius'][0],
                                   input_shape[1] + 2
                                   * _cache['gauss_window_radius'][1])

    _cache['zero_padded_input'] = zeros(_cache['zero_padded_shape'],
            dtype=data_type)

    _cache['tmp_col_result'] = zeros((_cache['input_shape'][0],
            _cache['zero_padded_shape'][1]), dtype=data_type)

    _cache['tmp_result'] = zeros(_cache['input_shape'], dtype=data_type)


def free():
    """
    Free up the internal data structures needed for the gauss2d filtering
    """

    _cache.clear()


def _generate_gauss_matrix(filter_shape, sigma, data_type=float32):
    """
    Returns a Gauss filter matrix equivalent to the MATLAB
    fspecial('gaussian', dim, sigma) function
    
    Parameters
    ----------
    filter_shape : (int,int)
        Filter window shape (rows,cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    data_type : data-type, optional
        The precision of the input and output array
        (numpy.float32/numpy.float64)

    Returns
    -------
    output : ndarray
        Gauss convolution matrix with the given dimensions, sigma and
        data_type.
    
    Raises
    ------
    ValueError
        If *filter_shape* values are even
    """

    if filter_shape[0] % 2 == 0 or filter_shape[1] % 2 == 0:
        msg = 'filter_shape: %s is _NOT_ odd' % str(filter_shape)
        raise ValueError(msg)

    result = zeros(filter_shape, dtype=data_type)

    y_radius = filter_shape[0] / 2
    x_radius = filter_shape[1] / 2

    for y in xrange(filter_shape[0]):
        y_distance = y - y_radius
        for x in xrange(filter_shape[1]):
            x_distance = x - x_radius
            result[y, x] = exp(-(y_distance ** 2 + x_distance ** 2)
                               / (2.0 * sigma ** 2))

    result = result / result.sum()

    return result


def filter_kernel(input, out=None):
    """
    Returns a 2d Gauss filtered array based on `convulution
    <http://www.songho.ca/dsp/convolution/convolution.html>`_.
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for filter_kernel(input). This is a performance feature. Therefore, if
        these conditions are not met, an exception is raised, instead of
        attempting to be flexible.
           
    Returns
    -------
    output : ndarray
        2d Gauss filtered version of *input*,
        if *out* is given, then it is returned.
        
    Raises
    ------
    ValueError
        If gauss2d wasn't initialized or if the shape and dtype of *input*
        (and *out*) don't match the ones given to the init function.
    """

    if not _cache:
        msg = 'gauss2d is not initialized, try init(...)'
        raise ValueError(msg)

    input_shape = _cache['input_shape']
    zero_padded_input = _cache['zero_padded_input']
    gauss_window_radius = _cache['gauss_window_radius']
    tmp_col_result = _cache['tmp_col_result']
    tmp_result = _cache['tmp_result']
    gauss_vectors = _cache['gauss_vectors']

    # If pre-allocated output matrix provided, check shape and types

    if input.shape != input_shape:
        msg = 'input.shape: %s differs from init shape %s' \
            % (str(input.shape), str(input_shape))
        raise ValueError(msg)

    if out != None:
        if out.shape != input_shape:
            msg = 'out.shape: %s differs from init shape: %s' \
                % (str(out.shape), str(input_shape))
            raise ValueError(msg)
        if input.dtype != out.dtype:
            msg = 'out.dtype: %s differs from input.dtype: %s' \
                % (out.dtype, input.dtype)
            raise ValueError(msg)
    else:

        # If no pre-allocated output matrix provided, allocate data

        out = zeros(input.shape, dtype=input.dtype)

    # Zero out tmp_col_result

    tmp_col_result[:] = 0

    # Copy data from input to zero padded input

    zero_padded_input[gauss_window_radius[0]:input.shape[0]
                      + gauss_window_radius[0], gauss_window_radius[1]:
                      input.shape[1] + gauss_window_radius[1]] = input

    # First calculate dot product of image and
    # Gauss vector along columns (y direction) with radius
    # 'gauss_window_radius[0]' from input pixels

    for y in xrange(gauss_window_radius[0], input.shape[0]
                    + gauss_window_radius[0]):
        start_y = y - gauss_window_radius[0]
        end_y = y + gauss_window_radius[0] + 1
        start_x = gauss_window_radius[1]
        end_x = input.shape[1] + gauss_window_radius[1]

        tmp_col_result[start_y, start_x:end_x] = \
            dot(zero_padded_input[start_y:end_y, start_x:end_x].T,
                gauss_vectors[0])

    # Second calculate dot product of the dot products calculated above
    # and Gauss vector along rows (x direction)
    # with radius 'gauss_window_radius[1]' from input pixel

    for x in xrange(gauss_window_radius[1], input.shape[1]
                    + gauss_window_radius[1]):
        start_x = x - gauss_window_radius[1]
        end_x = x + gauss_window_radius[1] + 1
        tmp_result[:, start_x] = dot(tmp_col_result[:, start_x:end_x],
                gauss_vectors[1])

    return _convolve2d_separate(
        input,
        gauss_vectors,
        gauss_window_radius,
        zero_padded_input,
        tmp_col_result,
        tmp_result,
        out,
        )


def filter(
    input,
    filter_shape,
    sigma,
    out=None,
    data_type=float32,
    ):
    """
    This performs a one-shot filtering: *init(...)*, *filter_kernel(...)* and
    *free(...)*
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    filter_shape : (int,int)
        Filter window shape (rows,cols) (must be odd)
    sigma : int
        The sigma value used to generate the `Gaussian window
        <http://en.wikipedia.org/wiki/Gaussian_filter>`_
    out : ndarray, optional
        Output argument. This must have the exact kind that would be returned
        if it was not used. In particular, it must have the right type, must be
        C-contiguous, and its dtype must be the dtype that would be returned
        for filter_kernel(input). This is a performance feature. Therefore, if
        these conditions are not met, an exception is raised, instead of
        attempting to be flexible.
    data_type : data-type, optional
        The precision of the internal data structures needed for the gauss2d
        filtering

    Returns
    -------
    output : ndarray
        2d Gauss filtered version of *input*, 
        if *out* is given, then it is returned.
        
    Raises
    ------
    ValueError
        If *filter_shape* values are even or
        if the shape and dtype of *input* and *out* don't match each other,
    """

    # Initialize

    init(input.shape, filter_shape, sigma, data_type)

    # Perform filtering

    out = filter_kernel(input, out)

    # Free up resources

    free()

    return out


