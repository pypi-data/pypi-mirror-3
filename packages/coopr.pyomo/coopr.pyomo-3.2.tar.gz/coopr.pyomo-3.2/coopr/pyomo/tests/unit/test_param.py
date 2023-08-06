#
# Unit Tests for Param() Objects
#
# PyomoModel                Base test class
# SimpleParam                Test singleton parameter
# ArrayParam1                Test arrays of parameters
# ArrayParam2                Test arrays of parameter with explicit zero default
# ArrayParam3                Test arrays of parameter with nonzero default
# TestIO                Test initialization from an AMPL *.dat file
#

import pyutilib.th as unittest
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/../..")
from coopr.pyomo import *
import math

class PyomoModel(unittest.TestCase):

    def config_repn(self):
        self.repn = 'pyomo_dict'

    def setUp(self):
        self.config_repn()
        self.model = AbstractModel()

    def construct(self,filename):
        self.instance = self.model.create(filename)


class SimpleParam(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.A = Param(initialize=3.3, repn=self.repn)
        self.instance = self.model.create()

    def tearDown(self):
        if os.path.exists("param.dat"):
            os.remove("param.dat")

    def test_value(self):
        """Check the value of the parameter"""
        tmp = value(self.instance.A)
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 3.3 )
        tmp = float(self.instance.A)
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 3.3 )
        tmp = int(self.instance.A)
        self.assertEqual( type(tmp), int)
        self.assertEqual( tmp, 3 )

    def test_getattr(self):
        """Check the use of the __getattr__ method"""
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.assertEqual( self.instance.A.value, 3.3)
        else:
            self.assertEqual( self.instance.A, 3.3)

    def test_setattr_value(self):
        """Check the use of the __setattr__ method"""
        self.instance.A = 3.3
        self.assertEqual( self.instance.A, 3.3)
        self.assertEqual( self.instance.components.A[None], 3.3)
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.assertEqual( self.instance.A.value, 3.3)
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.instance.A.value = 4.3
            self.assertEqual( self.instance.A.value, 4.3)
            try:
                self.instance.A.value = 'A'
            except ValueError:
                self.fail("fail test_setattr_value")
            else:
                #
                # NOTE: we can set bad values into a NumericValue object
                #
                pass

    def test_setattr_default(self):
        """Check the use of the __setattr__ method"""
        self.model.A = Param(repn=self.repn, default=4.3)
        self.instance = self.model.create()
        self.assertEqual( value(self.instance.A), 4.3)
        self.assertEqual( self.instance.components.A[None], 4.3)

    def test_dim(self):
        """Check the use of dim"""
        self.assertEqual( self.instance.components.A.dim(), 0)

    def test_keys(self):
        """Check the use of keys"""
        self.assertEqual( len(self.instance.components.A.keys()), 1)

    def test_len(self):
        """Check the use of len"""
        self.assertEqual( len(self.instance.components.A), 1)

    def test_getitem(self):
        import coopr.pyomo.base.param
        #print 'xxx',self.instance.components.components()
        #print 'XXX',type(self.instance.A),self.instance.A,self.instance.components.A,'YY'
        #print 'yyy',self.model.A.repn
        #print 'YYY', type(self.instance.A[None])
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.assertTrue(isinstance(self.instance.A[None], coopr.pyomo.base.param._ParamData))
        self.assertEqual( self.instance.components.A[None], 3.3)

    def test_check_values(self):
        """Check the use of check_values"""
        self.instance.components.A.check_values()


class MSimpleParam(SimpleParam):

    def config_repn(self):
        self.repn = 'sparse_dict'

MSimpleParam = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MSimpleParam)


class ArrayParam1(SimpleParam):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3}, repn=self.repn)
        self.instance = self.model.create()

    def test_value(self):
        try:
            tmp = value(self.instance.A)
        except ValueError:
            pass
        else:
            self.fail("test_value")
        try:
            tmp = float(self.instance.A)
        except TypeError:
            pass
        except ValueError:
            pass
        else:
            self.fail("test_value")
        try:
            tmp = int(self.instance.A)
        except TypeError:
            pass
        except ValueError:
            pass
        else:
            self.fail("test_value")
        tmp = value(self.instance.A[1])
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 1.3 )
        tmp = float(self.instance.A[1])
        self.assertEqual( type(tmp), float)
        self.assertEqual( tmp, 1.3 )
        tmp = int(self.instance.A[1])
        self.assertEqual( type(tmp), int)
        self.assertEqual( tmp, 1 )

    def test_call(self):
        """Check the use of the __call__ method"""
        try:
            tmp = self.instance.A()
        except TypeError:
            pass
        else:
            self.fail("test_call")

    def test_getattr(self):
        """Check the use of the __getattr__ method"""
        try:
            tmp = self.instance.A.value
        except AttributeError:
            pass
        else:
            self.fail("test_call")

    def test_setattr_value(self):
        """Check the use of the __setattr__ method"""
        import coopr.pyomo.base.param
        self.instance.components.A.value = 4.3
        #print type(self.instance.components.A)
        self.instance.components.A = 4.3
        #print type(self.instance.components.A)
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.instance.A[1].value = 4.3
            self.assertEqual( type(self.instance.A[1]), coopr.pyomo.base.param._ParamData)
        self.instance.A[1] = 4.3
        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.assertEqual( type(self.instance.A[1]), coopr.pyomo.base.param._ParamData)
        else:
            self.assertEqual( type(self.instance.A[1]), float)


    def test_setitem(self):
        """Check the use of the __setattr__ method"""
        self.instance.A[3] = 4.3
        self.assertEqual( self.instance.A[3], 4.3)
        self.instance.A[1] = 4.3
        self.assertEqual( self.instance.A[1], 4.3)
        try:
            self.instance.A[3] = 'A'
        except ValueError:
            self.fail("fail test_setitem")
        try:
            self.instance.A[2] = 4.3
            self.fail("Expected KeyError because 2 is not a valid key")
        except KeyError:
            pass

    def test_keys(self):
        """Check the use of keys"""
        self.assertEqual( len(self.instance.A.keys()), 1)

    def test_dim(self):
        """Check the use of dim"""
        self.assertEqual( self.instance.components.A.dim(), 1)

    def test_len(self):
        """Check the use of len"""
        self.instance.A[3] = 4.3
        self.assertEqual( len(self.instance.A), 2)

    def test_index(self):
        """Check the use of index"""
        self.instance.A[3] = 4.3
        self.assertEqual( len(self.instance.A.index()), 2)

    def test_getitem(self):
        import coopr.pyomo.base.param
        try:
            self.assertEqual( self.instance.A[1], 1.3)
        except KeyError:
            self.fail("test_getitem")

        if self.instance.components.A.repn_type == 'pyomo_dict':
            self.assertEqual(type(self.instance.A[1]), coopr.pyomo.base.param._ParamData)
        else:
            self.assertEqual(type(self.instance.A[1]), float)

        try:
            self.instance.A[3]
        except KeyError:
            pass
        except ValueError:
            pass
        else:
            self.fail("test_getitem")


class MArrayParam1(ArrayParam1):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam1 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam1)


class ArrayParam2(ArrayParam1):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3}, default=0.0, repn=self.repn)
        self.instance = self.model.create()

    def test_setattr_default(self):
        """Check the use of the __setattr__ method"""
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, repn=self.repn, default=4.3)
        self.instance = self.model.create()
        self.assertEqual( self.instance.A[3], 4.3)

    def test_keys(self):
        """Check the use of keys"""
        self.assertEqual( len(self.instance.A.keys()), 2)

    def test_len(self):
        """Check the use of len"""
        self.assertEqual( len(self.instance.A), 2)

    def test_getitem(self):
        try:
            self.assertEqual( self.instance.A[None], 0.0)
        except KeyError:
            pass
        else:
            if self.instance.components.A.repn_type == 'pyomo_dict':
                self.fail("test_getitem")
        self.assertEqual( self.instance.A[1], 1.3)
        self.assertEqual( self.instance.A[3], 0)


class MArrayParam2(ArrayParam2):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam2 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam2)

class ArrayParam3(ArrayParam2):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize={1:1.3}, default=99.0, repn=self.repn)
        self.instance = self.model.create()

    def test_len(self):
        """Check the use of len"""
        self.assertEqual( len(self.instance.A), 2)

    def test_getitem(self):
        try:
            self.assertEqual( self.instance.A[None], 0.0)
        except AssertionError:
            if self.instance.components.A.repn_type == 'pyomo_dict':
                self.fail("test_getitem")
        except KeyError:
            pass
        else:
            self.fail("test_getitem")
        self.assertEqual( self.instance.A[1], 1.3)
        self.assertEqual( self.instance.A[3], 99.0)


class MArrayParam3(ArrayParam3):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam3 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam3)


class ArrayParam4(ArrayParam3):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        self.model.A = Param(self.model.Z, initialize=1.3, repn=self.repn)
        self.instance = self.model.create()

    def test_keys(self):
        """Check the use of keys"""
        self.assertEqual( len(self.instance.A.keys()), 2)

    def test_len(self):
        """Check the use of len"""
        self.assertEqual( len(self.instance.A), 2)

    def test_getitem(self):
        try:
            self.assertEqual( self.instance.A[None], 0.0)
        except KeyError:
            pass
        else:
            self.fail("test_getitem")
        self.assertEqual( self.instance.A[1], 1.3)
        self.assertEqual( self.instance.A[3], 1.3)


class MArrayParam4(ArrayParam4):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam4 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam4)


class ArrayParam5(ArrayParam4):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)
        #
        # Create model instance
        #
        self.model.Z = Set(initialize=[1,3])
        def A_init(model, i):
            return 1.3
        self.model.A = Param(self.model.Z, initialize=A_init, repn=self.repn)
        self.instance = self.model.create()


class MArrayParam5(ArrayParam5):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam5 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam5)


class ArrayParam6(PyomoModel):

    def test_index1(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            for i in model.A:
                if i%2 == 0:
                    yield i
        def B_init(model, i, j):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init, repn=self.repn)
        self.instance = self.model.create()
        #self.instance.pprint()
        self.assertEqual(set(self.instance.B.keys()),set([(0,True),(2,True),(0,   False),(2,False)]))
        self.assertEqual(self.instance.B[0,True],2)
        self.assertEqual(self.instance.B[0,False],-2)
        self.assertEqual(self.instance.B[2,True],4)
        self.assertEqual(self.instance.B[2,False],-4)

    def test_index2(self):
        self.model.A = Set(initialize=range(0,4))
        @set_options(dimen=3)
        def B_index(model):
            return [(i,2*i,i*i) for i in model.A if i%2 == 0]
        def B_init(model, i, ii, iii, j):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init, repn=self.repn)
        self.instance = self.model.create()
        #self.instance.pprint()
        self.assertEqual(set(self.instance.B.keys()),set([(0,0,0,True),(2,4,4,True),(0,0,0,False),(2,4,4,False)]))
        self.assertEqual(self.instance.B[0,0,0,True],2)
        self.assertEqual(self.instance.B[0,0,0,False],-2)
        self.assertEqual(self.instance.B[2,4,4,True],4)
        self.assertEqual(self.instance.B[2,4,4,False],-4)

    def test_index3(self):
        self.model.A = Set(initialize=range(0,4))
        def B_index(model):
            return [(i,2*i,i*i) for i in model.A if i%2 == 0]
        def B_init(model, i, ii, iii, j):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init, repn=self.repn)
        try:
            self.instance = self.model.create()
            self.fail("Expected ValueError because B_index returns a tuple")
        except ValueError:
            pass

    def test_index4(self):
        self.model.A = Set(initialize=range(0,4))
        @set_options(within=Integers)
        def B_index(model):
            return [i/2.0 for i in model.A]
        def B_init(model, i, j):
            if j:
                return 2+i
            return -(2+i)
        self.model.B = Param(B_index, [True,False], initialize=B_init, repn=self.repn)
        try:
            self.instance = self.model.create()
            self.fail("Expected ValueError because B_index returns invalid index values")
        except ValueError:
            pass

    def test_dimen1(self):
        model=AbstractModel()
        model.A = Set(dimen=2, initialize=[(1,2),(3,4)])
        model.B = Set(dimen=3, initialize=[(1,1,1),(2,2,2),(3,3,3)])
        model.C = Set(dimen=1, initialize=[9,8,7,6,5])
        model.x = Param(model.A, model.B, model.C, initialize=-1, repn=self.repn)
        model.y = Param(model.B, initialize=(1,1), repn=self.repn)
        instance=model.create()
        self.assertEqual( instance.components.x.dim(), 6)
        self.assertEqual( instance.components.y.dim(), 3)

    def test_setitem(self):
        model = ConcreteModel()
        model.a = Set(initialize=[1,2,3])
        model.b = Set(initialize=['a','b','c'])
        model.c = model.b * model.b
        model.p = Param(model.a, model.c, within=NonNegativeIntegers, default=0)
        model.p[1,'a','b'] = 1
        model.p[(1,'b'),'b'] = 1
        try:
            model.p[1,5,7] = 1
            self.fail("Expected KeyError")
        except KeyError:
            pass

class MArrayParam6(ArrayParam6):

    def config_repn(self):
        self.repn = 'sparse_dict'

MArrayParam6 = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MArrayParam6)


class TestIO(PyomoModel):

    def setUp(self):
        #
        # Create Model
        #
        PyomoModel.setUp(self)

    def tearDown(self):
        if os.path.exists("param.dat"):
            os.remove("param.dat")

    def test_io1(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param A := 3.3;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Param(repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( value(self.instance.A), 3.3 )

    def test_io2(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param A :="
        print >>OUTPUT, "1 2.2"
        print >>OUTPUT, "3 2.3"
        print >>OUTPUT, "5 2.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( len(self.instance.A), 3 )

    def test_io3(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param : A B :="
        print >>OUTPUT, "1 2.2 3.3"
        print >>OUTPUT, "3 2.3 3.4"
        print >>OUTPUT, "5 2.5 3.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z, repn=self.repn)
        self.model.B=Param(self.model.Z, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( len(self.instance.A), 3 )
        self.assertEqual( len(self.instance.B), 3 )
        self.assertEqual( self.instance.B[5], 3.5 )

    def test_io4(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := A1 A2 A3;"
        print >>OUTPUT, "set Y := 1 2 3;"
        print >>OUTPUT, "param A: A1 A2 A3 :="
        print >>OUTPUT, "1 1.3 2.3 3.3"
        print >>OUTPUT, "2 1.4 2.4 3.4"
        print >>OUTPUT, "3 1.5 2.5 3.5"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.Y=Set()
        self.model.A=Param(self.model.Y,self.model.Z, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( len(self.instance.Y), 3 )
        self.assertEqual( len(self.instance.Z), 3 )
        self.assertEqual( len(self.instance.A), 9 )
        self.assertEqual( self.instance.A[1, 'A2'], 2.3 )

    def test_io5(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := A1 A2 A3;"
        print >>OUTPUT, "set Y := 1 2 3;"
        print >>OUTPUT, "param A (tr): A1 A2 A3 :="
        print >>OUTPUT, "1 1.3 2.3 3.3"
        print >>OUTPUT, "2 1.4 2.4 3.4"
        print >>OUTPUT, "3 1.5 2.5 3.5"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.Y=Set()
        self.model.A=Param(self.model.Z,self.model.Y, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( len(self.instance.Y), 3 )
        self.assertEqual( len(self.instance.Z), 3 )
        self.assertEqual( len(self.instance.A), 9 )
        self.assertEqual( self.instance.A['A2',1], 2.3 )

    def test_io6(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set Z := 1 3 5;"
        print >>OUTPUT, "param A default 0.0 :="
        print >>OUTPUT, "1 2.2"
        print >>OUTPUT, "3 ."
        print >>OUTPUT, "5 2.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.Z=Set()
        self.model.A=Param(self.model.Z, repn=self.repn)
        self.instance = self.model.create("param.dat")
        #self.instance.pprint()
        self.assertEqual( len(self.instance.components.A), 3 )
        self.assertEqual( self.instance.A[3], 0.0 )

    def test_io7(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param A := True;"
        print >>OUTPUT, "param B := False;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Param(within=Boolean, repn=self.repn)
        self.model.B=Param(within=Boolean, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( value(self.instance.A), True )
        self.assertEqual( value(self.instance.B), False )

    def test_io8(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param : A : B :="
        print >>OUTPUT, "\"A\" 3.3"
        print >>OUTPUT, "\"B\" 3.4"
        print >>OUTPUT, "\"C\" 3.5;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Set()
        self.model.B=Param(self.model.A, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( self.instance.A.data(), set(['A','B','C']) )

    def test_io9(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "param : A : B :="
        print >>OUTPUT, "\"A\" 0.1"
        print >>OUTPUT, "\"B\" 1e-1"
        print >>OUTPUT, "\"b\" 1.4e-1"
        print >>OUTPUT, "\"C\" 1E-1"
        print >>OUTPUT, "\"c\" 1.4E-1"
        print >>OUTPUT, "\"D\" 1E+1"
        print >>OUTPUT, "\"d\" 1.4E+1"
        print >>OUTPUT, "\"AA\" -0.1"
        print >>OUTPUT, "\"BB\" -1e-1"
        print >>OUTPUT, "\"bb\" -1.4e-1"
        print >>OUTPUT, "\"CC\" -1E-1"
        print >>OUTPUT, "\"cc\" -1.4E-1"
        print >>OUTPUT, "\"DD\" -1E+1"
        print >>OUTPUT, "\"dd\" -1.4E+1;"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A=Set()
        self.model.B=Param(self.model.A, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( self.instance.B['A'], 0.1)
        self.assertEqual( self.instance.B['B'], 0.1)
        self.assertEqual( self.instance.B['b'], 0.14)
        self.assertEqual( self.instance.B['C'], 0.1)
        self.assertEqual( self.instance.B['c'], 0.14)
        self.assertEqual( self.instance.B['D'], 10)
        self.assertEqual( self.instance.B['d'], 14)
        self.assertEqual( self.instance.B['AA'], -0.1)
        self.assertEqual( self.instance.B['BB'], -0.1)
        self.assertEqual( self.instance.B['bb'], -0.14)
        self.assertEqual( self.instance.B['CC'], -0.1)
        self.assertEqual( self.instance.B['cc'], -0.14)
        self.assertEqual( self.instance.B['DD'], -10)
        self.assertEqual( self.instance.B['dd'], -14)

    def test_io10(self):
        OUTPUT=open("param.dat","w")
        print >>OUTPUT, "data;"
        print >>OUTPUT, "set A1 := a b c d e f g h i j k l ;"
        print >>OUTPUT, "set A2 := 2 4 6 ;"
        print >>OUTPUT, "param B :="
        print >>OUTPUT, " [*,2,*] a b 1 c d 2 e f 3"
        print >>OUTPUT, " [*,4,*] g h 4 i j 5"
        print >>OUTPUT, " [*,6,*] k l 6"
        print >>OUTPUT, ";"
        print >>OUTPUT, "end;"
        OUTPUT.close()
        self.model.A1=Set()
        self.model.A2=Set()
        self.model.B=Param(self.model.A1,self.model.A2,self.model.A1, repn=self.repn)
        self.instance = self.model.create("param.dat")
        self.assertEqual( set(self.instance.B.keys()), set([('e', 2, 'f'), ('c', 2, 'd'), ('a', 2, 'b'), ('i', 4, 'j'), ('g', 4, 'h'), ('k', 6, 'l')]))


class MTestIO(TestIO):

    def config_repn(self):
        self.repn = 'sparse_dict'

MTestIO = unittest.skipIf(sys.version_info[:2] < (2,6), "Skipping tests because sparse_dict repn is not supported")(MTestIO)


class TestParamConditional(PyomoModel):

    def test1(self):
        self.model.p = Param(initialize=1.0)
        try:
            if self.model.p:
                pass
            self.fail("Expected ValueError because parameter was undefined")
        except ValueError:
            pass
        instance = self.model.create()
        if instance.p:
            pass
        else:
            self.fail("Wrong condition value")

    def test2(self):
        self.model.p = Param(initialize=0.0)
        try:
            if self.model.p:
                pass
            self.fail("Expected ValueError because parameter was undefined")
        except ValueError:
            pass
        instance = self.model.create()
        if instance.p:
            self.fail("Wrong condition value")
        else:
            pass


class MiscParamTests(pyutilib.th.TestCase):

    def test_constructor(self):
        a = Param(name="a")
        try:
            b = Param(foo="bar")
            self.fail("Cannot pass in 'foo' as an option to Param")
        except ValueError:
            pass
        model=AbstractModel()
        model.b = Param(initialize=[1,2,3])
        try:
            model.c = Param(model.b)
            self.fail("Can't index a parameter with a parameter")
        except TypeError:
            pass
        #
        model = AbstractModel()
        model.a = Param(initialize={None:3.3})
        instance = model.create()

    def test_get_set(self):
        model=AbstractModel()
        model.a = Param()
        model.b = Set(initialize=[1,2,3])
        model.c = Param(model.b, initialize=2, within=Reals)
        #try:
            #model.a.value = 3
            #self.fail("can't set the value of an unitialized parameter")
        #except AttributeError:
            #pass
        try:
            model.a.construct()
            self.fail("Can't construct a parameter without data")
        except ValueError:
            pass
        model.a = Param(initialize=2)
        instance=model.create()
        instance.a.value=3
        #try:
            #instance.a.default='2'
            #self.fail("can't set a bad default value")
        #except ValueError:
            #pass
        self.assertEqual(2 in instance.c, True)

        try:
            instance.a[1] = 3
            self.fail("can't index a singleton parameter")
        except KeyError:
            pass
        try:
            instance.c[4] = 3
            self.fail("can't index a parameter with a bad index")
        except KeyError:
            pass
        try:
            instance.c[3] = 'a'
            self.fail("can't set a parameter with a bad value")
        except ValueError:
            pass

    def test_iter(self):
        model=AbstractModel()
        model.b = Set(initialize=[1,2,3])
        model.c = Param(model.b,initialize=2)
        instance = model.create()
        for i in instance.c:
            self.assertEqual(i in instance.c, True)

    def test_valid(self):
        def d_valid(model, a):
            return True
        def e_valid(model, a, i, j):
            return True
        model=AbstractModel()
        model.b = Set(initialize=[1,3,5])
        model.c = Param(initialize=2, within=None)
        model.d = Param(initialize=(2,3), validate=d_valid)
        model.e = Param(model.b,model.b,initialize={(1,1):(2,3)}, validate=e_valid)
        instance = model.create()
        instance.components.e.check_values()
        #try:
            #instance.c.value = 'b'
            #self.fail("can't have a non-numerical parameter")
        #except ValueError:
            #pass
            
    
def createNonIndexedParamMethod(func, init_xy, new_xy, tol=1e-10):
    
    def testMethod(self):
        model = ConcreteModel()
        model.Q1 = Param(initialize=init_xy[0])
        model.x = Var()
        model.CON = Constraint(expr=func(model.Q1)<=model.x)
        inst = model.create()
        
        self.assertAlmostEqual(init_xy[1], inst.CON[None].lower.__float__(), 1e-10)
        
        inst.Q1 = new_xy[0]
        inst.preprocess()
        self.assertAlmostEqual(new_xy[1], inst.CON[None].lower.__float__(), tol)

    return testMethod

def createIndexedParamMethod(func, init_xy, new_xy, tol=1e-10):
    
    def testMethod(self):
        model = ConcreteModel()
        model.P = Param([1,2],initialize=init_xy[0])
        model.Q = Param([1,2],default=init_xy[0])
        model.R = Param([1,2])
        model.R[1] = init_xy[0]
        model.R[2] = init_xy[0]
        model.x = Var()
        model.CON1 = Constraint(expr=func(model.P[1])<=model.x)
        model.CON2 = Constraint(expr=func(model.Q[1])<=model.x)
        model.CON3 = Constraint(expr=func(model.R[1])<=model.x)
        inst = model.create()
        
        self.assertAlmostEqual(init_xy[1], inst.CON1[None].lower.__float__(),tol)
        self.assertAlmostEqual(init_xy[1], inst.CON2[None].lower.__float__(),tol)
        self.assertAlmostEqual(init_xy[1], inst.CON3[None].lower.__float__(),tol)        
        
        inst.P[1] = new_xy[0]
        inst.Q[1] = new_xy[0]
        inst.R[1] = new_xy[0]
        inst.preprocess()
        self.assertAlmostEqual(new_xy[1], inst.CON1[None].lower.__float__(),tol)
        self.assertAlmostEqual(new_xy[1], inst.CON2[None].lower.__float__(),tol)
        self.assertAlmostEqual(new_xy[1], inst.CON3[None].lower.__float__(),tol)

    return testMethod

def assignTestsNonIndexedParamTests(cls, problem_list):
    for val in problem_list:
        attrName = 'test_mutable_'+val[0]+'_expr'
        setattr(cls,attrName,createNonIndexedParamMethod(eval(val[0]),val[1],val[2]))
        
def assignTestsIndexedParamTests(cls, problem_list):
    for val in problem_list:
        attrName = 'test_mutable_'+val[0]+'_expr'
        setattr(cls,attrName,createIndexedParamMethod(eval(val[0]),val[1],val[2]))

instrinsic_test_list = [('sin', (0.0,0.0), (math.pi/2.0,1.0)), \
                        ('cos', (0.0,1.0), (math.pi/2.0,0.0)), \
                        ('log', (1.0,0.0), (math.e,1.0)), \
                        ('log10', (1.0,0.0), (10.0,1.0)),\
                        ('tan', (0.0,0.0), (math.pi/4.0,1.0)),\
                        ('cosh', (0.0,1.0), (math.acosh(1.5),1.5)),\
                        ('sinh', (0.0,0.0), (math.asinh(0.5),0.5)),\
                        ('tanh', (0.0,0.0), (math.atanh(0.8),0.8)),\
                        ('asin', (0.0,0.0), (math.sin(1.0),1.0)),\
                        ('acos', (1.0,0.0), (math.cos(1.0),1.0)),\
                        ('atan', (0.0,0.0), (math.tan(1.0),1.0)),\
                        ('exp', (0.0,1.0), (math.log(2),2.0)),\
                        ('sqrt', (1.0,1.0), (4.0,2.0)),\
                        ('asinh', (0.0,0.0), (math.sinh(2.0),2.0)),\
                        ('acosh', (1.0,0.0), (math.cosh(2.0),2.0)),\
                        ('atanh', (0.0,0.0), (math.tanh(2.0),2.0)),\
                        ('ceil', (0.5,1.0), (1.5,2.0)),\
                        ('floor', (0.5,0.0), (1.5, 1.0))\
                       ]

            
#class MiscNonIndexedParamBehaviorTests(pyutilib.th.TestCase):
class MiscNonIndexedParamBehaviorTests(object):

    # Test that non-indexed params are mutable
    def test_mutable_self(self):
        model = ConcreteModel()
        model.Q = Param(initialize=0.0)
        model.x = Var()
        model.CON = Constraint(expr=model.Q<=model.x)
        inst = model.create()
        
        self.assertEqual(0.0, inst.CON[None].lower.__float__())
        
        inst.Q = 1.0
        inst.preprocess()
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
    # Test that display actually displays the correct param value
    def test_mutable_display(self):
        model = ConcreteModel()
        model.Q = Param(initialize=0.0)
        
        self.assertEqual(model.Q, 0.0)
        model.Q = 1.0
        self.assertEqual(model.Q,1.0)
        tmp_stream = pyutilib.services.TempfileManager.create_tempfile(suffix = '.param_display.test')         
        f = open(tmp_stream,'w')
        display(model.Q,f)
        f.close()
        f = open(tmp_stream,'r')
        tmp = f.readlines()
        f.close()
        val = float(tmp[1].strip())
        self.assertEquals(model.Q, val)
        
    # Test mutability of non-indexed
    # params involved in sum expression
    def test_mutable_sum_expr(self):
        model = ConcreteModel()
        model.Q1 = Param(initialize=0.0)
        model.Q2 = Param(initialize=0.0)
        model.x = Var()
        model.CON = Constraint(expr=model.Q1+model.Q2<=model.x)
        inst = model.create()
        
        self.assertEqual(0.0, inst.CON[None].lower.__float__())
        
        inst.Q1 = 3.0
        inst.Q2 = 2.0
        inst.preprocess()
        self.assertEqual(5.0, inst.CON[None].lower.__float__())
        
    # Test mutability of non-indexed
    # params involved in prod expression
    def test_mutable_prod_expr(self):
        model = ConcreteModel()
        model.Q1 = Param(initialize=0.0)
        model.Q2 = Param(initialize=0.0)
        model.x = Var()
        model.CON = Constraint(expr=model.Q1*model.Q2<=model.x)
        inst = model.create()
        
        self.assertEqual(0.0, inst.CON[None].lower.__float__())
        
        inst.Q1 = 3.0
        inst.Q2 = 2.0
        inst.preprocess()
        self.assertEqual(6.0, inst.CON[None].lower.__float__())
    
    # Test mutability of non-indexed
    # params involved in pow expression
    def test_mutable_pow_expr(self):
        model = ConcreteModel()
        model.Q1 = Param(initialize=1.0)
        model.Q2 = Param(initialize=1.0)
        model.x = Var()
        model.CON = Constraint(expr=model.Q1**model.Q2<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
        inst.Q1 = 3.0
        inst.Q2 = 2.0
        inst.preprocess()
        self.assertEqual(9.0, inst.CON[None].lower.__float__())
        
    # Test mutability of non-indexed
    # params involved in abs expression
    def test_mutable_abs_expr(self):
        model = ConcreteModel()
        model.Q1 = Param(initialize=-1.0)
        model.x = Var()
        model.CON = Constraint(expr=abs(model.Q1)<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
        inst.Q1 = -3.0
        inst.preprocess()
        self.assertEqual(3.0, inst.CON[None].lower.__float__())
        

# Add test methods for all intrinsic functions
assignTestsNonIndexedParamTests(MiscNonIndexedParamBehaviorTests,instrinsic_test_list)

        
#class MiscIndexedParamBehaviorTests(pyutilib.th.TestCase):
class MiscIndexedParamBehaviorTests(object):

    # Test that indexed params are mutable
    def test_mutable_self1(self):
        model = ConcreteModel()
        model.P = Param([1])
        model.P[1] = 1.0
        model.x = Var()
        model.CON = Constraint(expr=model.P[1]<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
        inst.P[1] = 2.0
        inst.preprocess()
        self.assertEqual(2.0, inst.CON[None].lower.__float__())
        
    # Test that indexed params are mutable
    # when initialized with 'initialize'
    def test_mutable_self2(self):
        model = ConcreteModel()
        model.P = Param([1],initialize=1.0)
        model.x = Var()
        model.CON = Constraint(expr=model.P[1]<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
        inst.P[1] = 2.0
        inst.preprocess()
        self.assertEqual(2.0, inst.CON[None].lower.__float__())
        
    # Test that indexed params are mutable
    # when initialized with 'default'
    def test_mutable_self3(self):
        model = ConcreteModel()
        model.P = Param([1],default=1.0)
        model.x = Var()
        model.CON = Constraint(expr=model.P[1]<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON[None].lower.__float__())
        
        inst.P[1] = 2.0
        inst.preprocess()
        self.assertEqual(2.0, inst.CON[None].lower.__float__())
        
    # Test the behavior when using the 'default' keyword
    # in param initialization
    def test_mutable_self4(self):
        model = ConcreteModel()
        model.P = Param([1,2],default=1.0)
        
        self.assertEqual(model.P[1],1.0)
        self.assertEqual(model.P[2],1.0)
        model.P[1].value = 0.0
        self.assertEqual(model.P[1],0.0)
        self.assertEqual(model.P[2],1.0)
        
        model.Q = Param([1,2],default=1.0)
        self.assertEqual(model.Q[1],1.0)
        self.assertEqual(model.Q[2],1.0)
        model.Q[1] = 0.0
        self.assertEqual(model.Q[1],0.0)
        self.assertEqual(model.Q[2],1.0)
        
    # Test mutability of indexed
    # params involved in sum expression
    # and that params behave the same when initialized in 
    # different ways
    def test_mutable_sum_expr(self):
        model = ConcreteModel()
        model.P = Param([1,2],default=0.0)
        model.Q = Param([1,2],initialize=0.0)
        model.R = Param([1,2])
        model.R[1] = 0.0
        model.R[2] = 0.0
        model.x = Var()
        model.CON1 = Constraint(expr=model.P[1]+model.P[2]<=model.x)
        model.CON2 = Constraint(expr=model.Q[1]+model.Q[2]<=model.x)
        model.CON3 = Constraint(expr=model.R[1]+model.R[2]<=model.x)
        inst = model.create()
        
        self.assertEqual(0.0, inst.CON1[None].lower.__float__())
        self.assertEqual(0.0, inst.CON2[None].lower.__float__())
        self.assertEqual(0.0, inst.CON3[None].lower.__float__())
        
        inst.P[1] = 3.0
        inst.P[2] = 2.0
        inst.Q[1] = 3.0
        inst.Q[2] = 2.0
        inst.R[1] = 3.0
        inst.R[2] = 2.0
        inst.preprocess()
        self.assertEqual(5.0, inst.CON1[None].lower.__float__())
        self.assertEqual(5.0, inst.CON2[None].lower.__float__())
        self.assertEqual(5.0, inst.CON3[None].lower.__float__())
        
    # Test mutability of indexed
    # params involved in prod expression
    # and that params behave the same when initialized in 
    # different ways
    def test_mutable_prod_expr(self):
        model = ConcreteModel()
        model.P = Param([1,2],initialize=0.0)
        model.Q = Param([1,2],default=0.0)
        model.R = Param([1,2])
        model.R[1] = 0.0
        model.R[2] = 0.0
        model.x = Var()
        model.CON1 = Constraint(expr=model.P[1]*model.P[2]<=model.x)
        model.CON2 = Constraint(expr=model.Q[1]*model.Q[2]<=model.x)
        model.CON3 = Constraint(expr=model.R[1]*model.R[2]<=model.x)
        inst = model.create()
        
        self.assertEqual(0.0, inst.CON1[None].lower.__float__())
        self.assertEqual(0.0, inst.CON2[None].lower.__float__())
        self.assertEqual(0.0, inst.CON3[None].lower.__float__())
        
        inst.P[1] = 3.0
        inst.P[2] = 2.0
        inst.Q[1] = 3.0
        inst.Q[2] = 2.0
        inst.R[1] = 3.0
        inst.R[2] = 2.0
        inst.preprocess()
        self.assertEqual(6.0, inst.CON1[None].lower.__float__())
        self.assertEqual(6.0, inst.CON2[None].lower.__float__())
        self.assertEqual(6.0, inst.CON3[None].lower.__float__())
    
    # Test mutability of indexed
    # params involved in pow expression
    # and that params behave the same when initialized in 
    # different ways
    def test_mutable_pow_expr(self):
        model = ConcreteModel()
        model.P = Param([1,2],initialize=0.0)
        model.Q = Param([1,2],default=0.0)
        model.R = Param([1,2])
        model.R[1] = 0.0
        model.R[2] = 0.0
        model.x = Var()
        model.CON1 = Constraint(expr=model.P[1]**model.P[2]<=model.x)
        model.CON2 = Constraint(expr=model.Q[1]**model.Q[2]<=model.x)
        model.CON3 = Constraint(expr=model.R[1]**model.R[2]<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON1[None].lower.__float__())
        self.assertEqual(1.0, inst.CON2[None].lower.__float__())
        self.assertEqual(1.0, inst.CON3[None].lower.__float__())        
        
        inst.P[1] = 3.0
        inst.P[2] = 2.0
        inst.Q[1] = 3.0
        inst.Q[2] = 2.0
        inst.R[1] = 3.0
        inst.R[2] = 2.0
        inst.preprocess()
        self.assertEqual(9.0, inst.CON1[None].lower.__float__())
        self.assertEqual(9.0, inst.CON2[None].lower.__float__())
        self.assertEqual(9.0, inst.CON3[None].lower.__float__())
        
    # Test mutability of indexed
    # params involved in abs expression
    # and that params behave the same when initialized in 
    # different ways
    def test_mutable_abs_expr(self):
        model = ConcreteModel()
        model.P = Param([1,2],initialize=-1.0)
        model.Q = Param([1,2],default=-1.0)
        model.R = Param([1,2])
        model.R[1] = -1.0
        model.R[2] = -1.0
        model.x = Var()
        model.CON1 = Constraint(expr=abs(model.P[1])<=model.x)
        model.CON2 = Constraint(expr=abs(model.Q[1])<=model.x)
        model.CON3 = Constraint(expr=abs(model.R[1])<=model.x)
        inst = model.create()
        
        self.assertEqual(1.0, inst.CON1[None].lower.__float__())
        self.assertEqual(1.0, inst.CON2[None].lower.__float__())
        self.assertEqual(1.0, inst.CON3[None].lower.__float__())        
        
        inst.P[1] = -3.0
        inst.Q[1] = -3.0
        inst.R[1] = -3.0
        inst.preprocess()
        self.assertEqual(3.0, inst.CON1[None].lower.__float__())
        self.assertEqual(3.0, inst.CON2[None].lower.__float__())
        self.assertEqual(3.0, inst.CON3[None].lower.__float__())

# Add test methods for all intrinsic functions
assignTestsIndexedParamTests(MiscIndexedParamBehaviorTests,instrinsic_test_list)

        

if __name__ == "__main__":
    unittest.main()
