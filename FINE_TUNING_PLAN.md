# Fine-Tuning Pipeline Plan

## Overview

Train a small language model to correct typos/bad typing → proper English.

**Goal:** Input messy text → Output clean text (no paraphrasing, no commentary)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FINE-TUNING PIPELINE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ 1. DATA  │ →  │ 2. TRAIN │ →  │ 3. TEST  │ →  │ 4. EXPORT│          │
│  │          │    │          │    │          │    │          │          │
│  │ Create   │    │ Fine-tune│    │ Evaluate │    │ Convert  │          │
│  │ dataset  │    │ on cloud │    │ quality  │    │ to .pte  │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │               │               │               │                 │
│       ▼               ▼               ▼               ▼                 │
│   typo_data.json  model.pt      metrics.json    model.pte              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Dataset Preparation (Local - Free)

### What We Need
- **Input:** Messy typed text (typos, missing letters, jumbled words)
- **Output:** Clean corrected text (exact correction, no paraphrasing)

### Data Sources
1. **Synthetic generation** - Corrupt clean text with realistic typos
2. **C4_200M dataset** - Google's grammar correction pairs
3. **Custom collection** - Your own typing mistakes

### Dataset Format
```json
{
  "input": "hello how are you? ia amfi ne thank you",
  "output": "Hello, how are you? I am fine, thank you."
}
```

### Target Size
- Minimum: 10,000 pairs (basic quality)
- Recommended: 50,000-100,000 pairs (good quality)
- Ideal: 500,000+ pairs (production quality)

---

## Phase 2: Model Training (Cloud - Paid)

### Base Model Options

| Model | Parameters | Training Time | Quality |
|-------|------------|---------------|---------|
| SmolLM2-135M | 135M | ~1 hour | Basic |
| Qwen3-0.6B | 600M | ~2-3 hours | Good |
| Gemma-2B | 2B | ~4-6 hours | Best |

**Recommendation:** Start with **Qwen3-0.6B** (best size/quality ratio)

### Training Method: LoRA (Low-Rank Adaptation)
- Don't retrain entire model (expensive)
- Only train small adapter layers (~1-5% of parameters)
- Much faster and cheaper

---

## Phase 3: Cloud Service Options

### Option A: Google Colab (Cheapest - Recommended to Start)

| Tier | GPU | Cost | Training Time |
|------|-----|------|---------------|
| Free | T4 (15GB) | $0 | ~3-4 hours |
| Pro | A100 (40GB) | $10/month | ~1-2 hours |
| Pro+ | A100 (80GB) | $50/month | <1 hour |

**Pros:** Easy setup, Jupyter notebooks, free tier available
**Cons:** Session timeouts, limited hours

### Option B: RunPod (Best Value)

| GPU | Cost/Hour | VRAM | Training Time |
|-----|-----------|------|---------------|
| RTX 3090 | $0.44 | 24GB | ~2 hours |
| RTX 4090 | $0.69 | 24GB | ~1.5 hours |
| A100 40GB | $1.64 | 40GB | ~1 hour |

**Estimated cost:** $1-3 per training run

**Pros:** Pay per hour, no timeouts, fast GPUs
**Cons:** Need to set up environment

### Option C: Lambda Labs

| GPU | Cost/Hour | VRAM |
|-----|-----------|------|
| A10 | $0.60 | 24GB |
| A100 | $1.10 | 40GB |

**Pros:** Simple pricing, good availability
**Cons:** Slightly more expensive

### Option D: Modal (Serverless - Easiest)

```python
# Just decorate your function
@modal.function(gpu="A100")
def train_model():
    # Training code here
```

**Cost:** ~$1-2 per training run
**Pros:** No setup, pay only for compute, auto-scaling
**Cons:** Learning curve for their API

### Option E: Hugging Face AutoTrain (Easiest - No Code)

**Cost:** ~$5-20 per training run
**Pros:** Upload data, click train, done
**Cons:** Less control, more expensive

---

## Phase 4: Export to Mobile

### Pipeline
```
Fine-tuned Model (PyTorch)
         │
         ▼
    Quantization (INT8/INT4)
         │
         ▼
    ExecuTorch Export (.pte)
         │
         ▼
    Mobile App (Android/iOS)
```

### Tools Required
- `torch` - PyTorch
- `optimum-executorch` - Hugging Face export tool
- `executorch` - Meta's mobile runtime

---

## Recommended Approach

### For Learning/Prototyping
1. **Google Colab Free** - Test the pipeline
2. **Small dataset** (10k pairs)
3. **SmolLM2-135M** - Fastest iteration

### For Production
1. **RunPod or Modal** - Better GPUs, no timeouts
2. **Large dataset** (100k+ pairs)
3. **Qwen3-0.6B** - Best quality/size ratio

---

## Cost Estimate

| Phase | Service | Cost |
|-------|---------|------|
| Dataset | Local/Free | $0 |
| Training (prototype) | Colab Free | $0 |
| Training (production) | RunPod ~2hrs | $1-3 |
| Export | Local | $0 |
| **Total (prototype)** | | **$0** |
| **Total (production)** | | **$1-5** |

---

## Files We'll Create

```
typing-app/
├── FINE_TUNING_PLAN.md          # This file
├── model_test_results.csv        # Test results
├── data/
│   ├── generate_typos.py         # Synthetic data generator
│   ├── train_data.json           # Training dataset
│   └── eval_data.json            # Evaluation dataset
├── training/
│   ├── train.py                  # Training script
│   ├── config.yaml               # Training config
│   └── requirements.txt          # Dependencies
├── export/
│   ├── export_to_pte.py          # ExecuTorch export
│   └── test_model.py             # Test exported model
└── models/
    ├── checkpoint/               # Training checkpoints
    └── typing-corrector.pte      # Final mobile model
```

---

## Next Steps

1. [ ] Choose cloud service (recommend: Colab Free to start)
2. [ ] Create synthetic typo dataset
3. [ ] Write training script
4. [ ] Run training
5. [ ] Evaluate model
6. [ ] Export to .pte
7. [ ] Test on mobile

---

## API Keys / Accounts Needed

| Service | Required | Free Tier |
|---------|----------|-----------|
| Hugging Face | Yes (download models) | ✅ Free |
| Google Colab | Optional (training) | ✅ Free |
| RunPod | Optional (faster training) | ❌ Pay-as-you-go |
| Weights & Biases | Optional (logging) | ✅ Free |

**Minimum to start:** Just a Hugging Face account (free)
