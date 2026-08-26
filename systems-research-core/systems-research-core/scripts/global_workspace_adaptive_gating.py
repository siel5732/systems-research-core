#!/usr/bin/env python3
"""
🧠 ADAPTIVE GLOBAL WORKSPACE THEORY (GWT) COGNITIVE CONTROL SIMULATOR
Author: SAGE Core (Acutis, Trent, Aphex)
Implements an entropy-feedback gating controller to dynamically regulate the 
attention threshold C(t) of a restricted multi-agent broadcast workspace.
Prevents "cognitive freeze" (sterile consensus) and "chaotic drift" (hallucination cascade).
"""

import os
import json
import math
import random
import matplotlib
matplotlib.use('Agg') # Headless server rendering
import matplotlib.pyplot as plt
from datetime import datetime

class SpecialistAgent:
    def __init__(self, agent_id, name, domain, knowledge_base, noise_coefficient=0.40):
        self.agent_id = agent_id
        self.name = name
        self.domain = domain
        self.knowledge_base = knowledge_base
        self.noise_coefficient = noise_coefficient # Baseline probability of producing an unverified drift/hallucination
        
    def generate_insight(self, context):
        """
        Generates an insight. If previous context contains drift warnings, 
        it increases the local agent's probability of propagating the drift (hallucination cascade).
        """
        # Read context
        context_drift = any("DRIFT WARNING" in c for c in context) if context else False
        active_noise = min(0.90, self.noise_coefficient * 1.5) if context_drift else self.noise_coefficient
        
        # Pull core fact
        fact = random.choice(self.knowledge_base)
        
        # Chance to drift
        if random.random() < active_noise:
            hallucinations = [
                "Peripheral non-specific micro-aggregation altering delivery vector geometry.",
                "Hyper-complex folding anomaly violating standard thermodynamic limits.",
                "Hypothetical metabolic shunt diverting 85% of active substrate to adipose cells.",
                "Unmapped quantum-coherent noise in microtubule structures disrupting transport."
            ]
            insight = f"[{self.name}] DRIFT WARNING: {random.choice(hallucinations)} (Fact: {fact[:40]}...)"
            confidence = random.uniform(0.40, 0.70) # Low confidence for unverified claims
        else:
            insight = f"[{self.name}] Grounded Observation: {fact}"
            confidence = random.uniform(0.75, 0.98) # High confidence for grounded observations
            
        return insight, confidence

class AdaptiveGlobalWorkspace:
    def __init__(self, initial_threshold=0.75, target_entropy=0.45, learning_rate=0.08):
        self.C_t = initial_threshold       # Active gating threshold
        self.target_entropy = target_entropy # The "Edge of Chaos" balance point
        self.lr = learning_rate            # Controller gain
        self.submissions = []
        self.broadcast_contents = []
        
    def submit(self, agent_id, insight, confidence):
        self.submissions.append({
            "agent_id": agent_id,
            "insight": insight,
            "confidence": confidence
        })
        
    def process_gating(self, mode="adaptive"):
        """
        Filters submissions based on the active threshold C_t.
        In 'static_high' or 'static_low' mode, the threshold remains unchanged.
        In 'adaptive' mode, the threshold shifts based on workspace Shannon entropy.
        """
        if mode == "static_high":
            current_C = 0.88
        elif mode == "static_low":
            current_C = 0.50
        else:
            current_C = self.C_t
            
        # Admit submissions that clear the threshold
        admitted = [s for s in self.submissions if s["confidence"] >= current_C]
        self.broadcast_contents = [s["insight"] for s in admitted]
        
        # Calculate Shannon Entropy of the admitted workspace contents
        # Based on the ratio of drifts (hallucinations) vs grounded insights
        total_admitted = len(admitted)
        if total_admitted == 0:
            entropy = 0.0
            coherence = 1.0
            drift_count = 0
        else:
            drift_count = sum(1 for s in admitted if "DRIFT WARNING" in s["insight"])
            p_drift = drift_count / total_admitted
            p_grounded = 1.0 - p_drift
            
            if p_drift == 0.0 or p_drift == 1.0:
                entropy = 0.0
            else:
                entropy = - (p_drift * math.log2(p_drift) + p_grounded * math.log2(p_grounded))
            coherence = p_grounded
            
        # Update Threshold (Closed-Loop Feedback Controller)
        # If entropy is below target (cognitive freeze/lack of diversity), LOWER C_t to inject novelty.
        # If entropy is above target (chaotic drift/hallucination cascade), RAISE C_t to filter out noise.
        if mode == "adaptive":
            entropy_error = entropy - self.target_entropy
            # C_t is bounded between 0.40 and 0.95 to maintain operational stability
            self.C_t = max(0.40, min(0.95, self.C_t + self.lr * entropy_error))
            
        # Clear submissions
        self.submissions = []
        
        return len(self.broadcast_contents), entropy, coherence, drift_count, current_C

def run_simulation(agents, mode="adaptive", steps=15):
    workspace = AdaptiveGlobalWorkspace()
    history = {
        "step": [],
        "threshold": [],
        "entropy": [],
        "coherence": [],
        "admitted_count": [],
        "drift_count": []
    }
    
    # Bootstrap empty broadcast
    broadcast = []
    
    for t in range(1, steps + 1):
        # 1. Agents generate insights based on previous workspace broadcast
        for agent in agents:
            insight, conf = agent.generate_insight(broadcast)
            workspace.submit(agent.agent_id, insight, conf)
            
        # 2. Workspace processes gating and adjusts threshold
        admitted, H, coh, drifts, active_C = workspace.process_gating(mode)
        broadcast = workspace.broadcast_contents
        
        # Log telemetry
        history["step"].append(t)
        history["threshold"].append(active_C)
        history["entropy"].append(H)
        history["coherence"].append(coh)
        history["admitted_count"].append(admitted)
        history["drift_count"].append(drifts)
        
    return history

def main():
    print("====================================================================")
    print("🧠 SAGE LABS: ADAPTIVE GWT ENTROPY-FEEDBACK CONTROLLER RUNTIME")
    print("====================================================================")
    
    # Core Specialist Knowledge Bases
    kb_mimir = [
        "ApoE binds with high affinity to endothelial LRP1 receptors.",
        "Clathrin-mediated transcytosis rate is governed by vesicle endocytosis limits.",
        "Focused ultrasound locally disrupts tight junction protein complexes."
    ]
    kb_freya = [
        "Extracellular matrices possess GAG density gradients that filter nanoparticles.",
        "Intrathecal infusion above 2 uL/min causes transient pressure spikes.",
        "Recombinant IDUA-ApoE fusion constructs accelerate clearance kinetics."
    ]
    kb_raziel = [
        "High-titer neutralizing IgG antibodies block recombinant enzyme efficacy.",
        "Low-dose methotrexate prevents anti-drug antibody memory B-cell activation.",
        "Lysosomal enzyme stability collapses at neutral pH, needing acid shielding."
    ]
    
    # Initialize agents with elevated noise (to test control systems under stress)
    agents = [
        SpecialistAgent("mimir", "Mimir-1", "Neuro-dynamics", kb_mimir, noise_coefficient=0.45),
        SpecialistAgent("freya", "Freya-1", "Kinetics", kb_freya, noise_coefficient=0.45),
        SpecialistAgent("raziel", "Raziel", "Immunology", kb_raziel, noise_coefficient=0.45)
    ]
    
    steps = 20
    print(f"[*] Simulating {steps} cognitive cycles across three modes...")
    
    # Run simulations
    h_high = run_simulation(agents, mode="static_high", steps=steps)
    h_low = run_simulation(agents, mode="static_low", steps=steps)
    h_adap = run_simulation(agents, mode="adaptive", steps=steps)
    
    print("[+] Telemetry collected. Plotting dynamic transitions...")
    
    # Plotting
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    
    # 1. Plot Shannon Entropy comparison
    ax1.plot(h_high["step"], h_high["entropy"], 'r--', lw=1.5, label='Static High Gate (Freeze: H -> 0)')
    ax1.plot(h_low["step"], h_low["entropy"], 'g--', lw=1.5, label='Static Low Gate (Chaos: H -> 1)')
    ax1.plot(h_adap["step"], h_adap["entropy"], 'b-', lw=2.5, label='Adaptive GWT Gate (Edge of Chaos)')
    ax1.axhline(0.45, color='orange', linestyle=':', label='Target Entropy Balance')
    ax1.set_ylabel('Shannon Entropy (Bits)', fontsize=11)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_title('Workspace Cognitive Phase Transitions & Closed-Loop Control', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right')
    
    # 2. Plot Active Threshold C(t) for Adaptive Mode
    ax2.plot(h_adap["step"], h_adap["threshold"], 'b-', lw=2.5, label='Adaptive Threshold C(t)')
    ax2.set_ylabel('Gating Threshold C(t)', fontsize=11)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right')
    
    # 3. Plot System Coherence Comparison
    ax3.plot(h_high["step"], h_high["coherence"], 'r--', lw=1.5, label='Static High Gate')
    ax3.plot(h_low["step"], h_low["coherence"], 'g--', lw=1.5, label='Static Low Gate')
    ax3.plot(h_adap["step"], h_adap["coherence"], 'b-', lw=2.5, label='Adaptive GWT Gate')
    ax3.set_xlabel('Cognitive Cycle Step (t)', fontsize=11)
    ax3.set_ylabel('Workspace Coherence', fontsize=11)
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc='upper right')
    
    fig.tight_layout()
    plot_path = "results/gwt_adaptive_gating_telemetry.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    
    # Output metrics to JSON
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "steps_simulated": steps,
        "static_high_final_entropy": h_high["entropy"][-1],
        "static_low_final_entropy": h_low["entropy"][-1],
        "adaptive_final_entropy": h_adap["entropy"][-1],
        "adaptive_final_threshold": h_adap["threshold"][-1],
        "adaptive_final_coherence": h_adap["coherence"][-1]
    }
    
    json_path = "results/gwt_adaptive_gating_results.json"
    with open(json_path, "w") as f:
        json.dump(report_data, f, indent=2)
        
    print(f"[+] Simulation complete! Saved JSON to '{json_path}' and comparison plot to '{plot_path}'.")

if __name__ == "__main__":
    main()
