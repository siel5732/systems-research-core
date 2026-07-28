#!/usr/bin/env python3
"""
AcutisForge Preprint Synchronizer (Dynamic Edition)
Copies the latest preprints and results for the selected topics:
- MPS-I: Lipid Nanoparticle (LNP)-mRNA Delivery Kinetics (Topic 5) or matching selection
- Diabetes: Acoustic-Patterned Concentric Alignment of Beta-Cell Spheroids (Topic 7) or matching selection
- Math Optim: Geometric ODE Simulator & Manifold Relaxation
to the respective central directories for commitment and deployment.
"""

import shutil
import os
import json

def main():
    print("====================================================================")
    print("🔄 SYNCHRONIZING ACADEMIC PREPRINTS AND SIMULATION RESULTS")
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

    # Destination directories
    main_preprints_dir = "preprints"
    sys_preprints_dir = "systems-research-core/preprints"

    os.makedirs(main_preprints_dir, exist_ok=True)
    os.makedirs(sys_preprints_dir, exist_ok=True)

    # 1. Sync MPS-I Preprint
    # Map topic ID to source file
    mps_preprints = {
        1: {
            "src": "mps_research_core/crispr_hdr_kinetics_paper.md",
            "dst": "mps_i_crispr_hdr_preprint.md"
        },
        3: {
            "src": "mps_research_core/mps_joint_shear_stress_paper.md",
            "dst": "mps_i_joint_shear_stress_preprint.md"
        },
        5: {
            "src": "mps_research_core/mps_lnp_mrna_paper.md",
            "dst": "mps_i_lnp_delivery_preprint.md"
        },
        7: {
            "src": "mps_research_core/immune_tolerization_paper.md",
            "dst": "mps_i_ada_clearance_preprint.md"
        },
        9: {
            "src": "mps_research_core/mps_skeletal_matrix_degradation_paper.md",
            "dst": "mps_i_skeletal_matrix_degradation_preprint.md"
        }
    }
    mps_info = mps_preprints.get(mps_id, mps_preprints[5])
    mps_src = mps_info["src"]
    mps_dst_name = mps_info["dst"]

    if os.path.exists(mps_src):
        shutil.copyfile(mps_src, os.path.join(main_preprints_dir, mps_dst_name))
        shutil.copyfile(mps_src, os.path.join(sys_preprints_dir, mps_dst_name))
        print(f"[+] Synchronized MPS-I Preprint: {mps_src} -> {mps_dst_name}")
    else:
        print(f"[!] Warning: MPS-I source preprint not found: {mps_src}")

    # 2. Sync Diabetes Preprint
    # Map topic ID to source file
    diabetes_preprints = {
        1: {
            "src": "diabetes_research_core/artificial_pancreas_paper.md",
            "dst": "diabetes_preprint.md"
        },
        3: {
            "src": "diabetes_research_core/diabetes_capsule_oxygen_diffusion_paper.md",
            "dst": "diabetes_alginate_bioreactor_preprint.md"
        },
        5: {
            "src": "diabetes_research_core/islet_neovascularization_paper.md",
            "dst": "diabetes_islet_xenotransplant_preprint.md"
        },
        7: {
            "src": "diabetes_research_core/acoustic_islet_patterning_paper.md",
            "dst": "diabetes_acoustic_islet_patterning_preprint.md"
        }
    }
    db_info = diabetes_preprints.get(diabetes_id, diabetes_preprints[7])
    diabetes_src = db_info["src"]
    diabetes_dst_name = db_info["dst"]

    if os.path.exists(diabetes_src):
        shutil.copyfile(diabetes_src, os.path.join(main_preprints_dir, diabetes_dst_name))
        shutil.copyfile(diabetes_src, os.path.join(sys_preprints_dir, diabetes_dst_name))
        print(f"[+] Synchronized Diabetes Preprint: {diabetes_src} -> {diabetes_dst_name}")
    else:
        print(f"[!] Warning: Diabetes source preprint not found: {diabetes_src}")

    # 3. Sync Math Optimization Preprint
    math_opt_src = "math_optim_preprint.md"
    if os.path.exists(math_opt_src):
        shutil.copyfile(math_opt_src, os.path.join(main_preprints_dir, "math_opt_oblique_manifold_preprint.md"))
        shutil.copyfile(math_opt_src, os.path.join(sys_preprints_dir, "math_opt_oblique_manifold_preprint.md"))
        shutil.copyfile(math_opt_src, os.path.join(sys_preprints_dir, "math_opt_preprint.md"))
        print(f"[+] Synchronized Mathematical Optimization Preprint: {math_opt_src}")
    else:
        print(f"[!] Warning: Math Optimization source preprint not found: {math_opt_src}")

    # 4. Sync results to systems-research-core/results
    os.makedirs("systems-research-core/results", exist_ok=True)
    
    # We copy the consolidated results
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
