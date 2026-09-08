#!/usr/bin/env python3
"""
LoRA SFT for the synthetic pediatric triage model.
Targets Qwen2.5-0.5B-Instruct (or any similar chat model).
"""

import torch
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
DATASET_PATH = "data/synthetic_triage_chat.jsonl"
OUTPUT_DIR = "adapters/triage-lora-0.5b"
MAX_SEQ_LENGTH = 768
NUM_EPOCHS = 3
BATCH_SIZE = 4
GRAD_ACCUM = 4
LR = 2e-4
LORA_R = 16
LORA_ALPHA = 32

# ------------------------------------------------------------------
# Custom Data Collator for Completion-Only Loss (unstable in TRL)
# ------------------------------------------------------------------
class CustomCompletionOnlyCollator:
    def __init__(self, tokenizer, response_template):
        self.tokenizer = tokenizer
        self.response_template = response_template

    def __call__(self, features):
        # Filter out non-tokenized keys (like "messages") to avoid padding crashes
        clean_features = []
        for feature in features:
            clean_feature = {
                k: feature[k] for k in ["input_ids", "attention_mask"] if k in feature
            }
            clean_features.append(clean_feature)

        batch = self.tokenizer.pad(
            clean_features,
            padding=True,
            return_tensors="pt",
        )
        labels = batch["input_ids"].clone()
        
        # We find the response template token IDs in each sequence
        response_token_ids = self.tokenizer.encode(self.response_template, add_special_tokens=False)
        
        for i in range(len(features)):
            input_ids = batch["input_ids"][i].tolist()
            # Find the position where the response starts
            response_start_idx = -1
            for j in range(len(input_ids) - len(response_token_ids) + 1):
                if input_ids[j : j + len(response_token_ids)] == response_token_ids:
                    response_start_idx = j + len(response_token_ids)
                    break
            
            if response_start_idx != -1:
                # Mask all tokens before response_start_idx by setting label to -100
                labels[i, :response_start_idx] = -100
            else:
                # If template is not found, mask the entire sequence
                labels[i, :] = -100
                
        # Mask padding tokens
        if self.tokenizer.pad_token_id is not None:
            labels[batch["input_ids"] == self.tokenizer.pad_token_id] = -100
            
        batch["labels"] = labels
        return batch

def main():
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Check CUDA availability
    if torch.cuda.is_available():
        print("CUDA detected! Loading model in 4-bit quantization...")
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
        )
        model = prepare_model_for_kbit_training(model)
        bf16_val = True
        optim_val = "paged_adamw_8bit"
    else:
        print("CUDA not available. Loading model on CPU in standard Float32...")
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            device_map="cpu",
            trust_remote_code=True,
            torch_dtype=torch.float32,
        )
        bf16_val = False
        optim_val = "adamw_torch"

    # LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"], # Qwen-style
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # Dataset
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")
    dataset = dataset.train_test_split(test_size=0.08, seed=42)
    train_ds = dataset["train"]
    eval_ds = dataset["test"]

    # Use our bulletproof custom completion-only collator
    response_template = "<|im_start|>assistant\n" # Qwen chat template marker
    collator = CustomCompletionOnlyCollator(
        tokenizer=tokenizer,
        response_template=response_template,
    )

    # Use SFTConfig instead of TrainingArguments (new in TRL 1.x)
    training_args = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=LR,
        lr_scheduler_type="cosine",
        warmup_steps=10,
        logging_steps=10,
        save_strategy="epoch",
        eval_strategy="epoch",
        bf16=bf16_val,
        optim=optim_val,
        report_to="none",
        remove_unused_columns=False,
        max_length=MAX_SEQ_LENGTH, # SFTConfig max length
    )

    def formatting_func(example):
        # Convert messages list → single string via chat template
        return tokenizer.apply_chat_template(
            example["messages"],
            tokenize=False,
            add_generation_prompt=False,
        )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        formatting_func=formatting_func,
        data_collator=collator,
        processing_class=tokenizer, # pass as processing_class in TRL 1.x
    )

    trainer.train()
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Adapter saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
