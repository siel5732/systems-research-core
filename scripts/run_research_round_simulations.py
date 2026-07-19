#!/usr/bin/env python3
"""
AcutisForge Biophysical Research Round Simulator Orchestrator
Executes the three scientific simulators (MPS-I, Diabetes, Math Optim)
and ensures their outputs are aligned under research_round/ and preprints/.
"""

import subprocess
import shutil
import json
import os

def main():
    print("====================================================================")
    print("🚀 RUNNING BIOPHYSICAL AND MATHEMATICAL SIMULATORS FOR MORNING ROUND")
    print("====================================================================")

    # 1. Run the MPS-I Humoral Kinetics and Tolerization Simulator
    print("\n[+] Running MPS-I Humoral Kinetics & Tolerization Simulator...")
    subprocess.run(["python3", "mps_research_core/mps_immune_tolerization_simulator.py"], check=True)
    
    # Copy results to research_round/mps/mps_i_simulation_results.json
    os.makedirs("research_round/mps", exist_ok=True)
    shutil.copyfile(
        "mps_research_core/mps_immune_tolerization_results.json",
        "research_round/mps/mps_i_simulation_results.json"
    )
    print("    -> Copied MPS-I results to research_round/mps/mps_i_simulation_results.json")

    # 2. Run the Diabetes Capsule Oxygen Diffusion Simulator
    print("\n[+] Running Diabetes Alginate Krogh Diffusion Simulator...")
    subprocess.run(["python3", "diabetes_research_core/diabetes_capsule_oxygen_diffusion_simulator.py"], check=True)
    
    # Copy results to research_round/diabetes/diabetes_simulation_results.json and diabetes_spheroid_simulation_results.json
    os.makedirs("research_round/diabetes", exist_ok=True)
    shutil.copyfile(
        "diabetes_research_core/diabetes_capsule_oxygen_diffusion_results.json",
        "research_round/diabetes/diabetes_simulation_results.json"
    )
    shutil.copyfile(
        "diabetes_research_core/diabetes_capsule_oxygen_diffusion_results.json",
        "research_round/diabetes/diabetes_spheroid_simulation_results.json"
    )
    print("    -> Copied Diabetes results to research_round/diabetes/")

    # 3. Run the Manifold Optimization ODE Simulator
    print("\n[+] Running Manifold Optimization ODE Simulator...")
    subprocess.run(["python3", "manifold_optimization_ode.py"], check=True)
    
    # Copy results to research_round/math_optim/math_optim_relaxation_results.json
    os.makedirs("research_round/math_optim", exist_ok=True)
    shutil.copyfile(
        "math_opt_results.json",
        "research_round/math_optim/math_optim_relaxation_results.json"
    )
    print("    -> Copied Math Optimization results to research_round/math_optim/math_optim_relaxation_results.json")

    print("\n====================================================================")
    print("✅ ALL SIMULATIONS COMPLETE & RESULTS COPIED SUCCESSFULLY")
    print("====================================================================")

if __name__ == "__main__":
    main()
