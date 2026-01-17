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
- [x] English variant support (US/UK/AU + 10 more regional variants)
- [x] Mobile typo simulation
- [x] Modal training script
- [x] LLM-generated sample data (22,988 samples)
- [ ] Training run (in progress)
- [ ] Export to ExecuTorch
- [ ] Mobile app integration

## Sample Generation with Codex Bridge

### Overview

Samples are generated in two steps:
1. **LLM generates clean text** → realistic sentences in `data/samples/{region}.txt`
2. **Script adds typos** → `generate_typos.py` corrupts text for training pairs

### Regional Sample Files

```
data/samples/
├── us.txt    # American English
├── uk.txt    # British English
├── au.txt    # Australian English
├── sg.txt    # Singapore (Singlish)
├── my.txt    # Malaysian (Manglish)
├── in.txt    # Indian English
├── ph.txt    # Filipino (Taglish)
├── hk.txt    # Hong Kong English
├── ng.txt    # Nigerian English
├── za.txt    # South African English
├── nz.txt    # New Zealand (Kiwi)
├── ie.txt    # Irish English
└── sc.txt    # Scottish English
```

### Using Codex Bridge MCP

Generate samples by calling the `mcp__codex-bridge__consult_codex` tool:

```
Tool: mcp__codex-bridge__consult_codex
Parameters:
  query: "Append 300 Singlish texts to data/samples/sg.txt
          One per line. Use particles lah, leh, lor, meh, sia.
          No code, just 300 lines."
  directory: "/path/to/typing-app"
  format: "text"
  timeout: 240
```

**Key prompt patterns:**
- Always say "Append" not "Write" (preserves existing data)
- Specify "One per line" and "No code"
- Include regional expressions/particles for authenticity
- Keep batch size 200-300 lines (larger batches may timeout)

**Run multiple regions in parallel** for efficiency:
```
# Call codex bridge for SG, MY, IN, PH simultaneously
# Each with 300 lines, timeout 240s
```

### Checking Progress

```bash
# Count samples per region
wc -l data/samples/*.txt

# View total
wc -l data/samples/*.txt | tail -1
```

### How Many Samples?

| Sample Count | Quality | Use Case |
|--------------|---------|----------|
| 1,000 | Proof of concept | Testing pipeline works |
| 10,000 | Functional | Basic typo correction |
| 25,000 | Good | Handles common cases well |
| **50,000** | **Production** | **Recommended minimum** |
| 100,000+ | Excellent | Robust edge case handling |

**Target: ~3,850 samples per region × 13 regions = 50,000 total**

**Current: 22,988 samples** (need ~27,000 more for production)

### Rate Limits

Codex has usage limits. When hit:
- Error: `usage_limit_reached`
- Message shows reset time (e.g., "try again at 9:10 PM")
- Wait for reset, then resume generation

### Workflow

1. Check current counts: `wc -l data/samples/*.txt`
2. Identify regions needing more samples
3. Run parallel Codex calls (200-300 lines each)
4. Repeat until rate limit or target reached
5. Commit progress: `git add data/samples && git commit`

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
