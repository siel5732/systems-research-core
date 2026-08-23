#!/usr/bin/env python3
"""
=====================================================================================
👑 LOGOS OPERATING SYSTEM: REAL-TIME COGNITIVE JANITOR (SAGE-JIT)
=====================================================================================
Copyright (c) 2026 Zach Sielaff. All Rights Reserved.
Integrates staged logs from preconscious_buffer.md directly into MEMORY.md on-demand
or based on event-driven session completions, bypassing static cron timing.
=====================================================================================
"""

import os
import sys
import re
from datetime import datetime

def main():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    buffer_path = os.path.join(workspace_dir, "preconscious_buffer.md")
    memory_path = os.path.join(workspace_dir, "MEMORY.md")
    
    print("=" * 80)
    print("      🌌 LOGOS OPERATING SYSTEM: SAGE-JIT EPISTEMIC COMPACTOR")
    print("=" * 80)
    
    if not os.path.exists(buffer_path):
        print("[-] Error: preconscious_buffer.md not found.")
        sys.exit(1)
        
    buffer_content = open(buffer_path).read()
    
    # Extract logs
    queue_match = re.search(r"## Staged Learning Logs \(Queue\)(.*)", buffer_content, re.DOTALL)
    if not queue_match:
        print("[-] Error: No active queue found in preconscious buffer.")
        sys.exit(1)
        
    queue_text = queue_match.group(1).strip()
    
    # Clean up placeholders
    if "Empty - All logs consolidated" in queue_text or not queue_text:
        print("[*] Preconscious buffer queue is currently empty. No compaction required.")
        print("=" * 80)
        return
        
    logs = [line.strip() for line in queue_text.split("\n") if line.strip() and line.strip().startswith("-")]
    
    if not logs:
        print("[*] No active staged logs found to consolidate.")
        print("=" * 80)
        return
        
    print(f"[*] Found {len(logs)} staged learning logs to integrate:")
    for log in logs:
        print(f"  {log}")
    print("-" * 80)
    
    # Generate timestamped entry
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
    entry = f"\n### 🌌 Epistemic Consolidation Ledger — {timestamp}\n"
    for log in logs:
        entry += f"{log}\n"
        
    # Read MEMORY.md
    if not os.path.exists(memory_path):
        print("[-] Error: MEMORY.md not found.")
        sys.exit(1)
        
    memory_content = open(memory_path).read()
    
    # Check if Ledger section exists, if not, create it
    ledger_heading = "## Epistemic Ledger (Real-Time Consolidations)"
    
    if ledger_heading not in memory_content:
        # Create section before Future Roadmap or at the end
        if "### 5. Future Roadmap" in memory_content:
            memory_content = memory_content.replace("### 5. Future Roadmap", f"{ledger_heading}\n\n### 5. Future Roadmap")
        else:
            memory_content += f"\n\n{ledger_heading}\n"
            
    # Insert entry directly under the ledger heading
    target_pattern = rf"({re.escape(ledger_heading)})"
    memory_content = re.sub(target_pattern, r"\1" + entry, memory_content, count=1)
    
    # Save MEMORY.md
    with open(memory_path, "w") as f:
        f.write(memory_content)
        
    # Clear queue in preconscious_buffer.md
    new_buffer = re.sub(
        r"## Staged Learning Logs \(Queue\).*?$",
        "## Staged Learning Logs (Queue)\n(Empty - All logs consolidated to MEMORY.md)",
        buffer_content,
        flags=re.DOTALL
    )
    with open(buffer_path, "w") as f:
        f.write(new_buffer)
        
    print("✅ [SUCCESS] Event-driven memory compaction completed successfully!")
    print("🚀 MEMORY.md is now synchronized with real-time learnings.")
    print("=" * 80)

if __name__ == "__main__":
    main()
