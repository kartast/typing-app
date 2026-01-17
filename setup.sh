#!/bin/bash

echo "=== Setting up Typing App Fine-tuning Environment ==="

# Install dependencies
pip install --upgrade pip
pip install --upgrade "huggingface_hub[cli]"
pip install modal torch transformers datasets peft accelerate

echo ""
echo "=== Now login to Hugging Face ==="
echo "Get your token from: https://huggingface.co/settings/tokens"
echo ""

# Login to Hugging Face
huggingface-cli login

echo ""
echo "=== Verifying setup ==="
echo "Modal:"
modal --version

echo ""
echo "Hugging Face:"
huggingface-cli whoami

echo ""
echo "Python packages:"
python3 -c "import torch, transformers, datasets, peft; print('All packages installed!')"

echo ""
echo "=== Setup complete! ==="
