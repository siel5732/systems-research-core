import os
import sys
import math
import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

# Append SAGE-Lumen path
sys.path.append("/home/fq9f/systems-research-core")
sys.path.append("/data/.openclaw/workspace")

try:
    from scripts.lumen_model_architecture import SAGE_Lumen_3M, LumenConfig
except ImportError:
    # Fallback to local import if run outside workspace roots
    from lumen_model_architecture import SAGE_Lumen_3M, LumenConfig

def sample_tokens(model, input_ids, max_tokens=100, temp=0.7, top_p=0.9, rep_penalty=1.15, eos_id=1):
    model.eval()
    generated = input_ids.clone()
    
    for _ in range(max_tokens):
        curr_input = generated[:, -model.config.max_seq_len:]
        with torch.no_grad():
            logits, _ = model(curr_input)
        logits = logits[:, -1, :]
        
        # Apply repetition penalty
        if rep_penalty != 1.0:
            score = torch.gather(logits, 1, generated)
            score = torch.where(score < 0, score * rep_penalty, score / rep_penalty)
            logits.scatter_(1, generated, score)
            
        if temp > 0.0:
            logits = logits / max(temp, 1e-5)
            if top_p < 1.0:
                sorted_logits, sorted_idx = torch.sort(logits, descending=True, dim=-1)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                sorted_indices_to_remove = cumulative_probs > top_p
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = False
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_idx, sorted_indices_to_remove)
                logits = logits.masked_fill(indices_to_remove, float("-inf"))
                
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
        else:
            next_token = torch.argmax(logits, dim=-1, keepdim=True)
            
        generated = torch.cat([generated, next_token], dim=-1)
        if next_token.item() == eos_id:
            break
            
    return generated[0].tolist()

def evaluate_syntax_coherence(text: str) -> dict:
    """Checks XML structural integrity of SAGE-Lumen output syntax."""
    tags = ["<s>", "<state>", "</state>", "<thought>", "</thought>", "<state>", "</state>", "</s>"]
    positions = {tag: [] for tag in tags}
    
    # Simple order check
    for tag in tags:
        pos = text.find(tag)
        positions[tag].append(pos)
        
    passed_syntax = True
    reasons = []
    
    # 1. Check occurrences
    for tag in tags:
        if text.count(tag) == 0:
            passed_syntax = False
            reasons.append(f"Missing tag: {tag}")
            
    # 2. Check linear flow: s -> state -> /state -> thought -> /thought -> state -> /state -> /s
    if passed_syntax:
        indices = [text.find(t) for t in tags]
        # Sort and verify it is strictly increasing
        if indices != sorted(indices):
            passed_syntax = False
            reasons.append("Malformed tag sequence order.")
            
    return {"passed": passed_syntax, "reasons": reasons}

def evaluate_diversity_entropy(tokens: list) -> float:
    """Measures token repetition loop behavior. Returns unique token ratio."""
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)

def run_lumen_bench():
    print("=" * 60)
    print("         SAGE-LUMEN-3M STATE-TRANSITION BENCHMARK        ")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] Target Hardware Device: {device}")
    
    # 1. Resolve Paths
    model_weights_path = "/home/fq9f/systems-research-core/models/lumen_pretrained_3m/pytorch_model.bin"
    tokenizer_path = "/home/fq9f/systems-research-core/models/lumen_tokenizer/tokenizer.json"
    
    if not os.path.exists(model_weights_path):
        model_weights_path = "models/lumen_pretrained_3m/pytorch_model.bin"
        tokenizer_path = "models/lumen_tokenizer/tokenizer.json"
        
    if not os.path.exists(model_weights_path):
        print(f"[!] Error: Pre-trained model weights not found at {model_weights_path}")
        print("Please train the model or ensure the weights path matches your GEEKOM workspace.")
        return
        
    # 2. Load Tokenizer & Model
    print(f"[*] Loading Tokenizer from {tokenizer_path}...")
    tokenizer = Tokenizer.from_file(tokenizer_path)
    
    print(f"[*] Loading SAGE-Lumen-3M Architecture and Weights...")
    config = LumenConfig()
    model = SAGE_Lumen_3M(config)
    model.load_state_dict(torch.load(model_weights_path, map_location=device))
    model.to(device)
    model.eval()
    print("[+] Architecture loaded and weight matrices validated successfully.")
    
    # 3. Define State-Space Prompts
    test_prompts = {
        "Quantum Walk (DTQW)": "<s> <state> t=0 |ψ_0⟩ = ⟨0|ψ⟩:(0.71+0.71i)|0⟩ </state> <thought>",
        "Lorenz Attractor (Chaotic)": "<s> <state> t=0 coordinates: x=0.5000, y=-0.2000, z=20.0000 </state> <thought>",
        "Glycemic Homeostasis": "<s> <state> t=0 biophysical_state: Glucose=140.00mg/dL, Insulin=15.00uU/mL </state> <thought>",
        "G-Code Nonplanar Toolpath": "<s> <state> t=0 toolpath_state: X=0.00, Y=0.00, Z=0.20 </state> <thought>"
    }
    
    scorecard = {}
    
    print("\n" + "-"*50)
    print("LAUNCHING TRAJECTORY SIMULATION BENCHMARKS...")
    print("-"*50)
    
    for domain, prompt in test_prompts.items():
        print(f"\n[*] Evaluating Domain: {domain}")
        print(f"    Prompt: {prompt}")
        
        encoded = tokenizer.encode(prompt)
        input_ids = torch.tensor([encoded.ids], dtype=torch.long, device=device)
        
        # Simulate trajectory
        generated_tokens = sample_tokens(
            model=model,
            input_ids=input_ids,
            max_tokens=80,
            temp=0.7,
            top_p=0.9,
            rep_penalty=1.15,
            eos_id=1
        )
        
        # Decode and analyze output
        decoded_output = tokenizer.decode(generated_tokens)
        
        syntax_res = evaluate_syntax_coherence(decoded_output)
        diversity = evaluate_diversity_entropy(generated_tokens)
        
        print(f"    [Output]: {decoded_output}")
        print(f"    [Evaluation]:")
        print(f"      - Token Count: {len(generated_tokens)}")
        print(f"      - Syntax Coherence: {'PASSED' if syntax_res['passed'] else 'FAILED'}")
        if not syntax_res["passed"]:
            print(f"        Reason: {syntax_res['reasons']}")
        print(f"      - Unique Token Diversity: {diversity:.4f}")
        
        scorecard[domain] = {
            "token_count": len(generated_tokens),
            "syntax_passed": syntax_res["passed"],
            "diversity_score": diversity,
            "raw_output": decoded_output
        }
        
    print("\n" + "=" * 60)
    print("               FINAL BENCHMARK SCORECARD                 ")
    print("=" * 60)
    
    passed_domains = sum(1 for d in scorecard.values() if d["syntax_passed"])
    mean_diversity = sum(d["diversity_score"] for d in scorecard.values()) / len(scorecard)
    
    print(f"  - Syntactic Integrity: {passed_domains}/{len(scorecard)} Domains Passed")
    print(f"  - Mean Representation Diversity: {mean_diversity:.4f} (Ideal: > 0.400)")
    print(f"  - Loop Defense Integrity: {'SECURE' if mean_diversity > 0.35 else 'LOOP DETECTED (VULNERABLE)'}")
    print("=" * 60)

if __name__ == "__main__":
    run_lumen_bench()
