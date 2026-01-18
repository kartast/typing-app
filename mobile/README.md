# Typing Corrector Mobile App

React Native (Expo) app that corrects typing errors using on-device AI inference.

## Features

- On-device AI inference (fully offline after model download)
- Quantized ONNX model (473MB INT8)
- Supports regional English variants (US, UK, AU, etc.)
- Real-time typo correction

## Requirements

- Node.js 18+
- Xcode 15+ (for iOS)
- Android Studio (for Android)
- ~500MB storage for the model

## Quick Start

### 1. Install dependencies

```bash
npm install
```

### 2. Download the model

The ONNX model is not bundled with the app due to its size (473MB). You need to place the model files in the app's documents directory.

Model files needed:
- `model_quantized.onnx` (473MB) - from `../onnx_model/`
- `vocab.json` (2.6MB) - from `../onnx_model/`

For development, copy to device using Xcode/Android Studio file browser.

### 3. Build and run

Since this app uses native modules (ONNX Runtime), you cannot use Expo Go. You must build a development client:

```bash
# iOS
npx expo run:ios

# Android
npx expo run:android
```

## Architecture

```
mobile/
├── App.tsx                    # Main app UI
├── services/
│   └── TypingCorrector.ts     # ONNX inference service
├── app.json                   # Expo config
└── assets/                    # App icons
```

## Model Details

| Spec | Value |
|------|-------|
| Base Model | Qwen2.5-0.5B-Instruct |
| Fine-tuning | LoRA (r=16) |
| Export Format | ONNX (INT8 quantized) |
| Model Size | 473 MB |
| Inference Runtime | ONNX Runtime React Native |

## Development Notes

### Why ONNX instead of ExecuTorch?

- ONNX has mature React Native support via `onnxruntime-react-native`
- ExecuTorch is newer and better optimized for mobile but has less tooling
- For production, consider ExecuTorch for better performance

### Model Size Optimization

The current model is 473MB which is large for mobile. Options to reduce:

1. **4-bit quantization** - Can reduce to ~120MB
2. **Smaller model** - TinyLlama or DistilBERT-based approach
3. **Model pruning** - Remove unused weights
4. **On-demand download** - Download model on first launch

### Tokenization

The app includes a simplified BPE tokenizer. For production, consider:
- Using `@huggingface/transformers` with proper tokenizer support
- Pre-computing token mappings for common phrases
- Caching frequently used encodings

## Building for Production

### iOS

```bash
npx expo prebuild --platform ios
cd ios && pod install
# Open in Xcode and archive
```

### Android

```bash
npx expo prebuild --platform android
cd android && ./gradlew assembleRelease
```

## Troubleshooting

### "Model not found" error

Ensure model files are in the app's documents directory:
- iOS: `Documents/models/`
- Android: `files/models/`

### Slow inference

- First inference is slower due to model loading
- Subsequent inferences should be faster
- Consider running on newer devices with Neural Engine (iOS) or NNAPI (Android)

### App crashes on load

- Ensure you're building with native modules, not Expo Go
- Check device has sufficient RAM (2GB+ recommended)

## License

MIT
