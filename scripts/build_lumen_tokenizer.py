import os
import json
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import ByteLevel
from tokenizers.processors import ByteLevel as ByteLevelProcessor
from tokenizers.decoders import ByteLevel as ByteLevelDecoder

def build_lumen_tokenizer(corpus_path: str, output_dir: str = "models/lumen_tokenizer"):
    """
    Trains a highly specialized 2,048 (2k) vocabulary Byte-Level BPE tokenizer
    specifically optimized for the SAGE-Lumen symbolic math, quantum mechanics,
    and biophysical state-space transition syntax.
    """
    print(f"[*] Initializing SAGE-Lumen Tokenizer Trainer (Vocab limit: 2,048)...")
    
    # 1. Initialize BPE model with byte-level fallback support
    tokenizer = Tokenizer(BPE(unk_token="<unk>"))
    tokenizer.pre_tokenizer = ByteLevel(add_prefix_space=False)
    
    # 2. Add our critical domain-specific Special/Control Tokens.
    # These prevent byte-fallback cascades for our core state-machine and reasoning syntax.
    special_tokens = [
        "<s>", "</s>", "<pad>", "<unk>",
        "<thought>", "</thought>",  # Protoreasoning / Chain-of-thought delimiters
        "<state>", "</state>",      # State-space transition boundaries
        "\\partial", "dt", "t+1", "t", # Common ODE operator atoms
        "|->", "⟨", "⟩", "|ψ⟩", "σ_x", # Bra-ket and Pauli spin operators
        "Δt", "dx", "dy", "dz"      # Differential geometry steps
    ]
    
    # 3. Configure BPE Trainer with strict 2,048 vocabulary cap
    trainer = BpeTrainer(
        vocab_size=2048,
        min_frequency=2,
        special_tokens=special_tokens,
        initial_alphabet=ByteLevel.alphabet()
    )
    
    # Ensure corpus file exists before training
    if not os.path.exists(corpus_path):
        print(f"[-] Corpus path '{corpus_path}' not found. Generating a dummy preview corpus for initialization.")
        os.makedirs(os.path.dirname(corpus_path), exist_ok=True)
        generate_sample_math_corpus(corpus_path)

    # 4. Train Tokenizer exclusively on our specialized domain data
    print(f"[*] Training on {corpus_path}...")
    tokenizer.train(files=[corpus_path], trainer=trainer)
    
    # Enable post-processing for byte-level sequence recovery
    tokenizer.post_processor = ByteLevelProcessor(trim_offsets=False)
    tokenizer.decoder = ByteLevelDecoder()
    
    # Save the trained model
    os.makedirs(output_dir, exist_ok=True)
    tokenizer.save(os.path.join(output_dir, "tokenizer.json"))
    print(f"[+] Tokenizer successfully saved to {output_dir}/tokenizer.json")
    
    # Print sample tokens to inspect merge success
    vocab = tokenizer.get_vocab()
    print(f"[+] Actual trained vocabulary size: {len(vocab)}")
    print(f"[*] Sample special and domain tokens in vocabulary:")
    for token in special_tokens:
        if token in vocab:
            print(f"  - '{token}': ID {vocab[token]}")

def generate_sample_math_corpus(output_path: str):
    """
    Generates a high-density, highly-randomized sample mathematical corpus
    to initialize and test the tokenizer's BPE merge priority on symbolic physics.
    """
    samples = []
    # Loop over typical symbolic physical transitions to build up correct BPE merge frequencies
    for t in range(50):
        samples.append(f"<state> |ψ_{{t}}⟩ = a|0⟩ + b|1⟩ </state> <thought> apply σ_x rotation at t={t} </thought> <state> |ψ_{{t+1}}⟩ = b|0⟩ + a|1⟩ </state>")
        samples.append(f"<state> dx/dt = -k * x(t) </state> <thought> solve ODE using forward Euler with step size Δt </thought> <state> x(t+1) = x(t) - k * x(t) * Δt </state>")
        samples.append(f"<state> \\partial_t \\psi = i * H * \\psi </state> <thought> unitary evolution matrix U = exp(-i * H * Δt) </thought> <state> \\psi_{{t+1}} = U * \\psi_t </state>")
    
    with open(output_path, "w") as f:
        f.write("\n".join(samples))
    print(f"[+] Sample math corpus generated at {output_path}")

if __name__ == "__main__":
    # Prioritize the full training corpus if available to match pretrained weights
    corpus_file = "research_round/lumen_training_corpus.txt"
    if not os.path.exists(corpus_file):
        corpus_file = "research_round/lumen_preview_corpus.txt"
    build_lumen_tokenizer(corpus_file)
