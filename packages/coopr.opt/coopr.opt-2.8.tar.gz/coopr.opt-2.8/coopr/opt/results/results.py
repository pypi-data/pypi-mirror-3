#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['SolverResults']

import math
import sys
from container import *
from pyutilib.enum import Enum
from pyutilib.misc import Bunch
import copy

import StringIO

import problem
import solver
import solution

import json
try:
    import yaml
    yaml_available=True
except ImportError:
    yaml_available=False


class SolverResults(MapContainer):

    undefined = undefined
    default_print_options = solution.default_print_options

    # XXX begin debugging
    def __del__(self):
        MapContainer.__del__(self)
        #print("Called __del__ on SolverResults")
        self._sections = None
        self._descriptions = None
        self._symbol_map = None
    # XXX end debugging

    def __init__(self):
        MapContainer.__init__(self)
        self._sections = []
        self._symbol_map = None
        self._descriptions = {}
        self.add('problem', ListContainer(problem.ProblemInformation), False, "Problem Information")
        self.add('solver', ListContainer(solver.SolverInformation), False, "Solver Information")
        self.add('solution', solution.SolutionSet(), False, "Solution Information")

    def __getstate__(self):
        def _canonical_label(obj):
            if obj is obj.component():
                label = obj.name
            else:
                index = obj.index
                if type(index) is not tuple:
                    index = (index,)
                codedIdx = []
                for idx in index:
                    if idx is None:
                        codedIdx.append('!')
                    elif type(idx) is str:
                        codedIdx.append('$'+idx)
                    elif int(idx) == idx:
                        codedIdx.append('#'+str(idx))
                    else:
                        raise ValueError(
                            "Unexpected type %s encountered when pickling "
                            "SolverResults object index: %s" %
                            (str(type(idx)), str(obj.index)))
                obj = obj.component()
                label = obj.name + ':' + ','.join(codedIdx)
            if obj._parent is None or obj._parent() is None:
                return label
            obj = obj._parent()
            while obj._parent is not None and obj._parent() is not None:
                label = str(obj.name) + '.' + label
                obj = obj._parent()
            return label
            
        sMap = self._symbol_map
        if sMap is None:
            return MapContainer.__getstate__(self)
        for soln in self.solution:
            for symbol, obj in soln.objective.iteritems():
                obj.canonical_label = _canonical_label(sMap.getObject(symbol))
            for symbol, var in soln.variable.iteritems():
                if symbol == 'ONE_VAR_CONSTANT':
                    continue
                var['canonical_label'] = _canonical_label(sMap.getObject(symbol))
            for symbol, con in soln.constraint.iteritems():
                con.canonical_label = _canonical_label(sMap.getObject(symbol))
        results = MapContainer.__getstate__(self)
        results['_symbol_map'] = None
        return results

    def add(self, name, value, active, description):
        self.declare(name, value=value, active=active)
        tmp = self._convert(name)
        self._sections.append(tmp)
        self._descriptions[tmp]=description

    def json_repn(self, options=None):
        if options is None:
            return self._repn_(SolverResults.default_print_options)
        else:
            return self._repn_(options)

    def _repn_(self, option):
        if not option.schema and not self._active and not self._required:
            return ignore
        tmp = {}
        for key in self._sections:
            rep = dict.__getitem__(self, key)._repn_(option)
            if not rep == ignore:
                tmp[key] = rep
        return tmp

    def write(self, **kwds):
        if 'filename' in kwds:
            OUTPUT=open(kwds['filename'],"w")
            del kwds['filename']
            kwds['ostream']=OUTPUT
            self.write(**kwds)
            OUTPUT.close()
            return

        if not 'format' in kwds or kwds['format'] == 'yaml':
            self.write_yaml(**kwds)
            return
        #
        # Else, write in JSON format
        #
        repn = self.json_repn()
        if 'ostream' in kwds:
            ostream = kwds['ostream']
            del kwds['ostream']
        else:
            ostream = sys.stdout
        for soln in repn.get('Solution', []):
            for data in ['Variable', 'Constraint', 'Objective']:
                remove = set()
                data_value = soln.get(data,{})
                if not isinstance(data_value,dict):
                    continue
                for kk,vv in soln.get(data,{}).iteritems():
                    tmp = {}
                    for k,v in vv.iteritems():
                        if k == 'Id' or (k != 'Id' and math.fabs(v) != 0.0):
                            tmp[k] = v
                    if len(tmp) > 1 or (len(tmp) == 1 and not 'Id' in tmp):
                        soln[data][kk] = tmp
                    else:
                        remove.add((data,kk))
                for item in remove:
                    del soln[item[0]][item[1]]
        json.dump(repn, ostream, indent=4, sort_keys=True)

    def write_yaml(self, **kwds):
        if 'ostream' in kwds:
            ostream = kwds['ostream']
            del kwds['ostream']
        else:
            ostream = sys.stdout

        option = copy.copy(SolverResults.default_print_options)
        for key in kwds:
            setattr(option,key,kwds[key])

        repn = self._repn_(option)
        print >>ostream, "# =========================================================="
        print >>ostream, "# = Solver Results                                         ="
        print >>ostream, "# =========================================================="
        for i in xrange(len(self._order)):
            key = self._order[i]
            if not key in repn:
                continue
            item = dict.__getitem__(self,key)
            print >>ostream, ""
            print >>ostream, "# ----------------------------------------------------------"
            print >>ostream, "#   %s" % self._descriptions[key]
            print >>ostream, "# ----------------------------------------------------------"
            print >>ostream, key+":",
            if isinstance(item, ListContainer):
                item.pprint(ostream, option, prefix="", repn=repn[key])
            else:
                item.pprint(ostream, option, prefix="  ", repn=repn[key])

    def read(self, **kwds):
        if 'istream' in kwds:
            istream = kwds['istream']
            del kwds['istream']
        else:
            ostream = sys.stdin
        if 'filename' in kwds:
            INPUT=open(kwds['filename'],"r")
            del kwds['filename']
            kwds['istream']=INPUT
            self.read(**kwds)
            INPUT.close()
            return

        if not 'format' in kwds or kwds['format'] == 'yaml':
            if not yaml_available:
                raise IOError, "Aborting SolverResults.read() because PyYAML is not installed!"
            repn = yaml.load(istream, Loader=yaml.SafeLoader)
        else:
            repn = json.load(istream)
        for i in xrange(len(self._order)):
            key = self._order[i]
            if not key in repn:
                continue
            item = dict.__getitem__(self,key)
            item.load(repn[key])

    def __repr__(self):
        return str(self._repn_(SolverResults.default_print_options))

    def __str__(self):
        ostream = StringIO.StringIO()
        option=SolverResults.default_print_options
        self.pprint(ostream, option, repn=self._repn_(option))
        return ostream.getvalue()


if __name__ == '__main__':
    results = SolverResults()
    results.write(schema=True)
    #print results
