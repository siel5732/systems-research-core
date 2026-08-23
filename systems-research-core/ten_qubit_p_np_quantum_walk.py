import numpy as np
from scipy.stats import entropy
import json

# Configuration
NUM_QUBITS = 10
NUM_STATES = 2**NUM_QUBITS # 1024 dimensions
NUM_STEPS = 20 # Number of quantum walk steps
SOLUTION_STATE_INDEX = 0 # Example: |000...0> as the solution state (index 0)
DETACH_PHASE_ANGLE = np.pi / 2 # Phase rotation for "invalid" states

def create_initial_state(num_qubits):
    """Initializes a uniform superposition over all states."""
    state = np.ones(2**num_qubits, dtype=complex) / np.sqrt(2**num_qubits)
    return state

def create_hadamard_operator(num_qubits):
    """Creates a multi-qubit Hadamard operator using Kronecker products."""
    H = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
    H_multi = H
    for _ in range(num_qubits - 1):
        H_multi = np.kron(H_multi, H)
    return H_multi

def create_detach_phase_operator(num_qubits, solution_state_index, phase_angle):
    """
    Creates the "Detach" phase-rotation operator.
    This operator applies a phase to all states *except* the solution state,
    causing destructive interference for invalid paths and constructive
    for the solution.
    """
    detach_op = np.eye(2**num_qubits, dtype=complex)
    for i in range(2**num_qubits):
        if i != solution_state_index:
            detach_op[i, i] *= np.exp(1j * phase_angle)
    return detach_op

def run_quantum_walk_simulation(num_qubits, num_steps, solution_state_index, detach_phase_angle):
    """Runs the quantum walk simulation."""
    current_state_vector = create_initial_state(num_qubits)

    # Operators
    H_op = create_hadamard_operator(num_qubits)
    P_detach_op = create_detach_phase_operator(num_qubits, solution_state_index, detach_phase_angle)
    
    # Combined walk operator for one step: Hadamard followed by Detach phase.
    # The order matters; Detach is applied *after* the Hadamard spreads probabilities.
    walk_operator = P_detach_op @ H_op

    probabilities_over_time = []
    fidelities_over_time = []
    entropies_over_time = []

    # Define the target solution state vector for fidelity calculation
    solution_state_vector = np.zeros(NUM_STATES, dtype=complex)
    solution_state_vector[solution_state_index] = 1.0

    for step in range(num_steps):
        # Compute probabilities
        probabilities = np.abs(current_state_vector)**2
        probabilities_over_time.append(probabilities.tolist())

        # Compute fidelity to the solution state
        # Fidelity = |<current_state|solution_state>|^2
        fidelity = np.abs(np.vdot(current_state_vector, solution_state_vector))**2
        fidelities_over_time.append(fidelity)

        # Compute Shannon entropy
        # Avoid log(0) for states with zero probability
        non_zero_probabilities = probabilities[probabilities > 1e-12] # Threshold for numerical stability
        shannon_entropy = entropy(non_zero_probabilities, base=2)
        entropies_over_time.append(shannon_entropy)

        # Apply the walk operator
        current_state_vector = walk_operator @ current_state_vector
        current_state_vector = current_state_vector / np.linalg.norm(current_state_vector) # Normalize

    # Final state probabilities
    final_probabilities = (np.abs(current_state_vector)**2).tolist()

    return {
        "probabilities_over_time": probabilities_over_time,
        "fidelities_over_time": fidelities_over_time,
        "entropies_over_time": entropies_over_time,
        "final_probabilities": final_probabilities,
        "num_qubits": num_qubits,
        "num_steps": num_steps,
        "solution_state_index": solution_state_index,
        "detach_phase_angle": detach_phase_angle
    }

if __name__ == "__main__":
    print(f"Starting 10-qubit P vs NP Quantum Walk Simulation with {NUM_STEPS} steps...")
    results = run_quantum_walk_simulation(NUM_QUBITS, NUM_STEPS, SOLUTION_STATE_INDEX, DETACH_PHASE_ANGLE)
    
    output_path = "systems-research-core/ten_qubit_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"Simulation complete. Results saved to {output_path}")

    # Optional: Print some key final results
    print("\nFinal Probabilities (top 5):")
    # Create state labels for readability
    state_labels = [f'|{i:0{NUM_QUBITS}b}>' for i in range(NUM_STATES)]

    sorted_final_probs = sorted(zip(state_labels, results["final_probabilities"]), key=lambda x: x[1], reverse=True)
    for label, prob in sorted_final_probs[:5]:
        print(f"State {label}: {prob:.6f}")
    
    print(f"Final Fidelity to Solution State (|{SOLUTION_STATE_INDEX:0{NUM_QUBITS}b}>): {results['fidelities_over_time'][-1]:.6f}")
    print(f"Final Shannon Entropy: {results['entropies_over_time'][-1]:.6f}")
