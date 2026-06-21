#!/usr/bin/env python3
"""
Gargantua Quantum Walk Simulator
Designed by Imhotep, Trent, and Aphex (Subconscious Systems Group)
12-Qubit State Space (4,096 complex amplitudes) modeling Schwarzschild gravitational
time dilation and transfinite Cantor-dust accretion potential near Gargantua.
"""

import numpy as np
import scipy.linalg as la
import json
import os

def generate_cantor_set(length, depth=6):
    """Generates a Cantor-dust potential of a given length."""
    pot = np.zeros(length)
    def recurse(start, end, current_depth):
        if current_depth == 0:
            return
        third = (end - start) // 3
        if third == 0:
            return
        # Zero out the middle third
        pot[start + third : start + 2 * third] = 1.0
        recurse(start, start + third, current_depth - 1)
        recurse(start + 2 * third, end, current_depth - 1)
    
    recurse(0, length, depth)
    # Invert so 1s represent the Cantor dust barriers
    return 1.0 - pot

def main():
    print("Initializing 12-Qubit Gargantua Quantum Walk Simulation...")
    num_qubits = 12
    N = 2**num_qubits  # 4,096 dimensions
    print(f"Lattice Dimension (N): {N}")
    
    # Schwarzschild Metric & Radial Mapping
    r_s = 2.0  # Schwarzschild radius
    r_max = 10.0
    delta = 0.05  # Horizon cushion
    
    # Map index n to radial distance r(n)
    # Closest to horizon at n = 0 and n = N-1; furthest in flat space at n = N/2
    n_arr = np.arange(N)
    r = r_s + delta + (r_max - r_s - delta) * np.sin(np.pi * n_arr / N)**2
    
    # Schwarzschild Lapse Function (Time Dilation): alpha = sqrt(1 - r_s / r)
    alpha = np.sqrt(1.0 - r_s / r)
    
    # Gravitational Hopping Coefficients
    t0 = 1.0
    # Hopping between site n and n+1 (periodic boundary conditions)
    t = -t0 * alpha
    
    # Infinite Cardinality Potential (Cantor Dust Accretion Disk)
    cantor = generate_cantor_set(N, depth=6)
    W = 1.5  # Potential strength of Cantor dust
    V = W * cantor
    
    # Construct the Tight-Binding Schwarzschild Hamiltonian Matrix
    H = np.zeros((N, N), dtype=complex)
    
    # Diagonal potential
    np.fill_diagonal(H, V)
    
    # Off-diagonal hopping terms
    for i in range(N):
        next_idx = (i + 1) % N
        H[i, next_idx] = t[i]
        H[next_idx, i] = t[i]  # Hermitian conjugate
        
    print("Diagonalizing the 4,096-dimensional Schwarzschild Hamiltonian...")
    eigenvalues, eigenvectors = la.eigh(H)
    print("Diagonalization complete.")
    
    # State Initialization: Gaussian Wave Packet representing a quantum probe
    # Spawned in flat space (n = N/2) propelled toward the horizon (negative momentum)
    mu = N // 2
    sigma = 40.0
    k0 = -0.15  # Inward momentum
    
    psi0 = np.exp(-(n_arr - mu)**2 / (2 * sigma**2)) * np.exp(1j * k0 * n_arr)
    # Periodic boundary wrap
    psi0 = psi0 / np.linalg.norm(psi0)
    
    # Time Evolution
    # t_steps = 100, dt = 0.5 (models coordinate time evolution)
    dt = 0.5
    num_steps = 100
    times = np.arange(num_steps) * dt
    
    results_history = []
    
    print("Running coordinate time evolution...")
    # Project psi0 onto the eigenbasis
    # psi0_eigen = V^H * psi0
    psi0_eigen = np.dot(eigenvectors.conj().T, psi0)
    
    for step in range(num_steps):
        t_curr = times[step]
        # Evolve in eigenbasis: psi_eigen(t) = e^{-i * E * t} * psi0_eigen
        psi_eigen_t = psi0_eigen * np.exp(-1j * eigenvalues * t_curr)
        # Transform back to position basis: psi(t) = V * psi_eigen(t)
        psi_t = np.dot(eigenvectors, psi_eigen_t)
        
        # Compute Observables
        prob = np.abs(psi_t)**2
        ipr = float(np.sum(prob**2))
        
        # Prevent log(0)
        prob_safe = np.where(prob > 1e-12, prob, 1e-12)
        entropy = float(-np.sum(prob_safe * np.log(prob_safe)))
        
        # Horizon Penetration (near n = 0 and n = N)
        # We classify n < 200 or n > N - 200 as the "near-horizon" zone
        horizon_zone = 200
        horizon_prob = float(np.sum(prob[:horizon_zone]) + np.sum(prob[-horizon_zone:]))
        
        # Mean position
        mean_pos = float(np.sum(n_arr * prob))
        
        # Save a compressed spatial representation (128 bins for visualization)
        bin_size = N // 128
        binned_prob = [float(np.sum(prob[i*bin_size : (i+1)*bin_size])) for i in range(128)]
        
        results_history.append({
            "step": step,
            "time": t_curr,
            "ipr": ipr,
            "entropy": entropy,
            "horizon_prob": horizon_prob,
            "mean_pos": mean_pos,
            "binned_prob": binned_prob
        })
        
        if step % 20 == 0:
            print(f"   Step {step:03d} | Time: {t_curr:4.1f} | IPR: {ipr:.5f} | Horizon Prob: {horizon_prob:.4f} | Mean Pos: {mean_pos:.1f}")
            
    # Output metrics to JSON
    output_data = {
        "num_qubits": num_qubits,
        "N": N,
        "r_s": r_s,
        "r_max": r_max,
        "delta": delta,
        "times": times.tolist(),
        "history": results_history
    }
    
    os.makedirs("systems_core", exist_ok=True)
    with open("systems_core/gargantua_results.json", "w") as f:
        json.dump(output_data, f, indent=2)
        
    print("Simulation complete. Data saved to systems_core/gargantua_results.json.")

if __name__ == "__main__":
    main()
