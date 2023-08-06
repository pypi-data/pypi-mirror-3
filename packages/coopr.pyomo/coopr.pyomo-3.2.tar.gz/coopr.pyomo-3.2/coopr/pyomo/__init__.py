#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

from sys import stderr as SE

import pyutilib.component.core


pyutilib.component.core.PluginGlobals.push_env( 'coopr.pyomo' )

from base import *
import base.pyomo as pyomo
from expr import *
import data
from io import *
from components import *
import preprocess
import coopr.opt
import transform
import scripting
import check

pyutilib.component.core.PluginGlobals.pop_env()

try:
    import pkg_resources
    #
    # Load modules associated with Plugins that are defined in
    # EGG files.
    #
    for entrypoint in pkg_resources.iter_entry_points('coopr.pyomo'):
        try:
            plugin_class = entrypoint.load()
        except Exception, err:
            SE.write( "Error loading coopr.pyomo entry point: %s  entrypoint='%s'\n" % (err, entrypoint) )
except Exception, err:
    SE.write( "Error loading coopr.pyomo entry points\n" )

