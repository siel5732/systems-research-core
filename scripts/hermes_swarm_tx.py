#!/usr/bin/env python3
"""
scripts/hermes_swarm_tx.py

SAGE Distributed Swarm Timing Channel Transmitter (Phase 3).
Orchestrates GEEKOM (Node 1) and Boaz (Node 2) to interleave their packets:
- GEEKOM pre-populates and transmits EVEN sequence packets (0, 2, 4, ...).
- Boaz pre-populates and transmits ODD sequence packets (1, 3, 5, ...).
Synchronizes both nodes to blast instantly, letting the kernels merge their
streams on the wire into a single, seamless 192-packet timing channel!
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
import subprocess

# --- 1. LOAD NATIVE LIBBPF ---
LIBBPF_PATH = "/usr/lib/x86_64-linux-gnu/libbpf.so.1"
try:
    libbpf = ctypes.CDLL(LIBBPF_PATH, use_errno=True)
except Exception as e:
    print(f"[-] Failed to load libbpf: {e}")
    sys.exit(1)

libbpf.bpf_obj_get.argtypes = [ctypes.c_char_p]
libbpf.bpf_obj_get.restype = ctypes.c_int

libbpf.bpf_map_update_elem.argtypes = [
    ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64
]
libbpf.bpf_map_update_elem.restype = ctypes.c_int

# --- 2. CONFIGURATION LOAD ---
def load_calibrated_priors(config_path="/home/fq9f/systems-research-core/configs/hermes_calibrated_prior.json"):
    defaults = {
        "baseline_interval_ms": 50.0,
        "latency_floor_ms": 93.3164,
        "body_fit_lognormal": {"mu": 0.896835, "sigma": 0.968162},
        "tail_fit_gpd": {"threshold_val_ms": 4.4082, "xi_shape": 1.537106, "scale_beta": 0.293660}
    }
    return defaults

# --- 3. CRYPTOGRAPHIC & FEC LAYERS ---
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

# --- 4. SWARM MULTIPLEX COORDINATOR ---
def run_swarm_transmitter(target_ip, target_port, boaz_ip, secret_message, secret_key, hmac_key):
    # Padding / Truncating message
    secret_message = secret_message.ljust(16)[:16]
    print(f"[*] Swarm Payload   : '{secret_message}'")
    
    # Calculate HMAC
    h = hmac.new(hmac_key.encode(), secret_message.encode(), hashlib.sha256)
    expected_mac = h.hexdigest()[:16]
    
    # Generate Codewords and Timing Deltas
    G = generate_systematic_g_matrix(secret_key, k=128, n=192)
    fec_bits = encode_fountain_fec(secret_message, G)
    dynamic_deltas = derive_dynamic_deltas(secret_key, 192)
    
    priors = load_calibrated_priors()
    baseline = priors["baseline_interval_ms"]
    
    # Split the 192 delays
    geekom_delays = {}
    boaz_delays = {}
    
    for i in range(192):
        bit_val = fec_bits[i]
        delta_i = dynamic_deltas[i]
        offset_ms = delta_i if bit_val == 1 else -delta_i
        scheduled_time_ms = i * baseline + offset_ms
        delay_ns = int((scheduled_time_ms + 50.0) * 1000000.0)
        
        if i % 2 == 0:
            geekom_delays[i] = delay_ns
        else:
            boaz_delays[i] = delay_ns
            
    # --- PHASE 3A: WRITE GEEKOM DELAYS LOCALLY ---
    fd = libbpf.bpf_obj_get(b"/sys/fs/bpf/delay_map")
    if fd < 0:
        print("[-] delay_map not pinned on GEEKOM! Please load filter first.")
        sys.exit(1)
        
    key_c = ctypes.c_uint32()
    val_c = ctypes.c_uint64()
    
    print("[*] Writing GEEKOM (Even) delays locally...")
    for seq_id, delay_ns in geekom_delays.items():
        key_c.value = seq_id
        val_c.value = delay_ns
        libbpf.bpf_map_update_elem(fd, ctypes.byref(key_c), ctypes.byref(val_c), 0)
    os.close(fd)
    
    # --- PHASE 3B: WRITE BOAZ DELAYS VIA SSH ---
    print(f"[*] Synchronizing Boaz (Odd) delays to {boaz_ip} over SSH...")
    # We format Boaz's map updates into a single multi-command block to execute on Boaz!
    boaz_cmd_list = []
    # Find map ID dynamically on Boaz (using simple, spacing-proof grep | cut)
    boaz_cmd_list.append("MAP_ID=$(sudo bpftool map show | grep delay_map | cut -d: -f1 | head -n1)")
    boaz_cmd_list.append("if [ -z \"$MAP_ID\" ]; then echo '[-] Boaz map missing'; exit 1; fi")
    
    for seq_id, delay_ns in boaz_delays.items():
        # Format map update parameters
        key_bytes = struct.pack("<I", seq_id)
        val_bytes = struct.pack("<Q", delay_ns)
        key_hex = " ".join(f"0x{b:02x}" for b in key_bytes)
        val_hex = " ".join(f"0x{b:02x}" for b in val_bytes)
        # Note: Do NOT escape the $ symbol in $MAP_ID so the remote bash shell can expand the variable correctly!
        boaz_cmd_list.append(f"sudo bpftool map update id $MAP_ID key {key_hex} value {val_hex}")
        
    boaz_shell_script = " && ".join(boaz_cmd_list)
    try:
        # Force SSH to use the fq9f user's authorized private key (-i /home/fq9f/.ssh/id_ed25519)
        # to prevent Permission Denied errors when python runs under sudo (root)!
        subprocess.check_call(["ssh", "-t", "-i", "/home/fq9f/.ssh/id_ed25519", "-o", "StrictHostKeyChecking=no", f"fq9f@{boaz_ip}", boaz_shell_script])
        print("[✓] Boaz delays successfully written to Boaz kernel memory.")
    except Exception as e:
        print(f"[-] Failed to update Boaz map: {e}")
        sys.exit(1)
        
    # --- PHASE 3C: CO-ARMED BLAST ---
    print("\n" + "="*50)
    print("               CO-ARMED MULTIPLEX LAUNCH         ")
    print("="*50)
    print("[*] GEEKOM is blasting Even Packets...")
    print("[*] Boaz is blasting Odd Packets...")
    
    # 1. Trigger Boaz blast in background over SSH (using fq9f private key)
    boaz_blast_script = (
        f"python3 -c '"
        f"import socket, struct; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); "
        f"hmac_bytes = bytes.fromhex(\"{expected_mac}\"); "
        f"for i in range(1, 192, 2): "
        f"  s.sendto(struct.pack(\">I\", i) + hmac_bytes, (\"{target_ip}\", {target_port}))"
        f"'"
    )
    subprocess.Popen(["ssh", "-i", "/home/fq9f/.ssh/id_ed25519", "-o", "StrictHostKeyChecking=no", f"fq9f@{boaz_ip}", boaz_blast_script])
    
    # 2. Local GEEKOM blast (even packets)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hmac_bytes = bytes.fromhex(expected_mac)
    # Use loopback locally on GEEKOM if target is itself, bypassing raw loopback checksum offload drops
    local_target_ip = "127.0.0.1" if target_ip == "100.81.252.125" else target_ip
    for i in range(0, 192, 2):
        payload_bytes = struct.pack(">I", i) + hmac_bytes
        sock.sendto(payload_bytes, (local_target_ip, target_port))
    sock.close()
    
    print("[✓] Distributed swarm blast complete.")
    print("[*] Both nodes are actively pacing their interleaved streams in kernel-space!")
    print("="*50 + "\n")

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 2 else "10.240.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 3 else 18888
    boaz = "192.168.1.8"
    
    secret_key = "SEFIROTIC_COUNCIL_LOGOS_KEY"
    hmac_key = "SEFIROTIC_HMAC_KEY"
    
    run_swarm_transmitter(ip, port, boaz, "SAGE SECURE V3.2", secret_key, hmac_key)
