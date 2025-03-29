def hmm_forward_backward():
    """
    Computes the normalized forward and backward variables (hat(alpha), hat(beta))
    for a 2-state HMM, then finds the posterior probabilities gamma(n, i).
    Finally, determines argmax_z P(Z2=z | X1..X4).
    """

    # ------------------
    # 1. Setup HMM parameters
    # ------------------
    import numpy as np

    # States: 0 and 1
    # Transition probabilities:
    P = np.array([
        [0.9, 0.1],  # from state 0 to (0,1)
        [0.2, 0.8]   # from state 1 to (0,1)
    ])

    # Emission probabilities: P(Xn = x | Zn = i)
    #   if x == i, prob=0.9; else prob=0.1.
    def emission_prob(state, obs):
        return 0.9 if (state == obs) else 0.1

    # Initial distribution
    pi = np.array([0.5, 0.5])

    # Observation sequence
    observations = [0, 1, 0, 1]  # X1=0, X2=1, X3=0, X4=1
    T = len(observations)        # T=4
    num_states = 2               # {0,1}

    # ------------------
    # 2. Forward pass (compute alpha_hat)
    #    We also keep track of a scaling factor c_n at each time n
    # ------------------
    alpha_hat = np.zeros((T, num_states))  # alpha_hat[n, i]
    c = np.zeros(T)                        # scaling factors

    # -- Initialization (n=0 in 0-based indexing)
    for i in range(num_states):
        alpha_hat[0, i] = pi[i] * emission_prob(i, observations[0])
    # scale
    c[0] = np.sum(alpha_hat[0, :])
    alpha_hat[0, :] /= c[0]

    # -- Recursion
    for n in range(1, T):
        for j in range(num_states):
            # sum over previous states
            sum_val = 0.0
            for i in range(num_states):
                sum_val += alpha_hat[n-1, i] * P[i, j]
            alpha_hat[n, j] = sum_val * emission_prob(j, observations[n])

        # scale
        c[n] = np.sum(alpha_hat[n, :])
        alpha_hat[n, :] /= c[n]

    # ------------------
    # 3. Backward pass (compute beta_hat)
    #    Use the same scaling factors c[n] for consistency
    # ------------------
    beta_hat = np.zeros((T, num_states))  # beta_hat[n, i]

    # -- Initialization: beta_T(i) = 1 after scaling
    beta_hat[T-1, :] = 1.0

    # -- Backward recursion
    for n in range(T-2, -1, -1):
        for i in range(num_states):
            sum_val = 0.0
            for j in range(num_states):
                sum_val += P[i, j] * emission_prob(j, observations[n+1]) * beta_hat[n+1, j]
            beta_hat[n, i] = sum_val
        # scale by the same factor c[n]
        beta_hat[n, :] /= c[n]

    # ------------------
    # 4. Posterior Probabilities gamma(n, i)
    #    gamma(n, i) = alpha_hat[n, i] * beta_hat[n, i]
    #    (already scaled so that sum_i gamma(n, i) = 1)
    # ------------------
    gamma = alpha_hat * beta_hat

    # normalize each time-slice for numerical safety (though it should already sum to 1)
    for n in range(T):
        gamma_sum = np.sum(gamma[n, :])
        gamma[n, :] /= gamma_sum

    # ------------------
    # 5. Display results clearly
    # ------------------    
    print("\nalphaHat[time][state]")
    for n in range(T):
        print(f"alphaHat[{n+1}] = {alpha_hat[n, :]}")

    print("\nbetaHat[time][state]")
    for n in range(T):
        print(f"betaHat[{n+1}] = {beta_hat[n, :]}")

    print("\ngamma[time][state]")
    for n in range(T):
        print(f"gamma[{n+1}] = {gamma[n, :]}")

    # ------------------
    # 6. Most likely state at n=2
    #    index n=1 in 0-based => time step 2 in 1-based
    # ------------------
    argmax_state_n2 = np.argmax(gamma[1, :])  # n=1 => time=2
    print(f"\nMost probable state for n=2 is: {argmax_state_n2}")

# Run the code
if __name__ == "__main__":
    hmm_forward_backward()
