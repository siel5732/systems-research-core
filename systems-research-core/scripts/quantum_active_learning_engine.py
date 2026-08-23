#!/usr/bin/env python3
"""
Quantum-Inspired Active Learning & Topic Decider Engine (Zero-Dependency Edition)
Designed by the Subconscious Systems Group (Marie, Banting, Trent, Aphex).
Models the scientific knowledge landscape as a Hilbert space. 
Propagates a quantum wave function over research topics using a 1D Discrete-Time Quantum Walk (DTQW) 
and collapses it based on "Measurement Operators" derived from local vector database coverage (Shannon Entropy).
"""

import os
import json
import math
import random

# Define Research Topics
MPS_TOPICS = [
    {"id": 0, "title": "Intrathecal Nanoparticle Enzyme Delivery Kinetics across Spinal Cord Barriers", "keywords": ["intrathecal", "nanoparticle", "spinal cord", "transcytosis"]},
    {"id": 1, "title": "CRISPR-Cas12a Homology-Directed Repair (HDR) Optimization using Chondrocyte Enhancers", "keywords": ["crispr", "hdr", "cas12a", "chondrocyte", "nhej"]},
    {"id": 2, "title": "Recombinant IDUA-Apolipoprotein E Fusion Protein Transport across Blood-Brain Barrier (BBB)", "keywords": ["apoe", "fusion protein", "bbb", "receptor-mediated", "endocytosis"]},
    {"id": 3, "title": "Mechanical Joint Load-Bearing Shear Stress Impact on Chondrocyte GAG Synthesis", "keywords": ["shear stress", "mechanical", "chondrocyte", "joint", "synthesis"]},
    {"id": 4, "title": "Maternal-Fetal Transplacental IgG Neutralizing Antibody Transfer Kinetics", "keywords": ["maternal-fetal", "transplacental", "igg", "fcrn", "immunogenicity"]},
    {"id": 5, "title": "Lipid Nanoparticle (LNP)-mRNA Delivery Kinetics for Liver-Targeted Transient IDUA Expression", "keywords": ["lnp", "mrna", "liver-targeted", "transient", "expression"]},
    {"id": 6, "title": "Multi-Frequency Acoustic Levitation and Morphogenesis of 3D Hepatocyte Spheroids", "keywords": ["acoustic", "levitation", "morphogenesis", "spheroid", "hepatocyte"]},
    {"id": 7, "title": "Anti-Drug Antibody (ADA) Humoral Clearance Kinetics and Tolerization", "keywords": ["ada", "humoral", "clearance", "tolerization", "methotrexate"]},
    {"id": 8, "title": "Pharmacological Chaperone Thermodynamic Stabilization of Lysosomal Protein Missense Variants", "keywords": ["chaperone", "thermodynamic", "stabilization", "missense", "variant"]},
    {"id": 9, "title": "Skeletal Chondrocytic Extracellular Matrix Degradation under Local GAG Pressure", "keywords": ["extracellular matrix", "degradation", "chondrocyte", "skeletal", "pressure"]}
]

DIABETES_TOPICS = [
    {"id": 0, "title": "Maturity-Onset Diabetes of the Young Type 3 (MODY3) Mitochondrial Coupled Respiration", "keywords": ["mody3", "mitochondrial", "respiration", "hnf1a", "atp"]},
    {"id": 1, "title": "Closed-Loop Artificial Pancreas Model Predictive Control (MPC) under Exercise Challenges", "keywords": ["closed-loop", "artificial pancreas", "mpc", "exercise", "pid"]},
    {"id": 2, "title": "Pancreatic Beta-Cell Mass Long-Term Decay and Apoptosis under Glucotoxic ER Stress", "keywords": ["beta-cell", "decay", "apoptosis", "glucotoxic", "er stress"]},
    {"id": 3, "title": "Permselective Alginate Hydrogel Micro-Bioreactors Krogh Oxygen Diffusion", "keywords": ["permselective", "alginate", "micro-bioreactor", "krogh", "oxygen"]},
    {"id": 4, "title": "Dual-Agonist Incretin Kinetics on Gastric Emptying Rates and Hypothalamic Appetite Regulation", "keywords": ["dual-agonist", "incretin", "gastric", "appetite", "tirzepatide"]},
    {"id": 5, "title": "Stem-Cell-Derived Islet Cell Xenotransplant Neovascularization & Angiogenesis Coupling", "keywords": ["stem-cell", "islet", "xenotransplant", "neovascularization", "angiogenesis"]},
    {"id": 6, "title": "Glucokinase-Mutated (MODY2) Benign Set-Point Shifting under Postprandial Glucose Excursions", "keywords": ["mody2", "glucokinase", "set-point", "postprandial", "gck"]},
    {"id": 7, "title": "Acoustic-Patterned Concentric Alignment of Beta-Cell Spheroids within Hydrogel Scaffolds", "keywords": ["acoustic", "beta-cell", "spheroid", "concentric", "scaffold"]},
    {"id": 8, "title": "Incretin Co-Agonist Satiety and Glycemic Control Kinetics in Insulin-Resistant Phenotypes", "keywords": ["co-agonist", "satiety", "glycemic", "insulin-resistant", "phenotype"]},
    {"id": 9, "title": "MODY3 K-ATP Channel Bypass Kinetics using Low-Dose Oral Glipizide Therapies", "keywords": ["mody3", "k-atp", "bypass", "glipizide", "sulfonylurea"]}
]

def load_vector_db_coverage(db_path, topics):
    """
    Computes a measurement overlap coefficient based on keywords present in the local vector DB.
    Less coverage (entropy) in the database results in higher quantum potential for selection.
    """
    if not os.path.exists(db_path):
        return [1.0] * len(topics)  # Maximum uncertainty/potential if DB is missing
        
    try:
        with open(db_path, "r") as f:
            db_data = json.load(f)
            
        db_text = json.dumps(db_data).lower()
        
        coverage = []
        for topic in topics:
            hits = 0
            for kw in topic["keywords"]:
                if kw.lower() in db_text:
                    hits += 1
            cov_factor = max(0.1, 1.0 - (hits / len(topic["keywords"])))
            coverage.append(cov_factor)
        return coverage
    except Exception as e:
        return [1.0] * len(topics)

def run_quantum_walk_selection(topics, coverage_factors):
    """
    Simulates a Discrete-Time Quantum Walk (DTQW) on a cycle graph of N nodes in pure Python.
    Applies a Hadamard coin transformation, propagates the state, and applies 
    a Measurement Operator weighted by the vector DB coverage factor.
    """
    N = len(topics)
    # 2 coin states (Left=0, Right=1) x N spatial nodes
    # We store complex numbers as tuples (real, imag)
    state = [[(0.0, 0.0) for _ in range(N)] for _ in range(2)]
    
    # Initialize wave function as a symmetric superposition at node 0
    # Left spin has 1/sqrt(2), Right spin has i/sqrt(2)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    state[0][0] = (inv_sqrt2, 0.0)
    state[1][0] = (0.0, inv_sqrt2)
    
    steps = 7
    
    # Hadamard transformations on complex number tuples (a, b) + (c, d)
    # H = [[1, 1], [1, -1]] / sqrt(2)
    for _ in range(steps):
        # 1. Coin Flip Step: Apply Hadamard to each node's coin states
        for x in range(N):
            left_r, left_i = state[0][x]
            right_r, right_i = state[1][x]
            
            # Left node = (Left + Right) * inv_sqrt2
            new_left_r = (left_r + right_r) * inv_sqrt2
            new_left_i = (left_i + right_i) * inv_sqrt2
            
            # Right node = (Left - Right) * inv_sqrt2
            new_right_r = (left_r - right_r) * inv_sqrt2
            new_right_i = (left_i - right_i) * inv_sqrt2
            
            state[0][x] = (new_left_r, new_left_i)
            state[1][x] = (new_right_r, new_right_i)
            
        # 2. Shift Operator (Propagation)
        new_state = [[(0.0, 0.0) for _ in range(N)] for _ in range(2)]
        for x in range(N):
            # Spin up (Left=0) shifts left (x-1)
            new_state[0][(x - 1) % N] = state[0][x]
            # Spin down (Right=1) shifts right (x+1)
            new_state[1][(x + 1) % N] = state[1][x]
        state = new_state
        
    # 3. Compute Probabilities (modulus squared: real^2 + imag^2)
    probabilities = []
    for x in range(N):
        left_r, left_i = state[0][x]
        right_r, right_i = state[1][x]
        prob = (left_r**2 + left_i**2) + (right_r**2 + right_i**2)
        probabilities.append(prob)
        
    # Apply measurement operators (coverage weights)
    weighted_probs = [p * c for p, c in zip(probabilities, coverage_factors)]
    
    # Re-normalize probability wave
    total_w = sum(weighted_probs)
    if total_w > 0:
        weighted_probs = [w / total_w for w in weighted_probs]
    else:
        weighted_probs = [1.0 / N] * N
        
    # Collapse the wavefunction to select the next research topic (cumulative probability select)
    r = random.random()
    cumulative = 0.0
    selected_idx = 0
    for i, p in enumerate(weighted_probs):
        cumulative += p
        if r <= cumulative:
            selected_idx = i
            break
            
    return selected_idx, weighted_probs

def main():
    mps_db = "mps_research_core/mps_vector_db.json"
    diabetes_db = "diabetes_research_core/diabetes_vector_db.json"
    
    # 1. Load measurement operators from GEEKOM databases
    mps_coverage = load_vector_db_coverage(mps_db, MPS_TOPICS)
    diabetes_coverage = load_vector_db_coverage(diabetes_db, DIABETES_TOPICS)
    
    # 2. Run Quantum Walks
    mps_idx, mps_probs = run_quantum_walk_selection(MPS_TOPICS, mps_coverage)
    diabetes_idx, diabetes_probs = run_quantum_walk_selection(DIABETES_TOPICS, diabetes_coverage)
    
    chosen_mps = MPS_TOPICS[mps_idx]
    chosen_diabetes = DIABETES_TOPICS[diabetes_idx]
    
    # 3. Output results
    decision = {
        "metadata": {
            "title": "Quantum Active Learning Decider Output",
            "timestamp_utc": "2026-07-16 23:00:00",
            "methodology": "Hadamard-Coin 1D Discrete-Time Quantum Walk (DTQW)"
        },
        "mps_core": {
            "selected_topic_id": mps_idx,
            "title": chosen_mps["title"],
            "coverage_factor": round(mps_coverage[mps_idx], 3),
            "wave_amplitude_probability": round(mps_probs[mps_idx], 4),
            "state_vector_probabilities": [round(p, 4) for p in mps_probs]
        },
        "diabetes_core": {
            "selected_topic_id": diabetes_idx,
            "title": chosen_diabetes["title"],
            "coverage_factor": round(diabetes_coverage[diabetes_idx], 3),
            "wave_amplitude_probability": round(diabetes_probs[diabetes_idx], 4),
            "state_vector_probabilities": [round(p, 4) for p in diabetes_probs]
        }
    }
    
    # Ensure directory exists
    os.makedirs("scripts", exist_ok=True)
    
    # Save decision output
    with open("scripts/quantum_decision_output.json", "w") as f:
        json.dump(decision, f, indent=4)
        
    # Print clean readable output for isolated agent execution
    print("====================================================================")
    print("⚛️ QUANTUM-INSPIRED ACTIVE LEARNING DECISION ENGINE COLLAPSE")
    print("====================================================================")
    print(f"MPS-I Chosen Vector: ID {mps_idx} - {chosen_mps['title']}")
    print(f"  - Database Exploration Coefficient: {round(mps_coverage[mps_idx], 3)}")
    print(f"  - Quantum Probability Amplitude: {round(mps_probs[mps_idx], 4)}")
    print("--------------------------------------------------------------------")
    print(f"DIABETES Chosen Vector: ID {diabetes_idx} - {chosen_diabetes['title']}")
    print(f"  - Database Exploration Coefficient: {round(diabetes_coverage[diabetes_idx], 3)}")
    print(f"  - Quantum Probability Amplitude: {round(diabetes_probs[diabetes_idx], 4)}")
    print("====================================================================")

if __name__ == "__main__":
    main()