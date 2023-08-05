# -*- coding: utf-8 -*-

# Copyright (c) 2006-2007, Rectorate of the University of Freiburg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of the Freiburg Materials Research Center,
#   University of Freiburg nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
# OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

u"""
TODO
"""

__id__ = "$Id$"
__author__ = "$Author$"
__version__ = "$Revision$"
# $Source$

from pyphant.core import Worker, Connectors,\
                         Param, DataContainer
import ImageProcessing
import numpy, copy
from scipy import ndimage

def pile(func, imagedata, runs=1, dopile=True):
    assert imagedata.ndim in [2, 3]
    assert runs >= 0
    if runs == 0:
        return imagedata
    if imagedata.ndim == 2 or not dopile:
        pile = [imagedata]
    else:
        pile = imagedata
    for run in xrange(runs):
        pile = [func(data) for data in pile]
    if imagedata.ndim == 2 or not dopile:
        newdata = pile[0]
    else:
        newdata = numpy.array(pile)
    return newdata


class NDImage(Worker.Worker):
    API = 2
    VERSION = 1
    REVISION = "$Revision$"[11:-1]
    name = "ndimage"
    _sockets = [("image", Connectors.TYPE_IMAGE)]
    _filters = {"binary_closing":("iterations", ),
                "binary_opening":("iterations", ),
                "binary_fill_holes":(),
                "binary_erosion":("iterations", ),
                "binary_dilation":("iterations", ),
                "maximum_filter":("size", "mode", "cval"),
                "median_filter":("size", "mode", "cval"),
                "grey_closing":("size", "mode", "cval"),
                "grey_erosion":("size", "mode", "cval"),
                "grey_opening":("size", "mode", "cval"),
                "distance_transform_bf":("metric", ),
                "sobel":("axis", "mode", "cval"),
                "grey_invert":(None, ),
                "cut_histogram":(None, "tolerance"),
                "label":(None, "connectivity"),
                "threshold":(None, "threshold"),
                "area_opening":(None, "size")}
    _ndparams = {"iterations":1,
                 "size":5,
                 "mode":["reflect",
                         "nearest",
                         "wrap",
                         "constant"],
                 "cval":0,
                 "tolerance":1000,
                 "connectivity":2,
                 "metric":["euclidean",
                           "taxicab",
                           "chessboard"],
                 "threshold":"1 m",
                 "axis":-1}
    _params = [("pile", "Treat 3d images as pile of 2d images", True, None),
               ("ndfilter", "Filter", _filters.keys(), None)]
    _params += [(pn, pn, dflt, None) for pn, dflt in _ndparams.iteritems()]

    def area_opening(self, data, size):
        structure = ndimage.morphology.generate_binary_structure(data.ndim,
                                                                 2)
        labels = ndimage.label(data, structure=structure)[0]
        slices = ndimage.find_objects(labels)
        areas = [numpy.where(labels[sli] == label + 1, True, False).sum() \
                     for label, sli in enumerate(slices)]
        print areas
        output = numpy.zeros(data.shape, dtype=data.dtype)
        for label, sli, area in zip(range(len(slices)), slices, areas):
            if area >= size:
                output[sli] |= numpy.where(labels[sli] == label + 1, data[sli], 0)
        return output

    def threshold(self, data, threshold):
        from pyphant.quantities import (Quantity,
                                                           isQuantity)
        from pyphant.core.Helpers import uc2utf8
        try:
            thp = Quantity(uc2utf8(threshold))
        except:
            thp = float(threshold)
        thp /= self._unit
        assert not isQuantity(thp)
        return numpy.where(data < thp, False, True)

    def grey_invert(self, data):
        return 255 - data

    def label(self, data, connectivity):
        structure = ndimage.morphology.generate_binary_structure(data.ndim,
                                                               connectivity)
        return ndimage.label(data, structure=structure)[0]

    def cut_histogram(self, data, tolerance):
        hist = ndimage.histogram(data, 0, 256, 256)
        csum = numpy.cumsum(hist)
        cut = csum[255] / tolerance
        for i in xrange(len(csum)):
            if csum[i] > cut:
                newmin = i
                break
        meanvalue = data.mean()
        return numpy.where(data < newmin, meanvalue, data)

    def applyfilter(self, data):
        if None in self._filters[self.paramNdfilter.value]:
            call = getattr(self, self.paramNdfilter.value)
        else:
            call = getattr(ndimage, self.paramNdfilter.value)
        args = {}
        for par in self._filters[self.paramNdfilter.value]:
            if par != None:
                args[par] = self.getParam(par).value
        #print args
        return call(data, **args)

    @Worker.plug(Connectors.TYPE_IMAGE)
    def ndimage(self, image, subscriber=0):
        self._unit = image.unit
        if "iterations" in self._filters[self.paramNdfilter.value]:
            runs = 1
        else:
            runs = self.paramIterations.value
        newdata = pile(self.applyfilter, image.data, runs, self.paramPile.value)
        longname = "%s" % (self.paramNdfilter.value, )
        result = DataContainer.FieldContainer(
            newdata,
            copy.deepcopy(image.unit),
            None,
            copy.deepcopy(image.mask),
            copy.deepcopy(image.dimensions),
            longname,
            image.shortname,
            copy.deepcopy(image.attributes),
            False)
        result.seal()
        return result
