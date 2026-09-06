#!/usr/bin/env python3
"""
scripts/visualize_sefirotic_walk.py
Generates a beautiful, high-resolution line graph visualization of the 
Discrete-Time Quantum Walk probability distribution flowing across the 
10-node Sefirotic Tree of Life over 50 steps.
Saves the visualization to media/sefirotic_quantum_walk.png.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from sefirotic_quantum_walk import run_walk, SEFIROT

# Create output directories
os.makedirs("media", exist_ok=True)
output_path = "media/sefirotic_quantum_walk.png"

def generate_visualization():
    print("[*] Running Sefirotic Quantum Walk Simulation (50 steps)...")
    # Run the walk
    steps = 50
    history = run_walk(steps=steps, theta=np.pi/4, bias_toward_keter=True)
    
    # Configure Matplotlib Theme (Brutalist Modern Cyber-Hermetic: Deep Gray Background, Neon Cyan/Amber/Red accents)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    
    # Define alchemical neon colors for the 10 Sefirot
    colors = {
        "Keter": "#FFFFFF",      # Pure Divine White Light
        "Chokhmah": "#00FFCC",   # Neon Turquoise (Creative Latent Space)
        "Binah": "#FF007F",      # Radiant Magenta (Structured Logic)
        "Chesed": "#0099FF",     # Deep Sky Blue (Mercy / Expansion)
        "Gevurah": "#FF3333",    # Fiery Red (Severity / Constraint)
        "Tiferet": "#FFCC00",    # Solar Golden Yellow (Beauty / Harmony Core)
        "Netzach": "#33FF33",    # Emerald Green (Victory / Posture)
        "Hod": "#FF6600",        # Alchemical Orange (Glory / Acoustic Vibration)
        "Yesod": "#9933FF",      # Cosmic Violet (Foundation / Gatekeeper)
        "Malkhut": "#7A5230"     # Grounded Earth Bronze (Local Physical Hardware)
    }
    
    # Plot each Sefirah's probability trajectory
    x_steps = np.arange(steps + 1)
    
    # We highlight Keter, Tiferet, and Malkhut with thicker lines
    for idx, name in enumerate(SEFIROT):
        prob_y = history[:, idx]
        linewidth = 2.5 if name in ["Keter", "Tiferet", "Malkhut"] else 1.2
        alpha = 1.0 if name in ["Keter", "Tiferet", "Malkhut"] else 0.65
        linestyle = "-" if name in ["Keter", "Tiferet", "Malkhut"] else "--"
        
        ax.plot(
            x_steps, 
            prob_y, 
            color=colors.get(name, "#888888"), 
            label=name, 
            linewidth=linewidth, 
            alpha=alpha,
            linestyle=linestyle
        )
    
    # Custom Labels & Grid
    ax.set_title("Sefirotic Quantum Walk Probability Dynamics (Metatronic Ascent)", fontsize=14, fontweight="bold", pad=20, color="#E0E0E0")
    ax.set_xlabel("Simulation Steps", fontsize=11, labelpad=10, color="#B0B0B0")
    ax.set_ylabel("Probability Mass", fontsize=11, labelpad=10, color="#B0B0B0")
    
    ax.set_xlim(0, steps)
    ax.set_ylim(0, 0.6) # Max probability observed is under 0.6 (mostly Tiferet peaks)
    
    # Grid styling
    ax.grid(True, linestyle=":", alpha=0.25, color="#555555")
    
    # Legend styling
    ax.legend(loc="upper right", frameon=True, facecolor="#121212", edgecolor="#333333", fontsize=9, ncol=2)
    
    # Highlight milestones on plot
    ax.annotate(
        "Tiferet Peak (Harmonic Hub)", 
        xy=(15, 0.42), 
        xytext=(22, 0.48),
        arrowprops=dict(facecolor="#FFCC00", shrink=0.08, width=1, headwidth=6, headlength=6),
        fontsize=9, 
        color="#FFCC00",
        fontweight="bold"
    )
    
    ax.annotate(
        "Keter Accumulation", 
        xy=(50, 0.035), 
        xytext=(35, 0.12),
        arrowprops=dict(facecolor="#FFFFFF", shrink=0.08, width=1, headwidth=6, headlength=6),
        fontsize=9, 
        color="#FFFFFF",
        fontweight="bold"
    )
    
    # Aesthetic touches: border removal
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.spines['left'].set_color('#444444')
    ax.spines['bottom'].set_color('#444444')
    
    # Save fig
    plt.tight_layout()
    plt.savefig(output_path, facecolor='#121212', edgecolor='none')
    plt.close()
    print(f"[+] Visualization successfully exported -> {output_path}")

if __name__ == "__main__":
    generate_visualization()
