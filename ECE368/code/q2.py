import numpy as np

def hmm_q2():
    """
    Solve Q2(a) and Q2(b) for the 4-state HMM:
      - Q2(a): Most likely single state at n=2.
      - Q2(b): Viterbi path (Z1, Z2, Z3).
    Using:
      Transition matrix P,
      Emission probabilities P(X|Z),
      Initial distribution pi,
      Observations (X1, X2, X3) = (3, 0, 3).
    """

    # ----------------------
    # 1. Define HMM parameters
    # ----------------------
    # States = {0, 1, 2, 3}
    P = np.array([
        [0.0,  0.5, 0.0,  0.5],  # from state 0
        [0.0,  1.0, 0.0,  0.0],  # from state 1
        [0.0,  0.5, 0.5,  0.0],  # from state 2
        [0.5,  0.0, 0.5,  0.0]   # from state 3
    ])
    pi = np.array([0.25, 0.0, 0.25, 0.5])  # initial distribution

    # Emission probabilities table: P(X=x | Z=z)
    #   Rows: z in [0..3], Columns: x in [0..3].
    emission_table = np.array([
        [0.5,  0.25, 0.0,  0.25],  # z=0
        [0.25, 0.5,  0.25, 0.0 ],  # z=1
        [0.0,  0.25, 0.5,  0.25],  # z=2
        [0.25, 0.0,  0.25, 0.5 ]   # z=3
    ])

    def emission_prob(z, x):
        return emission_table[z, x]

    observations = [3, 0, 3]  # X1=3, X2=0, X3=3
    T = len(observations)     # T=3
    num_states = 4

    # ----------------------------------------------------------------
    # Q2(a) Most likely single state Z2 by forward-backward smoothing
    # ----------------------------------------------------------------

    # ---- Forward pass (alpha-hat) with scaling ----
    alpha = np.zeros((T, num_states))  # raw forward
    c = np.zeros(T)                    # scaling factors

    # Initialization
    for z in range(num_states):
        alpha[0, z] = pi[z] * emission_prob(z, observations[0])
    c[0] = np.sum(alpha[0, :])
    alpha[0, :] /= c[0]

    # Forward recursion
    for t in range(1, T):
        for j in range(num_states):
            s = 0.0
            for i in range(num_states):
                s += alpha[t-1, i] * P[i, j]
            alpha[t, j] = s * emission_prob(j, observations[t])
        c[t] = np.sum(alpha[t, :])
        alpha[t, :] /= c[t]

    # ---- Backward pass (beta-hat) with same scaling ----
    beta = np.zeros((T, num_states))

    # Initialization
    beta[T-1, :] = 1.0 

    # Backward recursion
    for t in range(T-2, -1, -1):
        for i in range(num_states):
            s = 0.0
            for j in range(num_states):
                s += P[i, j] * emission_prob(j, observations[t+1]) * beta[t+1, j]
            beta[t, i] = s / c[t]

    # ---- Posterior smoothed probabilities gamma(t,z) ----
    gamma = alpha * beta
    # Normalize (should already be near 1)
    for t in range(T):
        gamma_sum = np.sum(gamma[t, :])
        gamma[t, :] /= gamma_sum

    # Most likely single state at t=1 (i.e. time n=2 in 1-based indexing)
    z2_star = np.argmax(gamma[1, :])

    # ----------------------------------------------------------------
    # Q2(b) Viterbi path: (Z1, Z2, Z3)
    # ----------------------------------------------------------------
    # We'll store log(probabilities) to avoid underflow
    logP = np.log(P + 1e-15)  # small offset to avoid log(0)
    logE = np.log(emission_table + 1e-15)
    log_pi = np.log(pi + 1e-15)

    # Viterbi arrays
    w = np.zeros((T, num_states))      # w[t, j] = max log-prob of path ending in j
    psi = np.zeros((T, num_states), dtype=int)  # backpointer

    # Initialize (t=0)
    for j in range(num_states):
        w[0, j] = log_pi[j] + logE[j, observations[0]]
        psi[0, j] = j  # self-pointer initially

    # Recursion
    for t in range(1, T):
        for j in range(num_states):
            # pick i that maximizes w[t-1, i] + logP[i,j]
            candidates = w[t-1, :] + logP[:, j]
            best_i = np.argmax(candidates)
            w[t, j] = candidates[best_i] + logE[j, observations[t]]
            psi[t, j] = best_i

    # Backtrack
    zhat = np.zeros(T, dtype=int)
    zhat[T-1] = np.argmax(w[T-1, :])  # final state
    for t in range(T-2, -1, -1):
        zhat[t] = psi[t+1, zhat[t+1]]

    # ----------------------------------------------------------------
    # Print results
    # ----------------------------------------------------------------
    print("\nc[time]")
    for n in range(T):
        print(f"c[{n+1}] = {c[n]}")
        
    print("\nalphaHa[time][state]")
    for n in range(T):
        print(f"alpha_hat[{n+1}] = {alpha[n, :]}")

    print("\nbetaHat[time][state]")
    for n in range(T):
        print(f"beta_hat[{n+1}] = {beta[n, :]}")
        
    print("\ngamma[time][state]")
    print(f"gamma[{1+1}] = {gamma[1, :]}")
        
    print(f"Most likely state for n=2 is z2* = {z2_star}")
    
    print("\nw[time][state]")
    for n in range(T):
        print(f"w[{n+1}] = {w[n, :]}")
    
    print("\npsi[time][state]")
    for n in range(T):
        print(f"psi[{n+1}] = {psi[n, :]}")

    print(f"Most likely sequence for (Z1, Z2, Z3) = {zhat.tolist()}")

# Run the solver
if __name__ == "__main__":
    hmm_q2()
