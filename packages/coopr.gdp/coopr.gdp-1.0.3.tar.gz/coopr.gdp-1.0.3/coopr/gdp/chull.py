#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from pyutilib.component.core import Plugin, implements
from coopr.pyomo import *
from coopr.pyomo.base import expr
from coopr.pyomo.base.var import _VarData
from coopr.gdp import *

import logging
logger = logging.getLogger('coopr.pyomo')

class ConvexHull_Transforamtion(Plugin):
    implements(IPyomoScriptModifyInstance)

    def __init__(self):
        Plugin.__init__(self)
        self.handlers = {
            Constraint : self._xform_constraint,
            Var : self._xform_var,
            }

    def apply(self, **kwds):
        options = kwds['options']
        model = kwds['model']
        instance = kwds['instance']
        comp_map = instance.components._component

        disaggregatedVars = {}

        for disjunct in comp_map.get(Disjunct, {}).itervalues():
            if len(disjunct._data):
                for d in disjunct._data.itervalues():
                    self._transform_disjunct(d, instance, disaggregatedVars)
            else:
                self._transform_disjunct(disjunct, instance, disaggregatedVars)

        # Serious violation of encapsulation... treat each disjunction
        # as a simple constraint
        for disj in comp_map.get(Disjunction, {}).itervalues():
            comp_map[Constraint][disj.name]=disj

        def _generate_name(idx):
            if type(idx) in (tuple, list):
                if len(idx) == 0:
                    return ''
                else:
                    return '['+','.join([_generate_name(x) for x in idx])+']'
            else:
                return str(idx)

        # Correlate the disaggregated variables across the disjunctions
        for Disj in comp_map.get(Disjunction, {}).itervalues():
            for idx, disjuncts in Disj._disjuncts.iteritems():
                localVars = {}
                cName = _generate_name(idx)
                cName = Disj.name + (len(cName) and "."+cName or "")
                for d in disjuncts:
                    for eid, e in disaggregatedVars.get(id(d), ['',{}])[1].iteritems():
                        localVars.setdefault(eid, (e[0],[]))[1].append(e[2])
                for d in disjuncts:
                    for eid, v in localVars.iteritems():
                        if eid not in disaggregatedVars.get(id(d), ['',{}])[1]:
                            tmp = Var(domain=v[0].domain)
                            tmp.setlb(min(0,v[0].lb()))
                            tmp.setub(max(0,v[0].ub()))
                            disaggregatedVars[id(d)][1][eid] = (v[0], d.indicator_var, tmp)
                            v[1].append(tmp)
                for v in sorted(localVars.values(), key=lambda x: x[0].name):
                    newC = Constraint( expr = v[0] == sum(v[1]) )
                    instance._add_component( cName+"."+v[0].name, newC )
                    newC.construct()

        # Promote the local disaggregated variables and add BigM
        # constraints to force them to 0 when not active.
        for d_data in sorted(disaggregatedVars.values(), key=lambda x: x[0]):
            for e in sorted(d_data[1].values(), key=lambda x: x[0].name):
                # add the disaggregated variable
                instance._add_component( d_data[0]+e[0].name, e[2] )
                e[2].construct()
                # add Big-M constraints on disaggregated variable to
                # force to 0 if not active
                if e[2].lb is not None and e[2].lb() != 0:
                    newC = Constraint(expr=e[2].lb() * e[1] <= e[2])
                    instance._add_component( d_data[0]+e[0].name+"_lo", newC )
                    newC.construct()
                if e[2].ub is not None and e[2].ub() != 0:
                    newC = Constraint(expr=e[2] <= e[2].ub() * e[1])
                    instance._add_component( d_data[0]+e[0].name+"_hi", newC )
                    newC.construct()

        # REQUIRED: re-call preprocess()
        instance.preprocess()


    def _transform_disjunct(self, disjunct, instance, disaggregatedVars):
        # Calculate a unique name by concatenating all parent block names
        fullName = ''
        d = disjunct
        while d._parent is not None and d._parent() is not None:
            fullName = d.name + '.' + fullName
            d = d._parent()

        varMap = disaggregatedVars.setdefault(id(disjunct), [fullName,{}])[1]

        # Transform each component within this disjunct
        for name, obj in disjunct.components.iteritems():
            handler = self.handlers.get(obj.type(), None)
            if handler is None:
                raise GDP_Error, "No cHull transformation handler registered "\
                      "for modeling components of type " + obj.type()
            handler(fullName+name, obj, varMap, disjunct, instance)


    def _xform_var(self, name, var, varMap, disjunct, instance):
        # "Promote" the local variables up to the main model
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("GDP(cHull): Promoting local variable '%s' as '%s'",
                         var.name, name)
        instance._add_component(name, var)


    def _xform_constraint(self, _name, constraint, varMap, disjunct, instance):
        for cname, c in constraint._data.iteritems():
            name = _name + (cname and '.'+cname or '')

            if c.lin_body is not None:
                raise GDP_Error, 'GDP(cHull) cannot process linear ' \
                      'constraint bodies (yet) (found at ' + name + ').'

            constant = 0
            try:
                cannonical = generate_canonical_repn(c.body)
                NL = canonical_is_nonlinear(cannonical)
            except:
                NL = True
            exp = self._var_subst(NL, c.body, disjunct.indicator_var, varMap)
            if NL:
                exp = exp * disjunct.indicator_var
            else:
                # We need to make sure to pull out the constant terms
                # from the expression and put them into the lb/ub
                constant = cannonical.get(0, {}).get(None,0)

            if c.lower is not None:
                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(cHull): Promoting constraint " +
                                 "'%s' as '%s_lo'", name, name)
                bound = c.lower() - constant
                if bound != 0:
                    newC = Constraint( expr = bound*disjunct.indicator_var \
                                       <= exp - constant )
                else:
                    newC = Constraint( expr = bound <= exp - constant )
                instance._add_component( name+"_lo", newC )
                newC.construct()
            if c.upper is not None:
                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(cHull): Promoting constraint " +
                                 "'%s' as '%s_hi'", name, name)
                bound = c.upper() - constant
                if bound != 0:
                    newC = Constraint( expr = exp - constant <= \
                                       bound*disjunct.indicator_var )
                else:
                    newC = Constraint( expr = exp - constant <= bound )
                instance._add_component( name+"_hi", newC )
                newC.construct()

    def _var_subst(self, NL, exp, y, varMap):
        # Recursively traverse the S-expression and substitute all model
        # variables with disaggregated local disjunct variables (logic
        # stolen from collect_cannonical_repn())

        #
        # Expression
        #
        if isinstance(exp,expr.Expression):
            if isinstance(exp,expr._ProductExpression):
                exp._numerator = [self._var_subst(NL, e, y, varMap) for e in exp._numerator]
                exp._denominator = [self._var_subst(NL, e, y, varMap) for e in exp._denominator]
            elif isinstance(exp, expr._IdentityExpression) or \
                     isinstance(exp,expr._SumExpression) or \
                     isinstance(exp,expr._AbsExpression) or \
                     isinstance(exp,expr._PowExpression):
                exp._args = [self._var_subst(NL, e, y, varMap) for e in exp._args]
            else:
                raise ValueError, "Unsupported expression type: "+str(exp)
        #
        # Constant
        #
        elif exp.fixed_value():
            pass
        #
        # Variable
        #
        elif isinstance(exp, _VarData):
            # Check if this disjunct has used this variable before...
            if id(exp) not in varMap:
                # create a new variable
                if exp.lb is None or exp.ub is None:
                    raise GDP_Error, "Disjunct constraint referenced unbounded model variable; "\
                          "all variables must be bounded to use the Convex Hull transformation."
                v = Var(domain=exp.domain)
                v.setlb(min(0,exp.lb()))
                v.setub(max(0,exp.ub()))
                varMap[id(exp)] = (exp, y, v)
            if NL:
                return varMap[id(exp)][2] / y
            else:
                return varMap[id(exp)][2]
        elif exp.type() is Var:
            raise GDP_Error, "Unexpected Var encoundered in expression"
        #
        # ERROR
        #
        else:
            raise ValueError, "Unexpected expression type: "+str(exp)

        return exp

transform = ConvexHull_Transforamtion()
