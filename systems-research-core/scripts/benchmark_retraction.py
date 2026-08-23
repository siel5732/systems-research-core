#!/usr/bin/env python3
"""
scripts/benchmark_retraction.py

Micro-benchmark to compare original, fast-inv-sqrt, and einsum-vectorized
retraction implementations on GEEKOM bare-metal CPU.
"""

import time
import numpy as np

# Original Implementation
def retract_to_ob35_original(P: np.ndarray) -> np.ndarray:
    col_norms = np.linalg.norm(P, axis=0)
    col_norms = np.where(col_norms < 1e-12, 1e-12, col_norms)
    return P / col_norms

# 1. Fast Inverse Square Root (vectorized in NumPy)
def fast_inv_sqrt(x: np.ndarray) -> np.ndarray:
    x_f32 = x.astype(np.float32)
    i = x_f32.view(np.int32)
    i = np.array(0x5f3759df, dtype=np.int32) - (i >> 1)
    y = i.view(np.float32)
    # One Newton-Raphson iteration
    y = y * (1.5 - 0.5 * x_f32 * y * y)
    return y.astype(np.float64)

def retract_to_ob35_fast_inv(P: np.ndarray) -> np.ndarray:
    sq_norms = np.sum(P * P, axis=0)
    # Ensure no division by zero before inv_sqrt
    sq_norms = np.maximum(sq_norms, 1e-24)
    inv_norms = fast_inv_sqrt(sq_norms)
    return P * inv_norms[None, :]

# 2. Einstein Summation Vectorized (einsum)
def retract_to_ob35_einsum(P: np.ndarray) -> np.ndarray:
    sq_norms = np.einsum('ij,ij->j', P, P)
    inv_norms = 1.0 / np.sqrt(np.maximum(sq_norms, 1e-24))
    return P * inv_norms[None, :]


if __name__ == '__main__':
    # Initialize a typical random scheduler matrix on OB(3,5)
    np.random.seed(42)
    P_base = np.random.randn(3, 5)
    
    iterations = 500000
    print(f"Starting micro-benchmarking over {iterations:,} iterations...\n")
    
    # Benchmark Original
    t0 = time.perf_counter()
    P_test = P_base.copy()
    for _ in range(iterations):
        P_test = retract_to_ob35_original(P_test)
    t_orig = time.perf_counter() - t0
    err_orig = np.max(np.abs(np.linalg.norm(P_test, axis=0) - 1.0))
    print(f"Original: {t_orig:6.4f} seconds | Error: {err_orig:.2e}")
    
    # Benchmark Fast Inverse Square Root
    t0 = time.perf_counter()
    P_test = P_base.copy()
    for _ in range(iterations):
        P_test = retract_to_ob35_fast_inv(P_test)
    t_fast = time.perf_counter() - t0
    err_fast = np.max(np.abs(np.linalg.norm(P_test, axis=0) - 1.0))
    print(f"Fast-Inv: {t_fast:6.4f} seconds | Error: {err_fast:.2e} (Speedup: {t_orig/t_fast:.2f}x)")
    
    # Benchmark Einstein Summation
    t0 = time.perf_counter()
    P_test = P_base.copy()
    for _ in range(iterations):
        P_test = retract_to_ob35_einsum(P_test)
    t_ein = time.perf_counter() - t0
    err_ein = np.max(np.abs(np.linalg.norm(P_test, axis=0) - 1.0))
    print(f"Einsum:   {t_ein:6.4f} seconds | Error: {err_ein:.2e} (Speedup: {t_orig/t_ein:.2f}x)")
