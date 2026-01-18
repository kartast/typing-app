"""
Download model from Modal and export to ONNX for React Native.

Usage:
    modal run export/download_and_export.py
"""

import modal
from pathlib import Path

app = modal.App("typing-corrector-export")

# Volume with trained model
volume = modal.Volume.from_name("typing-corrector-vol")

# Image with export dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch",
        "transformers",
        "peft",
        "optimum[onnxruntime]",
        "onnx",
        "onnxruntime",
        "onnxruntime-tools",
    )
)


@app.function(
    image=image,
    gpu="A10G",
    timeout=1800,
    volumes={"/models": volume},
)
def merge_and_export():
    """Merge LoRA with base model and export to ONNX."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    from optimum.onnxruntime import ORTModelForCausalLM
    import os
    import shutil

    MODEL_DIR = "/models/typing-corrector"
    BASE_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
    MERGED_DIR = "/models/typing-corrector-merged"
    ONNX_DIR = "/models/typing-corrector-onnx"

    print("=== Step 1: Loading base model and LoRA adapter ===")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True)

    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )

    # Load and merge LoRA
    print("Loading LoRA adapter...")
    model = PeftModel.from_pretrained(base_model, MODEL_DIR)

    print("=== Step 2: Merging LoRA weights ===")
    model = model.merge_and_unload()

    # Save merged model
    print(f"Saving merged model to {MERGED_DIR}...")
    os.makedirs(MERGED_DIR, exist_ok=True)
    model.save_pretrained(MERGED_DIR)
    tokenizer.save_pretrained(MERGED_DIR)

    print("=== Step 3: Exporting to ONNX ===")
    os.makedirs(ONNX_DIR, exist_ok=True)

    # Export to ONNX using optimum
    ort_model = ORTModelForCausalLM.from_pretrained(
        MERGED_DIR,
        export=True,
        trust_remote_code=True,
    )
    ort_model.save_pretrained(ONNX_DIR)
    tokenizer.save_pretrained(ONNX_DIR)

    print("=== Step 4: Quantizing ONNX model (INT8 dynamic) ===")
    from onnxruntime.quantization import quantize_dynamic, QuantType

    QUANTIZED_DIR = "/models/typing-corrector-onnx-quantized"
    os.makedirs(QUANTIZED_DIR, exist_ok=True)

    # Find the main model file
    onnx_model_path = os.path.join(ONNX_DIR, "model.onnx")
    quantized_model_path = os.path.join(QUANTIZED_DIR, "model_quantized.onnx")

    if os.path.exists(onnx_model_path):
        print(f"Quantizing {onnx_model_path}...")
        quantize_dynamic(
            onnx_model_path,
            quantized_model_path,
            weight_type=QuantType.QUInt8,
        )
        print(f"Quantized model saved to {quantized_model_path}")

        # Copy tokenizer files to quantized dir
        for f in os.listdir(ONNX_DIR):
            if f.endswith('.json') or f == 'tokenizer.model':
                src = os.path.join(ONNX_DIR, f)
                dst = os.path.join(QUANTIZED_DIR, f)
                if os.path.isfile(src):
                    shutil.copy(src, dst)
                    print(f"Copied {f}")

    # Commit volume
    volume.commit()

    # List exported files
    onnx_files = os.listdir(ONNX_DIR)
    quantized_files = os.listdir(QUANTIZED_DIR) if os.path.exists(QUANTIZED_DIR) else []
    print(f"\nONNX files: {onnx_files}")
    print(f"Quantized files: {quantized_files}")

    # Get file sizes
    sizes = {}
    for f in onnx_files:
        path = os.path.join(ONNX_DIR, f)
        if os.path.isfile(path):
            sizes[f] = os.path.getsize(path) / (1024 * 1024)  # MB

    quantized_sizes = {}
    for f in quantized_files:
        path = os.path.join(QUANTIZED_DIR, f)
        if os.path.isfile(path):
            quantized_sizes[f] = os.path.getsize(path) / (1024 * 1024)  # MB

    print("\nOriginal file sizes:")
    for f, size in sizes.items():
        print(f"  {f}: {size:.1f} MB")

    print("\nQuantized file sizes:")
    for f, size in quantized_sizes.items():
        print(f"  {f}: {size:.1f} MB")

    return {
        "status": "success",
        "merged_dir": MERGED_DIR,
        "onnx_dir": ONNX_DIR,
        "quantized_dir": QUANTIZED_DIR,
        "files": onnx_files,
        "quantized_files": quantized_files,
        "sizes": sizes,
        "quantized_sizes": quantized_sizes,
    }


@app.function(
    image=modal.Image.debian_slim(),
    volumes={"/models": volume},
)
def list_files():
    """List all model files in volume."""
    import os

    result = {}
    for dir_name in ["typing-corrector", "typing-corrector-merged", "typing-corrector-onnx", "typing-corrector-onnx-quantized"]:
        dir_path = f"/models/{dir_name}"
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            # Add file sizes
            files_with_sizes = []
            for f in files:
                path = os.path.join(dir_path, f)
                if os.path.isfile(path):
                    size_mb = os.path.getsize(path) / (1024 * 1024)
                    files_with_sizes.append(f"{f} ({size_mb:.1f} MB)")
                else:
                    files_with_sizes.append(f"{f}/")
            result[dir_name] = files_with_sizes
        else:
            result[dir_name] = None

    return result


@app.function(
    image=modal.Image.debian_slim(),
    volumes={"/models": volume},
    timeout=600,
)
def get_onnx_files(quantized: bool = True):
    """Read ONNX files from volume and return them."""
    import os

    if quantized:
        ONNX_DIR = "/models/typing-corrector-onnx-quantized"
    else:
        ONNX_DIR = "/models/typing-corrector-onnx"

    files_data = {}

    if not os.path.exists(ONNX_DIR):
        return {"error": f"Directory not found: {ONNX_DIR}"}

    for filename in os.listdir(ONNX_DIR):
        filepath = os.path.join(ONNX_DIR, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            # Skip files larger than 500MB (too large to transfer via function return)
            if size > 500 * 1024 * 1024:
                print(f"Skipping {filename}: {size / (1024*1024):.1f} MB (too large)")
                files_data[filename] = {"size_mb": size / (1024*1024), "skipped": True}
                continue
            with open(filepath, "rb") as f:
                files_data[filename] = f.read()
            print(f"Read {filename}: {len(files_data[filename])} bytes")

    return files_data


@app.local_entrypoint()
def main(action: str = "export"):
    """
    Main entry point.

    Usage:
        modal run export/download_and_export.py --action export
        modal run export/download_and_export.py --action list
        modal run export/download_and_export.py --action download
    """
    if action == "export":
        print("Merging and exporting model to ONNX...")
        result = merge_and_export.remote()
        print(f"\nResult: {result}")

    elif action == "list":
        print("Listing model files...")
        result = list_files.remote()
        for dir_name, files in result.items():
            print(f"\n{dir_name}:")
            if files:
                for f in files:
                    print(f"  - {f}")
            else:
                print("  (not found)")

    elif action == "download":
        print("Downloading ONNX files from Modal...")
        local_dir = Path("./onnx_model")
        local_dir.mkdir(exist_ok=True)

        files_data = get_onnx_files.remote()

        if "error" in files_data:
            print(f"Error: {files_data['error']}")
            return

        for filename, data in files_data.items():
            filepath = local_dir / filename
            with open(filepath, "wb") as f:
                f.write(data)
            size_mb = len(data) / (1024 * 1024)
            print(f"Saved {filename}: {size_mb:.1f} MB")

        print(f"\nAll files saved to {local_dir.absolute()}")

    else:
        print(f"Unknown action: {action}")
        print("Use: export, list, download")
