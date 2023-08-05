#
# Test the Pyomo command-line interface
#

import unittest
import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep
scriptdir = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))+os.sep

import coopr.pyomo
import pyutilib.services
import pyutilib.subprocess
import pyutilib.th as unittest
import coopr.pyomo.scripting.convert as main
import StringIO
from pyutilib.misc import setup_redirect, reset_redirect
import re

if os.path.exists(sys.exec_prefix+os.sep+'bin'+os.sep+'coverage'):
    executable=sys.exec_prefix+os.sep+'bin'+os.sep+'coverage -x '
else:
    executable=sys.executable

def filter_fn(line):
    return line.startswith('Disjunct')


class Test(unittest.TestCase):

    def convert(self, cmd, type, **kwds):
        args=re.split('[ ]+',cmd)
        if 'file' in kwds:
            OUTPUT=kwds['file']
        else:
            OUTPUT=StringIO.StringIO()
        setup_redirect(OUTPUT)
        os.chdir(currdir)
        if type == 'lp':
            output = main.pyomo2lp(list(args))
        else:
            output = main.pyomo2nl(list(args))
        reset_redirect()
        if not 'file' in kwds:
            return OUTPUT.getvalue()
        return output

    def run_convert2nl(self, cmd, file=None):
        return pyutilib.subprocess.run('pyomo2nl '+cmd, outfile=file)

    def run_convert2lp(self, cmd, file=None):
        return pyutilib.subprocess.run('pyomo2lp '+cmd, outfile=file)

    def test1a(self):
        """Simple execution of 'convert2nl'"""
        self.convert('pmedian.py pmedian.dat', type='nl', file=currdir+'test1a.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'_pmedian.nl')
        os.remove(currdir+'test1a.out')

    def test1b(self):
        """Simple execution of 'pyomo2nl'"""
        self.run_convert2nl('pmedian.py pmedian.dat', file=currdir+'test1b.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'_pmedian.nl')
        os.remove(currdir+'test1b.out')

    def test2a(self):
        """Simple execution of 'convert2lp'"""
        self.convert('pmedian.py pmedian.dat', type='lp', file=currdir+'test2a.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_pmedian.lp')
        os.remove(currdir+'test2a.out')

    def test2b(self):
        """Simple execution of 'pyomo2lp'"""
        self.run_convert2lp('pmedian.py pmedian.dat', file=currdir+'test2b.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_pmedian.lp')
        os.remove(currdir+'test2b.out')

    def test3a(self):
        """Simple execution of 'convert2nl'"""
        self.convert('pmedian4.py', type='nl', file=currdir+'test3a.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'_pmedian4.nl')
        os.remove(currdir+'test3a.out')

    def test3b(self):
        """Simple execution of 'pyomo2nl'"""
        self.run_convert2nl('pmedian4.py', file=currdir+'test3b.out')
        self.assertFileEqualsBaseline(currdir+'unknown.nl', currdir+'_pmedian4.nl')
        os.remove(currdir+'test3b.out')

    def test4a(self):
        """Simple execution of 'convert2lp' with a concrete model"""
        self.convert('pmedian4.py', type='lp', file=currdir+'test4a.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_pmedian4.lp')
        os.remove(currdir+'test4a.out')

    def test4b(self):
        """Simple execution of 'pyomo2lp' with a concrete model"""
        self.run_convert2lp('pmedian4.py', file=currdir+'test4b.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_pmedian4.lp')
        os.remove(currdir+'test4b.out')

    def test_quadratic1(self):
        """Test examples/pyomo/quadratic/example1.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','quadratic','example1.py'), file=currdir+'quadratic1.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_quadratic1.lp')
        os.remove(currdir+'quadratic1.out')

    def test_quadratic2(self):
        """Test examples/pyomo/quadratic/example2.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','quadratic','example2.py'), file=currdir+'quadratic2.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_quadratic2.lp')
        os.remove(currdir+'quadratic2.out')

    def test_quadratic3(self):
        """Test examples/pyomo/quadratic/example3.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','quadratic','example3.py'), file=currdir+'quadratic3.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_quadratic3.lp')
        os.remove(currdir+'quadratic3.out')

    def test_quadratic4(self):
        """Test examples/pyomo/quadratic/example4.py"""
        self.run_convert2lp(os.path.join(scriptdir,'examples','pyomo','quadratic','example4.py'), file=currdir+'quadratic4.out')
        self.assertFileEqualsBaseline(currdir+'unknown.lp', currdir+'_quadratic4.lp')
        os.remove(currdir+'quadratic4.out')


if __name__ == "__main__":
    unittest.main()
