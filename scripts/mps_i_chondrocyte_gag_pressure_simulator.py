#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcutisForge MPS-I Chondrocyte & Skeletal Biomechanics Initiative:
ODE Simulator of Skeletal Chondrocytic Extracellular Matrix Degradation under Local GAG Pressure.
Author: Dr. Marie Sklodowska-Curie
Models local GAG accumulation, osmotic swelling pressure, MMP-mediated matrix degradation,
and chondrocyte viability rescue via localized gene correction.
"""

import math
import json
import os

def simulate_chondrocyte_gag_pressure(days=90, dt=0.1):
    time_steps = int(days / dt)
    results = {}
    
    # We define three physiological cohorts:
    # 1. Untreated MPS-I (zero IDUA, high GAG accumulation)
    # 2. Standard ERT (Laronidase, poor cartilage penetration and high systemic clearance)
    # 3. AcutisForge Chondrocyte-Targeted CRISPR/LNP (rejuvenated, sustained local IDUA expression)
    cohorts = {
        "Untreated MPS-I Chondrocytes": {
            "idua_level": 0.0,              # No enzyme
            "k_syn_gag": 5.0,               # Synthesis rate of GAGs (mg/g/day)
            "description": "Zero endogenous IDUA. Runaway GAG accumulation and severe osmotic matrix swelling."
        },
        "Standard Enzyme Replacement Therapy (ERT)": {
            "idua_level": 0.08,             # Poor avascular cartilage penetration (~8% of healthy baseline)
            "k_syn_gag": 5.0,
            "description": "Systemic laronidase infusions. Limited cartilage diffusion leaves deep tissue exposed to GAG pressure."
        },
        "AcutisForge Chondrocyte-Targeted CRISPR Rejuvenation": {
            "idua_level": 0.85,             # 85% normal healthy expression via targeted Cas12a gene correction in chondrocytes
            "k_syn_gag": 5.0,
            "description": "Direct chondrocytic editing yielding continuous local IDUA secretion, clearing GAGs from the inside out."
        }
    }

    # Model parameters
    V_max_IDUA = 12.0      # GAG clearance rate (mg/g/day per unit IDUA)
    K_M_GAG = 15.0         # Michaelis-Menten constant for GAG clearance (mg/g)
    
    P_baseline = 100.0     # Baseline cartilage hydrostatic pressure (kPa)
    alpha_press = 0.04     # Osmotic coefficient of sulfated GAGs (kPa / (mg/g)^2)
    
    k_mmp_baseline = 0.5   # Baseline MMP secretion (relative units/day)
    k_mmp_press = 0.015    # Pressure-induced MMP upregulation coefficient (units/day per kPa)
    P_threshold = 150.0    # Swelling pressure threshold for mechanical MMP activation (kPa)
    lambda_mmp = 0.25      # Clearance rate of MMPs (day^-1)
    
    k_ecm_syn = 0.02       # ECM repair rate by chondrocytes (day^-1)
    k_ecm_deg = 0.05       # ECM degradation rate by MMPs (day^-1 per unit MMP)
    
    k_chond_growth = 0.01  # Slow cartilage cell replication (day^-1)
    k_death_press = 0.0003 # Pressure-induced chondrocyte apoptosis rate (day^-1 per kPa)
    P_death_thresh = 180.0 # Pressure threshold for mechanical damage (kPa)
    k_death_anoikis = 0.005 # Apoptosis rate due to matrix detachment / loss of ECM support (day^-1 per % ECM loss)

    for cohort_name, params in cohorts.items():
        t_list = []
        
        # Initial conditions at Day 0 (severe MPS-I pathology before treatment)
        G = 65.0              # High pathological GAG accumulation (mg/g tissue) [Normal is <10.0]
        M_degrade = 12.0      # High baseline MMP activity due to chronic inflammation
        I_ECM = 45.0          # Severely compromised ECM integrity (% of normal)
        V_chond = 60.0        # Degraded chondrocyte viability (% of normal population)
        
        idua_active = params["idua_level"]

        for step in range(time_steps):
            t = step * dt
            
            # 1. GAG dynamics: synthesis - clearance
            # Clearance rate depends on active local IDUA level
            clearance_rate = (V_max_IDUA * idua_active * G) / (K_M_GAG + G)
            dG = params["k_syn_gag"] - clearance_rate
            
            # 2. Compute non-linear physical swelling pressure
            # Sulfated GAGs have dense negative charges, creating powerful osmotic swelling
            P = P_baseline + alpha_press * (G ** 2)
            
            # 3. MMP / Aggrecanase secretion
            # Excessive physical pressure triggers mechanoreceptors (integrins/stretch channels)
            # leading to massive MMP/ADAMTS upregulation
            active_pressure_stress = max(0.0, P - P_threshold)
            dM_degrade = k_mmp_baseline + k_mmp_press * active_pressure_stress * (V_chond / 100.0) - lambda_mmp * M_degrade
            
            # 4. ECM Integrity dynamics
            # Synthesis depends on living chondrocytes; degradation driven by active MMPs
            dI_ECM = k_ecm_syn * (V_chond / 100.0) * (100.0 - I_ECM) - k_ecm_deg * M_degrade * I_ECM
            
            # 5. Chondrocyte Viability dynamics
            # Threatened by excessive physical pressure and loss of structural ECM support (anoikis)
            p_death = k_death_press * max(0.0, P - P_death_thresh)
            a_death = k_death_anoikis * (100.0 - I_ECM)
            dV_chond = k_chond_growth * (V_chond / 100.0) * (100.0 - V_chond) - (p_death + a_death) * V_chond

            # Euler integration
            G = max(0.0, G + dG * dt)
            M_degrade = max(0.0, M_degrade + dM_degrade * dt)
            I_ECM = max(0.0, min(100.0, I_ECM + dI_ECM * dt))
            V_chond = max(0.0, min(100.0, V_chond + dV_chond * dt))

            # Record every 5 days
            if step % int(5.0 / dt) == 0:
                t_list.append({
                    "time_days": round(t, 1),
                    "gag_concentration_mg_g": round(G, 2),
                    "swelling_pressure_kPa": round(P, 2),
                    "mmp_concentration_units": round(M_degrade, 2),
                    "ecm_integrity_pct": round(I_ECM, 2),
                    "chondrocyte_viability_pct": round(V_chond, 2)
                })

        # Append final day point
        t_list.append({
            "time_days": round(days, 1),
            "gag_concentration_mg_g": round(G, 2),
            "swelling_pressure_kPa": round(P, 2),
            "mmp_concentration_units": round(M_degrade, 2),
            "ecm_integrity_pct": round(I_ECM, 2),
            "chondrocyte_viability_pct": round(V_chond, 2)
        })

        results[cohort_name] = {
            "metadata": {
                "idua_level": params["idua_level"],
                "k_syn_gag": params["k_syn_gag"],
                "description": params["description"]
            },
            "trajectory": t_list
        }

    return results

def main():
    print("🧬 SIMULATING SKELETAL CHONDROCYTIC ECM DEGRADATION & GAG PRESSURE...")
    results = simulate_chondrocyte_gag_pressure()
    
    # Save to multiple paths
    output_dirs = ["research_round/mps_i", "systems-research-core/research_round/mps_i"]
    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        output_path = os.path.join(out_dir, "mps_i_simulation_results.json")
        
        payload = {
            "metadata": {
                "title": "Skeletal Chondrocytic Extracellular Matrix Degradation under Local GAG Pressure",
                "PI": "Dr. Marie Sklodowska-Curie",
                "date": "2026-08-25",
                "units": {
                    "time": "days",
                    "gag_concentration": "mg/g wet tissue",
                    "swelling_pressure": "kPa",
                    "mmp_concentration": "relative units",
                    "ecm_integrity": "percentage (%) of normal healthy matrix",
                    "chondrocyte_viability": "percentage (%) of normal cell population"
                }
            },
            "simulation_results": results
        }
        
        with open(output_path, "w") as f:
            json.dump(payload, f, indent=4)
        print(f"✅ Successfully saved simulation data to {output_path}")

if __name__ == "__main__":
    main()
