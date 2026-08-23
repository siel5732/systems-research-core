
import numpy as np
import json
from scipy.linalg import eigh

# --- Constants ---
N = 1024  # Number of nodes
beta = (1 + np.sqrt(5)) / 2  # Golden Ratio, an irrational number for quasi-periodicity
phi = 0  # Phase offset, can be set to 0 without loss of generality for the model's core properties
time_steps = 100
dt = 0.1  # Time step for evolution

# --- Aubry-André Potential ---
def aubry_andre_potential(n, lambda_val, beta, phi):
    """Calculates the Aubry-André potential at node n."""
    return lambda_val * np.cos(2 * np.pi * beta * n + phi)

# --- Hamiltonian Construction ---
def build_hamiltonian(N, lambda_val, beta, phi):
    """Builds the N x N Aubry-André Hamiltonian matrix."""
    H = np.zeros((N, N))

    # On-site potential (diagonal elements)
    for n in range(N):
        H[n, n] = aubry_andre_potential(n, lambda_val, beta, phi)

    # Hopping terms (off-diagonal elements, nearest-neighbor coupling)
    # Assuming periodic boundary conditions for simplicity in a finite system
    # For a quantum walk, typically we'd consider free boundary or infinite lattice.
    # Here, for a finite system, periodic boundary conditions are a common approximation.
    t = -1  # Hopping integral, typically set to -1 or 1
    for n in range(N):
        H[n, (n + 1) % N] = t
        H[n, (n - 1 + N) % N] = t
    return H

# --- Inverse Participation Ratio (IPR) ---
def calculate_ipr(probability_distribution):
    """Calculates the Inverse Participation Ratio for a given probability distribution."""
    # IPR = sum_n ( |psi_n|^4 ) / ( sum_n |psi_n|^2 )^2
    # If psi is normalized (sum |psi_n|^2 = 1), then IPR = sum_n |psi_n|^4
    # For a normalized probability distribution P, IPR = sum_n P_n^2
    return np.sum(probability_distribution**2)

# --- Shannon Entropy ---
def calculate_shannon_entropy(probability_distribution):
    """Calculates the Shannon entropy for a given probability distribution."""
    # S = -sum_n P_n log(P_n)
    # Avoid log(0) by filtering out zero probabilities
    non_zero_probs = probability_distribution[probability_distribution > 0]
    return -np.sum(non_zero_probs * np.log(non_zero_probs))

# --- Quantum Walk Simulation (Time Evolution) ---
def simulate_quantum_walk(H, initial_state, dt, time_steps):
    """Simulates the time evolution of an initial state under Hamiltonian H."""
    psi_t = initial_state.copy()
    probabilities_over_time = []
    ipr_over_time = []
    entropy_over_time = []

    # Evolution operator U = exp(-iHt)
    # For small dt, U approx I - iHdt (Euler approximation for simplicity,
    # or use scipy.linalg.expm for more accuracy, but expm is computationally heavier)
    # Using Trotter-Suzuki decomposition or similar exact methods is complex for this general case.
    # For a basic demonstration of localization/delocalization,
    # we can simplify to consider the time evolution through eigenvectors.

    # Diagonalize the Hamiltonian once
    eigenvalues, eigenvectors = eigh(H)
    # Express initial state in the eigenbasis
    initial_state_in_eigenbasis = eigenvectors.T @ initial_state

    for t_step in range(time_steps):
        # Evolve each component in the eigenbasis
        evolved_in_eigenbasis = initial_state_in_eigenbasis * np.exp(-1j * eigenvalues * t_step * dt)
        # Transform back to the real space
        psi_t = eigenvectors @ evolved_in_eigenbasis

        probability_distribution = np.abs(psi_t)**2
        # Ensure normalization
        probability_distribution /= np.sum(probability_distribution)

        probabilities_over_time.append(probability_distribution.tolist())
        ipr_over_time.append(calculate_ipr(probability_distribution))
        entropy_over_time.append(calculate_shannon_entropy(probability_distribution))

    return {
        "final_probability_distribution": (np.abs(psi_t)**2).tolist(),
        "probabilities_over_time": probabilities_over_time,
        "ipr_over_time": ipr_over_time,
        "entropy_over_time": entropy_over_time
    }

# --- Main Simulation Loop ---
results = {}

# Initial state: localized at one node (e.g., node 0)
initial_state = np.zeros(N, dtype=complex)
initial_state[N // 2] = 1.0  # Start in the middle
initial_state /= np.linalg.norm(initial_state) # Ensure normalization

# Phase 1: De-localized (Solvable/Satisfiable Region, lambda < 2)
lambda_deloc = 1.0
print(f"Simulating De-localized Phase (lambda = {lambda_deloc})...")
H_deloc = build_hamiltonian(N, lambda_deloc, beta, phi)
results["de_localized_phase"] = {
    "lambda": lambda_deloc,
    "simulation": simulate_quantum_walk(H_deloc, initial_state, dt, time_steps)
}

# Phase 2: Critical Phase Transition (The Hardness Peak, lambda = 2)
lambda_critical = 2.0
print(f"Simulating Critical Phase (lambda = {lambda_critical})...")
H_critical = build_hamiltonian(N, lambda_critical, beta, phi)
results["critical_phase"] = {
    "lambda": lambda_critical,
    "simulation": simulate_quantum_walk(H_critical, initial_state, dt, time_steps)
}

# Phase 3: Localized (Over-constrained/Unsatisfiable Region, lambda > 2)
lambda_loc = 3.0
print(f"Simulating Localized Phase (lambda = {lambda_loc})...")
H_loc = build_hamiltonian(N, lambda_loc, beta, phi)
results["localized_phase"] = {
    "lambda": lambda_loc,
    "simulation": simulate_quantum_walk(H_loc, initial_state, dt, time_steps)
}

# --- Export Results ---
output_file = 'systems-research-core/aubry_andre_results.json'
with open(output_file, 'w') as f:
    json.dump(results, f, indent=4)

print(f"Simulation complete. Results saved to {output_file}")
