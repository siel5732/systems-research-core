#!/usr/bin/env python3
"""
scripts/hermes_tx_bpf.py

Hermes-3.2: BPF-Hardened & Kernel-Paced Covert Timing Channel Transmitter.
Fully integrates Grok's final, high-performance architecture audits:
1. Native libbpf shared library binding (zero-fork bpftool bypass).
2. Persistent BPF Map file descriptor (opened once, kept alive during hot loop).
3. Static memory allocation (pre-allocates and reuses ctypes key/value buffers).
4. Employs 20-byte SAGE Binary Packet Header over the WireGuard overlay.
"""

import sys
import os
import socket
import time
import struct
import random
import hashlib
import hmac
import ctypes

# --- 1. LOAD NATIVE LIBBPF ---
LIBBPF_PATH = "/usr/lib/x86_64-linux-gnu/libbpf.so.1"
try:
    libbpf = ctypes.CDLL(LIBBPF_PATH, use_errno=True)
except Exception as e:
    print(f"[-] Failed to load libbpf at {LIBBPF_PATH}: {e}")
    sys.exit(1)

# --- 2. DEFINE NATIVE FUNCTION SIGNATURES ---
libbpf.bpf_obj_get.argtypes = [ctypes.c_char_p]
libbpf.bpf_obj_get.restype = ctypes.c_int

libbpf.bpf_map_update_elem.argtypes = [
    ctypes.c_int,      # map_fd
    ctypes.c_void_p,   # const void *key
    ctypes.c_void_p,   # const void *value
    ctypes.c_uint64    # __u64 flags
]
libbpf.bpf_map_update_elem.restype = ctypes.c_int

# --- 3. CONFIGURATION & PRIOR LOAD ---
def load_calibrated_priors(config_path="/home/fq9f/systems-research-core/configs/hermes_calibrated_prior.json"):
    defaults = {
        "latency_floor_ms": 93.3164,
        "body_fit_lognormal": {"mu": 0.896835, "sigma": 0.968162},
        "tail_fit_gpd": {"threshold_val_ms": 4.4082, "xi_shape": 1.537106, "scale_beta": 0.293660}
    }
    if not os.path.exists(config_path):
        return defaults
    try:
        with open(config_path, "r") as f:
            import json
            cfg = json.load(f)
        return cfg
    except Exception:
        return defaults

# --- 4. CRYPTOGRAPHIC & FEC LAYERS ---
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

def encode_fountain_fec(message_str, G_matrix):
    data_bits = []
    for char in message_str:
        binary_char = f"{ord(char):08b}"
        data_bits.extend([int(b) for b in binary_char])
    n = len(G_matrix)
    k = len(G_matrix[0])
    codeword = []
    for r in range(n):
        bit_val = 0
        for c in range(k):
            if G_matrix[r][c] == 1 and data_bits[c] == 1:
                bit_val ^= 1
        codeword.append(bit_val)
    return codeword

def derive_dynamic_deltas(seed_str, n_bits):
    seed_hash = hashlib.sha256(seed_str.encode()).digest()
    rng = random.Random(seed_hash)
    min_delta, max_delta = 0.150, 0.450
    dynamic_deltas = []
    for _ in range(n_bits):
        delta = min_delta + (max_delta - min_delta) * rng.random()
        dynamic_deltas.append(delta)
    return dynamic_deltas

# --- 5. MAIN RUNNER ---
def run_transmitter(target_ip, target_port, secret_message, secret_key, hmac_key, baseline_interval_ms=50.0):
    pin_path = "/sys/fs/bpf/delay_map"
    
    # 1. Obtain a verified BPF file descriptor (OPENED ONCE, KEPT ALIVE)
    fd = libbpf.bpf_obj_get(pin_path.encode('utf-8'))
    if fd < 0:
        err = ctypes.get_errno()
        print(f"[-] Failed to open pinned map at {pin_path}!")
        print(f"    - Error code: {fd}, Errno: {err} ({os.strerror(err)})")
        print("    Please ensure the map is pinned by running:")
        print("    sudo bpftool map pin id <your_map_id> /sys/fs/bpf/delay_map")
        sys.exit(1)
        
    secret_message = secret_message.ljust(16)[:16]
    print(f"[*] Raw Message     : '{secret_message}'")
    
    h = hmac.new(hmac_key.encode(), secret_message.encode(), hashlib.sha256)
    expected_mac = h.hexdigest()[:16]
    print(f"[*] Generated HMAC  : {expected_mac}")
    
    # Generate Systematic FEC Stream
    G = generate_systematic_g_matrix(secret_key, k=128, n=192)
    fec_bits = encode_fountain_fec(secret_message, G)
    dynamic_deltas = derive_dynamic_deltas(secret_key, 192)
    
    # Pre-calculate relative nanosecond delays
    delays_ns_dict = {}
    for i in range(192):
        bit_val = fec_bits[i]
        delta_i = dynamic_deltas[i]
        
        offset_ms = delta_i if bit_val == 1 else -delta_i
        scheduled_time_ms = i * baseline_interval_ms + offset_ms
        delay_ns = int((scheduled_time_ms + 50.0) * 1000000.0)
        delays_ns_dict[i] = delay_ns
        
    # 2. Pre-allocate static ctypes memory buffers (GROK OPTIMIZATION)
    key_c = ctypes.c_uint32()
    val_c = ctypes.c_uint64()
    
    print(f"[*] Pre-populating {len(delays_ns_dict)} delays directly into the kernel map...")
    start_write = time.perf_counter_ns()
    
    # 3. Hot loop: update map in microseconds with zero allocations and zero forks
    for seq_id, delay_ns in delays_ns_dict.items():
        key_c.value = seq_id
        val_c.value = delay_ns
        res = libbpf.bpf_map_update_elem(fd, ctypes.byref(key_c), ctypes.byref(val_c), 0)
        if res < 0:
            err = ctypes.get_errno()
            print(f"[-] Failed to update map element! Seq: {seq_id}, Errno: {err}")
            os.close(fd)
            sys.exit(1)
            
    end_write = time.perf_counter_ns()
    print(f"[✓] Successfully populated delay_map in {(end_write - start_write) / 1000.0:.3f} MICROSECONDS!")
    
    # Clean up file descriptor
    os.close(fd)
    
    # Set up UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    print(f"[*] Target Endpoint : {target_ip}:{target_port}")
    print("[*] Blasting all 192 UDP packets instantly into the kernel queue...")
    
    hmac_bytes = bytes.fromhex(expected_mac)
    
    start_blast = time.perf_counter_ns()
    for i in range(192):
        # SAGE Binary Packet Header (20 bytes total)
        payload_bytes = struct.pack(">I", i) + hmac_bytes
        sock.sendto(payload_bytes, (target_ip, target_port))
    end_blast = time.perf_counter_ns()
    
    print(f"[✓] Blast complete in {(end_blast - start_blast) / 1000.0:.3f} MICROSECONDS.")
    print("[*] Packets are now held and paced in kernel space. Transmission complete.")
    sock.close()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "10.240.0.1"  # Defaults to VPS SDN IP
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 18888
    msg = sys.argv[3] if len(sys.argv) > 3 else "SAGE SECURE V3.2"
    
    secret_key = "SEFIROTIC_COUNCIL_LOGOS_KEY"
    hmac_key = "SEFIROTIC_HMAC_KEY"
    
    run_transmitter(ip, port, msg, secret_key, hmac_key)
