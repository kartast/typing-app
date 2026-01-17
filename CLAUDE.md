# Typing Corrector - AI Keyboard App

## Project Overview

Mobile keyboard app that corrects typing errors using on-device AI. Smarter than iOS autocorrect - uses context-aware correction at the passage level.

**Key Features:**
- Fully offline (privacy-focused)
- Passage-level correction (not word-by-word)
- Supports US/UK/AU English spelling variants
- On-device inference via ExecuTorch

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   data/                        training/                     │
│   ├── generate_typos.py        └── train_modal.py           │
│   ├── english_variants.py          (Modal GPU - A10G)       │
│   ├── train_data.json                                        │
│   └── eval_data.json           Base: Qwen2.5-0.5B-Instruct  │
│                                Fine-tune: LoRA (4-bit)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXPORT PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   PyTorch (LoRA merged) → ExecuTorch (.pte) → Mobile App    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
typing-app/
├── CLAUDE.md                 # This file
├── FINE_TUNING_PLAN.md       # Detailed training plan
├── run.sh                    # Main entry point
├── test_local.py             # Test on Mac (mlx-lm)
├── model_test_results.csv    # Ollama baseline tests
│
├── data/
│   ├── generate_typos.py     # Synthetic typo generator
│   ├── english_variants.py   # US/UK/AU spelling support
│   ├── train_data.json       # Training data
│   └── eval_data.json        # Evaluation data
│
└── training/
    └── train_modal.py        # Modal GPU training script
```

## Commands

```bash
# Generate training data
./run.sh generate                    # US English (default)
./run.sh generate --variant UK       # UK English
./run.sh generate --variant ALL      # All variants
./run.sh generate --train-samples 10000

# Train on Modal (GPU)
./run.sh train

# Test trained model (on Modal)
./run.sh test

# Download trained model
./run.sh download

# Test locally on Mac (Apple Silicon)
python test_local.py
```

## Model Details

| Spec | Value |
|------|-------|
| Base Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Parameters | 500M total, ~2M trainable (LoRA) |
| Training | LoRA r=16, 4-bit quantization |
| Cloud | Modal (A10G GPU, ~$1/hr) |
| Target Size | ~300MB quantized |

## Spelling Variants

| Code | Variant | Examples |
|------|---------|----------|
| `US` | American | color, organize, center |
| `UK` | British | colour, organise, centre |
| `AU` | Australian | (same as UK) |

**Note:** Model corrects typos only, not grammar or dialect. Singlish particles ("lah", "meh") and other non-standard English are preserved.

## Training Data Format

```json
{
  "input": "i woudl liek to schdule a meetign",
  "output": "I would like to schedule a meeting",
  "variant": "US"
}
```

Typo types simulated:
- Adjacent key (fat finger) - 35%
- Omission (skipped letter) - 20%
- Insertion (double tap) - 15%
- Transposition (swapped) - 15%
- Substitution - 5%
- Space errors - 5%
- Case errors - 5%

## Prompt Format

```
<|im_start|>user
Correct this text: {typo_text}<|im_end|>
<|im_start|>assistant
{corrected_text}<|im_end|>
```

## Current Status

- [x] Data generation pipeline
- [x] English variant support (US/UK/AU)
- [x] Mobile typo simulation
- [x] Modal training script
- [ ] Training run (in progress)
- [ ] Export to ExecuTorch
- [ ] Mobile app integration

## Next Steps

1. Complete training on Modal
2. Test model quality
3. Export to ExecuTorch (.pte format)
4. Integrate into iOS/Android keyboard

## Dependencies

**Training (Modal):**
- torch, transformers, datasets
- peft, accelerate, bitsandbytes
- trl==0.15.2 (pinned - API changes frequently)

**Local Testing (Mac):**
- mlx-lm (Apple Silicon optimized)

## Troubleshooting

**Modal training fails:**
- Check `trl` version is pinned to 0.15.2
- Ensure `train_data.json` exists in `data/`

**Local test fails:**
- Install mlx-lm: `pip install mlx-lm`
- Requires Apple Silicon Mac

**API changes:**
- Modal: Use `image.add_local_dir()` not `modal.Mount`
- trl: Use `TrainingArguments` + `tokenizer` param (v0.15)
- mlx-lm: Use `sampler=make_sampler(temp=0.1)` not `temperature=`
