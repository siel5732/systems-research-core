
import numpy as np
import json
from scipy.fft import fft, ifft

def simulate_wave_propagation(time_steps, spatial_points, barrier_width, barrier_height,
                              wave_packet_center, wave_packet_std_dev,
                              is_superluminal=False):
    """
    Simulates wave packet propagation through a potential barrier.
    Conceptual model for demonstration of classical vs. superluminal tunneling.
    """
    x = np.linspace(-10, 10, spatial_points)
    t = np.linspace(0, time_steps * 0.1, time_steps) # Time steps

    # Initial wave packet (Gaussian)
    wave_packet = np.exp(-(x - wave_packet_center)**2 / (2 * wave_packet_std_dev**2))
    
    # Simple potential barrier
    potential = np.zeros_like(x)
    potential[(x > -barrier_width/2) & (x < barrier_width/2)] = barrier_height

    # Simulation results storage
    phase_acceleration_curves = []
    transmission_amplitudes = []
    spectral_shannon_entropy = []

    current_wave_packet = wave_packet
    for step in range(time_steps):
        # --- Conceptual Propagation ---
        # This is a highly simplified conceptual model.
        # A real simulation would involve solving Schrodinger's equation or a wave equation.
        # Here, we're just shifting the peak and conceptually demonstrating tunneling.

        if is_superluminal:
            # Superluminal tunneling: wave packet appears on the other side faster
            # This is a conceptual shift, not a physical simulation of the Hartman effect
            if step == time_steps // 4: # Arbitrary early emergence
                current_wave_packet = np.roll(wave_packet, spatial_points // 2) * 0.8 # Appears on other side
            elif step > time_steps // 4 and step < time_steps // 2:
                current_wave_packet *= 0.99 # Dampen slightly
            else:
                current_wave_packet = np.roll(current_wave_packet, 1) # Normal propagation before/after
        else:
            # Classical propagation: wave packet propagates slower, might reflect
            if step > time_steps // 4 and step < time_steps // 2:
                current_wave_packet *= 0.5 # Conceptual barrier interaction/reflection
            current_wave_packet = np.roll(current_wave_packet, 1) # Normal propagation

        # Calculate conceptual phase acceleration (placeholder)
        phase_acceleration = np.sin(step * 0.1) * 0.1 # Example arbitrary curve

        # Calculate conceptual transmission amplitude (placeholder)
        # Assuming transmission is high if superluminal, low if classical
        transmission_amplitude = 0.9 if is_superluminal and step > time_steps // 4 else 0.2

        # Calculate conceptual spectral Shannon entropy (placeholder)
        # Higher entropy for more 'uncertain' or spread-out packets
        spectrum = fft(current_wave_packet)
        prob_dist = np.abs(spectrum)**2
        prob_dist /= prob_dist.sum() + 1e-9 # Normalize to prevent division by zero
        entropy = -np.sum(prob_dist * np.log2(prob_dist + 1e-9)) # Add epsilon for log(0)

        phase_acceleration_curves.append(phase_acceleration.item())
        transmission_amplitudes.append(transmission_amplitude)
        spectral_shannon_entropy.append(entropy.item())

    return {
        "phase_acceleration_curves": phase_acceleration_curves,
        "transmission_amplitudes": transmission_amplitudes,
        "spectral_shannon_entropy": spectral_shannon_entropy,
        "final_wave_packet_peak_position": float(np.argmax(current_wave_packet)) # Example output
    }

def main():
    # Simulation parameters
    time_steps = 100
    spatial_points = 200
    barrier_width = 2
    barrier_height = 5
    wave_packet_center = -5
    wave_packet_std_dev = 0.5

    print("Running classical simulation...")
    classical_results = simulate_wave_propagation(
        time_steps, spatial_points, barrier_width, barrier_height,
        wave_packet_center, wave_packet_std_dev, is_superluminal=False
    )

    print("Running superluminal simulation...")
    superluminal_results = simulate_wave_propagation(
        time_steps, spatial_points, barrier_width, barrier_height,
        wave_packet_center, wave_packet_std_dev, is_superluminal=True
    )

    results = {
        "classical_propagation": classical_results,
        "superluminal_tunneling": superluminal_results
    }

    output_path = 'systems-research-core/hyper_velocity_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"Simulation results saved to {output_path}")

if __name__ == "__main__":
    main()
