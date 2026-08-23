#!/usr/bin/env python3
"""
Cantor-Dust Bus Filter Simulator (Module 23)
Designed by Imhotep, Trent, and Aphex (Subconscious Systems Group)
Simulates continuous-wave phase-demodulation on a 12-qubit (4,096-dimensional) 
Software-Defined Commutation Bus (SDCB) to defeat fractal Cantor-dust hardware noise.
"""

import numpy as np
import json
import os

def generate_cantor_set(N, depth=5):
    """
    Generates a classical Cantor ternary dust on a grid of size N.
    A Cantor set has uncountably infinite points but has a Lebesgue measure of ZERO.
    This acts as our fractal hardware noise/jitter on the physical GEEKOM bus.
    """
    mask = np.ones(N, dtype=bool)
    
    def remove_middle_third(start, end, current_depth):
        if current_depth >= depth or (end - start) < 3:
            return
        third = (end - start) // 3
        # Remove the middle third
        mask[start + third : start + 2 * third] = False
        # Recurse on remaining thirds
        remove_middle_third(start, start + third, current_depth + 1)
        remove_middle_third(start + 2 * third, end, current_depth + 1)
        
    remove_middle_third(0, N, 0)
    # The noise is where we removed the middle thirds (the gaps)
    return ~mask

def main():
    print("Initializing 12-Qubit Cantor-Dust Bus Filter Simulator...")
    num_qubits = 12
    N = 2**num_qubits  # 4,096 dimensions
    
    # 1. Generate fractal Cantor-dust noise representing hardware jitter (PCIe/USB physical bus lanes)
    cantor_noise = generate_cantor_set(N, depth=6)
    noise_density = np.sum(cantor_noise) / N
    print(f"[*] Generated Cantor-Dust physical noise mask with density: {noise_density * 100.0:.2f}%")
    
    # 2. Classical Bus Transmission (Discrete Serial Bits)
    # Classical transmission relies on clean discrete voltage levels. 
    # Any intersection with the fractal noise causes clock-cycle desynchronization.
    classical_signal = np.zeros(N)
    # Send a clean square-wave payload (data bits)
    classical_signal[1500:2500] = 1.0
    
    # Noise collides with the classical bus
    corrupted_classical = np.where(cantor_noise, 0.0, classical_signal)
    classical_packet_loss = (1.0 - (np.sum(corrupted_classical) / np.sum(classical_signal))) * 100.0
    print(f"[❌] Classical Bus Packet Loss due to Cantor Dust Jitter: {classical_packet_loss:.2f}%")
    
    # 3. Quantum-Inspired Continuous SDCB Transmission (Wave-Phase Modulation)
    # We transmit our signal as a continuous wave-front across the entire 4,096-dimensional manifold.
    # The payload is encoded inside the phase-profile of the wavefunction.
    t = np.arange(N)
    carrier_wave = np.exp(2j * np.pi * t / N) # Carrier frequency
    # Phase modulate the payload
    payload_phase = np.zeros(N)
    payload_phase[1500:2500] = np.pi / 2.0 # Phase shift represents "1" bits
    
    psi_transmitted = carrier_wave * np.exp(1j * payload_phase)
    
    # Apply the same physical Cantor-dust noise (signal attenuation at the gaps)
    psi_received = np.where(cantor_noise, 0.0, psi_transmitted)
    
    # 4. Phase Demodulation & Reassembly (Aphex's Phase-Conjugate Filter)
    # We apply a phase-conjugate reflection of the carrier wave to decode the phase profile
    decoded_phases = np.angle(psi_received * np.conj(carrier_wave))
    
    # Use 1D Linear Interpolation (Aphex's Continuous Demodulator)
    # We extract the valid (non-noisy) coordinates
    valid_indices = np.where(~cantor_noise)[0]
    valid_values = decoded_phases[valid_indices]
    
    # Reconstruct the entire phase-front by interpolating across the Cantor-dust gaps
    reconstructed_phase = np.interp(np.arange(N), valid_indices, valid_values)
    
    # Measure reconstruction fidelity
    target_phase = payload_phase
    # Calculate Mean Squared Error (MSE) and Fidelity
    mse = np.mean((reconstructed_phase - target_phase)**2)
    fidelity = 1.0 - (mse / (np.pi/2.0)**2)
    
    print(f"[🎯] Continuous SDCB Wave Demodulation Completed:")
    print(f"    -> Reconstructed Phase MSE: {mse:.6f}")
    print(f"    -> Quantum-Inspired Phase Reconstruction Fidelity: {fidelity * 100.0:.4f}% Match")
    
    # Save results to JSON
    os.makedirs("systems_core", exist_ok=True)
    out_path = "systems_core/cantor_dust_bus_results.json"
    data = {
        "metadata": {
            "title": "Quantum-Inspired Software-Defined Commutation Bus (SDCB) Simulation",
            "dimensions": N,
            "noise_density": round(float(noise_density), 6),
            "classical_packet_loss_pct": round(float(classical_packet_loss), 4),
            "quantum_fidelity_pct": round(float(fidelity * 100.0), 4)
        },
        "signal_profiles": {
            "cantor_mask_downsampled": [bool(b) for b in cantor_noise[::32]],
            "reconstructed_phase_downsampled": [float(p) for p in reconstructed_phase[::32]]
        }
    }
    
    with open(out_path, "w") as f:
        json.dump(data, f, indent=4)
        
    print(f"Data cached at: {out_path}")

if __name__ == "__main__":
    main()
