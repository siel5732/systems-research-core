#!/usr/bin/env python3
"""
SAGE Local Music Composer (MusicGen-Medium)
Author: Acutis / SAGE Core Plane / Logos OS
Loads pre-cached facebook/musicgen-medium weights from local cache
and generates a custom Tron/NIN-inspired industrial-techno track.
"""

import os
import sys
import scipy.io.wavfile

def generate_music():
    print("===========================================================")
    print("      🎹 SAGE LOCAL MUSIC COMPOSER (MUSICGEN-MEDIUM) 🎹")
    print("===========================================================")
    
    # 1. Check for PyTorch and device offloading (ROCm/CUDA vs CPU)
    try:
        import torch
    except ImportError:
        print("[-] Error: 'torch' (PyTorch) is not installed in this environment.")
        sys.exit(1)
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Target Hardware Device: {device.upper()}")
    
    # 2. Check for transformers
    try:
        from transformers import MusicgenForConditionalGeneration, AutoProcessor
    except ImportError:
        print("[-] Error: 'transformers' library not found.")
        sys.exit(1)
        
    model_id = "facebook/musicgen-medium"
    print(f"[*] Loading pre-cached weights for '{model_id}'...")
    
    try:
        processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
        model = MusicgenForConditionalGeneration.from_pretrained(model_id, local_files_only=True)
        model.to(device)
        print("🟢 Model and processor successfully loaded into memory!")
    except Exception as e:
        print(f"❌ Error loading model from local cache: {e}")
        print("⚠️ Ensure the downloader script has fully completed Step 1 on this machine.")
        sys.exit(1)
        
    # 3. Formulate Prompt
    prompt = "A gritty industrial-techno track, heavy Nine Inch Nails bassline, Tron synthwave synthesizers, slow dark electronic beat, powerful and clean master"
    print(f"\n[*] Composition Prompt: '{prompt}'")
    print("[*] Generating audio (this will compose ~15 seconds of stereo music)...")
    
    # 4. Generate Audio Tensor
    try:
        inputs = processor(
            text=[prompt],
            padding=True,
            return_tensors="pt"
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # max_new_tokens=768 corresponds to exactly 15.0 seconds of audio at 32kHz
        with torch.no_grad():
            audio_values = model.generate(**inputs, max_new_tokens=768)
            
        sampling_rate = model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()
        
        # Save output WAV file
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(scripts_dir, "sage_generated_track.wav")
        
        print(f"[*] Writing high-fidelity WAV file to: '{output_path}'...")
        scipy.io.wavfile.write(output_path, rate=sampling_rate, data=audio_data)
        print(f"✅ [SUCCESS] Local music track composed and saved successfully!")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)
        
    print("===========================================================")

if __name__ == "__main__":
    generate_music()
