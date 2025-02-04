import itertools

###############################################################################
# 0. CSP Setup
###############################################################################

VARIABLES = ["A", "B", "C", "D", "E"]

# Initial domains
def initial_domains():
    return {
        "A": set([0, 1, 2, 3, 4]),
        "B": set([0, 1, 2, 3, 4]),
        "C": set([0, 1, 2, 3]),
        "D": set([0, 1, 2, 3, 4, 5]),
        "E": set([0, 1, 2, 3, 4, 5, 6]),
    }

# Constraints:
# We'll store them in a list of functions that take a dict {var: val, ...}
# and return True/False if that partial or full assignment is consistent
def constraint_C1(assignment):
    """8 <= 2A + 2B + 2D + 3E <= 10"""
    # Only check if all needed variables are assigned
    needed = ["A","B","D","E"]
    if not all(v in assignment for v in needed):
        return True  # can't evaluate fully => not violated yet
    A, B, D, E = assignment["A"], assignment["B"], assignment["D"], assignment["E"]
    lhs = 2*A + 2*B + 2*D + 3*E
    return 8 <= lhs <= 10

def constraint_C2(assignment):
    """3 <= A + C <= 4"""
    needed = ["A","C"]
    if not all(v in assignment for v in needed):
        return True
    A, C = assignment["A"], assignment["C"]
    return 3 <= A + C <= 4

def constraint_C3(assignment):
    """2 <= A + B + 2C <= 5"""
    needed = ["A","B","C"]
    if not all(v in assignment for v in needed):
        return True
    A, B, C_ = assignment["A"], assignment["B"], assignment["C"]
    return 2 <= A + B + 2*C_ <= 5

def constraint_C4(assignment):
    """1 <= B <= 2"""
    needed = ["B"]
    if not all(v in assignment for v in needed):
        return True
    B = assignment["B"]
    return (1 <= B <= 2)

CONSTRAINTS = [
    constraint_C1,
    constraint_C2,
    constraint_C3,
    constraint_C4
]

def all_constraints_satisfied(partial_assign):
    """Returns True if 'partial_assign' does NOT violate any constraint,
       i.e., for each constraint, either it's not fully checkable yet,
       or it is satisfied."""
    for c in CONSTRAINTS:
        if not c(partial_assign):
            return False
    return True


###############################################################################
# 1. Enforce 1-consistency (Node consistency)
###############################################################################
def enforce_1_consistency(domains):
    """
    Prunes domain values that violate any unary constraints.
    In this CSP, constraint C4 imposes '1 <= B <= 2', effectively unary on B.
    """
    # We'll check which constraints are purely unary.
    # In practice, we see only C4 is effectively unary on B.
    # But let's do a general approach: If a constraint references exactly 1 variable,
    # we test each value for that variable.
    for c in CONSTRAINTS:
        # find which vars are needed
        # in a more advanced setup, we'd parse them from the function
        # but let's do it "by reflection" for demonstration:
        # We'll just see how many variables it tries to read:
        # For simplicity, we check known constraints. We'll handle C4 directly.
        pass

    # The only truly unary constraint here is 1 <= B <= 2.
    # So let's just enforce that directly.
    to_remove = set()
    for b_val in domains["B"]:
        # Test if partial assignment B=b_val violates C4
        part = {"B": b_val}
        if not constraint_C4(part):
            to_remove.add(b_val)
    # Prune them
    domains["B"] -= to_remove

    # No other strictly unary constraints in the problem (C1, C2, C3 are multi-var).
    return domains


###############################################################################
# 2. Enforce 2-consistency (Generalized Arc Consistency, GAC)
###############################################################################
def enforce_2_consistency(domains):
    """
    Standard GAC on n-ary constraints. Iteratively remove domain values
    that have no support in each constraint. Stop when stable.
    """
    changed = True
    while changed:
        changed = False
        # For each constraint, for each variable used by that constraint,
        # we check each value in var's domain to see if it is "supported".
        for var in VARIABLES:
            # We'll try to prune domain[var] by checking each value
            to_prune = []
            for val in domains[var]:
                # We want to see if there is *some* assignment to the other variables
                # that appear in each relevant constraint so that no constraint is violated.
                # That means: for each constraint that includes 'var',
                # we check if val is "supported" by the others.
                # We'll do a single overall check:
                if not value_has_support(var, val, domains):
                    to_prune.append(val)
            # If we found any domain values to prune, remove them
            if to_prune:
                changed = True
                for val in to_prune:
                    domains[var].remove(val)
    return domains

def value_has_support(var, val, domains):
    """
    Check if "var=val" can participate in at least one full assignment
    (to the variables in the same constraint) that does not violate any constraint
    referencing 'var'.
    
    In n-ary GAC, we must ensure that for *each* constraint that involves 'var',
    there exists some combination of the other variables in that constraint
    that satisfies the constraint.
    
    We'll do a simple approach: we try to see if we can pick ANY values
    from the other relevant variables' domains that make the constraint hold.
    If none is found, there's no support.
    
    Because constraints can overlap in variables, the safe approach is:
    - For every constraint c, if c references var,
      check if there's a way to assign the other variables of c from their domains
      so that c is satisfied. If for some constraint c, no such assignment exists,
      then "var=val" is not supported.
    
    Because the CSP is small, we'll do a brute-force search on the other variables
    used by c.
    """
    # Temporarily fix var=val
    partial = {var: val}

    # Check all constraints c that 'matter' to var
    for c in CONSTRAINTS:
        # We figure out which variables c actually depends on
        # We'll test them by name. A quick hack is to try assigning from
        # each domain and see if c is ever fully satisfied.
        # But let's see if c needs var. If not, skip.
        # A quick way: we'll call c with partial to see if c tries to read var;
        # but let's just do a direct check on known constraints:

        # We'll do a function to guess which variables c needs by scanning text
        # or we can do a simpler approach: each c is known:
        needed_vars = needed_by_constraint(c)

        if var not in needed_vars:
            # This constraint doesn't involve var => no conflict => skip
            continue

        # Now we check if there's at least one combination of the other variables
        # in needed_vars \ {var} that satisfies c together with var=val
        other_vars = [v for v in needed_vars if v != var]

        found_support = False
        for assignment_tuple in itertools.product(*[domains[v] for v in other_vars]):
            trial = dict(partial)
            for ov, av in zip(other_vars, assignment_tuple):
                trial[ov] = av
            # Now check if constraint c is satisfied by 'trial'
            if c(trial):
                found_support = True
                break

        if not found_support:
            # that means this constraint c provides NO support for var=val
            return False

    # If we never found a constraint that fails to support var=val, it's supported
    return True

def needed_by_constraint(c):
    """
    A small helper to identify which variables a given constraint function
    depends on. We'll do it by matching function names or docstrings, for demo.
    Real code might store them more systematically.
    """
    if c == constraint_C4:
        return ["B"]
    elif c == constraint_C2:
        return ["A","C"]
    elif c == constraint_C3:
        return ["A","B","C"]
    elif c == constraint_C1:
        return ["A","B","D","E"]
    else:
        return []


###############################################################################
# 3. Enforce 3-consistency
###############################################################################
def enforce_3_consistency(domains):
    """
    For each triple of variables (X,Y,Z), and each triple of values in their domains
    that is mutually consistent among themselves, check if it can be extended
    to the remaining 2 variables in some full assignment. If it cannot,
    then we remove that triple from feasibility. Practically, that means
    we prune at least one of the domain values from X, Y, or Z so that
    triple never occurs.
    
    Because it's simpler for demonstration, we do a brute-force approach:
     1. Collect all *full* solutions (consistent assignments).
     2. For every triple (X,Y,Z), for every combination (x,y,z) that is consistent
        with X,Y,Z constraints, check if (x,y,z) appears in *any* full solution
        in which X=x, Y=y, Z=z. If not, we prune x from dom(X), or y from dom(Y), etc.
        (At least one must go so that triple can't occur.)
    
    In a real solver, 3-consistency is done more incrementally. But this is simpler to show.
    """
    full_solutions = all_full_solutions(domains)
    if not full_solutions:
        # If there's no full solution, the domains are contradictory anyway
        # (or 2-consistency might have made them empty). We'll just return.
        return domains

    changed = True
    while changed:
        changed = False
        # For each triple of distinct variables
        for (X,Y,Z) in itertools.combinations(VARIABLES, 3):
            # We'll gather domain values in a list for iteration
            domX = list(domains[X])
            domY = list(domains[Y])
            domZ = list(domains[Z])

            for x in domX:
                for y in domY:
                    for z in domZ:
                        # Check if (X=x, Y=y, Z=z) is consistent among themselves
                        # i.e., it doesn't violate any constraint that only involves X,Y,Z
                        partial = {X:x, Y:y, Z:z}
                        if not all_constraints_satisfied(partial):
                            # It's already internally inconsistent => no immediate need to prune
                            # because 2-consistency or GAC might have removed them,
                            # but let's skip.
                            continue

                        # Now see if there's any full solution in which X=x, Y=y, Z=z
                        # among full_solutions
                        if not can_extend_triple(full_solutions, partial):
                            # That means (x,y,z) cannot be extended to a full solution
                            # => remove it
                            # Typically we remove from at least one domain.
                            # The simplest approach: remove x from X's domain.
                            # But strictly, any of x,y,z is invalid in combination.
                            # We'll do a simple approach: remove x from X's domain.
                            # Or you might remove all three. Different textbooks do it differently.
                            # We'll just remove x from X to forbid that triple.
                            domains[X].discard(x)
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

    return domains

def can_extend_triple(full_solutions, partial):
    """Check if there's a full solution in 'full_solutions' that agrees with 'partial'."""
    for sol in full_solutions:
        # 'sol' is a dict, e.g. {"A":2,"B":1,"C":1,"D":1,"E":0}
        if all(sol[v] == partial[v] for v in partial):
            return True
    return False


###############################################################################
# 4. Enforce 4-consistency
###############################################################################
def enforce_4_consistency(domains):
    """
    Similar brute-force approach for 4-consistency:
    For every quadruple (W,X,Y,Z), check if it extends to the 5th variable in any full solution.
    If not, prune. We'll do the same approach using 'all_full_solutions'.
    """
    full_solutions = all_full_solutions(domains)
    if not full_solutions:
        return domains

    changed = True
    while changed:
        changed = False
        for (V1,V2,V3,V4) in itertools.combinations(VARIABLES, 4):
            dom1 = list(domains[V1])
            dom2 = list(domains[V2])
            dom3 = list(domains[V3])
            dom4 = list(domains[V4])

            for x1 in dom1:
                for x2 in dom2:
                    for x3 in dom3:
                        for x4 in dom4:
                            partial = {V1:x1, V2:x2, V3:x3, V4:x4}
                            # Check if partial is self-consistent
                            if not all_constraints_satisfied(partial):
                                continue
                            # Check extension to the 5th variable
                            if not can_extend_quad(full_solutions, partial):
                                # Prune from one domain, for demo we remove x1 from V1
                                domains[V1].discard(x1)
                                changed = True
                                break
                        if changed:
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break

    return domains

def can_extend_quad(full_solutions, partial):
    """Check if there's a full solution that extends 'partial'."""
    for sol in full_solutions:
        match = True
        for v in partial:
            if sol[v] != partial[v]:
                match = False
                break
        if match:
            return True
    return False


###############################################################################
# Helper: Collect all full solutions from the current domains
# (i.e., brute force all domain combos and check constraints).
###############################################################################
def all_full_solutions(domains):
    """
    Return a list of all dict assignments {A:a, B:b, ...} that satisfy all constraints,
    using the current 'domains'.
    """
    vars_ = list(VARIABLES)
    all_solutions = []
    def backtrack(i, current):
        if i == len(vars_):
            # Check constraints
            if all_constraints_satisfied(current):
                all_solutions.append(dict(current))
            return
        v = vars_[i]
        for val in domains[v]:
            current[v] = val
            # If partial is still not violating constraints, continue
            if all_constraints_satisfied(current):
                backtrack(i+1, current)
        del current[v]

    backtrack(0, {})
    return all_solutions


###############################################################################
# Putting it all together in 'main'
###############################################################################
def main():
    # 0. Initialize the CSP
    dom = initial_domains()

    print("Initial domains:")
    for var in VARIABLES:
        print(f"{var}: {sorted(dom[var])}")
    print()

    # 1. Enforce 1-consistency
    dom = enforce_1_consistency(dom)
    print("After 1-consistency (node consistency):")
    for var in VARIABLES:
        print(f"{var}: {sorted(dom[var])}")
    print()

    # 2. Enforce 2-consistency (GAC)
    dom = enforce_2_consistency(dom)
    print("After 2-consistency (GAC):")
    for var in VARIABLES:
        print(f"{var}: {sorted(dom[var])}")
    print()

    # 3. Enforce 3-consistency
    dom = enforce_3_consistency(dom)
    print("After 3-consistency:")
    for var in VARIABLES:
        print(f"{var}: {sorted(dom[var])}")
    print()

    # 4. Enforce 4-consistency
    dom = enforce_4_consistency(dom)
    print("After 4-consistency:")
    for var in VARIABLES:
        print(f"{var}: {sorted(dom[var])}")
    print()

    # Collect all final solutions
    sols = all_full_solutions(dom)
    print(f"Number of full solutions with final domains = {len(sols)}")
    print("All solutions:")
    for s in sols:
        print(s)


if __name__ == "__main__":
    main()
