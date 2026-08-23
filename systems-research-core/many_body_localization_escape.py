
import numpy as np
from scipy.linalg import expm
import json
import matplotlib.pyplot as plt

# --- System Parameters ---
L = 6  # Number of qubits (small for simulation tractability, ideally larger)
N = 2**L  # Hilbert space dimension
hbar = 1  # Planck's constant (set to 1 for simplicity)

# Aubry-André potential parameters
V = 1.0  # Potential strength
delta = (np.sqrt(5) - 1) / 2  # Irrational number for quasi-periodicity

# Interaction strengths
J_int_MBL = 0.0  # MBL regime (zero/weak interaction)
J_int_Thermal = 1.5  # Thermalized regime (strong interaction)

# Time evolution parameters
t_max = 10  # Maximum simulation time
dt = 0.1  # Time step
time_points = np.arange(0, t_max, dt)

# --- Pauli Matrices ---
sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
identity = np.array([[1, 0], [0, 1]], dtype=complex)

# --- Helper Functions ---
def get_op(op, site, L):
    """Construct a multi-qubit operator (e.g., sigma_x on a specific site)."""
    op_list = [identity] * L
    op_list[site] = op
    return reduce(np.kron, op_list)

def get_full_hamiltonian(J_int, L, V, delta):
    """Construct the full Hamiltonian for the system."""
    H = np.zeros((N, N), dtype=complex)

    # Local Potential (Aubry-André)
    for i in range(L):
        potential_term = V * np.cos(2 * np.pi * delta * i)
        H += potential_term * get_op(sigma_z, i, L)

    # Nearest-neighbor interaction (Ising-like ZZ interaction for simplicity)
    if J_int > 0:
        for i in range(L - 1):
            H += J_int * get_op(sigma_z, i, L) @ get_op(sigma_z, i + 1, L)
    
    # Adding a small XX term to facilitate entanglement spread for thermalization
    # This is crucial for genuinely seeing thermalization, as ZZ alone conserves parity
    for i in range(L - 1):
        H += 0.1 * J_int * get_op(sigma_x, i, L) @ get_op(sigma_x, i + 1, L)


    return H

def trace_out(state_vector, L, sub_system_A_sites):
    """Trace out a subsystem to get the reduced density matrix."""
    rho_full = np.outer(state_vector, state_vector.conj())
    
    # Identify the dimensions of subsystem A and B
    dims = [2] * L
    
    # Reshape the full density matrix to trace out B
    # This part is conceptually tricky and often involves permuting indices
    # For a simple half-system split, we can iterate
    
    # For a half-system, L_A = L // 2
    L_A = L // 2
    
    # Create the partial trace operator explicitly for a given split
    # For a bipartite split (A|B), the density matrix is rho_AB
    # Tr_B(rho_AB) = sum_k <k_B| rho_AB |k_B>
    
    # Example: L=4, L_A=2. Subsystem A = qubits 0,1. Subsystem B = qubits 2,3.
    # States are |q0 q1 q2 q3>
    # To trace out q2,q3: sum over |q2 q3>
    
    rho_A = np.zeros((2**L_A, 2**L_A), dtype=complex)
    
    # Iterate over all possible states of subsystem B
    for i_B in range(2**(L - L_A)):
        # Construct the basis state for subsystem B
        basis_B = [int(x) for x in bin(i_B)[2:].zfill(L - L_A)]
        
        # Select rows/columns corresponding to this basis state of B
        # This involves careful indexing. A more robust way uses qutip or explicit tensor reshaping.
        
        # A simpler approach for the half-system split:
        # Reshape the full N x N matrix into a (2^LA x 2^LB) x (2^LA x 2^LB) tensor
        # Then perform the sum
        
        # Simplified for fixed half-system split:
        # Map a global index 'k' to (k_A, k_B) indices
        
        # rho_full indices can be thought of as (alpha_A, alpha_B), (beta_A, beta_B)
        # We want to sum over alpha_B == beta_B
        
        for k_A_row in range(2**L_A):
            for k_A_col in range(2**L_A):
                for k_B in range(2**(L - L_A)):
                    # Global index for row: combine k_A_row and k_B
                    global_row_index = (k_A_row << (L - L_A)) | k_B
                    # Global index for col: combine k_A_col and k_B
                    global_col_index = (k_A_col << (L - L_A)) | k_B
                    
                    rho_A[k_A_row, k_A_col] += rho_full[global_row_index, global_col_index]
                    
    return rho_A


def von_neumann_entropy(rho):
    """Calculate the von Neumann entanglement entropy."""
    eigenvalues = np.linalg.eigvalsh(rho)
    # Filter out zero or negative eigenvalues due to numerical precision
    eigenvalues = eigenvalues[eigenvalues > 1e-12]
    if len(eigenvalues) == 0:
        return 0
    return -np.sum(eigenvalues * np.log2(eigenvalues))

def fidelity(state1, state2):
    """Calculate the fidelity between two quantum states."""
    return np.abs(np.vdot(state1, state2))**2

# --- Simulation Execution ---
def run_simulation():
    initial_state = np.zeros(N, dtype=complex)
    # Start with a simple product state, e.g., |00...0>
    initial_state[0] = 1.0

    all_results = {
        "MBL_Regime": {
            "entanglement_entropy": [],
            "probability_densities": [],
            "fidelities": [],
            "time_points": time_points.tolist()
        },
        "Thermalized_Regime": {
            "entanglement_entropy": [],
            "probability_densities": [],
            "fidelities": [],
            "time_points": time_points.tolist()
        }
    }

    # Regime 1: MBL
    print("Simulating MBL Regime...")
    H_MBL = get_full_hamiltonian(J_int_MBL, L, V, delta)
    current_state_MBL = initial_state.copy()
    
    # Pre-calculate evolution operator for MBL
    U_MBL = expm(-1j * H_MBL * dt / hbar)

    for t_idx, t in enumerate(time_points):
        # Calculate reduced density matrix for half-system entanglement entropy
        rho_A_MBL = trace_out(current_state_MBL, L, list(range(L // 2)))
        entropy_MBL = von_neumann_entropy(rho_A_MBL)
        all_results["MBL_Regime"]["entanglement_entropy"].append(entropy_MBL)

        # Probability densities (diagonal of density matrix, or |psi_i|^2)
        prob_dens_MBL = np.abs(current_state_MBL)**2
        all_results["MBL_Regime"]["probability_densities"].append(prob_dens_MBL.tolist())

        # Fidelity with initial state
        fid_MBL = fidelity(initial_state, current_state_MBL)
        all_results["MBL_Regime"]["fidelities"].append(fid_MBL)

        # Evolve state
        current_state_MBL = U_MBL @ current_state_MBL
        current_state_MBL /= np.linalg.norm(current_state_MBL) # Normalize after evolution


    # Regime 2: Thermalized
    print("Simulating Thermalized Regime...")
    H_Thermal = get_full_hamiltonian(J_int_Thermal, L, V, delta)
    current_state_Thermal = initial_state.copy()
    
    # Pre-calculate evolution operator for Thermalized
    U_Thermal = expm(-1j * H_Thermal * dt / hbar)


    for t_idx, t in enumerate(time_points):
        # Calculate reduced density matrix for half-system entanglement entropy
        rho_A_Thermal = trace_out(current_state_Thermal, L, list(range(L // 2)))
        entropy_Thermal = von_neumann_entropy(rho_A_Thermal)
        all_results["Thermalized_Regime"]["entanglement_entropy"].append(entropy_Thermal)

        # Probability densities
        prob_dens_Thermal = np.abs(current_state_Thermal)**2
        all_results["Thermalized_Regime"]["probability_densities"].append(prob_dens_Thermal.tolist())

        # Fidelity with initial state
        fid_Thermal = fidelity(initial_state, current_state_Thermal)
        all_results["Thermalized_Regime"]["fidelities"].append(fid_Thermal)

        # Evolve state
        current_state_Thermal = U_Thermal @ current_state_Thermal
        current_state_Thermal /= np.linalg.norm(current_state_Thermal) # Normalize after evolution

    # --- Export Results ---
    with open('many_body_results.json', 'w') as f:
        json.dump(all_results, f, indent=4)
    print("Simulation complete. Results saved to 'many_body_results.json'")
    
    # --- Basic Plotting (for conceptual understanding, not saved to file) ---
    plt.figure(figsize=(12, 6))
    plt.plot(time_points, all_results["MBL_Regime"]["entanglement_entropy"], label="MBL Regime (J_int=0.0)")
    plt.plot(time_points, all_results["Thermalized_Regime"]["entanglement_entropy"], label="Thermalized Regime (J_int=1.5)")
    plt.xlabel("Time")
    plt.ylabel("Half-System Entanglement Entropy")
    plt.title("Entanglement Entropy Over Time")
    plt.legend()
    plt.grid(True)
    # plt.show() # Don't show plots in a non-interactive environment

if __name__ == "__main__":
    from functools import reduce # Import reduce for get_op
    run_simulation()
