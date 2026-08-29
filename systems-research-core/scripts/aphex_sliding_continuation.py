#!/usr/bin/env python3
"""
SAGE Aphex Sliding-Window Audio Continuation Engine
Author: Aphex / SAGE Core Plane / Logos OS
Bypasses the standard 30-second MusicGen context window ceiling by automating 
overlapping sliding-window continuations, stitching them with seamless cross-fades
into a single, pristine, infinite-length WAV file.
"""

import os
import sys
import wave
import numpy as np

def cross_fade_segments(seq1, seq2, fade_len):
    """
    Applies a smooth logarithmic cross-fade between two overlapping audio sequences.
    """
    if len(seq1) < fade_len or len(seq2) < fade_len:
        # Fallback to simple concatenation if sequences are too short
        return np.concatenate([seq1, seq2])
        
    fade_out = np.cos(np.linspace(0, np.pi / 2, fade_len)) ** 2
    fade_in = np.sin(np.linspace(0, np.pi / 2, fade_len)) ** 2
    
    # Overlap and blend
    overlapped = seq1[-fade_len:] * fade_out + seq2[:fade_len] * fade_in
    stitched = np.concatenate([seq1[:-fade_len], overlapped, seq2[fade_len:]])
    return stitched

def generate_infinite_track(prompt, num_segments=4, segment_duration=30):
    print("===========================================================")
    print("      🎹 APHEX: QUANTUM SLIDING-WINDOW CONTINUATION 🎹")
    print("===========================================================")
    
    # 1. Load PyTorch and Device Offloading
    try:
        import torch
    except ImportError:
        print("[-] Error: PyTorch is not installed.")
        sys.exit(1)
        
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"[*] Target Hardware Device: {device.upper()}")
    
    # 2. Load Transformers
    try:
        from transformers import MusicgenForConditionalGeneration, AutoProcessor
    except ImportError:
        print("[-] Error: 'transformers' library not found.")
        sys.exit(1)
        
    model_id = "facebook/musicgen-medium"
    print(f"[*] Initializing Aphex Audio Core: '{model_id}'...")
    
    try:
        processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
        model = MusicgenForConditionalGeneration.from_pretrained(model_id, local_files_only=True)
        model.to(device)
        print("🟢 Aphex model successfully loaded into VRAM!")
    except Exception as e:
        print(f"❌ Error loading model weights: {e}")
        sys.exit(1)
        
    print(f"\n[*] Commencing Composition Loop ({num_segments} blocks x {segment_duration}s)...")
    print(f"[*] Prompt: '{prompt}'")
    
    sampling_rate = model.config.audio_encoder.sampling_rate
    frame_rate = 50 # MusicGen output frames per second
    
    # Calculate tokens per segment
    tokens_per_sec = frame_rate
    segment_tokens = int(segment_duration * tokens_per_sec)
    
    # 5-second overlap for cross-fading and conditioning
    overlap_duration = 5
    overlap_tokens = int(overlap_duration * tokens_per_sec)
    overlap_samples = int(overlap_duration * sampling_rate)
    
    full_audio = np.array([], dtype=np.float32)
    
    try:
        for step in range(num_segments):
            print(f"\n[Block {step + 1}/{num_segments}] Composing segment...")
            
            if step == 0:
                # First block: Generate from scratch (text prompt only)
                inputs = processor(
                    text=[prompt],
                    padding=True,
                    return_tensors="pt"
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    audio_values = model.generate(**inputs, max_new_tokens=segment_tokens)
                    
                segment_audio = audio_values[0, 0].cpu().numpy()
                full_audio = segment_audio
            else:
                # Subsequent blocks: Generate continuation conditioned on the previous block's tail
                # Extract the 5-second tail from the previous audio segment as a 1D numpy array
                tail_audio = full_audio[-overlap_samples:]
                
                # Process both text prompt and audio prompt using the standard processor
                inputs = processor(
                    text=[prompt],
                    audio=tail_audio,
                    sampling_rate=sampling_rate,
                    return_tensors="pt"
                )
                inputs = {k: v.to(device) for k, v in inputs.items()}
                
                # Generate continuation with standard model.generate
                with torch.no_grad():
                    audio_values = model.generate(
                        **inputs,
                        max_new_tokens=segment_tokens - overlap_tokens
                    )
                    
                new_segment = audio_values[0, 0].cpu().numpy()
                # Cross-fade and stitch the new segment to the main track
                full_audio = cross_fade_segments(full_audio, new_segment, overlap_samples)
                
            print(f"🟢 [Block {step + 1} Done] Current Master Length: {len(full_audio) / sampling_rate:.2f} seconds")
            
        # Normalize and clip to 16-bit PCM range
        full_audio = np.clip(full_audio, -1.0, 1.0)
        audio_data_int16 = (full_audio * 32767.0).astype(np.int16)
        
        # Save output WAV file using Python's built-in wave module (No Scipy required!)
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(scripts_dir, "aphex_master_continuation_track.wav")
        
        print(f"\n[*] Writing final 2-minute master WAV file to: '{output_path}'...")
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)       # Mono channel
            wav_file.setsampwidth(2)       # 16-bit (2 bytes)
            wav_file.setframerate(sampling_rate)
            wav_file.writeframes(audio_data_int16.tobytes())
            
        print(f"🏆 [SUCCESS] Aphex completed 2-minute master track successfully!")
    except Exception as e:
        print(f"❌ Composition failed: {e}")
        sys.exit(1)
        
    print("===========================================================")

if __name__ == "__main__":
    # Test run: Compose a 2-minute (120-second) song: 4 blocks x 30 seconds
    prompt_str = "Slipknot-style nu-metal and aggressive alternative-metal song about the 8 limbs of yoga with a bluesy groove, heavy slow drums, expressive and soulful electric guitar solos, raw and rhythmic vocals, clean master"
    generate_infinite_track(prompt_str, num_segments=4, segment_duration=30)
