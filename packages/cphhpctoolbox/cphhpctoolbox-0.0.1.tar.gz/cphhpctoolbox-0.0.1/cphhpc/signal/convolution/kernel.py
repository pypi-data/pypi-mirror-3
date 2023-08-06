#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# --- BEGIN_HEADER ---
#
# _convolution - http://www.songho.ca/dsp/convolution/convolution.html
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

"""Convolution: http://www.songho.ca/dsp/convolution/convolution.html"""

from numpy import spacing, sqrt, dot, rint, integer
from numpy.linalg import svd


def _separate2d(input):
    """
    `Separate a 2d-matrix convolution filter into two decomposed vectors
    <http://blogs.mathworks.com/steve/2006/11/28/separable-convolution-part-2/>`_
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array representing a convolution window
    out : Two tuple of 1-d ndarrays
        Tuple containing the two convolution vectors obtained by decomposing
        *input* 

    Raises
    ------
    ValueError
        If *input* can't be decomposed into two vectors
    """

    # Singular Value Decomposition

    (U, S, V) = svd(input)

    # Check rank of input matrix

    tolerance = max(input.shape) * spacing(max(S))
    rank = sum(S > tolerance)
    if rank != 1:
        msg = \
            'Decomposition error, \
             The number of linearly independent rows or columns are != 1'
        raise ValueError(msg)

    vertical_vector = U[:, 0] * sqrt(S[0])
    horizontal_vector = V[0, :] * sqrt(S[0])

    return (vertical_vector, horizontal_vector)


def _convolve2d_separate(
    input,
    window_vectors,
    window_radius,
    zero_padded_input,
    tmp_col_result,
    tmp_result,
    out,
    ):
    """
    Returns a 2d convoluted array based on:
    http://www.songho.ca/dsp/convolution/convolution.html
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_vectors: Two tuple of 1-d ndarrays
        Tuple containing the two convolution vectors obtained 
        by `seperating the convolution window matrix <cphhpc.signal.html#cphhpc.signal.convolution.separate2d>`_
    window_radius: (int,int)
        Tuple containing the (y,x) radius of the convolution window
    zero_padded_input: ndarray
        A 2-dimensional array with shape (*input.shape* + 2 * *window_radius*)
    tmp_col_result: ndarray
        A 2-dimensional array with the same shape as *input*
    tmp_result: ndarray
        A 2-dimensional array with the same shape as *input*
    out : ndarray, 
        A 2-dimensional convoluted array with the same shape 
        as *input*. 
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    # Zero out tmp_col_result

    tmp_col_result[:] = 0

    # Copy data from input to zero padded input

    zero_padded_input[window_radius[0]:input.shape[0]
                      + window_radius[0], window_radius[1]:
                      input.shape[1] + window_radius[1]] = input

    # First calculate dot product of image and Gauss vector
    # along columns (y direction) with radius 'window_radius[0]'
    # from input pixels

    for y in xrange(window_radius[0], input.shape[0]
                    + window_radius[0]):
        start_y = y - window_radius[0]
        end_y = y + window_radius[0] + 1
        start_x = window_radius[1]
        end_x = input.shape[1] + window_radius[1]

        tmp_col_result[start_y, start_x:end_x] = \
            dot(zero_padded_input[start_y:end_y, start_x:end_x].T,
                window_vectors[0])

    # Second calculate dot product of the dot products calculated above
    # and Gauss vector along rows (x direction)
    # with radius 'window_radius[1]' from input pixel

    for x in xrange(window_radius[1], input.shape[1]
                    + window_radius[1]):
        start_x = x - window_radius[1]
        end_x = x + window_radius[1] + 1
        tmp_result[:, start_x] = dot(tmp_col_result[:, start_x:end_x],
                window_vectors[1])

    # If provided *out* is an integer array, round result

    if isinstance(out.dtype.type(0), integer):
        rint(tmp_result, out)
    else:
        out[:] = tmp_result[:]

    return out


def _convolve2d(
    input,
    window_matrix,
    window_radius,
    zero_padded_input,
    tmp_result,
    out,
    ):
    """
    Convolve two 2-dimensional arrays:
    http://www.songho.ca/dsp/convolution/convolution.html
    
    Parameters
    ----------
    input : ndarray
        A 2-dimensional input array
    window_matrix: ndarray
        A 2-dimensional array containing convolution window
    window_radius: (int,int)
        Tuple containing the (y,x) radius of the convolution window
    zero_padded_input: ndarray
        A 2-dimensional array with shape (*input.shape* + 2 * *window_radius*)
    tmp_result: ndarray
        A 2-dimensional array with the same shape as *input*
    out : ndarray
        A 2-dimensional convoluted array with the same shape 
        as *input*. 
           
    Returns
    -------
    output : ndarray
        2d convoluted version of *input*,
    """

    zero_padded_input[window_radius[0]:-window_radius[0],
                      window_radius[1]:-window_radius[1]] = input

    tmp_result[:] = 0

    start_y = window_radius[0] * 2
    end_y = zero_padded_input.shape[0]

    for y in xrange(window_matrix.shape[0]):
        start_x = window_radius[1] * 2
        end_x = zero_padded_input.shape[1]

        for x in xrange(window_matrix.shape[1]):
            tmp = zero_padded_input * window_matrix[y][x]
            tmp_result += tmp[start_y:end_y, start_x:end_x]
            start_x -= 1
            end_x -= 1

        start_y -= 1
        end_y -= 1

    # If provided *out* is an integer matrix, round result

    if isinstance(out.dtype.type(0), integer):
        rint(tmp_result, out)
    else:
        out[:] = tmp_result[:]

    return out


