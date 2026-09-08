#!/usr/bin/env python3
"""
SAGE-Banting Quantum Maass Waveform & Spectral Diagonalization Suite.

1. Constructs the algebraically native, symmetric, tridiagonal q-deformed
   Laplace-Beltrami operator Delta_q on the geometric q-lattice.
2. Diagonalizes the operator to compute the exact discrete eigenvalues and
   hypergeometric eigenfunctions (quantum Maass waveforms) under Dirichlet boundary conditions.
3. Compares the spectral shifting and dimensional symmetry breaking for
   q = 0.94, q = 1.0, and q = 1.06.
4. Saves a beautiful comparative spectral visualization to media/quantum_maass_waveforms.png.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def run_spectral_diagonalization():
    print("=================================================================")
    print("  SAGE-BANTING QUANTUM MAASS WAVEFORM SPECTRAL DIAGONALIZATION")
    print("=================================================================")
    
    # ------------------------------------------------------------------
    # Step 1: Set up q-Lattice Grid and Parameters
    # ------------------------------------------------------------------
    q_values = [0.94, 1.0, 1.06]
    Ny = 80  # Dimension of our spectral Hilbert space
    
    # We will plot the first 4 eigenfunctions for each q
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    plt.subplots_adjust(hspace=0.25)
    
    for idx, q_val in enumerate(q_values):
        print(f"\nDiagonalizing Delta_q for non-commutative parameter q = {q_val}...")
        
        # 1. Coordinate Grid y in Poincare Upper Half-Plane
        # To make a clean comparison, we define y in [0.3, 1.8]
        if np.abs(q_val - 1.0) < 1e-4:
            # Classical limit: uniform grid
            Y = np.linspace(0.3, 1.8, Ny)
            dy = Y[1] - Y[0]
            
            # Construct standard symmetric tridiagonal classical Laplacian matrix
            # Delta = y**2 * d**2/dy**2
            M = np.zeros((Ny - 2, Ny - 2))
            for j in range(Ny - 2):
                y_val = Y[j + 1]
                # Diagonal
                M[j, j] = -2.0 * y_val**2 / dy**2
                # Off-diagonals
                if j > 0:
                    M[j, j - 1] = y_val**2 / dy**2
                if j < Ny - 3:
                    M[j, j + 1] = y_val**2 / dy**2
                    
        else:
            # Symmetric centered q-discretization on geometric q-lattice
            # Y_j = y_0 * q**j
            j_exps = np.linspace(-15, 15, Ny)
            Y = 0.3 * (q_val ** (j_exps - j_exps[0])) # Map grid to [0.3, ~1.8]
            Y = np.sort(Y)
            
            # Construct tridiagonal q-Laplacian matrix
            # Under centered q-derivative, Delta_q = y**2 * d2_qy
            # d2_qy U(y_j) = (U(y_{j+1}) - 2*U(y_j) + U(y_{j-1})) / ((q - q**-1)**2 * y_j**2)
            # Notice the y_j**2 cancels beautifully with Poincare's y**2 scaling,
            # leaving constant tridiagonal coefficients (spectral scale-invariance)!
            M = np.zeros((Ny - 2, Ny - 2))
            denom = (q_val - 1.0 / q_val)**2
            
            for j in range(Ny - 2):
                # Diagonal
                M[j, j] = -2.0 / denom
                # Off-diagonals
                if j > 0:
                    M[j, j - 1] = 1.0 / denom
                if j < Ny - 3:
                    M[j, j + 1] = 1.0 / denom
                    
        # ------------------------------------------------------------------
        # Step 2: Solve the Hermitian Eigenproblem
        # ------------------------------------------------------------------
        # eigh solves the symmetric eigenvalue problem: M * v = lambda * v
        eigenvalues, eigenvectors = np.linalg.eigh(M)
        
        # Sort by eigenvalue magnitude (Maass waveforms are ordered by increasing frequency)
        # Note: eigenvalues are negative, so we sort in descending order (closest to 0 first)
        sort_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sort_indices]
        eigenvectors = eigenvectors[:, sort_indices]
        
        # Print first 5 eigenvalues
        print("  First 5 Quantum Maass Eigenvalues:")
        for k in range(5):
            print(f"    \u03bb_{k} = {eigenvalues[k]:.6f}")
            
        # ------------------------------------------------------------------
        # Step 3: Plot the First 4 Maass Waveforms (Eigenvectors)
        # ------------------------------------------------------------------
        ax = axes[idx]
        Y_interior = Y[1:-1]
        
        colors = ['crimson', 'royalblue', 'forestgreen', 'darkorange']
        for k in range(4):
            # Normalize the waveform for clean plotting
            wave = eigenvectors[:, k]
            wave /= np.max(np.abs(wave))
            # Fix sign phase for visual consistency (ensure start is positive)
            if wave[5] < 0:
                wave = -wave
                
            ax.plot(Y_interior, wave, color=colors[k], linewidth=2, label=f"Mode {k+1} (\u03bb = {eigenvalues[k]:.3f})")
            
        title = "Classical Laplace-Beltrami Spectrum (q = 1.0)" if np.abs(q_val - 1.0) < 1e-4 else f"q-Deformed Laplace-Beltrami Spectrum (q = {q_val})"
        ax.set_title(title, fontsize=12, fontweight='bold', pad=8)
        ax.set_ylabel("Waveform Amplitude", fontsize=10)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.legend(loc="upper right", frameon=True, fontsize=9)
        
    axes[-1].set_xlabel("Hyperbolic Coordinate y", fontsize=11)
    fig.suptitle("Quantum Maass Waveforms & Scale-Invariant Spectral Diagonalization", 
                 fontsize=15, fontweight='bold', y=0.98)
    
    plot_path = "media/quantum_maass_waveforms.png"
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print("-" * 65)
    print(f"Spectral Diagonalization complete! Figure saved to: {plot_path}")
    print("=================================================================")

if __name__ == "__main__":
    run_spectral_diagonalization()
