#!/usr/bin/env python3
"""
AcutisForge Preprint Synchronizer
Copies the latest preprints and results to the respective central directories
for commitment and deployment.
"""

import shutil
import os

def main():
    print("====================================================================")
    print("🔄 SYNCHRONIZING ACADEMIC PREPRINTS AND SIMULATION RESULTS")
    print("====================================================================")

    # Paths to source preprints
    mps_src = "mps_research_core/preprints/mps_i_ada_clearance_preprint.md"
    diabetes_src = "diabetes_research_core/diabetes_capsule_oxygen_diffusion_paper.md"
    math_opt_src = "preprints/math_opt_preprint.md"

    # Destination directories
    main_preprints_dir = "preprints"
    sys_preprints_dir = "systems-research-core/preprints"

    os.makedirs(main_preprints_dir, exist_ok=True)
    os.makedirs(sys_preprints_dir, exist_ok=True)

    # 1. Sync MPS-I Preprint
    if os.path.exists(mps_src):
        shutil.copyfile(mps_src, os.path.join(main_preprints_dir, "mps_i_ada_clearance_preprint.md"))
        shutil.copyfile(mps_src, os.path.join(sys_preprints_dir, "mps_i_ada_clearance_preprint.md"))
        print(f"[+] Synchronized MPS-I ADA Clearance Preprint: {mps_src}")
    else:
        print(f"[!] Warning: MPS-I source preprint not found: {mps_src}")

    # 2. Sync Diabetes Preprint
    if os.path.exists(diabetes_src):
        shutil.copyfile(diabetes_src, os.path.join(main_preprints_dir, "diabetes_alginate_bioreactor_preprint.md"))
        shutil.copyfile(diabetes_src, os.path.join(sys_preprints_dir, "diabetes_alginate_bioreactor_preprint.md"))
        print(f"[+] Synchronized Diabetes Alginate Bioreactor Preprint: {diabetes_src}")
    else:
        print(f"[!] Warning: Diabetes source preprint not found: {diabetes_src}")

    # 3. Sync Math Optimization Preprint
    if os.path.exists(math_opt_src):
        shutil.copyfile(math_opt_src, os.path.join(sys_preprints_dir, "math_opt_preprint.md"))
        print(f"[+] Synchronized Mathematical Optimization Preprint: {math_opt_src}")
    else:
        print(f"[!] Warning: Math Optimization source preprint not found: {math_opt_src}")

    # 4. Sync results to systems-research-core
    # We want results for all three topics in systems-research-core/results/ as well
    os.makedirs("systems-research-core/results", exist_ok=True)
    
    shutil.copyfile(
        "research_round/mps/mps_i_simulation_results.json",
        "systems-research-core/results/mps_i_results.json"
    )
    shutil.copyfile(
        "research_round/diabetes/diabetes_simulation_results.json",
        "systems-research-core/results/diabetes_results.json"
    )
    shutil.copyfile(
        "research_round/math_optim/math_optim_relaxation_results.json",
        "systems-research-core/results/math_opt_results.json"
    )
    print("[+] Synchronized simulation results to systems-research-core/results/")

    print("====================================================================")
    print("✅ PREPRINT AND RESULTS SYNCHRONIZATION COMPLETE")
    print("====================================================================")

if __name__ == "__main__":
    main()
