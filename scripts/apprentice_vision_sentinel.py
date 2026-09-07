#!/usr/bin/env python3
"""
apprentice_vision_sentinel.py
=============================
AcutisForge Closed-Loop Vision Sentinel for Flashforge AD5M

Principal Computer Vision / Robotics daemon for Logos OS / SAGE swarm.

Responsibilities
----------------
1. Parse a .gcode.3mf package → extract per-layer geometry (bounding boxes +
   approximate cross-section polylines) from Metadata/plate_1.gcode.
2. Continuously capture frames from /dev/video0.
3. At each estimated layer change (or on motion trigger) perform lightweight
   OpenCV edge/contour analysis and compute a normalized Deviation Index D_i.
4. If D_i > CRITICAL_THRESHOLD, issue a pause via the local Flashforge MCP
   server (JSON-RPC tools/call → send_gcode_command) and write a high-priority
   alert into preconscious_buffer/print_emergency.json for the SAGE agents.

Author  : Logos OS Principal CV/Robotics Engineer
License : Proprietary – Logos OS internal
"""

from __future__ import annotations

import argparse
import json
import logging
import logging.handlers
import os
import re
import signal
import sys
import time
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ---------------------------------------------------------------------------
# Configuration (override via CLI or environment)
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    # Paths
    "gcode_3mf": "cristo-redentor_PLA_2h42m.gcode.3mf",
    "video_device": "/dev/video0",
    "emergency_json": "preconscious_buffer/print_emergency.json",
    "log_file": "logs/apprentice_vision_sentinel.log",

    # MCP server
    "mcp_url": "http://127.0.0.1:8765/mcp",  # adjust to your server
    "mcp_timeout_s": 4.0,
    "pause_gcode": "M25",  # or "PAUSE" on Klipper/Moonraker

    # Vision / geometry
    "critical_threshold": 0.35,  # D_i trigger
    "frame_width": 1280,
    "frame_height": 720,
    "blur_ksize": 5,
    "canny_low": 50,
    "canny_high": 150,
    "min_contour_area": 800,  # px² – ignore noise

    # Camera-to-bed calibration (rough defaults – refine with checkerboard)
    # Maps bed mm coordinates → image pixels (affine approximation)
    "bed_origin_px": (640, 600),  # image (x,y) of bed (0,0)
    "mm_to_px_x": 4.2,  # pixels per mm in X
    "mm_to_px_y": -4.2,  # negative because image Y down
    "roi_margin_px": 40,  # expand expected bbox for search

    # Timing / triggering
    "layer_poll_interval_s": 1.5,  # how often we check for layer change
    "motion_trigger_threshold": 12.0,  # mean absolute difference for motion
    "max_fps": 8,  # soft limit on analysis rate

    # Safety
    "dry_run": False,  # if True, never send pause
    "max_consecutive_failures": 8,
}

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class LayerGeometry:
    """Expected geometry for a single layer."""
    layer_idx: int
    z_height: float
    bbox_mm: Tuple[float, float, float, float]  # (xmin, ymin, xmax, ymax)
    # Optional polyline approximation of the outer contour (list of (x,y) mm)
    outline_mm: List[Tuple[float, float]] = field(default_factory=list)
    # Approximate time (s) from start of print when this layer begins
    estimated_time_s: float = 0.0


@dataclass
class DeviationResult:
    layer_idx: int
    z_height: float
    deviation_index: float
    expected_bbox_px: Tuple[int, int, int, int]
    observed_bbox_px: Optional[Tuple[int, int, int, int]]
    timestamp: float
    reason: str = ""


# ---------------------------------------------------------------------------
# G-code / 3MF parser
# ---------------------------------------------------------------------------

class GCodeLayerParser:
    """
    Extract per-layer bounding boxes from a Bambu/Orca-style .gcode.3mf.

    Strategy
    --------
    - Unzip the 3MF and read Metadata/plate_1.gcode (or plate_N.gcode).
    - Detect layer changes via:
      * ;LAYER_CHANGE (Orca / Bambu)
      * ;LAYER:N
      * significant Z move with extrusion (G1 Z… E…)
    - Accumulate extruded XY moves inside each layer → axis-aligned bbox.
    - Optionally keep a simplified outer outline for future contour matching.
    """

    LAYER_CHANGE_RE = re.compile(
        r";\s*(?:LAYER_CHANGE|LAYER\s*[:=]\s*(\d+)|CHANGE\s+LAYER)",
        re.IGNORECASE,
    )
    Z_MOVE_RE = re.compile(
        r"G[01]\s+.*?\bZ([-+]?\d*\.?\d+)",
        re.IGNORECASE,
    )
    XY_MOVE_RE = re.compile(
        r"G[01]\s+(?:.*?\bX([-+]?\d*\.?\d+))?.*?\bY([-+]?\d*\.?\d+).*?(?:\bE([-+]?\d*\.?\d+))?",
        re.IGNORECASE,
    )
    TIME_RE = re.compile(r";\s*(?:TIME_ELAPSED|estimated printing time)\s*[:=]?\s*([\d.]+)", re.I)

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.layers: List[LayerGeometry] = []
        self.total_estimated_time_s: float = 0.0

    def parse(self) -> List[LayerGeometry]:
        if not self.path.exists():
            raise FileNotFoundError(f"3MF/G-code not found: {self.path}")

        gcode_text = self._extract_gcode()
        return self._parse_gcode(gcode_text)

    def _extract_gcode(self) -> str:
        """Unzip 3MF and return the first plate_*.gcode content."""
        if self.path.suffix.lower() == ".gcode":
            return self.path.read_text(encoding="utf-8", errors="ignore")

        with zipfile.ZipFile(self.path, "r") as zf:
            candidates = [
                n for n in zf.namelist()
                if n.startswith("Metadata/plate_") and n.endswith(".gcode")
            ]
            if not candidates:
                # Fallback for older / different slicers
                candidates = [n for n in zf.namelist() if n.endswith(".gcode")]
                if not candidates:
                    raise ValueError("No plate_*.gcode found inside 3MF")
            # Prefer plate_1
            preferred = sorted(candidates, key=lambda x: (0 if "plate_1" in x else 1, x))[0]
            logging.info("Extracting G-code from %s", preferred)
            return zf.read(preferred).decode("utf-8", errors="ignore")

    def _parse_gcode(self, text: str) -> List[LayerGeometry]:
        layers: List[LayerGeometry] = []
        current_z = 0.0
        current_layer_idx = -1
        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        outline: List[Tuple[float, float]] = []
        last_x = last_y = 0.0
        time_accum = 0.0

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("; TYPE:"):
                continue

            # Time estimation (best-effort)
            m_time = self.TIME_RE.search(line)
            if m_time:
                try:
                    time_accum = float(m_time.group(1))
                except ValueError:
                    pass

            # Layer change markers
            if self.LAYER_CHANGE_RE.search(line):
                if current_layer_idx >= 0 and xmin < float("inf"):
                    layers.append(LayerGeometry(
                        layer_idx=current_layer_idx,
                        z_height=current_z,
                        bbox_mm=(xmin, ymin, xmax, ymax),
                        outline_mm=outline.copy(),
                        estimated_time_s=time_accum,
                    ))
                current_layer_idx += 1
                xmin = ymin = float("inf")
                xmax = ymax = float("-inf")
                outline.clear()
                continue

            # Z height
            m_z = self.Z_MOVE_RE.search(line)
            if m_z:
                try:
                    new_z = float(m_z.group(1))
                    if abs(new_z - current_z) > 0.01 and current_layer_idx >= 0:
                        # implicit layer change on significant Z jump
                        if xmin < float("inf"):
                            layers.append(LayerGeometry(
                                layer_idx=current_layer_idx,
                                z_height=current_z,
                                bbox_mm=(xmin, ymin, xmax, ymax),
                                outline_mm=outline.copy(),
                                estimated_time_s=time_accum,
                            ))
                        current_layer_idx += 1
                        xmin = ymin = float("inf")
                        xmax = ymax = float("-inf")
                        outline.clear()
                    current_z = new_z
                except ValueError:
                    pass

            # Extruded XY moves → geometry
            m_xy = self.XY_MOVE_RE.search(line)
            if m_xy and "E" in line.upper():  # only when extruding
                try:
                    x = float(m_xy.group(1)) if m_xy.group(1) else last_x
                    y = float(m_xy.group(2)) if m_xy.group(2) else last_y
                    last_x, last_y = x, y
                    xmin = min(xmin, x)
                    ymin = min(ymin, y)
                    xmax = max(xmax, x)
                    ymax = max(ymax, y)
                    # Keep a coarse outline (every Nth point to limit memory)
                    if len(outline) % 8 == 0:
                        outline.append((x, y))
                except (ValueError, TypeError):
                    pass

        # Final layer
        if current_layer_idx >= 0 and xmin < float("inf"):
            layers.append(LayerGeometry(
                layer_idx=current_layer_idx,
                z_height=current_z,
                bbox_mm=(xmin, ymin, xmax, ymax),
                outline_mm=outline,
                estimated_time_s=time_accum,
            ))

        self.layers = layers
        self.total_estimated_time_s = time_accum
        logging.info("Parsed %d layers from G-code (est. total time %.0fs)",
                     len(layers), time_accum)
        return layers

    def layer_at_time(self, t_s: float) -> Optional[LayerGeometry]:
        """Best-effort lookup of the layer that should be printing at time t."""
        if not self.layers:
            return None
        for i, lyr in enumerate(self.layers):
            if i + 1 < len(self.layers):
                if lyr.estimated_time_s <= t_s < self.layers[i + 1].estimated_time_s:
                    return lyr
            else:
                return lyr
        return self.layers[-1]


# ---------------------------------------------------------------------------
# Vision analysis
# ---------------------------------------------------------------------------

class VisionAnalyzer:
    """Lightweight real-time contour extraction + Deviation Index."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.prev_gray: Optional[np.ndarray] = None

    def mm_to_px(self, x_mm: float, y_mm: float) -> Tuple[int, int]:
        ox, oy = self.cfg["bed_origin_px"]
        sx = self.cfg["mm_to_px_x"]
        sy = self.cfg["mm_to_px_y"]
        return int(ox + x_mm * sx), int(oy + y_mm * sy)

    def expected_bbox_px(self, geom: LayerGeometry) -> Tuple[int, int, int, int]:
        xmin, ymin, xmax, ymax = geom.bbox_mm
        x0, y0 = self.mm_to_px(xmin, ymin)
        x1, y1 = self.mm_to_px(xmax, ymax)
        # Normalize ordering (image Y may be inverted)
        return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))

    def extract_print_contour(self, frame: np.ndarray,
                              search_roi: Optional[Tuple[int, int, int, int]] = None
                              ) -> Optional[np.ndarray]:
        """Gaussian → Canny → largest external contour inside ROI.
        Returns the contour in full-frame coordinates or None.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (self.cfg["blur_ksize"], self.cfg["blur_ksize"]), 0)
        edges = cv2.Canny(blurred, self.cfg["canny_low"], self.cfg["canny_high"])

        if search_roi is not None:
            x0, y0, x1, y1 = search_roi
            mask = np.zeros_like(edges)
            mask[y0:y1, x0:x1] = edges[y0:y1, x0:x1]
            edges = mask

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Keep only reasonably large contours
        candidates = [c for c in contours if cv2.contourArea(c) >= self.cfg["min_contour_area"]]
        if not candidates:
            return None

        # Largest contour is assumed to be the active print object
        return max(candidates, key=cv2.contourArea)

    def compute_deviation(self, frame: np.ndarray, geom: LayerGeometry) -> DeviationResult:
        """
        Normalized Deviation Index D_i ∈ [0, 1+].

        Components (weighted):
        • Area ratio difference
        • Bounding-box IoU (1 – IoU)
        • Centroid displacement normalized by expected size
        """
        exp_bbox = self.expected_bbox_px(geom)
        margin = self.cfg["roi_margin_px"]
        h, w = frame.shape[:2]
        roi = (
            max(0, exp_bbox[0] - margin),
            max(0, exp_bbox[1] - margin),
            min(w, exp_bbox[2] + margin),
            min(h, exp_bbox[3] + margin),
        )

        contour = self.extract_print_contour(frame, search_roi=roi)
        if contour is None:
            return DeviationResult(
                layer_idx=geom.layer_idx,
                z_height=geom.z_height,
                deviation_index=1.0,  # complete miss
                expected_bbox_px=exp_bbox,
                observed_bbox_px=None,
                timestamp=time.time(),
                reason="no_contour",
            )

        x, y, bw, bh = cv2.boundingRect(contour)
        obs_bbox = (x, y, x + bw, y + bh)

        # --- metrics ---
        # 1. Bounding-box IoU
        inter_x0 = max(exp_bbox[0], obs_bbox[0])
        inter_y0 = max(exp_bbox[1], obs_bbox[1])
        inter_x1 = min(exp_bbox[2], obs_bbox[2])
        inter_y1 = min(exp_bbox[3], obs_bbox[3])
        inter_area = max(0, inter_x1 - inter_x0) * max(0, inter_y1 - inter_y0)
        exp_area = max(1, (exp_bbox[2] - exp_bbox[0]) * (exp_bbox[3] - exp_bbox[1]))
        obs_area = max(1, bw * bh)
        union = exp_area + obs_area - inter_area
        iou = inter_area / union if union > 0 else 0.0
        iou_term = 1.0 - iou

        # 2. Area ratio
        area_ratio = abs(obs_area - exp_area) / exp_area
        area_term = min(1.0, area_ratio)

        # 3. Centroid shift
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
        else:
            cx, cy = x + bw / 2, y + bh / 2
        exp_cx = (exp_bbox[0] + exp_bbox[2]) / 2
        exp_cy = (exp_bbox[1] + exp_bbox[3]) / 2
        diag = max(1.0, np.hypot(exp_bbox[2] - exp_bbox[0], exp_bbox[3] - exp_bbox[1]))
        centroid_term = min(1.0, np.hypot(cx - exp_cx, cy - exp_cy) / diag)

        # Weighted combination
        di = 0.45 * iou_term + 0.30 * area_term + 0.25 * centroid_term
        di = float(np.clip(di, 0.0, 2.0))

        return DeviationResult(
            layer_idx=geom.layer_idx,
            z_height=geom.z_height,
            deviation_index=di,
            expected_bbox_px=exp_bbox,
            observed_bbox_px=obs_bbox,
            timestamp=time.time(),
            reason="ok",
        )

    def motion_detected(self, frame: np.ndarray) -> bool:
        """Simple frame-difference motion trigger."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        if self.prev_gray is None:
            self.prev_gray = gray
            return False
        diff = cv2.absdiff(self.prev_gray, gray)
        self.prev_gray = gray
        score = float(np.mean(diff))
        return score > self.cfg["motion_trigger_threshold"]


# ---------------------------------------------------------------------------
# MCP client (JSON-RPC)
# ---------------------------------------------------------------------------

class FlashforgeMCPClient:
    """Minimal JSON-RPC client for the custom Flashforge MCP server."""

    def __init__(self, url: str, timeout: float = 4.0):
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=2, backoff_factor=0.3, status_forcelist=[502, 503, 504])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self._id = 0

    def _rpc(self, method: str, params: dict | None = None) -> dict:
        self._id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": method,
            "params": params or {},
        }
        try:
            r = self.session.post(self.url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(f"MCP error: {data['error']}")
            return data.get("result", {})
        except Exception as exc:
            logging.error("MCP RPC failed (%s): %s", method, exc)
            raise

    def send_gcode(self, gcode: str) -> dict:
        """Call tools/call → send_gcode_command."""
        try:
            return self._rpc("tools/call", {
                "name": "send_gcode_command",
                "arguments": {"command": gcode},
            })
        except Exception:
            return self._rpc("send_gcode_command", {"command": gcode})

    def get_status(self) -> dict:
        try:
            return self._rpc("tools/call", {
                "name": "get_printer_status",
                "arguments": {},
            })
        except Exception:
            return self._rpc("get_printer_status", {})


# ---------------------------------------------------------------------------
# Emergency logger
# ---------------------------------------------------------------------------

def write_emergency_alert(path: str | Path, result: DeviationResult, extra: dict | None = None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    alert = {
        "severity": "critical",
        "source": "apprentice_vision_sentinel",
        "timestamp": result.timestamp,
        "layer": result.layer_idx,
        "z_height": result.z_height,
        "deviation_index": result.deviation_index,
        "expected_bbox_px": result.expected_bbox_px,
        "observed_bbox_px": result.observed_bbox_px,
        "reason": result.reason,
        "extra": extra or {},
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(alert, indent=2), encoding="utf-8")
    tmp.replace(path)
    logging.critical("Emergency alert written → %s (D_i=%.3f layer=%d)",
                     path, result.deviation_index, result.layer_idx)


# ---------------------------------------------------------------------------
# Main daemon
# ---------------------------------------------------------------------------

class VisionSentinelDaemon:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.parser = GCodeLayerParser(cfg["gcode_3mf"])
        self.layers = self.parser.parse()
        if not self.layers:
            raise RuntimeError("No layers extracted from G-code – aborting")

        self.analyzer = VisionAnalyzer(cfg)
        self.mcp = FlashforgeMCPClient(cfg["mcp_url"], cfg["mcp_timeout_s"])
        self.running = True
        self.print_start_time: Optional[float] = None
        self.current_layer_idx = -1
        self.consecutive_failures = 0
        self.last_analysis_t = 0.0

        # Open camera
        self.cap = cv2.VideoCapture(cfg["video_device"])
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open video device {cfg['video_device']}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg["frame_width"])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg["frame_height"])
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        logging.info("Camera opened: %s (%dx%d)", cfg["video_device"],
                     int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                     int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, signum, frame):
        logging.info("Shutdown signal received (%s)", signum)
        self.running = False

    def _estimate_current_layer(self) -> Optional[LayerGeometry]:
        if self.print_start_time is None:
            self.print_start_time = time.time()
            return self.layers[0] if self.layers else None
        elapsed = time.time() - self.print_start_time
        return self.parser.layer_at_time(elapsed)

    def _should_analyze(self, frame: np.ndarray, geom: LayerGeometry) -> bool:
        now = time.time()
        if now - self.last_analysis_t < 1.0 / self.cfg["max_fps"]:
            return False
        if geom.layer_idx != self.current_layer_idx:
            return True
        if self.analyzer.motion_detected(frame):
            return True
        return False

    def run(self):
        logging.info("Vision Sentinel daemon started – monitoring %d layers", len(self.layers))
        logging.info("Critical threshold D_i = %.2f | pause cmd = %s",
                     self.cfg["critical_threshold"], self.cfg["pause_gcode"])

        while self.running:
            try:
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.consecutive_failures += 1
                    logging.warning("Frame grab failed (%d consecutive)", self.consecutive_failures)
                    if self.consecutive_failures >= self.cfg["max_consecutive_failures"]:
                        logging.error("Too many consecutive frame failures – exiting")
                        break
                    time.sleep(0.5)
                    continue
                self.consecutive_failures = 0

                geom = self._estimate_current_layer()
                if geom is None:
                    time.sleep(self.cfg["layer_poll_interval_s"])
                    continue

                if not self._should_analyze(frame, geom):
                    time.sleep(0.05)
                    continue

                self.last_analysis_t = time.time()
                self.current_layer_idx = geom.layer_idx

                result = self.analyzer.compute_deviation(frame, geom)
                logging.info(
                    "Layer %d (Z=%.2f) D_i=%.3f reason=%s",
                    result.layer_idx, result.z_height,
                    result.deviation_index, result.reason,
                )

                if result.deviation_index > self.cfg["critical_threshold"]:
                    logging.critical(
                        "CRITICAL DEVIATION (%.3f > %.2f) – initiating emergency pause",
                        result.deviation_index, self.cfg["critical_threshold"],
                    )
                    write_emergency_alert(
                        self.cfg["emergency_json"],
                        result,
                        extra={"pause_gcode": self.cfg["pause_gcode"]},
                    )
                    if not self.cfg["dry_run"]:
                        try:
                            self.mcp.send_gcode(self.cfg["pause_gcode"])
                            logging.critical("Pause command '%s' sent via MCP", self.cfg["pause_gcode"])
                        except Exception as e:
                            logging.error("Failed to send pause: %s", e)
                    else:
                        logging.warning("DRY-RUN: would have sent pause command")
                    time.sleep(5.0)

            except Exception as exc:
                logging.exception("Unhandled error in main loop: %s", exc)
                time.sleep(1.0)

        self.cap.release()
        logging.info("Vision Sentinel daemon stopped cleanly")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def setup_logging(log_file: str):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    root.addHandler(ch)
    fh = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8"
    )
    fh.setFormatter(fmt)
    root.addHandler(fh)


def parse_args():
    p = argparse.ArgumentParser(description="AcutisForge Vision Sentinel daemon")
    p.add_argument("--gcode", default=DEFAULT_CONFIG["gcode_3mf"],
                    help="Path to .gcode.3mf or .gcode")
    p.add_argument("--device", default=DEFAULT_CONFIG["video_device"])
    p.add_argument("--mcp-url", default=DEFAULT_CONFIG["mcp_url"])
    p.add_argument("--threshold", type=float, default=DEFAULT_CONFIG["critical_threshold"])
    p.add_argument("--pause-cmd", default=DEFAULT_CONFIG["pause_gcode"])
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--log", default=DEFAULT_CONFIG["log_file"])
    return p.parse_args()


def main():
    args = parse_args()
    cfg = DEFAULT_CONFIG.copy()
    cfg.update({
        "gcode_3mf": args.gcode,
        "video_device": args.device,
        "mcp_url": args.mcp_url,
        "critical_threshold": args.threshold,
        "pause_gcode": args.pause_cmd,
        "dry_run": args.dry_run,
        "log_file": args.log,
    })

    setup_logging(cfg["log_file"])
    logging.info("Starting AcutisForge Vision Sentinel")
    logging.info("Config: %s", {k: v for k, v in cfg.items() if k != "log_file"})

    try:
        daemon = VisionSentinelDaemon(cfg)
        daemon.run()
    except Exception as e:
        logging.critical("Fatal error: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
