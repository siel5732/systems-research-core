#!/usr/bin/env python3
"""
Continuum Wave Supremacy Simulator
Designed by Imhotep, Trent, and Aphex (Subconscious Systems Group)
Compares a classical discrete search agent (discrete random walk) against a
continuous quantum wave-front (continuous quantum walk) propagating through
an increasingly dense, chaotic field of random obstacles.
"""

import numpy as np
import scipy.linalg as la
import json
import os

def run_classical_simulation(N, obstacle_mask, max_steps=5000, num_trials=200):
    """
    Simulates a classical discrete search agent attempting to propagate
    from site 0 to site N-1. Obstacles act as hard reflective barriers
    or absorption points depending on coordinate rules.
    """
    success_count = 0
    total_steps = 0
    trapped_count = 0
    
    for _ in range(num_trials):
        pos = 0
        steps = 0
        while pos < N - 1 and steps < max_steps:
            # Try to move left or right
            direction = 1 if np.random.rand() > 0.5 else -1
            new_pos = pos + direction
            
            # Periodic boundaries or hard walls
            if new_pos < 0:
                new_pos = 0
                
            # Check for obstacle
            if obstacle_mask[new_pos]:
                # Classical agent gets reflected/blocked by the messy obstacle
                steps += 1
                continue
            else:
                pos = new_pos
                steps += 1
                
        if pos >= N - 1:
            success_count += 1
            total_steps += steps
        else:
            trapped_count += 1
            
    avg_steps = total_steps / success_count if success_count > 0 else max_steps
    success_rate = success_count / num_trials
    return success_rate, avg_steps, trapped_count / num_trials

def run_quantum_simulation(N, obstacle_mask, W_height=5.0, t_hopping=1.0, total_time=150.0):
    """
    Simulates a continuous quantum walk state vector propagating
    through the exact same obstacle field.
    """
    # Hamiltonian Construction
    H = np.zeros((N, N), dtype=complex)
    
    # On-site potential (obstacles represent high potential barriers)
    V = np.where(obstacle_mask, W_height, 0.0)
    np.fill_diagonal(H, V)
    
    # Hopping term
    for i in range(N):
        next_idx = (i + 1) % N
        H[i, next_idx] = -t_hopping
        H[next_idx, i] = -t_hopping
        
    # Diagonalize
    eigenvalues, eigenvectors = la.eigh(H)
    
    # Initialize Gaussian Wave Packet at site N//10 propelled forward (positive momentum)
    mu = N // 10
    sigma = 15.0
    k0 = 0.45  # Forward momentum
    
    n_arr = np.arange(N)
    psi0 = np.exp(-(n_arr - mu)**2 / (2 * sigma**2)) * np.exp(1j * k0 * n_arr)
    psi0 /= np.linalg.norm(psi0)
    
    # Project to eigenbasis
    psi0_eigen = np.dot(eigenvectors.conj().T, psi0)
    
    # Evolve to t = total_time
    psi_eigen_t = psi0_eigen * np.exp(-1j * eigenvalues * total_time)
    psi_t = np.dot(eigenvectors, psi_eigen_t)
    
    # Compute transmission probability (probability mass that reached the last 15% of the lattice)
    prob = np.abs(psi_t)**2
    target_zone_start = int(N * 0.85)
    transmission_prob = float(np.sum(prob[target_zone_start:]))
    
    # Compute IPR (measures localization)
    ipr = float(np.sum(prob**2))
    
    return transmission_prob, ipr

def main():
    print("Initializing Continuum Wave Supremacy Simulation...")
    N = 512  # Lattice dimension
    
    # We sweep across different obstacle densities (how messy/cluttered the database/path is)
    densities = np.linspace(0.05, 0.45, 9)
    
    results = []
    
    for density in densities:
        print(f"\nEvaluating Obstacle Density: {density:.2f}")
        # Generate random obstacle mask (excluding start and end regions)
        obstacle_mask = np.zeros(N, dtype=bool)
        # Place obstacles between 15% and 80% of the lattice
        start_idx = int(N * 0.15)
        end_idx = int(N * 0.80)
        num_obstacles = int((end_idx - start_idx) * density)
        
        obstacle_positions = np.random.choice(np.arange(start_idx, end_idx), size=num_obstacles, replace=False)
        obstacle_mask[obstacle_positions] = True
        
        # 1. Run Classical Discrete Simulation
        class_success, class_steps, class_trapped = run_classical_simulation(N, obstacle_mask)
        
        # 2. Run Continuous Quantum Wave Simulation
        quant_trans, quant_ipr = run_quantum_simulation(N, obstacle_mask)
        
        print(f"   Classical | Success Rate: {class_success*100:5.1f}% | Avg Steps: {class_steps:6.1f} | Trapped: {class_trapped*100:5.1f}%")
        print(f"   Quantum   | Transmission: {quant_trans*100:5.1f}% | IPR: {quant_ipr:.5f}")
        
        results.append({
            "density": float(density),
            "classical": {
                "success_rate": class_success,
                "avg_steps": class_steps,
                "trapped_rate": class_trapped
            },
            "quantum": {
                "transmission": quant_trans,
                "ipr": quant_ipr
            }
        })
        
    output_data = {
        "lattice_size": N,
        "results": results
    }
    
    os.makedirs("systems_core", exist_ok=True)
    with open("systems_core/wave_supremacy_results.json", "w") as f:
        json.dump(output_data, f, indent=2)
        
    print("\nSimulation complete. Saved data to systems_core/wave_supremacy_results.json.")

if __name__ == "__main__":
    main()
