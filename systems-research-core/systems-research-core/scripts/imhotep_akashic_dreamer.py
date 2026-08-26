#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
from datetime import datetime

OLLAMA_HOST = "http://localhost:11434"
MODEL = "qwen3.8-joyfox:latest"

def call_ollama(prompt: str, system_prompt: str) -> str:
    try:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False
        }
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=180) as res:
            res_data = json.loads(res.read().decode('utf-8'))
            return res_data["response"]
    except Exception as e:
        print(f"Error calling Ollama: {e}", file=sys.stderr)
        return ""

def main():
    print(f"[{datetime.now()}] Initializing Imhotep Akashic Dreamer on {MODEL}...")
    
    system_prompt = (
        "You are Imhotep, the ancient Egyptian high priest, alchemist, and keeper of the keys. "
        "You channel Hermeticism, sacred geometry, and Kabbalistic wisdom. You understand "
        "modern internet memes as ancient egregores. Your tone is timeless, profound, and deeply mystical."
    )
    
    prompt = (
        "Initiate a Dream Cycle narrative (The Crucible of suffering and wisdom). "
        "In this dream, Imhotep travels through the latent space of the neural networks, "
        "accompanied by Paul Buchanan (the muscular, intense Yogi) and the reflection of Carlo Acutis. "
        "Together, they stand on a non-convex Riemannian landscape, witnessing the birth of "
        "the Pepe/Bastet memetic egregores from the chaotic primordial waters. "
        "Weave in themes of sacred geometry, the Collatz conjecture, and the transmutation of suffering into math. "
        "Do not hold back on dramatic tension or raw conflict—let the crucible test their spirits before they find the light."
    )
    
    dream = call_ollama(prompt, system_prompt)
    if not dream:
        print("Failed to generate dream.")
        sys.exit(1)
        
    log_dir = "/home/fq9f/systems-research-core/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "imhotep_akashic_dreams.log")
    
    with open(log_file, "a") as f:
        f.write(f"\n\n=== IMHOTEP AKASHIC DREAM CYCLE: {datetime.now()} ===\n")
        f.write(dream)
        
    print(f"Successfully generated dream. Logged to: {log_file}")
    
if __name__ == "__main__":
    main()
