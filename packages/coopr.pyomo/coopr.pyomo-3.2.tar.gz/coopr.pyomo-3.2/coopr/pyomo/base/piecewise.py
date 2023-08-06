
__all__ = ['Piecewise']

from component import Component
from constraint import Constraint
from sos import SOSConstraint
from var import Var, _VarArray, _VarElement
from sets import Set, _BaseSet
from set_types import *
from pyutilib.component.core import alias
from pyutilib.misc import flatten_tuple
import math
import copy
from itertools import product

"""
This file contains a library of functions needed to construct linear/piecewise-linear
constraints for a Pyomo model. All piecewise types except for SOS2, BIGM_SOS1,
BIGM_BIN were taken from the paper: Mixed-Integer Models for Non-separable Piecewise Linear
Optimization: Unifying framework and Extensions (Vielma, Nemhauser 2008).

USAGE NOTES:
*) The BIGM methods currently determine tightest constant M values. This method is
   implemented in such a way that binary/SOS variables are not created when this M is
   zero. In a way, this determines convexity/concavity and can simplify constraints up to the point
   where no binary/SOS variables may exist. The other piecewise representations have the ability to do
   this simplification only with the check for convexity/concavity. *** not quite ready, I found a 
   test case that fails *** Note, however,for strictly affine functions the BIGM
   method can still eliminate a few variables when determining the tightest M value.
*) I have NOT tested what happens when Pyomo params are in f_rule/d_f_rule. I think the only safe thing to do
   for now would be to place value() around the params if they are present. The function rules need to return a 
   numeric value, I'm not sure what happens when they don't.


TODOS (in rough order of priority):
_DONE_ *) insure points are sorted ???? THIS IS NEEDED FOR SOME PW_REPS
_DONE_ *) user not providing floats can be an major issue for BIGM's and MC
_DONE_ *) raise error when (2^n)+1 break points not givenfor LOG, DLOG piecewise reps
_DONE_ *) check for convexity/concavity, do we really need the convex/concave kwds? ---- replaced convex/concave kwds with force_pw
       *) check for continuity?? This is required, but should we check?
       *) Consider another piecewise rep "SOS2_MANUAL" where we manually implement extra constraints to
          define an SOS2 set, this would be compatible with GLPK, http://winglpk.sourceforge.net/media/glpk-sos2_02.pdf
_DONE_ *) arbitrary number index sets of arbitrary dimension
_DONE_  *) params in f_rules? (in particular when the they don't have value() around them)
_DONE_ *) non-indexed variables
       *) Clean up BIGM code if convexity check is implemented
       *) handle when break points are given as Sets??? Right now must be dictionary( or list for non-indexed)
       *) write tests
_DONE_ *) check when adding elements to dicts, those elements don't already exist in model, hasattr()
_DONE_ *) finish function documentation string
_DONE_ *) add more description of capabilities
_DONE_ *) clean up naming scheme for added model attributes
_DONE_ *) remove addition of optimal BIGM values as model attribute
_DONE_ *) tests that inputs make sense
_DONE_ *) collect list of variables added to the model like constraints
_DONE_ *) collect list of sets added to the model just like constraints
       *) affine functions - BIGM_SOS1, BIGM_SOS2 *****Not quite done
*) speed up? Search for BOTTLENECK to see a few spots worth considering
*) double check that LOG and DLOG reps really do require 2^n points
*) multivar linearizations
*) multivar piecewise reps
"""

def isPowerOfTwo(x):
    if (x <= 0):
	return false
    else:
	return ( (x & (x - 1)) == 0 )

def isIncreasing(l):
    """
    checks that list of points is
    strictly increasing
    """
    for i, el in enumerate(l[1:]):
        if el <= l[i]:
            return False
    return True

def isDecreasing(l):
    """
    checks that list of points is
    strictly decreasing
    """
    for i, el in enumerate(l[1:]):
        if el >= l[i]:
            return False
    return True

def isNonDecreasing(l):
    """
    checks that list of points is
    not decreasing
    """
    for i, el in enumerate(l[1:]):
        if el < l[i]:
            return False
    return True

def isNonIncreasing(l):
    """
    checks that list of points is
    not increasing
    """
    for i, el in enumerate(l[1:]):
        if el > l[i]:
            return False
    return True

def isIndexer(x):
    """
    Determines if object is eligable to 
    index the method
    """
    return isinstance(x, set) or \
           isinstance(x,_BaseSet) or \
           isinstance(x,list) or \
           isinstance(x,tuple) 

class TupleIterator:
    def __init__(self, underlyingIter):
        self.underlying = underlyingIter

    def __iter__(self):
        return self

    def next(self):
        try:
            return (self.underlying.next(),)
        except StopIteration:
            raise

class TupleSet(set):
    """
    Behaves as a set but has 
    tuplize() method which 
    returns elements as a singleton
    tuple
    """
    
    def __init__(self, dimen, *args):
	self.dimen = dimen
	set.__init__(self,*args)

    def tuplize(self):
	if self.dimen > 1:
	    return self.__iter__()
	elif self.dimen == 1:
	    return TupleIterator(self.__iter__())
	else:
	    return [()]

def _GrayCode(nbits):

    bitset = [0 for i in xrange(nbits)]
    graycode = [''.join(map(str,bitset))]

    for	i in xrange(2,(1<<nbits)+1):
	if i%2:
            for	j in xrange(-1,-nbits,-1):
                if bitset[j]:
                    bitset[j-1]=bitset[j-1]^1
                    break
        else:
            bitset[-1]=bitset[-1]^1

        graycode.append(''.join(map(str,bitset)))

    return graycode


def _DLog_Branching_Scheme(L):
    """
    Branching scheme for DLOG
    """

    MAX = 2**L
    mylists1 = {}
    for i in xrange(1,L+1):
	mylists1[i] = []
	start = 1
	step = MAX/(2**i)
	while(start < MAX):
	    mylists1[i].extend([j for j in xrange(start,start+step)])
	    start += 2*step
        
    biglist = [i for i in xrange(1,MAX+1)]
    mylists2 = {}
    for i in sorted(mylists1.keys()):
	mylists2[i] = []
	for j in biglist:
	    if j not in mylists1[i]:
		mylists2[i].append(j)
	mylists2[i] = sorted(mylists2[i])
    
    return mylists1, mylists2

def _Log_Branching_Scheme(n):
    """
    Branching scheme for LOG, requires G be a gray code
    """

    BIGL = 2**n
    S = [j for j in xrange(1,n+1)]    
    code = _GrayCode(n)
    G = dict((i, [int(j) for j in code[i-1]]) for i in xrange(1,len(code)+1))

    L = {}
    R = {}
    for s in S:
	L[s] = []
	R[s] = []
	for k in range(BIGL+1):
	    if ((k == 0) or (G[k][s-1] == 1)) and ((k == BIGL) or (G[k+1][s-1] == 1)):
		L[s].append(k+1)
	    if ((k == 0) or (G[k][s-1] == 0)) and ((k == BIGL) or (G[k+1][s-1] == 0)):
		R[s].append(k+1)
		
    return S,L,R

def characterize_function(f,tpl):
    
    # determines convexity or concavity
    # return 1 (convex), -1 (concave), 0 (neither)
    
    points = tpl[-1]
    new_tpl = flatten_tuple(tpl[:-1])
    SLOPES = [(f( *(new_tpl+(points[i],)) )-f( *(new_tpl+(points[i-1],)) ))/(points[i]-points[i-1]) for i in xrange(1,len(points))]
    
    if isNonDecreasing(SLOPES):
	# convex
	return 1
    elif isNonIncreasing(SLOPES):
	# concave
	return -1
    
    return 0


class Piecewise(Component):
    """
    Adds linear/piecewise-linear constraints to a Pyomo model for functions of the form, y = f(x).
    
    Usage:
            model.const = Piecewise(model.index,model.yvar,model.xvar,**Keywords) - for indexed variables
            model.const = Piecewise(model.yvar,model.xvar,**Keywords) - for non-indexed variables
	    
	    where,
	            model.index - indexing set
		    model.yvar - Pyomo Var which represents the range values of f(x)
		    model.xvar - Pyomo Var which represents the domain values of f(x)

    Keywords:
    
-pw_pts={},[],()  
	  A dictionary of lists (keys are index set) or a single list (for non-indexed variables) defining
	  the set of domain vertices for a continuous piecewise linear function. Default is None
	  *** REQUIRES 'f_rule', and 'pw_constr_type' kwds, 'pw_repn' is optional ***

-tan_pts={},[],()
	  A dictionary of lists (keys are index set) or a single list (for non-indexed variables) defining
	  the set of domain vertices for the linear under/over estimators.
	  *** REQUIRES 'f_rule', 'd_f_rule', and 'tan_constr_type' kwds ***

-pw_repn=''
	  Indicates the type of piecewise representation to use. Each representation uses its own sets of different 
	  constraints and variables. This can have a major impact on performance of the MIP solve.
	  Choices:
		 
		 ~ + 'SOS2' - standard representation using SOS2 variables. (Default)
		 ~ + 'BIGM_BIN' - uses BigM constraints with binary variables. Theoretically tightest M
				  values are automatically determined.
		 ~ + 'BIGM_SOS1' - uses BigM constraints with sos1 variables. Theoretically tightest M
				  values are automatically determined.
		 ~*+ 'DCC' - Disaggregated convex combination model
		 ~*+ 'DLOG' - Logarithmic Disaggregated convex combination model
		 ~*+ 'CC' - Convex combination model
		 ~*+ 'LOG' - Logarithmic branching convex combination
		 ~*+ 'MC' - Multiple choice model
		 ~*+ 'INC' - Incremental (delta) method

		   * Source: "Mixed-Integer Models for Non-separable Piecewise Linear Optimization: 
			      Unifying framework and Extensions" (Vielma, Nemhauser 2008)
		   ~ Refer to the optional 'force_pw' kwd.

-pw_constr_type=''
	  Indicates whether piecewise function represents an upper bound, lower bound, or equality constraint.
	  *** REQUIRED WHEN 'pw_pts' ARE SPECIFIED ***
	  Choices:
		 
		   + 'UB' - y variable is bounded above by piecewise function
		   + 'LB' - y variable is bounded below by piecewise function
		   + 'EQ' - y variable is equal to the piecewise function

-tan_constr_type
	  Indicates whether the function linearization represents an upper bound or lower bound.
	  *** REQUIRED WHEN 'tan_pts' ARE SPECIFIED ***
	  Choices:
		 
		   + 'UB' - y variable is bounded above by the function linearizations
		   + 'LB' - y variable is bounded below by the function linearizations

-f_rule=f(model,i,j,...,x)
	  A callable object defining the function that linearizations/piecewise constraints will be applied to.
	  First argument must be a Pyomo model. The last argument is the domain value at which the function evaluates.
	  Intermediate arguments are the corresponding indices of the Piecewise variables (model.yvar, model.xvar).
	  If these variables are non-indexed, no intermediate arguments are needed.
	  *** ALWAYS REQUIRED ***
	  Examples:
		   + def f(model,j,x):
			  if (j == 2):
			     return x**2 + 1.0
			  else:
			     return x**2 + 5.0
		   + f = lambda model,x: return exp(x) + value(model.p) (p is a Pyomo Param)
		   + def f(model,x):
			 return mydictionary[x]

-d_f_rule=f(model,i,j,...,x)
	  A callable object defining the derivative of the function that linearizations will be applied to.
	  First argument must be a Pyomo model. The last argument is the domain value at which the function evaluates.
	  Intermediate arguments are the corresponding indices of the Piecewise variables (model.yvar, model.xvar).
	  If these variables are non-indexed, no intermediate arguments are needed.
	  *** REQUIRED WHEN 'tan_pts' ARE SPECIFIED ***
	  Examples:
		   + def df(model,j,x):
			  return 2.0*x
		   + df = lambda model,x: return exp(x)
		   + def df(model,x):
			 return mydictionary[x]                      

-force_pw=True/False
	  Using the given function rule and pw_pts, a check for convexity/concavity is implemented. If (1) the function is convex and
	  the piecewise constraints are lower bounds or if (2) the function is concave and the piecewise constraints are upper bounds
	  the piecewise constraints will be substituted for strictly linear constraints. Setting 'force_pw=True' will force the use
	  of the original piecewise constraints when one of these two cases applies.
    """
    
    alias("Piecewise", "A Generator of linear and piecewise-linear constraints.")
    
    def __init__(self, *args, **kwds):

	self.piecewise_choices = ['BIGM_SOS1','BIGM_BIN','SOS2','CC','DCC','DLOG','LOG','MC','INC']
        self.PW_PTS = kwds.pop('pw_pts',None)
        self.GRAD_PTS = kwds.pop('tan_pts',None)
        self.PW_REP = kwds.pop('pw_repn', 'SOS2')
        self.PW_TYPE = kwds.pop('pw_constr_type',None)
	self.GRAD_TYPE = kwds.pop('tan_constr_type',None)
	self.candidate_f = kwds.pop('f_rule',None)
	self.candidate_d_f = kwds.pop('d_f_rule',None)
	self._force_pw = kwds.pop('force_pw',False)
	if len(kwds) != 0:
	    raise AssertionError, "WARNING: Possible invalid keywords given to LinearConstraint: "+str(kwds.keys())
	
	self._element_mode = False
	self._index_args = []
	self._index_dimen = None
	
        if len(args) > 2:
	    if all([isIndexer(args[i]) for i in range(len(args)-2)]) and \
	    isinstance(args[-2],_VarArray) and \
	    isinstance(args[-1],_VarArray):
		self._index_args = [args[i] for i in range(len(args)-2)]
		self._index_dimen = 0
		for arg in self._index_args:
		    if isinstance(arg,_BaseSet):
			self._index_dimen += arg.dimen
		    elif isinstance(arg, set):
			element = iter(arg).next()
			if isinstance(element,tuple):
			    self._index_dimen += len(element)
			else:
			    self._index_dimen += 1
		    elif isinstance(arg,list) or isinstance(arg,tuple):
			element = arg[0]
			if isinstance(element,tuple):
			    self._index_dimen += len(element)
			else:
			    self._index_dimen += 1
		self.YVAR = args[-2]
		self.XVAR = args[-1]
		args = ()
        elif isinstance(args[0],_VarElement) and isinstance(args[1],_VarElement):
            self.YVAR = args[0]
            self.XVAR = args[1]
	    self._index_dimen = 0
	    args = ()
	    self._element_mode = True
        else:
            raise TypeError, "Piecewise: Invalid function arguments. Syntax: \n\
            (1) F(Set,Var,Var,**kwds) \n\
	    (2) F(set,Var,Var,**kwds) \n\
	    (3) F(list,Var,Var,**kwds) \n\
	    (4) F(tuple,Var,Var,**kwds) \n\
            (5) F(Var,Var,**kwds)"
	
	self._constraints_dict = {}
	self._vars_dict = {}
	self._sets_dict = {}
	
	# Test that inputs make sense
	if self._force_pw not in [True,False]:
	    raise AssertionError, "Piecewise: invalid kwd value for 'force_pw', must be True or False"
	if (self.GRAD_PTS is not None) and (self.GRAD_TYPE is None):
	    raise AssertionError, "Piecewise kwd 'tan_constr_type' required when 'tan_pts' is specified"
	if (self.PW_PTS is not None):
	    if (self.PW_TYPE is None):
		raise AssertionError, "Piecewise kwd 'pw_constr_type' required when 'pw_pts' is specified"
	    if (self.PW_REP not in self.piecewise_choices):
		raise AssertionError, repr(self.PW_REP)+" is not a valid type for Piecewise kwd 'pw_repn' \n\
		                      Choices are: "+str(self.piecewise_choices)
						  
	if (self._element_mode is True) and (not (self.PW_PTS is None)) and (not isinstance(self.PW_PTS, list)) and (not isinstance(self.PW_PTS,tuple)):
	    raise AssertionError, "Piecewise kwd 'pw_pts' must be of type list or tuple when no indexing set is given"
	if (self._element_mode is False) and (not (self.PW_PTS is None)) and (not isinstance(self.PW_PTS, dict)):
	    raise AssertionError, "Piecewise kwd 'pw_pts' must be of type dict when indexing set is given"
	if (self._element_mode is True) and (not (self.GRAD_PTS is None)) and (not isinstance(self.GRAD_PTS, list)) and (not isinstance(self.GRAD_PTS,tuple)):
	    raise AssertionError, "Piecewise kwd 'tan_pts' must be of type list or tuple when no indexing set is given"
	if (self._element_mode is False) and (not (self.GRAD_PTS is None)) and (not isinstance(self.GRAD_PTS, dict)):
	    raise AssertionError, "Piecewise kwd 'tan_pts' must be of type dict when indexing set is given"

	self.name = "unknown"
	# Construct parent
        Component.__init__(self,ctype=Piecewise, **kwds)
	self._index_set = None
	self._index = None
	
	
    def _grad_pts(self,*targs):
	args = flatten_tuple(targs)
	if len(args) > 1:
	    return self.GRAD_PTS[args]
	elif len(args) == 1:
	    return self.GRAD_PTS[args[0]]
	else:
	    return self.GRAD_PTS
	
    def _pw_pts(self,*targs):
	args = flatten_tuple(targs)
	if len(args) > 1:
	    return self.PW_PTS[args]
	elif len(args) == 1:
	    return self.PW_PTS[args[0]]
	else:
	    return self.PW_PTS
	
    def _getvar(self,model,name,*targs):
	args = flatten_tuple(targs)
	if len(args) > 1:
	    return getattr(model,name)[args]
	elif len(args) == 1:
	    return getattr(model,name)[args[0]]
	return getattr(model,name)
	
    def _getset(self,model,name,*targs):
	args = flatten_tuple(targs)
	if len(args) > 1:
	    return getattr(model,name)[args]
	elif len(args) == 1:
	    return getattr(model,name)[args[0]]
	return getattr(model,name)
	
    def pprint(self, *args, **kwds):
        pass
    
    def reset(self):            #pragma:nocover
        pass                    #pragma:nocover
    
    def deactivate(self):
	"""
	Deactivates all model constraints created by this class.
	"""
	[con.deactivate() for con in self._constraints_dict.itervalues()]
	self.active = False
    
    def activate(self):
	"""
	Activates all model constraints created by this class.
	"""
	[con.activate() for con in self._constraints_dict.itervalues()]
	self.active = True
    
    def construct(self, *args, **kwds):
	
        #A hack to call add after data has been loaded.
	if self._model()._defer_construction:
	    self._model().concrete_mode()
	    self.add()
	    self._model().symbolic_mode()
	else:
	    self.add()
	self._constructed=True
	

    def add(self, *args):

        #Mimics Constraint.add, but is only used to alert preprocessors
        #to its existence. Ignores all arguments passed to it.
	if len(self._index_args) > 1:
	    self.index = set([flatten_tuple(idx) for idx in product(*self._index_args)])
	elif len(self._index_args) == 1:
	    self.index = self._index_args[0]
	else:
	    # Non-indexed case
	    self.index = []
	
	
	if self.candidate_f != None:
	    self._define_F(self.candidate_f)
	if self.candidate_d_f != None:
	    self._define_d_F(self.candidate_d_f)
	
	#construct the linear over/under estimators
	if self.GRAD_PTS != None:
	    self._construct_linear_estimators(TupleSet(self._index_dimen,self.index))
	
	#If a piecewise list is given then construct the piecewise constraints.
	#These functions look at the size of each list of x points and create
	#variables/constraints as needed. For instance if only two points are supplied
	#as a list for piecewise, no binary variable is actually needed, therefore
	#the constraints are created using the _construct_simple_single_bound function.
	if self.PW_PTS != None:
	    
	    #check that lists are sorted and for special cases
	    #(pw_repn='LOG' or 'DLOG') that lists have 2^n + 1 points.
	    if self._element_mode:
		if (self.PW_REP in ['DLOG','LOG']) and (not isPowerOfTwo(len(self._pw_pts())-1)):
		    raise AssertionError, self.name+": 'pw_pts' list must have 2^n + 1 points in list for " \
		                                       +self.PW_REP+" type piecewise representation"
		if not isIncreasing(self._pw_pts()):
		    raise AssertionError, self.name+": 'pw_pts' must be sorted in increasing order"
	    else:
		if (self.PW_REP in ['DLOG','LOG']) and (not all((isPowerOfTwo(len(self._pw_pts(t))-1) for t in self.index))):
		    raise AssertionError, self.name+": 'pw_pts' lists must have 2^n + 1 points in each list for " \
		                                       +self.PW_REP+" type piecewise representation"
		if not all((isIncreasing(self._pw_pts(t)) for t in self.index)):
		    raise AssertionError, self.name+": 'pw_pts' must be sorted in increasing order"
		
	    #determine convexity or concavity in terms of piecewise points
	    simplified_index = []
	    pw_index = []
	    force_simple = False
	    force_pw = False
	    if self._element_mode:
		tpl = (self._model(),)+(self._pw_pts(),)
		result = characterize_function(self._F, tpl)
		if (result == -1):
		    self.function_character = 'concave'
		    if (self.PW_TYPE == 'UB'):
			force_simple = True
		    else:
			force_pw = True
		elif (result == 1):
		    self.function_character = 'convex'
		    if (self.PW_TYPE == 'LB'):
			force_simple = True
		    else:
			force_pw = True
		else:
		    self.function_character = 'affine'
		    force_pw = True
	    else:
		self.function_character = {}
		for t in self.index:
		    tpl = (self._model(),)+(t,)+(self._pw_pts(t),)
		    result = characterize_function(self._F, tpl)
		    if (result == -1):
			self.function_character[t] = 'concave'
			if (self.PW_TYPE == 'UB'):
			    simplified_index.append(t)
			    force_simple = True
			else:
			    force_pw = True
			    pw_index.append(t)
		    elif (result == 1):
			self.function_character[t] = 'convex'
			if (self.PW_TYPE == 'LB'):
			    simplified_index.append(t)
			    force_simple = True
			else:
			    force_pw = True
			    pw_index.append(t)
		    else:
			self.function_character[t] = 'affine'
			pw_index.append(t)
			force_pw = True
			
	    # make sure user doesn't want to force the use of pw constraints
	    if self._force_pw is True:
		force_simple = False
		force_pw = True
		pw_index = self.index
		simplified_index = []
	    
	    if force_simple is True:
		self._construct_simple_bounds(TupleSet(self._index_dimen,simplified_index))
	    if force_pw is True:
		INDEX_SET_PW = TupleSet(self._index_dimen,[])
		INDEX_SET_SIMPLE = TupleSet(self._index_dimen,[])
		force_simple = False
		force_pw = False
		if self._element_mode:
		    if len(self._pw_pts()) == 2:
			force_simple = True
		    else:
			force_pw = True
		else:
		    for t in pw_index:
			if len(self._pw_pts(t)) == 2:
			    INDEX_SET_SIMPLE.add(t)
			    force_simple = True
			else:
			    INDEX_SET_PW.add(t)
			    force_pw = True
			
		####### SIMPLE
		if force_simple is True:
		    self._construct_simple_single_bound(INDEX_SET_SIMPLE)
		    
		##### SOS2
		if force_pw is True:
		    if self.PW_REP == 'SOS2':
			self._construct_SOS2(INDEX_SET_PW)
		    elif self.PW_REP in ['BIGM_SOS1','BIGM_BIN']:
			self._construct_BIGM(INDEX_SET_PW)
		    elif self.PW_REP == 'DCC':
			self._construct_DCC(INDEX_SET_PW)
		    elif self.PW_REP == 'DLOG':
			self._construct_DLOG(INDEX_SET_PW)
		    elif self.PW_REP == 'CC':
			self._construct_CC(INDEX_SET_PW)
		    elif self.PW_REP == 'LOG':
			self._construct_LOG(INDEX_SET_PW)
		    elif self.PW_REP == 'MC':
			self._construct_MC(INDEX_SET_PW)
		    elif self.PW_REP == 'INC':
			self._construct_INC(INDEX_SET_PW)

    
    def _define_F(self,candidate):
	# check that f_rule defines a function
	if candidate == None:
	    raise TypeError, "Piecewise kwd 'f_rule' is required."
	else:
	    test_point = 0.0
	    if self.PW_PTS != None:
		if self.PW_PTS.__class__ is dict:
		    test_point = self.PW_PTS.items()[0]
		    test_point = flatten_tuple((test_point[0],test_point[1][0]))
		elif self.PW_PTS.__class__ is tuple or self.PW_PTS.__class__ is list:
		    test_point = self.PW_PTS[0]
		else:
		    raise TypeError, "Piecewise kwd 'pw_pts' must be of type dict, list, or tuple"
	    elif self.GRAD_PTS != None:
		if self.GRAD_PTS.__class__ is dict:
		    test_point = self.GRAD_PTS.items()[0]
		    test_point = flatten_tuple((test_point[0],test_point[1][0]))
		elif self.GRAD_PTS.__class__ is tuple or self.GRAD_PTS.__class__ is list:
		    test_point = self.GRAD_PTS[0]
		else:
		    raise TypeError, "Piecewise kwd 'tan_pts' must be of type dict, list, or tuple"
	    else:
		raise AssertionError, "Must specify at least one of 'tan_pts' or 'pw_points' as kwd to Piecewise"
	    try:
		if test_point.__class__ is tuple:
		    candidate(self._model(),*(test_point))
		else:
		    candidate(self._model(),*(test_point,))
	    except Exception:
		raise TypeError, "Piecewise kwd 'f_rule' must be callable with the form f(model,x),\n" \
		                +"where the first argument 'model' is a Pyomo model and the second argument \n" \
		                +"'x' is a number"
	    else:
		self._F_imp = candidate

    def _F(self,m,*args):
	# we cast to float to avoid integer division in case the 
	# user supplies integer type points and return values
	return float(self._F_imp(m,*flatten_tuple(args)))
	
    def _define_d_F(self,candidate):
	# check that d_f_rule defines a function
	if (candidate == None) and (self.GRAD_PTS != None):
	    raise TypeError, "Piecewise kwd 'd_f_rule' is required when kwd 'tan_pts' is specified."
	elif (self.GRAD_PTS == None) and (candidate != None):
	    raise TypeError, "Piecewise kwd 'tan_pts' is required when kwd 'd_f_rule' is specified."
	else:
	    test_point = 0.0
	    if self.GRAD_PTS != None:
		if self.GRAD_PTS.__class__ is dict:
		    test_point = self.GRAD_PTS.items()[0]
		    test_point = flatten_tuple((test_point[0],test_point[1][0]))
		elif self.GRAD_PTS.__class__ is tuple or self.GRAD_PTS.__class__ is list:
		    test_point = self.GRAD_PTS[0]
		else:
		    raise TypeError, "Piecewise kwd 'tan_pts' must be of type dict, list, or tuple"
	    try:
		if test_point.__class__ is tuple:
		    candidate(self._model(),*(test_point))
		else:
		    candidate(self._model(),*(test_point,))
	    except Exception:
		raise TypeError, "Piecewise kwd 'd_f_rule' must be callable with the form f(model,x),\n" \
		                +"where the first argument 'model' is a Pyomo model and the second argument \n" \
		                +"'x' is a number"
	    self._d_F_imp = candidate	

    def _d_F(self,m,*args):
	# we cast to float to avoid integer division in case the 
	# user supplies integer type points and return values
	return float(self._d_F_imp(m,*flatten_tuple(args)))
    
    def _update_dicts(self,name,_object_):
	if isinstance(_object_,Constraint) or isinstance(_object_,SOSConstraint):
	    constraint_name = self.name+'_'+name
	    if hasattr(self._model(),constraint_name):
		raise AssertionError, "Error: "+self.name+" trying to overwrite model attribute: "+constraint_name
	    setattr(self._model(),constraint_name,_object_)
	    self._constraints_dict[constraint_name] = getattr(self._model(), constraint_name)
	    return None
	elif isinstance(_object_,_VarArray):
	    var_name = self.name+'_'+name
	    if hasattr(self._model(),var_name):
		raise AssertionError, "Error: "+self.name+" trying to overwrite model attribute: "+var_name
	    setattr(self._model(),var_name,_object_)
	    self._vars_dict.update([(v.name,v) for (n,v) in getattr(self._model(), var_name).iteritems()])
	    return var_name
	elif isinstance(_object_,_VarElement):
	    var_name = self.name+'_'+name
	    if hasattr(self._model(),var_name):
		raise AssertionError, "Error: "+self.name+" trying to overwrite model attribute: "+var_name
	    setattr(self._model(),var_name,_object_)
	    self._vars_dict[var_name] = getattr(self._model(), var_name)
	    return var_name
	elif isinstance(_object_,_BaseSet):
	    set_name = self.name+'_'+name
	    if hasattr(self._model(),set_name):
		raise AssertionError, "Error: "+self.name+" trying to overwrite model attribute: "+set_name
	    setattr(self._model(),set_name,_object_)
	    self._sets_dict[set_name] = getattr(self._model(), set_name)
	    return set_name
    
    
    def variables(self):
	"""
	Returns a dictionary of the model variables created by this class.
	Key, Value pairs are (var.name, var)
	"""
	return self._vars_dict
    
    def constraints(self):
	"""
	Returns a dictionary of the model constraints created by this class.
	Key, Value pairs are (constraint.name, constraint)
	"""
	return self._constraints_dict
    
    def sets(self):
	"""
	Returns a dictionary of the model sets created by this class.
	Key, Value pairs are (set.name, set)
	"""
	return self._sets_dict
    
    def components(self):
	"""
	Returns a dictionary of the model components created by this class.
	Key, Value pairs are (component.name, component)
	"""
	tmp_dict = {}
	tmp_dict.update(self._vars_dict)
	tmp_dict.update(self._sets_dict)
	tmp_dict.update(self._constraints_dict)
	return tmp_dict

    def _construct_linear_estimators(self, INDEX_SET_TANGENT):
	
	def linear_estimators_LINEAR_indices_init(model):
	    if self._element_mode:
		return (i for i in xrange(len(self._grad_pts())))
	    else:
		return (t+(i,) for t in INDEX_SET_TANGENT.tuplize() \
		              for i in xrange(len(self._grad_pts(t))))
	tangent_indices = self._update_dicts('tangent_indices',Set(dimen=self._index_dimen+1, ordered=True, rule=linear_estimators_LINEAR_indices_init))


	def linear_estimators_constraint_rule(model,*args):
	    t = args[:-1]
	    i = args[-1]
	    LHS = self._getvar(model,self.YVAR.name,t)
	    F_AT_XO = self._F(model,t,self._grad_pts(t)[i])
	    dF_AT_XO = self._d_F(model,t,self._grad_pts(t)[i])
	    X_MINUS_XO = (self._getvar(model,self.XVAR.name,t)-self._grad_pts(t)[i])
	    if self.GRAD_TYPE == 'LB':
		return LHS >= F_AT_XO + dF_AT_XO*X_MINUS_XO
	    elif self.GRAD_TYPE == 'UB':
		return LHS <= F_AT_XO + dF_AT_XO*X_MINUS_XO

	self._update_dicts('tangent_constraint' , Constraint(getattr(self._model(),tangent_indices),rule=linear_estimators_constraint_rule))
    
	
    def _construct_simple_single_bound(self, INDEX_SET_SIMPLE):
	
	def SIMPLE_LINEAR_constraint1_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    F_AT_XO = self._F(model,t,min(self._pw_pts(t)))
	    dF_AT_XO = (float(self._F(model,t,max(self._pw_pts(t)))-self._F(model,t,min(self._pw_pts(t))))/float(max(self._pw_pts(t))-min(self._pw_pts(t))))
	    X_MINUS_XO = (self._getvar(model,self.XVAR.name,t)-min(self._pw_pts(t)))
	    if self.PW_TYPE == 'UB':
		return LHS <= F_AT_XO + dF_AT_XO*X_MINUS_XO	
	    elif self.PW_TYPE == 'LB':
		return LHS >= F_AT_XO + dF_AT_XO*X_MINUS_XO	
	    elif self.PW_TYPE == 'EQ':
		return LHS == F_AT_XO + dF_AT_XO*X_MINUS_XO

	self._update_dicts('simplified_single_line_constraint',Constraint(INDEX_SET_SIMPLE,rule=SIMPLE_LINEAR_constraint1_rule))
	
    def _construct_simple_bounds(self, INDEX_SET_SIMPLE_BOUNDS):
	
	def simple_bounds_indices_init(model):
	    if self._element_mode:
		return (i for i in xrange(len(self._pw_pts())-1))
	    else:
		return (t+(i,) for t in INDEX_SET_SIMPLE_BOUNDS.tuplize() \
		              for i in xrange(len(self._pw_pts(t))-1))
	simple_bounds_indices = self._update_dicts('simplified_bounds_indices',Set(dimen=self._index_dimen+1,ordered=True, rule=simple_bounds_indices_init))
	
	
	def SIMPLE_LINEAR_constraint1_rule(model,*args):
	    t = args[:-1]
	    i = args[-1]
	    LHS = self._getvar(model,self.YVAR.name,t)
	    F_AT_XO = self._F(model,t,self._pw_pts(t)[i])
	    dF_AT_XO = (float(self._F(model,t,self._pw_pts(t)[i+1])-self._F(model,t,self._pw_pts(t)[i]))/float(self._pw_pts(t)[i+1]-self._pw_pts(t)[i]))
	    X_MINUS_XO = (self._getvar(model,self.XVAR.name,t)-self._pw_pts(t)[i])
	    if self.PW_TYPE == 'UB':
		return LHS <= F_AT_XO + dF_AT_XO*X_MINUS_XO
	    elif self.PW_TYPE == 'LB':
		return LHS >= F_AT_XO + dF_AT_XO*X_MINUS_XO

	self._update_dicts('simplified_bounds_constraint',Constraint(getattr(self._model(),simple_bounds_indices),rule=SIMPLE_LINEAR_constraint1_rule))
    
    def _construct_SOS2(self, INDEX_SET_SOS2):
	
	def SOS_indices_init(*t):
	    if self._element_mode:
		return (i for i in xrange(len(self._pw_pts(t))))
	    else:
		if type(t[0]) is tuple:
		    return (t[0]+(i,) for i in xrange(len(self._pw_pts(t))))
		else:
		    return ((t[0],i) for i in xrange(len(self._pw_pts(t))))
	def y_indices_init(model):
	    if self._element_mode:
		return (i for i in xrange(len(self._pw_pts())))
	    else:
		return (t+(i,) for t in INDEX_SET_SOS2.tuplize() for i in xrange(len(self._pw_pts(t))))

	SOS_indices = ''
	if self._element_mode:
	    SOS_indices += self._update_dicts('SOS2_indices',Set(INDEX_SET_SOS2,dimen=self._index_dimen+1, ordered=True, \
	                                 initialize=SOS_indices_init()))
	else:
	    SOS_indices += self._update_dicts('SOS2_indices',Set(INDEX_SET_SOS2,dimen=self._index_dimen+1, ordered=True, \
	                                 initialize=dict([(t,SOS_indices_init(t)) for t in INDEX_SET_SOS2 ])))
	y_indices = self._update_dicts('y_SOS2_indices',Set(ordered=True, dimen=self._index_dimen+1,initialize=y_indices_init))
	
	#Add SOS2 weighting variable to self._model()
	y = self._update_dicts('y_SOS2',Var(getattr(self._model(),y_indices),within=NonNegativeReals))
	
	#Add SOS2 constraints to self._model()
	def SOS2_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,y,t,i)*self._pw_pts(t)[i] for i in xrange(len(self._pw_pts(t))))
	def SOS2_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = sum(self._getvar(model,y,t,i)*self._F(model,t,self._pw_pts(t)[i]) for i in xrange(len(self._pw_pts(t))))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def SOS2_constraint3_rule(model,*t):
	    return sum(self._getvar(model,y,t,j) for j in xrange(len(self._pw_pts(t)))) == 1
	
	if self._element_mode is True:
	    self._update_dicts('SOS2_constraint1',Constraint(rule=SOS2_constraint1_rule))
	    self._update_dicts('SOS2_constraint2',Constraint(rule=SOS2_constraint2_rule))
	    self._update_dicts('SOS2_constraint3',Constraint(rule=SOS2_constraint3_rule))
	    self._update_dicts('SOS2_constraint4',SOSConstraint(var=getattr(self._model(),y), sos=2))
	else:
	    self._update_dicts('SOS2_constraint1',Constraint(INDEX_SET_SOS2,rule=SOS2_constraint1_rule))
	    self._update_dicts('SOS2_constraint2',Constraint(INDEX_SET_SOS2,rule=SOS2_constraint2_rule))
	    self._update_dicts('SOS2_constraint3',Constraint(INDEX_SET_SOS2,rule=SOS2_constraint3_rule))
	    self._update_dicts('SOS2_constraint4',SOSConstraint(INDEX_SET_SOS2, var=getattr(self._model(),y), set=getattr(self._model(),SOS_indices), sos=2))

    def _construct_BIGM(self,BIGM_SET):
	
	#Add dictionary of optimal big M values as attribute to self._model()
	#same index as SOS variable
	OPT_M = {}
	OPT_M['UB'] = {}
	OPT_M['LB'] = {}

	if self.PW_TYPE in ['UB','EQ']:
	    OPT_M['UB'] = self._find_M(self.PW_PTS, 'UB')
	if self.PW_TYPE in ['LB','EQ']:
	    OPT_M['LB'] = self._find_M(self.PW_PTS, 'LB')
	
	all_keys = set(OPT_M['UB'].keys()).union(OPT_M['LB'].keys())
	full_indices = []
	if self._element_mode:
	    full_indices.extend([i for i in xrange(1,len(self._pw_pts()))])
	else:
	    full_indices.extend([t+(i,) for t in BIGM_SET.tuplize() for i in xrange(1,len(self._pw_pts(t)))])
	y_indices = ''
	y = ''
	if len(all_keys) > 0:
	    y_indices += self._update_dicts('y_'+self.PW_REP+'_indices',Set(ordered=True, dimen=self._index_dimen+1,initialize=all_keys))
	    
	    #Add indicator variable to self._model()
	    def y_domain():
		if self.PW_REP == 'BIGM_BIN':
		    return Binary
		elif self.PW_REP == 'BIGM_SOS1':
		    return NonNegativeReals
	    y += self._update_dicts('y_'+self.PW_REP,Var(getattr(self._model(),y_indices),within=y_domain()))
	
	def BIGM_LINEAR_constraint1_rule(model,*args):
	    t = args[:-1]
	    i = args[-1]
	    if self._element_mode:
		targs = i
	    else:
		targs = flatten_tuple(args)
	    if (self.PW_TYPE == 'UB') or (self.PW_TYPE == 'EQ'):
		rhs = 1.0
		if targs not in OPT_M['UB'].keys():
		    rhs *= 0.0
		else:
		    rhs *= OPT_M['UB'][targs]*(1-self._getvar(model,y,t,i))
		return self._getvar(model,self.YVAR.name,t) - (self._F(model,t,self._pw_pts(t)[i-1]) + ((self._F(model,t,self._pw_pts(t)[i])-self._F(model,t,self._pw_pts(t)[i-1]))/(self._pw_pts(t)[i]-self._pw_pts(t)[i-1]))*(self._getvar(model,self.XVAR.name,t)-self._pw_pts(t)[i-1])) <= rhs
	    elif self.PW_TYPE == 'LB':
		rhs = 1.0
		if targs not in OPT_M['LB'].keys():
		    rhs *= 0.0
		else:
		    rhs *= OPT_M['LB'][targs]*(1-self._getvar(model,y,t,i))
		return self._getvar(model,self.YVAR.name,t) - (self._F(model,t,self._pw_pts(t)[i-1]) + ((self._F(model,t,self._pw_pts(t)[i])-self._F(model,t,self._pw_pts(t)[i-1]))/(self._pw_pts(t)[i]-self._pw_pts(t)[i-1]))*(self._getvar(model,self.XVAR.name,t)-self._pw_pts(t)[i-1])) >= rhs
	def BIGM_LINEAR_constraint2_rule(model,*t):
	    if self._element_mode:
		expr = [self._getvar(model,y,t,i) for i in xrange(1,len(self._pw_pts())) if i in all_keys]
	    else:
		expr = [self._getvar(model,y,t,i) for i in xrange(1,len(self._pw_pts(t))) if flatten_tuple((t,i)) in all_keys]
	    if len(expr) > 0:
		return sum(expr) == 1
	    else:
		return Constraint.Skip
	def BIGM_LINEAR_constraintAFF_rule(model,*args):
	    t = args[:-1]
	    i = args[-1]
	    targs = 0
	    if self._element_mode:
		targs = i
	    else:
		targs = flatten_tuple(args)
	    rhs = 1.0
	    if targs not in OPT_M['LB'].keys():
		rhs *= 0.0
	    else:
		rhs *= OPT_M['LB'][targs]*(1-self._getvar(model,y,t,i))
	    return self._getvar(model,self.YVAR.name,t) - (self._F(model,t,self._pw_pts(t)[i-1]) + ((self._F(model,t,self._pw_pts(t)[i])-self._F(model,t,self._pw_pts(t)[i-1]))/(self._pw_pts(t)[i]-self._pw_pts(t)[i-1]))*(self._getvar(model,self.XVAR.name,t)-self._pw_pts(t)[i-1])) >= rhs

	self._update_dicts(self.PW_REP+'_constraint1',Constraint(full_indices,rule=BIGM_LINEAR_constraint1_rule))
	if len(all_keys) > 0:
	    if self._element_mode:
		self._update_dicts(self.PW_REP+'_constraint2',Constraint(rule=BIGM_LINEAR_constraint2_rule))
	    else:
		self._update_dicts(self.PW_REP+'_constraint2',Constraint(BIGM_SET,rule=BIGM_LINEAR_constraint2_rule))
	if self.PW_TYPE == 'EQ':
		self._update_dicts(self.PW_REP+'_constraint3',Constraint(full_indices,rule=BIGM_LINEAR_constraintAFF_rule))
	
	if len(all_keys) > 0:
	    if (self.PW_REP == 'BIGM_SOS1'):
		def BIGM_SOS1_indices_init(*t):
		    if self._element_mode is True:
			return [i for i in xrange(len(self._pw_pts())) if i in all_keys]
		    else:
			if type(t[0]) is tuple:
			    return [t[0]+(i,) for i in xrange(1,len(self._pw_pts(t))) if t[0]+(i,) in all_keys]
			else:
			    return [(t[0],i) for i in xrange(1,len(self._pw_pts(t))) if (t[0],i) in all_keys]
	    
		if self._element_mode:
		    self._update_dicts('BIGM_SOS1_constraintSOS',SOSConstraint(var=getattr(self._model(),y), sos=1))
		else:
		    SOS_indices = self._update_dicts('BIGM_SOS1_indices',Set(list(BIGM_SET),dimen=self._index_dimen+1, ordered=True, \
			                                                    initialize=dict([(t,BIGM_SOS1_indices_init(t)) for t in BIGM_SET])))
		    self._update_dicts('BIGM_SOS1_constraintSOS',SOSConstraint(BIGM_SET, var=getattr(self._model(),y), set=getattr(self._model(),SOS_indices), sos=1))

    def _construct_DCC(self,DCC_SET):
	
	def DCC_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))

	    else:
		return (t+(i,) for t in DCC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def DCC_poly_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))))
	def DCC_VERTICES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(i,) for t in DCC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))+1))
	def DCC_vert_init(args):
	    try:
		t = args[:-1]
		p = args[-1]
	    except:
		p = args
	    return (i for i in xrange(p,p+2))
	def DCC_lamba_set_init(model):
	    if self._element_mode is True:
    		return ((p,v) for p in xrange(1,len(self._pw_pts())) \
		                for v in xrange(1,len(self._pw_pts())+1))
	    else:
		# BOTTLENECK: speed/memory, this set can be extremely large and time consuming to
	        #             build when number of indices and breakpoints is large.
		return (t+(p,v) for t in DCC_SET.tuplize() \
		                for p in xrange(1,len(self._pw_pts(t))) \
		                for v in xrange(1,len(self._pw_pts(t))+1))
	
	DCC_POLYTOPES = self._update_dicts('DCC_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=DCC_POLYTOPES_init))
	if self._element_mode:
	    DCC_poly = self._update_dicts('DCC_poly',Set(ordered=True, initialize=DCC_poly_init()))
	else:
	    DCC_poly = self._update_dicts('DCC_poly',Set(DCC_SET,ordered=True, \
		                                         initialize=dict([(t,DCC_poly_init(t)) for t in DCC_SET])))
	DCC_VERTICES = self._update_dicts('DCC_VERTICES',Set(ordered=True,dimen=self._index_dimen+1,initialize=DCC_VERTICES_init))
	DCC_vert = self._update_dicts('DCC_vert',Set(getattr(self._model(),DCC_POLYTOPES),ordered=True, \
	                                             initialize=dict([(args,DCC_vert_init(args)) for args in getattr(self._model(),DCC_POLYTOPES)])))	
	DCC_LAMBDA_SET = self._update_dicts('DCC_LAMBDA_SET',Set(ordered=True,dimen=self._index_dimen+2,initialize=DCC_lamba_set_init))
	
	lmda = self._update_dicts('DCC_LAMBDA',Var(getattr(self._model(),DCC_LAMBDA_SET),within=PositiveReals))
	
	
	y = self._update_dicts('DCC_BIN_y',Var(getattr(self._model(),DCC_POLYTOPES),within=Binary))
	
	def DCC_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,lmda,t,p,v)*self._pw_pts(t)[v-1] for p in self._getset(model,DCC_poly,t) for v in self._getset(model,DCC_vert,t,p))
	def DCC_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = sum(self._getvar(model,lmda,t,p,v)*self._F(model,t,self._pw_pts(t)[v-1]) for p in self._getset(model,DCC_poly,t) for v in self._getset(model,DCC_vert,t,p))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def DCC_LINEAR_constraint3_rule(model,*args):
	    t = args[:-1]
	    p = args[-1]
	    return self._getvar(model,y,t,p) == sum(self._getvar(model,lmda,t,p,v) for v in self._getset(model,DCC_vert,t,p))
	def DCC_LINEAR_constraint4_rule(model,*t):
	    return sum(self._getvar(model,y,t,p) for p in self._getset(model,DCC_poly,t)) == 1

	if self._element_mode:
	    self._update_dicts('DCC_constraint1',Constraint(rule=DCC_LINEAR_constraint1_rule))
	    self._update_dicts('DCC_constraint2',Constraint(rule=DCC_LINEAR_constraint2_rule))
	    self._update_dicts('DCC_constraint3',Constraint(getattr(self._model(),DCC_POLYTOPES),rule=DCC_LINEAR_constraint3_rule))
	    self._update_dicts('DCC_constraint4',Constraint(rule=DCC_LINEAR_constraint4_rule))
	else:
	    self._update_dicts('DCC_constraint1',Constraint(DCC_SET,rule=DCC_LINEAR_constraint1_rule))
	    self._update_dicts('DCC_constraint2',Constraint(DCC_SET,rule=DCC_LINEAR_constraint2_rule))
	    self._update_dicts('DCC_constraint3',Constraint(getattr(self._model(),DCC_POLYTOPES),rule=DCC_LINEAR_constraint3_rule))
	    self._update_dicts('DCC_constraint4',Constraint(DCC_SET,rule=DCC_LINEAR_constraint4_rule))


    def _construct_DLOG(self,DLOG_SET):
	
	L = {}
	L_i = 0
	B_ZERO = {}
	B_ZERO_l = []
	B_ONE = {}
	B_ONE_l = []
	if self._element_mode:
	    L_i += int(math.log(len(self._pw_pts())-1,2))
	    B_ZERO_l,B_ONE_l = _DLog_Branching_Scheme(L_i)
	else:
	    for t in DLOG_SET:
		L[t] = int(math.log(len(self._pw_pts(t))-1,2))
		L[(t,)] = L[t]
	    for t in sorted(L.keys()):
		B_ZERO[t],B_ONE[t] = _DLog_Branching_Scheme(L[t])
		B_ZERO[(t,)] = B_ZERO[t]
		B_ONE[(t,)] = B_ONE[t]
	    
	def DLOG_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))

	    else:
		return (t+(i,) for t in DLOG_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def DLOG_LENGTH_POLY_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,L_i+1))
	    else:
		return (t+(i,) for t in DLOG_SET.tuplize() \
		              for i in xrange(1,L[t]+1))
	def DLOG_poly_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))))
	def DLOG_poly_one_init(args):
	    if self._element_mode:
		l = args
		return B_ZERO_l[l]
	    else:
		t = args[:-1]
		l = args[-1]
		return B_ZERO[t][l]
	def DLOG_poly_zero_init(args):
	    if self._element_mode:
		l = args
		return B_ONE_l[l]
	    else:
		t = args[:-1]
		l = args[-1]
		return B_ONE[t][l]
	def DLOG_VERTICES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(i,) for t in DLOG_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))+1))
	def DLOG_vert_init(args):
	    try:
		t = args[:-1]
		p = args[-1]
	    except:
		p = args
	    return (i for i in xrange(p,p+2))
	def DLOG_lamba_set_init(model):
	    if self._element_mode:
		return ((p,v) for p in xrange(1,len(self._pw_pts())) \
		              for v in xrange(1,len(self._pw_pts())+1))
	    else:
		# BOTTLENECK: speed/memory, this set can be extremely large and time consuming to
	        #             build when number of indices and breakpoints is large.
		return (t+(p,v) for t in DLOG_SET.tuplize() \
		                for p in xrange(1,len(self._pw_pts(t))) \
		                for v in xrange(1,len(self._pw_pts(t))+1))
	
	DLOG_POLYTOPES = self._update_dicts('DLOG_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=DLOG_POLYTOPES_init))
	DLOG_LENGTH_POLY = self._update_dicts('DLOG_LENGTH_POLY',Set(ordered=True,dimen=self._index_dimen+1,initialize=DLOG_LENGTH_POLY_init))
	if self._element_mode:
	    DLOG_poly = self._update_dicts('DLOG_poly',Set(ordered=True, \
		                                           initialize=DLOG_poly_init()))
	else:
	    DLOG_poly = self._update_dicts('DLOG_poly',Set(DLOG_SET,ordered=True, \
		                                           initialize=dict([(t,DLOG_poly_init(t)) for t in DLOG_SET])))
	DLOG_poly_one = self._update_dicts('DLOG_poly_one',Set(getattr(self._model(),DLOG_LENGTH_POLY),ordered=True, \
	                                                       initialize=dict([(args,DLOG_poly_one_init(args)) for args in getattr(self._model(),DLOG_LENGTH_POLY)])))
	DLOG_poly_zero = self._update_dicts('DLOG_poly_zero',Set(getattr(self._model(),DLOG_LENGTH_POLY),ordered=True, \
	                                                         initialize=dict([(args,DLOG_poly_zero_init(args)) for args in getattr(self._model(),DLOG_LENGTH_POLY)])))
	DLOG_VERTICES = self._update_dicts('DLOG_VERTICES',Set(ordered=True,dimen=self._index_dimen+1,initialize=DLOG_VERTICES_init))
	DLOG_vert = self._update_dicts('DLOG_vert',Set(getattr(self._model(),DLOG_POLYTOPES),ordered=True, \
	                                               initialize=dict([(args,DLOG_vert_init(args)) for args in getattr(self._model(),DLOG_POLYTOPES)])))	
	DLOG_LAMBDA_SET = self._update_dicts('DLOG_LAMBDA_SET',Set(ordered=True,dimen=self._index_dimen+2,initialize=DLOG_lamba_set_init))
	
	lmda = self._update_dicts('DLOG_LAMBDA',Var(getattr(self._model(),DLOG_LAMBDA_SET),within=PositiveReals))
	y = self._update_dicts('DLOG_BIN_y',Var(getattr(self._model(),DLOG_LENGTH_POLY),within=Binary))
	
	def DLOG_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,lmda,t,p,v)*self._pw_pts(t)[v-1] for p in self._getset(model,DLOG_poly,t) for v in self._getset(model,DLOG_vert,t,p))
	def DLOG_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = sum(self._getvar(model,lmda,t,p,v)*self._F(model,t,self._pw_pts(t)[v-1]) for p in self._getset(model,DLOG_poly,t) for v in self._getset(model,DLOG_vert,t,p))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def DLOG_LINEAR_constraint3_rule(model,*t):
	    return 1 == sum(self._getvar(model,lmda,t,p,v) for p in self._getset(model,DLOG_poly,t) for v in self._getset(model,DLOG_vert,t,p))
	def DLOG_LINEAR_constraint4_rule(model,*args):
	    t = args[:-1]
	    l = args[-1]
	    return sum(self._getvar(model,lmda,t,p,v) for p in self._getvar(model,DLOG_poly_one,t,l) for v in self._getset(model,DLOG_vert,t,p)) <= self._getvar(model,y,t,l)
	def DLOG_LINEAR_constraint5_rule(model,*args):
	    t = args[:-1]
	    l = args[-1]
	    return sum(self._getvar(model,lmda,t,p,v) for p in self._getvar(model,DLOG_poly_zero,t,l) for v in self._getset(model,DLOG_vert,t,p)) <= (1-self._getvar(model,y,t,l))

	if self._element_mode:
	    self._update_dicts('DLOG_constraint1',Constraint(rule=DLOG_LINEAR_constraint1_rule))
	    self._update_dicts('DLOG_constraint2',Constraint(rule=DLOG_LINEAR_constraint2_rule))
	    self._update_dicts('DLOG_constraint3',Constraint(rule=DLOG_LINEAR_constraint3_rule))
	    self._update_dicts('DLOG_constraint4',Constraint(getattr(self._model(),DLOG_LENGTH_POLY),rule=DLOG_LINEAR_constraint4_rule))
	    self._update_dicts('DLOG_constraint5',Constraint(getattr(self._model(),DLOG_LENGTH_POLY),rule=DLOG_LINEAR_constraint5_rule))
	else:
	    self._update_dicts('DLOG_constraint1',Constraint(DLOG_SET,rule=DLOG_LINEAR_constraint1_rule))
	    self._update_dicts('DLOG_constraint2',Constraint(DLOG_SET,rule=DLOG_LINEAR_constraint2_rule))
	    self._update_dicts('DLOG_constraint3',Constraint(DLOG_SET,rule=DLOG_LINEAR_constraint3_rule))
	    self._update_dicts('DLOG_constraint4',Constraint(getattr(self._model(),DLOG_LENGTH_POLY),rule=DLOG_LINEAR_constraint4_rule))
	    self._update_dicts('DLOG_constraint5',Constraint(getattr(self._model(),DLOG_LENGTH_POLY),rule=DLOG_LINEAR_constraint5_rule))

    def _construct_CC(self,CC_SET):
	
	def CC_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))
	    else:
		return (t+(i,) for t in CC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def CC_poly_init(args):
	    if self._element_mode:
		v = args
		if v == 1:
		    return [v]
		elif v == len(self._pw_pts()):
		    return [v-1]
		else:
		    return [v-1,v]
	    else:
		t = args[:-1]
		v = args[-1]
		if v == 1:
		    return [v]
		elif v == len(self._pw_pts(t)):
		    return [v-1]
		else:
		    return [v-1,v]
	def CC_VERTICES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(i,) for t in CC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))+1))
	def CC_vert_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))+1))
	def CC_lamba_set_init(model):
	    if self._element_mode:
		return (v for v in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(v,) for t in CC_SET.tuplize() \
		              for v in xrange(1,len(self._pw_pts(t))+1))
	
	CC_VERTICES = self._update_dicts('CC_VERTICES',Set(ordered=True,dimen=self._index_dimen+1,initialize=CC_VERTICES_init))
	if self._element_mode:
	    CC_vert = self._update_dicts('CC_vert',Set(ordered=True, initialize=CC_vert_init()))
	else:
	    CC_vert = self._update_dicts('CC_vert',Set(CC_SET,ordered=True,\
		                                       initialize=dict([(t,CC_vert_init(t)) for t in CC_SET])))
	CC_POLYTOPES = self._update_dicts('CC_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=CC_POLYTOPES_init))
	CC_poly = self._update_dicts('CC_poly',Set(getattr(self._model(),CC_VERTICES),ordered=True, \
	                                           initialize=dict([(args,CC_poly_init(args)) for args in getattr(self._model(),CC_VERTICES)])))
	CC_LAMBDA_SET = self._update_dicts('CC_LAMBDA_SET',Set(ordered=True,dimen=self._index_dimen+1,initialize=CC_lamba_set_init))
	
	lmda = self._update_dicts('CC_LAMBDA',Var(getattr(self._model(),CC_LAMBDA_SET),within=NonNegativeReals))
	y = self._update_dicts('CC_BIN_y',Var(getattr(self._model(),CC_POLYTOPES),within=Binary))

	
	def CC_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,lmda,t,v)*self._pw_pts(t)[v-1] for v in self._getset(model,CC_vert,t))
	def CC_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = sum(self._getvar(model,lmda,t,v)*self._F(model,t,self._pw_pts(t)[v-1]) for v in self._getset(model,CC_vert,t))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def CC_LINEAR_constraint3_rule(model,*t):
	    return 1 == sum(self._getvar(model,lmda,t,v) for v in self._getset(model,CC_vert,t))
	def CC_LINEAR_constraint4_rule(model,*args):
	    t = args[:-1]
	    v = args[-1]
	    return self._getvar(model,lmda,t,v) <= sum(self._getvar(model,y,t,p) for p in self._getset(model,CC_poly,t,v))
	def CC_LINEAR_constraint5_rule(model,*t):
	    return sum(self._getvar(model,y,t,p) for p in xrange(1,len(self._pw_pts(t)))) == 1

	if self._element_mode:
	    self._update_dicts('CC_constraint1',Constraint(rule=CC_LINEAR_constraint1_rule))
	    self._update_dicts('CC_constraint2',Constraint(rule=CC_LINEAR_constraint2_rule))
	    self._update_dicts('CC_constraint3',Constraint(rule=CC_LINEAR_constraint3_rule))
	    self._update_dicts('CC_constraint4',Constraint(getattr(self._model(),CC_VERTICES),rule=CC_LINEAR_constraint4_rule))
	    self._update_dicts('CC_constraint5',Constraint(rule=CC_LINEAR_constraint5_rule))
	else:
	    self._update_dicts('CC_constraint1',Constraint(CC_SET,rule=CC_LINEAR_constraint1_rule))
	    self._update_dicts('CC_constraint2',Constraint(CC_SET,rule=CC_LINEAR_constraint2_rule))
	    self._update_dicts('CC_constraint3',Constraint(CC_SET,rule=CC_LINEAR_constraint3_rule))
	    self._update_dicts('CC_constraint4',Constraint(getattr(self._model(),CC_VERTICES),rule=CC_LINEAR_constraint4_rule))
	    self._update_dicts('CC_constraint5',Constraint(CC_SET,rule=CC_LINEAR_constraint5_rule))

    def _construct_LOG(self,LOG_SET):
	
	L = {}
	Li = 0
	S = {}
	Si = 0
	LEFT = {}
	LEFT_l = []
	RIGHT = {}
	RIGHT_l = []
	if self._element_mode:
	    Li += int(math.log(len(self._pw_pts())-1,2))
	    Si,LEFT_l,RIGHT_l = _Log_Branching_Scheme(Li)
	else:
	    for t in LOG_SET:
		L[t] = int(math.log(len(self._pw_pts(t))-1,2))
		S[t],LEFT[t],RIGHT[t] = _Log_Branching_Scheme(L[t])
		S[(t,)] = S[t]
		LEFT[(t,)] = LEFT[t]
		RIGHT[(t,)] = RIGHT[t]
	
	
	def LOG_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))
	    else:
		return (t+(i,) for t in LOG_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def LOG_poly_init(args):
	    if self._element_mode:
		v = args
		if v == 1:
		    return [v]
		elif v == len(self._pw_pts()):
		    return [v-1]
		else:
		    return [v-1,v]
	    else:
		t = args[:-1]
		v = args[-1]
		if v == 1:
		    return [v]
		elif v == len(self._pw_pts(t)):
		    return [v-1]
		else:
		    return [v-1,v]

	def LOG_VERTICES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(i,) for t in LOG_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))+1))
	def LOG_vert_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))+1))
	def LOG_lamba_set_init(model):
	    if self._element_mode:
		return (v for v in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(v,) for t in LOG_SET.tuplize() \
		              for v in xrange(1,len(self._pw_pts(t))+1))
	def LOG_BRANCHING_SCHEME_init(model):
	    if self._element_mode:
		return (s for s in Si)
	    else:
		return (t+(s,) for t in LOG_SET.tuplize() \
		              for s in S[t])
	def LOG_BRANCHING_LEFT_init(args):
	    if self._element_mode:
		s = args
		return LEFT_l[s]
	    else:
		t = args[:-1]
		s = args[-1]
		return LEFT[t][s]
	def LOG_BRANCHING_RIGHT_init(args):
	    if self._element_mode:
		s = args
		return RIGHT_l[s]
	    else:
		t = args[:-1]
		s = args[-1]
		return RIGHT[t][s]
	
	LOG_VERTICES = self._update_dicts('LOG_VERTICES',Set(ordered=True,dimen=self._index_dimen+1,initialize=LOG_VERTICES_init))
	if self._element_mode:
	    LOG_vert = self._update_dicts('LOG_vert',Set(ordered=True, initialize=LOG_vert_init()))
	else:
	    LOG_vert = self._update_dicts('LOG_vert',Set(LOG_SET,ordered=True, \
		                                         initialize=dict([(t,LOG_vert_init(t)) for t in LOG_SET])))
	LOG_POLYTOPES = self._update_dicts('LOG_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=LOG_POLYTOPES_init))
	LOG_poly = self._update_dicts('LOG_poly',Set(getattr(self._model(),LOG_VERTICES),ordered=True, \
	                                                     initialize=dict([(args,LOG_poly_init(args)) for args in getattr(self._model(),LOG_VERTICES)])))
	LOG_LAMBDA_SET = self._update_dicts('LOG_LAMBDA_SET',Set(ordered=True,dimen=self._index_dimen+1,initialize=LOG_lamba_set_init))
	LOG_BRANCHING_SCHEME = self._update_dicts('LOG_BRANCHING_SCHEME',Set(ordered=True,dimen=self._index_dimen+1,initialize=LOG_BRANCHING_SCHEME_init))
	LOG_BRANCHING_LEFT = self._update_dicts('LOG_BRANCHING_LEFT',Set(getattr(self._model(),LOG_BRANCHING_SCHEME),ordered=True, \
	                                                                 initialize=dict([(args,LOG_BRANCHING_LEFT_init(args)) for args in getattr(self._model(),LOG_BRANCHING_SCHEME)])))
	LOG_BRANCHING_RIGHT = self._update_dicts('LOG_BRANCHING_RIGHT',Set(getattr(self._model(),LOG_BRANCHING_SCHEME),ordered=True,\
	                                                                   initialize=dict([(args,LOG_BRANCHING_RIGHT_init(args)) for args in getattr(self._model(),LOG_BRANCHING_SCHEME)])))
	
	lmda = self._update_dicts('LOG_LAMBDA',Var(getattr(self._model(),LOG_LAMBDA_SET),within=NonNegativeReals))
	y = self._update_dicts('LOG_BIN_y',Var(getattr(self._model(),LOG_BRANCHING_SCHEME),within=Binary))

	def LOG_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,lmda,t,v)*self._pw_pts(t)[v-1] for v in self._getset(model,LOG_vert,t))
	def LOG_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = sum(self._getvar(model,lmda,t,v)*self._F(model,t,self._pw_pts(t)[v-1]) for v in self._getset(model,LOG_vert,t))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def LOG_LINEAR_constraint3_rule(model,*t):
	    return 1 == sum(self._getvar(model,lmda,t,v) for v in self._getset(model,LOG_vert,t))
	def LOG_LINEAR_constraint4_rule(model,*args):
	    t = args[:-1]
	    s = args[-1]
	    return sum(self._getvar(model,lmda,t,v) for v in self._getset(model,LOG_BRANCHING_LEFT,t,s)) <= self._getvar(model,y,t,s)
	def LOG_LINEAR_constraint5_rule(model,*args):
	    t = args[:-1]
	    s = args[-1]
	    return sum(self._getvar(model,lmda,t,v) for v in self._getset(model,LOG_BRANCHING_RIGHT,t,s)) <= (1-self._getvar(model,y,t,s))

	if self._element_mode:
	    self._update_dicts('LOG_constraint1',Constraint(rule=LOG_LINEAR_constraint1_rule))
	    self._update_dicts('LOG_constraint2',Constraint(rule=LOG_LINEAR_constraint2_rule))
	    self._update_dicts('LOG_constraint3',Constraint(rule=LOG_LINEAR_constraint3_rule))
	    self._update_dicts('LOG_constraint4',Constraint(getattr(self._model(),LOG_BRANCHING_SCHEME),rule=LOG_LINEAR_constraint4_rule))
	    self._update_dicts('LOG_constraint5',Constraint(getattr(self._model(),LOG_BRANCHING_SCHEME),rule=LOG_LINEAR_constraint5_rule))
	else:
	    self._update_dicts('LOG_constraint1',Constraint(LOG_SET,rule=LOG_LINEAR_constraint1_rule))
	    self._update_dicts('LOG_constraint2',Constraint(LOG_SET,rule=LOG_LINEAR_constraint2_rule))
	    self._update_dicts('LOG_constraint3',Constraint(LOG_SET,rule=LOG_LINEAR_constraint3_rule))
	    self._update_dicts('LOG_constraint4',Constraint(getattr(self._model(),LOG_BRANCHING_SCHEME),rule=LOG_LINEAR_constraint4_rule))
	    self._update_dicts('LOG_constraint5',Constraint(getattr(self._model(),LOG_BRANCHING_SCHEME),rule=LOG_LINEAR_constraint5_rule))

    def _construct_MC(self,MC_SET):
	
	SLOPE = {}
	INTERSEPT = {}
	if self._element_mode:
	    for i in xrange(1,len(self._pw_pts())):
		SLOPE[i] = (self._F(self._model(),self._pw_pts()[i])-self._F(self._model(),self._pw_pts()[i-1]))/(self._pw_pts()[i]-self._pw_pts()[i-1])
		INTERSEPT[i] = self._F(self._model(),self._pw_pts()[i-1]) - (SLOPE[i]*self._pw_pts()[i-1])
	else:
	    for t in MC_SET:
		SLOPE[t] = {}
		INTERSEPT[t] = {}
		for i in xrange(1,len(self._pw_pts(t))):
		    SLOPE[t][i] = (self._F(self._model(),t,self._pw_pts(t)[i])-self._F(self._model(),t,self._pw_pts(t)[i-1]))/(self._pw_pts(t)[i]-self._pw_pts(t)[i-1])
		    INTERSEPT[t][i] = self._F(self._model(),t,self._pw_pts(t)[i-1]) - (SLOPE[t][i]*self._pw_pts(t)[i-1])
		SLOPE[(t,)] = SLOPE[t]
		INTERSEPT[(t,)] = INTERSEPT[t]
	
	def MC_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))
	    else:
		return (t+(i,) for t in MC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def MC_poly_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))))
	
	MC_POLYTOPES = self._update_dicts('MC_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=MC_POLYTOPES_init))
	if self._element_mode:
	    MC_poly = self._update_dicts('MC_poly',Set(ordered=True, initialize=MC_poly_init()))
	else:
	    MC_poly = self._update_dicts('MC_poly',Set(MC_SET,ordered=True, \
		                                       initialize=dict([(t,MC_poly_init(t)) for t in MC_SET])))
	
	xp = self._update_dicts('MC_X_POLY',Var(getattr(self._model(),MC_POLYTOPES)))
	y = self._update_dicts('MC_BIN_y',Var(getattr(self._model(),MC_POLYTOPES),within=Binary))
	
	def MC_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == sum(self._getvar(model,xp,t,p) for p in self._getset(model,MC_poly,t))
	def MC_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = 0
	    if self._element_mode:
		RHS += sum((self._getvar(model,xp,t,p)*SLOPE[p])+(self._getvar(model,y,t,p)*INTERSEPT[p]) for p in self._getset(model,MC_poly,t))
	    else:
		RHS += sum((self._getvar(model,xp,t,p)*SLOPE[t][p])+(self._getvar(model,y,t,p)*INTERSEPT[t][p]) for p in self._getset(model,MC_poly,t))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def MC_LINEAR_constraint3_rule(model,*args):
	    t = args[:-1]
	    p = args[-1]
	    return self._getvar(model,y,t,p)*self._pw_pts(t)[p-1] <= self._getvar(model,xp,t,p)
	def MC_LINEAR_constraint4_rule(model,*args):
	    t = args[:-1]
	    p = args[-1]
	    return self._getvar(model,xp,t,p)  <= self._getvar(model,y,t,p)*self._pw_pts(t)[p]
	def MC_LINEAR_constraint5_rule(model,*t):
	    return sum(self._getvar(model,y,t,p) for p in self._getset(model,MC_poly,t)) == 1
	    
	if self._element_mode:
	    self._update_dicts('MC_constraint1',Constraint(rule=MC_LINEAR_constraint1_rule))
	    self._update_dicts('MC_constraint2',Constraint(rule=MC_LINEAR_constraint2_rule))
	    self._update_dicts('MC_constraint3',Constraint(getattr(self._model(),MC_POLYTOPES),rule=MC_LINEAR_constraint3_rule))
	    self._update_dicts('MC_constraint4',Constraint(getattr(self._model(),MC_POLYTOPES),rule=MC_LINEAR_constraint4_rule))	    
	    self._update_dicts('MC_constraint5',Constraint(rule=MC_LINEAR_constraint5_rule))
	else:
	    self._update_dicts('MC_constraint1',Constraint(MC_SET,rule=MC_LINEAR_constraint1_rule))
	    self._update_dicts('MC_constraint2',Constraint(MC_SET,rule=MC_LINEAR_constraint2_rule))
	    self._update_dicts('MC_constraint3',Constraint(getattr(self._model(),MC_POLYTOPES),rule=MC_LINEAR_constraint3_rule))
	    self._update_dicts('MC_constraint4',Constraint(getattr(self._model(),MC_POLYTOPES),rule=MC_LINEAR_constraint4_rule))	    
	    self._update_dicts('MC_constraint5',Constraint(MC_SET,rule=MC_LINEAR_constraint5_rule))

    def _construct_INC(self,INC_SET):
	
	def INC_POLYTOPES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())))
	    else:
		return (t+(i,) for t in INC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))))
	def INC_poly_init(*t):
	    return (i for i in xrange(1,len(self._pw_pts(t))))
	def INC_VERTICES_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())+1))
	    else:
		return (t+(i,) for t in INC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))+1))
	def INC_Y_init(model):
	    if self._element_mode:
		return (i for i in xrange(1,len(self._pw_pts())-1))
	    else:
		return (t+(i,) for t in INC_SET.tuplize() \
		              for i in xrange(1,len(self._pw_pts(t))-1))
	
	INC_POLYTOPES = self._update_dicts('INC_POLYTOPES',Set(ordered=True,dimen=self._index_dimen+1,initialize=INC_POLYTOPES_init))
	if self._element_mode:
	    INC_poly = self._update_dicts('INC_poly',Set(ordered=True, initialize=INC_poly_init()))
	else:
	    INC_poly = self._update_dicts('INC_poly',Set(INC_SET,ordered=True, \
		                                         initialize=dict([(t,INC_poly_init(t)) for t in INC_SET])))
	INC_VERTICES = self._update_dicts('INC_VERTICES',Set(ordered=True,dimen=self._index_dimen+1,initialize=INC_VERTICES_init))
	INC_YSET = self._update_dicts('INC_YSET',Set(ordered=True,dimen=self._index_dimen+1,initialize=INC_Y_init))
	
	delta = self._update_dicts('INC_DELTA',Var(getattr(self._model(),INC_POLYTOPES)))
	if self._element_mode:
	    self._getvar(self._model(),delta,1).setub(1)
	    self._getvar(self._model(),delta,len(self._pw_pts())-1).setlb(0)
	else:
	    for t in INC_SET:
		self._getvar(self._model(),delta,t,1).setub(1)
		self._getvar(self._model(),delta,t,len(self._pw_pts(t))-1).setlb(0)
	y = self._update_dicts('INC_BIN_y',Var(getattr(self._model(),INC_YSET),within=Binary))
	
	def INC_LINEAR_constraint1_rule(model,*t):
	    return self._getvar(model,self.XVAR.name,t) == self._pw_pts(t)[0] + sum(self._getvar(model,delta,t,p)*(self._pw_pts(t)[p]-self._pw_pts(t)[p-1]) for p in self._getset(model,INC_poly,t))
	def INC_LINEAR_constraint2_rule(model,*t):
	    LHS = self._getvar(model,self.YVAR.name,t)
	    RHS = self._F(model,t,self._pw_pts(t)[0]) + sum(self._getvar(model,delta,t,p)*(self._F(model,t,self._pw_pts(t)[p])-self._F(model,t,self._pw_pts(t)[p-1])) for p in self._getset(model,INC_poly,t))
	    if self.PW_TYPE == 'UB':
		return LHS <= RHS
	    elif self.PW_TYPE == 'LB':
		return LHS >= RHS
	    elif self.PW_TYPE == 'EQ':
		return LHS == RHS
	def INC_LINEAR_constraint3_rule(model,*args):
	    t = args[:-1]
	    p = args[-1]
	    if p != self._getset(model,INC_poly,t).last():
		return self._getvar(model,delta,t,p+1) <= self._getvar(model,y,t,p)
	    else:
		return Constraint.Skip
	def INC_LINEAR_constraint4_rule(model,*args):
	    t = args[:-1]
	    p = args[-1]
	    if p != self._getset(model,INC_poly,t).last():
		return self._getvar(model,y,t,p) <= self._getvar(model,delta,t,p)
	    else:
		return Constraint.Skip
	
	if self._element_mode:
	    self._update_dicts('INC_constraint1',Constraint(rule=INC_LINEAR_constraint1_rule))
	    self._update_dicts('INC_constraint2',Constraint(rule=INC_LINEAR_constraint2_rule))
	    self._update_dicts('INC_constraint3',Constraint(getattr(self._model(),INC_POLYTOPES),rule=INC_LINEAR_constraint3_rule))
	    self._update_dicts('INC_constraint4',Constraint(getattr(self._model(),INC_POLYTOPES),rule=INC_LINEAR_constraint4_rule))
	else:
	    self._update_dicts('INC_constraint1',Constraint(INC_SET,rule=INC_LINEAR_constraint1_rule))
	    self._update_dicts('INC_constraint2',Constraint(INC_SET,rule=INC_LINEAR_constraint2_rule))
	    self._update_dicts('INC_constraint3',Constraint(getattr(self._model(),INC_POLYTOPES),rule=INC_LINEAR_constraint3_rule))
	    self._update_dicts('INC_constraint4',Constraint(getattr(self._model(),INC_POLYTOPES),rule=INC_LINEAR_constraint4_rule))

    
    
    ###### Find tightest possible BIGM values for convex/concave BIG constraints
    def _M_func(self,a,b,c,*args):
	tpl = flatten_tuple((self._model(),)+args)
	return self._F(*(tpl+(a,))) - self._F(*(tpl+(b,))) - ((a-b) * (float(self._F(*(tpl+(c,)))-self._F(*(tpl+(b,)))) / float(c-b)))

    def _find_M(self,PTS,BOUND):
	
	M_final = {}
	if self._element_mode:
	    for j in xrange(1,len(PTS)):
		index = j
		if (BOUND == 'LB'):
		    M_final[index] = min( [0.0, min([self._M_func(PTS[k],PTS[j-1],PTS[j]) for k in xrange(len(PTS))])] )
		elif (BOUND == 'UB'):
		    M_final[index] = max( [0.0, max([self._M_func(PTS[k],PTS[j-1],PTS[j]) for k in xrange(len(PTS))])] )
		if M_final[index] == 0.0:
		    del M_final[index]
	else:
	    for t in PTS.keys():
		for j in xrange(1,len(PTS[t])):
		    index = flatten_tuple((t,j))
		    if (BOUND == 'LB'):
			M_final[index] = min( [0.0, min([self._M_func(PTS[t][k],PTS[t][j-1],PTS[t][j],t) for k in xrange(len(PTS[t]))])] )
		    elif (BOUND == 'UB'):
			M_final[index] = max( [0.0, max([self._M_func(PTS[t][k],PTS[t][j-1],PTS[t][j],t) for k in xrange(len(PTS[t]))])] )
		    if M_final[index] == 0.0:
			del M_final[index]
	return M_final
    ########
