#
# Unit Tests for Piecewise
#

import os
import sys
from os.path import abspath, dirname
currdir = dirname(abspath(__file__))+os.sep

from coopr.pyomo import *
import pyutilib.th as unittest
import pyutilib.services

class TestMiscPiecewise(unittest.TestCase):

    # test that the Piecewise component
    # does not overwrite a possibly existing
    # model component. This could lead to an 
    # extremely difficult debugging situation
    # for a user. If Piecewise is derived from Block
    # then this should be handled trivialy
    def test_no_overwrite(self):
        
        name = 'None_SOS2_y'
        val = 2.187
        
        model = ConcreteModel()
        model.x = Var(bounds=(-1,1))
        model.y = Var()
        setattr(model,name,val)

        model.con = Piecewise(model.y,\
                                  model.x,\
                                  pw_pts=[-1,0,1],\
                                  force_pw=True,\
                                  pw_constr_type='EQ',\
                                  f_rule=lambda model,x: x**2)

        # check that Piecewise did actually create a component with 
        # the name above so that we can make sure this test is not
        # erroneously passing
        self.assertTrue(name == model.con._data[None]._vars[0].name)
        # check that the original model component did not get
        # overwritten by piecewise
        self.assertEqual(getattr(model,name),val)

    # test that indexed Piecewise can handle
    # non-indexed vars
    def test_indexed_with_nonindexed_vars(self):
        model = ConcreteModel()
        model.range1 = Var()

        model.x = Var(bounds=(-1,1))
        args = ([1],model.range1,model.x)
        keywords = {'pw_pts':{1:[-1,0,1]},\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,i,x: x**2}
        model.con1 = Piecewise(*args,**keywords)

        model.range2 = Var([1])
        model.y = Var([1],bounds=(-1,1))
        args = ([1],model.range2,model.y)
        model.con2 = Piecewise(*args,**keywords)

        args = ([1],model.range2,model.y[1])
        model.con3 = Piecewise(*args,**keywords)

    # test that nonindexed Piecewise can handle
    # _VarData (e.g model.x[1]
    def test_nonindexed_with_indexed_vars(self):
        model = ConcreteModel()
        model.range = Var([1])

        model.x = Var([1],bounds=(-1,1))
        args = (model.range[1],model.x[1])
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con1 = Piecewise(*args,**keywords)

    # test that Piecewise can be initialized on
    # an abstract model
    def test_abstract_piecewise(self):
        model = AbstractModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        instance = model.create()

    # test that Piecewise can be initialized on
    # a concrete model
    def test_concrete_piecewise(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)

class TestInvalidPiecewise(unittest.TestCase):


    # test the that Piecewise component raises
    # an exception when the LOG/DLOG reps
    # are requested without a (2^n)+1 length
    # pw_pts list
    def test_dlog_bad_length(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'pw_repn':'DLOG',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)

        try:
            keywords['pw_pts'] = [-1,0,0.5,1]
            model.con3 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with DLOG an pw_pts list with length not "\
                      "equal to (2^n)+1.")

    # test the that Piecewise component raises
    # an exception when the LOG/DLOG reps
    # are requested without a (2^n)+1 length
    # pw_pts list
    def test_log_bad_length(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'pw_repn':'LOG',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)

        try:
            keywords['pw_pts'] = [-1,0,0.5,1]
            model.con3 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with LOG an pw_pts list with length not "\
                      "equal to (2^n)+1.")

    # test the that Piecewise component raises
    # an exception with an unsorted list of
    # domain points
    def test_unsorted_pw_pts(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)

        try:
            keywords['pw_pts'] = [0,-1,1]
            model.con3 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with unsorted domain points.")

    # test the that Piecewise component raises
    # an exception when initialized without
    # a valid f_rule keyword
    def test_bad_f_rules(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)

        try:
            del keywords['f_rule']
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "without a proper f_rule keyword.")

        try:
            keywords['f_rule'] = None
            model.con2 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "without a proper f_rule keyword.")

        try:
            keywords['f_rule'] = model.x
            model.con3 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "without a proper f_rule keyword.")

    # test the that Piecewise component raises
    # an exception if the domain variable arguments
    # are not actually Pyomo vars
    def test_bad_var_args(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            args = (None,model.x)
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "without Pyomo vars as variable args.")

        try:
            args = (model.range,None)
            model.con2 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "without Pyomo vars as variable args.")

    # test the that Piecewise component raises
    # an exception if the piecewise bound type is
    # a bad value
    def test_bad_bound_type(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            keywords['pw_constr_type'] = 1.0
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with invalid bound type.")
        try:
            del keywords['pw_constr_type']
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with invalid bound type.")

    # test the that Piecewise component raises
    # an exception if the piecewise representation
    # keyword has an invalid value
    def test_bad_repn(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            keywords['pw_repn'] = 1.0
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with invalid piecewise representation.")

    # test the that Piecewise component raises
    # an exception if the warning_tol
    # keyword has an invalid value
    def test_bad_warning_tol(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            keywords['warning_tol'] = None
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with invalid warning_tol.")

    # test the that Piecewise component raises
    # an exception if initialized with an invalid
    # number of args
    def test_bad_args_count(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            args = (model.range,)
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with less than two arguments.")

    # test the that Piecewise component raises
    # an exception if initialized with an unbounded
    # domain variable
    def test_unbounded_var(self):
        model = ConcreteModel()
        model.range = Var()

        model.x = Var(bounds=(-1,1))
        args = (model.range,model.x)
        keywords = {'pw_pts':[-1,0,1],\
                    'pw_constr_type':'EQ',\
                    'f_rule':lambda model,x: x**2}
        model.con = Piecewise(*args,**keywords)
        try:
            model.x.setlb(None)
            model.x.setub(None)
            model.con1 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with unbounded domain variable.")
            
        model.y = Var(bounds=(0,None))
        try:
            args = (model.range,model.y)
            model.con2 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with unbounded domain variable.")
        
        model.z = Var(bounds=(None,10))
        try:
            args = (model.range,model.z)
            model.con3 = Piecewise(*args,**keywords)
        except Exception:
            pass
        else:
            self.fail("Piecewise should fail when initialized "\
                      "with unbounded domain variable.")


if __name__ == "__main__":
    unittest.main()
     
        
