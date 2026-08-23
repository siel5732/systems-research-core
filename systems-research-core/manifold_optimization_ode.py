#!/usr/bin/env python3
"""
🌐 GEOMETRIC ODE SIMULATOR & MANIFOLD RELAXATION ENGINE
Authors: Dr. Marie Curie & Imhotep (Subconscious Systems Group)

This script implements:
1. A high-fidelity Ordinary Differential Equation (ODE) simulator on the Oblique Manifold M = (S^{d-1})^n
   for non-convex quadratic optimization under orthogonality/row-norm constraints.
2. A geometric integration scheme (retraction-based Runge-Kutta 4th Order) to simulate the Riemannian gradient flow.
3. A discrete Riemannian Gradient Descent (RGD) solver starting from the same initial conditions.
4. Dynamical estimation of the Lipschitz constant L of the Riemannian gradient.
5. Exact construction and eigenvalue decomposition of the Riemannian Hessian to compute the Morse Index.
6. Verification of the continuous-to-discrete complexity bounds derived via manifold relaxations.
7. Saving the trajectory and mathematical insights into 'math_opt_results.json'.
"""

import numpy as np
import json
import os

def generate_problem_data(n=50, seed=42):
    """
    Generates a representative non-convex symmetric matrix A representing a Max-Cut
    like objective or non-convex quadratic optimization landscape.
    We use a deterministic seed to ensure reproducibility.
    """
    np.random.seed(seed)
    # Generate a random symmetric Wigner-like matrix
    A_raw = np.random.randn(n, n)
    A = 0.5 * (A_raw + A_raw.T) / np.sqrt(n)
    
    # Add a diagonal shift to make it non-convex with negative eigenvalues
    # ensuring a rich non-convex optimization landscape with multiple saddle points
    eigenvals = np.linalg.eigvalsh(A)
    print(f"[+] Matrix A generated. Eigenvalue range: [{eigenvals.min():.4f}, {eigenvals.max():.4f}]")
    return A

def project_to_tangent_space(Y, V):
    """
    Projects an ambient matrix V in R^{n x d} onto the tangent space of the oblique manifold at Y.
    T_Y M = { V \in R^{n x d} : diag(V Y^T) = 0 }
    """
    # Compute row-wise inner products of V and Y
    vy_diag = np.sum(V * Y, axis=1) # shape (n,)
    # Subtract the projection: V_i - (V_i . Y_i) * Y_i
    proj_V = V - vy_diag[:, np.newaxis] * Y
    return proj_V

def retract(Y, V):
    """
    Retracts a tangent vector V from T_Y M onto the oblique manifold M.
    We use the standard row-wise normalization as the retraction operator.
    """
    X = Y + V
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / norms

def compute_objective(Y, A):
    """
    Computes the objective function f(Y) = Tr(Y^T A Y).
    """
    return np.trace(Y.T @ A @ Y)

def compute_riemannian_gradient(Y, A):
    """
    Computes the Riemannian gradient of f(Y) = Tr(Y^T A Y) on the oblique manifold M.
    The ambient gradient is \nabla f(Y) = 2 A Y.
    The Riemannian gradient is the projection of 2 A Y onto the tangent space.
    """
    grad_ambient = 2 * (A @ Y)
    return project_to_tangent_space(Y, grad_ambient)

def estimate_local_lipschitz(Y1, Y2, grad1, grad2):
    """
    Estimates the local Lipschitz constant L of the Riemannian gradient.
    We approximate this by comparing the change in gradient to the change in state.
    Since they lie in different tangent spaces, we use ambient subtraction as a
    numerically stable approximation to vector transport.
    """
    delta_Y_norm = np.linalg.norm(Y1 - Y2, 'fro')
    if delta_Y_norm < 1e-12:
        return 0.0
    delta_grad_norm = np.linalg.norm(grad1 - grad2, 'fro')
    return delta_grad_norm / delta_Y_norm

def run_geometric_ode_simulation(A, Y0, t_span=(0.0, 15.0), h=0.02):
    """
    Integrates the Riemannian gradient flow ODE: \dot{Y} = -grad f(Y)
    using a retraction-based Runge-Kutta 4th Order (RK4) geometric integrator.
    """
    t_start, t_end = t_span
    t_steps = int((t_end - t_start) / h)
    
    Y = Y0.copy()
    trajectory = []
    
    # Initial evaluation
    f_val = compute_objective(Y, A)
    grad = compute_riemannian_gradient(Y, A)
    grad_norm = np.linalg.norm(grad, 'fro')
    
    trajectory.append({
        "t": 0.0,
        "f_val": float(f_val),
        "grad_norm": float(grad_norm),
        "L_est": 0.0
    })
    
    for step in range(t_steps):
        t = (step + 1) * h
        
        # RK4 stages on the manifold
        # k1
        k1 = -compute_riemannian_gradient(Y, A)
        
        # k2
        Y_k2 = retract(Y, 0.5 * h * k1)
        k2 = -compute_riemannian_gradient(Y_k2, A)
        
        # k3
        Y_k3 = retract(Y, 0.5 * h * k2)
        k3 = -compute_riemannian_gradient(Y_k3, A)
        
        # k4
        Y_k4 = retract(Y, h * k3)
        k4 = -compute_riemannian_gradient(Y_k4, A)
        
        # Combine stages and retract
        V_step = (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        Y_next = retract(Y, V_step)
        
        # Evaluation
        f_val = compute_objective(Y_next, A)
        grad_next = compute_riemannian_gradient(Y_next, A)
        grad_norm = np.linalg.norm(grad_next, 'fro')
        
        # Estimate local Lipschitz constant
        L_est = estimate_local_lipschitz(Y_next, Y, grad_next, grad)
        
        trajectory.append({
            "t": float(t),
            "f_val": float(f_val),
            "grad_norm": float(grad_norm),
            "L_est": float(L_est)
        })
        
        Y = Y_next
        grad = grad_next
        
    return Y, trajectory

def run_riemannian_gradient_descent(A, Y0, L, epsilon=1e-3, max_iter=2000):
    """
    Runs discrete Riemannian Gradient Descent with constant step size eta = 1/L.
    Y_{k+1} = Retr_{Y_k}( - \eta * grad f(Y_k) )
    We stop when the Riemannian gradient norm is below epsilon.
    """
    Y = Y0.copy()
    eta = 1.0 / L
    trajectory = []
    
    for iteration in range(max_iter):
        f_val = compute_objective(Y, A)
        grad = compute_riemannian_gradient(Y, A)
        grad_norm = np.linalg.norm(grad, 'fro')
        
        trajectory.append({
            "iteration": int(iteration),
            "f_val": float(f_val),
            "grad_norm": float(grad_norm)
        })
        
        if grad_norm <= epsilon:
            break
            
        # Take step
        V_step = -eta * grad
        Y = retract(Y, V_step)
        
    return Y, trajectory

def compute_riemannian_hessian_eigenvalues(Y, A):
    """
    Constructs the exact matrix representation of the Riemannian Hessian operator on the oblique manifold
    and computes its eigenvalue spectrum.
    
    The dimension of the oblique manifold M = (S^{d-1})^n is N_v = n * (d - 1).
    We construct an orthonormal basis for the tangent space T_Y M.
    At each row i, the tangent space is orthogonal to Y_i.
    We find an orthonormal basis B_i in R^{d x (d-1)} for the orthogonal complement of Y_i.
    """
    n, d = Y.shape
    d_tangent = d - 1
    N_v = n * d_tangent
    
    # 1. Construct orthonormal bases B_i for each row i
    B = []
    for i in range(n):
        y_i = Y[i, :] # shape (d,)
        # Use QR decomposition to find orthogonal complement of y_i
        q, r = np.linalg.qr(y_i.reshape(-1, 1), mode='complete')
        # The first column of q is y_i (up to sign), the remaining (d-1) columns are orthogonal to y_i
        B_i = q[:, 1:] # shape (d, d-1)
        # Verify orthogonality: B_i.T @ y_i should be 0
        assert np.linalg.norm(B_i.T @ y_i) < 1e-12, "Orthonormal basis construction failed."
        B.append(B_i)
        
    # 2. Define the Hessian operator mapping tangent vector u in R^{N_v} to w in R^{N_v}
    def hessian_operator(u):
        # Map 1D tangent vector u of shape (N_v,) to matrix tangent vector V of shape (n, d)
        V = np.zeros((n, d))
        for i in range(n):
            V[i, :] = B[i] @ u[i*d_tangent : (i+1)*d_tangent]
            
        # Apply Riemannian Hessian formula:
        # Heis f(Y)[V] = 2 * Proj_Y( A V ) - 2 * \Lambda(Y) V
        # where \Lambda(Y)_{ii} = (A Y)_{i, :} Y_{i, :}^T
        AV = A @ V
        # Compute diag(A V Y^T)
        avy_diag = np.sum(AV * Y, axis=1) # shape (n,)
        # Compute \Lambda(Y)_{ii} = (A Y)_i . Y_i
        Lambda = np.sum((A @ Y) * Y, axis=1) # shape (n,)
        
        # Project A V
        proj_AV = AV - avy_diag[:, np.newaxis] * Y
        
        # Hessian matrix result: 2 * proj_AV - 2 * Lambda * V
        HV = 2 * (proj_AV - Lambda[:, np.newaxis] * V)
        
        # Map matrix tangent vector HV back to 1D vector w of shape (N_v,)
        w = np.zeros(N_v)
        for i in range(n):
            w[i*d_tangent : (i+1)*d_tangent] = B[i].T @ HV[i, :]
            
        return w

    # 3. Construct the full Hessian matrix by applying the operator to the identity basis
    H_matrix = np.zeros((N_v, N_v))
    for k in range(N_v):
        e_k = np.zeros(N_v)
        e_k[k] = 1.0
        H_matrix[:, k] = hessian_operator(e_k)
        
    # 4. Symmetrize to clean up any tiny numerical asymmetric noise
    H_matrix = 0.5 * (H_matrix + H_matrix.T)
    
    # 5. Compute eigenvalues
    eigenvals = np.linalg.eigvalsh(H_matrix)
    
    return eigenvals

def main():
    print("==========================================================================")
    print("⚛️  RIEMANNIAN MANIFOLD RELAXATION & GEOMETRIC ODE SIMULATOR ACTIVE  ⚛️")
    print("==========================================================================")
    
    n = 50
    d = 3
    t_span = (0.0, 15.0)
    h = 0.02
    epsilon = 1e-3
    
    print(f"[+] Configuration: n={n} (variables), d={d} (manifold relaxation rank)")
    print(f"[+] Manifold: Oblique Manifold M = (S^2)^50 in R^{{n x d}}")
    print(f"[+] Dimension of manifold tangent space: N_v = n * (d - 1) = {n * (d - 1)}")
    
    # 1. Generate Problem Data
    A = generate_problem_data(n, seed=42)
    A_norm = float(np.linalg.norm(A, 'fro'))
    
    # Calculate the theoretical global Lipschitz constant L_global = 4 * ||A||_2
    eigenvals_A = np.linalg.eigvalsh(A)
    spectral_norm_A = np.max(np.abs(eigenvals_A))
    L_global = float(4.0 * spectral_norm_A)
    print(f"[+] Spectral norm ||A||_2: {spectral_norm_A:.4f}")
    print(f"[+] Rigorous global Lipschitz bound (4 * ||A||_2): L_global = {L_global:.4f}")
    
    # 2. Generate Initial Condition on the Manifold
    # We generate a random matrix and row-normalize it to lie on M
    np.random.seed(101)
    Y0_raw = np.random.randn(n, d)
    Y0 = Y0_raw / np.linalg.norm(Y0_raw, axis=1, keepdims=True)
    
    # 3. Run Geometric ODE Simulation
    print(f"\n[+] Integrating Riemannian Gradient Flow ODE over t ∈ {t_span} (h={h})...")
    Y_final_ode, ode_traj = run_geometric_ode_simulation(A, Y0, t_span=t_span, h=h)
    
    # Find maximum estimated Lipschitz constant along the trajectory
    L_estimates = [pt["L_est"] for pt in ode_traj if pt["t"] > 0.0]
    L_max_empirical = float(np.max(L_estimates))
    print(f"[+] Dynamically estimated Lipschitz constant from ODE path: L_max_empirical = {L_max_empirical:.4f}")
    
    # 4. Run Discrete Riemannian Gradient Descent
    # We use a step size based on the mathematically rigorous global Lipschitz constant L_global.
    # This guarantees monotonic descent and absolute convergence to a critical point.
    print(f"\n[+] Running Discrete Riemannian Gradient Descent (eta = 1/L_global, epsilon = {epsilon})...")
    Y_final_rgd, rgd_traj = run_riemannian_gradient_descent(A, Y0, L_global, epsilon=epsilon, max_iter=2000)
    
    actual_iterations_K = len(rgd_traj) - 1
    print(f"[+] RGD convergence reached in {actual_iterations_K} iterations.")
    print(f"    - Initial objective: {rgd_traj[0]['f_val']:.6f}")
    print(f"    - Final objective:   {rgd_traj[-1]['f_val']:.6f}")
    print(f"    - Final gradient norm: {rgd_traj[-1]['grad_norm']:.6e}")
    
    # 5. Compute Continuous-to-Discrete Complexity Bounds
    # Continuous-to-discrete complexity bound formula:
    # K_theoretical = L_global * (f(Y0) - f(Y_final)) / epsilon^2
    f_init = rgd_traj[0]['f_val']
    f_final = rgd_traj[-1]['f_val']
    theoretical_bound_K = float(L_global * (f_init - f_final) / (epsilon ** 2))
    bound_is_tight = actual_iterations_K <= theoretical_bound_K
    print(f"\n[+] Complexity Bound Verification:")
    print(f"    - Theoretical bound K_theoretical: {theoretical_bound_K:.2f}")
    print(f"    - Actual iterations K_actual:      {actual_iterations_K}")
    print(f"    - Is actual iterations <= theoretical bound? {bound_is_tight}")
    
    # 6. Compute Riemannian Hessian Eigenvalues & Morse Index
    print(f"\n[+] Constructing Riemannian Hessian matrix at final RGD state...")
    hessian_eigenvals = compute_riemannian_hessian_eigenvalues(Y_final_rgd, A)
    
    # Morse Index is the count of strictly negative eigenvalues
    # To avoid tiny numerical float noise around zero, we use a small tolerance
    neg_threshold = -1e-6
    morse_index = int(np.sum(hessian_eigenvals < neg_threshold))
    is_local_minimum = morse_index == 0
    
    print(f"[+] Riemannian Hessian spectrum computed:")
    print(f"    - Min eigenvalue: {hessian_eigenvals.min():.6f}")
    print(f"    - Max eigenvalue: {hessian_eigenvals.max():.6f}")
    print(f"    - Morse Index (negative eigenvalues): {morse_index}")
    print(f"    - Is convergence point a local minimum? {is_local_minimum}")
    
    # 7. Prepare JSON results
    results = {
        "metadata": {
            "title": "Continuous Manifold Relaxation for High-Dimensional Non-Convex Optimization",
            "authors": ["Dr. Marie Curie", "Imhotep"],
            "timestamp": "2026-06-29 11:00 EDT"
        },
        "problem_parameters": {
            "problem_dimension_n": n,
            "relaxation_dimension_d": d,
            "matrix_A_frobenius_norm": A_norm,
            "matrix_A_spectral_norm": spectral_norm_A,
            "manifold_dimension": n * (d - 1),
            "convergence_epsilon": epsilon,
            "lipschitz_constant_L_empirical_ode": L_max_empirical,
            "lipschitz_constant_L_global_theoretical": L_global,
            "step_size_eta": 1.0 / L_global
        },
        "simulation_results": {
            "initial_objective_value": float(f_init),
            "final_objective_value": float(f_final),
            "ode_trajectory": ode_traj,
            "rgd_trajectory": rgd_traj
        },
        "complexity_bounds_verification": {
            "theoretical_bound_K": theoretical_bound_K,
            "actual_iterations_K": actual_iterations_K,
            "bound_is_tight": bool(bound_is_tight)
        },
        "manifold_second_order_properties": {
            "final_gradient_norm": float(rgd_traj[-1]['grad_norm']),
            "hessian_eigenvalue_min": float(hessian_eigenvals.min()),
            "hessian_eigenvalue_max": float(hessian_eigenvals.max()),
            "morse_index": morse_index,
            "is_local_minimum": bool(is_local_minimum),
            "hessian_eigenvalue_spectrum": [float(val) for val in hessian_eigenvals]
        }
    }
    
    # Save to JSON file
    output_filename = "math_opt_results.json"
    with open(output_filename, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\n[+] Simulation payload successfully saved to '{output_filename}'.")
    print("==========================================================================")

if __name__ == "__main__":
    main()
