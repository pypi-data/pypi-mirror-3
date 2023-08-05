#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from pyutilib.enum import Enum
import pyutilib.component.core
from plugin import *

def predefined_sets():
    import set_types
    ans = []
    for item in set_types._virtual_sets:
        ans.append( (item.name,item.doc) )
    return ans


def model_components():
    return [(name,ModelComponentFactory.doc(name)) for name in ModelComponentFactory.services()]
