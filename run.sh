#!/bin/bash

# Typing Corrector - Fine-tuning Pipeline
# Usage: ./run.sh [command] [options]

set -e

cd "$(dirname "$0")"

# Default variant
VARIANT="${VARIANT:-US}"

case "$1" in
    generate)
        echo "=== Generating Training Data ==="
        shift  # Remove 'generate' from args
        python3 data/generate_typos.py "$@"
        ;;

    train)
        echo "=== Starting Training on Modal ==="
        modal run training/train_modal.py --action train
        ;;

    test)
        echo "=== Testing Model ==="
        modal run training/train_modal.py --action test
        ;;

    download)
        echo "=== Downloading Model ==="
        modal run training/train_modal.py --action download
        ;;

    all)
        echo "=== Running Full Pipeline ==="
        echo ""
        echo "Step 1: Generate data"
        shift  # Remove 'all' from args
        python3 data/generate_typos.py "$@"
        echo ""
        echo "Step 2: Train on Modal"
        modal run training/train_modal.py --action train
        echo ""
        echo "Step 3: Test model"
        modal run training/train_modal.py --action test
        ;;

    *)
        echo "Typing Corrector - Fine-tuning Pipeline"
        echo ""
        echo "Usage: ./run.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  generate  - Generate synthetic training data"
        echo "  train     - Train model on Modal (GPU)"
        echo "  test      - Test the trained model"
        echo "  download  - Download trained model"
        echo "  all       - Run full pipeline"
        echo ""
        echo "Data Generation Options:"
        echo "  --variant, -v     Spelling variant: US, UK, AU, or ALL"
        echo "  --train-samples   Number of training samples (default: 10000)"
        echo "  --eval-samples    Number of eval samples (default: 1000)"
        echo "  --error-rate      Error rate per word (default: 0.22)"
        echo ""
        echo "Spelling Variants:"
        echo "  US  - American (color, organize, center)"
        echo "  UK  - British (colour, organise, centre)"
        echo "  AU  - Australian (same as UK)"
        echo ""
        echo "Examples:"
        echo "  ./run.sh generate                    # US English data"
        echo "  ./run.sh generate --variant UK       # UK English data"
        echo "  ./run.sh generate --variant ALL      # All 3 variants"
        echo "  ./run.sh all --variant UK            # Full pipeline, UK spelling"
        ;;
esac
