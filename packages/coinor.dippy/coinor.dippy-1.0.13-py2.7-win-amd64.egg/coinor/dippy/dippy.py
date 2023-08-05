import coinor.pulp as pulp

from _dippy import *

from collections import defaultdict

class DipError(Exception):
    """
    Dip Exception
    """

_Solve = Solve
def Solve(prob, params=None):
    """
    Solve a DipProblem instance, returning a solution object

    @param prob A DipProblem instance to solve
    @param params A dictionary of parameters to pass to DIP
    """

    # params is a dictionary, keys are strings, values are
    # strings or dictionaries

    # if value is a dictionary, key is a section, and items
    # of dictionary are names/values

    # if value is a string, then section is NULL and key is name
    # for these parameters we also assign them to the 'DECOMP'
    # section as a convenience

    # the dictionary is converted into a dictionary of
    # strings indexed by (section, name) tuples

    processed = {}
    if params is None:
        params = {}

    if prob.branch_method == None:
        params['pyBranchMethod'] = '0'
    if prob.relaxed_solver == None:
        params['pyRelaxedSolver'] = '0'
    if prob.is_solution_feasible == None:
        params['pyIsSolutionFeasible'] = '0'
    if prob.generate_cuts == None:
        params['pyGenerateCuts'] = '0'
    if prob.heuristics == None:
        params['pyHeuristics'] = '0'
    if prob.init_vars == None:
        params['pyInitVars'] = '0'

    for key, value in params.items():
        valid_types = (basestring, int, float)
        if not isinstance(key, basestring):
            raise DipError("Bad key in parameter dictionary, expecting string")
        if isinstance(value, dict):
            section = key
            for name, param_val in value.items():
                if not isinstance(param_val, valid_types):
                    raise DipError("Bad value '%s' in parameter dictionary, expecting string or number" % param_val)
                processed[(section, name)] = str(param_val)
        elif isinstance(value, valid_types):
            # add this parameter to both the 'None' section and the 'DECOMP' section
            processed[(None, key)] = str(value)
            processed[('DECOMP', key)] = str(value)
        else:
            raise DipError("Bad value '%s' in parameter dictionary, expecting string" % value)

    # DIP only solves minimisation problems
    if prob.sense == pulp.LpMaximize:
        print "Dippy: Maximize objective transformed to "
        print "minimize objective before solving in DIP..."
        prob.sense = pulp.LpMinimize
        prob.objective = -prob.objective

    # DIP only allows non-negative variables. This is difficult
    # to transform automatically, so request re-formulation
    for v in prob.variables():
        if v.lowBound < 0:
            raise DipError("Variable %s has negative lower bound, please re-formulate using sum of non-negative variables" % v.name)
        
    # call the Solve method from _dippy
    try:
        solList = _Solve(prob, processed)
    except:
        print "Error returned from _dippy"
        raise
    
    # solList is a simple list of values, assign these to the variables
    for i, v in enumerate(prob.variables()):
        v.varValue = solList[i]

    # return a solution object
    return prob._makeSolution(solList)

class DipProblem(pulp.LpProblem):

    def __init__(self, *args, **kwargs):
        # callback functions can be passed to class constructor as keyword arguments
        self.branch_method = kwargs.pop('branch_method', None)
        self.relaxed_solver = kwargs.pop('relaxed_solver', None)
        self.is_solution_feasible = kwargs.pop('is_solution_feasible', None)
        self.generate_cuts = kwargs.pop('generate_cuts', None)
        self.heuristics = kwargs.pop('heuristics', None)
        self.init_vars = kwargs.pop('init_vars', None)

        super(DipProblem, self).__init__(*args, **kwargs)
        self._subproblem = []
        self.relaxation = RelaxationCollection(self)

    def variables(self):
        """
        Returns a list of the problem variables
        Overrides LpProblem.variables()
        
        Inputs:
            - none
        
        Returns:
            - A list of the problem variables
        """
        variables = {}
        if self.objective:
            variables.update(self.objective)
        for c in self.constraints.itervalues():
            variables.update(c)
        for p in sorted(self.relaxation.keys()):
            for c in self.relaxation[p].constraints.itervalues():
                variables.update(c)
        variables = list(variables)
        variables = sorted(variables, key=lambda variable: variable.name)
        
        return variables

    def _varIdx(self):
        # construct dict mapping variable objects to indices
        return dict((v, i) for i, v in enumerate(self.variables()))

    def getObjectiveCoefficients(self):
        """
        Return objective coefficients for variables as a list
        """

        return [self.objective.get(v, 0.0) for v in self.variables()]

    def getMatrixData(self, problem=None):
        """
        Returns a tuple containing information to construct a
        CoinPackedMatrix: (rowOrdered, rowIndices, colIndices, elements, numnzs)
        """

        if problem is None:
            problem = self

        rowIndices = []
        colIndices = []
        elements = []

        _varIdx = self._varIdx()

        def _add(rowInd, colInd, value):
            rowIndices.append(rowInd)
            colIndices.append(colInd)
            elements.append(value)

        for i, constraint in enumerate(problem.constraints.values()):
            for var, coef in constraint.items():
                _add(i, _varIdx[var], coef)

        return (False, rowIndices, colIndices, elements, len(elements))

    def _getConstraintBounds(self, constraint):
        """
        Return the rhs bounds for a given constraint
        """

        if constraint.sense == pulp.LpConstraintLE:
            return -DecompInf, -constraint.constant
        elif constraint.sense == pulp.LpConstraintGE:
            return -constraint.constant, DecompInf,
        elif constraint.sense == pulp.LpConstraintEQ:
            return -constraint.constant, -constraint.constant

    def getRowNames(self, problem=None):
        """
        Returns a list of row names
        """
        if problem is None:
            problem = self

        names = []

        for n, c in problem.constraints.iteritems():
            if c.name:
                names.append(c.name)
            else:
                names.append(n)
                
        return names

    def getRowBounds(self, problem=None):
        """
        Returns a tuple containing information about row bounds
        """
        if problem is None:
            problem = self

        lbs = []
        ubs = []

        for constraint in problem.constraints.values():
            lower, upper = self._getConstraintBounds(constraint)
            lbs.append(lower)
            ubs.append(upper)

        return (lbs, ubs)

    def getColNames(self):
        """
        Returns a list of variable names
        """

        names = []

        for var in self.variables():
            names.append(var.name)
        return names

    def getColBounds(self):
        """
        Returns a tuple containing information about column bounds
        """

        lbs = []
        ubs = []

        for var in self.variables():
            lowBound = var.lowBound
            if lowBound is None:
                lowBound = -DecompInf
            upBound = var.upBound
            if upBound is None:
                upBound = DecompInf
            lbs.append(lowBound)
            ubs.append(upBound)
        return (lbs, ubs)

    def getIntegerVars(self):
        """
        Returns a list containing indices of integer variables
        """

        return [ i for i, v in enumerate(self.variables())
                 if v.cat == pulp.LpInteger ]
    
    def _makeSolution(self, sol):
        varIdx = self._varIdx()
        class Solution(object):
            def __init__(self, v):
                self.v = v
            def getValue(self, var): #DEPRECATED
                return self[var]
            def __getitem__(self,var):
                return self.v[varIdx[var]]
            def __repr__(self):
                rv = dict([(v, k) for k, v in varIdx.items()])
                return str(dict((rv[i], v) for i, v in enumerate(self.v) if v))

        return Solution(sol)

    def chooseBranchSet(self, solution_vector):

        if not self.branch_method:
            return None
        tup = self.branch_method(self, self._makeSolution(solution_vector))
        if tup is None:
            return None

        down_lb, down_ub, up_lb, up_ub = tup

        varIdx = self._varIdx()
        # transform var indices into var objects
        t = lambda t : [(varIdx[var], v) for var, v in t]

        return t(down_lb), t(down_ub), t(up_lb), t(up_ub)

    def getRelaxedAsList(self):
        return self.relaxation.values()

    def writeRelaxed(self, block, filename, mip = 1):
        """
        Write the given block into a .lp file.
        
        This function writes the specifications (NO objective function,
        constraints, variables) of the defined Lp problem to a file.
        
        Inputs:
            - block -- the key to the block to write
            - filename -- the name of the file to be created.          
                
        Side Effects:
            - The file is created.
        """
        relaxation = self.relaxation.values()[block]
        f = file(filename, "w")
        f.write("\\* "+relaxation.name+" *\\\n")
        f.write("Subject To\n")
        ks = relaxation.constraints.keys()
        ks.sort()
        for k in ks:
            f.write(relaxation.constraints[k].asCplexLpConstraint(k))
        vs = relaxation.variables()
        vs.sort()
        # Bounds on non-"positive" variables
        # Note: XPRESS and CPLEX do not interpret integer variables without 
        # explicit bounds
        if mip:
            vg = [v for v in vs if not (v.isPositive() and \
                                        v.cat == pulp.LpContinuous) \
                and not v.isBinary()]
        else:
            vg = [v for v in vs if not v.isPositive()]
        if vg:
            f.write("Bounds\n")
            for v in vg:
                f.write("%s\n" % v.asCplexLpVariable())
        # Integer non-binary variables
        if mip:
            vg = [v for v in vs if v.cat == pulp.LpInteger and \
                                   not v.isBinary()]
            if vg:
                f.write("Generals\n")
                for v in vg: f.write("%s\n" % v.name)
            # Binary variables
            vg = [v for v in vs if v.isBinary()]
            if vg:
                f.write("Binaries\n")
                for v in vg: f.write("%s\n" % v.name)
        f.write("End\n")
        f.close()
        
    def solveRelaxed(self, whichBlock, redCostX, convexDual):
        """
        whichBlock integer
        redCostX list of floats
        convexDual float
        varList list
        """

        block = self.relaxation.keys()[whichBlock]
        if not self.relaxed_solver:
            return None

        # transform redCostX into a dictionary indexed by variable
        # TODO: lazy evaluate?
        varsRC = dict((var, redCostX[i]) for i, var in enumerate(self.variables()))

        dvars = self.relaxed_solver(self, block, varsRC, convexDual)
        if not dvars:
            return None

        # need to return a list of tuples, where each tuple is of the form:
        # (var_idx_list, value_list, rc, cost)
        varIdx = self._varIdx()
        ret = []
        for dv in dvars:
            var_idx_list = [varIdx[var] for var, val in dv.var_values]
            value_list = [val for var, val in dv.var_values]
            ret.append((var_idx_list, value_list, dv.rc, dv.cost))
        return ret

    def isUserFeasible(self, sol, tol):
        """
        Called from C++
        """
        if not self.is_solution_feasible:
            return None

        return self.is_solution_feasible(self, self._makeSolution(sol))

    def generateCuts(self, sol):
        """
        Called from C++
        """
        if not self.generate_cuts:
            return None
        
        # should return list of LpConstraints
        cuts = self.generate_cuts(self, self._makeSolution(sol))
        if not cuts:
            return None

        # list of cuts, each cut is defined by a tuple of the form:
        # (lower_bound, upper_bound, list_of_indices, list_of_values)
        r = []
        varIdx = self._varIdx()
        for constraint in cuts:
            lower, upper = self._getConstraintBounds(constraint)
            indices = [varIdx[var] for var in constraint.keys()]
            values = constraint.values()
            r.append((lower, upper, indices, values))

        return r

    def solveHeuristics(self, xhat, cost):
        """
        xhat list of floats
        cost list of floats
        solList list
        """

        if not self.heuristics:
            return None

        # transform xhat and cost into dictionaries indexed by variable
        # TODO: lazy evaluate?
        varsXHat = dict((var, xhat[i]) for i, var in enumerate(self.variables()))
        varsCost = dict((var, cost[i]) for i, var in enumerate(self.variables()))

        sols = self.heuristics(self, varsXHat, varsCost)
        if not sols:
            return None

        # need to return a list of tuples, where each tuple is of the form:
        # (var_idx_list, value_list)
        varIdx = self._varIdx()
        ret = []
        for sol in sols:
            indices = [varIdx[var] for var in sol.keys()]
            values = sol.values()
            ret.append((indices, values))
        return ret

    def generateInitVars(self):
        """
        varList list
        """

        if not self.init_vars:
            return None

        bvs = self.init_vars(self)
        if not bvs:
            return None

        # need to return a list of tuples, where each tuple is of the form:
        # (block, (var_idx_list, value_list, cost))
        varIdx = self._varIdx()
        ret = []
        for bv in bvs:
            var_idx_list = [varIdx[var] for var, val in bv[1].var_values]
            value_list = [val for var, val in bv[1].var_values]
            ret.append((self.relaxation.keys().index(bv[0]), (var_idx_list, value_list, bv[1].cost)))
        return ret

class DecompVar(object):
    def __init__(self, var_values, rc, cost):
        self.var_values = var_values
        self.rc = rc
        self.cost = cost

class RelaxationCollection(object):
    """
    A simple defaultdict for holding relaxation problems
    """
    PROBLEM_CLASS = pulp.LpProblem

    def __init__(self, parent):
        self.parent = parent
        self.dict = {}

    def __getitem__(self, name):
        if name not in self.dict:
            self.dict[name] = self.PROBLEM_CLASS()
        return self.dict[name]

    def __setitem__(self, name, value):
        self.dict[name] = value

    def keys(self):
        return self.dict.keys()

    def values(self):
        return self.dict.values()



