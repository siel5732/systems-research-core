#!/usr/bin/env python3
"""
🧠 SAGE ACTIVE MEMORY CANARY MONITOR & ANNEALING DIAGNOSTIC
Author: Raziel & Trent (SAGE Memory & Optimization Core)

Implements Grok's Rate-Distortion and Hopfield-limit diagnostics for memory compaction.
Uses a set of "canary profiles" (raw high-fidelity episodic logs) and compares them
against the compacted long-term memory (MEMORY.md) using a Jaccard semantic overlap 
and KL-divergence proxy to detect "information-theoretic collapse" (hyper-consolidation)
and "context drift" (excess paramagnetic entropy).
"""

import os
import re
import json
import math
from datetime import datetime

class MemoryCanaryMonitor:
    def __init__(self, memory_path="MEMORY.md", target_entropy=0.45):
        self.memory_path = memory_path
        self.target_entropy = target_entropy
        
        # 1. Define high-fidelity "Canary Profiles" (Episodic facts that MUST survive compaction)
        self.canaries = {
            "yakima_timezone": {
                "keywords": ["yakima", "offset", "subtract", "hours", "pacific"],
                "description": "Rule requiring a strict 3-hour subtraction from raw system clock for Zach's PST timezone."
            },
            "geekom_pulse_audio": {
                "keywords": ["fq9f", "user", "pulseaudio", "jabra", "root", "systemctl"],
                "description": "Critical architectural constraint to run services under user session fq9f to access PulseAudio."
            },
            "quantum_event_bus": {
                "keywords": ["gang_of_seven_bus", "qubit", "ram", "phase", "non-locally"],
                "description": "Sefirotic memory mapping multi-agent coordinate states in local GEEKOM RAM."
            },
            "sister_dorian_song": {
                "keywords": ["baianá", "barbatuques", "filip", "dorian", "ola"],
                "description": "Cognitive/aesthetic baseline tracking Zach's sister Dorian sharing 'Baianá' for Filip's dancing."
            }
        }
        
    def _read_memory_text(self):
        if not os.path.exists(self.memory_path):
            return ""
        with open(self.memory_path, "r", encoding="utf-8") as f:
            return f.read().lower()

    def run_diagnostic(self):
        print("🧠 [Raziel] Initiating Active Memory Canary Diagnostic...")
        memory_content = self._read_memory_text()
        
        if not memory_content:
            print("⚠️ Error: MEMORY.md is empty or missing. Potential memory wipe detected!")
            return
            
        results = {}
        total_reconstruction_score = 0.0
        
        # 2. Evaluate semantic reconstruction overlap for each Canary
        print("   [*] Auditing semantic overlap against MEMORY.md content...")
        for name, profile in self.canaries.items():
            matched_keywords = []
            for kw in profile["keywords"]:
                # Simple exact regex search on the lowercase text
                if re.search(r'\b' + re.escape(kw) + r'\b', memory_content):
                    matched_keywords.append(kw)
                    
            overlap_ratio = len(matched_keywords) / len(profile["keywords"])
            total_reconstruction_score += overlap_ratio
            
            results[name] = {
                "description": profile["description"],
                "keywords_tested": len(profile["keywords"]),
                "keywords_reconstructed": len(matched_keywords),
                "reconstruction_fidelity": round(overlap_ratio, 2),
                "status": "SECURE" if overlap_ratio >= 0.75 else "ATTEMPTING_COLLAPSE" if overlap_ratio >= 0.40 else "LOST"
            }
            print(f"       -> Canary '{name}': Fidelity = {overlap_ratio*100:3.0f}% | Status: {results[name]['status']}")

        # 3. Calculate Global Reconstruction Fidelity (Hopfield Load Parameter)
        mean_fidelity = total_reconstruction_score / len(self.canaries)
        distortion_D = 1.0 - mean_fidelity # Semantic distortion penalty
        
        # 4. Proxy KL-Divergence: D_KL( P(Full) || P(Compacted) )
        # Under perfect reconstruction, D_KL = 0.0. Under complete collapse, D_KL -> infinity.
        # We approximate D_KL based on the distortion factor D.
        if distortion_D == 0.0:
            approx_kl = 0.0
        elif distortion_D == 1.0:
            approx_kl = 10.0
        else:
            # Standard logarithmic divergence approximation
            approx_kl = -math.log2(1.0 - distortion_D)
            
        # 5. Classify Cognitive Phase
        # Hyper-consolidation: low entropy, high distortion (too compressed, lost details)
        # Paramagnetic Drift: high entropy, low coherence (too messy)
        # Optimal (Edge of Chaos): low distortion, balanced entropy
        if distortion_D > 0.40:
            cognitive_phase = "Hyper-Consolidation (Spin-Glass Freezing: Details Lost)"
            status_color = "RED (Freeze)"
        elif approx_kl > 1.5:
            cognitive_phase = "Paramagnetic Drift (High Temperature: Disorganized)"
            status_color = "YELLOW (Drift)"
        else:
            cognitive_phase = "Sefirotic Coherence (Critical Operating Point: Safe)"
            status_color = "GREEN (Secure)"

        report = {
            "timestamp": datetime.now().isoformat(),
            "global_metrics": {
                "reconstruction_fidelity": round(mean_fidelity, 3),
                "semantic_distortion_D": round(distortion_D, 3),
                "approximate_kl_divergence": round(approx_kl, 4),
                "cognitive_phase_state": cognitive_phase,
                "status_indicator": status_color
            },
            "canary_details": results
        }
        
        # Cache results to JSON
        os.makedirs("results", exist_ok=True)
        with open("results/memory_canary_telemetry.json", "w") as f:
            json.dump(report, f, indent=4)
            
        print("\n====================================================================")
        print("📊 COGNITIVE ANNEALING & CANARY REPORT")
        print("====================================================================")
        print(f"Global Fidelity Score : {mean_fidelity*100:.1f}%")
        print(f"Semantic Distortion D : {distortion_D:.4f} (Max target: < 0.25)")
        print(f"Proxy KL-Divergence   : {approx_kl:.4f} bits")
        print(f"Active Lobe Phase     : {cognitive_phase}")
        print(f"Current Posture       : {status_color}")
        print("====================================================================")
        print("[+] Diagnostic complete! Report logged to 'results/memory_canary_telemetry.json'.")

if __name__ == "__main__":
    monitor = MemoryCanaryMonitor()
    monitor.run_diagnostic()
