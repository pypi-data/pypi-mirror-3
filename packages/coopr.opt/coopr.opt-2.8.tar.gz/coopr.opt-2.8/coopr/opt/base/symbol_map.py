#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [ 'SymbolMap', 'symbol_map_from_instance' ]

# 
# an experimental utility method to create a symbol map from an instance. really will 
# only work if name-based labelers are used, but that's good enough for now. also 
# won't work with blocks. 
#

def symbol_map_from_instance(instance):

   from coopr.pyomo.base import Var, label_from_name, Constraint, Objective
   from coopr.pyomo.io.cpxlp import CPXLP_text_labeler

   resulting_map = SymbolMap(instance)

   labeler = CPXLP_text_labeler()

   for block in instance.all_blocks():
      for variable in block.active_components(Var).itervalues():
         for varvalue in variable.itervalues():
            # ignore the return value - we're just trying to populate the map.
            symbol = resulting_map.getSymbol(varvalue, labeler)

   for block in instance.all_blocks():
       active_constraints = block.active_components(Constraint)
       for constraint in active_constraints.itervalues():
           for constraint_data in constraint.itervalues():
               con_symbol = resulting_map.getSymbol( constraint_data, labeler )               
               if constraint_data._equality:               
                   label = 'c_e_' + con_symbol + '_'
                   resulting_map.alias(constraint_data, label)
               else:
                   if constraint_data.lower is not None:
                       label = 'c_l_' + con_symbol + '_'
                       resulting_map.alias(constraint_data, label)
                   if constraint_data.upper is not None:
                       label = 'c_u_' + con_symbol + '_'
                       resulting_map.alias(constraint_data, label)

   for objective in instance.active_components(Objective).itervalues():
      for objective_data in objective.itervalues():
         # ignore the return value - we're just trying to populate the map.
         resulting_map.getSymbol(objective_data, labeler)      
         resulting_map.alias(objective_data, "__default_objective__")

   return resulting_map

#
# a symbol map is a mechanism for tracking assigned labels (e.g., for use when writing 
# problem files for input to an optimizer) for objects in a particular problem instance.
#

class SymbolMap(object):

    class UnknownSymbol:
        pass

    def __init__(self, instance):

        # conceptually, a symbol map must be associated with an instance - for example,
        # the byObject map creates associations between object ids and their symbols
        # => the ids are tied to a specific instance. however, we don't actually do
        # anything with the instance within this class quite yet.
        self.instance = instance
        
        # maps object id()s to their assigned symbol.
        self.byObject = {}

        # maps assigned symbols to the corresponding objects.
        self.bySymbol = {}

        self.aliases = {}

    # 
    # it is often useful to extract the by-object dictionary
    # to directly access it, principally to avoid the overhead
    # associated with function calls and error checking - in
    # cases where you know an object will be in the dictionary.
    # this method is useful in cases such as the problem
    # writers, in which a single pass is performed through all
    # objects in the model to populate the symbol map - it 
    # is read-only after that point.
    #
    def getByObjectDictionary(self):
        return self.byObject
 

    #
    # invoked when the caller guarantees that a name conflict will not arise. use with care!
    #
    def createSymbol(self, obj, labeler, *args):

        # the following test is slightly faster than always calling *args.
        if args:
           ans = labeler(obj, *args)
        else:
           ans = labeler(obj)
        self.byObject[id(obj)] = ans
        self.bySymbol[ans] = obj
        return ans
  
    #
    # same as above, but with full error checking for duplicates / collisions.
    #
    def getSymbol(self, obj, labeler, *args):

        obj_id = id(obj)
        if obj_id in self.byObject:
           return self.byObject[obj_id]

        # the following test is slightly faster than always calling *args
        if args:
           ans = labeler(obj, *args)
        else:
           ans = labeler(obj)
           
        if self.bySymbol.setdefault(ans, obj) is not obj:
           raise RuntimeError(
              "Duplicate symbol '%s' already associated with "
              "component '%s' (conflicting component: '%s')"
              % (ans, self.bySymbol[ans].name, obj.name) )
        self.byObject[obj_id] = ans
        return ans

    def alias(self, obj, name):

        #if id(obj) not in self.byObject:
        #    raise RuntimeError(
        #        "Cannot alias object '%s': object not in SymbolMap."
        #        % ( name, ))
        if self.aliases.setdefault(name, obj) is not obj:
            raise RuntimeError(
                "Duplicate alias '%s' already associated with "
                "component '%s' (conflicting component: '%s')"
                % (name, self.aliases[name].name, obj.name) )

    def getObject(self, symbol):

        ans = self.bySymbol.get(symbol, SymbolMap.UnknownSymbol)
        if ans is SymbolMap.UnknownSymbol:
            ans = self.aliases.get(symbol, SymbolMap.UnknownSymbol)
        return ans
            
    def getEquivalentObject(self, symbol, instance):

        obj = self.bySymbol.get(symbol, SymbolMap.UnknownSymbol)
        if obj is SymbolMap.UnknownSymbol:
            obj = self.aliases.get(symbol, SymbolMap.UnknownSymbol)
            if obj is SymbolMap.UnknownSymbol:
                return SymbolMap.UnknownSymbol
            
        # FIXME: This is still a hack that needs to be fixed for constraints
        # Actually, it works for constraints, objectives, and vars, but
        # not for other indexable objects.  I am not sure if that is a
        # problem, though,
        if 'parent' in obj.__dict__:
            idx = None
        else:
            idx = obj.index
            obj = obj.component()
        path = []
        while obj is not None:
            path.append(obj)
            obj = obj.parent
        path.pop() # skip the model itself
        obj = instance
        while path:
            try:
                obj = getattr(obj, path.pop().name)
            except AttributeError:
                return SymbolMap.UnknownSymbol
        if idx is not None:
            obj = obj[idx]
        return obj
                
        
        

        
