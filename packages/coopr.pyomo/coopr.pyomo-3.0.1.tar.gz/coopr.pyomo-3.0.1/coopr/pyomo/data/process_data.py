#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import re
import copy
import math
import logging

from parse_datacmds import parse_data_commands
from pyutilib.misc import quote_split, Options
from coopr.pyomo.base.plugin import *
from coopr.pyomo.base.plugin import *
import pyutilib.common

logger = logging.getLogger('coopr.pyomo')

global Lineno
global Filename


def _preprocess_data(cmd):
    """
    Called by _process_data() to (1) combine tokens that comprise a tuple
    and (2) combine the ':' token with the previous token
    """
    if __debug__:
        logger.debug("_preprocess_data(start) %s",cmd)
    status=")"
    newcmd=[]
    for token in cmd:
        if type(token) in (str,unicode):
            token=str(token)
            if "(" in token and ")" in token:
                newcmd.append(token)
                status=")"
            elif "(" in token:
                if status == "(":
                    raise ValueError, "Two '('s follow each other in data "+token
                status="("
                newcmd.append(token)
            elif ")" in token:
                if status == ")":
                    raise ValueError, "Two ')'s follow each other in data"
                status=")"
                newcmd[-1] = newcmd[-1]+token
            elif status == "(":
                newcmd[-1] = newcmd[-1]+token
            else:
                newcmd.append(token)
        else:
            if type(token) is float and math.floor(token) == token:
                token=int(token)
            newcmd.append(token)
    if __debug__:
        logger.debug("_preprocess_data(end) %s", newcmd)
    return newcmd


def _process_set(cmd, _model, _data):
    """
    Called by _process_data() to process a set declaration.
    """
    if __debug__:
        logger.debug("DEBUG: _process_set(start) %s",cmd)
    #
    # Process a set
    #
    if "[" in cmd[1]:
        tokens = re.split("[\[\]]",cmd[1])
        ndx=tokens[1]
        ndx=tuple(_data_eval(ndx.split(",")))
        if tokens[0] not in _data:
            _data[tokens[0]] = {}
        _data[tokens[0]][ndx] = _process_set_data(cmd[3:], tokens[0], _model)
    elif cmd[2] == ":":
        _data[cmd[1]] = {}
        _data[cmd[1]][None] = []
        i=3
        while cmd[i] != ":=":
            i += 1
        ndx1 = cmd[3:i]
        i += 1
        while i<len(cmd):
            ndx=cmd[i]
            for j in range(0,len(ndx1)):
                if cmd[i+j+1] == "+":
                    _data[cmd[1]][None] += _process_set_data(["("+str(ndx1[j])+","+str(cmd[i])+")"], cmd[1], _model)
            i += len(ndx1)+1
    else:
        _data[cmd[1]] = {}
        _data[cmd[1]][None] = _process_set_data(cmd[3:], cmd[1], _model)


def _process_set_data(cmd, sname, _model):
    """
    Called by _process_set() to process set data.
    """
    if __debug__:
        logger.debug("DEBUG: _process_set_data(start) %s",cmd)
    if len(cmd) == 0:
        return []
    try:
        sd = getattr(_model,sname)
    except AttributeError:
        raise IOError, "Cannot process data for set '%s' because it is not defined in model '%s'" % (sname, _model.name)
    #d = sd.dimen
    cmd = _data_eval(cmd)
    ans=[]
    i=0
    tmp=None
    ndx=[]
    while i<len(cmd):
        if type(cmd[i]) is not tuple:
            if len(ndx) > 0:
                #if type(cmd[i]) is not tuple:
                #   raise ValueError, "Problem initializing set="+sname+" with input data="+str(cmd)+" - first element was interpreted as a tuple, but element="+str(i)+" is of type="+str(type(cmd[i]))+"; types must be consistent"
                tmpval=tmp
                for kk in range(len(ndx)):
                    if i == len(cmd):
                        raise IOError, "Expected another set value to flush out a tuple pattern!"
                    tmpval[ndx[kk]] = _data_eval([cmd[i]])[0]
                    i += 1
                #
                # WEH - I'm not sure what the next two lines are for
                #        These are called when initializing a set with more than
                #        one dimension
                #if d > 1:
                #   tmpval = util.tuplize(tmpval,d,sname)
                ans.append(tuple(tmpval))
                continue
            else:
                ans.append(cmd[i])
        elif "*" not in cmd[i]:
            ans.append(cmd[i])
        else:
            j = i
            tmp=list(cmd[j])
            ndx=[]
            for kk in range(len(tmp)):
                if tmp[kk] == '*':
                    ndx.append(kk)
            #print 'NDX',ndx
        i += 1
    if __debug__:
        logger.debug("DEBUG: _process_set_data(end) %s",ans)
    return ans


def _process_param(cmd, _model, _data, _default):
    """
    Called by _process_data to process data for a Parameter declaration
    """
    #print 'x',cmd,_data
    if __debug__:
        logger.debug("DEBUG: _process_param(start) %s",cmd)
    #
    # Process parameters
    #
    dflt = None
    singledef = True
    cmd = cmd[1:]
    if cmd[0] == ":":
        singledef = False
        cmd = cmd[1:]
    if singledef:
        pname = cmd[0]
        cmd = cmd[1:]
        if len(cmd) >= 2 and cmd[0] == "default":
            dflt = _data_eval(cmd[1])[0]
            cmd = cmd[2:]
        if dflt != None:
            _default[pname] = dflt
        if cmd[0] == ":=":
            cmd = cmd[1:]
        transpose = False
        if cmd[0] == "(tr)":
            transpose = True
            if cmd[1] == ":":
                cmd = cmd[1:]
            else:
                cmd[0] = ":"
        if cmd[0] != ":":
            if __debug__:
                logger.debug("DEBUG: _process_param (singledef without :...:=) %s",cmd)
            cmd = _apply_templates(cmd)
            #print 'cmd',cmd
            if not transpose:
                if pname not in _data:
                    _data[pname] = {}
                finaldata = _process_data_list(pname, getattr(_model,pname).dim(), _data_eval(cmd))
                for key in finaldata:
                    _data[pname][key]=finaldata[key]
            else:
                tmp = ["param", pname, ":="]
                i=1
                while i < len(cmd):
                    i0 = i
                    while cmd[i] != ":=":
                        i=i+1
                    ncol = i - i0 + 1
                    lcmd = i
                    while lcmd < len(cmd) and cmd[lcmd] != ":":
                        lcmd += 1
                    j0 = i0 - 1
                    for j in range(1,ncol):
                        ii = 1 + i
                        kk = ii + j
                        while kk < lcmd:
                            if cmd[kk] != ".":
                            #if 1>0:
                                tmp.append(copy.copy(cmd[j+j0]))
                                tmp.append(copy.copy(cmd[ii]))
                                tmp.append(copy.copy(cmd[kk]))
                            ii = ii + ncol
                            kk = kk + ncol
                    i = lcmd + 1
                _process_param(tmp, _model, _data, _default)
        else:
            tmp = ["param", pname, ":="]
            i=1
            if __debug__:
                logger.debug("DEBUG: _process_param (singledef with :...:=) %s",cmd)
            while i < len(cmd):
                i0 = i
                while i<len(cmd) and cmd[i] != ":=":
                    i=i+1
                if i==len(cmd):
                    raise ValueError, "ERROR: Trouble on line "+str(Lineno)+" of file "+Filename
                ncol = i - i0 + 1
                lcmd = i
                while lcmd < len(cmd) and cmd[lcmd] != ":":
                    lcmd += 1
                j0 = i0 - 1
                for j in range(1,ncol):
                    ii = 1 + i
                    kk = ii + j
                    while kk < lcmd:
                        if cmd[kk] != ".":
                            if transpose:
                                tmp.append(copy.copy(cmd[j+j0]))
                                tmp.append(copy.copy(cmd[ii]))
                            else:
                                tmp.append(copy.copy(cmd[ii]))
                                tmp.append(copy.copy(cmd[j+j0]))
                            tmp.append(copy.copy(cmd[kk]))
                        ii = ii + ncol
                        kk = kk + ncol
                i = lcmd + 1
                _process_param(tmp, _model, _data, _default)

    else:
        if __debug__:
            logger.debug("DEBUG: _process_param (cmd[0]=='param:') %s",cmd)
        i=0
        nsets=0
        while i<len(cmd) and cmd[i] != ":=":
            if cmd[i] == ":":
                nsets = i
            i += 1
        if i==len(cmd):
            raise ValueError, "Trouble on data file line "+str(Lineno)+" of file "+Filename
        if __debug__:
            logger.debug("NSets %d",nsets)
        Lcmd = len(cmd)
        j=0
        d = 1
        #
        # Process sets first
        #
        while j<nsets:
            sname = cmd[j]
            d = getattr(_model,sname).dimen
            np = i-1
            if __debug__:
                logger.debug("I %d, J %d, SName %s, d %d",i,j,sname,d)
            dnp = d + np - 1
            #k0 = i + d - 2
            ii = i + j + 1
            tmp = [ "set", cmd[j], ":=" ]
            while ii < Lcmd:
                for dd in range(0,d):
                    tmp.append(copy.copy(cmd[ii+dd]))
                ii += dnp
            _process_set(tmp, _model, _data)
            j += 1
        if nsets > 0:
            j += 1
        #
        # Process parameters second
        #
        #print "JI",j,i # XXX
        while j < i:
            pname = cmd[j]
            if __debug__:
                logger.debug("I %d, J %d, Pname %s",i,j,pname)
            #d = 1
            d = getattr(_model,pname).dim()
            if nsets > 0:
                np = i-1
                dnp = d+np-1
                ii = i + 1
                kk = i + d + j-1
            else:
                np = i
                dnp = d + np
                ii = i + 1
                kk = np + 1 + d + nsets + j
            tmp = [ "param", pname, ":=" ]
            if __debug__:
                logger.debug('dnp %d\nnp %d', dnp, np)
            while kk < Lcmd:
                if __debug__:
                    logger.debug("kk %d, ii %d",kk,ii)
                iid = ii + d
                while ii < iid:
                    tmp.append(copy.copy(cmd[ii]))
                    ii += 1
                ii += dnp-d
                tmp.append(copy.copy(cmd[kk]))
                kk += dnp
            _process_param(tmp, _model, _data, _default)
            j += 1


def _apply_templates(cmd):
    cmd = _data_eval(cmd)
    template = []
    ilist = set()
    ans = []
    i = 0
    while i < len(cmd):
    #print i, len(cmd), cmd[i], ilist, template, ans
        if type(cmd[i]) is tuple and '*' in cmd[i]:
            j = i
            tmp=list(cmd[j])
            nindex = len(tmp)
            template=tmp
            ilist = set()
            for kk in range(len(tmp)):
                if tmp[kk] == '*':
                    ilist.add(kk)
        elif len(ilist) == 0:
            ans.append(cmd[i])
        else:
            for kk in range(len(template)):
                if kk in ilist:
                    ans.append(cmd[i])
                    i += 1
                else:
                    ans.append(template[kk])
            ans.append(cmd[i])
        i += 1
    return ans


def _process_data_list(param_name, dim, cmd):
    """\
 Called by _process_param() to process a list of data for a Parameter.
 """
    if __debug__:
        logger.debug("process_data_list %d %s",dim,cmd)

    if len(cmd) % (dim+1) != 0:
        msg = "Parameter '%s' defined with '%d' dimensions, " \
              "but data has '%d' values: %s."
        msg = msg % (param_name, dim, len(cmd), cmd)
        if len(cmd) % (dim+1) == dim:
            msg += " Are you missing a value for a %d-dimensional index?" % dim
        elif len(cmd) % dim == 0:
            msg += " Are you missing the values for %d-dimensional indices?" % dim
        else:
            msg += " Data declaration must be given in multiples of %d." % (dim + 1)
        raise ValueError, msg

    ans={}
    if dim==0:
        ans[None]=cmd[0]
        return ans
    i=0
    while i < len(cmd):
        ndx = tuple(cmd[i:i+dim])
        if cmd[i+dim] != ".":
            ans[ndx] = cmd[i+dim]
        i += dim+1
    return ans



def _data_eval(values):
    """
    Evaluate the list of values to make them bool, integer or float,
    or a tuple value.
    """
    if __debug__:
        logger.debug("DEBUG: _data_eval(start) %s",values)
    ans = []
    for val in values:
        if type(val) in (bool,int,float,long):
            ans.append(val)
            continue
        if val in ('True','true','TRUE'):
            ans.append(True)
            continue
        if val in ('False','false','FALSE'):
            ans.append(False)
            continue
        tmp = None
        tval = val.strip()
        if (tval[0] == "(" and tval[-1] == ")") or (tval[0] == '[' and tval[-1] == ']'):
            vals = []
            tval = tval[1:-1]
            for item in tval.split(","):
                tmp=_data_eval([item])
                vals.append(tmp[0])
            ans.append(tuple(vals))
            continue
        try:
            tmp = int(val)
            ans.append(tmp)
        except ValueError:
            pass
        if tmp is None:
            try:
                tmp = float(val)
                ans.append(tmp)
            except ValueError:
                if val[0] == "'" or val[0] == '"':
                    ans.append(val[1:-1])
                else:
                    ans.append(val)
    if __debug__:
        logger.debug("DEBUG: _data_eval(end) %s",ans)
    return ans


def _process_include(cmd, _model, _data, _default):
    if len(cmd) == 1:
        raise IOError, "Cannot execute 'include' command without a filename"
    if len(cmd) > 2:
        raise IOError, "The 'include' command only accepts a single filename"

    global Filename
    Filename = cmd[1]
    global Lineno
    Lineno = 0

    try:
        scenarios = parse_data_commands(filename=cmd[1])
    except IOError, err:
        raise IOError, "Error parsing file '%s': %s" % (Filename, str(err))
    if scenarios is None:
        return False
    for scenario in scenarios:
        for cmd in scenarios[scenario]:
            #print "SCENARIO",scenario,"CMD",cmd
            if scenario not in _data:
                _data[scenario] = {}
            #print "X _data",_data
            if cmd[0] in ('include', 'import'):
                _tmpdata = {}
                _process_data(cmd, _model, _tmpdata, _default, Filename, Lineno)
                #print "X _tmpdata",_tmpdata
                if scenario is None:
                    for key in _tmpdata:
                        if key in _data:
                            _data[key].update(_tmpdata[key])
                        else:
                            _data[key] = _tmpdata[key]
                else:
                    for key in _tmpdata:
                        if key is None:
                            _data[scenario].update(_tmpdata[key])
                        else:
                            raise IOError, "Cannot define a scenario within another scenario"
            else:
                _process_data(cmd, _model, _data[scenario], _default, Filename, Lineno)
            #print "X _data update",_data
    return True


def X_process_include(cmd, _model, _data, _default):
    if len(cmd) == 1:
        raise IOError, "Cannot execute 'include' command without a filename"
    if len(cmd) > 2:
        raise IOError, "The 'include' command only accepts a single filename"

    global Filename
    Filename = cmd[1]
    global Lineno
    Lineno = 0
    cmd=""
    status=True
    INPUT=open(Filename,'r')
    for line in INPUT:
        Lineno = Lineno + 1
        line = re.sub(":"," :",line)
        line = line.strip()
        if line == "" or line[0] == '#':
            continue
        cmd = cmd + " " + line
        if ';' in cmd:
            #
            # We assume that a ';' indicates an end-of-command declaration.
            # However, the user might have put multiple commands on a single
            # line, so we need to split the line based on these values.
            # BUT, at the end of the line we should see an 'empty' command,
            # which we ignore.
            #
            for item in cmd.split(';'):
                item = item.strip()
                if item != "":
                    _process_data(quote_split("[\t ]+",item), _model, _data, _default, Filename, Lineno)
                cmd = ""
    if cmd != "":
        INPUT.close()
        raise IOError, "ERROR: There was unprocessed text at the end of the data file!: \"" + cmd + "\""
    INPUT.close()
    return status


def _process_import(cmd, _model, _data, _default):
    #print "IMPORT",cmd
    if len(cmd) < 2:
        raise IOError, "The 'import' command must specify a filename"

    options = Options(**cmd[1])
    for key in options:
        if not key in ['range','filename','format','using','driver','query','table','user','password']:
            raise ValueError, "Unknown import option '%s'" % key

    global Filename
    Filename = cmd[1]
    global Lineno
    Lineno = 0

    #
    # TODO: process mapping info
    #
    if options.using is None:
        tmp = options.filename.split(".")[-1]
        data = DataManagerFactory(tmp)
        if data is None:
            raise pyutilib.common.ApplicationError, "Cannot create data manager '%s'" % tmp
    else:
        data = DataManagerFactory(options.using)
        if data is None:
            raise pyutilib.common.ApplicationError, "Cannot create data manager '%s'" % options.using
    set_name=None
    param_name=None
    #
    # Create symbol map
    #
    symb_map = cmd[3]
    if len(symb_map) == 0:
        raise IOError, "Must specify at least one set or parameter name that will be imported"
    #
    # Process index data
    #
    index=cmd[2][1]
    index_name=cmd[2][0]
    #
    # Set the 'set name' based on the format
    #
    if options.format == 'set' or options.format == 'set_array':
        if len(cmd[3]) != 1:
            raise IOError, "A single set name must be specified when using format '%s'" % options.format
        set_name=cmd[3].keys()[0]
    else:
        set_name=None
    #
    # Set the 'param name' based on the format
    #
    if options.format == 'transposed_array' or options.format == 'array' or options.format == 'param':
        if len(cmd[3]) != 1:
            raise IOError, "A single parameter name must be specified when using format '%s'" % options.format
        param_name = cmd[3].keys()[0]
    else:
        param_name = None
    #
    data.initialize(options.filename, index=index, index_name=index_name, param_name=symb_map, set=set_name, param=param_name, format=options.format, range=options.range, query=options.query, using=options.using, table=options.table)
    #
    data.open()
    try:
        data.read()
    except Exception, e:
        data.close()
        raise e
    data.close()
    data.process(_model, _data, _default)


def _process_data(cmd, _model, _data, _default, Filename_, Lineno_=0):
    """
    Called by import_file() to (1) preprocess data and (2) call
    subroutines to process different types of data
    """
    #print "CMD",cmd
    global Lineno
    global Filename
    Lineno=Lineno_
    Filename=Filename_

    if __debug__:
        logger.debug("DEBUG: _process_data (start) %s",cmd)
    if len(cmd) == 0:                       #pragma:nocover
        raise ValueError, "ERROR: Empty list passed to Model::_process_data"

    cmd = _preprocess_data(cmd)

    if cmd[0] == "data":
        return True
    if cmd[0] == "end":
        return False
    if cmd[0].startswith('set'):
        _process_set(cmd, _model, _data)
    elif cmd[0].startswith('param'):
        _process_param(cmd, _model, _data, _default)
    elif cmd[0] == 'include':
        _process_include(cmd, _model, _data, _default)
    elif cmd[0] == 'import':
        _process_import(cmd, _model, _data, _default)
    else:
        raise IOError, "ERROR: Unknown data command: "+" ".join(cmd)
    return True
