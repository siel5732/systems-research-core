#!/usr/bin/env python3
"""
scripts/hermes_jitter_simulator.py

The Hermes-1.5M Steganographic Covert-Channel & Anomaly Oracle.
Simulates a zero-dependency, local state-space communication channel where
encrypted SAGE message bits are programmatically embedded directly into 
the microsecond timing fluctuations (network jitter) of standard packet streams.
Detects active probing and network tamper injections using a Shannon Entropy threshold.
"""

import os
import sys
import math
import random
import time

# --- 1. CHAOTIC NETWORK JITTER PRIORS (LORENZ / LOGISTIC MAP CHAOS MODEL) ---
def generate_legitimate_jitter_envelope(n_steps=100, x_init=0.5):
    """
    Simulates a natural, non-Gaussian network jitter envelope using a Logistic Map:
    x_{n+1} = r * x_n * (1 - x_n)
    Models the complex, chaotic queuing patterns of typical internet hops.
    """
    r = 3.9  # Chaotic regime parameter
    x = x_init
    jitter_envelope = []
    
    # Typical base network latency (e.g., VPS to GEEKOM WireGuard tunnel: ~97.6 ms)
    base_latency_ms = 97.6
    
    for _ in range(n_steps):
        x = r * x * (1 - x)
        # Scale chaotic output to microsecond-level jitter (e.g., 0 to 5.0 ms variation)
        jitter_ms = x * 5.0
        total_delay_ms = base_latency_ms + jitter_ms
        jitter_envelope.append(total_delay_ms)
        
    return jitter_envelope

# --- 2. HERMES STEGANOGRAPHIC COVERT-CHANNEL ENCODER ---
def encode_covert_message(message_str, jitter_envelope):
    """
    Encodes a secret ASCII string into microscopic packet timing delays.
    Converts characters to binary and modulates the chaotic jitter envelope:
    - Bit '0': Aligns the packet delay strictly to the lower half of the local chaotic probability band.
    - Bit '1': Aligns the packet delay strictly to the upper half of the local chaotic probability band.
    """
    # Convert ASCII to raw binary stream
    binary_stream = ""
    for char in message_str:
        binary_stream += f"{ord(char):08b}"
        
    print(f"[*] Staging covert message: '{message_str}'")
    print(f"[*] Generated binary stream ({len(binary_stream)} bits): {binary_stream[:16]}...{binary_stream[-16:]}")
    
    encoded_delays = []
    
    # We embed 1 bit per packet step
    for i, bit in enumerate(binary_stream):
        # Retrieve the base chaotic jitter prior for this packet index
        base_delay = jitter_envelope[i % len(jitter_envelope)]
        
        # Microscopic modulation interval (e.g. +/- 250 microseconds)
        modulation_delta_ms = 0.250 
        
        if bit == '0':
            # Slightly decrease the local delay, keeping it within natural limits
            modulated_delay = base_delay - modulation_delta_ms
        else:
            # Slightly increase the local delay, keeping it within natural limits
            modulated_delay = base_delay + modulation_delta_ms
            
        encoded_delays.append(modulated_delay)
        
    return encoded_delays

# --- 3. HERMES STEGANOGRAPHIC DECODER ---
def decode_covert_message(received_delays, jitter_envelope):
    """
    Decodes the covert ASCII stream by comparing received packet delays
    against the expected chaotic network jitter prior.
    """
    decoded_bits = ""
    
    for i, received_delay in enumerate(received_delays):
        base_delay = jitter_envelope[i % len(jitter_envelope)]
        
        # Compare actual delay with expected prior
        if received_delay < base_delay:
            decoded_bits += "0"
        else:
            decoded_bits += "1"
            
    # Convert binary stream back to ASCII characters
    decoded_chars = []
    for i in range(0, len(decoded_bits), 8):
        byte = decoded_bits[i:i+8]
        if len(byte) == 8:
            decoded_chars.append(chr(int(byte, 2)))
            
    return "".join(decoded_chars)

# --- 4. SHANNON ENTROPY TAMPER & PROBING DETECTOR ---
def calculate_shannon_entropy(delays, expected_envelope):
    """
    Measures the Shannon Entropy of the received trajectory deviations.
    Active sniffing, packet injections, or routing watermarks dramatically disrupt
    the tight chaotic probability bounds, causing immediate entropy collapse/spikes.
    """
    deviations = [abs(rec - exp) for rec, exp in zip(delays, expected_envelope)]
    
    # Create histogram probability bins of the deviations
    bins = {}
    for dev in deviations:
        # Group into 100-microsecond bins
        bin_idx = round(dev, 1)
        bins[bin_idx] = bins.get(bin_idx, 0) + 1
        
    entropy = 0.0
    total = len(deviations)
    
    for count in bins.values():
        prob = count / total
        entropy -= prob * math.log2(prob)
        
    return entropy

# --- 5. SYSTEM SIMULATION ---
def run_hermes_simulation():
    print("=" * 65)
    print("        HERMES-1.5M: STEGANOGRAPHIC COVERT JITTER SIMULATOR      ")
    print("=" * 65)
    
    # 1. Establish the legitimate baseline channel model (The Prior)
    total_packets = 128  # Capable of holding 16 ASCII characters (16 * 8 = 128 bits)
    jitter_prior = generate_legitimate_jitter_envelope(n_steps=total_packets)
    print(f"[+] Local chaotic network jitter prior successfully trained.")
    print(f"    - Sample Packet Latency Range: {min(jitter_prior):.3f} ms to {max(jitter_prior):.3f} ms")
    
    # 2. Secret data to embed
    secret_thought = "SAGE GHOST PROT" # 15 characters = 120 bits
    
    # 3. Encode the covert stream into the network delays
    transmitted_packet_delays = encode_covert_message(secret_thought, jitter_prior)
    print(f"[✓] Microsecond-level packet jitter modulated with steganographic envelope.")
    
    # 4. Scenario A: Honest, un-tampered channel transmission
    print("\n--- SCENARIO A: HONEST OFFLINE DECODING ---")
    decoded_secret = decode_covert_message(transmitted_packet_delays, jitter_prior)
    entropy_honest = calculate_shannon_entropy(transmitted_packet_delays, jitter_prior)
    
    print(f"[*] Decoded Secret Thought: '{decoded_secret}'")
    print(f"[*] Measured Channel Shannon Entropy: {entropy_honest:.4f} bits")
    print(f"[*] Posture Status: {'SECURE' if entropy_honest < 1.1 else 'COMPROMISED'}")
    
    # 5. Scenario B: Attack / Active Probing Injection
    print("\n--- SCENARIO B: ACTIVE ATTACK / ROUTING INJECTION ---")
    
    # Attacker injects randomized delay modifications (active sniffing or network watermarking)
    tampered_delays = list(transmitted_packet_delays)
    print("[!] Attacker is probing the tunnel! Injecting 1.5ms network jitter anomalies...")
    for idx in range(12, 40):
        # Attacker introduces a slight routing delay on selected packets
        tampered_delays[idx] += random.uniform(0.500, 2.50)
        
    # Attempt to decode tampered delays
    tampered_decoded_secret = decode_covert_message(tampered_delays, jitter_prior)
    entropy_tampered = calculate_shannon_entropy(tampered_delays, jitter_prior)
    
    print(f"[*] Decoded Secret (Tampered): '{tampered_decoded_secret}'")
    print(f"[*] Measured Channel Shannon Entropy: {entropy_tampered:.4f} bits")
    
    # Threshold trigger check (Normal baseline is extremely tightly bounded at ~1.0 bits)
    threshold = 1.2
    if entropy_tampered > threshold:
        print(f"\n[⚠️] !!! ALARM !!! DIVERGENT HIGH-ENTROPY COLLAPSE DETECTED: {entropy_tampered:.4f} > {threshold}")
        print("[🛡️] POSTURE Posture: SILENT LOCKDOWN TRIPPED (DTQW Research Core Collapsed).")
        print("[🛡️] ACTION: Revoking reverse tunnel keys, rotating WireGuard endpoint configurations.")
    else:
        print("[*] Posture Status: SECURE (Under threshold).")
        
    print("=" * 65)

if __name__ == "__main__":
    run_hermes_simulation()
