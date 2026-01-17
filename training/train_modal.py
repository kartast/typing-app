"""
Fine-tuning script for typo correction model.
Runs on Modal with GPU.

Usage:
    modal run training/train_modal.py
"""

import modal
import json
from pathlib import Path

# Define Modal app
app = modal.App("typing-corrector")

# Get local data directory path
DATA_DIR = Path(__file__).parent.parent / "data"

# Define the image with all dependencies + mount local data
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "datasets",
        "peft",
        "accelerate",
        "bitsandbytes",
        "trl==0.15.2",  # Pin version - API changes frequently
        "huggingface_hub",
    )
    .add_local_dir(DATA_DIR, remote_path="/data")
)

# Volume to persist trained model
volume = modal.Volume.from_name("typing-corrector-vol", create_if_missing=True)


@app.function(
    image=image,
    gpu="A10G",  # 24GB VRAM, ~$1/hr
    timeout=3600,  # 1 hour max
    volumes={"/models": volume},
)
def train():
    """Fine-tune a model for typo correction."""
    import torch
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
    )
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from trl import SFTTrainer, SFTConfig
    from datasets import Dataset

    print("=== Starting Training ===\n")

    # Config
    MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"  # Small but capable
    OUTPUT_DIR = "/models/typing-corrector"
    MAX_LENGTH = 256

    # Load training data
    print("Loading data...")
    with open("/data/train_data.json") as f:
        train_data = json.load(f)
    with open("/data/eval_data.json") as f:
        eval_data = json.load(f)

    print(f"Train samples: {len(train_data)}")
    print(f"Eval samples: {len(eval_data)}")

    # Format data for instruction tuning
    def format_sample(sample):
        return {
            "text": f"""<|im_start|>user
Correct this text: {sample['input']}<|im_end|>
<|im_start|>assistant
{sample['output']}<|im_end|>"""
        }

    train_dataset = Dataset.from_list([format_sample(s) for s in train_data])
    eval_dataset = Dataset.from_list([format_sample(s) for s in eval_data])

    print(f"\nSample formatted input:\n{train_dataset[0]['text']}\n")

    # Load tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Quantization config for efficient training
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load model
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    # LoRA config
    lora_config = LoraConfig(
        r=16,  # Rank
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # SFT config (combines TrainingArguments with SFT-specific settings)
    sft_config = SFTConfig(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        gradient_accumulation_steps=2,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_ratio=0.1,
        logging_steps=50,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="steps",
        save_steps=500,
        save_total_limit=2,
        fp16=True,
        report_to="none",
        optim="paged_adamw_8bit",
        max_seq_length=MAX_LENGTH,
        dataset_text_field="text",
    )

    # Trainer
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
    )

    # Train
    print("\n=== Starting Training ===\n")
    trainer.train()

    # Save
    print("\n=== Saving Model ===\n")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    # Commit volume
    volume.commit()

    print(f"\nModel saved to {OUTPUT_DIR}")
    print("Training complete!")

    return {"status": "success", "output_dir": OUTPUT_DIR}


@app.function(
    image=image,
    gpu="A10G",
    timeout=600,
    volumes={"/models": volume},
)
def test_model(test_inputs: list[str] = None):
    """Test the trained model."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    MODEL_DIR = "/models/typing-corrector"
    BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

    if test_inputs is None:
        test_inputs = [
            "hello how are you? ia amfi ne thank you",
            "teh quikc brown fox jumsp over teh lazy dog",
            "i woudl like to schdule a meetign for tomrrow",
            "can yuo plase help me wtih this problme",
            "todya i am goign to teh offcie",
        ]

    print("Loading model...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )

    model = PeftModel.from_pretrained(base_model, MODEL_DIR)
    model.eval()

    print("\n=== Testing Model ===\n")
    results = []

    for text in test_inputs:
        prompt = f"""<|im_start|>user
Correct this text: {text}<|im_end|>
<|im_start|>assistant
"""
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=128,
                temperature=0.1,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        # Only decode the new tokens (exclude prompt)
        new_tokens = outputs[0][input_len:]
        response = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

        print(f"Input:  {text}")
        print(f"Output: {response}")
        print()

        results.append({"input": text, "output": response})

    return results


@app.function(
    image=image,
    volumes={"/models": volume},
)
def download_model():
    """Download the trained model to local machine."""
    import shutil
    import os

    MODEL_DIR = "/models/typing-corrector"

    if not os.path.exists(MODEL_DIR):
        return {"error": "Model not found. Run training first."}

    # List files
    files = os.listdir(MODEL_DIR)
    print(f"Model files: {files}")

    return {"files": files, "path": MODEL_DIR}


@app.local_entrypoint()
def main(action: str = "train"):
    """
    Main entry point.

    Usage:
        modal run training/train_modal.py --action train
        modal run training/train_modal.py --action test
        modal run training/train_modal.py --action download
    """
    if action == "train":
        print("Starting training on Modal...")
        result = train.remote()
        print(f"Result: {result}")

    elif action == "test":
        print("Testing model...")
        results = test_model.remote()
        print(f"Results: {results}")

    elif action == "download":
        print("Downloading model...")
        result = download_model.remote()
        print(f"Result: {result}")

    else:
        print(f"Unknown action: {action}")
        print("Use: train, test, or download")
