#!/usr/bin/env python3
"""
SAGE-Banting Quantum Conformal Boundary Scaling & CFT Exponent Extractor.

Computes the q-commutator Frobenius norm leakage as a function of the spectral 
truncation dimension N (from N = 4 to 20).
Fits a power-law E(N) ~ C * N**(-alpha) to extract the exact scaling exponent alpha, 
providing a direct numerical window onto the boundary conformal field theory (CFT)
regularity of the q-deformed Poincaré upper half-plane.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from scipy.optimize import curve_fit

def extract_conformal_scaling_exponent():
    print("=================================================================")
    print("  SAGE-BANTING SPECTRAL LEAKAGE SCALING & BOUNDARY CFT EXTRACTION")
    print("=================================================================")
    
    q_val = 1.05
    powers_x = np.arange(-20, 11)
    powers_y = np.arange(-18, 15)
    
    Lx = len(powers_x)
    X_pos = np.sort(q_val ** powers_x)
    X_neg = - X_pos[::-1]
    X = np.concatenate([X_neg, X_pos])
    Nx = len(X)
    
    Y = np.sort(q_val ** powers_y)
    Ny = len(Y)
    N_tot = Nx * Ny
    
    # 1. Re-construct the symmetric 2D quantum Laplacian M_int
    A = sp.lil_matrix((N_tot, N_tot))
    denom = (q_val - 1.0 / q_val)**2
    dx_gap = X[Lx] - X[Lx-1]
    
    idx_qx = np.clip(np.arange(Nx) + 1, 0, Nx - 1)
    idx_q_inv_x = np.clip(np.arange(Nx) - 1, 0, Nx - 1)
    idx_qy = np.clip(np.arange(Ny) + 1, 0, Ny - 1)
    idx_q_inv_y = np.clip(np.arange(Ny) - 1, 0, Ny - 1)
    
    for j in range(Ny):
        y_val = Y[j]
        for i in range(Nx):
            p = i + j * Nx
            p_next_x = idx_qx[i] + j * Nx
            p_prev_x = idx_q_inv_x[i] + j * Nx
            
            coef_x_next = y_val**2 / (denom * X[i] * X[idx_qx[i]])
            coef_x_prev = y_val**2 / (denom * X[i] * X[idx_q_inv_x[i]])
            
            if idx_qx[i] != i:
                A[p, p_next_x] = coef_x_next
            if idx_q_inv_x[i] != i:
                A[p, p_prev_x] = coef_x_prev
                
            A[p, p] += -2.0 * y_val**2 / (denom * X[i]**2)
            
            p_next_y = i + idx_qy[j] * Nx
            p_prev_y = i + idx_q_inv_y[j] * Nx
            
            if idx_qy[j] != j:
                A[p, p_next_y] = 1.0 / denom
            if idx_q_inv_y[j] != j:
                A[p, p_prev_y] = 1.0 / denom
                
            A[p, p] += -2.0 / denom
            
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
                
    A = (A + A.T) / 2.0
    
    interior_indices = []
    for j in range(1, Ny - 1):
        for i in range(1, Nx - 1):
            interior_indices.append(i + j * Nx)
            
    M_int = A[interior_indices, :][:, interior_indices].tocsc()
    
    # 2. Extract spatial coordinate grids for interior nodes
    X_int = np.zeros(len(interior_indices))
    Y_int = np.zeros(len(interior_indices))
    for idx, p in enumerate(interior_indices):
        i = p % Nx
        j = p // Nx
        X_int[idx] = X[i]
        Y_int[idx] = Y[j]
        
    # We will test N from 4 to 20 in steps of 2
    N_list = np.arange(4, 22, 2)
    leaks = []
    standard_comms = []
    
    # Solve once for the max N = 20 eigenvectors
    max_N = np.max(N_list)
    print(f"Solving for the first {max_N} Maass wavefunctions to compute truncation sequence...")
    eigenvalues, eigenvectors_int = sla.eigsh(M_int, k=max_N, which='SM')
    sort_idx = np.argsort(eigenvalues)[::-1]
    eigenvectors_int = eigenvectors_int[:, sort_idx]
    
    print("\nTracing Conformal Truncation Leakage vs Basis Dimension N:")
    for N in N_list:
        # Select first N eigenvectors
        V_N = eigenvectors_int[:, :N]
        
        # Project coordinate operators onto N x N basis
        # X_op[n, m] = sum_p v_n[p] * X_p * v_m[p]
        X_op = V_N.T @ (X_int[:, np.newaxis] * V_N)
        Y_op = V_N.T @ (Y_int[:, np.newaxis] * V_N)
        
        # Compute q-commutator norm
        q_comm = Y_op @ X_op - q_val * X_op @ Y_op
        standard_comm = Y_op @ X_op - X_op @ Y_op
        
        norm_q_comm = np.linalg.norm(q_comm)
        norm_std_comm = np.linalg.norm(standard_comm)
        
        leaks.append(norm_q_comm)
        standard_comms.append(norm_std_comm)
        print(f"  N = {N:2d} | Std Commutator Norm: {norm_std_comm:.6f} | q-Commutator Norm: {norm_q_comm:.6f}")
        
    leaks = np.array(leaks)
    standard_comms = np.array(standard_comms)
    
    # 3. Fit power law E(N) = C * N**(-alpha)
    # log(E) = log(C) - alpha * log(N)
    def power_law(N, C, alpha):
        return C * N**(-alpha)
        
    popt_q, pcov_q = curve_fit(power_law, N_list, leaks, p0=[1.0, 1.0])
    popt_std, pcov_std = curve_fit(power_law, N_list, standard_comms, p0=[1.0, 1.0])
    
    print("\nPower Law Fitting Results [E(N) = C * N**(-\u03b1)]:")
    print(f"  q-Commutator Scale C:       {popt_q[0]:.4f}")
    print(f"  q-Commutator Exponent \u03b1:   {popt_q[1]:.4f}")
    print(f"  Std Commutator Scale C:     {popt_std[0]:.4f}")
    print(f"  Std Commutator Exponent \u03b1: {popt_std[1]:.4f}")
    
    print("\nConformal Regularity Verdict:")
    print(f"  The extracted scaling exponent of the q-commutator is \u03b1 = {popt_q[1]:.4f}.")
    if popt_q[1] >= 1.5:
        print("  \u03b1 >= 1.5: High Sobolev regularity. The coordinate multiplication operators are extremely smooth")
        print("  relative to the domain of the q-deformed Laplacian (H^2/H^1 trace bound).")
    else:
        print("  \u03b1 < 1.5: Power-law decay is dominated by the Dirichlet conformal boundary CFT,")
        print("  reflecting the topological edge states of the quantum plane (L^2 trace bound).")
    print("=================================================================")

if __name__ == "__main__":
    extract_conformal_scaling_exponent()
