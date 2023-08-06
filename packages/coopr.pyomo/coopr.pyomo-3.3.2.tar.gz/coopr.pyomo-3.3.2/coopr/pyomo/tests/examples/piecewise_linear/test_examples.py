#
# Test the Pyomo command-line interface
#

import unittest
import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
scriptdir = dirname(dirname(dirname(dirname(dirname(dirname(abspath(__file__)))))))+os.sep

import coopr.pyomo
import pyutilib.subprocess
import pyutilib.th as unittest



class Test(unittest.TestCase):

    def run_convert2nl(self, cmd, file=None):
        os.chdir(currdir)
        return pyutilib.subprocess.run('pyomo2nl --symbolic-solver-labels '+cmd, outfile=file)

    def run_convert2lp(self, cmd, file=None):
        os.chdir(currdir)
        return pyutilib.subprocess.run('pyomo2lp --symbolic-solver-labels '+cmd, outfile=file)

    def test_step_lp(self):
        """Test examples/pyomo/piecewise/step.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','piecewise','step.py'), file=currdir+'step.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'step.lp')
        os.remove(currdir+'step.out')

    def test_step_nl(self):
        """Test examples/pyomo/piecewise/step.py"""
        self.run_convert2nl(os.path.join(scriptdir,'examples','pyomo','piecewise','step.py'), file=currdir+'step.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'step.nl')
        os.remove(currdir+'unknown.row')
        os.remove(currdir+'unknown.col')
        os.remove(currdir+'step.out')

    def test_affine_lp(self):
        """Test examples/pyomo/piecewise/affine.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','piecewise','affine.py'), file=currdir+'affine.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'affine.lp')
        os.remove(currdir+'affine.out')

    def test_affine_nl(self):
        """Test examples/pyomo/piecewise/affine.py"""
        self.run_convert2nl(os.path.join(scriptdir,'examples','pyomo','piecewise','affine.py'), file=currdir+'affine.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'affine.nl')
        os.remove(currdir+'unknown.row')
        os.remove(currdir+'unknown.col')
        os.remove(currdir+'affine.out')

    def test_convex_lp(self):
        """Test examples/pyomo/piecewise/convex.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','piecewise','convex.py'), file=currdir+'convex.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'convex.lp')
        os.remove(currdir+'convex.out')

    def test_convex_nl(self):
        """Test examples/pyomo/piecewise/convex.py"""
        self.run_convert2nl(os.path.join(scriptdir,'examples','pyomo','piecewise','convex.py'), file=currdir+'convex.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'convex.nl')
        os.remove(currdir+'unknown.row')
        os.remove(currdir+'unknown.col')
        os.remove(currdir+'convex.out')

    def test_indexed_lp(self):
        """Test examples/pyomo/piecewise/indexed.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','piecewise','indexed.py'), file=currdir+'indexed.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'indexed.lp')
        os.remove(currdir+'indexed.out')

    def test_indexed_nl(self):
        """Test examples/pyomo/piecewise/indexed.py"""
        self.run_convert2nl(os.path.join(scriptdir,'examples','pyomo','piecewise','indexed.py'), file=currdir+'indexed.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'indexed.nl')
        os.remove(currdir+'unknown.row')
        os.remove(currdir+'unknown.col')
        os.remove(currdir+'indexed.out')

    def test_indexed_nonlinear_nl(self):
        """Test examples/pyomo/piecewise/indexed_nonlinear.py"""
        self.run_convert2nl(os.path.join(scriptdir,'examples','pyomo','piecewise','indexed_nonlinear.py'), file=currdir+'indexed_nonlinear.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'indexed_nonlinear.nl')
        os.remove(currdir+'unknown.row')
        os.remove(currdir+'unknown.col')
        os.remove(currdir+'indexed_nonlinear.out')


if __name__ == "__main__":
    unittest.main()
