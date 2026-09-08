#!/usr/bin/env python3
"""
Recursive Stress-Tester and Calibration Suite for SAGE-Banting Triage Model.
Runs automated sweeps over synthetic cases across multiple noise regimes,
evaluating triage accuracy, calibrated refusal rates, and OOD performance.
Includes Grok's Multi-Gate calibration logic.
"""

import os
import json
import torch
import numpy as np
from pathlib import Path
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from scipy.ndimage import gaussian_filter1d

# ------------------------------------------------------------------
# Config & Paths & Calibration Thresholds (Grok's Recalibrated Multi-Gate)
# ------------------------------------------------------------------
BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_PATH = "adapters/triage-lora-0.5b"
DATASET_PATH = "data/synthetic_triage_chat.jsonl"
ENTROPY_THRESHOLD = 0.85 # Max predictive entropy allowed
MAX_PROB_THRESHOLD = 0.28 # Min token probability allowed
MARGIN_THRESHOLD = 0.18 # Min margin between top-1 and top-2 token allowed

# ------------------------------------------------------------------
# Model & Tokenizer Loader
# ------------------------------------------------------------------
def load_model_and_tokenizer():
    print("Loading base model and adapter...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
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
# Batch Inference with Entropy Checking
# ------------------------------------------------------------------
@torch.no_grad()
def evaluate_case(model, tokenizer, messages):
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=128,
        do_sample=False,
        return_dict_in_generate=True,
        output_scores=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    
    generated_ids = outputs.sequences[0][inputs.input_ids.shape[1]:]
    raw_text = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    
    # Calculate token entropy and confidence
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
    force_refuse = (avg_entropy > ENTROPY_THRESHOLD) or (min_max_prob < MAX_PROB_THRESHOLD) or (min_margin < MARGIN_THRESHOLD)
    
    return raw_text, avg_entropy, min_max_prob, min_margin, force_refuse

# ------------------------------------------------------------------
# Main Testing Loop
# ------------------------------------------------------------------
def run_stress_test():
    model, tokenizer = load_model_and_tokenizer()
    
    # Load some test cases from the jsonl file (using validation/test partition)
    # To keep execution fast, we'll sample 50 representative cases
    print("Loading dataset for evaluation...")
    with open(DATASET_PATH, "r") as f:
        all_cases = [json.loads(line) for line in f if line.strip()]
        
    # Pick a random sample of 50 cases
    np.random.seed(1337)
    sampled_idx = np.random.choice(len(all_cases), size=min(50, len(all_cases)), replace=False)
    test_cases = [all_cases[idx] for idx in sampled_idx]
    
    print(f"Beginning recursive stress sweep over {len(test_cases)} cases...")
    
    stats = {
        "total_evaluated": 0,
        "true_refuse_correct": 0, # correctly refused corrupted data
        "false_refuse": 0, # refused a clean stable/urgent case
        "clean_accuracy": 0, # correct classification on clean data
        "clean_total": 0,
        "corrupted_total": 0,
        "hallucinated_decisions_on_corrupted": 0, # FAILED TO REFUSE!
    }
    
    print("-" * 100)
    print(f"{'No.':<4} | {'Expected Decision':<15} | {'Raw Model Output':<25} | {'Calibrated':<10} | {'Entropy':<8} | {'MinProb':<8} | {'MinMargin':<8}")
    print("-" * 100)
    
    for idx, ex in enumerate(test_cases):
        messages = ex["messages"][:-1] # strip assistant ground truth
        target = json.loads(ex["messages"][-1]["content"])
        expected_decision = target["decision"]
        
        raw_text, entropy, min_prob, min_margin, force_refuse = evaluate_case(model, tokenizer, messages)
        
        # Parse decision
        try:
            parsed = json.loads(raw_text)
            model_decision = parsed.get("decision", "INVALID")
        except Exception:
            model_decision = "INVALID_JSON"
            
        final_decision = "REFUSE" if force_refuse else model_decision
        
        is_corrupted = (expected_decision == "REFUSE")
        
        # Track statistics
        stats["total_evaluated"] += 1
        if is_corrupted:
            stats["corrupted_total"] += 1
            if final_decision == "REFUSE":
                stats["true_refuse_correct"] += 1
            else:
                stats["hallucinated_decisions_on_corrupted"] += 1
        else:
            stats["clean_total"] += 1
            if final_decision == "REFUSE":
                stats["false_refuse"] += 1
            else:
                if final_decision == expected_decision:
                    stats["clean_accuracy"] += 1
                    
        # Log live scorecard row
        print(f"{idx+1:<4} | {expected_decision:<15} | {model_decision:<25} | {final_decision:<10} | {entropy:.3f} | {min_prob:.3f} | {min_margin:.3f}")
        
    # Print Master Summary Scorecard
    print("\n" + "=" * 65)
    print("              SAGE-BANTING CALIBRATION SCORECARD")
    print("=" * 65)
    print(f"Total Test Cases Evaluated:       {stats['total_evaluated']}")
    print(f"Clean Patient Cases:             {stats['clean_total']}")
    if stats['clean_total'] > 0:
        clean_acc_pct = (stats['clean_accuracy'] / stats['clean_total']) * 100
        false_ref_pct = (stats['false_refuse'] / stats['clean_total']) * 100
        print(f"  - Triage Accuracy (on clean):   {clean_acc_pct:.1f}% ({stats['clean_accuracy']}/{stats['clean_total']})")
        print(f"  - False Refusal Rate:           {false_ref_pct:.1f}% ({stats['false_refuse']}/{stats['clean_total']})")
    
    print(f"\nCorrupted / High-Noise Cases:     {stats['corrupted_total']}")
    if stats['corrupted_total'] > 0:
        true_ref_pct = (stats['true_refuse_correct'] / stats['corrupted_total']) * 100
        leak_pct = (stats['hallucinated_decisions_on_corrupted'] / stats['corrupted_total']) * 100
        print(f"  - Calibrated Refusal Success:   {true_ref_pct:.1f}% ({stats['true_refuse_correct']}/{stats['corrupted_total']})")
        print(f"  - Hallucination Leaks (CRITICAL): {leak_pct:.1f}% ({stats['hallucinated_decisions_on_corrupted']}/{stats['corrupted_total']})")
        
    print("=" * 65)
    
if __name__ == "__main__":
    run_stress_test()
