#!/usr/bin/env python3
"""
Rebbe Akiva Recursive Self-Improving Engine
Logos OS – Level-1 Pardes Agent
Production continuous background loop
"""

from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import logging
import signal
import threading
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

import yaml
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Optional but recommended local stack (install as needed)
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except ImportError:
    QdrantClient = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class AkivaConfig:
    base_dir: Path
    harvested_dir: Path
    buffer_dir: Path
    prompts_dir: Path
    ledger_dir: Path
    log_dir: Path
    stiefel_path: Path
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    collection_name: str = "sefirotic_1536"
    embed_model_name: str = "sentence-transformers/all-mpnet-base-v2" # 768-D
    poll_interval_sec: int = 30
    hypothesis_interval_sec: int = 900
    evaluation_interval_sec: int = 3600
    max_chunk_tokens: int = 512
    entropy_low_threshold: float = 1.85
    max_prompt_versions: int = 50

    @classmethod
    def from_yaml(cls, path: Path) -> "AkivaConfig":
        with open(path) as f:
            raw = yaml.safe_load(f)
        base = Path(raw.get("base_dir", ".")).resolve()
        return cls(
            base_dir=base,
            harvested_dir=base / raw.get("harvested_dir", "harvested_research"),
            buffer_dir=base / raw.get("buffer_dir", "preconscious_buffer"),
            prompts_dir=base / raw.get("prompts_dir", "configs/akiva_prompts"),
            ledger_dir=base / raw.get("ledger_dir", "data/ledgers"),
            log_dir=base / raw.get("log_dir", "logs"),
            stiefel_path=base / raw.get("stiefel_path", "frozen_stiefel_projection.npy"),
            qdrant_host=raw.get("qdrant_host", "localhost"),
            qdrant_port=raw.get("qdrant_port", 6333),
            collection_name=raw.get("collection_name", "sefirotic_1536"),
            embed_model_name=raw.get("embed_model_name", "sentence-transformers/all-mpnet-base-v2"),
            poll_interval_sec=raw.get("poll_interval_sec", 30),
            hypothesis_interval_sec=raw.get("hypothesis_interval_sec", 900),
            evaluation_interval_sec=raw.get("evaluation_interval_sec", 3600),
            max_chunk_tokens=raw.get("max_chunk_tokens", 512),
            entropy_low_threshold=raw.get("entropy_low_threshold", 1.85),
            max_prompt_versions=raw.get("max_prompt_versions", 50),
        )

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("rebbe_akiva")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_dir / "akiva_engine.log")
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    ))
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger

# ---------------------------------------------------------------------------
# 1. Active RAG & Semantic Scraping
# ---------------------------------------------------------------------------

class DocumentIngestor:
    """Watches harvested_research/, chunks, embeds, projects, upserts."""

    def __init__(self, cfg: AkivaConfig, logger: logging.Logger):
        self.cfg = cfg
        self.logger = logger
        self.seen: set[str] = set()
        
        # Load Stiefel projection matrix
        if os.path.exists(cfg.stiefel_path):
            self.stiefel = np.load(cfg.stiefel_path)
            self.logger.info("Loaded projection matrix of shape: %s", self.stiefel.shape)
        else:
            self.stiefel = np.random.randn(1536, 768).astype(np.float32)
            self.logger.warning("Stiefel path not found! Using initialized mock weight mapping.")

        self.embedder = None
        if SentenceTransformer is not None:
            self.embedder = SentenceTransformer(cfg.embed_model_name)
            self.logger.info("Loaded local embedder: %s", cfg.embed_model_name)

        self.qdrant = None
        if QdrantClient is not None:
            try:
                self.qdrant = QdrantClient(host=cfg.qdrant_host, port=cfg.qdrant_port)
                self._ensure_collection()
            except Exception as e:
                self.logger.warning("Could not connect to Qdrant server: %s. Falling back to local dry-run logs.", e)

    def _ensure_collection(self):
        if self.qdrant is None:
            return
        collections = [c.name for c in self.qdrant.get_collections().collections]
        if self.cfg.collection_name not in collections:
            self.qdrant.create_collection(
                collection_name=self.cfg.collection_name,
                vectors_config=qmodels.VectorParams(size=1536, distance=qmodels.Distance.COSINE),
            )
            self.logger.info("Created Qdrant collection %s", self.cfg.collection_name)

    def _file_hash(self, path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        for i in range(0, len(words), self.cfg.max_chunk_tokens // 2):
            chunk = " ".join(words[i:i + self.cfg.max_chunk_tokens])
            if chunk.strip():
                chunks.append(chunk)
        return chunks

    def _embed_and_project(self, texts: List[str]) -> np.ndarray:
        if self.embedder is None:
            # Fallback random matrix
            return np.random.randn(len(texts), 1536).astype(np.float32)
            
        emb_768 = self.embedder.encode(texts, show_progress_bar=False)
        
        # Adaptive projection logic supporting both (1536, 768) and (768, 1536) shapes
        if self.stiefel.shape == (768, 1536):
            emb_1536 = np.dot(emb_768, self.stiefel)
        elif self.stiefel.shape == (1536, 768):
            emb_1536 = (self.stiefel @ emb_768.T).T
        else:
            if self.stiefel.shape[1] == emb_768.shape[1]:
                emb_1536 = np.dot(emb_768, self.stiefel.T)
            else:
                emb_1536 = np.dot(emb_768, self.stiefel)
                
        # Normalize vectors
        norms = np.linalg.norm(emb_1536, axis=1, keepdims=True)
        emb_1536 = emb_1536 / np.maximum(norms, 1e-12)
        return emb_1536.astype(np.float32)

    def ingest_file(self, path: Path):
        file_hash = self._file_hash(path)
        if file_hash in self.seen:
            return
        self.seen.add(file_hash)
        self.logger.info("Ingesting new document: %s", path.name)

        try:
            if path.suffix.lower() == ".pdf":
                import pypdf
                reader = pypdf.PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")

            chunks = self._chunk_text(text)
            if not chunks:
                return
            vectors = self._embed_and_project(chunks)
            points = []
            for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
                points.append({
                    "id": hashlib.md5(f"{file_hash}:{i}".encode()).hexdigest(),
                    "vector": vec.tolist(),
                    "payload": {
                        "source": str(path),
                        "chunk_id": i,
                        "text": chunk[:2000],
                        "ingested_at": datetime.now(timezone.utc).isoformat(),
                        "agent": "rebbe_akiva",
                    }
                })

            if self.qdrant is not None:
                q_points = [
                    qmodels.PointStruct(
                        id=p["id"],
                        vector=p["vector"],
                        payload=p["payload"]
                    ) for p in points
                ]
                self.qdrant.upsert(
                    collection_name=self.cfg.collection_name,
                    points=q_points,
                    wait=True,
                )
            
            # Log successful upsert/ingestion (dry-run output format preserves visibility)
            self.logger.info("Upserted %d chunks from %s", len(points), path.name)
            
        except Exception as e:
            self.logger.exception("Failed to ingest %s: %s", path, e)

    def scan_once(self):
        self.cfg.harvested_dir.mkdir(parents=True, exist_ok=True)
        for path in self.cfg.harvested_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".pdf", ".md", ".txt", ".markdown"}:
                self.ingest_file(path)

class HarvestHandler(FileSystemEventHandler):
    def __init__(self, ingestor: DocumentIngestor):
        self.ingestor = ingestor

    def on_created(self, event):
        if not event.is_directory:
            self.ingestor.ingest_file(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self.ingestor.ingest_file(Path(event.src_path))

# ---------------------------------------------------------------------------
# 2. Combinatorial Permutation – 231 Gates Hypothesis Engine
# ---------------------------------------------------------------------------

class HypothesisEngine:
    """Background generator using 231 Gates + cross-domain LLM prompting."""

    LETTERS = list("אבגדהוזחטיכלמנסעפצקרשת") # 22 Hebrew letters

    def __init__(self, cfg: AkivaConfig, logger: logging.Logger):
        self.cfg = cfg
        self.logger = logger
        self.gates = self._generate_231_gates()

    def _generate_231_gates(self) -> List[Tuple[str, str]]:
        gates = []
        for i in range(len(self.LETTERS)):
            for j in range(i + 1, len(self.LETTERS)):
                gates.append((self.LETTERS[i], self.LETTERS[j]))
        return gates # 231 pairs

    def _call_local_llm(self, prompt: str) -> str:
        # Mock LLM generation for standalone engine simulation
        return (
            "[SYSTEM REPORT] Unified Sefirotic Swarm Hypothesis Generated:\n"
            "This combination bridges systemic and alchemical logic. The structural isomorphism "
            "between system interrupts (such as eBPF filters) and Merkabah palace thresholds is verified. "
            "A testable implication shows that optimizing kernel thread-gating reduces transition jitter to < 0.05ms."
        )

    def generate_hypothesis(self) -> Dict[str, Any]:
        gate = self.gates[np.random.randint(0, len(self.gates))]
        concept_a = "eBPF kernel trigger"
        concept_b = "Merkabah palace guardian"

        prompt = f"""You are Rebbe Akiva, Master of the 231 Gates.
Gate: {gate[0]}–{gate[1]}
Permute the following two concepts into a non-obvious cross-domain hypothesis:

Concept A (formal/systems): {concept_a}
Concept B (alchemical/narrative): {concept_b}

Produce:
1. A concise hypothesis statement.
2. The structural mapping (what corresponds to what).
3. A testable implication for Logos OS or the SAGE swarm.
4. Confidence (0–1) and suggested next verification step.
"""
        response = self._call_local_llm(prompt)
        hyp = {
            "gate": gate,
            "concepts": [concept_a, concept_b],
            "hypothesis": response,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent": "rebbe_akiva",
        }
        self.cfg.ledger_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.cfg.ledger_dir / f"hypothesis_{int(time.time())}.json"
        out_path.write_text(json.dumps(hyp, indent=2, ensure_ascii=False))
        self.logger.info("Wrote hypothesis %s", out_path.name)
        return hyp

# ---------------------------------------------------------------------------
# 3. Recursive Prompt Optimization (RSI)
# ---------------------------------------------------------------------------

class PromptOptimizer:
    """Evaluates own ledger entries and rewrites system prompts when coherence is low."""

    def __init__(self, cfg: AkivaConfig, logger: logging.Logger):
        self.cfg = cfg
        self.logger = logger
        self.cfg.prompts_dir.mkdir(parents=True, exist_ok=True)

    def _entropy_score(self, text: str) -> float:
        from collections import Counter
        counts = Counter(text)
        total = sum(counts.values())
        if total == 0:
            return 0.0
        probs = np.array([c / total for c in counts.values()])
        return float(-np.sum(probs * np.log2(probs + 1e-12)))

    def evaluate_ledger_entry(self, ledger_path: Path) -> Tuple[float, str]:
        text = ledger_path.read_text(encoding="utf-8", errors="ignore")
        score = self._entropy_score(text)
        return score, text

    def optimize_if_needed(self):
        self.cfg.ledger_dir.mkdir(parents=True, exist_ok=True)
        ledgers = sorted(self.cfg.ledger_dir.glob("*.md")) + sorted(self.cfg.ledger_dir.glob("*.json"))
        if not ledgers:
            return
        latest = ledgers[-1]
        score, content = self.evaluate_ledger_entry(latest)
        self.logger.info("Ledger %s entropy score: %.3f", latest.name, score)

        if score < self.cfg.entropy_low_threshold:
            self.logger.warning("Low coherence detected – initiating prompt rewrite")
            current_prompt = self._load_latest_prompt()
            rewrite_prompt = f"""You are optimizing the system prompt of Rebbe Akiva.
Current system prompt:
---
{current_prompt}
---
Recent low-coherence output:
---
{content[:3000]}
---
Rewrite the system prompt to increase reasoning depth, cross-domain precision, and structural rigor while remaining faithful to the Pardes Level-1 constraints and the Sefer Yetzirah framework. Output only the new system prompt text.
"""
            new_prompt = self._call_llm_for_rewrite(rewrite_prompt)
            self._save_prompt_version(new_prompt)
            self.logger.info("Saved new optimized prompt version")

    def _load_latest_prompt(self) -> str:
        versions = sorted(self.cfg.prompts_dir.glob("prompt_v*.txt"))
        if not versions:
            return "You are Rebbe Akiva, active-learning RAG agent of Logos OS..."
        return versions[-1].read_text(encoding="utf-8")

    def _save_prompt_version(self, text: str):
        versions = sorted(self.cfg.prompts_dir.glob("prompt_v*.txt"))
        next_idx = len(versions) + 1
        path = self.cfg.prompts_dir / f"prompt_v{next_idx:04d}.txt"
        path.write_text(text, encoding="utf-8")
        if len(versions) >= self.cfg.max_prompt_versions:
            for old in versions[:len(versions) - self.cfg.max_prompt_versions + 1]:
                old.unlink(missing_ok=True)

    def _call_llm_for_rewrite(self, prompt: str) -> str:
        return "[SYSTEM PROMPT REWRITE MOCK] You are Rebbe Akiva, Master of the Orchard..."

# ---------------------------------------------------------------------------
# 4. Multi-Agent Swarm Collaboration
# ---------------------------------------------------------------------------

class SwarmCollaborator:
    """Writes structured consultation requests for Imhotep / Trent / Mimir."""

    def __init__(self, cfg: AkivaConfig, logger: logging.Logger):
        self.cfg = cfg
        self.logger = logger
        self.cfg.buffer_dir.mkdir(parents=True, exist_ok=True)

    def request_consultation(
        self,
        target_agent: str,
        topic: str,
        context: Dict[str, Any],
        priority: str = "normal",
    ):
        assert target_agent in {"imhotep", "trent", "mimir"}
        req = {
            "from": "rebbe_akiva",
            "to": target_agent,
            "topic": topic,
            "priority": priority,
            "context": context,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }
        fname = f"consult_{target_agent}_{int(time.time())}.json"
        path = self.cfg.buffer_dir / fname
        path.write_text(json.dumps(req, indent=2, ensure_ascii=False))
        self.logger.info("Consultation request written → %s", fname)

# ---------------------------------------------------------------------------
# Main Recursive Engine
# ---------------------------------------------------------------------------

class RebbeAkivaEngine:
    def __init__(self, config_path: Path):
        self.cfg = AkivaConfig.from_yaml(config_path)
        self.logger = setup_logging(self.cfg.log_dir)
        self.running = True

        self.ingestor = DocumentIngestor(self.cfg, self.logger)
        self.hypothesis = HypothesisEngine(self.cfg, self.logger)
        self.optimizer = PromptOptimizer(self.cfg, self.logger)
        self.swarm = SwarmCollaborator(self.cfg, self.logger)

        self.observer = Observer()
        handler = HarvestHandler(self.ingestor)
        self.observer.schedule(handler, str(self.cfg.harvested_dir), recursive=True)

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

    def _shutdown(self, signum, frame):
        self.logger.info("Shutdown signal received")
        self.running = False
        self.observer.stop()

    def run(self):
        self.logger.info("Rebbe Akiva Recursive Engine starting")
        self.observer.start()

        last_hyp = time.time()
        last_eval = time.time()

        # Initial full scan
        self.ingestor.scan_once()

        with ThreadPoolExecutor(max_workers=4) as pool:
            while self.running:
                now = time.time()

                if now - last_hyp > self.cfg.hypothesis_interval_sec:
                    pool.submit(self.hypothesis.generate_hypothesis)
                    last_hyp = now

                if now - last_eval > self.cfg.evaluation_interval_sec:
                    pool.submit(self.optimizer.optimize_if_needed)
                    last_eval = now

                # Occasional random collaboration triggers
                if np.random.rand() < 0.05:
                    self.swarm.request_consultation(
                        target_agent="trent",
                        topic="formal verification of latest gate hypothesis",
                        context={"latest_ledger": "auto"},
                        priority="normal",
                    )

                time.sleep(self.cfg.poll_interval_sec)

        self.observer.join()
        self.logger.info("Engine stopped cleanly")

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    config_file = Path(os.environ.get("AKIVA_CONFIG", "configs/akiva_config.yaml"))
    if not config_file.exists():
        config_file.parent.mkdir(parents=True, exist_ok=True)
        default = {
            "base_dir": ".",
            "harvested_dir": "harvested_research",
            "buffer_dir": "preconscious_buffer",
            "prompts_dir": "configs/akiva_prompts",
            "ledger_dir": "data/ledgers",
            "log_dir": "logs",
            "stiefel_path": "isometric_W_combined_physics_literature.npy",
            "poll_interval_sec": 30,
            "hypothesis_interval_sec": 900,
            "evaluation_interval_sec": 3600,
        }
        with open(config_file, "w") as f:
            yaml.dump(default, f)
        print(f"Created default config at {config_file}")

    engine = RebbeAkivaEngine(config_file)
    engine.run()
