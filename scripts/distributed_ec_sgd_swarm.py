#!/usr/bin/env python3
"""
SAGE Distributed Over-the-Air (OTA) EC-SGD Swarm Node
Author: Acutis / SAGE Core Plane / Logos OS
Phase 3: Real-world physical cluster coordinate-descent script over Tailscale SDN.
Can be executed on GEEKOM (the-grid), Jachin, and Boaz to run a live P2P optimization loop.
"""

import sys
import os
import json
import socket
import time
import threading
import math
import numpy as np

# Node Configuration (Local Homelab Mapping)
NODES_MAP = {
    "the-grid": "127.0.0.1",       # GEEKOM core
    "jachin": "192.168.1.12",      # Minisforum Node 1
    "boaz": "192.168.1.8"          # Minisforum Node 2
}

PORT = 18890 # Port for SAGE EC-SGD P2P consensus
DIM = 128    # 128-dimensional Hilbert parameter space

class DistributedECSGDNode:
    def __init__(self, node_name, peer_names):
        self.node_name = node_name
        self.peers = peer_names
        self.ip = NODES_MAP.get(node_name, "127.0.0.1")
        
        # Local parameter copy θ_i
        np.random.seed(42) # Start synchronized
        self.theta = np.random.randn(DIM) * 2.0
        self.theta_star = np.random.randn(DIM)
        self.theta_star /= np.linalg.norm(self.theta_star)
        
        self.eta = 0.05
        self.lock = threading.Lock()
        self.step = 0
        self.running = True
        
        # Buffer to collect peer parameters during active steps
        self.received_parameters = {}

    def get_local_grad(self, theta):
        """∇f_i(θ) = θ - θ* + spatial_heterogeneity_bias"""
        global_grad = theta - self.theta_star
        # Deterministic spatial bias per node to simulate heterogeneous datasets
        np.random.seed(hash(self.node_name) % 4294967295)
        bias = np.random.randn(DIM)
        bias /= np.linalg.norm(bias)
        bias *= 0.25 # σ_het = 0.25
        
        # Stochastic temporal noise
        noise = np.random.randn(DIM) * 0.1 # σ = 0.1
        return global_grad + bias + noise

    def start_server(self):
        """Listen for incoming parameter packets from active peers."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind(("0.0.0.0", PORT))
            server.listen(5)
            print(f"📡 [{self.node_name}] SAGE P2P Server listening on port {PORT}...")
        except Exception as e:
            print(f"❌ [{self.node_name}] Failed to bind server on port {PORT}: {e}")
            return
            
        while self.running:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self.handle_peer, args=(conn,), daemon=True).start()
            except Exception:
                break

    def handle_peer(self, conn):
        """Process incoming state vector from an active peer."""
        try:
            data = conn.recv(65536).decode('utf-8')
            if not data:
                return
            payload = json.loads(data)
            sender = payload.get("sender")
            theta_peer = np.array(payload.get("theta"))
            step = payload.get("step")
            
            with self.lock:
                if step == self.step:
                    self.received_parameters[sender] = theta_peer
        except Exception as e:
            pass
        finally:
            conn.close()

    def broadcast_state(self, step):
        """Broadcasts current parameter vector to all peers over TCP."""
        payload = {
            "sender": self.node_name,
            "theta": self.theta.tolist(),
            "step": step
        }
        message = json.dumps(payload)
        
        for peer in self.peers:
            peer_ip = NODES_MAP.get(peer)
            if not peer_ip:
                continue
            # Non-blocking connection attempt to simulate random delays / erasures
            threading.Thread(target=self.send_to_peer, args=(peer_ip, message), daemon=True).start()

    def send_to_peer(self, ip, message):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(1.5) # Strict latency threshold. Delays > 1.5s are heralded erasures!
            client.connect((ip, PORT))
            client.sendall(message.encode('utf-8'))
            client.close()
        except Exception:
            # Failed connection represents a network erasure (E_t)
            pass

    def run_consensus_step(self):
        """Executes a single step of the Erasure-Coherent SGD consensus."""
        with self.lock:
            current_step = self.step
            # 1. Compute local gradient
            grad = self.get_local_grad(self.theta)
            
            # 2. Broadcast local state to peers
            self.broadcast_state(current_step)
            
        # Wait for peers to respond (simulates communication round)
        time.sleep(2.0)
        
        with self.lock:
            # 3. Identify Active Set A_t (Self + Peers who completed the handshake)
            active_peers = list(self.received_parameters.keys())
            active_set = [self.node_name] + active_peers
            k = len(active_set)
            
            # 4. Apply Consensus Recovery Map R = Π_A ∘ P_A
            # Reconstruct the consensus manifold by averaging over all active nodes
            active_thetas = [self.theta] + [self.received_parameters[p] for p in active_peers]
            active_mean = np.mean(active_thetas, axis=0)
            
            # Erased coordinates are set to the recovered consensus mean
            self.theta = active_mean.copy()
            
            # 5. Compute active gradients and update
            # Step size η_t = η / sqrt(t + 1)
            eta_t = self.eta / math.sqrt(current_step + 1)
            self.theta -= eta_t * grad
            
            # Clear buffer for the next round
            self.received_parameters.clear()
            self.step += 1
            
            # Print SAGE telemetry metric
            obj = 0.5 * np.dot(self.theta - self.theta_star, self.theta - self.theta_star)
            print(f"⚙️ [{self.node_name}] Step {current_step:03d} | Active Peers: {k}/{len(self.peers)+1} | Loss f(θ): {obj:.6f}")

    def start(self):
        # Run server thread
        threading.Thread(target=self.start_server, daemon=True).start()
        time.sleep(1)
        
        print(f"🚀 SAGE OTA Distributed EC-SGD Node [{self.node_name}] Starting Swarm Optimization...")
        try:
            for _ in range(50): # Run 50 steps
                self.run_consensus_step()
        except KeyboardInterrupt:
            print("\nStopping SAGE Node...")
        finally:
            self.running = False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 distributed_ec_sgd_swarm.py <node_name>")
        print("Available nodes: the-grid, jachin, boaz")
        sys.exit(1)
        
    node = sys.argv[1]
    if node not in NODES_MAP:
        print(f"Error: Unknown node '{node}'")
        sys.exit(1)
        
    peers = [name for name in NODES_MAP.keys() if name != node]
    node_runner = DistributedECSGDNode(node, peers)
    node_runner.start()
