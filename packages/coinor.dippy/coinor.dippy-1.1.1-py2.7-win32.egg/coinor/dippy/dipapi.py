"""
How to use this file:

from _dippy import *

_Solve = Solve
def Solve(prob, params=None):
  # Set up prob here, must have DipAPI as a base class

  # call the Solve method from _dippy
  try:
    solList, dualList = _Solve(prob, processed)
    # solList  is a list of (col_name, value) pairs
    # dualList is a list of (row_name, value) pairs
  except:
    print "Error returned from _dippy"
    raise
"""

class DipAPIError(Exception):
  """
  DipAPI Exception
  """
  pass

class DipAPI(object):

  def getObjectiveCoefficients(self):
    """
    Return non-zero objective coefficients for variables as a dictionary
    """
    raise DipAPIError("Bad function definition, DipAPI.getObjectiveCoefficients must be overwritten")

  def getMatrixData(self, problem=None):
    """
    Returns a list of dictionaries that contain rows
    """
    raise DipAPIError("Bad function definition, DipAPI.getMatrixData must be overwritten")

  def getRowNames(self, problem=None):
    """
    Returns a list of row names
    """
    raise DipAPIError("Bad function definition, DipAPI.getRowNames must be overwritten")

  def getRowBounds(self, problem=None):
    """
    Returns a 2-tuple containing dictionaries of row bounds
    """
    raise DipAPIError("Bad function definition, DipAPI.getRowBounds must be overwritten")

  def getColNames(self):
    """
    Returns a list of variable names
    """
    raise DipAPIError("Bad function definition, DipAPI.getColNames must be overwritten")

  def getColBounds(self):
    """
    Returns a 2-tuple containing dictionaries of column bounds
    """
    raise DipAPIError("Bad function definition, DipAPI.getColBounds must be overwritten")

  def getIntegerVars(self):
    """
    Returns a list containing names of integer variables
    """
    raise DipAPIError("Bad function definition, DipAPI.getIntegerVars must be overwritten")

  def getMasterAsTuple(self):
    """
    Returns all the master problem data as a tuple of other
    "data gathering" functions
    """
    raise DipAPIError("Bad function definition, DipAPI.getMasterAsTuple must be overwritten")

  def getRelaxAsTuple(self, prob):
    """
    Returns the constraint matrix and row bounds (=rhs) for
    a relaxed problem
    """
    raise DipAPIError("Bad function definition, DipAPI.getRelaxAsTuple must be overwritten")

  def chooseBranchSet(self, xhat):
    """
    Finds the best branch for a fractional solution

    Inputs:
    xhat (list of (name, value) tuples) = list of solution values for all variables

    Output:
    down_lb, down_ub, up_lb, up_ub (tuple of lists of (name, value) tuples) =
    lower and upper bounds for down branch, lower and upper bounds for up branch
    """
    raise DipAPIError("Bad function definition, DipAPI.chooseBranchSet must be overwritten")

  def solveRelaxed(self, whichBlock, redCostX, convexDual):
    """
    Returns solutions to the whichBlock relaxed subproblem

    Inputs:  
    whichBlock (integer) = index of relaxed subproblem to be solved
    redCostX (list of (name, value) tuples) = list of reduced costs for all variables
    convexDual (float) = dual for convexity constraint for this relaxed subproblem

    Output:
    varList (list of (cost, reduced cost, list of (name, value) tuples)) =
    solutions for this relaxed subproblem expressed as a cost, reduced cost and
    list of non-zero values for variables
    """
    raise DipAPIError("Bad function definition, DipAPI.solveRelaxed must be overwritten")

  def isUserFeasible(self, sol, tol):
    """
    Lets the user decide if an integer solution is really feasible

    Inputs:
    sol (list of (name, value) tuples) = list of solution values for all variables
    tol (double) = zero tolerance

    Outputs:
    (boolean) = false if not feasible (generate cuts) or true if feasible
    """
    raise DipAPIError("Bad function definition, DipAPI.isUserFeasible must be overwritten")

  def generateCuts(self, xhat):
    """
    Lets the user generate cuts to remove fractional "pieces" of xhat

    Inputs:
    sol (list of (name, value) tuples) = list of solution values for all variables

    Output:
    cutList (list of (name, value) tuples), lower bound, upper bound) =
    cuts for this fractional solution expressed as a list of non-zero values
    for variables, lower bound and upper bound
    """
    raise DipAPIError("Bad function definition, DipAPI.generateCuts must be overwritten")

  def solveHeuristics(self, xhat, costX):
    """
    Lets the user generate (heuristic) solutions from a fractional solution

    Inputs:
    xhat  (list of (name, value) tuples) = list of solution values for all variables
    costX (list of (name, value) tuples) = list of costs for all variables

    Outputs:
    solList (list of (name, value) lists) =
    solutions found from this fractional solution expressed as a
    list of non-zero values for variables
    """
    raise DipAPIError("Bad function definition, DipAPI.solveHeuristics must be overwritten")

  def generateInitVars(self):
    """
    Returns initial solutions to relaxed subproblems

    Inputs:
    None

    Output:
    varList (list of (subproblem_index, (cost, list of (name, value) tuples))) =
    initial solutions for the relaxed subproblems expressed as a cost and
    list of non-zero values for variables
    """
    raise DipAPIError("Bad function definition, DipAPI.generateInitVars must be overwritten")
