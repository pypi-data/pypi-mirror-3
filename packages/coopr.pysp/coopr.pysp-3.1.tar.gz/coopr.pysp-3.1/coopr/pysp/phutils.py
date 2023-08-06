#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

import string
import traceback
import os

from coopr.pyomo import *

from coopr.pyomo.expr.linear_repn import linearize_model_expressions

# for PYRO
try:
    import Pyro.core
    import Pyro.naming
    pyro_available = True
except:
    pyro_available = False

#
# a utility to scan through a scenario tree and set the variable values to None 
# for each variable not in the final stage that has not converged. necessary
# to avoid an illegal / infeasible warm-start for the extensive form solve.
#

def reset_nonconverged_variables(scenario_tree, scenario_instances):

   for stage in scenario_tree._stages[:-1]:

      for tree_node in stage._tree_nodes:
  
         for variable_name, indices in tree_node._variable_indices.iteritems():

            for index in indices:

               min_var_value = value(tree_node._minimums[variable_name][index])
               max_var_value = value(tree_node._maximums[variable_name][index])

               # TBD: THIS IS A HACK - GET THE THRESHOLD FROM SOMEWHERE AS AN INPUT ARGUMENT
               if (max_var_value - min_var_value) > 0.00001:

                  for scenario in tree_node._scenarios:

                     scenario_instance = scenario_instances[scenario._name]
                     getattr(scenario_instance, variable_name)[index].value = None

#
# a utility to clear all cost variables - these are easily derived by the solvers,
# and can/will lead to infeasibilities unless everything is perfectly blended.
# in which case, you don't need to write the EF.
#

def reset_stage_cost_variables(scenario_tree, scenario_instances):

   for scenario_name, scenario_instance in scenario_instances.iteritems():

       for stage in scenario_tree._stages:

          getattr(scenario_instance, stage._cost_variable[0].name)[stage._cost_variable[1]].value = None

#
# a utility to clear the value of any PHQUADPENALTY* variables in the instance. these are
# associated with linearization, and if they are not cleared, can interfere with warm-starting
# due to infeasibilities.
#

def reset_linearization_variables(instance):

    for variable_name, variable in instance.active_components(Var).iteritems():
        if variable_name.startswith("PHQUADPENALTY"):
            for var_value in variable.itervalues():
                var_value.value = None    

#
# a utility for shutting down Pyro-related components, which at the
# moment is restricted to the name server and any dispatchers. the
# mip servers will come down once their dispatcher is shut down.
# NOTE: this is a utility that should eventually become part of
#       pyutilib.pyro, but because is prototype, I'm keeping it
#       here for now.
#

def shutDownPyroComponents():
    if not pyro_available:
        return

    Pyro.core.initServer()
    try:
        ns = Pyro.naming.NameServerLocator().getNS()
    except:
        print "***WARNING - Could not locate name server - Pyro PySP components will not be shut down"
        return
    ns_entries = ns.flatlist()
    for (name,uri) in ns_entries:
        if name == ":Pyro.NameServer":
            proxy = Pyro.core.getProxyForURI(uri)
            proxy._shutdown()
        elif name == ":PyUtilibServer.dispatcher":
            proxy = Pyro.core.getProxyForURI(uri)
            proxy.shutdown()

#
# a simple utility function to pretty-print an index tuple into a [x,y] form string.
#

def indexToString(index):

    # if the input type is a string or an int, then this isn't a tuple!
    if isinstance(index, (str, int)):
        return "["+str(index)+"]"

    result = "["
    for i in range(0,len(index)):
        result += str(index[i])
        if i != len(index) - 1:
            result += ","
    result += "]"
    return result

#
# a simple utility to determine if a variable name contains an index specification.
# in other words, is the reference to a complete variable (e.g., "foo") - which may
# or may not be indexed - or a specific index or set of indices (e.g., "foo[1]" or
# or "foo[1,*]".
#

def isVariableNameIndexed(variable_name):

    left_bracket_count = variable_name.count('[')
    right_bracket_count = variable_name.count(']')

    if (left_bracket_count == 1) and (right_bracket_count == 1):
        return True
    elif (left_bracket_count == 1) or (right_bracket_count == 1):
        raise ValueError, "Illegally formed variable name="+variable_name+"; if indexed, variable names must contain matching left and right brackets"
    else:
        return False

#
# takes a string indexed of the form "('foo', 'bar')" and returns a proper tuple ('foo','bar')
#

def tupleizeIndexString(index_string):

    index_string=index_string.lstrip('(')
    index_string=index_string.rstrip(')')
    pieces = index_string.split(',')
    return_index = ()
    for piece in pieces:
        piece = string.strip(piece)
        piece = piece.lstrip('\'')
        piece = piece.rstrip('\'')
        transformed_component = None
        try:
            transformed_component = int(piece)
        except ValueError:
            transformed_component = piece
        return_index = return_index + (transformed_component,)

    # IMPT: if the tuple is a singleton, return the element itself.
    if len(return_index) == 1:
        return return_index[0]
    else:
        return return_index

#
# related to above, extract the index from the variable name.
# will throw an exception if the variable name isn't indexed.
# the returned variable name is a string, while the returned
# index is a tuple. integer values are converted to integers
# if the conversion works!
#

def extractVariableNameAndIndex(variable_name):

    if isVariableNameIndexed(variable_name) is False:
        raise ValueError, "Non-indexed variable name passed to function extractVariableNameAndIndex()"

    pieces = variable_name.split('[')
    name = string.strip(pieces[0])
    full_index = pieces[1].rstrip(']')

    # even nested tuples in pyomo are "flattened" into
    # one-dimensional tuples. to accomplish flattening
    # replace all parens in the string with commas and
    # proceed with the split.
    full_index=string.translate(full_index, string.maketrans("",""), "()")
    indices = full_index.split(',')

    return_index = ()

    for index in indices:

        # unlikely, but strip white-space from the string.
        index=string.strip(index)

        # if the tuple contains nested tuples, then the nested
        # tuples have single quotes - "'" characters - around
        # strings. remove these, as otherwise you have an
        # illegal index.
        index=string.translate(index, string.maketrans("",""), "\'")

        # if the index is an integer, make it one!
        transformed_index = None
        try:
            transformed_index = int(index)
        except ValueError:
            transformed_index = index
        return_index = return_index + (transformed_index,)

    # IMPT: if the tuple is a singleton, return the element itself.
    if len(return_index) == 1:
        return name, return_index[0]
    else:
        return name, return_index

#
# determine if the input index is an instance of the template,
# which may or may not contain wildcards.
#

def indexMatchesTemplate(index, index_template):

    # if the input index is not a tuple, make it one.
    # ditto with the index template. one-dimensional
    # indices in pyomo are not tuples, but anything
    # else is.

    if type(index) != tuple:
        index = (index,)
    if type(index_template) != tuple:
        index_template = (index_template,)

    if len(index) != len(index_template):
        return False

    for i in xrange(0,len(index_template)):
        if index_template[i] == '*':
            # anything matches
            pass
        else:
            if index_template[i] != index[i]:
                return False

    return True

#
# given a variable (the real object, not the name) and an index,
# "shotgun" the index and see which variable indices match the
# input index. the cardinality could be > 1 if slices are
# specified, e.g., [*,1].
# 
# NOTE: This logic can be expensive for scenario trees with many
#       nodes, and for variables with many indices. thus, the 
#       logic behind the indexMatchesTemplate utility above
#       is in-lined in an efficient way here.
#

def extractVariableIndices(variable, index_template):

    result = []

    variable_index_dimension = variable.dim()

    # do special handling for the case where the variable is
    # not indexed, i.e., of dimension 0. for singleton variables,
    # the mactch template can be the empty string, or - more
    # commonly, given that the empty string is hard to specify
    # in the scenario tree input data - a single wildcard character.
    if variable_index_dimension == 0:
       if (index_template != '') and (index_template != "*"):
          raise RuntimeError, "Index template="+index_template+" specified for singleton variable="+variable.name

       result.append(None)
       return result

    # from this point on, we're dealing with indexed variables.
       
    # if the input index template is not a tuple, make it one.
    # one-dimensional indices in pyomo are not tuples, but 
    # everything else is.
    if type(index_template) != tuple:
       index_template = (index_template,)

    if variable_index_dimension != len(index_template):
        raise RuntimeError, "Dimension="+str(len(index_template))+" of index template="+str(index_template)+" does match the dimension="+str(variable_index_dimension)+" of variable="+variable.name
        return False

    # cache for efficiency
    iterator_range = range(0, variable_index_dimension)

    for index in variable:

        # if the input index is not a tuple, make it one for processing
        # purposes. however, return the original index always.
        if variable_index_dimension == 1:
           modified_index = (index,)
        else:
           modified_index = index

        match_found = True # until proven otherwise
        for i in iterator_range:
           if index_template[i] == '*':
               # anything matches
               pass
           else:
               if index_template[i] != modified_index[i]:
                   match_found = False
                   break

        if match_found is True:
            result.append(index)

    return result

#
# method to eliminate constraints from an input instance.
#
def cull_constraints_from_instance(model):

    active_constraints = model.active_components(Constraint)
    for constraint_name, constraint in active_constraints.iteritems():
        # the model/block do not currently have a delattr over-ride.
        # in the mean-time, use _clear_attriutbute.
        model._clear_attribute(constraint_name)

#
# construct a scenario instance - just like it sounds!
#
def construct_scenario_instance(scenario_tree_instance,
                                scenario_data_directory_name,
                                scenario_name,
                                reference_model,
                                verbose,
                                preprocess = True,
                                linearize = True):

    if verbose is True:
        if scenario_tree_instance._scenario_based_data == 1:
            print "Scenario-based instance initialization enabled"
        else:
            print "Node-based instance initialization enabled"

    scenario = scenario_tree_instance.get_scenario(scenario_name)
    scenario_instance = None

    if verbose is True:
        print "Creating instance for scenario=" + scenario._name

    try:
        if scenario_tree_instance._scenario_based_data == 1:
            scenario_data_filename = scenario_data_directory_name + os.sep + scenario._name + ".dat"
            if verbose is True:
                print "Data for scenario=" + scenario._name + " loads from file=" + scenario_data_filename
            scenario_instance = reference_model.create(scenario_data_filename, preprocess=preprocess)
        else:
            scenario_instance = reference_model.clone()

            data_files = []
            current_node = scenario._leaf_node
            while current_node is not None:
                node_data_filename = scenario_data_directory_name + os.sep + current_node._name + ".dat"
                if os.path.exists(node_data_filename) is False:
                    raise RuntimeError, "Node data file="+node_data_filename+" does not exist or cannot be accessed"
                data_files.append(node_data_filename)
                current_node = current_node._parent

            # to make sure we read from root node to leaf node
            data_files.reverse()

            scenario_data = ModelData()
            for data_file in data_files:
                if verbose is True:
                    print "Node data for scenario=" + scenario._name + " partially loading from file=" + data_file
                scenario_data.add(data_file)

            scenario_data.read(model=scenario_instance)
            scenario_instance.load(scenario_data)
            
            if preprocess is True:
                scenario_instance.preprocess()
    except Exception, exception:
        raise RuntimeError, "Failed to create model instance for scenario=" + scenario._name+"; Source error="+str(exception)

    if linearize is True:
        # IMPT: The model *must* be preprocessed in order for linearization to work. This is because
        #       linearization relies on the canonical expression representation extraction routine,
        #       which in turn relies on variables being identified/categorized (e.g., into "Used").
        if preprocess is False:
            scenario_instance.preprocess()
        linearize_model_expressions(scenario_instance)

    return scenario_instance


# creates all PH parameters for a problem instance, given a scenario tree
# (to identify the relevant variables), a default rho (simply for initialization),
# and a boolean indicating if quadratic penalty terms are to be linearized.
# returns a list of any created variables, specifically when linearizing -
# this is useful to clean-up reporting.

def create_ph_parameters(instance, scenario_tree, default_rho, linearizing_penalty_terms):

    new_penalty_variable_names = []

    # first, gather all unique variables referenced in any stage
    # other than the last, independent of specific indices. this
    # "gather" step is currently required because we're being lazy
    # in terms of index management in the scenario tree - which
    # should really be done in terms of sets of indices.
    # NOTE: technically, the "instance variables" aren't really references
    # to the variable in the instance - instead, the reference model. this
    # isn't an issue now, but it could easily become one (esp. in avoiding deep copies).

    instance_variables = {}          # map between variable names and the variable in the reference model
    instance_variable_templates = {} # map between variable names and a list of index match templates 

    # collects indices referenced in any non-terminal stage. 
    for stage in scenario_tree._stages[:-1]:

        for variable_name, (reference_variable, index_match_template) in stage._variables.iteritems():

            reference_variable_name = reference_variable.name

            if reference_variable_name not in instance_variables:

                instance_variables[reference_variable_name] = reference_variable
                instance_variable_templates[reference_variable_name] = []

            instance_variable_templates[reference_variable_name].extend(index_match_template)

    for (variable_name, reference_variable) in instance_variables.iteritems():

        index_match_templates = instance_variable_templates[variable_name]

        match_indices = set()

        for index_match_template in instance_variable_templates[variable_name]:
           these_match_indices = extractVariableIndices(getattr(instance,variable_name),index_match_template)
           match_indices = match_indices.union(these_match_indices)

        new_w_parameter_name = "PHWEIGHT_"+variable_name
        new_avg_parameter_name = "PHAVG_"+variable_name
        new_xbar_parameter_name = "PHXBAR_"+variable_name
        new_rho_parameter_name = "PHRHO_"+variable_name
        if linearizing_penalty_terms > 0:
            new_penalty_term_variable_name = "PHQUADPENALTY_"+variable_name
        new_blend_parameter_name = "PHBLEND_"+variable_name

        new_w_parameter = None
        new_avg_parameter = None
        new_xbar_parameter = None
        new_rho_parameter = None
        new_penalty_term_variable = None
        new_blend_parameter = None

        # this bit of ugliness is due to Pyomo not correctly handling the Param construction
        # case when the supplied index set consists strictly of None, i.e., the source variable
        # is a singleton. this case be cleaned up when the source issue in Pyomo is fixed.

        if (len(match_indices) is 1) and (None in match_indices):
            new_w_parameter = Param(name=new_w_parameter_name, default=0.0, nochecking=True)
            new_avg_parameter = Param(name=new_avg_parameter_name, default=0.0, nochecking=True)
            new_xbar_parameter = Param(name=new_xbar_parameter_name, default=0.0, nochecking=True)
            new_rho_parameter = Param(name=new_rho_parameter_name, default=0.0, nochecking=True)
            if linearizing_penalty_terms > 0:
                new_penalty_term_variable = Var(name=new_penalty_term_variable_name, bounds=(0.0,None))
            new_blend_parameter = Param(name=new_blend_parameter_name, within=Binary, default=False, nochecking=True)
        else:

            # create the index set and add it to the model. this should save memory and
            # replication costs, by avoiding the need to create in-line sets everywhere.
            new_variable_index_set = Set(initialize=match_indices,dimen=reference_variable._index.dimen)
            new_variable_index_set.construct()
            setattr(instance, "PHINDEXSET_"+variable_name, new_variable_index_set)

            new_w_parameter = Param(new_variable_index_set, name=new_w_parameter_name, default=0.0, nochecking=True)
            new_avg_parameter = Param(new_variable_index_set, name=new_avg_parameter_name, default=0.0, nochecking=True)
            new_xbar_parameter = Param(new_variable_index_set, name=new_xbar_parameter_name, default=0.0, nochecking=True)
            new_rho_parameter = Param(new_variable_index_set, name=new_rho_parameter_name, default=0.0, nochecking=True)
            if linearizing_penalty_terms > 0:
                new_penalty_term_variable = Var(new_variable_index_set, name=new_penalty_term_variable_name, bounds=(0.0,None))
            new_blend_parameter = Param(new_variable_index_set, name=new_blend_parameter_name, within=Binary, default=False, nochecking=True)

        setattr(instance,new_w_parameter_name,new_w_parameter)
        setattr(instance,new_avg_parameter_name,new_avg_parameter)
        setattr(instance,new_xbar_parameter_name,new_xbar_parameter)
        setattr(instance,new_rho_parameter_name,new_rho_parameter)
        if linearizing_penalty_terms > 0:
            setattr(instance, new_penalty_term_variable_name, new_penalty_term_variable)
            new_penalty_variable_names.append(new_penalty_term_variable_name)
        setattr(instance,new_blend_parameter_name,new_blend_parameter)

        # if you don't explicitly assign values to each index, the entry isn't created - instead, when you reference
        # the parameter that hasn't been explicitly assigned, you just get the default value as a constant. I'm not
        # sure if this has to do with the model output, or the function of the model, but I'm doing this to avoid the
        # issue in any case for now. NOTE: I'm not sure this is still the case in Pyomo.
        for index in match_indices:
            new_w_parameter[index] = 0.0
            new_avg_parameter[index] = 0.0
            new_xbar_parameter[index] = 0.0
            new_rho_parameter[index] = default_rho
            new_blend_parameter[index] = 1

    return new_penalty_variable_names

def preprocess_scenario_instance(scenario_instance, instance_variables_fixed, \
                                 instance_constraints_modified, instance_ph_constraints, \
                                 instance_objective_changed, instance_objective_modified, solver_type):

    from coopr.pyomo.preprocess.identify_vars import IdentifyVariablesPresolver
    from coopr.pyomo.preprocess.compute_canonical_repn import ComputeCanonicalRepn

    # these are the only two preprocessors currently invoked by 
    # the simple_preprocessor, which in turn is invoked by the 
    # preprocess() method of PyomoModel.
    canonical_expression_preprocessor = ComputeCanonicalRepn()

    if (instance_objective_changed is True) or (instance_variables_fixed is True):

        # there are optimizations that can be performed here, if we had finer-grained information.
        identify_vars_preprocessor = IdentifyVariablesPresolver()
        identify_vars_preprocessor.preprocess(scenario_instance)                       

    if (instance_objective_modified is False) and (instance_variables_fixed is False) and (instance_constraints_modified is False): 

       # the condition of "nothing modified" should only be triggered at PH iteration 0. instances are
       # already preprocessed following construction, and there isn't any augmentation of the objective 
       # function yet.
       return

    if (instance_objective_modified is True):

       if (solver_type == "asl") or (solver_type == "ipopt"):
          # this is kludgy until we make workflows explicit in Coopr - the NL writer combines writing and
          # preprocessing, so all we can do is tag the instance with an appropriate attribute.
          setattr(scenario_instance, "gen_obj_ampl_repn", True) # the value is irrelevant - the writer checks for the existence of this attribute
       else:
          # if only the objective changed, there is minimal work to do - 
          # just recompute the associated canonical expressions.
          canonical_expression_preprocessor.preprocess_objectives(scenario_instance, None)

    if (instance_variables_fixed is True):

        if (solver_type == "asl") or (solver_type == "ipopt"):
            # this is kludgy until we make workflows explicit in Coopr - the NL writer combines writing and
            # preprocessing, so all we can do is tag the instance with an appropriate attribute.
            setattr(scenario_instance, "gen_obj_ampl_repn", True) # the value is irrelevant - the writer checks for the existence of this attribute
            setattr(scenario_instance, "gen_con_ampl_repn", True) # the value is irrelevant - the writer checks for the existence of this attribute                                    
        else:
            canonical_expression_preprocessor.preprocess(scenario_instance)

    elif (instance_constraints_modified is True):

        # only pre-process the piecewise constraints

        if (solver_type == "asl") or (solver_type == "ipopt"):
            # this is kludgy until we make workflows explicit in Coopr - the NL writer combines writing and
            # preprocessing, so all we can do is tag the instance with an appropriate attribute.
            setattr(scenario_instance, "gen_con_ampl_repn", True) # the value is irrelevant - the writer checks for the existence of this attribute                                    
        else:
            var_id_map = {}
            for constraint_name in instance_ph_constraints:
                canonical_expression_preprocessor.preprocess_constraint(scenario_instance, getattr(scenario_instance, constraint_name), var_id_map)
