# -*- coding: utf-8 -*-
"""
Graphics utilities.

AUTHORS:

- THOMAS MCTAVISH (2011-09-23): initial version, 0.1
"""
# While this software is under the permissive MIT License, 
# (http://www.opensource.org/licenses/mit-license.php)
# We ask that you cite the neuronpy package (or tools used in this package)
# in any publications and contact the author with your referenced publication.
#
# Format:
# McTavish, T.S. NeuronPy library, version 0.1, http://bitbucket.org/tommctavish/neuronpy
#
# Copyright (c) 2010 Thomas S. McTavish
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import numpy
from matplotlib.colors import colorConverter

def alpha_color_to_rgb(color, alpha, background='white'):
    """Since EPS files do not permit the drawing of transparency, this
    method converts a color and its alpha value into a standard RGB
    color against a background.
    :param color: Opaque Matplotlib color to convert.
    :param alpha: Normalized alpha value (0=transparent, 1=opaque)
    :param background: Opaque Matplotlib background color.
    :return: RGB value as normalized list of 3 floats."""
    rgb = colorConverter.to_rgb(color)
    bkgrd = colorConverter.to_rgb(background)
    rgb = numpy.multiply(rgb, alpha)
    rgb = numpy.add(rgb, bkgrd)
    rgb = numpy.subtract(rgb, alpha)
    return rgb
    
