#!/usr/bin/env python3
"""
scripts/hermes_rx.py

Hermes-3.2 Live Socket Timing Channel Receiver.
Listens on UDP Port 18888, captures high-resolution timestamps, and executes
the SAGE PLL-Hardened, Hurst-Adaptive, and GF(2) Fountain FEC reconstruction.
Utilizes the production-grade SAGE Binary Packet Header (20 bytes).
"""

import sys
import os
import socket
import time
import struct
import math
import random
import hashlib
import hmac

# --- 1. CONFIGURATION LOAD ---
def load_calibrated_priors(config_path="configs/hermes_calibrated_prior.json"):
    defaults = {
        "latency_floor_ms": 93.3164,
        "body_fit_lognormal": {"mu": 0.896835, "sigma": 0.968162},
        "tail_fit_gpd": {"threshold_val_ms": 4.4082, "xi_shape": 1.537106, "scale_beta": 0.293660}
    }
    if not os.path.exists(config_path):
        return defaults
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
        return cfg
    except Exception:
        return defaults

# --- 2. HEAVY-TAILED CALIBRATED QUEUE PRIORS ---
def generate_calibrated_queue_delay(n_steps, priors):
    floor = priors["latency_floor_ms"]
    mu = priors["body_fit_lognormal"]["mu"]
    sigma = priors["body_fit_lognormal"]["sigma"]
    threshold = priors["tail_fit_gpd"]["threshold_val_ms"]
    xi = priors["tail_fit_gpd"]["xi_shape"]
    beta = priors["tail_fit_gpd"]["scale_beta"]
    
    rng = random.Random(101)
    queue_delays = []
    for _ in range(n_steps):
        if rng.random() < 0.85:
            jitter = rng.lognormvariate(mu, sigma)
        else:
            u = rng.random()
            u = max(0.001, min(u, 0.999))
            jitter = threshold + (beta / xi) * (math.pow(1.0 - u, -xi) - 1.0)
        jitter = min(jitter, 25.0)
        queue_delays.append(floor + jitter)
    return queue_delays

# --- 3. SYSTEMATIC BINARY FOUNTAIN FEC (GF(2) GE SOLVER) ---
def generate_systematic_g_matrix(seed_str, k=128, n=192):
    seed_hash = hashlib.sha256(seed_str.encode()).digest()
    rng = random.Random(seed_hash)
    G = []
    for r in range(k):
        row = [0] * k
        row[r] = 1
        G.append(row)
    for r in range(n - k):
        row = [rng.randint(0, 1) for _ in range(k)]
        G.append(row)
    return G

def gf2_gaussian_elimination(A, b):
    rows = len(A)
    cols = len(A[0]) if rows > 0 else 0
    if rows < cols:
        return None
    M = []
    for r in range(rows):
        M.append(list(A[r]) + [b[r]])
    lead = 0
    for r in range(cols):
        if lead >= cols:
            break
        pivot = r
        while M[pivot][lead] == 0:
            pivot += 1
            if pivot == rows:
                pivot = r
                lead += 1
                if lead == cols:
                    break
        if lead == cols:
            break
        M[r], M[pivot] = M[pivot], M[r]
        for i in range(rows):
            if i != r and M[i][lead] == 1:
                for c in range(lead, cols + 1):
                    M[i][c] ^= M[r][c]
        lead += 1
    x_sol = [0] * cols
    for r in range(cols):
        ones = [c for c in range(cols) if M[r][c] == 1]
        if len(ones) == 1:
            x_sol[ones[0]] = M[r][-1]
        else:
            return None
    return x_sol

def decode_fountain_fec(received_bits_dict, G_matrix):
    received_indices = sorted(list(received_bits_dict.keys()))
    if len(received_indices) < 128:
        print(f"    -> [FEC] Failure: Only {len(received_indices)} packets received. Min 128 required.")
        return ""
    A_sub = []
    b_sub = []
    for idx in received_indices:
        A_sub.append(G_matrix[idx])
        b_sub.append(received_bits_dict[idx])
    solved_bits = gf2_gaussian_elimination(A_sub, b_sub)
    if solved_bits is None:
        print("    -> [FEC] Failure: Systematic submatrix is singular.")
        return ""
    decoded_chars = []
    for i in range(0, len(solved_bits), 8):
        byte_bits = solved_bits[i:i+8]
        byte_str = "".join(str(b) for b in byte_bits)
        decoded_chars.append(chr(int(byte_str, 2)))
    return "".join(decoded_chars)

def derive_dynamic_deltas(seed_str, n_bits):
    seed_hash = hashlib.sha256(seed_str.encode()).digest()
    rng = random.Random(seed_hash)
    min_delta, max_delta = 0.150, 0.450
    dynamic_deltas = []
    for _ in range(n_bits):
        delta = min_delta + (max_delta - min_delta) * rng.random()
        dynamic_deltas.append(delta)
    return dynamic_deltas

# --- 4. CORE RECONSTRUCTION & PLL TIMING AUDITOR ---
def decode_and_audit_live(received_packets, queue_prior, secret_key, baseline_interval_ms=50.0):
    sorted_packets = sorted(received_packets, key=lambda x: x["seq"])
    total_fec_bits = 192
    
    # GROK BUG FIX #1: Correctly seed the RNG once and derive the unique delta array
    rng_deltas = random.Random(hashlib.sha256(secret_key.encode()).digest())
    dynamic_deltas = [0.150 + 0.300 * rng_deltas.random() for _ in range(total_fec_bits)]
    
    arrival_times = {pkt["seq"]: pkt["arrival_time"] for pkt in sorted_packets}
    
    decoded_bits_dict = {}
    valid_deviations = []
    expected_deviations = []
    
    discarded_count = 0
    timing_boundary_ms = 4.000  # 80 microseconds
    hurst_h = 0.75              # Hurst-scaled parameter
    
    pll_bias_ms = 0.0
    # Adaptive Kalman PLL Parameters (Phase 2)
    priors_cfg = load_calibrated_priors()
    K_0 = 0.04                  # Nominal loop gain
    beta_0 = priors_cfg["tail_fit_gpd"]["scale_beta"] if "tail_fit_gpd" in priors_cfg else 0.293660
    running_residual_scale = beta_0
    
    first_seq = sorted_packets[0]["seq"] if sorted_packets else None
    if first_seq is None:
        return {}, 0.0, True, 0
        
    last_ts = arrival_times[first_seq]
    last_idx = first_seq
    
    last_bit_decoded = 1 if (last_ts % baseline_interval_ms > (baseline_interval_ms / 2.0)) else 0
    decoded_bits_dict[first_seq] = last_bit_decoded
    
    # Establish a baseline reference epoch (NTP synchronized start time)
    start_time_est = last_ts - (first_seq * baseline_interval_ms + queue_prior[first_seq % len(queue_prior)])
    
    for j in range(first_seq + 1, total_fec_bits):
        if j in arrival_times:
            # GROK OPTIMIZATION #2: Hard Re-lock to the absolute grid every 24 packets
            # This halts any cumulative error propagation from corrupted feedback bits!
            if j % 24 == 0:
                expected_absolute_time = start_time_est + j * baseline_interval_ms + queue_prior[j % len(queue_prior)]
                deviation = arrival_times[j] - expected_absolute_time
            else:
                n = j - last_idx
                expected_baseline = n * baseline_interval_ms
                expected_queue_gap = queue_prior[j % len(queue_prior)] - queue_prior[last_idx % len(queue_prior)]
                ipd_arr = arrival_times[j] - last_ts
                
                last_mod = 0.0
                if last_bit_decoded is not None:
                    last_delta = dynamic_deltas[last_idx]
                    last_mod = last_delta if last_bit_decoded == 1 else -last_delta
                    
                deviation = ipd_arr - expected_baseline - expected_queue_gap + last_mod
            
            clean_deviation = deviation - pll_bias_ms
            expected_delta = dynamic_deltas[j]
            
            # Hurst-scaled tolerance
            tol = timing_boundary_ms * math.pow(j - last_idx if j % 24 != 0 else 1, hurst_h)
            
            if abs(abs(clean_deviation) - expected_delta) > tol:
                discarded_count += 1
            else:
                bit_val = 0 if clean_deviation < 0 else 1
                decoded_bits_dict[j] = bit_val
                
                valid_deviations.append(abs(clean_deviation))
                expected_deviations.append(expected_delta)
                
                # Update PLL tracking state with GROK OPTIMIZATION #3: Soft Magnitude Clamp
                error_residual = clean_deviation - (expected_delta if bit_val == 1 else -expected_delta)
                clamped_residual = max(-3.0 * tol, min(3.0 * tol, error_residual))
                
                # Adaptive loop gain: desensitize loop under heavy GPD tail noise (Phase 2)
                running_residual_scale = (0.95 * running_residual_scale) + (0.05 * abs(error_residual))
                pll_mu = K_0 / (1.0 + 3.0 * (running_residual_scale / beta_0))
                
                pll_bias_ms += pll_mu * clamped_residual
                
                # Advance tracking anchor
                last_ts = arrival_times[j]
                last_idx = j
                last_bit_decoded = bit_val
                
    n_dev = len(valid_deviations)
    if n_dev < 2:
        return decoded_bits_dict, 0.0, True, discarded_count
        
    mean_rec = sum(valid_deviations) / n_dev
    mean_exp = sum(expected_deviations) / n_dev
    num = sum((r - mean_rec) * (e - mean_exp) for r, e in zip(valid_deviations, expected_deviations))
    den_rec = math.sqrt(sum((r - mean_rec)**2 for r in valid_deviations))
    den_exp = math.sqrt(sum((e - mean_exp)**2 for e in expected_deviations))
    
    correlation = num / (den_rec * den_exp) if (den_rec != 0 and den_exp != 0) else 0.0
    tamper_flag = (discarded_count > 15)
    
    return decoded_bits_dict, correlation, tamper_flag, discarded_count

# --- 5. RECEIVER SOCKET RUNNER ---
def run_receiver(port, secret_key, hmac_key, expected_packets=192):
    priors_cfg = load_calibrated_priors()
    queue_prior = generate_calibrated_queue_delay(192, priors_cfg)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.settimeout(600.0)  # 10 minute listen timeout
    
    print(f"[*] Listening on UDP Port {port}...")
    print("[*] Waiting for incoming packet stream...")
    
    received_packets = []
    expected_mac = None
    
    while len(received_packets) < expected_packets:
        try:
            data, addr = sock.recvfrom(1024)
            arrival_epoch_ms = time.time() * 1000.0  # Milliseconds
            
            # SAGE Binary Header Parsing (20-byte binary packet payload)
            if len(data) < 20:
                continue
            seq, = struct.unpack(">I", data[:4])
            expected_mac = data[4:20].hex()
            
            received_packets.append({
                "seq": seq,
                "arrival_time": arrival_epoch_ms
            })
            
            if len(received_packets) == 1:
                print(f"[*] First packet received from {addr[0]}. Initiated grid lock...")
                sock.settimeout(5.0)  # Tighten timeout once stream begins
                
        except socket.timeout:
            print("[!] Listening timeout or stream ended prematurely.")
            break
            
    sock.close()
    
    n_rec = len(received_packets)
    if n_rec == 0:
        print("[!] No packets received. Exiting.")
        return
        
    print(f"[*] Captured {n_rec} packet arrival timestamps.")
    print("[*] Running SAGE Reconstruction Pipeline...")
    
    decoded_bits, correlation, tamper_flag, discarded = decode_and_audit_live(
        received_packets, queue_prior, secret_key
    )
    
    G = generate_systematic_g_matrix(secret_key, k=128, n=192)
    decoded_msg = decode_fountain_fec(decoded_bits, G)
    
    # GROK BUG FIX #4: Rigidly enforce HMAC payload verification, rejecting on mismatch
    rec_mac = hmac.new(hmac_key.encode(), decoded_msg.encode(), hashlib.sha256).hexdigest()[:16] if decoded_msg else ""
    hmac_verified = (rec_mac == expected_mac) and (expected_mac is not None)
    
    print("\n" + "="*50)
    print("              SAGE COGNITIVE DECODER REPORT       ")
    print("="*50)
    if hmac_verified:
        print(f"[*] Decoded Secret       : '{decoded_msg}'")
        print(f"[*] HMAC Verification    : SUCCESS")
    else:
        print(f"[*] Decoded Secret       : [REJECTED - DATA CORRUPTED OR FORGED]")
        print(f"[*] HMAC Verification    : FAILED")
    print(f"[*] Timing Correlation   : {correlation:.6f}")
    print(f"[*] Anomalous Discards   : {discarded}")
    print(f"[*] Tampering Flagged    : {'YES !!! SECURITY BREACH !!!' if (tamper_flag or not hmac_verified) else 'NO (Secure)'}")
    print("="*50 + "\n")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 18888
    
    secret_key = "SEFIROTIC_COUNCIL_LOGOS_KEY"
    hmac_key = "SEFIROTIC_HMAC_KEY"
    
    run_receiver(port, secret_key, hmac_key)
