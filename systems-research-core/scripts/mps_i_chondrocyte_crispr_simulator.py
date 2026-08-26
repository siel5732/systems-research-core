#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AcutisForge CRISPR & Molecular Genetics Initiative:
CRISPR-Cas12a NHEJ vs HDR Competitive Repair Kinetics Simulator in Human Chondrocytes.
Author: Dr. Marie Sklodowska-Curie
Focus: Overcoming the avascular skeletal barriers of MPS-I by targeted gene editing in chondrocytes.
"""

import math
import json
import os

def simulate_chondrocyte_crispr(hours=72, dt=0.01):
    time_steps = int(hours / dt)
    results = {}
    
    # Chondrocytes are typically post-mitotic or slow-dividing, making HDR baseline even lower than hepatocytes.
    # We introduce cell-cycle reactivation via transient growth factor treatment (e.g., FGF2/TGF-beta)
    # to push chondrocytes into the active S/G2 phase, dramatically boosting HDR rates.
    cohorts = {
        "Naive CRISPR-Cas12a in Chondrocytes (NHEJ Dominant)": {
            "nhej_rate": 0.52,        # Extremely active NHEJ repair (hr^-1)
            "hdr_rate": 0.002,        # Dismally low baseline HDR in slow-dividing chondrocytes (hr^-1)
            "donor_recruitment_mult": 1.0,
            "description": "Untreated articular chondrocytes relying almost entirely on error-prone NHEJ."
        },
        "NHEJ-Inhibited CRISPR in Chondrocytes (SCR7-Enhanced)": {
            "nhej_rate": 0.052,       # 90% inhibition of NHEJ via Ligase IV inhibitor SCR7
            "hdr_rate": 0.002,
            "donor_recruitment_mult": 3.0, # Slow clearance of DSBs increases donor template availability
            "description": "NHEJ inhibited by SCR7, holding DNA double-strand breaks open longer."
        },
        "AcutisForge Chondrocyte-Targeted HDR-Optimized (FGF2 + SCR7 + NLS-Cas12a)": {
            "nhej_rate": 0.052,       # 90% NHEJ inhibition via SCR7
            "hdr_rate": 0.058,        # 29x HDR boost by pushing chondrocytes into S/G2 phase using transient FGF2 stimulation
            "donor_recruitment_mult": 9.5, # Nuclear Localization Signal (NLS) engineered donor template with Col2a1 enhancer
            "description": "Combined NHEJ inhibition, cell-cycle reactivation with FGF2, and Col2a1-enhancer-driven precise integration."
        }
    }

    for cohort_name, params in cohorts.items():
        t_list = []
        unbroken_dna_pct = 100.0   # Percentage of intact target loci (Col2a1 safe-harbor or similar)
        double_strand_breaks = 0.0 # Percentage of active CRISPR cuts
        nhej_indels = 0.0          # Error-prone indels (joint scarring / loss of structural integrity)
        hdr_integrations = 0.0     # Precise, therapeutic IDUA transgene integrations under Col2a1 enhancer

        k_cut = 0.28 # Cas12a cutting rate constant (hr^-1)

        for step in range(time_steps):
            t = step * dt
            
            # Active CRISPR cut rate decays as guide RNA degrades over time
            active_cut_rate = k_cut * math.exp(-0.06 * t)
            
            # CRISPR cutting ODE
            d_cut = active_cut_rate * unbroken_dna_pct
            
            # NHEJ and HDR repair rates acting on active DSBs
            r_nhej = params["nhej_rate"] * double_strand_breaks
            r_hdr = params["hdr_rate"] * params["donor_recruitment_mult"] * double_strand_breaks
            
            # Systems of ODEs
            dunbroken = -d_cut
            ddsb = d_cut - r_nhej - r_hdr
            dnhej = r_nhej
            dhdr = r_hdr

            # Euler integration
            unbroken_dna_pct = max(0.0, unbroken_dna_pct + dunbroken * dt)
            double_strand_breaks = max(0.0, double_strand_breaks + ddsb * dt)
            nhej_indels = max(0.0, nhej_indels + dnhej * dt)
            hdr_integrations = max(0.0, hdr_integrations + dhdr * dt)

            # Record every 6 hours
            if step % int(6.0 / dt) == 0:
                t_list.append({
                    "time_hours": round(t, 1),
                    "unbroken_dna_pct": round(unbroken_dna_pct, 2),
                    "double_strand_breaks_pct": round(double_strand_breaks, 2),
                    "nhej_indels_pct": round(nhej_indels, 2),
                    "hdr_precise_integration_pct": round(hdr_integrations, 2)
                })

        # Append final 72h point
        t_list.append({
            "time_hours": round(hours, 1),
            "unbroken_dna_pct": round(unbroken_dna_pct, 2),
            "double_strand_breaks_pct": round(double_strand_breaks, 2),
            "nhej_indels_pct": round(nhej_indels, 2),
            "hdr_precise_integration_pct": round(hdr_integrations, 2)
        })

        results[cohort_name] = {
            "metadata": {
                "nhej_rate_constant": params["nhej_rate"],
                "hdr_rate_constant": params["hdr_rate"],
                "donor_recruitment_mult": params["donor_recruitment_mult"],
                "description": params["description"]
            },
            "trajectory": t_list
        }

    return results

def main():
    print("🧬 SIMULATING CHONDROCYTE CRISPR-CAS12A REPAIR KINETICS...")
    results = simulate_chondrocyte_crispr()
    
    # Format and save to research_round/mps_i/mps_i_simulation_results.json
    output_dir = "research_round/mps_i"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "mps_i_simulation_results.json")
    
    payload = {
        "metadata": {
            "title": "MPS-I Articular Chondrocyte CRISPR-Cas12a Homology-Directed Repair (HDR) Kinetics Simulation",
            "PI": "Dr. Marie Sklodowska-Curie",
            "date": "2026-08-20",
            "units": {
                "time": "hours",
                "dna_states": "percentage (%) of total alleles"
            }
        },
        "simulation_results": results
    }
    
    with open(output_path, "w") as f:
        json.dump(payload, f, indent=4)
        
    print(f"✅ Successfully cached chondrocyte repair kinetics to {output_path}")

if __name__ == "__main__":
    main()
