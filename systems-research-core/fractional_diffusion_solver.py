#!/usr/bin/env python3
"""
Fractional-Order Anomalous Diffusion Solver (Caputo L1 Discretization Scheme)
Designed by SCRUM Master Trent Reznor under the Subconscious Systems Group.
Implements a pure-Python time-fractional partial differential equation (PDE) solver
using the L1 finite-difference scheme to model anomalous sub-diffusion and history-dependent
viscoelastic entrapment inside crowded biological hydrogels (e.g., alginate).
"""

import json
import math
import os

def solve_fractional_diffusion(alpha, M=15, N=40, T=5.0, L=1.0, D=0.1):
    """
    Solves time-fractional diffusion equation using explicit L1 discretization:
    Caputo_D^alpha C(x,t) = D * d2C/dx2
    Boundary conditions: C(0, t) = 10.0 (high source concentration), C(L, t) = 0.0 (sink)
    Initial condition: C(x, 0) = 0.0 for x > 0
    """
    dt = T / N
    dx = L / (M - 1)
    
    # Pre-calculate L1 coefficients: a_k = (k+1)^(1-alpha) - k^(1-alpha)
    a = []
    for k in range(N):
        a.append((k + 1)**(1.0 - alpha) - k**(1.0 - alpha))
        
    # Gamma function scaling constant
    # Caputo L1 scaling coefficient: K_alpha = (Gamma(2 - alpha) * dt^alpha * D) / dx^2
    gamma_coeff = math.gamma(2.0 - alpha)
    K_alpha = (gamma_coeff * (dt**alpha) * D) / (dx**2)
    
    # Initialize concentration grid over time: C[time_step][spatial_node]
    C = [[0.0] * M for _ in range(N + 1)]
    
    # Apply Dirichlet boundary conditions
    for n in range(N + 1):
        C[n][0] = 10.0  # high constant source (e.g., blood cytokine concentration)
        C[n][M - 1] = 0.0  # open boundary sink
        
    # Time-stepping loop (L1 explicit solver)
    for n in range(1, N + 1):
        for i in range(1, M - 1):
            # 1. Compute spatial second derivative (Fickian flux term)
            d2C_dx2 = C[n - 1][i + 1] - 2.0 * C[n - 1][i] + C[n - 1][i - 1]
            
            # 2. Integrate Caputo history memory term
            history_sum = 0.0
            for k in range(1, n):
                # past difference term: (C_k - C_{k-1}) weighted by chronological age a_{n-k}
                diff = C[n - k][i] - C[n - k - 1][i]
                history_sum += a[k] * diff
                
            # 3. Explicit L1 update step
            # C_n = C_{n-1} - history_sum + K_alpha * d2C_dx2
            # Since a[0] = 1, we divide/scale directly
            C[n][i] = C[n - 1][i] - history_sum + K_alpha * d2C_dx2
            
            # Clip numerical noise
            if C[n][i] < 0.0:
                C[n][i] = 0.0
            elif C[n][i] > 10.0:
                C[n][i] = 10.0
                
    return C, dx, dt

def run_simulation():
    # Grid config
    M = 15  # space steps
    N = 250  # time steps (stabilizes fractional L1 explicit scheme)
    T = 4.0  # total seconds
    L = 100.0  # alginate capsule wall thickness (microns)
    D = 120.0  # diffusion constant (microns^2/sec)
    
    # We compare three anomalous diffusion exponents (alpha):
    # 1. alpha = 1.0 -> Classic Fickian Brownian Diffusion (No viscoelastic memory)
    # 2. alpha = 0.75 -> Anomalous Sub-Diffusion (Crowded hydrogel mesh, molecular trapping)
    # 3. alpha = 0.50 -> Severe Viscoelastic Entrapment (High polymer compaction, compact PLL-coating)
    alphas = [1.0, 0.75, 0.50]
    results = {}
    
    for alpha in alphas:
        C, dx, dt = solve_fractional_diffusion(alpha, M, N, T, L, D)
        results[f"alpha_{alpha}"] = C
        
    # Package data
    trajectory = []
    for n in range(N + 1):
        t = n * (T / N)
        step_data = {"time_sec": round(t, 3)}
        for alpha in alphas:
            C_grid = results[f"alpha_{alpha}"][n]
            # Log center point concentration and spatial profiles
            step_data[f"alpha_{alpha}_center"] = round(C_grid[int(M/2)], 3)
            step_data[f"alpha_{alpha}_grid"] = [round(val, 2) for val in C_grid]
        trajectory.append(step_data)
        
    # Save JSON results
    os.makedirs("systems_core", exist_ok=True)
    out_path = "systems_core/fractional_diffusion_results.json"
    data = {
        "metadata": {
            "title": "Time-Fractional Caputo L1 Anomalous Sub-Diffusion Solver",
            "PI": "Trent Reznor (SCRUM Master)",
            "date": "2026-06-19",
            "alphas": alphas,
            "units": {
                "time": "seconds",
                "space": "microns",
                "concentration": "relative intensity (0.0 to 10.0)"
            }
        },
        "trajectory": trajectory
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Fractional simulation completed. Results saved to: {out_path}")
    
    # Save a quick preview of our grid concentrations at final step
    final_step = trajectory[-1]
    print(f"Final Spatial Profiles at t = {T}s:")
    for alpha in alphas:
        print(f"  Alpha = {alpha}: Center = {final_step[f'alpha_{alpha}_center']}, Grid = {final_step[f'alpha_{alpha}_grid']}")

if __name__ == "__main__":
    run_simulation()
