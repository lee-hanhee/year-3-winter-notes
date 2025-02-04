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
        return True
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
    """Identifies which variables a given constraint depends on."""
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
    
def value_has_support(var, val, domains, constraint):
    """
    Checks if 'var=val' has support in at least one assignment that satisfies 'constraint'.
    """
    # Fix var=val in a partial assignment
    partial = {var: val}

    # Find other variables in the constraint
    needed_vars = needed_by_constraint(constraint)
    other_vars = [v for v in needed_vars if v != var]

    # If no other variables, it's a unary constraint (e.g., 1 <= B <= 2)
    if not other_vars:
        return constraint(partial)

    # Try all combinations of values for the other variables
    for assignment_tuple in itertools.product(*[domains[v] for v in other_vars]):
        trial = dict(partial)  # Start with var=val
        for ov, av in zip(other_vars, assignment_tuple):
            trial[ov] = av  # Assign values to other variables
        
        # If constraint holds for this assignment, var=val has support
        if constraint(trial):
            return True

    return False  # No support found

###############################################################################
# 2. AC-3 Algorithm (2-Consistency)
###############################################################################

def ac3(domains):
    """
    Implements the AC-3 algorithm to enforce arc consistency (2-consistency).
    """
    queue = deque()
    
    for c in CONSTRAINTS:
        vars_in_c = needed_by_constraint(c)
        for var in vars_in_c:
            queue.append((var, c))

    while queue:
        var, constraint = queue.popleft()
        to_remove = set()
        
        for val in domains[var]:
            if not value_has_support(var, val, domains, constraint):
                to_remove.add(val)

        if to_remove:
            domains[var] -= to_remove
            for neighbor in needed_by_constraint(constraint):
                if neighbor != var:
                    queue.append((neighbor, constraint))

    return domains

###############################################################################
# 3. Enforce 3-Consistency
###############################################################################

def enforce_3_consistency(domains):
    """
    Enforces 3-consistency by ensuring that for every pair of variables (X, Y),
    there exists a value for a third variable (Z) that satisfies all constraints.
    """
    changed = True
    while changed:
        changed = False
        
        for X, Y, Z in itertools.combinations(VARIABLES, 3):
            for x in list(domains[X]):
                for y in list(domains[Y]):
                    found_support = False
                    
                    for z in domains[Z]:
                        assignment = {X: x, Y: y, Z: z}
                        if all_constraints_satisfied(assignment):
                            found_support = True
                            break
                    
                    if not found_support:
                        domains[X].discard(x)
                        changed = True
                        break

    return domains

###############################################################################
# 4. Finding All Valid Solutions (Backtracking)
###############################################################################

def all_valid_solutions(domains):
    """
    Finds all valid solutions after enforcing AC-3 and 3-consistency.
    """
    solutions = []
    vars_ = list(VARIABLES)

    def backtrack(index, assignment):
        if index == len(vars_):
            if all_constraints_satisfied(assignment):
                solutions.append(dict(assignment))
            return
        
        var = vars_[index]
        for value in sorted(domains[var]):  
            assignment[var] = value
            if all_constraints_satisfied(assignment):
                backtrack(index + 1, assignment)
            del assignment[var]

    backtrack(0, {})
    return solutions

def all_constraints_satisfied(assignment):
    """Returns True if 'assignment' satisfies all constraints."""
    return all(c(assignment) for c in CONSTRAINTS)

###############################################################################
# 5. Run the Algorithm
###############################################################################

if __name__ == "__main__":
    # Initialize domains
    domains = initial_domains()

    print("Initial domains:")
    for var in VARIABLES:
        print(f"{var}: {sorted(domains[var])}")
    print()

    # Apply AC-3 (2-consistency)
    pruned_domains = ac3(domains)

    print("Domains after AC-3 enforcement:")
    for var in VARIABLES:
        print(f"{var}: {sorted(pruned_domains[var])}")

    # Apply 3-consistency
    pruned_domains = enforce_3_consistency(pruned_domains)

    print("\nDomains after 3-consistency enforcement:")
    for var in VARIABLES:
        print(f"{var}: {sorted(pruned_domains[var])}")

    print("\nFinding all valid solutions...")

    # Find all valid solutions
    solutions = all_valid_solutions(pruned_domains)

    # Print all valid solutions
    print(f"\nNumber of valid solutions: {len(solutions)}")
    for i, sol in enumerate(solutions, start=1):
        print(f"Solution {i}: {sol}")

    print("\nAC-3, 3-Consistency, and Backtracking Completed.")
