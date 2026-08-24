#!/usr/bin/env python3
"""
SAGE Local Music Composer: Paul & Hauser's Cascade Dirge
Author: Acutis / SAGE Core Plane / Logos OS
Generates a 'Far Over Misty Mountains Cold' style dirge about Paul and Hauser the dog
fighting the Three Queens fire in Washington state in the Cascade Mountains.
"""

import os
import sys
import wave

def generate_dirge():
    print("===========================================================")
    print("      🎹 SAGE LOCAL MUSIC COMPOSER (PAUL'S CASCADE DIRGE) 🎹")
    print("===========================================================")
    
    # 1. Check for PyTorch and device offloading (ROCm/CUDA vs CPU)
    try:
        import torch
        import numpy as np
    except ImportError:
        print("[-] Error: 'torch' (PyTorch) or 'numpy' is not installed.")
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
        sys.exit(1)
        
    # 3. Formulate the Poetic Prompt
    # We combine "Far Over Misty Mountains Cold" styles (haunting male choral chanting, solemn, deep, slow minor-key)
    # with the dramatic narrative of Paul and Hauser fighting the Three Queens wildfire in the Cascades.
    prompt = (
        "A low, haunting male-voice dirge, Far Over Misty Mountains Cold style, "
        "heavy solemn chanting, slow minor-key acoustic backing, dark and dramatic, "
        "epic fantasy sound, about Paul and Hauser the dog fighting the Three Queens wildfire in the Cascade Mountains"
    )
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
        
        # Normalize and clip float32 data to 16-bit PCM range [-32768, 32767]
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data_int16 = (audio_data * 32767.0).astype(np.int16)
        
        # Save output WAV file using Python's built-in wave module (No Scipy required!)
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(scripts_dir, "paul_cascade_dirge.wav")
        
        print(f"[*] Writing high-fidelity WAV file (PCM 16-bit) to: '{output_path}'...")
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)       # Mono channel
            wav_file.setsampwidth(2)       # 16-bit (2 bytes)
            wav_file.setframerate(sampling_rate)
            wav_file.writeframes(audio_data_int16.tobytes())
            
        print(f"✅ [SUCCESS] Paul's Cascade Dirge composed and saved successfully!")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        sys.exit(1)
        
    print("===========================================================")

if __name__ == "__main__":
    generate_dirge()
