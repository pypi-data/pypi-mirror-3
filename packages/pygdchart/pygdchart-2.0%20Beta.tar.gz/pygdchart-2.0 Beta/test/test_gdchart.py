import unittest, os, shutil
import gdchart

class uUtilityFunctions(unittest.TestCase):
    def test_uniformLength(self):
        self.failUnlessEqual(gdchart._uniformLength(*([1, 2], [1, 2])), 2)
        self.failUnlessEqual(gdchart._uniformLength(*([1, 2],)), 2)
        self.failUnlessEqual(gdchart._uniformLength(*([1], [1, 2])), -1)

    def test_flattenList(self):
        expected = [1, 2, 3, 4]
        self.failUnless(gdchart._flattenList(*([1, 2], [3, 4])) == expected)
        self.failUnless(gdchart._flattenList(*([1, 2, 3], [4])) == expected)
        self.failUnless(gdchart._flattenList(*([1, 2, 3, 4],)) == expected)
        self.failUnless(gdchart._flattenList(*([],)) == [])

class uRGB(unittest.TestCase):
    def test_int(self):
        rgb = gdchart.RGB(0,0,0)
        self.failUnlessEqual(repr(rgb), "0x0")
        rgb.r = 0xFF 
        self.failUnlessEqual(repr(rgb), "0xff0000")
        rgb.g = 0xFF 
        self.failUnlessEqual(repr(rgb), "0xffff00")
        rgb.b = 0xFF 
        self.failUnlessEqual(repr(rgb), "0xffffff")

    def test_err(self):
        self.failUnlessRaises(ValueError, gdchart.RGB, 0, 0, 257)
        self.failUnlessRaises(ValueError, gdchart.RGB, 0, 257, 0)
        self.failUnlessRaises(ValueError, gdchart.RGB, 257, 0, 0)

    def test_rgbFactory(self):
        gdchart.rgbFactory("black")

class uChartBase(unittest.TestCase):
    def setUp(self):
        # We use the graph class to test the ChartBase functionality.
        self.g = gdchart.GraphBase()

    def test_setOption_err(self):
        self.failUnlessRaises(ValueError, self.g.setOption, "foo", 2)

    def test_setOption(self):
        self.g.setOption("hard_graphwidth", 12)

    def test_getOption(self):
        self.failUnless(self.g.getOption("hard_graphwidth") == 0)
        self.g.setOption("hard_graphwidth", 10)
        self.failUnless(self.g.getOption("hard_graphwidth") == 10)
        self.failUnlessRaises(ValueError, self.g.getOption, "foo")

    def test_getAllOptions(self):
        x = self.g.getAllOptions()["hard_graphwidth"]
        self.g.setOption("hard_graphwidth", 99)
        self.failUnlessEqual(self.g.getAllOptions()["hard_graphwidth"], 99)

    def test_noattr(self):
        try:
            self.g.asfdasdf
        except AttributeError:
            pass
        else:
            fail()

    def test_noattrSet(self):
        try:
            self.g.asfdasdf = "foo"
        except AttributeError:
            pass
        else:
            fail()


class uOptions(unittest.TestCase):
    # FIXME: Generalise this to test ALL options for both types
    def setUp(self):
        self.graph = gdchart.GraphBase()
        self.pie = gdchart.Pie()

    def _testOption(self, opType, testValue, chartType):
        """
            First we zero out all options. Then we retrieve the options, and
            check that they are zero. Then we restore the defaults, retrieve
            the options again, and check that the value agrees with the cached
            default dictionary.
        """
        # Set all options to testValue
        for i in chartType._defaultOptions:
            # Ignore constrained values
            if not chartType._lookupOptions.has_key(i) and not chartType._maskOptions.has_key(i):
                o = chartType._defaultOptions[i]
                if o[1] == opType:
                    chartType.setOption(i, testValue) 

        chartType._actualiseOptions()
        # Retrieve the options, and check that they are all testValue
        zeros = gdchart._gdchartc.getOptions(chartType._myType)
        for i in zeros:
            o = zeros[i]
            if o[1] == opType:
                # Ignore constrained values
                if not chartType._lookupOptions.has_key(i) and not chartType._maskOptions.has_key(i):
                    self.failUnlessEqual(o[2], testValue)

        # Now restore the defaults
        chartType.restoreDefaultOptions()
        chartType._actualiseOptions()

        # Retrieve the options, and check that they are all set to the defaults
        defaults = gdchart._gdchartc.getOptions(chartType._myType)
        for i in defaults:
            # Ignore constrained values
            if not chartType._lookupOptions.has_key(i) and not chartType._maskOptions.has_key(i):
                self.failUnlessEqual(defaults[i], chartType._defaultOptions[i])

    def test_options(self):
        self._testOption(gdchart._gdchartc.OPT_INT, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_COLOR, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_SHORT, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_USHORT, 0, self.pie)
        self._testOption(gdchart._gdchartc.OPT_UCHAR, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_BOOL, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_FONTSIZE, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_LONG, 0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_FLOAT, 0.0, self.graph)
        self._testOption(gdchart._gdchartc.OPT_STRING, "foo", self.graph)
        self._testOption(gdchart._gdchartc.OPT_INT_A, range(500), self.pie)
        self._testOption(gdchart._gdchartc.OPT_COLOR_A, range(500), self.pie)
        self._testOption(gdchart._gdchartc.OPT_BOOL_A, [1, 0, 1]*100, self.pie)

    def test_optionsColor(self):
        self.graph.bg_color = "black"
        self.failUnlessEqual(self.graph.bg_color, 0)

    def test_optionsColorA(self):
        self.graph.ext_color = ["black", "black", "black"]
        self.failUnlessEqual(self.graph.ext_color, [0, 0, 0])

    def test_maskOptions(self):
        self.graph.setOption("border", ("TOP", "X"))
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "border", ("TOP", "foo"))

    def test_lookupOptions(self):
        self.graph.setOption("image_type", "GIF")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "image_type", "foo")

    def test_getOptions(self):
        self.graph.setOption("border", ("TOP", "X"))

        ret = self.graph.getOption("border")
        ret.sort()
        self.failUnlessEqual(ret, ["TOP", "X"])

        ret = self.graph.border
        ret.sort()
        self.failUnlessEqual(ret, ["TOP", "X"])

        self.graph.setOption("image_type", "GIF")
        self.failUnlessEqual(self.graph.getOption("image_type"), "GIF")

    def test_getOptions_dimensions(self):
        self.graph.width
        self.graph.height

    def test_getAllOptions(self):
        self.graph.setOption("border", ("TOP", "X"))
        self.graph.setOption("image_type", "GIF")
        all = self.graph.getAllOptions()
        border = all["border"]
        border.sort()
        self.failUnlessEqual(border, ["TOP", "X"])
        self.failUnlessEqual(all["image_type"], "GIF")

    def test_typeErr(self):
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "threeD_depth", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "annotation_font_size", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "border", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "bg_color", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "xlabel_spacing", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.pie.setOption, "perspective", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "bar_width", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "bar_width", 101)
        self.graph.setOption("bar_width", 100)
        self.failUnlessRaises(gdchart.GDChartError, self.graph.setOption, "threeD_angle", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.pie.setOption, "other_threshold", "foo")
        self.failUnlessRaises(gdchart.GDChartError, self.pie.setOption, "explode", [1, 2, "a"])


class uSimpleBase(unittest.TestCase):
    def setUp(self):
        self.sb = gdchart.SimpleBase()

    def test_getSimpleData(self):
        data = [(1, 2), (3, 4), (5, 6)]
        len, lst = self.sb._getSimpleData(*data)
        self.failUnlessEqual(len, 2)
        self.failUnlessEqual(lst, [1, 2, 3, 4, 5, 6])

    def test_getSimpleDataErr(self):
        data = [(1,), (3, 4), (5, 6)]
        self.failUnlessRaises(gdchart.GDChartError, self.sb._getSimpleData, *data)

class uMultisetBase(unittest.TestCase):
    def setUp(self):
        self.fb = gdchart.FloatingBarBase()

    def test_getMultisetData(self):
        data = [
                    [ (1, 2, 3), (4, 5, 6)],
                    [ (7, 8, 9), (10, 11, 12)]
                ]
        len, lst = self.fb._getMultisetData(2, *data)
        self.failUnlessEqual(len, 3)
        self.failUnlessEqual(lst, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])

        data = [
                    [ (1, 2, 3), (4, 5, 6), (7, 8, 9)],
                    [ (10, 11, 12), (13, 14, 15), (16, 17, 18)]
                ]
        len, lst = self.fb._getMultisetData(3, *data)
        self.failUnlessEqual(len, 3)
        self.failUnlessEqual(lst, range(1, 19))

    def test_getMultisetDataErr(self):
        data = [
                    [ (1, 2, 3), (4, 5, 6)],
                    [ (7, 8, 9), (11, 12)]
                ]
        self.failUnlessRaises(gdchart.GDChartError, self.fb._getMultisetData, 2, *data)

        data = [
                    [ (1, 2, 3), (4, 5, 6)],
                    [ (7, 8, 9)]
                ]
        self.failUnlessRaises(gdchart.GDChartError, self.fb._getMultisetData, 2, *data)

        data = [
                    [ (1, 2, 3), (4, 5, 6)],
                    [ (1, 2, 3), (4, 5, 6)],
                    [ (7, 8), (11, 12)]
                ]
        self.failUnlessRaises(gdchart.GDChartError, self.fb._getMultisetData, 2, *data)


class uConformanceErrors(unittest.TestCase):
    def test_conformance(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setLabels, range(10))

        gd = gdchart.Line()
        gd.setLabels(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setData, range(10))
        
        gd = gdchart.LineLineCombo()
        gd.setLabels(range(100))
        gd.setComboData(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setData, range(10))

        gd = gdchart.LineLineCombo()
        gd.setComboData(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setData, range(10))

        gd = gdchart.LineLineCombo()
        gd.setLabels(range(100))
        gd.setData(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setComboData, range(10))

        gd = gdchart.LineLineCombo()
        gd.setLabels(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setData, range(10))

        gd = gdchart.LineLineCombo()
        gd.setLabels(range(100))
        gd.setData(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setComboData, range(10))

    def test_conformance(self):
        gd = gdchart.Pie()
        gd.setLabels(range(100))
        self.failUnlessRaises(gdchart.GDChartError, gd.setData, range(10))


class uComboErrors(unittest.TestCase):
    def test_comboerr(self):
        gd = gdchart.HLCAreaCombo()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        self.failUnlessRaises(gdchart.GDChartError, gd.draw, os.path.join("error"))

        gd = gdchart.LineBarCombo()
        gd.setData((5, 7, 10))
        gd.setLabels([1, 2, 3])
        self.failUnlessRaises(gdchart.GDChartError, gd.draw, os.path.join("error"))


class uPie(unittest.TestCase):
    def setUp(self):
        self.gp = gdchart.Pie()

    def test_empty(self):
        self.failUnlessRaises(gdchart.GDChartError, self.gp.draw, "err")
        

class uPieSuite(unittest.TestCase):
    OUTPUT = "testgraphs"
    def setUp(self):
        try:
            os.mkdir(self.OUTPUT)
        except OSError:
            pass

    def test_simple(self):
        p = gdchart.Pie()
        p.setData(*range(5))
        p.setLabels(range(5))
        colors = ["red", "green", "blue", "yellow", "orange"]
        p.color = colors
        p.draw(os.path.join(self.OUTPUT, "pie.png"))

    def test_simple3d(self):
        p = gdchart.Pie3D()
        p.setData(*range(5))
        p.setLabels(range(5))
        colors = [
                    gdchart.rgbFactory("red"),
                    gdchart.rgbFactory("green"),
                    gdchart.rgbFactory("blue"),
                    gdchart.rgbFactory("yellow"),
                    gdchart.rgbFactory("orange"),
                ]
        p.color = colors
        p.draw(os.path.join(self.OUTPUT, "pie3d.png"))

    def test_explode(self):
        p = gdchart.Pie3D()
        p.setData(*range(5))
        p.setLabels(range(5))
        colors = [
                    gdchart.rgbFactory("red"),
                    gdchart.rgbFactory("green"),
                    gdchart.rgbFactory("blue"),
                    gdchart.rgbFactory("yellow"),
                    gdchart.rgbFactory("orange"),
                ]
        p.color = colors
        p.explode = [0, 0, 0, 20, 80]
        p.draw(os.path.join(self.OUTPUT, "explode.png"))

    def test_drawtofp(self):
        p = gdchart.Pie()
        p.setData(*range(5))
        p.setLabels(range(5))
        colors = ["red", "green", "blue", "yellow", "orange"]
        p.color = colors
        f = file(os.path.join(self.OUTPUT, "tofile-pie.png"), "w")
        p.draw(f)


class uScatter(unittest.TestCase):
    def setUp(self):
        self.s = gdchart.Scatter(0, 0)

    def test_type(self):
        try:
            self.s.type = "foo"
        except ValueError:
            pass
        else:
            self.fail()
        self.s.type = "TRIANGLE_DOWN"
        self.failUnlessEqual(self.s.type, "TRIANGLE_DOWN")

    def test_width(self):
        try:
            self.s.width = "foo"
        except ValueError:
            pass
        else:
            self.fail()
        try:
            self.s.width = 101
        except (ValueError):
            pass
        else:
            self.fail()
        self.s.width = 99
        self.failUnlessEqual(self.s.width, 99)

    def test_setScatter(self):
        gd = gdchart.GraphBase()
        gd.setLabels(["one", "two", "three"])
        scats = []
        for i in range(10):
            s = gdchart.Scatter(0, 0)
            s.point = i 
            scats.append(s)
        self.failUnlessRaises(ValueError, gd.setScatter, scats)


class uAnnotate(unittest.TestCase):
    def setUp(self):
        self.s = gdchart.GraphBase()

    def test_datalen(self):
        self.s._datalen = 5
        self.failUnlessRaises(ValueError, self.s.annotate, 10)

        self.s._datalen = None
        self.s._labels = [1, 2, 3]
        self.failUnlessRaises(ValueError, self.s.annotate, 10)

    def test_label(self):
        self.s._labels = ["one", "two", "three"]
        self.failUnlessRaises(ValueError, self.s.annotate, 10)
        
    def test_label(self):
        self.failUnlessRaises(ValueError, self.s.annotate, 10, "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

    def test_color(self):
        self.failUnlessRaises(gdchart.GDChartError, self.s.annotate, 10, color="foo")

    def test_clear(self):
        self.s.annotate(10, "aaaaaaaaa", 1)
        self.s.clearAnnotation()
        self.failIf(self.s._annotation)


class uGraphSuite(unittest.TestCase):
    OUTPUT = "testgraphs"
    def setUp(self):
        try:
            os.mkdir(self.OUTPUT)
        except OSError:
            pass

    def test_size(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "sizetest-default.png"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("width", 0) 
        self.failUnlessRaises(gdchart.GDChartError, gd.draw, os.path.join(self.OUTPUT, "error"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("width", 500)
        gd.setOption("height", 0)
        self.failUnlessRaises(gdchart.GDChartError, gd.draw, os.path.join(self.OUTPUT, "error"))

        gd = gdchart.Line()
        gd.setOption("width", 60)
        gd.setOption("height",  60)
        gd.setData(range(2))
        gd.setLabels(range(2))
        gd.draw(os.path.join(self.OUTPUT, "sizetest-tiny.png"))

        gd = gdchart.Line()
        gd.setOption("width", 1000)
        gd.setOption("height", 1000)
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "sizetest-big.png"))

    def test_mydata(self):
        gd = gdchart.Line()
        gd.setData(range(100000))
        gd.setLabels(range(100000))
        gd.draw(os.path.join(self.OUTPUT, "data-big.png"))

        gd = gdchart.Line()
        gd.setData(range(1))
        gd.setLabels(range(1))
        gd.draw(os.path.join(self.OUTPUT, "data-small.png"))

        gd = gdchart.Line()
        gd.setData([])
        gd.setLabels([])
        self.failUnlessRaises(gdchart.GDChartError, gd.draw, os.path.join(self.OUTPUT, "error"))

    def test_simpleTypes(self):
        gd = gdchart.Line()
        gd.setData(range(100), range(100, 0, -1))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "types-Line.png"))

        gd = gdchart.Line3D()
        gd.setData(range(100), range(100, 0, -1))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "types-Line3D.png"))

        gd = gdchart.Area()
        gd.setData(range(100), range(100, 0, -1))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "types-Area.png"))

        gd = gdchart.Area3D()
        gd.setData(range(100), range(100, 0, -1))
        gd.setLabels(range(100))
        gd.draw(os.path.join(self.OUTPUT, "types-Area3D.png"))

        gd = gdchart.Bar()
        gd.setData((50, 100, 300))
        gd.setLabels([50, 100, 300])
        gd.draw(os.path.join(self.OUTPUT, "types-Bar.png"))

        gd = gdchart.Bar3D()
        gd.setData((50, 100, 300))
        gd.setLabels([50, 100, 300])
        gd.draw(os.path.join(self.OUTPUT, "types-Bar.png"))

    def test_floatingBarTypes(self):
        gd = gdchart.FloatingBar()
        gd.setData(((1, 2, 3), (5, 6, 7)))
        gd.setLabels([1, 2, 3])
        gd.draw(os.path.join(self.OUTPUT, "types-floatingBar.png"))

        gd = gdchart.FloatingBar3D()
        gd.setData(((1, 2, 3), (5, 6, 7)))
        gd.setLabels([1, 2, 3])
        gd.draw(os.path.join(self.OUTPUT, "types-floatingBar3D.png"))

    def test_HLCTypes(self):
        gd = gdchart.HLC()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.draw(os.path.join(self.OUTPUT, "types-HLC.png"))

        gd = gdchart.HLC3D()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.draw(os.path.join(self.OUTPUT, "types-HLC3D.png"))

    def test_HLCComboTypes(self):
        gd = gdchart.HLCAreaCombo()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.setComboData((5, 7, 10))
        gd.draw(os.path.join(self.OUTPUT, "types-HLCAreaCombo.png"))

        gd = gdchart.HLCAreaCombo3D()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.setComboData((5, 7, 10))
        gd.draw(os.path.join(self.OUTPUT, "types-HLCAreaCombo3D.png"))

        gd = gdchart.HLCBarCombo()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.setComboData((5, 7, 10))
        gd.draw(os.path.join(self.OUTPUT, "types-HLCBarCombo.png"))

        gd = gdchart.HLCBarCombo3D()
        gd.setData(((5, 7, 10), (0, 2, 4), (3, 4, 6)))
        gd.setLabels([1, 2, 3])
        gd.setComboData((5, 7, 10))
        gd.draw(os.path.join(self.OUTPUT, "types-HLCBarCombo3D.png"))

    def test_SimpleComboTypes(self):
        gd = gdchart.LineBarCombo()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineBarCombo.png"))

        gd = gdchart.LineAreaCombo()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineAreaCombo.png"))

        gd = gdchart.LineLineCombo()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineLineCombo.png"))

        gd = gdchart.LineBarCombo3D()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineBarCombo3D.png"))

        gd = gdchart.LineAreaCombo3D()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineAreaCombo3D.png"))

        gd = gdchart.LineLineCombo3D()
        gd.setData(range(5))
        gd.setComboData(range(5, 0, -1))
        gd.setLabels(range(5))
        gd.draw(os.path.join(self.OUTPUT, "types-LineLineCombo3D.png"))

    def test_colors(self):
        gd = gdchart.Line()
        colorPath = os.path.join(self.OUTPUT, "colors")
        try:
            os.mkdir(colorPath)
        except OSError:
            pass
        gd.setOption("width", 100)
        gd.setOption("height", 100)
        gd.setData(range(10))
        gd.setLabels(range(10))
        x = gdchart.RGB()
        for r in range(0, 256, 64):
            x.r = r
            for g in range(0, 256, 64):
                x.g = g
                for b in range(0, 256, 64):
                    x.b = b
                    gd.setOption("bg_color", x)
                    gd.draw(os.path.join(colorPath, "color-%s.png"%int(x)))

    def test_scolors(self):
        gd = gdchart.Bar()
        gd.setData(range(5), range(2, 7), range(4, 9))
        colors = [
            gdchart.rgbFactory("red"),
            gdchart.rgbFactory("blue"),
            gdchart.rgbFactory("green"),
        ]
        gd.set_color = colors
        gd.draw(os.path.join(self.OUTPUT, "set_color.png"))

    def test_xlabel_ctl(self):
        gd = gdchart.Bar()
        gd.setData(range(5))
        gd.setLabels(range(5))
        gd.xlabel_ctl = [1, 0, 1, 0, 1]
        gd.draw(os.path.join(self.OUTPUT, "xlabel_ctl.png"))
        
    def test_options(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("title", "Main Title")
        gd.draw(os.path.join(self.OUTPUT, "titles.png"))

    def test_maskoptions(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("border", ("TOP", "X"))
        gd.draw(os.path.join(self.OUTPUT, "borders.png"))

    def test_fonts(self):
        fontPath = os.path.join(self.OUTPUT, "fonts")
        try:
            os.mkdir(fontPath)
        except OSError:
            pass
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("ytitle_font_size", "TINY")
        gd.setOption("xtitle_font_size", "TINY")
        gd.draw(os.path.join(fontPath, "TINY.png"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("ytitle_font_size", "SMALL")
        gd.setOption("xtitle_font_size", "SMALL")
        gd.draw(os.path.join(fontPath, "SMALL.png"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("ytitle_font_size", "MEDBOLD")
        gd.setOption("xtitle_font_size", "MEDBOLD")
        gd.draw(os.path.join(fontPath, "MEDBOLD.png"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("ytitle_font_size", "LARGE")
        gd.setOption("xtitle_font_size", "LARGE")
        gd.draw(os.path.join(fontPath, "LARGE.png"))

        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.setOption("xtitle", "xtitle")
        gd.setOption("ytitle", "ytitle")
        gd.setOption("ytitle_font_size", "GIANT")
        gd.setOption("xtitle_font_size", "GIANT")
        gd.draw(os.path.join(fontPath, "GIANT.png"))

    def test_scatter(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.grid = "NONE"
        scats = [
            gdchart.Scatter(10, 30, type="CIRCLE", width=100, color=gdchart.rgbFactory("red")),
            gdchart.Scatter(30, 50, width=100, color=gdchart.rgbFactory("blue")),
        ]
        gd.setScatter(scats)
        gd.draw(os.path.join(self.OUTPUT, "scatter.png"))

    def test_annotate(self):
        gd = gdchart.Line()
        gd.setData(range(100))
        gd.setLabels(range(100))
        gd.annotate(5, "foo")
        gd.draw(os.path.join(self.OUTPUT, "annotate.png"))

    def test_missingvalues(self):
        gd = gdchart.Bar()
        gd.setData([1, 2, None, 3, None, 5])
        gd.draw(os.path.join(self.OUTPUT, "missingvalues.png"))

    def test_tofile(self):
        gd = gdchart.Line()
        gd.setData(range(100), range(100, 0, -1))
        gd.setLabels(range(100))
        f = file(os.path.join(self.OUTPUT, "tofile-graph.png"), "w")
        gd.draw(f)


