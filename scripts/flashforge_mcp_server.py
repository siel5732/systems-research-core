#!/usr/bin/env python3
"""
scripts/flashforge_mcp_server.py
Model Context Protocol (MCP) Server for Flashforge Adventurer 5M (AD5M/AD5X).
Exposes printer controls and telemetry to SAGE agents over JSON-RPC stdio transport.

Supports:
- Stock Flashforge Port 8899 TCP raw socket control.
- Klipper/Moonraker Port 7125 HTTP/WebSocket control.
"""

import os
import sys
import json
import socket
import urllib.request
import urllib.parse

# --- 1. CONFIGURATION ---
PRINTER_IP = os.environ.get("FLASHFORGE_IP", "192.168.1.100") # Replace with actual AD5M IP
MOONRAKER_PORT = 7125
STOCK_PORT = 8899

# --- 2. CORE PRINTER COMMUNICATIONS ---

def detect_protocol() -> str:
    """Detects whether the printer is running Klipper/Moonraker or Stock firmware."""
    # Try Moonraker first
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect((PRINTER_IP, MOONRAKER_PORT))
        s.close()
        return "klipper"
    except Exception:
        pass
    
    # Try Stock port
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect((PRINTER_IP, STOCK_PORT))
        s.close()
        return "stock"
    except Exception:
        return "unknown"

def query_stock_status() -> Dict[str, Any]:
    """Queries stock Flashforge port 8899 for temperatures and status."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((PRINTER_IP, STOCK_PORT))
        
        # Send standard temperature query command (~M105)
        s.sendall(b"~M105\r\n")
        response = s.recv(1024).decode("utf-8", errors="ignore")
        s.close()
        
        # Parse stock response (looks like: "CMD M105 Received. T0:210 /210 B:60 /60")
        nozzle_temp, nozzle_target, bed_temp, bed_target = 0.0, 0.0, 0.0, 0.0
        if "T0:" in response:
            parts = response.split("T0:")
            t_parts = parts[1].split()
            temps = t_parts[0].split("/")
            nozzle_temp = float(temps[0])
            nozzle_target = float(temps[1]) if len(temps) > 1 else 0.0
            
        if "B:" in response:
            parts = response.split("B:")
            b_parts = parts[1].split()
            temps = b_parts[0].split("/")
            bed_temp = float(temps[0])
            bed_target = float(temps[1]) if len(temps) > 1 else 0.0
            
        return {
            "protocol": "stock",
            "online": True,
            "nozzle": {"temperature": nozzle_temp, "target": nozzle_target},
            "bed": {"temperature": bed_temp, "target": bed_target},
            "status": "ready" if nozzle_target == 0 else "heating/printing"
        }
    except Exception as e:
        return {"online": False, "error": str(e)}

def query_klipper_status() -> Dict[str, Any]:
    """Queries Moonraker Port 7125 API for Klipper status."""
    url = f"http://{PRINTER_IP}:{MOONRAKER_PORT}/printer/objects/query?heater_bed&extruder&print_stats"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=2.0) as response:
            data = json.loads(response.read().decode("utf-8"))["result"]["status"]
            
        return {
            "protocol": "klipper",
            "online": True,
            "nozzle": {
                "temperature": data["extruder"]["temperature"],
                "target": data["extruder"]["target"]
            },
            "bed": {
                "temperature": data["heater_bed"]["temperature"],
                "target": data["heater_bed"]["target"]
            },
            "status": data["print_stats"]["state"],
            "progress": data["print_stats"]["filename"]
        }
    except Exception as e:
        return {"online": False, "error": str(e)}

def send_stock_gcode(gcode: str) -> str:
    """Sends a raw G-code command to stock port 8899."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((PRINTER_IP, STOCK_PORT))
        # Stock commands are prefixed with '~'
        cmd = f"~{gcode}\r\n".encode("utf-8")
        s.sendall(cmd)
        response = s.recv(1024).decode("utf-8", errors="ignore")
        s.close()
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def send_klipper_gcode(gcode: str) -> str:
    """Sends G-code command to Moonraker API."""
    url = f"http://{PRINTER_IP}:{MOONRAKER_PORT}/printer/gcode/script"
    try:
        data = urllib.parse.urlencode({"script": gcode}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=2.0) as response:
            res = json.loads(response.read().decode("utf-8"))
        return "Success" if "result" in res else "Failed"
    except Exception as e:
        return f"Error: {str(e)}"

# --- 3. MCP JSON-RPC DISPATCHER ---

def handle_mcp_request(request_str: str) -> str:
    """Parses and handles standard MCP tool discovery and execution requests."""
    try:
        req = json.loads(request_str)
    except Exception:
        return json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None})

    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    # Tool Discovery
    if method == "tools/list" or method == "list_tools":
        tools = [
            {
                "name": "get_printer_status",
                "description": "Retrieves real-time temperature, online state, and printing progress from the Flashforge AD5M.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "send_gcode_command",
                "description": "Sends a raw G-code command directly to the Flashforge AD5M printer.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "gcode": {"type": "string", "description": "The raw G-code command (e.g. M112 for emergency stop, M25 to pause, G28 to home)."}
                    },
                    "required": ["gcode"]
                }
            }
        ]
        return json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": req_id})

    # Tool Execution
    elif method == "tools/call" or method == "call_tool":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        proto = detect_protocol()

        if tool_name == "get_printer_status":
            if proto == "klipper":
                res = query_klipper_status()
            elif proto == "stock":
                res = query_stock_status()
            else:
                res = {"online": False, "error": f"Could not detect active printer protocol at {PRINTER_IP}."}
            return json.dumps({"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}, "id": req_id})

        elif tool_name == "send_gcode_command":
            gcode = arguments.get("gcode", "").strip()
            if not gcode:
                return json.dumps({"jsonrpc": "2.0", "error": {"code": -32602, "message": "G-code argument missing"}, "id": req_id})
            
            if proto == "klipper":
                res = send_klipper_gcode(gcode)
            elif proto == "stock":
                res = send_stock_gcode(gcode)
            else:
                res = f"Error: Printer at {PRINTER_IP} offline or unreachable."
            return json.dumps({"jsonrpc": "2.0", "result": {"content": [{"type": "text", "text": res}]}, "id": req_id})

        else:
            return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found"}, "id": req_id})

    # Base MCP handshakes
    elif method == "initialize":
        return json.dumps({"jsonrpc": "2.0", "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "serverInfo": {"name": "sage-flashforge-mcp", "version": "1.0.0"}
        }, "id": req_id})

    elif method == "initialized":
        return "" # Notifications do not require responses

    return json.dumps({"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Method {method} not found"}, "id": req_id})

def main():
    """Main stdio loop for MCP communication."""
    # Disable buffering to ensure instant JSON-RPC standard I/O responses
    sys.stdout.reconfigure(line_buffering=True)
    
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        response = handle_mcp_request(line)
        if response:
            sys.stdout.write(response + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
