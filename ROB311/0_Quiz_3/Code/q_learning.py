# Form a bijection b/w state-space and subset of N.
# define the state constants
HUNGRY, RAW, RIPE, ROTTEN, FULL, DEAD = 0, 1, 2, 3, 4, 5
states = [HUNGRY, RAW, RIPE, ROTTEN, FULL, DEAD]

# Form a bijection b/w actions and subset of N.
# define the action constants
HUNT, PLANT, HARVEST, WAIT = 0, 1, 2, 3
actions = [HUNT, PLANT, HARVEST, WAIT]

# Define the topology of the MDP: a map, A, so A[s] ≡ A(s)
# the set of legal actions from each state
A = {}
A[HUNGRY] = [HUNT, PLANT]
A[RAW] = [HARVEST, WAIT]
A[RIPE] = [HARVEST]
A[ROTTEN] = [HARVEST]

# a list, tstates, so tstates ≡ Set of terminal states
tstates = [FULL, DEAD]

# Define the properties of the MDP: a map, P, so P[s,a][s2] ≡ p(s'|s,a)
# the state transition distributions
P = {}
P[HUNGRY, HUNT] = [0.0, 0.0, 0.0, 0.0, 0.5, 0.5]
P[HUNGRY, PLANT] = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]
P[RAW, HARVEST] = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
P[RAW, WAIT] = [0.0, 0.0, 0.7, 0.3, 0.0, 0.0]
P[RIPE, HARVEST] = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0]
P[ROTTEN, HARVEST] = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]

# a map, R, so R[s,a,s2] ≡ r(s,a,s')
# the reward function
R = {}
R[HUNGRY, HUNT, FULL] = 4
R[RAW, HARVEST, FULL] = 1
R[RIPE, HARVEST, FULL] = 3

# Define the transition dynamics of the MDP:
import numpy as np

def transition(s, a):
    # choose the next state based on the distribution
    snew = np.random.choice(states, p=P[s, a])
    
    # determine the reward
    if (s, a, snew) not in R.keys():
        rnew = 0
    else:
        rnew = R[(s, a, snew)]
    
    # return the next state and reward
    return snew, rnew

# Define the Q-learning data:
# maps, Q and N, so Q[s,a] ≡ q*(s,a) and N[s,a] ≡ N(s,a)
Q, N = {}, {}
for s in states:
    for a in A[s]:
        Q[s, a] = 0
        N[s, a] = 0

# a scalar, s0 ≡ s₀
s0 = HUNGRY

# a scalar, sims, denoting # of simulations
sims = 500

# Define the Q-learning algorithm:
for t in range(1, sims):
    snew = s0
    
    while snew not in tstates:
        # randomly choose an action (and get next state).
        s = snew
        a = np.random.choice(A[s])
        N[s, a] += 1
        snew, rnew = transition(s, a)
        
        # find the maximum q-value from new state.
        qmax = 0
        if snew not in tstates:
            for a2 in A[snew]:
                qmax = max(qmax, Q[snew, a2])
        
        # apply q-learning update rule.
        discount = 0.9  # assuming a discount factor
        Q[s, a] += 1 / N[s, a] * (rnew + discount * qmax - Q[s, a])