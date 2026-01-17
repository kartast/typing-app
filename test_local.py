"""
Test the fine-tuned model locally on Mac (Apple Silicon).

Usage:
    pip install mlx-lm
    python test_local.py
"""

import subprocess
import sys

# Check if mlx-lm is installed
try:
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler
except ImportError:
    print("Installing mlx-lm...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mlx-lm"])
    from mlx_lm import load, generate
    from mlx_lm.sample_utils import make_sampler


def test_model(model_path: str = "Qwen/Qwen2.5-0.5B-Instruct"):
    """
    Test the model with sample typo inputs.

    Args:
        model_path: HuggingFace model ID or local path
    """
    print(f"Loading model: {model_path}")
    model, tokenizer = load(model_path)

    # Create a low-temperature sampler for more deterministic output
    sampler = make_sampler(temp=0.1)

    test_cases = [
        "hello how are you? ia amfi ne thank you",
        "teh quikc brown fox jumsp over teh lazy dog",
        "i woudl like to schdule a meetign for tomrrow",
        "can yuo plase help me wtih this problme",
        "todya i am goign to teh stoer",
        "wat time is teh meetign?",
        "i realy liek this colour lah",  # Test Singlish preservation
    ]

    print("\n" + "="*60)
    print("TYPO CORRECTION TEST")
    print("="*60 + "\n")

    for text in test_cases:
        prompt = f"""<|im_start|>user
Correct this text: {text}<|im_end|>
<|im_start|>assistant
"""
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=128,
            sampler=sampler,
        )

        # Clean up response
        output = response.strip()
        if "<|im_end|>" in output:
            output = output.split("<|im_end|>")[0].strip()

        print(f"Input:  {text}")
        print(f"Output: {output}")
        print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test typo correction model locally")
    parser.add_argument(
        "--model", "-m",
        default="Qwen/Qwen2.5-0.5B-Instruct",
        help="Model path (HuggingFace ID or local path)"
    )
    args = parser.parse_args()

    test_model(args.model)
