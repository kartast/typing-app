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

### Prerequisites

- Node.js 18+
- EAS CLI: `npm install -g eas-cli`
- Expo account: `eas login`
- Apple Developer account (for device builds)

### Step 1: Download ONNX Model

First, download the quantized model from Modal:

```bash
# Export and quantize model (if not done already)
modal run export/download_and_export.py --action export

# Download to local onnx_model/ folder
modal run export/download_and_export.py --action download
```

This creates `onnx_model/` with:
- `model_quantized.onnx` (473 MB)
- `vocab.json` (2.6 MB)
- Config files

### Step 2: Build with EAS Cloud

**Cannot use Expo Go** - the app requires native ONNX Runtime modules.

```bash
cd mobile
npm install

# For iOS Simulator (no Apple credentials needed)
eas build --platform ios --profile simulator

# For iOS Device (requires Apple Developer account)
eas build --platform ios --profile development
```

The device build will prompt you to:
1. Sign in to Apple Developer account
2. Create provisioning profile
3. Register test devices

### Step 3: Install on Device

**Option A: QR Code (easiest)**
1. Open the EAS build URL from the terminal output
2. Scan QR code with your iPhone camera
3. Follow prompts to install

**Option B: CLI**
```bash
# List recent builds
eas build:list

# Install latest build
eas build:run -p ios
```

**Option C: Manual**
1. Download `.ipa` from EAS dashboard
2. Use Apple Configurator or Xcode Devices to install

### Step 4: Copy Model to Device

The app looks for model files in the app's Documents folder. Use one of these methods:

**Option A: Finder (macOS Ventura+)**
1. Connect iPhone to Mac
2. Open Finder → iPhone → Files
3. Find "Typing Corrector" app
4. Create `models/` folder
5. Copy `model_quantized.onnx` and `vocab.json`

**Option B: Xcode**
1. Open Xcode → Window → Devices and Simulators
2. Select your iPhone
3. Find "Typing Corrector" in Installed Apps
4. Click gear icon → Download Container
5. Add files to `AppData/Documents/models/`
6. Click gear icon → Replace Container

**Option C: iTunes File Sharing (if enabled)**
1. Connect iPhone to Mac
2. Open Finder → iPhone → Files tab
3. Drag model files to app's folder

### Step 5: Run the App

1. Open "Typing Corrector" on your iPhone
2. Wait for "Model ready!" status
3. Type text with typos in the input box
4. Tap "Correct" to see AI-corrected output

### EAS Build Profiles

| Profile | Command | Use Case |
|---------|---------|----------|
| `simulator` | `eas build -p ios --profile simulator` | iOS Simulator testing |
| `development` | `eas build -p ios --profile development` | Real device testing |
| `preview` | `eas build -p ios --profile preview` | Internal distribution |
| `production` | `eas build -p ios --profile production` | App Store |

### Local Build (Alternative)

If you prefer local builds instead of EAS cloud:

```bash
cd mobile

# Generate native projects
npx expo prebuild

# Build with Xcode
cd ios && pod install
open TypingCorrector.xcworkspace
# Build and run from Xcode
```

### Model File Locations

| Platform | Path |
|----------|------|
| iOS Device | `<App>/Documents/models/` |
| iOS Simulator | `~/Library/Developer/CoreSimulator/.../Documents/models/` |
| Android | `/data/data/com.typingcorrector.app/files/models/` |

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
