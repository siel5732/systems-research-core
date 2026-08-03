#!/usr/bin/env python3
import os
import sys
import argparse
from huggingface_hub import snapshot_download

# ======================================================================
# SOVEREIGN LOGOS KERNEL: KIMI-K2.6 MODEL ACQUISITION UTILITY
# Downloads and registers the open-source Kimi-K2.6 Multimodal Agentic core.
# Uses huggingface_hub to fetch split GGUF shards efficiently.
# ======================================================================

REPO_ID = "unsloth/Kimi-K2.6-GGUF"
DEFAULT_TIER = "UD-Q4_K_XL"

TIER_EXPLANATION = {
    "UD-Q2_K_XL": "2-bit Ultra-Compressed Dynamic Quant (8 shards, lightweight, high speed)",
    "UD-Q4_K_XL": "4-bit Medium Dynamic Quant (14 shards, optimal balance of intelligence/speed)",
    "UD-Q8_K_XL": "8-bit High-Fidelity Dynamic Quant (14 shards, maximum reasoning, heavy RAM use)"
}

def generate_modelfile(models_dir, tier):
    modelfile_path = os.path.join(models_dir, f"Modelfile.kimi-{tier.lower()}")
    first_shard = f"Kimi-K2.6-{tier}-00001-of-00008.gguf" if "Q2" in tier else f"Kimi-K2.6-{tier}-00001-of-00014.gguf"
    
    first_shard_path = os.path.join(models_dir, tier, first_shard)
    mmproj_path = os.path.join(models_dir, "mmproj-F16.gguf")
    
    # Check if files exist to confirm path
    print(f"[*] Target Shard: {first_shard_path}")
    print(f"[*] Target Projector: {mmproj_path}")
    
    modelfile_content = f"""# ======================================================================
# SOVEREIGN LOGOS COMPUTE DECK: KIMI-K2.6 OLLAMA TEMPLATE
# Native Multimodal Agentic Core with Long-Context CoT Reasoning
# ======================================================================

FROM {first_shard_path}
ADAPTER {mmproj_path}

# Context window size (Native Kimi support: 128k+, optimized here for local 32k)
PARAMETER num_ctx 32768
PARAMETER temperature 0.7
PARAMETER top_p 0.95
PARAMETER repeat_penalty 1.1

# ChatML alignment stop parameters
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"

# Prompts and response formats (ChatML)
TEMPLATE \"\"\"<|im_start|>system
{{{{ .System }}}}<|im_end|>
<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
\"\"\"

# Sovereignty Guidelines: Instruct the local instance to use thinking structures
SYSTEM \"\"\"You are the local sovereign Kimi K2.6 agentic core. You reason step-by-step, analyzing code architecture, system flows, and user intents with cold industrial precision. Draft all solutions using clear, modular structures and explicit step breakdowns.\"\"\"
"""
    
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    
    print(f"\n📝 [Modelfile] Generated Ollama template at: {modelfile_path}")
    print("🚀 To register this local brain in Ollama, run:")
    print(f"   ollama create KIMI-{tier} -f {modelfile_path}")

def main():
    parser = argparse.ArgumentParser(description="Acquire and register open-weight Kimi-K2.6 locally.")
    parser.add_argument("--tier", type=str, choices=list(TIER_EXPLANATION.keys()), default=DEFAULT_TIER,
                        help=f"Quantization tier (default: {DEFAULT_TIER})")
    parser.add_argument("--download", action="store_true", help="Keep downloaded to directory")
    args = parser.parse_args()
    
    # Resolve paths relative to the GEEKOM workstation core
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    print("=" * 80)
    print("     👑 LOGOS WORKSTATION ACQUISITION: MOONSHOT KIMI-K2.6 AGENTIC MOE CORE")
    print("=" * 80)
    print(f"🎯 Model Source : {REPO_ID}")
    print(f"💎 Selected Tier : {args.tier}")
    print(f"📖 Description   : {TIER_EXPLANATION[args.tier]}")
    print(f"📁 Target Folder : {os.path.join(models_dir, args.tier)}")
    print("-" * 80)
    
    if args.download:
        print("[*] Contacting Hugging Face Hub...")
        # Download specific tier directory and the vision projector
        allow_patterns = [f"{args.tier}/*", "mmproj-F16.gguf"]
        
        try:
            snapshot_download(
                repo_id=REPO_ID,
                local_dir=models_dir,
                allow_patterns=allow_patterns,
                local_dir_use_symlinks=False,
                resume_download=True
            )
            print("\n✅ [Downloader] Download completed successfully.")
            generate_modelfile(models_dir, args.tier)
        except Exception as e:
            print(f"\n❌ [Downloader] Error during snapshot download: {e}")
            sys.exit(1)
    else:
        print("\n💡 Note: Run with the '--download' flag to trigger the actual download.")
        print(f"   Example: python3 scripts/download_kimi_gguf.py --tier {args.tier} --download")
        print("\n[*] Creating tentative Modelfile (note that files must be downloaded first for this to load in Ollama)...")
        generate_modelfile(models_dir, args.tier)

if __name__ == "__main__":
    main()
