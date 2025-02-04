from collections import deque
import itertools

###############################################################################
# 1. Problem Setup: Variables, Domains, and Constraints
###############################################################################

# Define variables
VARIABLES = ["A", "B", "C", "D", "E"]

# Define initial domains
def initial_domains():
    return {
        "A": set([0, 1, 2, 3, 4]),
        "B": set([0, 1, 2, 3, 4]),
        "C": set([0, 1, 2, 3]),
        "D": set([0, 1, 2, 3, 4, 5]),
        "E": set([0, 1, 2, 3, 4, 5, 6]),
    }

# Define constraints
def constraint_C1(assignment):
    """8 <= 2A + 2B + 2D + 3E <= 10"""
    needed = ["A", "B", "D", "E"]
    if not all(v in assignment for v in needed):
        return True  # Can't evaluate fully => not violated yet
    A, B, D, E = assignment["A"], assignment["B"], assignment["D"], assignment["E"]
    return 8 <= 2*A + 2*B + 2*D + 3*E <= 10

def constraint_C2(assignment):
    """3 <= A + C <= 4"""
    needed = ["A", "C"]
    if not all(v in assignment for v in needed):
        return True
    A, C = assignment["A"], assignment["C"]
    return 3 <= A + C <= 4

def constraint_C3(assignment):
    """2 <= A + B + 2C <= 5"""
    needed = ["A", "B", "C"]
    if not all(v in assignment for v in needed):
        return True
    A, B, C = assignment["A"], assignment["B"], assignment["C"]
    return 2 <= A + B + 2*C <= 5

def constraint_C4(assignment):
    """1 <= B <= 2 (Unary Constraint)"""
    needed = ["B"]
    if not all(v in assignment for v in needed):
        return True
    B = assignment["B"]
    return 1 <= B <= 2

# List of all constraints
CONSTRAINTS = [constraint_C1, constraint_C2, constraint_C3, constraint_C4]

# Function to get variables involved in a constraint
def needed_by_constraint(c):
    """
    Identifies which variables a given constraint function depends on.
    """
    if c == constraint_C1:
        return ["A", "B", "D", "E"]
    elif c == constraint_C2:
        return ["A", "C"]
    elif c == constraint_C3:
        return ["A", "B", "C"]
    elif c == constraint_C4:
        return ["B"]
    else:
        return []

###############################################################################
# 2. AC-3 Algorithm (Arc Consistency)
###############################################################################

def ac3(domains):
    """
    Implements the AC-3 algorithm to enforce arc consistency.
    It maintains a queue of arcs (variable, constraint) and removes values
    that have no supporting assignments.
    """
    queue = deque()
    
    # Initialize queue with all arcs (X, C) where C is a constraint involving X
    for c in CONSTRAINTS:
        vars_in_c = needed_by_constraint(c)
        for var in vars_in_c:
            queue.append((var, c))

    while queue:
        var, constraint = queue.popleft()
        to_remove = set()
        
        # Check each value in the domain of `var`
        for val in domains[var]:
            if not value_has_support(var, val, domains, constraint):
                to_remove.add(val)

        # If values were removed, update domains and recheck affected variables
        if to_remove:
            domains[var] -= to_remove
            for neighbor in needed_by_constraint(constraint):
                if neighbor != var:
                    queue.append((neighbor, constraint))  # Re-check this neighbor

    return domains

###############################################################################
# 3. Support Check Function
###############################################################################

def value_has_support(var, val, domains, constraint):
    """
    Checks if 'var=val' has support in at least one assignment that satisfies 'constraint'.
    """
    # Fix var=val in a partial assignment
    partial = {var: val}

    # Find other variables in the constraint
    needed_vars = needed_by_constraint(constraint)
    other_vars = [v for v in needed_vars if v != var]

    # Try all combinations of values for the other variables
    for assignment_tuple in itertools.product(*[domains[v] for v in other_vars]):
        trial = dict(partial)
        for ov, av in zip(other_vars, assignment_tuple):
            trial[ov] = av
        # If constraint holds for this assignment, var=val has support
        if constraint(trial):
            return True

    return False

###############################################################################
# 4. Run the AC-3 Algorithm and Print Results
###############################################################################

if __name__ == "__main__":
    # Initialize domains
    domains = initial_domains()

    print("Initial domains:")
    for var in VARIABLES:
        print(f"{var}: {sorted(domains[var])}")
    print()

    # Apply AC-3
    pruned_domains = ac3(domains)

    print("Domains after AC-3 enforcement:")
    for var in VARIABLES:
        print(f"{var}: {sorted(pruned_domains[var])}")

    print("\nAC-3 Algorithm Finished.")
