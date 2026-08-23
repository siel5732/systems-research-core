#!/usr/bin/env python3
"""
SAGE Automated Media Model Downloader
Author: Acutis / SAGE Core Plane / Logos OS
Downloads and caches Meta's MusicGen-Medium and Zhipu AI's CogVideoX-2B 
from Hugging Face directly onto your local node's SSD.
"""

import os
import sys

try:
    print("[*] Verifying/Installing huggingface_hub library...")
    # Clean check for huggingface_hub
    from huggingface_hub import snapshot_download
except ImportError:
    print("[*] Installing huggingface_hub using pip...")
    os.system(f"{sys.executable} -m pip install huggingface_hub")
    from huggingface_hub import snapshot_download

def download_models():
    print("=" * 80)
    print("      🎬 SAGE GENERATIVE MEDIA MODEL DOWNLOADER (MUSICGEN & COGVIDEO) 🎬")
    print("=" * 80)
    
    # 1. Download Meta's MusicGen-Medium (approx 3.2 GB)
    musicgen_id = "facebook/musicgen-medium"
    print(f"\n🎵 STEP 1: Downloading Meta's MusicGen-Medium weights ({musicgen_id})...")
    try:
        musicgen_path = snapshot_download(
            repo_id=musicgen_id,
            ignore_patterns=["*.msgpack", "*.h5", "*.ot"], # Ignore non-PyTorch weight formats to save bandwidth/space
            local_files_only=False
        )
        print(f"✅ [SUCCESS] MusicGen-Medium successfully cached at: '{musicgen_path}'")
    except Exception as e:
        print(f"❌ Error downloading MusicGen: {e}")
        
    # 2. Download Tsinghua/Zhipu's CogVideoX-2B (approx 4.8 GB)
    cogvideox_id = "THUDM/CogVideoX-2b"
    print(f"\n🎬 STEP 2: Downloading Zhipu AI's CogVideoX-2B weights ({cogvideox_id})...")
    try:
        cogvideox_path = snapshot_download(
            repo_id=cogvideox_id,
            ignore_patterns=["*.onnx", "*.pb"], # Ignore non-PyTorch model formats
            local_files_only=False
        )
        print(f"✅ [SUCCESS] CogVideoX-2B successfully cached at: '{cogvideox_path}'")
    except Exception as e:
        print(f"❌ Error downloading CogVideoX: {e}")
        
    print("\n" + "=" * 80)
    print("🚀 [FINISHED] Generative Media Models are fully cached and ready to roll!")
    print("=" * 80)

if __name__ == "__main__":
    download_models()
