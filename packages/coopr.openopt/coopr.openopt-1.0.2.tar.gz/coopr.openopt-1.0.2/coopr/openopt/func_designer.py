__all__ = ['Pyomo2FuncDesigner']

from coopr.pyomo.base import Constraint, Objective, Var, maximize
from coopr.pyomo.base import expr, var
from coopr.pyomo.base import param
from coopr.pyomo.base import numvalue
from coopr.pyomo.io.cpxlp import CPXLP_numeric_labeler
from coopr.opt import SymbolMap
try:
    import FuncDesigner
    FD_available=True
except ImportError:
    FD_available=False

import logging
logger = logging.getLogger('coopr.pyomo')

labeler = CPXLP_numeric_labeler('x')

if FD_available:

    try:
        tanh = FuncDesigner.tanh
        arcsinh = FuncDesigner.arcsinh
        arccosh = FuncDesigner.arccosh
        arctanh = FuncDesigner.arctanh
    except:
        import FuncDesignerExt
        tanh = FuncDesignerExt.tanh
        arcsinh = FuncDesignerExt.arcsinh
        arccosh = FuncDesignerExt.arccosh
        arctanh = FuncDesignerExt.arctanh

    def fd_pow(x,y):
        return x**y

    intrinsic_function_expressions = {
        'log':FuncDesigner.log,
        'log10':FuncDesigner.log10,
        'sin':FuncDesigner.sin,
        'cos':FuncDesigner.cos,
        'tan':FuncDesigner.tan,
        'sinh':FuncDesigner.sinh,
        'cosh':FuncDesigner.cosh,
        'tanh':FuncDesigner.tanh,
        'asin':FuncDesigner.arcsin,
        'acos':FuncDesigner.arccos,
        'atan':FuncDesigner.arctan,
        'exp':FuncDesigner.exp,
        'sqrt':FuncDesigner.sqrt,
        'asinh':FuncDesigner.arcsinh,
        'acosh':arccosh,
        'atanh':arctanh,
        'pow':fd_pow,
        'abs':FuncDesigner.abs,
        'ceil':FuncDesigner.ceil,
        'floor':FuncDesigner.floor
    }


id_counter=0

def Pyomo2FD_expression(exp, ipoint, vars, symbol_map):
    if isinstance(exp, expr._IntrinsicFunctionExpression):
        if not exp.name in intrinsic_function_expressions:
            logger.error("Unsupported intrinsic function (%s)", exp.name)
            raise TypeError("FuncDesigner does not support '{0}' expressions".format(exp.name))

        args = []
        for child_exp in exp._args:
            args.append( Pyomo2FD_expression(child_exp, ipoint, vars, symbol_map) )

        fn = intrinsic_function_expressions[exp.name]
        return fn(*tuple(args))

    elif isinstance(exp, expr._SumExpression):
        args = []
        for child_exp in exp._args:
            args.append( Pyomo2FD_expression(child_exp, ipoint, vars, symbol_map) )

        iargs = args.__iter__()
        #
        # NOTE: this call to FuncDesigner.sum() _must_ be passed a list.  If a 
        # generator is passed to this function, then an unbalanced expression tree will
        # be generated that is not well-suited for large models!
        #
        return FuncDesigner.sum([c*iargs.next() for c in exp._coef]) + exp._const

    elif isinstance(exp, expr._ProductExpression):
        ans = exp.coef
        for n in exp._numerator:
            ans *= Pyomo2FD_expression(n, ipoint, vars, symbol_map)
        for n in exp._denominator:
            ans /= Pyomo2FD_expression(n, ipoint, vars, symbol_map)
        return ans

    #elif isinstance(exp, expr._InequalityExpression):
        #args = []
        #for child_exp in exp._args:
            #args.append( Pyomo2FD_expression(child_exp, ipoint, vars, symbol_map) )
#
        #ans = args[0]
        #for i in xrange(len(args)-1):
            ## FD doesn't care whether the inequality is strict
            #ans = ans < args[i+1]
        #return ans

    #elif isinstance(exp, expr._InequalityExpression):
        #return Pyomo2FD_expression(exp._args[0], ipoint, vars) == Pyomo2FD_expression(exp._args[1], ipoint, vars, symbol_map)

    elif isinstance(exp, expr._IdentityExpression):
        return Pyomo2FD_expression(exp._args[0], ipoint, vars, symbol_map)

    elif (isinstance(exp,var._VarData) or isinstance(exp,var.Var)) and not exp.fixed_value():
        vname = symbol_map.getSymbol(exp, labeler)
        if not vname in vars:
            vars[vname] = FuncDesigner.oovar(vname)
            ipoint[vars[vname]] = 0.0 if exp.value is None else exp.value
            #symbol_map.getSymbol(exp, lambda obj,x: x, vname)
        return vars[vname]

    elif isinstance(exp,param._ParamData):
        return exp.value

    elif type(exp) in [int, float, long]:
        return exp

    elif isinstance(exp,numvalue.NumericConstant) or exp.fixed_value:
        return exp.value

    else:
        raise ValueError, "Unsupported expression type in Pyomo2FD_expression: "+str(type(exp))


def Pyomo2FuncDesigner(instance):
    if not FD_available:
        return None

    ipoint = {}
    vars = {}
    sense = None
    nobj = 0
    smap = SymbolMap(instance)

    _f_name = []
    _f = []
    _c = []
    for c in instance.active_components():
        if issubclass(c, Constraint):
            cons = instance.active_components(c)
            for con_set_name in cons:
                con_set = cons[con_set_name]
                # For each indexed constraint in the constraint set
                for ndx in con_set._data:
                    body = Pyomo2FD_expression(con_set._data[ndx].body, ipoint, vars, smap)
                    if not con_set._data[ndx].lower is None:
                        lower = Pyomo2FD_expression(con_set._data[ndx].lower, ipoint, vars, smap)
                        _c.append( body > lower )
                    if not con_set._data[ndx].upper is None:
                        upper = Pyomo2FD_expression(con_set._data[ndx].upper, ipoint, vars, smap)
                        _c.append( body < upper )

        elif issubclass(c, Var):
            _vars = instance.active_components(c)
            for var_set_name in _vars:
                var_set = _vars[var_set_name]
                for ndx in var_set.keys():
                    body = Pyomo2FD_expression(var_set[ndx], ipoint, vars, smap)
                    if not var_set[ndx].lb is None:
                        lower = Pyomo2FD_expression(var_set[ndx].lb, ipoint, vars, smap)
                        _c.append( body > lower )
                    if not var_set[ndx].ub is None:
                        upper = Pyomo2FD_expression(var_set[ndx].ub, ipoint, vars, smap)
                        _c.append( body < upper )

        elif issubclass(c, Objective):
            objs = instance.active_components(c)
            for obj_set_name in objs:
                obj_set = objs[obj_set_name]
                sense = obj_set.sense
                # For each indexed objective in the objective set
                for ndx in obj_set._data:
                    nobj += 1
                    if sense == maximize:
                        _f.append( - Pyomo2FD_expression(obj_set._data[ndx].expr, ipoint, vars, smap) )
                    else:
                        _f.append( Pyomo2FD_expression(obj_set._data[ndx].expr, ipoint, vars, smap) )
                    _f_name.append( obj_set._data[ndx].name )
                    smap.getSymbol(obj_set._data[ndx], lambda obj,x: x, obj_set._data[ndx].name)

    # TODO - use 0.0 for default values???
    # TODO - create results map
    S = FuncDesigner.oosystem()
    S._symbol_map = smap
    S.f = _f[0]
    S._f_name = _f_name
    S.constraints.update(_c)
    S.initial_point = ipoint
    S.sense = sense
    #print ipoint
    #print dir(S)
    #print S.nlpSolvers
    #print S.constraints
    return S

