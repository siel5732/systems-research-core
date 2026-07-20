#!/usr/bin/env python3
"""
AcutisForge Biophysical Research Round Simulator Orchestrator (Dynamic Edition)
Executes the three scientific simulators (MPS-I, Diabetes, Math Optim) for the dynamically selected topics:
- MPS-I: Lipid Nanoparticle (LNP)-mRNA Delivery Kinetics (Topic 5) or matching selection
- Diabetes: Acoustic-Patterned Concentric Alignment of Beta-Cell Spheroids (Topic 7) or matching selection
- Math Optim: Geometric ODE Simulator & Manifold Relaxation
Ensures their outputs are aligned under research_round/ and preprints/.
"""

import subprocess
import shutil
import os
import json

def main():
    print("====================================================================")
    print("🚀 RUNNING DYNAMIC BIOPHYSICAL AND MATHEMATICAL SIMULATORS")
    print("====================================================================")

    # 1. Load the selected topics from the Quantum Active Learning Engine
    decision_file = "scripts/quantum_decision_output.json"
    if not os.path.exists(decision_file):
        raise FileNotFoundError(f"Could not find quantum decision file: {decision_file}")

    with open(decision_file, "r") as f:
        decision = json.load(f)

    mps_id = decision["mps_core"]["selected_topic_id"]
    mps_title = decision["mps_core"]["title"]
    diabetes_id = decision["diabetes_core"]["selected_topic_id"]
    diabetes_title = decision["diabetes_core"]["title"]

    print(f"[+] Loaded selected MPS-I topic (ID {mps_id}): {mps_title}")
    print(f"[+] Loaded selected Diabetes topic (ID {diabetes_id}): {diabetes_title}")

    # Map MPS topics to simulators and result files
    mps_mappings = {
        5: {
            "script": "mps_research_core/mps_lnp_mrna_simulator.py",
            "results_src": "results/mps_i_lnp_delivery_results.json",
            "results_dst": "research_round/mps/mps_i_simulation_results.json"
        }
    }
    
    # Map Diabetes topics to simulators and result files
    diabetes_mappings = {
        3: {
            "script": "diabetes_research_core/diabetes_capsule_oxygen_diffusion_simulator.py",
            "results_src": "diabetes_research_core/diabetes_capsule_oxygen_diffusion_results.json",
            "results_dst": "research_round/diabetes/diabetes_simulation_results.json",
            "additional_dst": "research_round/diabetes/diabetes_spheroid_simulation_results.json"
        },
        7: {
            "script": "diabetes_research_core/diabetes_acoustic_islet_simulator.py",
            "results_src": "diabetes_research_core/diabetes_acoustic_islet_results.json",
            "results_dst": "research_round/diabetes/diabetes_simulation_results.json",
            "additional_dst": "research_round/diabetes/diabetes_spheroid_simulation_results.json"
        }
    }

    # Execute MPS-I Simulator
    mps_info = mps_mappings.get(mps_id, mps_mappings[5])  # Fallback to topic 5
    print(f"\n[+] Executing MPS-I Simulator: {mps_info['script']}...")
    subprocess.run(["python3", mps_info["script"]], check=True)
    
    os.makedirs("research_round/mps", exist_ok=True)
    if os.path.exists(mps_info["results_src"]):
        shutil.copyfile(mps_info["results_src"], mps_info["results_dst"])
        print(f"    -> Copied MPS-I results from {mps_info['results_src']} to {mps_info['results_dst']}")
    else:
        print(f"    [!] Error: MPS-I results source not found at {mps_info['results_src']}")

    # Execute Diabetes Simulator
    diabetes_info = diabetes_mappings.get(diabetes_id, diabetes_mappings[7])  # Default to 7
    print(f"\n[+] Executing Diabetes Simulator: {diabetes_info['script']}...")
    subprocess.run(["python3", diabetes_info["script"]], check=True)
    
    os.makedirs("research_round/diabetes", exist_ok=True)
    if os.path.exists(diabetes_info["results_src"]):
        shutil.copyfile(diabetes_info["results_src"], diabetes_info["results_dst"])
        print(f"    -> Copied Diabetes results from {diabetes_info['results_src']} to {diabetes_info['results_dst']}")
        if "additional_dst" in diabetes_info:
            shutil.copyfile(diabetes_info["results_src"], diabetes_info["additional_dst"])
            print(f"    -> Copied Diabetes results to additional destination: {diabetes_info['additional_dst']}")
    else:
        print(f"    [!] Error: Diabetes results source not found at {diabetes_info['results_src']}")

    # Execute Math Optimization ODE Simulator
    print("\n[+] Executing Manifold Optimization ODE Simulator...")
    subprocess.run(["python3", "manifold_optimization_ode.py"], check=True)
    
    os.makedirs("research_round/math_optim", exist_ok=True)
    if os.path.exists("math_opt_results.json"):
        shutil.copyfile("math_opt_results.json", "research_round/math_optim/math_optim_relaxation_results.json")
        print("    -> Copied Math Optimization results to research_round/math_optim/math_optim_relaxation_results.json")
    else:
        print("    [!] Error: Math Optimization results source not found at math_opt_results.json")

    print("\n====================================================================")
    print("✅ DYNAMIC BIOPHYSICAL & MATHEMATICAL SIMULATIONS COMPLETE")
    print("====================================================================")

if __name__ == "__main__":
    main()
