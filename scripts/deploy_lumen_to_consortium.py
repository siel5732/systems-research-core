#!/usr/bin/env python3
"""
scripts/deploy_lumen_to_consortium.py

Programmatic deployment script to upload SAGE-Lumen-3M model weights,
tokenizer configurations, and the architecture definition directly to the
Small Model Consortium (slmconsortium) organization on Hugging Face as a PR.
"""

import os
import sys
import argparse

try:
    from huggingface_hub import HfApi, create_repo, CommitOperationAdd
except ImportError:
    print("[-] huggingface_hub library not found. Run: pip install huggingface_hub")
    sys.exit(1)

def deploy_lumen_to_consortium(
    token,
    model_dir="/home/fq9f/systems-research-core/models/lumen_pretrained_3m",
    tokenizer_path="/home/fq9f/systems-research-core/models/lumen_tokenizer/tokenizer.json",
    arch_path="/home/fq9f/systems-research-core/scripts/lumen_model_architecture.py",
    repo_id="slmconsortium/sage-lumen-3m"
):
    if not token:
        print("[!] Error: No Hugging Face token provided. Pass it via --token *** or set the HF_TOKEN environment variable.")
        sys.exit(1)
        
    api = HfApi(token=token)
    
    print(f"[*] Initializing Small Model Consortium Release: {repo_id}...")
    
    # 1. Create the repository on Hugging Face under the Consortium Org (no-op since Zach already created it)
    try:
        create_repo(
            repo_id=repo_id,
            token=***
            repo_type="model",
            exist_ok=True,
            private=False # Public and open-source for the Consortium!
        )
        print(f"[+] Hugging Face Consortium repository '{repo_id}' verified/created successfully.")
    except Exception as e:
        print(f"[!] Note: Repository already exists or verification bypassed: {e}")

    # 2. Write a beautiful, custom README for the Consortium
    readme_content = f"""---
language:
- en
tags:
- state-space
- physical-simulation
- quantum-mechanics
- differential-equations
- g-code
- edge-llm
- sovereign-ai
- muon-optimizer
license: mit
metrics:
- causal-entropy-loss
---

# 📐 SAGE-Lumen-3M: Sovereign State-Space Transition Engine
**SAGE-Lumen-3M** is an ultra-compact, parameter-disciplined 3 million parameter language model optimized for offline edge execution on homelab nodes (e.g., AMD Ryzen APUs).

Published as an official contribution to the **Small Model Consortium (SLMConsortium)**.

Unlike general-purpose chatbots, SAGE-Lumen-3M is built strictly as a **Symbolic Physical Reasoning and State-Space Transition Simulator**. It models trajectories across three primary domains:
1. **Discrete-Time Quantum Walks (DTQW):** Simulating 1-D position states under Hadamard-coin operations.
2. **Biophysical ODE Trajectories:** Homeostatic insulin-glucose couplings and islet cell neovascularization.
3. **Non-Planar G-code Toolpaths:** Predicting Z-axis warp corrections dynamically against mechanical thermals.

## 🧠 Architectural Specifications
- **Parameters:** 2,754,816 active parameters (Tied Embeddings)
- **Vocabulary Size:** 2,048 (Capped BPE)
- **Decoder Layers:** 4 layers
- **Attention Heads:** 4 query heads, 1 Key-Value head (**Multi-Query Attention**)
- **Position Embeddings:** Rotary Positional Embeddings (**RoPE**)
- **Feed-Forward Blocks:** SwiGLU MLP (SiLU-gated, intermediate dimension 512)
- **Normalization:** RMSNorm (Root Mean Square Layer Normalization)
- **Training Optimization:** Matrix-preconditioned momentum (**Muon Optimizer** on 2D projections, AdamW on 1D variables).

## 🚀 Quickstart Usage (PyTorch)
```python
import torch
# Place the model on your local target device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

For full details on SAGE (Sovereign Agentic Governance & Epistemic Protocol) or Logos OS, check our Github repository at `siel5732/systems-research-core`.
"""
    readme_path = "temp_consortium_readme.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("[*] Staging files for Hugging Face Hub Pull Request...")
    
    # 3. Define the file uploads map
    files_to_upload = {
        readme_path: "README.md",
        tokenizer_path: "tokenizer.json",
        arch_path: "model_architecture.py"
    }
    
    pytorch_bin = os.path.join(model_dir, "pytorch_model.bin")
    if os.path.exists(pytorch_bin):
        files_to_upload[pytorch_bin] = "pytorch_model.bin"
    else:
        vps_bin = "models/lumen_pretrained_3m/pytorch_model.bin"
        if os.path.exists(vps_bin):
            files_to_upload[vps_bin] = "pytorch_model.bin"
            
    # Build commit operations list
    operations = []
    for local_file, repo_file in files_to_upload.items():
        if os.path.exists(local_file):
            print(f"  - Staging {local_file} -> {repo_file}...")
            operations.append(CommitOperationAdd(path_in_repo=repo_file, path_or_fileobj=local_file))
        else:
            print(f"  - [!] Warning: Local file '{local_file}' not found. Skipping.")

    if not operations:
        print("[!] Error: No files to upload. Process aborted.")
        sys.exit(1)

    print(f"[*] Executing programmatically opened Pull Request on {repo_id}...")
    try:
        pr_info = api.create_commit(
            repo_id=repo_id,
            operations=operations,
            commit_message="Publish SAGE-Lumen-3M model weights, tokenizer, and architecture",
            token=token,
            repo_type="model",
            create_pr=True
        )
        print(f"\n[+] Pull Request successfully created live!")
        print(f"    [+] PR URL: {pr_info.pr_url}")
        print(f"\n[+] Consortium Release Submitted! SAGE-Lumen-3M is live and awaiting merge at: {pr_info.pr_url}")
    except Exception as e:
        print(f"    [!] Error during Pull Request creation: {e}")
        print("\n[-] Upload failed. Please check your token or repository state.")

    # Clean up local temporary README
    if os.path.exists(readme_path):
        os.remove(readme_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy SAGE-Lumen-3M to the Small Model Consortium as a PR")
    parser.add_argument("--token", type=str, default=os.environ.get("HF_TOKEN"), help="Hugging Face API Write Token")
    args = parser.parse_args()
    
    deploy_lumen_to_consortium(token=args.token)
