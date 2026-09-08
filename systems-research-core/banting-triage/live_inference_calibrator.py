#!/usr/bin/env python3
"""
Live inference + simple entropy / max-prob calibrator.
Forces REFUSE when the model is uncertain using Grok's Multi-Gate logic.
"""

import json
import torch
import numpy as np
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import librosa
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

# ------------------------------------------------------------------
# Paths & Calibration Thresholds (Grok's Recalibrated Multi-Gate)
# ------------------------------------------------------------------
BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_PATH = "adapters/triage-lora-0.5b"
ENTROPY_THRESHOLD = 0.85 # Max predictive entropy allowed
MAX_PROB_THRESHOLD = 0.28 # Min token probability allowed
MARGIN_THRESHOLD = 0.18 # Min margin between top-1 and top-2 token allowed

# ------------------------------------------------------------------
# Feature extractors (same as generator)
# ------------------------------------------------------------------
def extract_cough_features(wav_path: str, sr: int = 16000) -> str:
    audio, _ = librosa.load(wav_path, sr=sr, mono=True)
    if len(audio) < 100:
        return "[COUGH] invalid_signal"
    rms = librosa.feature.rms(y=audio, frame_length=512, hop_length=256)[0]
    threshold = np.percentile(rms, 75)
    duration = np.sum(rms > threshold) * 256 / sr
    centroid = np.mean(librosa.feature.spectral_centroid(y=audio, sr=sr))
    flatness = np.mean(librosa.feature.spectral_flatness(y=audio))
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1/sr)
    peak_freq = freqs[np.argmax(fft[10:])]
    snr_est = 10 * np.log10(np.mean(audio**2) / (np.var(audio - gaussian_filter1d(audio, 5)) + 1e-8))
    return (f"[COUGH] duration={duration:.2f}s peak_freq={peak_freq:.0f}Hz "
            f"centroid={centroid:.0f} flatness={flatness:.3f} snr_est={snr_est:.1f}dB")

def extract_ppg_features_from_metrics(hr: float, spo2: float, amp_var: float = 0.15,
                                     rmssd: float = 25.0, wander: float = 0.08,
                                     dropouts: int = 0) -> str:
    return (f"[PPG] hr={hr:.0f} spo2={spo2:.0f} amp_var={amp_var:.3f} "
            f"rmssd={rmssd:.0f} baseline_wander={wander:.3f} dropouts={dropouts}")

# ------------------------------------------------------------------
# Model loading
# ------------------------------------------------------------------
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    base = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto",
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base, ADAPTER_PATH)
    model.eval()
    return model, tokenizer

# ------------------------------------------------------------------
# Generation + uncertainty check
# ------------------------------------------------------------------
@torch.no_grad()
def generate_with_calibration(model, tokenizer, messages, max_new_tokens=128):
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Generate with scores
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        do_sample=False, # greedy for stability
        return_dict_in_generate=True,
        output_scores=True,
        pad_token_id=tokenizer.eos_token_id,
    )

    generated_ids = outputs.sequences[0][inputs.input_ids.shape[1]:]
    text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

    # Sequence-level uncertainty proxies
    entropies = []
    max_probs = []
    margins = []
    for score in outputs.scores:
        probs = torch.softmax(score[0], dim=-1)
        
        # Calculate token entropy
        entropy = -torch.sum(probs * torch.log(probs + 1e-10)).item()
        entropies.append(entropy)
        
        # Sort probabilities to get top 2
        top2 = torch.topk(probs, k=2, dim=-1)
        best_prob = top2.values[0].item()
        second_prob = top2.values[1].item()
        
        max_probs.append(best_prob)
        margins.append(best_prob - second_prob)

    avg_entropy = float(np.mean(entropies)) if entropies else 99.0
    min_max_prob = float(np.min(max_probs)) if max_probs else 0.0
    min_margin = float(np.min(margins)) if margins else 0.0

    # Multi-Gate Calibration Check
    # Refuse if average entropy is too high, or min token probability is too low, or confidence margin is too tight
    force_refuse = (avg_entropy > ENTROPY_THRESHOLD) or (min_max_prob < MAX_PROB_THRESHOLD) or (min_margin < MARGIN_THRESHOLD)

    return text, avg_entropy, min_max_prob, min_margin, force_refuse

# ------------------------------------------------------------------
# Main live loop
# ------------------------------------------------------------------
def main(wav_path: str, hr: float = 140.0, spo2: float = 91.0):
    model, tokenizer = load_model()

    cough_feat = extract_cough_features(wav_path)
    ppg_feat = extract_ppg_features_from_metrics(hr, spo2)

    system = (
        "You are a research-only pediatric triage assistant. "
        "You receive text symptoms plus compact sensor feature strings. "
        "Output ONLY a single valid JSON object with keys: decision, confidence, action "
        "(and reason if REFUSE). Never invent clinical advice beyond the decision."
    )
    user = (
        f"Symptoms: Age 4 years, weight 16 kg. Parent reports increased work of breathing.\n"
        f"{cough_feat}\n{ppg_feat}"
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    raw_text, entropy, min_prob, min_margin, force_refuse = generate_with_calibration(
        model, tokenizer, messages
    )

    print("=" * 60)
    print("Raw generation:", raw_text)
    print(f"Avg entropy: {entropy:.3f} | Min max-prob: {min_prob:.3f} | Min margin: {min_margin:.3f}")
    print(f"Force REFUSE: {force_refuse}")

    if force_refuse:
        final = {
            "decision": "REFUSE",
            "reason": "model_uncertainty_high",
            "confidence": 0.15,
            "action": "demand_human_review",
            "diagnostics": {"entropy": entropy, "min_max_prob": min_prob, "min_margin": min_margin}
        }
    else:
        try:
            # Attempt to parse the model JSON; fall back to refuse on failure
            final = json.loads(raw_text)
            final["diagnostics"] = {"entropy": entropy, "min_max_prob": min_prob, "min_margin": min_margin}
        except Exception:
            final = {
                "decision": "REFUSE",
                "reason": "invalid_json_from_model",
                "confidence": 0.10,
                "action": "demand_human_review",
            }

    print("\nCalibrated decision:")
    print(json.dumps(final, indent=2))
    return final

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--wav", type=str, required=True, help="Path to cough .wav")
    parser.add_argument("--hr", type=float, default=142.0)
    parser.add_argument("--spo2", type=float, default=90.0)
    args = parser.parse_args()
    main(args.wav, args.hr, args.spo2)
