#!/usr/bin/env python3
"""
SAGE-Banting Quantum Coordinate Operator Algebra Solver.

Computes the matrix elements of the non-commutative coordinate operators x and y 
in the exact 2D quantum Maass eigenbasis, directly implementing Grok's suggested check.
Quantifies the residual non-commutativity and algebraic relations of space in the
spectral representation.
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla

def compute_coordinate_operators():
    print("=================================================================")
    print("  SAGE-BANTING QUANTUM COORDINATE OPERATOR SPECTRAL MEASUREMENT")
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
    
    # Solve for first 6 eigenfunctions
    num_eigenvalues = 6
    eigenvalues, eigenvectors_int = sla.eigsh(M_int, k=num_eigenvalues, which='SM')
    sort_idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[sort_idx]
    eigenvectors_int = eigenvectors_int[:, sort_idx]
    
    # 2. Extract spatial coordinate grids for interior nodes
    X_int = np.zeros(len(interior_indices))
    Y_int = np.zeros(len(interior_indices))
    for idx, p in enumerate(interior_indices):
        i = p % Nx
        j = p // Nx
        X_int[idx] = X[i]
        Y_int[idx] = Y[j]
        
    # 3. Compute 6x6 matrix representations of coordinate operators X and Y
    # X_op[n, m] = sum_p v_n[p] * X_p * v_m[p]
    X_op = np.zeros((6, 6))
    Y_op = np.zeros((6, 6))
    
    for n in range(6):
        v_n = eigenvectors_int[:, n]
        for m in range(6):
            v_m = eigenvectors_int[:, m]
            X_op[n, m] = np.sum(v_n * X_int * v_m)
            Y_op[n, m] = np.sum(v_n * Y_int * v_m)
            
    print("\n[RESULT 1] Matrix representation of coordinate Operator X in Maass basis:")
    print(np.round(X_op, 5))
    
    print("\n[RESULT 2] Matrix representation of coordinate Operator Y in Maass basis:")
    print(np.round(Y_op, 5))
    
    # 4. Check the algebraic relation: Y_op * X_op - q * X_op * Y_op
    relation_matrix = Y_op @ X_op - q_val * X_op @ Y_op
    standard_commutator = Y_op @ X_op - X_op @ Y_op
    
    print("\n[RESULT 3] Standard Commutator [Y, X] in Maass basis:")
    print(np.round(standard_commutator, 5))
    
    print("\n[RESULT 4] q-Commutator (Y*X - q*X*Y) in Maass basis:")
    print(np.round(relation_matrix, 5))
    
    norm_comm = np.linalg.norm(standard_commutator)
    norm_q_comm = np.linalg.norm(relation_matrix)
    print("\nSpectral Measurement Summary:")
    print(f"  Frobenius norm of Standard Commutator [Y, X]: {norm_comm:.6f}")
    print(f"  Frobenius norm of q-Commutator [Y, X]_q:       {norm_q_comm:.6f}")
    print("=================================================================")

if __name__ == "__main__":
    compute_coordinate_operators()
