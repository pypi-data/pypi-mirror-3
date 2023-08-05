#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

# this module contains various utilities for creating PH weighted penalty
# objectives, e.g., through quadratic or linearized penalty terms.

from math import fabs, log, exp
from coopr.pyomo import *
from phutils import indexToString

# IMPT: In general, the breakpoint computation codes can return a 2-list even if the lb equals
#       the ub. This case happens quite often in real models (although typically lb=xvag=ub).
#       See the code for constructing the pieces on how this case is handled in the linearization.

#
# routine to compute linearization breakpoints uniformly between the bounds and the mean.
#

def compute_uniform_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints_per_side, tolerance):

    breakpoints = []

    # add the lower bound - the first breakpoint.
    breakpoints.append(lb)

    # determine the breakpoints to the left of the mean.
    left_step = (xavg - lb) / num_breakpoints_per_side
    current_x = lb
    for i in range(1,num_breakpoints_per_side+1):
        this_lb = current_x
        this_ub = current_x+left_step
        if (fabs(this_lb-lb) > tolerance) and (fabs(this_lb-xavg) > tolerance):
            breakpoints.append(this_lb)
        current_x += left_step

    # add the mean - it's always a breakpoint. unless!
    # the lb or ub and the avg are the same.
    if (fabs(lb-xavg) > tolerance) and (fabs(ub-xavg) > tolerance):
        breakpoints.append(xavg)

    # determine the breakpoints to the right of the mean.
    right_step = (ub - xavg) / num_breakpoints_per_side
    current_x = xavg
    for i in range(1,num_breakpoints_per_side+1):
        this_lb = current_x
        this_ub = current_x+right_step
        if (fabs(this_ub-xavg) > tolerance) and (fabs(this_ub-ub) > tolerance):
            breakpoints.append(this_ub)
        current_x += right_step

    # add the upper bound - the last breakpoint.
    # the upper bound should always be different than the lower bound (I say with some
    # hesitation - it really depends on what plugins are doing to modify the bounds dynamically).
    breakpoints.append(ub)

    return breakpoints

#
# routine to compute linearization breakpoints uniformly between the current node min/max bounds.
#

def compute_uniform_between_nodestat_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints, tolerance):

    breakpoints = []

    # add the lower bound - the first breakpoint.
    breakpoints.append(lb)

    # add the node-min - the second breakpoint. but only if it is different than the lower bound and the mean.
    if (fabs(node_min-lb) > tolerance) and (fabs(node_min-xavg) > tolerance):
        breakpoints.append(node_min)

    step = (node_max - node_min) / num_breakpoints
    current_x = node_min
    for i in range(1,num_breakpoints+1):
        this_lb = current_x
        this_ub = current_x+step
        if (fabs(this_lb-node_min) > tolerance) and (fabs(this_lb-node_max) > tolerance) and (fabs(this_lb-xavg) > tolerance):
            breakpoints.append(this_lb)
        current_x += step

    # add the node-max - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
    if (fabs(node_max-ub) > tolerance) and (fabs(node_max-xavg) > tolerance):
        breakpoints.append(node_max)

    # add the upper bound - the last breakpoint.
    breakpoints.append(ub)

    # add the mean - it's always a breakpoint. unless! -
    # it happens to be equal to (within tolerance) the lower or upper bounds.
    # sort to insert it in the correct place.
    if (fabs(xavg - lb) > tolerance) and (fabs(xavg - ub) > tolerance):
        breakpoints.append(xavg)
    breakpoints.sort()

    return breakpoints

#
# routine to compute linearization breakpoints using "Woodruff" relaxation of the compute_uniform_between_nodestat_breakpoints.
#

def compute_uniform_between_woodruff_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints, tolerance):

    breakpoints = []

    # add the lower bound - the first breakpoint.
    breakpoints.append(lb)

    # be either three "differences" from the mean, or else "halfway to the bound", whichever is closer to the mean.
    left = max(xavg - 3.0 * (xavg - node_min), xavg - 0.5 * (xavg - lb))
    right = min(xavg + 3.0 * (node_max - xavg), xavg + 0.5 * (ub - xavg))

    # add the left bound - the second breakpoint. but only if it is different than the lower bound and the mean.
    if (fabs(left-lb) > tolerance) and (fabs(left-xavg) > tolerance):
        breakpoints.append(left)

    step = (right - left) / num_breakpoints
    current_x = left
    for i in range(1,num_breakpoints+1):
        this_lb = current_x
        this_ub = current_x+step
        if (fabs(this_lb-left) > tolerance) and (fabs(this_lb-right) > tolerance) and (fabs(this_lb-xavg) > tolerance):
            breakpoints.append(this_lb)
        current_x += step

    # add the right bound - the second-to-last breakpoint. but only if it is different than the upper bound and the mean.
    if (fabs(right-ub) > tolerance) and (fabs(right-xavg) > tolerance):
        breakpoints.append(right)

    # add the upper bound - the last breakpoint.
    breakpoints.append(ub)

    # add the mean - it's always a breakpoint.
    # sort to insert it in the correct place.
    breakpoints.append(xavg)
    breakpoints.sort()

    return breakpoints

#
# routine to compute linearization breakpoints based on an exponential distribution from the mean in each direction.
#

def compute_exponential_from_mean_breakpoints(lb, node_min, xavg, node_max, ub, num_breakpoints_per_side, tolerance):

    breakpoints = []

    # add the lower bound - the first breakpoint.
    breakpoints.append(lb)

    # determine the breakpoints to the left of the mean.
    left_delta = xavg - lb
    base = exp(log(left_delta) / num_breakpoints_per_side)
    current_offset = base
    for i in range(1,num_breakpoints_per_side+1):
        current_x = xavg - current_offset
        if (fabs(current_x-lb) > tolerance) and (fabs(current_x-xavg) > tolerance):
            breakpoints.append(current_x)
        current_offset *= base

    # add the mean - it's always a breakpoint.
    breakpoints.append(xavg)

    # determine the breakpoints to the right of the mean.
    right_delta = ub - xavg
    base = exp(log(right_delta) / num_breakpoints_per_side)
    current_offset = base
    for i in range(1,num_breakpoints_per_side+1):
        current_x = xavg + current_offset
        if (fabs(current_x-xavg) > tolerance) and (fabs(current_x-ub) > tolerance):
            breakpoints.append(current_x)
        current_offset *= base

    # add the upper bound - the last breakpoint.
    breakpoints.append(ub)

    return breakpoints

#
# a utility to create piece-wise linear constraint expressions for a given variable, for
# use in constructing the augmented (penalized) PH objective. lb and ub are the bounds
# on this piece, variable is the actual instance variable, and average is the instance
# parameter specifying the average of this variable across instances sharing passing
# through a common tree node. lb and ub are floats.
# IMPT: There are cases where lb=ub, in which case the slope is 0 and the intercept
#       is simply the penalty at the lower(or upper) bound.
#

def create_piecewise_constraint_tuple(lb, ub, instance_variable, variable_average, quad_variable, tolerance):

    penalty_at_lb = (lb - value(variable_average)) * (lb - value(variable_average))
    penalty_at_ub = (ub - value(variable_average)) * (ub - value(variable_average))
    slope = None
    if fabs(ub-lb) > tolerance:
        slope = (penalty_at_ub - penalty_at_lb) / (ub - lb)
    else:
        slope = 0.0
    intercept = penalty_at_lb - slope * lb
    expression = (0.0, quad_variable - slope * instance_variable - intercept, None)

    return expression

#
# form the baseline objective. really just a wrapper around a clone
# operation at this point.
#

def form_standard_objective(instance_name, instance, original_objective_expression):

    objective_name = instance.active_components(Objective).keys()[0]
    objective = instance.active_components(Objective)[objective_name]
    # clone the objective, because we're going to augment (repeatedly) the original objective.
    objective_expression = original_objective_expression.clone()
    instance.active_components(Objective)[objective_name]._data[None].expr = objective_expression

#
# form the penalized PH objective, guided by various options.
#

def form_ph_objective(instance_name, instance, original_objective_expression, scenario_tree, \
                      linearize_nonbinary_penalty_terms, drop_proximal_terms, \
                      retain_quadratic_binary_terms):

    # cache for efficiency purposes.
    instance_parameters = instance.active_components(Param)
    instance_variables = instance.active_components(Var)
    instance_objectives = instance.active_components(Objective)

    objective_name = instance_objectives.keys()[0]
    objective = instance_objectives[objective_name]
    # clone the objective, because we're going to augment (repeatedly) the original objective.
    objective_expression = original_objective_expression.clone()

    # linear penalty expressions.
    linear_expression = 0.0 # indicates unassigned

    # quadratic penalty expressions.
    quad_expression = 0.0 # indicates unassigned

    # for each blended variable (i.e., those not appearing in the final stage),
    # add the linear and quadratic penalty terms to the objective.
    for stage in scenario_tree._stages[:-1]: # skip the last stage, as no blending occurs

        # identify the node in the scenario tree corresponding to this instance, so
        # we can extract the appropriate min/avg/max values for use in forming the 
        # various constraints and objective expressions.
        variable_tree_node = None
        for node in stage._tree_nodes:
            for scenario in node._scenarios:
                if scenario._name == instance_name:
                    variable_tree_node = node
                    break

        for variable_name, (reference_variable, index_template) in stage._variables.iteritems():

            variable_type = reference_variable.domain

            w_parameter_name = "PHWEIGHT_"+variable_name
            w_parameter = instance_parameters[w_parameter_name]

            xbar_parameter_name = "PHXBAR_"+variable_name
            xbar_parameter = instance_parameters[xbar_parameter_name]

            rho_parameter_name = "PHRHO_"+variable_name
            rho_parameter = instance_parameters[rho_parameter_name]

            blend_parameter_name = "PHBLEND_"+variable_name
            blend_parameter = instance_parameters[blend_parameter_name]

            node_min_parameter = variable_tree_node._minimums[variable_name]
            node_max_parameter = variable_tree_node._maximums[variable_name]

            quad_penalty_term_variable = None
            # if linearizing, then we have previously defined a variable associated with the result of the
            # linearized approximation of the penalty term - this is simply added to the objective function.
            if linearize_nonbinary_penalty_terms > 0:
                quad_penalty_term_variable_name = "PHQUADPENALTY_"+variable_name
                quad_penalty_term_variable = instance_variables[quad_penalty_term_variable_name]

            instance_variable = instance_variables[variable_name]

            # only a subset of the indices of a particular variable may be associated with a given scenario tree node.
            variable_indices = variable_tree_node._variable_indices[variable_name]

            for index in variable_indices:

                instance_varvalue = instance_variable[index]

                if (instance_varvalue.status is not VarStatus.unused) and (instance_varvalue.fixed is False):

                    # add the linear (w-weighted) term in a consistent fashion, independent of variable type.
                    # don't adjust the sign of the weight here - that has already been accounted for in the main PH routine.
                    linear_expression += w_parameter[index] * instance_varvalue

                    # there are some cases in which a user may want to avoid the proximal term completely.
                    # it's of course only a good idea when there are at least bounds (both lb and ub) on
                    # the variables to be blended. otherwise, unboundedness is likely to occur.
                    if drop_proximal_terms is False:

                        # deal with binaries
                        if isinstance(variable_type, BooleanSet) is True:

                            if retain_quadratic_binary_terms is False:
                                if objective.sense is minimize:
                                    linear_expression += (blend_parameter[index] * rho_parameter[index] / 2.0 * (instance_varvalue - 2.0 * xbar_parameter[index] * instance_varvalue + xbar_parameter[index] * xbar_parameter[index]))
                                else:
                                    linear_expression -= (blend_parameter[index] * rho_parameter[index] / 2.0 * (instance_varvalue - 2.0 * xbar_parameter[index] * instance_varvalue + xbar_parameter[index] * xbar_parameter[index]))
                            else:
                                if objective.sense is minimize:
                                    quad_expression += (blend_parameter[index] * (rho_parameter[index] / 2.0) * (instance_varvalue - xbar_parameter[index]) * (instance_varvalue - xbar_parameter[index]))
                                else:
                                    quad_expression -= (blend_parameter[index] * (rho_parameter[index] / 2.0) * (instance_varvalue - xbar_parameter[index]) * (instance_varvalue - xbar_parameter[index]))

                        # deal with everything else
                        else:

                            if linearize_nonbinary_penalty_terms > 0:

                                # the variables are easy - just a single entry.
                                if objective.sense is minimize:
                                    linear_expression += (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])
                                else:
                                    linear_expression -= (rho_parameter[index] / 2.0 * quad_penalty_term_variable[index])

                            else:

                               # deal with the baseline quadratic case.
                               if objective.sense is minimize:
                                   quad_expression += (blend_parameter[index] * (rho_parameter[index] / 2.0) * (instance_varvalue - xbar_parameter[index]) * (instance_varvalue - xbar_parameter[index]))
                               else:
                                   quad_expression -= (blend_parameter[index] * (rho_parameter[index] / 2.0) * (instance_varvalue - xbar_parameter[index]) * (instance_varvalue - xbar_parameter[index]))

    # augment the original objective with the new linear terms.
    if linear_expression != 0.0:
       objective_expression += linear_expression
    
    # if we are linearizing everything, then nothing will appear in the quadratic expression -
    # don't add the empty "0.0" expression to the objective. otherwise, the output file won't
    # be properly generated.
    if quad_expression != 0.0:
       objective_expression += quad_expression

    # assign the new expression to the objective.
    instance_objectives[objective_name]._data[None].expr = objective_expression

    return linear_expression, quad_expression

#
# form the constraints required to compute the cost variable values
# when linearizing PH objectives.
#

def form_linearized_objective_constraints(instance_name, instance, scenario_tree, \
                                          linearize_nonbinary_penalty_terms, drop_proximal_terms, \
                                          retain_quadratic_binary_terms, breakpoint_strategy, \
                                          tolerance):

    # flags indicating what type of instance components were modified/added.
    objective_modified = False
    constraints_added = False 

    # cache for efficiency purposes.
    instance_parameters = instance.active_components(Param)
    instance_variables = instance.active_components(Var)
    instance_objectives = instance.active_components(Objective)

    # keep track and return what was added to the instance, so
    # it can be cleaned up if necessary.
    new_instance_attributes = []

    # for each blended variable (i.e., those not appearing in the final stage),
    # add the appropriate constraints for compute the linearized cost variable.
    for stage in scenario_tree._stages[:-1]: # skip the last stage, as no blending occurs

        # identify the node in the scenario tree corresponding to this instance, so
        # we can extract the appropriate min/avg/max values for use in forming the 
        # various constraints and objective expressions.

        variable_tree_node = None
        for node in stage._tree_nodes:
            for scenario in node._scenarios:
                if scenario._name == instance_name:
                    variable_tree_node = node
                    break

        for variable_name, (reference_variable, index_template) in stage._variables.iteritems():

            variable_type = reference_variable.domain

            xbar_parameter_name = "PHXBAR_"+variable_name
            xbar_parameter = instance_parameters[xbar_parameter_name]

            node_min_parameter = variable_tree_node._minimums[variable_name]
            node_max_parameter = variable_tree_node._maximums[variable_name]

            # if linearizing, then we have previously defined a variable associated with the result of the
            # linearized approximation of the penalty term - this is simply added to the objective function.
            quad_penalty_term_variable_name = "PHQUADPENALTY_"+variable_name
            quad_penalty_term_variable = instance_variables[quad_penalty_term_variable_name]

            instance_variable = instance_variables[variable_name]

            # only a subset of the indices of a particular variable may be associated with a given scenario tree node.
            variable_indices = variable_tree_node._variable_indices[variable_name]

            for index in variable_indices:

                instance_varvalue = instance_variable[index]

                if (instance_varvalue.status is not VarStatus.unused) and (instance_varvalue.fixed is False):

                    # there are some cases in which a user may want to avoid the proximal term completely.
                    # it's of course only a good idea when there are at least bounds (both lb and ub) on
                    # the variables to be blended. otherwise, unboundedness is likely to occur.
                    if drop_proximal_terms is False:

                        # binaries have already been dealt with in the objective function formation.
                        if isinstance(variable_type, BooleanSet) is False:

                            if linearize_nonbinary_penalty_terms > 0:

                                # TBD - DEFINE CONSTRAINTS ON-THE-FLY?? (INDIVIDUALLY NAMED FOR NOW - CREATE INDEX SETS!) - OR A LEAST AN INDEX SET PER "PIECE"
                                xbar = xbar_parameter[index]
                                x = instance_varvalue

                                if x.lb is None or x.ub is None:
                                    var = variable_name + indexToString(index)
                                    msg = "Missing bound for variable '%s'\n"         \
                                          'Both lower and upper bounds required when' \
                                          ' piece-wise approximating quadratic '      \
                                          'penalty terms'
                                    raise ValueError, msg % var
                                lb = x.lb()
                                ub = x.ub()

                                node_min = value(node_min_parameter[index])
                                node_max = value(node_max_parameter[index])

                                # compute the breakpoint sequence according to the specified strategy.
                                try:
                                    strategy = (
                                      compute_uniform_breakpoints,
                                      compute_uniform_between_nodestat_breakpoints,
                                      compute_uniform_between_woodruff_breakpoints,
                                      compute_exponential_from_mean_breakpoints,
                                    )[ breakpoint_strategy ]
                                    args = ( lb, node_min, value(xbar), node_max, ub, \
                                        linearize_nonbinary_penalty_terms, tolerance )
                                    breakpoints = strategy( *args )
                                except ValueError, e:
                                    msg = 'A breakpoint distribution strategy (%s) '  \
                                          'is currently not supported within PH!'
                                    raise ValueError, msg % breakpoint_strategy

                                for i in range(0,len(breakpoints)-1):

                                    this_lb = breakpoints[i]
                                    this_ub = breakpoints[i+1]

                                    piece_tuple = create_piecewise_constraint_tuple(this_lb, this_ub, x, xbar, \
                                                                                    quad_penalty_term_variable[index], \
                                                                                    tolerance)

                                    def makePieceRule(tuple):
                                        def pieceRule(model):
                                            return tuple
                                        return pieceRule

                                    piece_constraint_name = "QUAD_PENALTY_PIECE_"+str(i)+"_"+variable_name+str(index)

                                    if hasattr(instance, piece_constraint_name) is False:
                                        # this is the first time the constraint is being added - add it to the list of PH-specific constraints for this instance.
                                        new_instance_attributes.append(piece_constraint_name)

                                    piece_constraint = Constraint(name=piece_constraint_name, rule=makePieceRule(piece_tuple))
                                    setattr(instance, piece_constraint_name, piece_constraint)
                                    constraints_added = True

    return new_instance_attributes



