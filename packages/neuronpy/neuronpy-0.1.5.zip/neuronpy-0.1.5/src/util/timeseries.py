# -*- coding: utf-8 -*-
"""
Utility methods for timeseries data.

AUTHORS:

- THOMAS MCTAVISH (2011-09-13): initial version
"""
# While this software is under the permissive MIT License, 
# (http://www.opensource.org/licenses/mit-license.php)
# We ask that you cite the neuronpy package (or tools used in this package)
# in any publications and contact the author with your referenced publication.
#
# Format:
# McTavish, T.S. NeuronPy library, version 0.1, 
# http://bitbucket.org/tommctavish/neuronpy
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

__version__ = 0.1

import numpy

def local_maxima(ts, window, threshold=0.):
    """Determine local peaks of a time series signal.
    :param ts: Time series signal.
    :param window: minimum number of samples to filter out subpeaks.
    :param threshold: minimum value to be declared a peak.
    
    :return: Two vectors. The first vector are the peak values, the
        second vector are the associated indices.
    """
    peaks = []
    idxs = []
    startidx = 0
    for i, v in enumerate(ts):
        if v >= threshold:
            startidx = i
            break
    if startidx == 0:
        return peaks, idxs
        
    endidx = startidx + window
    lents = len(ts)
    while endidx < lents:
        maxval = numpy.max(ts[startidx:endidx])
        maxidx = numpy.argmax(ts[startidx:endidx])+startidx
        if maxval >= threshold:                    
            peaks.append(maxval)
            idxs.append(maxidx)
            startidx += window
            foundend = True
            for i, v in enumerate(ts[startidx:]):
                if v >= threshold:
                    startidx += i
                    foundend = False
                    break
            if foundend:
                break
            endidx = startidx + window
    
    return peaks, idxs
