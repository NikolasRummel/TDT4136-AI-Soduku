from typing import Any
from collections import deque
import time


class CSP:
    def __init__(
        self,
        variables: list[str],
        domains: dict[str, set],
        edges: list[tuple[str, str]],
    ):
        """Constructs a CSP instance with the given variables, domains and edges.
        
        Parameters
        ----------
        variables : list[str]
            The variables for the CSP
        domains : dict[str, set]
            The domains of the variables
        edges : list[tuple[str, str]]
            Pairs of variables that must not be assigned the same value
        """
        self.variables = variables
        self.domains = domains


        ## Init values for benchmark
        self.backtrack_calls = 0
        self.backtrack_failures = 0
        self.backtrack_runtime = 0.0

        # Binary constraints as a dictionary mapping variable pairs to a set of value pairs.
        #
        # To check if variable1=value1, variable2=value2 is in violation of a binary constraint:
        # if (
        #     (variable1, variable2) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable1, variable2)]
        # ) or (
        #     (variable2, variable1) in self.binary_constraints and
        #     (value1, value2) not in self.binary_constraints[(variable2, variable1)]
        # ):
        #     Violates a binary constraint
        self.binary_constraints: dict[tuple[str, str], set] = {}
        for variable1, variable2 in edges:
            self.binary_constraints[(variable1, variable2)] = set()
            for value1 in self.domains[variable1]:
                for value2 in self.domains[variable2]:
                    if value1 != value2:
                        self.binary_constraints[(variable1, variable2)].add((value1, value2))
                        self.binary_constraints[(variable1, variable2)].add((value2, value1))

    def ac_3(self) -> bool:
        """Performs AC-3 on the CSP.
        Meant to be run prior to calling backtracking_search() to reduce the search for some problems.
        
        Returns
        -------
        bool
            False if a domain becomes empty, otherwise True
        """
        start = time.time()

        def allowed_pairs(a: str, b: str) -> set:
            if (a, b) in self.binary_constraints:
                return self.binary_constraints[(a, b)]
            if (b, a) in self.binary_constraints:
                return self.binary_constraints[(b, a)]
            return set()

        def revise(Xi, Xj): 
            revised = False
            Di = list(self.domains[Xi])
            for x in Di:
                allowed = False
                Dj = list(self.domains[Xj])
                for y in Dj:
                    if(x,y) in allowed_pairs(Xi, Xj):
                        allowed = True
                        break

                if not allowed:
                    self.domains[Xi].remove(x)
                    revised = True

            return revised  


        def neighbors(X: str) -> set:
            neighbors = set()
            for (a, b) in list(self.binary_constraints.keys()):
                if a == X:
                    neighbors.add(b)
                if b == X:
                    neighbors.add(a)
            return neighbors 

        queue = deque()
        
        for (xi, xj) in list(self.binary_constraints.keys()):
            queue.append((xi, xj))
            queue.append((xj, xi))

        
        while queue:
            Xi, Xj = queue.popleft()
            if revise(Xi, Xj):
                Dj = list(self.domains[Xj])

                if len(Dj) == 0:
                    return False
                
                for Xk in neighbors(Xi):
                    if Xk == Xj: 
                        continue
                    queue.append((Xk, Xi))  
        
        self.ac3_runtime = time.time() - start
        self.domains_after_ac3 = {v: set(self.domains[v]) for v in self.variables}
        return True        


    def backtracking_search(self) -> None | dict[str, Any]:
        """Performs backtracking search on the CSP.
        
        Returns
        -------
        None | dict[str, Any]
            A solution if any exists, otherwise None
        """
        def select_unassigned_variable(assignment): 
            unassigned = [v for v in self.variables if v not in assignment]

            # Choosing by smallest domain:
            best = unassigned[0]
            min_domain = len(self.domains[best])

            for curr in unassigned:
                curr_domain = len(self.domains[curr])

                if curr_domain < min_domain:
                    min_domain = curr_domain
                    best = curr
            return best
        

        def order_domain_values(var, assignment): # any order is fine was stated
            return list(self.domains[var])


        def is_consistent(var, value, assignment):
            for other_var, other_val in assignment.items():
                if (var, other_var) in self.binary_constraints:
                    if (value, other_val) not in self.binary_constraints[(var, other_var)]:
                        return False
                elif (other_var, var) in self.binary_constraints:
                    if (value, other_val) not in self.binary_constraints[(other_var, var)]:
                        return False
            return True


        def backtrack(assignment: dict[str, Any]):
            self.backtrack_calls += 1

            if len(assignment) == len(self.variables): # every variable is has a assigment
                return assignment
            
            var = select_unassigned_variable(assignment)

            for value in order_domain_values(var, assignment):
                if is_consistent(var, value, assignment):
                    assignment[var] = value
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]

            self.backtrack_failures +=1
            return None       
        start = time.time()
        result = backtrack({})
        self.backtrack_runtime = time.time() - start
        return result


def alldiff(variables: list[str]) -> list[tuple[str, str]]:
    """Returns a list of edges interconnecting all of the input variables
    
    Parameters
    ----------
    variables : list[str]
        The variables that all must be different

    Returns
    -------
    list[tuple[str, str]]
        List of edges in the form (a, b)
    """
    return [(variables[i], variables[j]) for i in range(len(variables) - 1) for j in range(i + 1, len(variables))]
