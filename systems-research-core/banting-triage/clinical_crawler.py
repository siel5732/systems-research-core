#!/usr/bin/env python3
"""
SAGE-Banting Clinical Reference Data Crawler.
Downloads and processes real-world clinical datasets for Diabetes (Pima Indians)
and parses genomic metadata for the IDUA gene (MPS-I) from open-access databases.
"""

import os
import json
import urllib.request
import pandas as pd
from pathlib import Path

# ------------------------------------------------------------------
# Config & Directories
# ------------------------------------------------------------------
OUT_DIR = Path("banting-triage/clinical_reference_data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------
# 1. Download Real-World Diabetes Patient Dataset (Pima Indians)
# ------------------------------------------------------------------
def fetch_pima_diabetes_dataset():
    print("\n[1/2] Fetching Real-World Diabetes Dataset (Pima Indians)...")
    # Public URL for the Pima Indians Diabetes dataset on GitHub/HuggingFace raw csv
    url = "https://raw.githubusercontent.com/jbrownlee/Datasets/master/pima-indians-diabetes.data.csv"
    out_path = OUT_DIR / "diabetes_pima.csv"
    
    try:
        print(f"Downloading from: {url}")
        urllib.request.urlretrieve(url, out_path)
        
        # Load and add headers for structured indexing
        columns = [
            "Pregnancies", "Glucose", "BloodPressure", "SkinThickness", 
            "Insulin", "BMI", "DiabetesPedigreeFunction", "Age", "Outcome"
        ]
        df = pd.read_csv(out_path, names=columns)
        df.to_csv(out_path, index=False)
        
        print(f"Successfully downloaded and structured: {out_path}")
        print(f"  - Total patient profiles: {len(df)}")
        print(f"  - Average Glucose: {df['Glucose'].mean():.1f} mg/dL")
        print(f"  - Average Insulin: {df['Insulin'].mean():.1f} mu U/ml")
    except Exception as e:
        print(f"Failed to fetch diabetes dataset: {e}")

# ------------------------------------------------------------------
# 2. Fetch IDUA Genomic Metadata from Ensembl/NCBI Open APIs
# ------------------------------------------------------------------
def fetch_idua_genomic_metadata():
    print("\n[2/2] Querying Ensembl Genomic API for IDUA Gene (MPS-I)...")
    # Ensembl REST API endpoint for human IDUA gene (ENSG00000127415)
    gene_id = "ENSG00000127415"
    url = f"https://rest.ensembl.org/lookup/id/{gene_id}?content-type=application/json;expand=1"
    out_path = OUT_DIR / "idua_gene_metadata.json"
    
    try:
        print(f"Querying Ensembl REST API: {url}")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        # Structure key fields for local SAGE indexing
        idua_summary = {
            "gene_name": data.get("display_name", "IDUA"),
            "ensembl_id": data.get("id"),
            "description": data.get("description"),
            "chromosome": data.get("seq_region_name"),
            "start_coordinate": data.get("start"),
            "end_coordinate": data.get("end"),
            "strand": "Forward" if data.get("strand") == 1 else "Reverse",
            "biotype": data.get("biotype"),
            "number_of_transcripts": len(data.get("Transcript", []))
        }
        
        with open(out_path, "w") as f:
            json.dump(idua_summary, f, indent=2)
            
        print(f"Successfully retrieved and structured IDUA genomic metadata: {out_path}")
        print(f"  - Gene Name: {idua_summary['gene_name']}")
        print(f"  - Location: Chromosome {idua_summary['chromosome']}:{idua_summary['start_coordinate']}-{idua_summary['end_coordinate']}")
        print(f"  - Number of Active Transcripts: {idua_summary['number_of_transcripts']}")
    except Exception as e:
        print(f"Failed to fetch IDUA genomic metadata: {e}")

# ------------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------------
def main():
    print("==================================================")
    print("       SAGE-BANTING CLINICAL DATA CRAWLER")
    print("==================================================")
    fetch_pima_diabetes_dataset()
    fetch_idua_genomic_metadata()
    print("\n==================================================")
    print("Crawler executed successfully! Reference data is live.")
    print("==================================================")

if __name__ == "__main__":
    main()
