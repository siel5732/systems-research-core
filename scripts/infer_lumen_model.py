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
    """
    Temperature + Nucleus (top-p) + Repetition Penalty Sampler.
    Bypasses greedy self-reinforcing loops (like the infinite '3909' squeal) 
    and drives clean, multi-step state transitions.
    """
    model.eval()
    input_ids = input_ids.to(device)
    generated = input_ids.clone()

    # Track token frequencies for vectorized repetition penalty calculations
    # Capped at our 2k vocabulary boundary
    vocab_size = model.config.vocab_size

    for _ in range(max_new_tokens):
        # Forward pass on active slice
        curr_input = generated[:, -model.config.max_seq_len:]
        logits, _ = model(curr_input)
        logits = logits[:, -1, :] # Fetch final logits [1, vocab_size]

        # --- Repetition Penalty (Vectorized HF-style) ---
        if repetition_penalty != 1.0:
            # Gather logits of previously generated tokens
            score = torch.gather(logits, 1, generated)
            # Penalize: positive logits are divided, negative are multiplied to push down probability
            score = torch.where(score < 0, score * repetition_penalty, score / repetition_penalty)
            logits.scatter_(1, generated, score)

        # --- Temperature Scaling ---
        if temperature > 0.0:
            logits = logits / max(temperature, 1e-5)

            # --- Nucleus (Top-p) Sampling ---
            if top_p < 1.0:
                sorted_logits, sorted_idx = torch.sort(logits, descending=True, dim=-1)
                cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)
                
                # Remove tokens with cumulative probability exceeding threshold
                sorted_indices_to_remove = cumulative_probs > top_p
                # Shift indices to the right to keep at least the first/highest probability option
                sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
                sorted_indices_to_remove[..., 0] = False
                
                indices_to_remove = sorted_indices_to_remove.scatter(1, sorted_idx, sorted_indices_to_remove)
                logits = logits.masked_fill(indices_to_remove, float("-inf"))

            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
        else:
            # Deterministic greedy fallback
            next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)

        generated = torch.cat([generated, next_token], dim=-1)

        # Break on End of Sequence (</s> ID 1)
        if eos_token_id is not None and next_token.item() == eos_token_id:
            break

    return generated

def run_inference(prompt: str, max_new_tokens: int = 64, temperature: float = 0.7, top_p: float = 0.9, repetition_penalty: float = 1.15):
    """
    Initializes SAGE-Lumen-3M and generates trajectories utilizing controlled sampling.
    """
    sys.path.append("/home/fq9f/systems-research-core")
    from scripts.lumen_model_architecture import SAGE_Lumen_3M, LumenConfig
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Paths configuration
    model_weights_path = "/home/fq9f/systems-research-core/models/lumen_pretrained_3m/pytorch_model.bin"
    tokenizer_path = "/home/fq9f/systems-research-core/models/lumen_tokenizer/tokenizer.json"
    
    if not os.path.exists(model_weights_path):
        model_weights_path = "models/lumen_pretrained_3m/pytorch_model.bin"
        tokenizer_path = "models/lumen_tokenizer/tokenizer.json"

    tokenizer = Tokenizer.from_file(tokenizer_path)
    
    config = LumenConfig()
    model = SAGE_Lumen_3M(config)
    
    print(f"[*] Loading model weights from {model_weights_path}...")
    state_dict = torch.load(model_weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    
    print(f"[+] SAGE-Lumen-3M initialized successfully on {device}!")
    print(f"[*] Input Starting Prompt: '{prompt}'")
    
    encoded = tokenizer.encode(prompt)
    input_ids = torch.tensor([encoded.ids], dtype=torch.long, device=device)
    
    print(f"[*] Simulating trajectory via Controlled Sampler (temp={temperature}, top_p={top_p}, penalty={repetition_penalty})...")
    generated_ids = sample_with_controls(
        model=model,
        input_ids=input_ids,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        repetition_penalty=repetition_penalty,
        eos_token_id=1, # </s> ID 1
        device=device
    )
    
    decoded_output = tokenizer.decode(generated_ids[0].tolist(), skip_special_tokens=False)
    print("\n--- GENERATED STATE-SPACE TRAJECTORY ---")
    print(decoded_output)
    print("----------------------------------------\n")
    return decoded_output

if __name__ == "__main__":
    test_prompt = "<s> <state> t=0 |ψ_0⟩ = ⟨0|ψ⟩:(0.71+0.71i)|0⟩ </state> <thought>"
    run_inference(test_prompt, max_new_tokens=60, temperature=0.7, top_p=0.9, repetition_penalty=1.15)
