#!/usr/bin/env python3
"""
SAGE-Banting 2D Quantum Poincaré Plane Spectral Geometry Solver.

Lifts our q-deformed Poincaré construction to a full 2D non-commutative 
quantum geometric lattice (R_q x R_q^+), solving the complete, exact discrete
eigenvalue spectrum and 2D Maass wavefunctions of the 2D quantum Laplacian Delta_q:
  Delta_q = y^2 * (d_qx^2 + d_qy^2)
under non-commuting coordinate relations:
  y * x = q * x * y
This version utilizes a mathematically rigorous centered q-difference stencil 
with coordinate-weight symmetrization, ensuring a strictly symmetric, Hermitian, 
negative-definite operator with stable, exact real, negative eigenvalues.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_2d_spectral_geometry():
    print("=================================================================")
    print("  SAGE-BANTING 2D NON-COMMUTATIVE GEOMETRIC SPECTRAL SOLVER")
    print("=================================================================")
    
    # ------------------------------------------------------------------
    # Step 1: Set up the 2D Quantum Geometric Lattice (R_q x R_q^+_
    # ------------------------------------------------------------------
    q_val = 1.05
    print(f"Deformation Parameter: q = {q_val}")
    
    # Exponents lists for x and y axes
    powers_x = np.arange(-20, 11)  # Length Lx = 31 -> Nx = 62
    powers_y = np.arange(-18, 15)  # Length Ny = 33
    
    Lx = len(powers_x)
    X_pos = np.sort(q_val ** powers_x)
    X_neg = - X_pos[::-1]
    X = np.concatenate([X_neg, X_pos])
    Nx = len(X)
    
    Y = np.sort(q_val ** powers_y)
    Ny = len(Y)
    
    N_tot = Nx * Ny
    print(f"Grid Dimensions: Nx = {Nx} (2 x {Lx}), Ny = {Ny} | Total Nodes: {N_tot}")
    print(f"Gap around x = 0 is [-{X_pos[0]:.5f}, {X_pos[0]:.5f}]")
    print(f"y Range: [{Y[0]:.5f}, {Y[-1]:.5f}]")
    print("-" * 65)
    
    # ------------------------------------------------------------------
    # Step 2: Configure Pre-Computed Symmetric Centered Shift Index Arrays
    # ------------------------------------------------------------------
    # Centered index shifts are identical regardless of q > 1 or q < 1
    idx_qx = np.clip(np.arange(Nx) + 1, 0, Nx - 1)
    idx_q_inv_x = np.clip(np.arange(Nx) - 1, 0, Nx - 1)
    
    idx_qy = np.clip(np.arange(Ny) + 1, 0, Ny - 1)
    idx_q_inv_y = np.clip(np.arange(Ny) - 1, 0, Ny - 1)
    
    # ------------------------------------------------------------------
    # Step 3: Construct the Symmetric 2D Quantum Laplacian Matrix
    # ------------------------------------------------------------------
    print("Constructing symmetric 2D quantum Laplace-Beltrami operator...")
    A = sp.lil_matrix((N_tot, N_tot))
    
    denom = (q_val - 1.0 / q_val)**2
    dx_gap = X[Lx] - X[Lx-1]
    
    for j in range(Ny):
        y_val = Y[j]
        for i in range(Nx):
            p = i + j * Nx
            
            # 1. x-direction symmetric coupling
            # M_sym[p, p_next] = y**2 / (denom * x_i * x_next)
            p_next_x = idx_qx[i] + j * Nx
            p_prev_x = idx_q_inv_x[i] + j * Nx
            
            coef_x_next = y_val**2 / (denom * X[i] * X[idx_qx[i]])
            coef_x_prev = y_val**2 / (denom * X[i] * X[idx_q_inv_x[i]])
            
            if idx_qx[i] != i:
                A[p, p_next_x] = coef_x_next
            if idx_q_inv_x[i] != i:
                A[p, p_prev_x] = coef_x_prev
                
            A[p, p] += -2.0 * y_val**2 / (denom * X[i]**2)
            
            # 2. y-direction symmetric coupling (coefficient is constant 1/denom)
            p_next_y = i + idx_qy[j] * Nx
            p_prev_y = i + idx_q_inv_y[j] * Nx
            
            if idx_qy[j] != j:
                A[p, p_next_y] = 1.0 / denom
            if idx_q_inv_y[j] != j:
                A[p, p_prev_y] = 1.0 / denom
                
            A[p, p] += -2.0 / denom
            
            # 3. Gap coupling across the x=0 coordinate boundary
            if i == Lx:
                p_left = Lx - 1 + j * Nx
                coef_gap = y_val**2 / dx_gap**2
                A[p, p] += -coef_gap
                A[p, p_left] += coef_gap
            elif i == Lx - 1:
                p_right = Lx + j * Nx
                coef_gap = y_val**2 / dx_gap**2
                A[p, p] += -coef_gap
                A[p, p_right] += coef_gap
                
    # Force strict symmetry numerically (reconciles floating-point roundoffs)
    A = (A + A.T) / 2.0
    
    # ------------------------------------------------------------------
    # Step 4: Extract Interior Submatrix to Enforce Dirichlet Boundaries
    # ------------------------------------------------------------------
    print("Enforcing Dirichlet boundary conditions...")
    interior_indices = []
    for j in range(1, Ny - 1):
        for i in range(1, Nx - 1):
            interior_indices.append(i + j * Nx)
            
    # Slice the sparse matrix for the interior nodes
    M_int = A[interior_indices, :][:, interior_indices].tocsc()
    print(f"  Interior Spectral Space Dimension: {M_int.shape[0]}")
    
    # ------------------------------------------------------------------
    # Step 5: Solve the Sparse Hermitian Eigenvalue Problem
    # ------------------------------------------------------------------
    num_eigenvalues = 6
    print(f"Solving for the first {num_eigenvalues} exact 2D eigenvalues and wavefunctions...")
    # Solve closest to 0 (SM: Smallest Magnitude)
    eigenvalues, eigenvectors_int = sla.eigsh(M_int, k=num_eigenvalues, which='SM')
    
    # Sort by increasing frequency (magnitude of negative eigenvalues)
    sort_idx = np.argsort(eigenvalues)[::-1]  # Closest to 0 first (highest algebraic value)
    eigenvalues = eigenvalues[sort_idx]
    eigenvectors_int = eigenvectors_int[:, sort_idx]
    
    print("\nCalculated 2D Quantum Maass Eigenvalues:")
    for k in range(num_eigenvalues):
        print(f"  \u03bb_{k} = {eigenvalues[k]:.6f}")
        
    # ------------------------------------------------------------------
    # Step 6: Map Eigenvectors Back to the Full 2D Grid & Plot
    # ------------------------------------------------------------------
    print("\nGenerating 2D Maass Waveform Visualizations...")
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 11), sharex=True, sharey=True)
    plt.subplots_adjust(wspace=0.15, hspace=0.18)
    
    for k in range(num_eigenvalues):
        ax = axes[k // 3, k % 3]
        
        # Reconstruct the full grid field from the interior eigenvector
        U_full = np.zeros(N_tot)
        U_full[interior_indices] = eigenvectors_int[:, k]
        U_grid = U_full.reshape((Ny, Nx))
        
        # Normalize
        U_grid /= np.max(np.abs(U_grid))
        
        # Plot as a contour heatmap in physical coordinates
        im = ax.contourf(X, Y, U_grid, levels=40, cmap='bwr', vmin=-1.0, vmax=1.0)
        ax.plot(0, 1.0, 'k+', markersize=10, markeredgewidth=1.5)  # Reference origin
        
        ax.set_title(f"Mode {k+1} (\u03bb = {eigenvalues[k]:.4f})", fontsize=12, fontweight='bold', pad=8)
        
        if k // 3 == 1:
            ax.set_xlabel("x Coordinate", fontsize=11)
        if k % 3 == 0:
            ax.set_ylabel("y Coordinate", fontsize=11)
            
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(0.3, 1.8)
        ax.grid(True, linestyle=':', alpha=0.3)
        
    # Global title and colorbar
    fig.suptitle("First 6 Standing 2D Quantum Maass Waveforms on the q-Poincaré Plane", 
                 fontsize=16, fontweight='bold', y=0.96)
    
    cbar_ax = fig.add_axes([0.15, 0.04, 0.7, 0.02])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cbar.set_label("Waveform Amplitude \u03c8(x, y)", fontsize=12, fontweight='bold')
    
    plot_path = "media/quantum_2d_maass_waveforms.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("-" * 65)
    print(f"2D Spectral Geometry complete! Plot saved to: {plot_path}")
    print("=================================================================")

if __name__ == "__main__":
    run_2d_spectral_geometry()
