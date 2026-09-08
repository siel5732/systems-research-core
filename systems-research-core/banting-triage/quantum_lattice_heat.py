#!/usr/bin/env python3
"""
SAGE-Banting Pure Quantum Lattice Geometric Heat Equation Solver.

Implements the "algebraically native" geometric discretization of the quantum Poincaré plane
minus the axes, using the quantum real line R_q and positive half-line R_q^+.
This approach eliminates any coordinate singularity at x = 0 by utilizing the native
multiplicative shift structure of the Jackson q-derivative, completely bypassing
extrinsic interpolation or classical finite-difference blending.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_native_lattice_heat_simulation():
    print("=================================================================")
    print("  SAGE-BANTING NATIVE ALGEBRAIC q-LATTICE SPECTRAL PDE SOLVER")
    print("=================================================================")
    
    # ------------------------------------------------------------------
    # Step 1: Set up the q-Lattice Grid (Quantum Plane R_q x R_q^+)
    # ------------------------------------------------------------------
    q_values = [0.94, 1.0, 1.06]
    
    # We will simulate and compare all three q-values
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
    plt.subplots_adjust(wspace=0.15)
    
    for ax_idx, q_val in enumerate(q_values):
        print(f"\nSetting up quantum lattice for q = {q_val}...")
        
        is_classical = False
        if np.abs(q_val - 1.0) < 1e-4:
            is_classical = True
            # Classical limit runs on a uniform grid
            Nx, Ny = 120, 120
            X = np.linspace(-1.5, 1.5, Nx)
            Y = np.linspace(0.2, 2.0, Ny)
            X_grid, Y_grid = np.meshgrid(X, Y, indexing='ij')
            
            # Gaussian point source at (0.0, 1.0)
            sigma2 = 0.018
            U = np.exp(-(X_grid**2 + (Y_grid - 1.0)**2) / (2.0 * sigma2))
            U /= np.sum(U)
            U = U.T  # Shape (Ny, Nx)
            
            dtau = 8e-5
            steps = 300
            
            dy = Y[1] - Y[0]
            dx = X[1] - X[0]
            
            print(f"  Uniform grid: Nx = {Nx}, Ny = {Ny}")
            print(f"  y range: [{Y[0]:.2f}, {Y[-1]:.2f}]")
            print(f"  Integrating {steps} steps of dtau = {dtau}...")
            
            for step in range(1, steps + 1):
                # Centered classical finite differences
                d2_x = np.zeros_like(U)
                d2_x[:, 1:-1] = (U[:, 2:] - 2*U[:, 1:-1] + U[:, :-2]) / dx**2
                d2_x[:, 0] = d2_x[:, 1]
                d2_x[:, -1] = d2_x[:, -2]
                
                d2_y = np.zeros_like(U)
                d2_y[1:-1, :] = (U[2:, :] - 2*U[1:-1, :] + U[:-2, :]) / dy**2
                d2_y[0, :] = d2_y[1, :]
                d2_y[-1, :] = d2_y[-2, :]
                
                Lap = Y_grid.T**2 * (d2_x + d2_y)
                U += dtau * Lap
                U = np.clip(U, 0.0, None)
                
        else:
            # Algebraically native quantum geometric lattice
            # Exponents list: from -40 to 15
            powers = np.arange(-40, 16)
            L = len(powers)
            
            # Positive branch of R_q: X_pos = sorted q**powers
            X_pos = np.sort(q_val ** powers)
            # Negative branch of R_q: X_neg = -X_pos[::-1] (furthest to closest to zero)
            X_neg = - X_pos[::-1]
            
            # Concatenate to form the full strictly increasing quantum real line R_q
            X = np.concatenate([X_neg, X_pos])
            Nx = len(X)
            
            # Positive half-line R_q^+ for the y-axis
            j_exps = np.arange(-33, 20)
            Y = np.sort(q_val ** j_exps)
            Ny = len(Y)
            
            X_grid, Y_grid = np.meshgrid(X, Y, indexing='ij')
            sigma2 = 0.018
            U = np.exp(-(X_grid**2 + (Y_grid - 1.0)**2) / (2.0 * sigma2))
            U /= np.sum(U)
            U = U.T  # Shape (Ny, Nx)
            
            dtau = 1e-5
            steps = 500  # Total time = 0.005 s
            
            print(f"  Lattice sizes: Nx = {Nx} (2 x {L}), Ny = {Ny}")
            print(f"  Gap around x = 0 is [-{X_pos[0]:.5f}, {X_pos[0]:.5f}]")
            print(f"  y range: [{Y[0]:.5f}, {Y[-1]:.5f}]")
            print(f"  Integrating {steps} steps of dtau = {dtau}...")
            
            # Set up pre-computed index shifts for Jackson derivatives
            idx_qx = np.zeros(Nx, dtype=int)
            idx_q2x = np.zeros(Nx, dtype=int)
            
            if q_val > 1.0:
                # Positive branch (k >= L): scale by q moves right (k+1, k+2)
                idx_qx[L:] = np.clip(np.arange(L, Nx) + 1, 0, Nx - 1)
                idx_q2x[L:] = np.clip(np.arange(L, Nx) + 2, 0, Nx - 1)
                # Negative branch (k < L): scale by q moves left (k-1, k-2)
                idx_qx[:L] = np.clip(np.arange(0, L) - 1, 0, Nx - 1)
                idx_q2x[:L] = np.clip(np.arange(0, L) - 2, 0, Nx - 1)
            else:
                # Positive branch (k >= L): scale by q moves left (k-1, k-2)
                idx_qx[L:] = np.clip(np.arange(L, Nx) - 1, 0, Nx - 1)
                idx_q2x[L:] = np.clip(np.arange(L, Nx) - 2, 0, Nx - 1)
                # Negative branch (k < L): scale by q moves right (k+1, k+2)
                idx_qx[:L] = np.clip(np.arange(0, L) + 1, 0, Nx - 1)
                idx_q2x[:L] = np.clip(np.arange(0, L) + 2, 0, Nx - 1)
                
            idx_qy = np.zeros(Ny, dtype=int)
            idx_q2y = np.zeros(Ny, dtype=int)
            
            if q_val > 1.0:
                idx_qy = np.clip(np.arange(Ny) + 1, 0, Ny - 1)
                idx_q2y = np.clip(np.arange(Ny) + 2, 0, Ny - 1)
            else:
                idx_qy = np.clip(np.arange(Ny) - 1, 0, Ny - 1)
                idx_q2y = np.clip(np.arange(Ny) - 2, 0, Ny - 1)
                
            Y_grid_T = Y_grid.T
            X_grid_T = X_grid.T
            
            denom_x = q_val * (q_val - 1.0)**2 * X_grid_T**2
            denom_y = q_val * (q_val - 1.0)**2 * Y_grid_T**2
            
            for step in range(1, steps + 1):
                # Vectorized Jackson derivatives using index arrays
                U_qx = U[:, idx_qx]
                U_q2x = U[:, idx_q2x]
                d2_qx = (U_q2x - (1.0 + q_val) * U_qx + q_val * U) / denom_x
                
                U_qy = U[idx_qy, :]
                U_q2y = U[idx_q2y, :]
                d2_qy = (U_q2y - (1.0 + q_val) * U_qy + q_val * U) / denom_y
                
                # Couple the positive and negative branches across x=0
                # flow matches standard symmetric boundary condition
                dx_gap = X[L] - X[L-1]
                gap_flux = (U[:, L] - U[:, L-1]) / dx_gap
                d2_qx[:, L-1] += gap_flux / dx_gap
                d2_qx[:, L] -= gap_flux / dx_gap
                
                Lap = Y_grid_T**2 * (d2_qx + d2_qy)
                U += dtau * Lap
                U = np.clip(U, 0.0, None)
                
        # ------------------------------------------------------------------
        # Step 4: Plotting the Quantum Heat Distribution
        # ------------------------------------------------------------------
        ax = axes[ax_idx]
        
        # Create a contour plot in physical coordinates
        im = ax.contourf(X, Y, U, levels=40, cmap='inferno')
        ax.plot(0, 1.0, 'w+', markersize=10, markeredgewidth=1.5)
        
        title = "q = 1.0 (Classical Limit)" if is_classical else f"q = {q_val} (Quantum Lattice)"
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel("Quantum x Coordinate", fontsize=11)
        if ax_idx == 0:
            ax.set_ylabel("Quantum y Coordinate", fontsize=11)
            
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(0.3, 1.8)
        ax.grid(True, linestyle=':', alpha=0.3)
        
    # Global title and colorbar
    fig.suptitle("Algebraically Native Geometric q-Lattice Heat Propagation", 
                 fontsize=15, fontweight='bold', y=0.98)
    
    # Colorbar
    cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.025])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label("Spectral Heat Density u(x, y, \u03c4)", fontsize=11, fontweight='bold')
    
    plot_path = "media/quantum_native_lattice_heat.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("-" * 65)
    print(f"Sovereign q-Lattice Simulation complete! Plot saved to: {plot_path}")
    print("=================================================================")

if __name__ == "__main__":
    run_native_lattice_heat_simulation()
