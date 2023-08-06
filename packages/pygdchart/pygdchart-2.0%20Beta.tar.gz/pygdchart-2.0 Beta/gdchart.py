# PyGDChart
# 
# Copyright (c) 2003, Nullcube Pty Ltd
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# *   Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
# *   Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# *   Neither the name of Nullcube nor the names of its contributors may be used to
#     endorse or promote products derived from this software without specific prior
#     written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
PyGDChart is an interface to the gdchart graphing library.
"""
import types
import _gdchartc

class GDChartError(Exception): pass

class _Bucket:
    """
        An internal PyGDChart general dataholder class. 
    """
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

def _uniformLength(*lst):
    """
        Takes a list of lists, and tests wether all lists have the same length.
        Returns a 0 if lengths differ, 1 if not.
        This is an internal PyGDChart utility function.
    """
    baselen = len(lst[0])
    for l in lst:
        if len(l) != baselen:
            return -1
    return baselen

def _flattenList(*lst):
    """
        Takes a set of lists, and flattens them by appending them all
        together. 
        This is an internal PyGDChart utility function.
    """
    flat = []
    for i in lst:
        flat.extend(i)
    return flat


class RGB:
    """
        A simple class for representing RGB colors.
    """
    def __init__(self, r=0, g=0, b=0):
        self.r, self.g, self.b = r, g, b
        self._sanity()

    def _sanity(self):
        checks = [0 <= i <= 256 for i in (self.r, self.g, self.b)]
        if 0 in checks:
            raise ValueError("All RGB values should be 0 <= val <= 100")

    def __int__(self):
        self._sanity()
        intval = self.r*(256**2)
        intval += self.g*(256)
        intval += self.b
        return intval

    def __hex__(self):
        return hex(int(self))

    def __repr__(self):
        return hex(self)


def rgbFactory(color):
    """
        Manufacture an RGB object by colour name. Included colours are:
            black, white, blue, green, yellow, red, orange
    """
    # This should be re-written using a dictionary.
    if color == "black":
        return RGB(0,0,0)
    elif color == "white":
        return RGB(255,255,255)
    elif color == "blue":
        return RGB(50,50,204)
    elif color == "green":
        return RGB(37,180,21)
    elif color == "yellow":
        return RGB(255,255,21)
    elif color == "red":
        return RGB(255,0,0)
    elif color == "orange":
        return RGB(255,127,0)
    raise GDChartError, "No such colour: %s."%color


class ChartBase(object):
    """
        Base class of both Pie and Graph chart classes.
    """
    _ImageTypes = {
        "GIF":      _gdchartc.GDC_GIF,
        "JPEG":     _gdchartc.GDC_JPEG,
        "PNG":      _gdchartc.GDC_PNG,
        "WBMP":     _gdchartc.GDC_WBMP
    }
    _FontSizes = {
        "TINY":     _gdchartc.GDC_TINY,
        "SMALL":    _gdchartc.GDC_SMALL,
        "MEDBOLD":  _gdchartc.GDC_MEDBOLD,
        "LARGE":    _gdchartc.GDC_LARGE,
        "GIANT":    _gdchartc.GDC_GIANT
    }
    _lookupOptions = {}
    _maskOptions = {}
    def __init__(self):
        self.__dict__["_options"] = {}
        self.__dict__["_width"] = 500
        self.__dict__["_height"] = 500
        self.__dict__["_data"] = None
        self.__dict__["_labels"] = None
        self.__dict__["_datalen"] = None
        self.__dict__["_scatterPoints"] = None

    def __getattr__(self, attr):
        try:
            return self.getOption(attr)
        except ValueError:
            raise AttributeError

    def __setattr__(self, attr, val):
        try:
            return self.setOption(attr, val)
        except ValueError:
            if self.__dict__.has_key(attr):
                self.__dict__[attr] = val
            else:
                raise AttributeError

    def _actualiseOptions(self):
        for i in self._defaultOptions.values():
            _gdchartc.setOption(self._myType, i[0], i[2])
        for k, v in self._options.iteritems():
            index = self._defaultOptions[k][0]
            _gdchartc.setOption(self._myType, index, v)
        _gdchartc.setScatter(self._scatterPoints)

    def setOption(self, option, myval):
        """
            Set an option. Using this function explicitly is discouraged - it
            is equivalent to using explicit attribute assignment, like so:
                myclass.foo = val
        """
        if self._defaultOptions.has_key(option):
            if self._lookupOptions.has_key(option):
                # We have to look the value up in our dictionary
                if self._lookupOptions[option].has_key(myval):
                    val = self._lookupOptions[option][myval]
                else:
                    values = ", ".join([k for k in self._lookupOptions[option].keys()])
                    raise GDChartError("%s must be one of the following: %s"%(option, values))
            elif self._maskOptions.has_key(option):
                val = 0
                for i in myval:
                    bits = self._maskOptions[option].get(i, None)
                    if bits is not None:
                        val |= bits
                    else:
                        values = ", ".join([k for k in self._maskOptions[option].keys()])
                        raise GDChartError("%s must be a list chosen from the following strings: %s"%
                                                                                        (option, values))
            else:
                # Now we do some standard format checks
                type = self._defaultOptions[option][1]
                if type == _gdchartc.OPT_FLOAT:
                    try:
                        val = float(myval)
                    except ValueError:
                        raise GDChartError("%s must be representable as a float."%(option))
                elif type in (  _gdchartc.OPT_FONTSIZE, 
                                _gdchartc.OPT_INT,
                                _gdchartc.OPT_LONG,
                                _gdchartc.OPT_SHORT,
                                _gdchartc.OPT_USHORT,
                                _gdchartc.OPT_UCHAR,
                                _gdchartc.OPT_CHAR):
                    try:
                        val = int(myval)
                    except ValueError:
                        raise GDChartError("%s must be representable as an int."%(option))
                elif type == _gdchartc.OPT_COLOR:
                    try:
                        rgb = rgbFactory(myval)
                    except GDChartError:
                        try:
                            val = int(myval)
                        except ValueError:
                            raise GDChartError("%s must be representable as an int."%(option))
                    else:
                        val = int(rgb)
                elif type == _gdchartc.OPT_PERCENT:
                    try:
                        val = int(myval)
                    except ValueError:
                        raise GDChartError("%s must be representable as an int."%(option))
                    if not (0 <= val <= 100):
                        raise GDChartError, "Percentage must be > 0, and < 100"
                elif type == _gdchartc.OPT_COLOR_A:
                    try:
                        colours = [rgbFactory(i) for i in myval]
                    except GDChartError:
                        colours = myval
                    try:
                        val = [int(i) for i in colours]
                    except ValueError:
                        raise GDChartError("%s must be representable as a list of ints."%(option))
                elif type in [_gdchartc.OPT_COLOR_A, _gdchartc.OPT_INT_A, _gdchartc.OPT_BOOL_A]:
                    try:
                        val = [int(i) for i in myval]
                    except ValueError:
                        raise GDChartError("%s must be representable as a list of ints."%(option))
                else:
                    val = myval
            self.__dict__["_options"][option] = val
        elif option == "width":
            self.__dict__["_width"] = int(myval)
        elif option == "height":
            self.__dict__["_height"] = int(myval)
        else:
            raise ValueError, "No such option: %s"%option

    def getOption(self, option):
        """
            Retrieve an option. Using this function is equivalent to just
            referring to an option as a chart-object attribute.
        """
        if self._options.has_key(option):
            # Now convert it to a value the user will recognise...
            val = self._options[option]
            if self._lookupOptions.has_key(option):
                for k, v in self._lookupOptions[option].items():
                    if v == val:
                        return k
                    else:
                        raise GDChartError, "Lookup value not known - this should never happen. Please contact software authors."
            elif self._maskOptions.has_key(option):
                lst = []
                for k, v in self._maskOptions[option].items():
                    if (val&v):
                        lst.append(k)
                return lst
            else:
                return self._options[option]
        elif self._defaultOptions.has_key(option):
            return self._defaultOptions[option][2]
        elif option == "width":
            return self._width
        elif option == "height":
            return self._height
        else:
            raise ValueError, "No such option: %s"%option

    def getAllOptions(self):
        """
            Retrieve a dictionary of all options.
        """
        x = {}
        for i in self._defaultOptions:
            x[i] = self.getOption(i)
        x["width"] = self._width
        x["height"] = self._height
        return x

    def restoreDefaultOptions(self):
        """
            Restore options to their default values. 
        """
        self._options = {}
        self._scatterPoints = None

    def setLabels(self, labels):
        """
            Set chart labels. The argument is a single list of strings.
        """
        if self._datalen:
            if len(labels) != self._datalen:
                raise GDChartError, "List of labels must have same length as data."
        self._labels = labels


class PieBase(ChartBase):
    """
        Base class of all Pie chart classes.
    """
    _myType = _gdchartc.PIE
    _defaultOptions = _gdchartc.getOptions(_gdchartc.PIE)
    _ChartTypes = {
        "3D":                   _gdchartc.GDC_3DPIE,
        "2D":                   _gdchartc.GDC_2DPIE,
    }
    _PercentPlacement = {
        "NONE":                 _gdchartc.GDCPIE_PCT_NONE,
        "ABOVE":                _gdchartc.GDCPIE_PCT_ABOVE,
        "BELOW":                _gdchartc.GDCPIE_PCT_BELOW,
        "RIGHT":                _gdchartc.GDCPIE_PCT_RIGHT,
        "LEFT":                 _gdchartc.GDCPIE_PCT_LEFT,
    }
    _lookupOptions = {
        "title_size":           ChartBase._FontSizes,
        "label_size":           ChartBase._FontSizes,
        "image_type":           ChartBase._ImageTypes,
        "percent_labels":       _PercentPlacement,
    }
    def __init__(self, *args, **kwargs):
        ChartBase.__init__(self, *args, **kwargs)

    def _conformanceCheck(self):
        if self._labels:
            if self._datalen:
                if self._datalen != len(self._labels):
                    raise GDChartError, "Datasets must be of same length as list of labels."

    def draw(self, filedef):
        """
            Draw a graph to filename. 
        """
        if not self._datalen:
            raise GDChartError, "No data to graph"
        if type(filedef) in types.StringTypes:
            filedef = open(filedef, "w")
        self._actualiseOptions()
        try:
            _gdchartc.out_pie(   self._width, 
                                    self._height,
                                    filedef,
                                    self._type,
                                    self._datalen,
                                    self._labels,               
                                    self._data,
                                )
        except _gdchartc.PGError, val:
            raise GDChartError, val

    def setData(self, *data):
        """
            Set pie data to be graphed. 
            mypie.setData(1, 2, 3, 4)
        """
        self._datalen = len(data)
        self._data = data
        self._conformanceCheck()

class Pie(PieBase): 
    """
        A 2D pie chart.
    """
    _type = _gdchartc.GDC_2DPIE

class Pie3D(PieBase): 
    """
        A 3D pie chart.
    """
    _type = _gdchartc.GDC_3DPIE


class Scatter(object):
    """
        This class represents a scatter point. You would normally construct an
        array of these to pass to the setScatter method of graph classes. 
        
        The constructor takes the following arguments:
            type        - Scatter graph types are:
                                    TRIANGLE_DOWN
                                    TRIANGLE_UP
                                    CIRCLE
            point       - X-axis co-ordinate
            val         - Y-axis co-ordinate
            width       - 0-100%
            color       - An RGB object, or an integer representing the point colour.
    """
    _ScatterTypes = {
        "TRIANGLE_DOWN":        _gdchartc.GDC_SCATTER_TRIANGLE_DOWN,
        "TRIANGLE_UP":          _gdchartc.GDC_SCATTER_TRIANGLE_UP,
        "CIRCLE":               _gdchartc.GDC_SCATTER_CIRCLE,
    }
    def __init__(self, point, val, type="TRIANGLE_DOWN", width=100, color="white"):
        self.type = type
        self.point = point
        self.val = val
        self.width = width
        try:
            color = rgbFactory(color)
        except GDChartError:
            pass
        try:
            self.color = int(color)
        except ValueError:
            raise GDChartError, "Colour must be representable as an int."

    def _setType(self, val):
        if not self._ScatterTypes.has_key(val):
            values = ", ".join([k for k in self._ScatterTypes.keys()])
            raise ValueError("Scatter type must be one of %s"%values)
        else:
            self._type = self._ScatterTypes[val]

    def _getType(self):
        for k, v in self._ScatterTypes.items():
            if (v == self._type):
                return k
        else:
            raise GDChartError("Unknown type set. This should never happen.")

    def _setWidth(self, val):
        i = int(val)
        if  (i < 0) or (i > 100): 
            raise ValueError("Width must be 0 > width > 100.")
        self._width = val

    def _getWidth(self):
        return self._width 
            
    type = property(_getType, _setType)
    width = property(_getWidth, _setWidth)


class GraphBase(ChartBase):
    """
        Base class for all Graph charts.
    """
    _myType = _gdchartc.GRAPH
    _defaultOptions = _gdchartc.getOptions(_gdchartc.GRAPH)
    _StackTypes = {
        "DEPTH":                _gdchartc.GDC_STACK_DEPTH,
        "SUM":                  _gdchartc.GDC_STACK_SUM,
        "BESIDE":               _gdchartc.GDC_STACK_BESIDE,
        "LAYER":                _gdchartc.GDC_STACK_LAYER,
    }
    _TickTypes = {
        "LABELS":               _gdchartc.GDC_TICK_LABELS,
        "POINTS":               _gdchartc.GDC_TICK_POINTS,
        "NONE":                 _gdchartc.GDC_TICK_NONE,
    }
    _BorderTypes = {
        "NONE":                 _gdchartc.GDC_BORDER_NONE,
        "ALL":                  _gdchartc.GDC_BORDER_ALL,
        "X":                    _gdchartc.GDC_BORDER_X,
        "Y":                    _gdchartc.GDC_BORDER_Y,
        "Y2":                   _gdchartc.GDC_BORDER_Y2,
        "TOP":                  _gdchartc.GDC_BORDER_TOP,
    }
    _HilocloseTypes = {
        "DIAMOND":              _gdchartc.GDC_HLC_DIAMOND,
        "CLOSE_CONNECTED":      _gdchartc.GDC_HLC_CLOSE_CONNECTED,
        "CONNECTING":           _gdchartc.GDC_HLC_CONNECTING,
        "I_CAP":                _gdchartc.GDC_HLC_I_CAP,
    }
    _lookupOptions = {
        "image_type":           ChartBase._ImageTypes,
        "stack_type":           _StackTypes,
        "grid":                 _TickTypes,
        "ticks":                _TickTypes,
        "title_font_size":      ChartBase._FontSizes,
        "xtitle_font_size":     ChartBase._FontSizes,
        "ytitle_font_size":     ChartBase._FontSizes,
        "xaxisfont_size":       ChartBase._FontSizes,
        "yaxisfont_size":       ChartBase._FontSizes,
        "annotation_font_size": ChartBase._FontSizes,
    }
    _maskOptions = {
        "hlc_style":            _HilocloseTypes,
        "border":               _BorderTypes,
    }
    def __init__(self, *args, **kwargs):
        ChartBase.__init__(self, *args, **kwargs)
        self.__dict__["_numsets"] = None
        self.__dict__["_combodata"] = None
        self.__dict__["_combodatalen"] = None
        self.__dict__["_combonumsets"] = None
        self.__dict__["_annotation"] = None

    def _conformanceCheck(self):
        if self._labels:
            if self._datalen:
                if self._datalen != len(self._labels):
                    raise GDChartError, "Datasets must be of same length as list of labels."
            if self._combodatalen:
                if self._combodatalen != len(self._labels):
                    raise GDChartError, "Combo datasets must be of same length as list of labels."
        if self._datalen:
            if self._combodatalen:
                if self._datalen != self._combodatalen:
                    raise GDChartError, "Main and combo datasets must be of same length."

    def setScatter(self, scatterpoints):
        """
            Set scatter points. This should be a list of Scatter objects.
        """
        slen = None
        if self._datalen:
            slen = self._datalen
        elif self._labels:
            slen = len(self._labels)

        if slen:
            for i in scatterpoints:
                if i.point > slen or i.point < 0:
                    raise ValueError("Scatter point value must be > 0 and < numpoints.")
        self._scatterPoints = scatterpoints

    def clearAnnotation(self):
        self._annotation = None

    def annotate(self, point=0, note = "", color="white"):
        """
            Set an annotation. At the moment the gdchart library is limited to
            one annotation per graph.
        """
        slen = None
        if self._datalen:
            slen = self._datalen
        elif self._labels:
            slen = len(self._labels)

        if slen:
            if (point>slen) or (point<0):
                raise ValueError("Annotation point value must be > 0 and < numpoints.")

        if len(note) > _gdchartc.MAX_NOTE_LEN:
                raise ValueError("Annotation note length must be < %i."%(_gdchartc.MAX_NOTE_LEN))

        try:
            intcolor = rgbFactory(color)
        except GDChartError:
            try:
                intcolor = int(color)
            except ValueError:
                raise GDChartError("color must be representable as an int.")
        intcolor = int(intcolor)

        b = _Bucket(point=point, note=note, color=intcolor)
        self._annotation = b

    def draw(self, filedef):
        """
            Draw a graph to file. 
        """
        if not self._datalen:
            raise GDChartError, "No data to graph"
        if type(filedef) in types.StringTypes:
            filedef = open(filedef, "w")
        self._actualiseOptions()
        _gdchartc.annotate(self._annotation)
        try:
            _gdchartc.out_graph(    self._width, 
                                    self._height,
                                    filedef,
                                    self._type,
                                    self._datalen,
                                    self._labels,               
                                    self._numsets,
                                    self._data,
                                    self._combodata          
                                )
        except _gdchartc.PGError, val:
            raise GDChartError, val

#
# Simple data graphs
#
class SimpleBase(GraphBase):
    """
        Base class for "Simple" graph types. 
    """
    def _getSimpleData(self, *data):
        """
            Returns the data length, the number of sets and the flattened data
        """
        length = _uniformLength(*data)
        if length < 0:
            raise GDChartError, "All data sets have to be of the same length."
        return length, _flattenList(*data)

    def setData(self, *data):
        """
            Set the data to graph. This method takes a set of lists of data,
            that should all be of the same length. I.e.
                x.setData([1, 2, 3], [4, 5, 6])
        """
        self._numsets = len(data)
        self._datalen, self._data = self._getSimpleData(*data)
        self._conformanceCheck()

class Line(SimpleBase):
    """
        A simple line graph.
    """
    _type = _gdchartc.GDC_LINE

class Area(SimpleBase):
    """
        A graph with the area under the data filled.
    """
    _type = _gdchartc.GDC_AREA

class Bar(SimpleBase):
    """
        A classical bar graph.
    """
    _type = _gdchartc.GDC_BAR

class Area3D(SimpleBase):
    """
        A 3D graph with the area under the line filled.
    """
    _type = _gdchartc.GDC_3DAREA

class Line3D(SimpleBase):
    """
        A 3D line graph.
    """
    _type = _gdchartc.GDC_3DLINE

class Bar3D(SimpleBase):
    """
        A 3D bar graph.
    """
    _type = _gdchartc.GDC_3DBAR


class MultisetGraphBase(GraphBase):
    """
        The base class of all multiset graphs.
    """
    def _getMultisetData(self, setlen, *data):
        """
            Returns the data length, the number of sets and the flattened data
        """
        baseLength = None
        allData = []
        for i in data:
            if len(i) != setlen:
                raise GDChartError("Sets of %s data lists required."%setlen)
            length = _uniformLength(*i)
            if length < 0:
                raise GDChartError, "All data sets must be of the same length."
            if baseLength:
                if length != baseLength:
                    raise GDChartError, "All data sets must be of the same length."
            else:
                baseLength = length
            allData += _flattenList(*i)
        return baseLength, allData

#
# Floating Bars
#
class FloatingBarBase(MultisetGraphBase):
    """
        Base class of all floating bar graphs. 
    """
    def setData(self, *data):
        """

            This function takes a set of data tuples, where the first element
            of the tuple are all of the lower values, and the second element
            the upper values. Eg.

            x.setData(((1, 2, 3), (4, 5, 6)), ((3, 6, 9), (6, 9, 12)))
        """
        self._numsets = len(data)
        self._datalen, self._data = self._getMultisetData(2, *data)
        self._conformanceCheck()

class FloatingBar(FloatingBarBase):
    """
        A floating bar graph. 
    """
    _type = _gdchartc.GDC_FLOATINGBAR

class FloatingBar3D(FloatingBarBase):
    """
        A 3D floating bar graph. 
    """
    _type = _gdchartc.GDC_3DFLOATINGBAR

#
# HLC
#
class HLCBase(MultisetGraphBase):
    """
        Base class for High-Low-Close graphs. 
    """
    def setData(self, *data):
        """
            Takes a list of data triplets, where the first element is high, the
            second, low, and the third close. Eg.

            x.setData(((6, 9, 12), (1, 2, 3), (5, 6, 7)))
        """
        self._numsets = len(data)
        self._datalen, self._data = self._getMultisetData(3, *data)
        self._conformanceCheck()

class HLC(HLCBase):
    _type = _gdchartc.GDC_HILOCLOSE

class HLC3D(HLCBase):
    _type = _gdchartc.GDC_3DHILOCLOSE

#
# HLC Combo Graphs
#
class HLCComboBase(HLCBase, SimpleBase):
    """
        Base class for HLC combo data.
    """
    def setComboData(self, *data):
        """
            Set the combo data for this graph. This function takes a simple
            list of data sets.
        """
        self._combonumsets = len(data)
        self._combodatalen, self._combodata = self._getSimpleData(*data)
        self._conformanceCheck()

    def draw(self, filename):
        """
            Write the graph to file. 
        """
        if not self._combodata:
            raise GDChartError, "Combo data must be specified for a combo graph."
        # We should be using super for this...
        SimpleBase.draw(self, filename)

class HLCAreaCombo(HLCComboBase):
    """
        A High-Low-Close/Area combo graph.
    """
    _type = _gdchartc.GDC_COMBO_HLC_AREA

class HLCAreaCombo3D(HLCComboBase):
    """
        A 3D High-Low-Close/Area combo graph.
    """
    _type = _gdchartc.GDC_3DCOMBO_HLC_AREA

class HLCBarCombo(HLCComboBase):
    """
        A High-Low-Close/Bar combo graph.
    """
    _type = _gdchartc.GDC_COMBO_HLC_BAR

class HLCBarCombo3D(HLCComboBase):
    """
        A 3D High-Low-Close/Bar combo graph.
    """
    _type = _gdchartc.GDC_3DCOMBO_HLC_BAR

#
# Simple Combo Graphs
#
class SimpleComboBase(SimpleBase):
    """
        Base class for "simple" combo graph types. 
    """
    def setData(self, *data):
        """
            Set the data to graph. This method takes a set of lists of data,
            that should all be of the same length. I.e.
                x.setData([1, 2, 3], [4, 5, 6])
        """
        self._numsets = len(data)
        self._datalen, self._data = self._getSimpleData(*data)
        self._conformanceCheck()

    def setComboData(self, *data):
        """
            Set the combo data to graph. This method takes a set of lists of data,
            that should all be of the same length. I.e.
                x.setComboData([1, 2, 3], [4, 5, 6])
        """
        self._combonumsets = len(data)
        self._combodatalen, self._combodata = self._getSimpleData(*data)
        self._conformanceCheck()

    def draw(self, filename):
        if not self._combodata:
            raise GDChartError, "Combo data must be specified for a combo graph."
        # We should be using super for this...
        SimpleBase.draw(self, filename)

class LineBarCombo(SimpleComboBase):
    """
        A Line/Bar combo graph.
    """
    _type = _gdchartc.GDC_COMBO_LINE_BAR

class LineAreaCombo(SimpleComboBase):
    """
        A Line/Area combo graph.
    """
    _type = _gdchartc.GDC_COMBO_LINE_AREA

class LineLineCombo(SimpleComboBase):
    """
        A Line/Line combo graph.
    """
    _type = _gdchartc.GDC_COMBO_LINE_LINE

class LineBarCombo3D(SimpleComboBase):
    """
        A 3D Line/Bar combo graph.
    """
    _type = _gdchartc.GDC_3DCOMBO_LINE_BAR

class LineAreaCombo3D(SimpleComboBase):
    """
        A 3D Line/Area combo graph.
    """
    _type = _gdchartc.GDC_3DCOMBO_LINE_AREA

class LineLineCombo3D(SimpleComboBase):
    """
        A 3D Line/Line combo graph.
    """
    _type = _gdchartc.GDC_3DCOMBO_LINE_LINE
