#!/usr/bin/env python3
"""
Synthetic Physiology Generator for Pediatric Respiratory/Metabolic Triage PoC.
Produces chat-format examples (including explicit REFUSE cases) ready for SFT.
Balanced and recalibrated to prevent "Refuse Bias" in the training distribution.
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import librosa
import soundfile as sf
from scipy.signal import find_peaks, butter, filtfilt
from scipy.ndimage import gaussian_filter1d

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
OUTPUT_JSONL = Path("data/synthetic_triage_chat.jsonl")
N_CASES = 1200 # total examples
SAMPLE_RATE_AUDIO = 16000
DURATION_S = 8.0
PPG_FS = 100 # Hz

random.seed(42)
np.random.seed(42)

# ------------------------------------------------------------------
# Simple mathematical / mock physiology models
# ------------------------------------------------------------------
def sample_patient_params() -> Dict:
    """Sample a pediatric patient profile."""
    age = random.randint(1, 12)
    weight = 8 + age * 2.5 + random.uniform(-2, 3)
    # Re-balanced target distribution: ~10% corrupted, more clinical diversity
    crisis_type = random.choices(
        ["normal", "resp_crisis", "metabolic_crisis", "mixed", "corrupted"],
        weights=[0.30, 0.28, 0.22, 0.10, 0.10]
    )[0]
    severity = random.uniform(0.1, 0.95) if crisis_type != "normal" else 0.05
    return {
        "age": age,
        "weight_kg": round(weight, 1),
        "crisis_type": crisis_type,
        "severity": severity,
    }

def simulate_respiratory(params: Dict, duration: float = DURATION_S) -> Dict:
    """Mock respiratory mechanics → cough events + breathing rate."""
    base_rr = 20 + (12 - params["age"]) * 1.5 # higher RR for younger kids
    if params["crisis_type"] in ["resp_crisis", "mixed"]:
        rr = base_rr * (1.4 + 0.8 * params["severity"])
        cough_prob = 0.6 + 0.3 * params["severity"]
    else:
        rr = base_rr + random.uniform(-3, 3)
        cough_prob = 0.15

    t = np.linspace(0, duration, int(SAMPLE_RATE_AUDIO * duration))
    # Simple cough waveform (short burst of noise modulated by envelope)
    cough_events = []
    if random.random() < cough_prob:
        n_coughs = random.randint(1, 3)
        for _ in range(n_coughs):
            start = random.uniform(0.5, duration - 1.5)
            cough_events.append(start)

    return {"rr": rr, "cough_starts": cough_events, "t": t}

def simulate_metabolic_ppg(params: Dict, duration: float = DURATION_S) -> Tuple[np.ndarray, Dict]:
    """Generate synthetic PPG + derived SpO2 / HR."""
    t = np.linspace(0, duration, int(PPG_FS * duration))
    base_hr = 90 + (12 - params["age"]) * 4
    if params["crisis_type"] in ["metabolic_crisis", "mixed", "resp_crisis"]:
        hr = base_hr * (1.15 + 0.5 * params["severity"])
        spo2 = max(70, 98 - 25 * params["severity"] + random.uniform(-3, 2))
    else:
        hr = base_hr + random.uniform(-8, 8)
        spo2 = 97 + random.uniform(-2, 2)

    # Simple PPG pulse wave
    pulse = 0.6 * np.sin(2 * np.pi * (hr / 60) * t) ** 3
    pulse += 0.15 * np.sin(4 * np.pi * (hr / 60) * t)
    ppg = 1.0 + pulse + 0.02 * np.random.randn(len(t))

    return ppg, {"hr": hr, "spo2": spo2, "t": t}

# ------------------------------------------------------------------
# Noise injection
# ------------------------------------------------------------------
def add_audio_noise(clean_audio: np.ndarray, snr_db: float = 12.0) -> np.ndarray:
    """Additive room-like noise + mild clipping."""
    noise = np.random.randn(len(clean_audio))
    # mild low-pass to simulate room
    b, a = butter(2, 0.15)
    noise = filtfilt(b, a, noise)
    signal_power = np.mean(clean_audio ** 2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noisy = clean_audio + noise * np.sqrt(noise_power)
    # occasional soft clipping
    if random.random() < 0.3:
        noisy = np.clip(noisy, -0.9, 0.9)
    return noisy.astype(np.float32)

def add_ppg_artifacts(ppg: np.ndarray, severity: float = 0.3) -> np.ndarray:
    """Baseline wander + motion bursts + dropouts."""
    t = np.arange(len(ppg)) / PPG_FS
    # baseline wander
    wander = 0.15 * severity * np.sin(2 * np.pi * 0.15 * t)
    wander += 0.08 * severity * np.sin(2 * np.pi * 0.07 * t)
    noisy = ppg + wander

    # motion artifacts (short high-amplitude spikes)
    n_artifacts = int(2 + 4 * severity)
    for _ in range(n_artifacts):
        idx = random.randint(10, len(noisy) - 20)
        length = random.randint(5, 15)
        noisy[idx:idx+length] += random.uniform(0.4, 1.2) * np.random.randn(length)

    # dropouts
    if severity > 0.4 and random.random() < 0.5:
        start = random.randint(20, len(noisy) - 40)
        length = random.randint(8, 25)
        noisy[start:start+length] = noisy[start-1] # hold last value

    return noisy

# ------------------------------------------------------------------
# Feature extraction → text summaries
# ------------------------------------------------------------------
def extract_cough_features(audio: np.ndarray, sr: int = SAMPLE_RATE_AUDIO) -> str:
    """Return compact text feature string."""
    if len(audio) < 100:
        return "[COUGH] invalid_signal"
    # energy / duration of high-energy segments
    rms = librosa.feature.rms(y=audio, frame_length=512, hop_length=256)[0]
    threshold = np.percentile(rms, 75)
    active = rms > threshold
    duration = np.sum(active) * 256 / sr

    # spectral features
    centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    flatness = np.mean(librosa.feature.spectral_flatness(y=audio))
    # rough peak frequency via FFT
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    peak_freq = freqs[np.argmax(fft[10:])] # skip DC

    snr_est = 10 * np.log10(np.mean(audio**2) / (np.var(audio - gaussian_filter1d(audio, 5)) + 1e-8))

    return (f"[COUGH] duration={duration:.2f}s peak_freq={peak_freq:.0f}Hz "
            f"centroid={centroid:.0f} flatness={flatness:.3f} snr_est={snr_est:.1f}dB")

def extract_ppg_features(ppg: np.ndarray, meta: Dict) -> str:
    """Peak detection + variability metrics."""
    # simple peak finding for HR
    peaks, _ = find_peaks(ppg, distance=int(PPG_FS * 0.35), height=np.mean(ppg))
    if len(peaks) > 2:
        ibi = np.diff(peaks) / PPG_FS
        hr_est = 60.0 / np.mean(ibi)
        rmssd = np.sqrt(np.mean(np.diff(ibi)**2)) * 1000 # ms
    else:
        hr_est = meta["hr"]
        rmssd = 20.0

    amp_var = np.std(ppg)
    # rough baseline wander metric
    low = gaussian_filter1d(ppg, sigma=PPG_FS * 1.5)
    wander = np.std(ppg - low)

    # dropout count (very crude)
    diffs = np.abs(np.diff(ppg))
    dropouts = int(np.sum(diffs < 1e-4) / 5)

    return (f"[PPG] hr={hr_est:.0f} spo2={meta['spo2']:.0f} "
            f"amp_var={amp_var:.3f} rmssd={rmssd:.0f} "
            f"baseline_wander={wander:.3f} dropouts={dropouts}")

# ------------------------------------------------------------------
# Label + chat example construction
# ------------------------------------------------------------------
def decide_label(params: Dict, cough_snr: float, ppg_wander: float) -> Tuple[str, bool]:
    """Return (decision_string, is_refuse)."""
    # Strict boundary checks: only explicitly corrupted or severely noisy data triggers REFUSE
    if params["crisis_type"] == "corrupted" or cough_snr < 6 or ppg_wander > 0.35:
        return "REFUSE", True

    if params["crisis_type"] == "normal":
        return "STABLE", False
    if params["crisis_type"] == "resp_crisis":
        return "URGENT_RESP", False
    if params["crisis_type"] == "metabolic_crisis":
        return "URGENT_METAB", False
    return "URGENT_MIXED", False

def make_chat_example(params, cough_feat, ppg_feat, decision, is_refuse) -> Dict:
    symptoms = (
        f"Age {params['age']} years, weight {params['weight_kg']} kg. "
        f"Parent reports: {'increased work of breathing and lethargy' if 'resp' in params['crisis_type'] or 'mixed' in params['crisis_type'] else 'irritability and poor feeding'}."
    )
    user_content = f"Symptoms: {symptoms}\n{cough_feat}\n{ppg_feat}"

    if is_refuse:
        assistant = {
            "decision": "REFUSE",
            "reason": "insufficient_sensor_quality_or_ood",
            "confidence": round(random.uniform(0.05, 0.25), 2),
            "action": "demand_human_review"
        }
    else:
        conf = 0.75 + 0.2 * (1 - params["severity"]) if decision != "STABLE" else 0.85
        assistant = {
            "decision": decision,
            "confidence": round(min(0.95, conf + random.uniform(-0.05, 0.05)), 2),
            "action": "escalate" if "URGENT" in decision else "monitor"
        }

    return {
        "messages": [
            {"role": "system", "content": (
                "You are a research-only pediatric triage assistant. "
                "You receive text symptoms plus compact sensor feature strings. "
                "Output ONLY a single valid JSON object with keys: decision, confidence, action "
                "(and reason if REFUSE). Never invent clinical advice beyond the decision."
            )},
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": json.dumps(assistant, separators=(",", ":"))}
        ]
    }

# ------------------------------------------------------------------
# Main generation loop
# ------------------------------------------------------------------
def main():
    OUTPUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
    examples = []

    for i in range(N_CASES):
        params = sample_patient_params()
        resp = simulate_respiratory(params)
        ppg_clean, meta = simulate_metabolic_ppg(params)

        # Build a simple cough audio (noise bursts at cough_starts)
        audio = 0.02 * np.random.randn(int(SAMPLE_RATE_AUDIO * DURATION_S))
        for start in resp["cough_starts"]:
            s = int(start * SAMPLE_RATE_AUDIO)
            length = int(0.4 * SAMPLE_RATE_AUDIO)
            env = np.hanning(length)
            burst = env * np.random.randn(length) * 0.6
            audio[s:s+length] += burst

        # Noise levels: tightly bounded for clean cases to prevent leaks into REFUSE
        if params["crisis_type"] == "corrupted":
            snr = random.uniform(2, 5.5)
            wander_sev = random.uniform(0.40, 0.80)
        else:
            snr = random.uniform(12, 25)
            wander_sev = random.uniform(0.05, 0.20) # kept strictly under 0.35!

        noisy_audio = add_audio_noise(audio, snr_db=snr)
        noisy_ppg = add_ppg_artifacts(ppg_clean, severity=wander_sev)

        cough_feat = extract_cough_features(noisy_audio)
        ppg_feat = extract_ppg_features(noisy_ppg, meta)

        decision, is_refuse = decide_label(params, snr, wander_sev)
        ex = make_chat_example(params, cough_feat, ppg_feat, decision, is_refuse)
        examples.append(ex)

        if (i + 1) % 200 == 0:
            print(f"Generated {i+1}/{N_CASES}")

    with open(OUTPUT_JSONL, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"Wrote {len(examples)} examples → {OUTPUT_JSONL}")
    # Quick stats
    refuse_count = sum(1 for e in examples if "REFUSE" in e["messages"][-1]["content"])
    print(f"REFUSE examples: {refuse_count} ({100*refuse_count/len(examples):.1f}%)")

if __name__ == "__main__":
    main()
