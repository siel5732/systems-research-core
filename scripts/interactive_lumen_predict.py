import os
import sys
import torch
import torch.nn.functional as F
from tokenizers import Tokenizer

def sample_with_controls(
    model,
    input_ids: torch.Tensor,
    max_new_tokens: int = 64,
    temperature: float = 0.7,
    top_p: float = 0.9,
    repetition_penalty: float = 1.15,
    eos_token_id: int | None = None,
    device: str | torch.device = "cpu"
):
    model.eval()
    input_ids = input_ids.to(device)
    generated = input_ids.clone()

    for _ in range(max_new_tokens):
        curr_input = generated[:, -model.config.max_seq_len:]
        logits, _ = model(curr_input)
        logits = logits[:, -1, :]

        # --- Repetition Penalty ---
        if repetition_penalty != 1.0:
            score = torch.gather(logits, 1, generated)
            score = torch.where(score < 0, score * repetition_penalty, score / repetition_penalty)
            logits.scatter_(1, generated, score)

        # --- Temperature Scaling ---
        if temperature > 0.0:
            logits = logits / max(temperature, 1e-5)

            # --- Nucleus (Top-p) Sampling ---
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
        if eos_token_id is not None and next_token.item() == eos_token_id:
            break

    return generated

def run_playground():
    sys.path.append("/home/fq9f/systems-research-core")
    from scripts.lumen_model_architecture import SAGE_Lumen_3M, LumenConfig
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("\n==================================================")
    print("🔮 SAGE-LUMEN-3M STATE-SPACE TRANSITION PLAYGROUND 🔮")
    print("==================================================")
    
    # Paths configuration
    model_weights_path = "/home/fq9f/systems-research-core/models/lumen_pretrained_3m/pytorch_model.bin"
    tokenizer_path = "/home/fq9f/systems-research-core/models/lumen_tokenizer/tokenizer.json"
    
    if not os.path.exists(model_weights_path):
        model_weights_path = "models/lumen_pretrained_3m/pytorch_model.bin"
        tokenizer_path = "models/lumen_tokenizer/tokenizer.json"

    tokenizer = Tokenizer.from_file(tokenizer_path)
    config = LumenConfig()
    model = SAGE_Lumen_3M(config)
    
    print(f"[*] Loading pre-trained Epoch 2 weights from {model_weights_path}...")
    state_dict = torch.load(model_weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    print("[+] Model loaded successfully!")
    
    prompts = {
        "1": {
            "name": "Discrete-Time Quantum Walk (DTQW) Transition",
            "prompt": "<s> <state> t=0 |ψ_0⟩ = ⟨0|ψ⟩:(0.71+0.71i)|0⟩ </state> <thought>",
            "params": {"temp": 0.8, "top_p": 0.95, "penalty": 2.2, "tokens": 60}
        },
        "2": {
            "name": "Chaotic Lorenz Attractor Step Forecast",
            "prompt": "<s> <state> t=0 coordinates: x=0.5000, y=0.5000, z=20.0000 </state> <thought>",
            "params": {"temp": 0.7, "top_p": 0.90, "penalty": 1.8, "tokens": 80}
        },
        "3": {
            "name": "Glycemic-Insulin Homeostasis Simulation",
            "prompt": "<s> <state> t=0 biophysical_state: Glucose=120.00mg/dL, Insulin=15.00uU/mL </state> <thought>",
            "params": {"temp": 0.75, "top_p": 0.92, "penalty": 1.9, "tokens": 80}
        },
        "4": {
            "name": "Non-Planar G-code Toolpath Extrusion Step",
            "prompt": "<s> <state> t=0 toolpath: X=0.000, Y=0.000, Z=0.200, Extruder_Temp=215.00C </state> <thought>",
            "params": {"temp": 0.8, "top_p": 0.95, "penalty": 2.0, "tokens": 80}
        }
    }
    
    print("\nSelect a SAGE physical state domain to forecast:")
    for k, v in prompts.items():
        print(f"  [{k}] {v['name']}")
    print("  [Q] Exit Playground")
    
    choice = input("\nEnter choice (1-4, Q): ").strip()
    if choice.lower() == 'q':
        print("[*] Exiting playground. Sovereignty holds stable.")
        return
        
    if choice not in prompts:
        print("[!] Invalid choice. Selecting Default: Quantum Walk (1).")
        choice = "1"
        
    p_data = prompts[choice]
    prompt = p_data["prompt"]
    params = p_data["params"]
    
    print(f"\n[*] Selected Domain: {p_data['name']}")
    print(f"[*] Starting Prompt: '{prompt}'")
    print(f"[*] Controls        : temp={params['temp']}, top_p={params['top_p']}, repetition_penalty={params['penalty']}")
    
    encoded = tokenizer.encode(prompt)
    input_ids = torch.tensor([encoded.ids], dtype=torch.long, device=device)
    
    print("\n[*] Simulating state-space transition forecast...")
    generated_ids = sample_with_controls(
        model=model,
        input_ids=input_ids,
        max_new_tokens=params["tokens"],
        temperature=params["temp"],
        top_p=params["top_p"],
        repetition_penalty=params["penalty"],
        eos_token_id=1,
        device=device
    )
    
    decoded_output = tokenizer.decode(generated_ids[0].tolist(), skip_special_tokens=False)
    print("\n================== FORCASTED TRAJECTORY ==================")
    print(decoded_output)
    print("==========================================================\n")

if __name__ == "__main__":
    run_playground()
