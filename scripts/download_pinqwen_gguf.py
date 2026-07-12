#!/usr/bin/env python3
import os
import sys
import argparse
import urllib.request
import time

# ======================================================================
# SOVEREIGN LOGOS KERNEL: PINQWEN MODEL ACQUISITION UTILITY
# Downloads and registers the Blackfrost-AI PINQWEN-3.6 MoE GGUF model.
# ======================================================================

REPO_ID = "mradermacher/PINQWEN-3.6-35B-CLEAN-BF16-i1-GGUF"
DEFAULT_QUANT = "IQ3_M"

QUANT_MAPPING = {
    "IQ3_M": "PINQWEN-3.6-35B-CLEAN-BF16.i1-IQ3_M.gguf",
    "Q3_K_M": "PINQWEN-3.6-35B-CLEAN-BF16.i1-Q3_K_M.gguf",
    "Q4_K_M": "PINQWEN-3.6-35B-CLEAN-BF16.i1-Q4_K_M.gguf"
}

def format_bytes(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

def download_file(url, output_path):
    print(f"📡 [Downloader] Fetching from: {url}")
    print(f"📂 [Downloader] Saving to: {output_path}")
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req) as response:
            total_size = int(response.info().get('Content-Length', 0))
            bytes_downloaded = 0
            start_time = time.time()
            
            with open(output_path, 'wb') as f:
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    
                    # Calculate speed & ETA
                    elapsed = time.time() - start_time
                    speed = bytes_downloaded / elapsed if elapsed > 0 else 0
                    eta = (total_size - bytes_downloaded) / speed if speed > 0 else 0
                    
                    # Progress bar
                    percent = (bytes_downloaded / total_size) * 100 if total_size > 0 else 0
                    bar = '#' * int(percent // 4) + '-' * (25 - int(percent // 4))
                    
                    sys.stdout.write(
                        f"\r   [{bar}] {percent:.1f}% | "
                        f"{format_bytes(bytes_downloaded)}/{format_bytes(total_size)} | "
                        f"{format_bytes(speed)}/s | ETA: {eta:.0f}s"
                    )
                    sys.stdout.flush()
            print("\n✅ [Downloader] Download completed successfully.")
    except Exception as e:
        print(f"\n❌ [Downloader] Error occurred during download: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        sys.exit(1)

def write_modelfile(gguf_filename, models_dir):
    modelfile_path = os.path.join(models_dir, "Modelfile")
    gguf_path = os.path.join(models_dir, gguf_filename)
    
    modelfile_content = f"""# ======================================================================
# SOVEREIGN LOGOS COMPUTE DECK: PINQWEN-3.6 OLLAMA TEMPLATE
# Optimized for Distilled Reasoning and Agentic XML Tool Calls
# ======================================================================

FROM {gguf_path}

# Context window size (Native Qwen MoE context: 262,144, but we map 32k for RAM)
PARAMETER num_ctx 32768
PARAMETER temperature 0.2
PARAMETER top_p 0.95
PARAMETER repeat_penalty 1.1

# Stop sequences for ChatML-style dialogue boundaries
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|im_start|>"

# Prompts and response formats
TEMPLATE \"\"\"<|im_start|>system
{{{{ .System }}}}<|im_end|>
<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
<|im_process|>\"\"\"

# Sovereignty Guidelines: Instruct the local instance to use thinking structures
SYSTEM \"\"\"You are the local sovereign compute node core. You reason step-by-step, wrapping your internal chain-of-thought within <think>...</think> XML blocks before emitting your definitive action or synthesis. Execute all commands with cold industrial precision.\"\"\"
"""
    
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    print(f"📝 [Modelfile] Generated Ollama template at: {modelfile_path}")
    print("\n🚀 To register this local brain in Ollama, run:")
    print(f"   ollama create PINQWEN -f {modelfile_path}")

def main():
    parser = argparse.ArgumentParser(description="Acquire and register PINQWEN MoE model locally.")
    parser.add_argument("--quant", type=str, choices=list(QUANT_MAPPING.keys()), default=DEFAULT_QUANT,
                        help=f"Quantization tier (default: {DEFAULT_QUANT})")
    parser.add_argument("--download", action="store_true", help="Initiate the actual large model download")
    args = parser.parse_args()
    
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    filename = QUANT_MAPPING[args.quant]
    output_path = os.path.join(models_dir, filename)
    url = f"https://huggingface.co/{REPO_ID}/resolve/main/{filename}"
    
    print("=" * 80)
    print("     👑 LOGOS WORKSTATION ACQUISITION: BLACKFROST PINQWEN-3.6 MOE ENGINE")
    print("=" * 80)
    print(f"🎯 Model Target: {REPO_ID}")
    print(f"💎 Selected Quant: {args.quant} ({filename})")
    print(f"📁 Workspace Target: {output_path}")
    print("-" * 80)
    
    write_modelfile(filename, models_dir)
    
    if args.download:
        download_file(url, output_path)
    else:
        print("\n💡 Note: Run with the '--download' flag to trigger the actual download.")
        print("   Example: python3 scripts/download_pinqwen_gguf.py --download")

if __name__ == "__main__":
    main()
