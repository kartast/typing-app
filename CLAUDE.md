# Typing Corrector - AI Keyboard App

## Project Overview

Mobile keyboard app that corrects typing errors using on-device AI. Smarter than iOS autocorrect - uses context-aware correction at the passage level.

**Key Features:**
- Fully offline (privacy-focused)
- Passage-level correction (not word-by-word)
- Supports 13 regional English variants
- On-device inference via ONNX Runtime

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      TRAINING PIPELINE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   data/                        training/                     │
│   ├── generate_typos.py        └── train_modal.py           │
│   ├── samples/*.txt               (Modal GPU - A10G)        │
│   ├── train_data.json                                        │
│   └── eval_data.json           Base: Qwen2.5-0.5B-Instruct  │
│                                Fine-tune: LoRA (r=16)        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      EXPORT PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   export/download_and_export.py                              │
│   PyTorch (LoRA merged) → ONNX → INT8 Quantized (473MB)     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      MOBILE APP                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   mobile/                                                    │
│   ├── App.tsx                  # Main UI                    │
│   └── services/                                              │
│       └── TypingCorrector.ts   # ONNX inference             │
│                                                              │
│   Expo + React Native + ONNX Runtime                        │
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
│
├── data/
│   ├── generate_typos.py     # Synthetic typo generator
│   ├── english_variants.py   # Regional spelling support
│   ├── samples/              # LLM-generated clean text
│   ├── train_data.json       # Training data (24,844 pairs)
│   └── eval_data.json        # Evaluation data
│
├── training/
│   └── train_modal.py        # Modal GPU training script
│
├── export/
│   └── download_and_export.py # ONNX export + quantization
│
├── onnx_model/               # Downloaded quantized model
│   ├── model_quantized.onnx  # 473 MB INT8 model
│   ├── vocab.json            # Tokenizer vocabulary
│   └── *.json                # Config files
│
└── mobile/                   # Expo React Native app
    ├── App.tsx               # Main UI
    ├── services/
    │   └── TypingCorrector.ts # Inference service
    └── package.json
```

## Commands

```bash
# Generate training data
./run.sh generate                    # US English (default)
./run.sh generate --variant ALL      # All variants
./run.sh generate --variants-per-sample 3  # Multiple typo variants

# Train on Modal (GPU)
./run.sh train

# Test trained model (on Modal)
./run.sh test

# Export to ONNX with quantization
modal run export/download_and_export.py --action export

# Download model locally
modal run export/download_and_export.py --action download

# Run mobile app (requires native build)
cd mobile && npx expo run:ios
```

## Model Details

| Spec | Value |
|------|-------|
| Base Model | `Qwen/Qwen2.5-0.5B-Instruct` |
| Parameters | 500M total, ~2M trainable (LoRA) |
| Training | LoRA r=16, 3 epochs, loss 0.776 |
| Cloud | Modal (A10G GPU) |
| Export Format | ONNX (INT8 quantized) |
| Model Size | 473 MB |
| Token Accuracy | 86.3% |

## Spelling Variants (13 regions)

| Code | Variant | Regional Features |
|------|---------|-------------------|
| `US` | American | color, organize, center |
| `UK` | British | colour, organise, centre |
| `AU` | Australian | arvo, servo, barbie |
| `NZ` | New Zealand | sweet as, yeah nah |
| `IE` | Irish | grand, fella |
| `SC` | Scottish | aye, braw, wee |
| `SG` | Singapore | lah, leh, lor, meh |
| `MY` | Malaysian | la, -kah, boleh |
| `IN` | Indian | yaar, ji, only |
| `PH` | Filipino | po, ano, naman |
| `HK` | Hong Kong | wor, la, fighting! |
| `NG` | Nigerian | abi, o, sha |
| `ZA` | South African | braai, lekker, now-now |

## Training Data

- 24,844 training pairs
- 988 evaluation pairs
- 3 typo variants per clean sample
- 50,337 clean samples across 13 regions

## Current Status

- [x] Data generation pipeline
- [x] 13 regional variant support
- [x] LLM-generated samples (50,000+)
- [x] Modal training (3 epochs, 86.3% accuracy)
- [x] ONNX export with INT8 quantization
- [x] Expo React Native app scaffold
- [x] ONNX inference service
- [ ] Model bundling/download in app
- [ ] Keyboard extension integration

## Mobile App

### Building

```bash
cd mobile
npm install
npx expo run:ios    # or run:android
```

**Note:** Cannot use Expo Go because onnxruntime-react-native requires native modules.

### Model Loading

The app expects model files in the device's documents folder:
- `Documents/models/model_quantized.onnx` (473 MB)
- `Documents/models/vocab.json` (2.6 MB)

For production, implement model download on first launch.

## Dependencies

**Training (Modal):**
- torch, transformers, datasets
- peft, accelerate, bitsandbytes
- trl==0.15.2

**Export:**
- optimum[onnxruntime]
- onnxruntime, onnx

**Mobile:**
- expo, react-native
- onnxruntime-react-native
- expo-file-system

## Troubleshooting

**Training fails:**
- Check `trl` version is pinned to 0.15.2
- Ensure `train_data.json` exists

**ONNX export fails:**
- Ensure A10G GPU is available
- Check Modal volume has space

**Mobile app crashes:**
- Ensure building with native modules, not Expo Go
- Check device has 2GB+ RAM

**Model too large:**
- Current: 473 MB (INT8 quantized)
- Consider: 4-bit quantization, smaller model, or on-demand download
