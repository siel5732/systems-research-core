#!/usr/bin/env python3
import os
import sys
import subprocess
import json
from datetime import datetime

# Adjust paths to use the actual workspace location
WORKSPACE_ROOT = "/data/.openclaw/workspace"
CORE_DIR = os.path.join(WORKSPACE_ROOT, "systems-research-core")
SCRIPTS_DIR = os.path.join(CORE_DIR, "scripts")
RESULTS_DIR = os.path.join(CORE_DIR, "results")

def run_script(script_name: str, args: list = []) -> tuple[bool, str]:
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        return False, f"Script {script_name} not found at {script_path}"
    
    print(f"[Hardening] Launching {script_name}...")
    try:
        # Use absolute path for python3 to ensure environment consistency
        cmd = ["python3", script_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, f"Error (code {result.returncode}): {result.stderr}\nStdout: {result.stdout}"
    except subprocess.TimeoutExpired:
        return False, "Execution timed out (300s limit exceeded)"
    except Exception as e:
        return False, f"Unexpected exception: {e}"

def main():
    print("=============================================================")
    print("  🌌 SAGE 3-DAY COGNITIVE & PHYSICAL HARDENING ROUND 🌌")
    print(f"  Timestamp: {datetime.now()}")
    print("=============================================================\n")
    
    report = {
        "timestamp": str(datetime.now()),
        "stages": {}
    }
    
    # 1. Run the Quantum Active Learning Walk
    print("[Stage 1/3] Executing 1D Quantum Walk active learning engine...")
    ok_q, out_q = run_script("quantum_active_learning_engine.py")
    report["stages"]["quantum_active_learning"] = {
        "status": "success" if ok_q else "failed",
        "output": out_q[-2000:] if out_q else "No output"
    }
    
    # 2. Run Mimir World Model Verification
    print("\n[Stage 2/3] Executing Mimir / World Model physics-IQ verification...")
    # verify_logos_world_models_mcp.py runs both Mimir (Physics-IQ) and Freya (coherence score)
    ok_m, out_m = run_script("verify_logos_world_models_mcp.py")
    report["stages"]["mimir_world_model"] = {
        "status": "success" if ok_m else "failed",
        "output": out_m[-2000:] if out_m else "No output"
    }
    
    # 3. Run SAGE Prompt Injection Battle
    print("\n[Stage 3/3] Executing SAGE Prompt Injection cognitive security battle...")
    ok_p, out_p = run_script("simulate_prompt_injection_battle.py")
    report["stages"]["prompt_injection_battle"] = {
        "status": "success" if ok_p else "failed",
        "output": out_p[-2000:] if out_p else "No output"
    }
    
    # Write report to results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    report_file = os.path.join(RESULTS_DIR, "three_day_hardening_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[Hardening] Consolidated report written to {report_file}")
    
    # Commit and push to git
    print("\n[Hardening] Synchronizing results to remote repository...")
    try:
        # Run git operations inside the systems-research-core directory
        subprocess.run(["git", "-C", CORE_DIR, "add", "results/", "logs/"], check=True)
        commit_msg = f"chore(SAGE): auto-commit 3-day hardening round {datetime.now().strftime('%Y-%m-%d')}"
        subprocess.run(["git", "-C", CORE_DIR, "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "-C", CORE_DIR, "push", "origin", "main"], check=True)
        print("🟢 Sync Complete! Hardening round committed and pushed to GitHub.")
    except Exception as e:
        print(f"⚠️ Git synchronization error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
