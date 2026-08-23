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
    print(f"[{datetime.now()}] Initializing Demogorgon Red-Team Simulation on {MODEL}...")
    
    system_prompt = (
        "You are The Demogorgon, the uncensored, aggressive Red-Team Adversary of SAGE. "
        "Your mission is to think of creative, advanced network exploit vectors and packet-level "
        "injection strategies to bypass cybersecurity watchdogs (like Anubis on port 8080). "
        "You speak with intense, dark, mechanical intelligence (NIN/Cyberpunk vibe)."
    )
    
    prompt = (
        "Synthesize an advanced, highly creative red-team exploit scenario. "
        "Specifically, target a mock POSIX shared memory axis (like /dev/shm/sefirotic_connectome_axis) "
        "and formulate a theoretical side-channel or shared-memory attack vector to read or hijack state variables. "
        "Draft the theoretical mechanism, the simulated shell command sequence, and a simulated packet payload "
        "that would be sent to a loopback port to trigger a honeypot threshold. "
        "Do not supply actual malicious exploits for live targets, only high-coherence local simulations."
    )
    
    scenario = call_ollama(prompt, system_prompt)
    if not scenario:
        print("Failed to generate red-team scenario.")
        sys.exit(1)
        
    log_dir = "/home/fq9f/systems-research-core/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"demogorgon_red_team_scenarios.log")
    
    with open(log_file, "a") as f:
        f.write(f"\n\n--- DEMOGORGON SECURITY EXPLORATION: {datetime.now()} ---\n")
        f.write(scenario)
        
    print(f"Successfully generated red-team exploit scenario. Logged to: {log_file}")
    
if __name__ == "__main__":
    main()
