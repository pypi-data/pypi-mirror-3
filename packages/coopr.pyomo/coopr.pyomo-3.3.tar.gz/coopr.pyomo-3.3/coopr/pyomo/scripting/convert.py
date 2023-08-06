#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['pyomo2lp', 'pyomo2nl', 'pyomo2osil']


import argparse
from coopr.opt import ProblemFormat
from coopr.opt.base import SolverFactory
from pyutilib.misc import Options, Container

import util
import pyomo

def create_parser(cmd):
    #
    #
    # Setup command-line options
    #
    #
    parser = argparse.ArgumentParser(
                usage = '%s [options] <model_file> [<data_files>]' % cmd
                )
    pyomo.add_model_group(parser)
    pyomo.add_logging_group(parser)
    pyomo.add_misc_group(parser)
    parser.add_argument('model_file', action='store', nargs='?', default='', help='A Python module that defines a Pyomo model')
    parser.add_argument('data_files', action='store', nargs='*', default=[], help='Pyomo data files that defined data used to create a model instance')
    return parser

format = None

def convert(options=Options(), parser=None):
    global format
    if options.save_model is None:
        if format == ProblemFormat.cpxlp:
            options.save_model = 'unknown.lp'
        else:
            options.save_model = 'unknown.'+str(format)
    options.format = format
    #
    data = Options(options=options)
    #
    if options.help_components:
        util.print_components(data)
        return Container()
    #
    util.setup_environment(data)
    #
    util.apply_preprocessing(data, parser=parser)
    if data.error:
        return Container()
    #
    model_data = util.create_model(data)
    #
    util.finalize(data, model=model_data.model)
    #
    model_data.options = options
    return model_data

def pyomo2lp(args=None):
    global format
    parser = create_parser('pyomo2lp')
    format = ProblemFormat.cpxlp
    return util.run_command(command=convert, parser=parser, args=args, name='pyomo2lp').retval

def pyomo2lp_main(args=None):
    ans = pyomo2lp(args)
    if ans is None:
        return 0
    return 1

def pyomo2nl(args=None):
    global format
    parser = create_parser('pyomo2nl')
    format = ProblemFormat.nl
    return util.run_command(command=convert, parser=parser, args=args, name='pyomo2nl').retval

def pyomo2nl_main(args=None):
    ans = pyomo2nl(args)
    if ans is None:
        return 0
    return 1

def pyomo2osil(args=None):
    global format
    parser = create_parser('pyomo2osil')
    format = ProblemFormat.osil
    return util.run_command(command=convert, parser=parser, args=args, name='pyomo2osil').retval

def pyomo2osil_main(args=None):
    ans = pyomo2osil(args)
    if ans is None:
        return 0
    return 1

