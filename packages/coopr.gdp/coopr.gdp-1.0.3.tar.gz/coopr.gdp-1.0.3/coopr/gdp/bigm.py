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
from coopr.gdp import *

import logging
logger = logging.getLogger('coopr.pyomo')

class BigM_Transforamtion(Plugin):
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

        for disjunct in comp_map.get(Disjunct, {}).itervalues():
            if len(disjunct._data):
                for d in disjunct._data.itervalues():
                    self._bigM_transform(d, instance)
            else:
                self._bigM_transform(disjunct, instance)

        # Serious violation of encapsulation... treat each disjunction
        # as a simple constraint
        for disj in comp_map.get(Disjunction, {}).itervalues():
            comp_map[Constraint][disj.name]=disj

        # REQUIRED: re-call preprocess()
        instance.preprocess()

    def _bigM_transform(self, disjunct, instance):
        # Calculate a unique name by concatenating all parent block names
        fullName = ''
        d = disjunct
        while d._parent is not None and d._parent() is not None:
            fullName = d.name + '.' + fullName
            d = d._parent()

        # Transform each component within this disjunct
        for name, obj in disjunct.components.iteritems():
            handler = self.handlers.get(obj.type(), None)
            if handler is None:
                raise GDP_Error, "No BigM transformation handler registered "\
                      "for modeling components of type " + obj.type()
            handler(fullName+name, obj, disjunct, instance)


    def _xform_constraint(self, _name, constraint, disjunct, instance):
        M = disjunct.next_M()
        for cname, c in constraint._data.iteritems():
            name = _name + (cname and '.'+cname or '')

            if c.lin_body is not None:
                raise GDP_Error, 'GDP(BigM) cannot process linear ' \
                      'constraint bodies (yet) (found at ' + name + ').'

            if isinstance(M, list):
                if len(M):
                    m = M.pop(0)
                else:
                    m = (None,None)
            else:
                m = M
            if not isinstance(m, tuple):
                if m is None:
                    m = (None, None)
                else:
                    m = (-1*m,m)

            # If we need an M (either for upper and/or lower bounding of
            # the expression, then try and estimate it
            if ( c.lower is not None and m[0] is None ) or \
                   ( c.upper is not None and m[1] is None ):
                m = self._estimate_M(c.body, name, m)

            bounds = (c.lower, c.upper)
            for i in (0,1):
                if bounds[i] is None:
                    continue
                if m[i] is None:
                    raise GDP_Error, "Cannot relax disjunctive " + \
                          "constraint %s because M is not defined." % name
                n = name;
                if bounds[1-i] is not None:
                    n += ('_lo','_hi')[i]

                if __debug__ and logger.isEnabledFor(logging.DEBUG):
                    logger.debug("GDP(BigM): Promoting local constraint "
                                 "'%s' as '%s'", constraint.name, n)
                M_expr = (m[i]-bounds[i])*(1-disjunct.indicator_var)
                if i == 0:
                    newC = Constraint(expr=c.lower <= c.body - M_expr)
                else:
                    newC = Constraint(expr=c.body - M_expr <= c.upper)
                instance._add_component(n, newC)
                newC.construct()


    def _xform_var(self, name, var, disjunct, instance):
        # "Promote" the local variables up to the main model
        if __debug__ and logger.isEnabledFor(logging.DEBUG):
            logger.debug("GDP(BigM): Promoting local variable '%s' as '%s'",
                         var.name, name)
        instance._add_component(name, var)


    def _estimate_M(self, expr, name, m):
        # Calculate a best guess at M
        tmp = generate_canonical_repn(expr)
        M = [0,0]
        for degree, terms in tmp.iteritems():
            if degree == 0:
                for term, coef in terms.iteritems():
                    for i in (0,1):
                        if M[i] is not None:
                            M[i] += coef
            elif degree == 1:
                for term, coef in terms.iteritems():
                    var = tmp[-1][term]
                    bounds = (var.lb, var.ub)
                    for i in (0,1):
                        # reverse the bounds if the coefficient is negative
                        if coef > 0:
                            j = i
                        else:
                            j = 1-i

                        try:
                            M[j] += value(bounds[i]) * coef
                        except:
                            M[j] = None
            elif degree != -1:
                logger.error("GDP(BigM): cannot estimate M for nonlinear "
                             "expressions.\n\t(found while processing %s)",
                             name)
                return m

        # Allow user-defined M values to override the estimates
        for i in (0,1):
            if m[i] is not None:
                M[i] = m[i]
        return tuple(M)

transform = BigM_Transforamtion()
