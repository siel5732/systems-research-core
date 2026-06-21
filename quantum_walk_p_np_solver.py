import numpy as np
from scipy.stats import entropy
from scipy.linalg import svd

# --- 1. Graph Definition (Simplified NP-Complete Graph Structure - 8-vertex) ---
# For demonstration, we use a simple cycle graph on 8 vertices.
# This represents a generic "NP-Complete Graph Structure" for the quantum walk.
num_nodes = 8
adj_matrix = np.zeros((num_nodes, num_nodes))
for i in range(num_nodes):
    adj_matrix[i, (i + 1) % num_nodes] = 1
    adj_matrix[i, (i - 1 + num_nodes) % num_nodes] = 1

# Normalize adjacency matrix for probabilities (not strictly needed for unitary shift, but good for context)
# For a quantum walk, we need to convert this to a shift operator.

# --- 2. Define the 2D Coin State Space and Hadamard Coin Transformation ---
# Coin space for 1D walk has two basis states: |0> (or |Left>), |1> (or |Right>)
# Hadamard coin operator
H_coin = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]])

# --- 3. Implement the Quantum Walk Unitary Operator ---
# The total Hilbert space is H_position x H_coin, dimension num_nodes * 2
# Coin operator acts on the coin space at each node.
# Shift operator moves the walker based on coin state and graph connectivity.

# The "Shift" operator:
# For each node 'i' and coin state 'c', if the coin is '0' (left/up), move one way; if '1' (right/down), move another.
# This is a general form for graph walks.
# For a standard DTQW on a line:
# If coin state is |0>, move left. If coin state is |1>, move right.
# On a general graph, this requires careful definition.
# Let's simplify:
# C_0 is "move to neighbor 1", C_1 is "move to neighbor 2" (or other neighbors based on coin)
# For simplicity in this exploratory simulation, let's create a *single* unitary operator
# that combines the coin and the "potential" for movement.

# Let's define the Unitary operator U in the (position x coin) basis
# U = S * (I_position tensor H_coin)
# Where S is the shift operator.
# The shift operator S maps |i>|c> to |j>|c'> based on connectivity and coin.
# This is a common construction for DTQW on graphs:
# S |i>|0> -> |i-1>|0> (move left from i)
# S |i>|1> -> |i+1>|1> (move right from i)
# For a general graph, we need to map to neighbors.

# Let's construct a "Generalized Shift" operator S_g
# For each node 'u' and coin state |0> and |1>:
# if coin is |0>, move to (u-1)%N. if coin is |1>, move to (u+1)%N.
# This is a specific choice for this simulation, making it "1D-like" on the graph structure.
S_general = np.zeros((num_nodes * 2, num_nodes * 2), dtype=complex)

for i in range(num_nodes):
    # If coin state is |0> (index 0 for coin): move to (i-1)%num_nodes
    target_node_left = (i - 1 + num_nodes) % num_nodes
    S_general[target_node_left * 2 + 0, i * 2 + 0] = 1.0 # From |i>|0> to |(i-1)%N>|0>

    # If coin state is |1> (index 1 for coin): move to (i+1)%num_nodes
    target_node_right = (i + 1) % num_nodes
    S_general[target_node_right * 2 + 1, i * 2 + 1] = 1.0 # From |i>|1> to |(i+1)%N>|1>

# Total Unitary Evolution Operator (U)
# U = S_general (I_position tensor H_coin)
# I_position is identity matrix of size num_nodes x num_nodes
I_position = np.identity(num_nodes)
# Kronecker product combines the position and coin spaces for the coin operator
Coin_operator_total = np.kron(I_position, H_coin)
U_operator = np.dot(S_general, Coin_operator_total)

# Check if U_operator is unitary (U_dagger * U = I)
# assert np.allclose(np.dot(U_operator.conj().T, U_operator), np.identity(num_nodes * 2)), "U_operator is not unitary!"
# For complex matrices, numpy.allclose is good.
if not np.allclose(np.dot(U_operator.conj().T, U_operator), np.identity(num_nodes * 2)):
    print("Warning: U_operator is not perfectly unitary.")


# --- Initial State (psi_0) ---
# Start at node 0, with coin in |0> state (or a superposition)
# Let's start at node 0, with coin in superposition state (|0> + i|1>)/sqrt(2)
initial_node = 0
coin_state_0 = np.array([1.0, 0.0]) # |0>
coin_state_1 = np.array([0.0, 1.0]) # |1>
initial_coin_superposition = (coin_state_0 + 1j * coin_state_1) / np.sqrt(2)

psi_0 = np.zeros(num_nodes * 2, dtype=complex)
psi_0[initial_node * 2 : initial_node * 2 + 2] = initial_coin_superposition

# Normalize initial state
psi_0 = psi_0 / np.linalg.norm(psi_0)


# --- Simulation Parameters ---
num_steps = 20
results = []

# --- Helper Functions for Metrics ---
def calculate_spatial_probability(psi, num_nodes):
    # Sum probabilities for each position over coin states
    prob_dist = np.zeros(num_nodes)
    for i in range(num_nodes):
        prob_dist[i] = np.sum(np.abs(psi[i*2 : i*2+2])**2)
    return prob_dist

def calculate_shannon_entropy(prob_dist):
    # Filter out zero probabilities to avoid log(0)
    non_zero_probs = prob_dist[prob_dist > 1e-10]
    return entropy(non_zero_probs, base=2)

def calculate_von_neumann_entanglement_entropy(psi, num_nodes):
    # Reshape psi into a (num_nodes, 2) matrix for the density operator
    psi_matrix = psi.reshape(num_nodes, 2)
    
    # Calculate the total density matrix rho = |psi><psi|
    rho_total = np.outer(psi, psi.conj())

    # --- Partial Trace to get reduced density matrix for position (rho_pos) ---
    # Trace out the coin degree of freedom
    rho_pos = np.zeros((num_nodes, num_nodes), dtype=complex)
    for i in range(num_nodes):
        for j in range(num_nodes):
            # Sum over coin indices (0 and 1)
            rho_pos[i, j] = rho_total[i*2, j*2] + rho_total[i*2+1, j*2+1]

    # --- Partial Trace to get reduced density matrix for coin (rho_coin) ---
    # Trace out the position degree of freedom
    rho_coin = np.zeros((2, 2), dtype=complex)
    for c1 in range(2):
        for c2 in range(2):
            for i in range(num_nodes):
                rho_coin[c1, c2] += rho_total[i*2 + c1, i*2 + c2]

    # Entanglement entropy is typically calculated by taking the partial trace
    # over one subsystem and then calculating the von Neumann entropy of the reduced state.
    # S(rho_A) = -Tr(rho_A log2 rho_A)
    # For a bipartite state, S(rho_A) = S(rho_B) if the total state is pure.

    # Calculate eigenvalues of rho_pos
    eigenvalues_pos = np.linalg.eigvalsh(rho_pos)
    # Filter out zero eigenvalues to avoid log(0)
    non_zero_eigenvalues_pos = eigenvalues_pos[eigenvalues_pos > 1e-10]
    von_neumann_pos = -np.sum(non_zero_eigenvalues_pos * np.log2(non_zero_eigenvalues_pos))

    # Calculate eigenvalues of rho_coin
    eigenvalues_coin = np.linalg.eigvalsh(rho_coin)
    # Filter out zero eigenvalues to avoid log(0)
    non_zero_eigenvalues_coin = eigenvalues_coin[eigenvalues_coin > 1e-10]
    von_neumann_coin = -np.sum(non_zero_eigenvalues_coin * np.log2(non_zero_eigenvalues_coin))

    # For a pure bipartite state, these two should be equal. We return the average or one of them.
    # Let's return the one calculated from rho_pos.
    return von_neumann_pos


# --- Main Simulation Loop ---
current_psi = psi_0

for step in range(num_steps):
    spatial_prob = calculate_spatial_probability(current_psi, num_nodes)
    shannon = calculate_shannon_entropy(spatial_prob)
    von_neumann = calculate_von_neumann_entanglement_entropy(current_psi, num_nodes)

    step_results = {
        "step": step,
        "spatial_probability": spatial_prob.tolist(),
        "shannon_entropy": shannon,
        "von_neumann_entanglement_entropy": von_neumann
    }
    results.append(step_results)

    # Propagate the quantum walker
    current_psi = np.dot(U_operator, current_psi)
    # Re-normalize (numerical stability, though U should be unitary)
    current_psi = current_psi / np.linalg.norm(current_psi)

# --- Save Results ---
import json
output_filename = 'quantum_walk_p_np_results.json'
with open(output_filename, 'w') as f:
    json.dump(results, f, indent=4)

print(f"Simulation complete. Results saved to {output_filename}")

# --- Mathematical and Numerical Evaluation Implications ---
# The core question is whether "phase-interference of quantum superposition can exploit
# physical/analog wave structures (operating on transfinite cardinality 'c') to flatten
# the exponential computational complexity curve of standard discrete Turing machines
# (which are bound to step limits 'aleph_0')".

# This simulation, while discrete, hints at the *potential* for quantum
# systems to explore solution spaces differently. The key aspects are:
# 1. Superposition: The walker is in multiple "path" states simultaneously.
# 2. Interference: These paths interfere, potentially amplifying correct solutions
#    and canceling out incorrect ones.
# 3. Entanglement: Between coin and position, crucial for the "quantumness" of the walk.

# Numerical observation from this simulation:
# - Spatial probability distribution: How does it spread? Does it focus on certain nodes?
# - Shannon entropy: Measures the "spread" or uncertainty in the spatial distribution.
#   A rapid increase might suggest faster exploration than classical random walk.
# - Von Neumann entropy: Measures entanglement between coin and position.
#   High entanglement means these degrees of freedom are strongly correlated,
#   which is a resource for quantum computation.

# This discrete simulation operates on 'aleph_0' steps. The "transfinite cardinality 'c'"
# argument refers to a theoretical advantage of *continuous* analog systems,
# which are not perfectly modeled by discrete quantum walks. However, DTQWs
# are a stepping stone. If quantum interference *can* lead to a polynomial speedup
# (e.g., in search algorithms like Grover's), it suggests that leveraging quantum
# phenomena might offer a different scaling behavior.

# The simulation itself, being discrete, is still bound by discrete steps.
# The "flattening" of complexity curve would be indicated if the required
# number of steps to find a solution (or characteristic behavior) scales
# polynomially with problem size, rather than exponentially, for problems
# that are classically exponential. Our small 8-node example doesn't directly
# prove this for NP-Complete problems, but the calculated entropies and
# probability distribution are key metrics to analyze in larger-scale,
# more specialized simulations. The entanglement is particularly
# interesting as it indicates non-classical correlations that underpin quantum advantage.
