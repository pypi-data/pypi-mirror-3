import unittest, os, os.path, shutil
import _gdchartc

class uPyGDChart(unittest.TestCase):
    SCRATCH = "scratch"
    def setUp(self):
        try:
            os.mkdir(self.SCRATCH)
        except OSError:
            pass

    def tearDown(self):
        shutil.rmtree(self.SCRATCH)

    def test_constants(self):
        # Check a random constant...
        self.failUnless(hasattr(_gdchartc, "GDC_LINE"))
        # Check the single float constant
        self.failUnless(hasattr(_gdchartc, "GDC_INTERP_VALUE"))

    def test_options(self):
        self.failUnless(_gdchartc.getOptions(_gdchartc.GRAPH))
        self.failUnless(_gdchartc.getOptions(_gdchartc.PIE))

    def test_out_graph_nonfile(self):
        try:
            _gdchartc.out_graph(1, 2, 1, 1, 1, ["one", "two"], 1, [1, 2], [1, 2])
        except TypeError:
            pass
        else:
            self.fail()

    def test_out_graph_nonlist(self):
        f = file(os.path.join(self.SCRATCH, "outgraph"), "w")
        self.failUnlessRaises(TypeError, _gdchartc.out_graph, 1, 2, f, 1, 1, 2, 1, [1, 2], [1, 2])
        self.failUnlessRaises(TypeError, _gdchartc.out_graph, 1, 2, f, 1, 1, [1, 2], 1, 2, [1, 2])
        self.failUnlessRaises(TypeError, _gdchartc.out_graph, 1, 2, f, 1, 1, [1, 2], 1, [1, 2], 2)
        _gdchartc.out_graph(100, 100, f, 1, 1, [1, 2], 1, [1, 2], [1, 2])

    def test_out_graph_notfloats(self):
        f = file(os.path.join(self.SCRATCH, "outgraph"), "w")
        self.failUnlessRaises(TypeError, _gdchartc.out_graph, 1, 2, f, 1, 1, [1, 2], 1, ["one", "two"], [1, 2])

    def test_out_graph_nulls(self):
        f = file(os.path.join(self.SCRATCH, "outgraph"), "w")
        _gdchartc.out_graph(100, 100, f, 1, 1, None, 1, [1, 2], [1, 2])
        _gdchartc.out_graph(100, 100, f, 1, 1, None, 1, [1, 2], None)
        _gdchartc.out_graph(100, 100, f, 1, 1, None, 1, [1, 2], [1, 2, None, 3, None])
        self.failUnlessRaises(TypeError, _gdchartc.out_graph, 1, 2, f, 1, 1, None, 1, None, None)

    def test_out_graph_succeed(self):
        f = file(os.path.join(self.SCRATCH, "outgraph"), "w")
        _gdchartc.out_graph(100, 100, f, 1, 1, ["one", "two"], 1, [1, 2], [1, 2])


class uPyGDChartOptions(unittest.TestCase):
    def _testOption(self, setFunction, option, testvalue, chartType=_gdchartc.GRAPH):
        opts = _gdchartc.getOptions(chartType)
        val = opts[option][2]
        setFunction(chartType, opts[option][0], testvalue)
        opts = _gdchartc.getOptions(chartType)
        self.failUnlessEqual(opts[option][2], testvalue)
        # Now we restore the value...
        setFunction(chartType, opts[option][0], val)

    def test_setoptions(self):
        self._testOption(_gdchartc.setOption, "grid", 99)                              # INT 
        self._testOption(_gdchartc.setOption, "xlabel_spacing", 99)                    # SHORT
        self._testOption(_gdchartc.setOption, "perspective", 99, _gdchartc.PIE)       # USHORT
        self._testOption(_gdchartc.setOption, "threeD_angle", 20)                          # UCHAR
        self._testOption(_gdchartc.setOption, "bg_transparent", 20)                    # BOOL
        self._testOption(_gdchartc.setOption, "annotation_font_size", 20)              # FONT
        self._testOption(_gdchartc.setOption, "bar_width", 20)                         # PERCENT
        self._testOption(_gdchartc.setOption, "other_threshold", 20, _gdchartc.PIE)   # CHAR
        self._testOption(_gdchartc.setOption, "bg_color", 20)                          # LONG
        self._testOption(_gdchartc.setOption, "threeD_depth", 20)                          # FLOAT
        self._testOption(_gdchartc.setOption, "bg_image", "foinklebar")                # STRING
        self._testOption(_gdchartc.setOption, "explode", range(500), _gdchartc.PIE)   # INT_A
        bools = [1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0]
        self._testOption(_gdchartc.setOption, "xlabel_ctl", bools)                     # BOOL_A
        self._testOption(_gdchartc.setOption, "ext_color", range(500))                 # COLORL_A

class Scat:
    point = 0
    val = 0
    width = 0
    color = 0
    _type = 0
    
class uScatter(unittest.TestCase):
    def test_scatter(self):
        self.failUnlessRaises(TypeError, _gdchartc.setScatter, 1)
        s = Scat()
        s.point = "foo"
        self.failUnlessRaises(TypeError, _gdchartc.setScatter, [s, Scat(), Scat(), Scat()])
        _gdchartc.setScatter([Scat(), Scat(), Scat(), Scat()])
        _gdchartc.setScatter(None)


class Anno:
    point = 0
    color = 0
    note = "foo"

class uAnnotate(unittest.TestCase):
    def test_anno(self):
        _gdchartc.annotate(None)

        a = Anno()
        _gdchartc.annotate(a)

        _gdchartc.annotate(None)
        _gdchartc.annotate(None)

        try:
            _gdchartc.annotate(1)
        except TypeError:
            pass
        _gdchartc.annotate(None)


