def satisfies_all_constraints(a, b, c, d, e):
    """
    Returns True if (a, b, c, d, e) satisfies constraints C1..C4.
    """
    # C1: 8 <= 2A + 2B + 2D + 3E <= 10
    lhs1 = 2*a + 2*b + 2*d + 3*e
    if not (8 <= lhs1 <= 10):
        return False

    # C2: 3 <= A + C <= 4
    lhs2 = a + c
    if not (3 <= lhs2 <= 4):
        return False

    # C3: 2 <= A + B + 2C <= 5
    lhs3 = a + b + 2*c
    if not (2 <= lhs3 <= 5):
        return False

    # C4: 1 <= B <= 2
    if not (1 <= b <= 2):
        return False

    return True


def solve_csp():
    # Original domains
    A_domain = [0, 1, 2, 3, 4]
    B_domain = [0, 1, 2, 3, 4]  # will prune by constraint 4
    C_domain = [0, 1, 2, 3]
    D_domain = [0, 1, 2, 3, 4, 5]
    E_domain = [0, 1, 2, 3, 4, 5, 6]

    solutions = []
    for a in A_domain:
        for b in B_domain:
            # Constraint 4 immediate prune
            if b < 1 or b > 2:
                continue
            for c in C_domain:
                for d in D_domain:
                    for e in E_domain:
                        if satisfies_all_constraints(a, b, c, d, e):
                            solutions.append((a, b, c, d, e))

    # Extract pruned domains
    A_pruned = set()
    B_pruned = set()
    C_pruned = set()
    D_pruned = set()
    E_pruned = set()

    for (a, b, c, d, e) in solutions:
        A_pruned.add(a)
        B_pruned.add(b)
        C_pruned.add(c)
        D_pruned.add(d)
        E_pruned.add(e)

    return {
        'solutions': solutions,
        'pruned_domains': {
            'A': sorted(A_pruned),
            'B': sorted(B_pruned),
            'C': sorted(C_pruned),
            'D': sorted(D_pruned),
            'E': sorted(E_pruned)
        }
    }


if __name__ == "__main__":
    result = solve_csp()
    print("All consistent solutions:")
    for sol in result['solutions']:
        print(sol)
    print("\nPruned domains after enforcing k=4 consistency:")
    for var, dom in result['pruned_domains'].items():
        print(f"{var}: {dom}")
