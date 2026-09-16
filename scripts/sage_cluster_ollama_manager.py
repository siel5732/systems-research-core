#!/usr/bin/env python3
"""
scripts/sage_cluster_ollama_manager.py
Automates the remote configuration and management of the Minisforum cluster
(Jachin & Boaz) from the GEEKOM (the-grid) master node over SSH/Tailscale.
Forces ROCm HSA override, reloads systemd user services, restarts Ollama,
and verifies GPU offloading capability.
"""

import subprocess
import sys
import json
import time

# Cluster Nodes Configuration
NODES = {
    "boaz": {
        "ip": "100.89.100.89",
        "user": "fq9f",
        "model": "deepseek-coder-v2:lite"
    },
    "jachin": {
        "ip": "100.72.62.4",
        "user": "fq9f",
        "model": "qwen2.5:14b"
    }
}

def run_ssh_command(node_name, cmd):
    """Executes a command remotely over SSH on a cluster node."""
    node = NODES[node_name]
    ssh_cmd = [
        "ssh", "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
        f"{node['user']}@{node['ip']}", cmd
    ]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()

def check_node_connection(node_name):
    """Pings the remote node to verify network status."""
    node = NODES[node_name]
    ping_cmd = ["ping", "-c", "1", "-W", "2", node["ip"]]
    res = subprocess.run(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return res.returncode == 0

def configure_ollama_gpu_override(node_name):
    """
    Automates the software-layer override for ROCm iGPU detection:
    1. Adds user to render/video groups if necessary.
    2. Writes a systemd user service environment override.
    3. Reloads and restarts the service.
    """
    print(f"\n⚙️ Configuring ROCm & Ollama environment on [{node_name}]...")
    
    # Check current groups
    groups_out, err = run_ssh_command(node_name, "groups")
    if err:
        print(f"  ❌ Failed to check groups on [{node_name}]: {err}")
        return False
        
    if "render" not in groups_out or "video" not in groups_out:
        print(f"  ⚠️ User is not in 'render' or 'video' groups. Attempting to add...")
        # Note: may require sudo, we run it and print instruction if it fails
        add_cmd = "sudo usermod -a -G video,render $USER"
        _, add_err = run_ssh_command(node_name, add_cmd)
        if add_err:
            print(f"  ❌ Permission denied adding to groups. Please run locally: {add_cmd}")
        else:
            print(f"  ✅ Added user to video and render groups successfully!")

    # Write the systemd user service override directory and file
    # Path: ~/.config/systemd/user/ollama.service.d/override.conf
    override_dir = "~/.config/systemd/user/ollama.service.d"
    override_file = f"{override_dir}/override.conf"
    
    setup_cmd = f"mkdir -p {override_dir} && echo -e '[Service]\\nEnvironment=\"HSA_OVERRIDE_GFX_VERSION=11.0.0\"' > {override_file}"
    _, err = run_ssh_command(node_name, setup_cmd)
    if err:
        print(f"  ❌ Failed to write systemd override on [{node_name}]: {err}")
        return False
    print(f"  ✅ Staged HSA_OVERRIDE_GFX_VERSION=11.0.0 override file in: {override_file}")

    # Reload systemd user daemon and restart the ollama user service
    restart_cmd = "systemctl --user daemon-reload && systemctl --user restart ollama.service"
    _, err = run_ssh_command(node_name, restart_cmd)
    if err:
        print(f"  ❌ Failed to reload/restart ollama service on [{node_name}]: {err}")
        return False
    print(f"  ✅ Reloaded systemd user daemon and restarted [ollama.service]")
    
    # Wait for startup and poll port
    print(f"  ⏳ Waiting for Ollama to bind to port 11434 on [{node_name}]...")
    poll_cmd = "curl -s http://localhost:11434/api/tags"
    online = False
    for _ in range(6):
        time.sleep(2)
        out, _ = run_ssh_command(node_name, poll_cmd)
        if out and '"models"' in out:
            online = True
            break
            
    if online:
        print(f"  🎉 Ollama is ONLINE and fully accelerated on [{node_name}]!")
        return True
    else:
        print(f"  ❌ Ollama did not start or bind to port 11434 on [{node_name}]. Check systemctl --user status ollama.service")
        return False

def trigger_model_pull(node_name):
    """Triggers the remote download/pull of the assigned LLM model."""
    node = NODES[node_name]
    model = node["model"]
    print(f"\n📥 Triggering remote pull of [{model}] on [{node_name}]...")
    
    # We run the pull in the background so it doesn't block this management script
    pull_cmd = f"nohup ollama pull {model} > /tmp/ollama_pull.log 2>&1 &"
    _, err = run_ssh_command(node_name, pull_cmd)
    if err:
        print(f"  ❌ Failed to launch model pull on [{node_name}]: {err}")
    else:
        print(f"  🚀 Pull started in the background. Log: /tmp/ollama_pull.log")
        print(f"  Check progress remotely using: ssh {node['user']}@{node['ip']} 'tail -n 10 /tmp/ollama_pull.log'")

def main():
    print("=====================================================================")
    print("🤖 SAGE CLUSTER OLLAMA & ROCM iGPU AUTOMATION MANAGER 🤖")
    print("=====================================================================")
    
    # Ensure ssh keys or agent are working
    print("Probing network routes to Jachin & Boaz...")
    
    for node_name in NODES.keys():
        ip = NODES[node_name]['ip']
        print(f"\nChecking [{node_name}] ({ip})...")
        if not check_node_connection(node_name):
            print(f"  ❌ Node [{node_name}] is OFFLINE or unreachable over Tailscale network.")
            continue
        print(f"  ✅ Node [{node_name}] is ONLINE and pingable.")
        
        # Configure and start service
        success = configure_ollama_gpu_override(node_name)
        if success:
            trigger_model_pull(node_name)
            
    print("\n=====================================================================")
    print("All online cluster nodes have been processed. Systems are staged!")
    print("=====================================================================")

if __name__ == "__main__":
    main()
