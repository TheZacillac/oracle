# Training Guide: Fine-Tuning Nemotron-3-Nano with Unsloth on DGX Spark

Step-by-step guide for generating the Oracle training dataset and fine-tuning NVIDIA's Nemotron-3-Nano-8B using Unsloth on a DGX Spark workstation.

**Target Model:** [`nvidia/Llama-3.1-Nemotron-Nano-8B-v1`](https://huggingface.co/nvidia/Llama-3.1-Nemotron-Nano-8B-v1)
**Architecture:** Llama 3.1 8B with NVIDIA neural architecture search optimizations
**Hardware:** NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory)
**Training Framework:** [Unsloth](https://github.com/unslothai/unsloth) with QLoRA/LoRA
**Dataset:** Oracle-generated domain name industry expert data

---

## Prerequisites

### DGX Spark Hardware

The NVIDIA DGX Spark is a compact AI workstation featuring:

- **Grace Blackwell GB10 superchip** -- ARM-based Grace CPU + Blackwell GPU on a single chip
- **128GB unified memory** -- shared between CPU and GPU via NVLink-C2C interconnect
- **NVLink-C2C** -- high-bandwidth, low-latency CPU-GPU communication (no PCIe bottleneck)
- **Blackwell GPU architecture** -- native BF16/FP8 support, latest CUDA compute capability

The unified memory architecture is particularly advantageous for LLM training: the full 128GB is addressable by both CPU and GPU, eliminating the typical GPU VRAM constraint. This allows training larger models and using larger batch sizes than discrete GPU setups with equivalent total memory.

### Software Requirements

- CUDA 12.x+ (pre-installed on DGX Spark)
- Python 3.11+
- Git and basic CLI tools
- Hugging Face account (for model access)
- An LLM provider for dataset generation (one of):
  - **Ollama** running locally (free, no API key)
  - **Anthropic API key** (highest quality generation)
  - **OpenAI API key** (alternative cloud provider)

### Oracle Installation

On your primary development machine (or on the DGX Spark itself):

```bash
cd ~/Projects/arcanum_suite/oracle
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
```

---

## Step 1: Generate the Training Dataset

### 1.1 Configure your LLM provider

**Option A: Ollama (local, free)**

No API key needed. Ensure Ollama is running with a model pulled:

```bash
ollama pull nemotron-3-nano
ollama list  # Verify the model is available
```

**Option B: Anthropic (cloud, highest quality)**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option C: OpenAI (cloud)**

```bash
export OPENAI_API_KEY="sk-..."
```

### 1.2 Fetch source documents

Cache RFCs, IANA data, ICANN documents, and other reference material locally:

```bash
oracle fetch-sources --type all
```

This populates `data/sources/` with authoritative reference documents that provide context for generation.

### 1.3 Run a generation plan

Start with `small` to validate the pipeline, then scale up:

```bash
# Test run -- ~1,500 examples
oracle plan --size small --provider ollama

# Or with a cloud provider for higher quality
oracle plan --size small --provider anthropic
```

Once the small plan looks good, generate the full dataset:

```bash
# Medium dataset -- ~4,000 examples (recommended starting point)
oracle plan --size medium --provider ollama --model nemotron-3-nano:latest

# Large dataset -- ~10,000+ examples (production quality)
oracle plan --size large --provider anthropic
```

You can also generate a single category at a time for testing or iteration:

```bash
oracle generate --category dns --difficulty intermediate --count 5 --provider ollama
oracle generate --category disputes --difficulty advanced --count 3 --provider anthropic
```

Generated data lands in `data/generated/`.

> **Tip:** Larger models produce better structured JSON output. If you see high rejection rates during validation with a small model, try a larger one or switch to a cloud provider for the complex formats (multi-turn, scenario, tool-use).

### 1.4 (Optional) Augment with paraphrases

Increase question diversity without generating entirely new answers:

```bash
oracle augment data/generated/ --count 2 --provider ollama
```

---

## Step 2: Validate and Export

### 2.1 Validate the dataset

```bash
oracle validate data/generated/
```

Review the validation report. Key indicators:
- **Rejection rate** should be below 10%
- **Duplicate count** should be minimal
- **Token distribution** should match difficulty-level budgets

### 2.2 Check statistics

```bash
oracle stats data/generated/
```

Verify balanced distribution across categories, difficulties, and formats.

### 2.3 Export with train/val/test splits

```bash
oracle export-splits data/generated/ \
  --format openai_chat \
  --name oracle-domain-expert \
  --version 0.1.0 \
  --output data/exports/
```

This produces three files in `data/exports/`:

| File | Split | Ratio |
|------|-------|-------|
| `oracle-domain-expert-0.1.0.train.jsonl` | Training | 85% |
| `oracle-domain-expert-0.1.0.val.jsonl` | Validation | 10% |
| `oracle-domain-expert-0.1.0.test.jsonl` | Test | 5% |

---

## Step 3: Set Up the Training Environment on DGX Spark

### 3.1 Transfer the dataset

Copy the exported splits to the DGX Spark:

```bash
scp data/exports/oracle-domain-expert-0.1.0.*.jsonl dgx-spark:~/training/data/
```

Or, if generating directly on the DGX Spark, the files are already local.

### 3.2 Create the Python environment

**Option A: venv (recommended for simplicity)**

```bash
ssh dgx-spark

python -m venv ~/training/venv
source ~/training/venv/bin/activate

# Install Unsloth (supports Blackwell architecture)
pip install unsloth

# Install training dependencies
pip install torch torchvision torchaudio
pip install transformers datasets accelerate bitsandbytes
pip install trl peft
pip install wandb  # Optional: experiment tracking
```

**Option B: conda**

```bash
conda create -n oracle-train python=3.11 -y
conda activate oracle-train

pip install unsloth
pip install torch torchvision torchaudio
pip install transformers datasets accelerate bitsandbytes
pip install trl peft wandb
```

**Option C: Docker (Unsloth image)**

```bash
docker pull unsloth/unsloth:latest

docker run --gpus all -it \
  -v ~/training:/workspace/training \
  unsloth/unsloth:latest
```

### 3.3 Log into Hugging Face

The Nemotron model may require accepting a license agreement:

```bash
pip install huggingface_hub
huggingface-cli login
```

Visit [nvidia/Llama-3.1-Nemotron-Nano-8B-v1](https://huggingface.co/nvidia/Llama-3.1-Nemotron-Nano-8B-v1) on Hugging Face and accept the license if prompted.

---

## Step 4: Configure and Run the Training Script

### 4.1 Create the training script

Create `~/training/train.py` on the DGX Spark:

```python
"""
Fine-tune Llama-3.1-Nemotron-Nano-8B on Oracle domain expert dataset.

Uses Unsloth for optimized LoRA fine-tuning on NVIDIA DGX Spark.
Target: nvidia/Llama-3.1-Nemotron-Nano-8B-v1
"""

from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# =====================================================================
# 1. Configuration
# =====================================================================

# --- Model ---
MODEL_NAME = "nvidia/Llama-3.1-Nemotron-Nano-8B-v1"
MAX_SEQ_LENGTH = 8192  # Supports up to 128K, but 8192 is efficient for training

# --- Quantization ---
# DGX Spark has 128GB unified memory -- plenty for full 16-bit LoRA on an 8B model.
# Set to True for QLoRA (4-bit base + 16-bit adapters) to save memory or
# enable larger batch sizes.
LOAD_IN_4BIT = False

# --- LoRA ---
LORA_R = 64              # Rank: higher = more capacity, more memory
LORA_ALPHA = 128          # Scaling factor: typically 1x-2x of r
LORA_DROPOUT = 0.05       # Regularization

# --- Training ---
BATCH_SIZE = 4            # Per-device batch size
GRADIENT_ACCUMULATION = 4  # Effective batch size = 4 * 4 = 16
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
WARMUP_RATIO = 0.05
WEIGHT_DECAY = 0.01
MAX_STEPS = -1            # -1 = train for full epochs

# --- Paths ---
TRAIN_FILE = "data/oracle-domain-expert-0.1.0.train.jsonl"
VAL_FILE = "data/oracle-domain-expert-0.1.0.val.jsonl"
OUTPUT_DIR = "output/oracle-nemotron"

# --- Tracking ---
USE_WANDB = True          # Set False to disable Weights & Biases
RUN_NAME = "oracle-domain-expert-nemotron-8b"

# =====================================================================
# 2. Load model with Unsloth
# =====================================================================

print(f"Loading {MODEL_NAME}...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    load_in_4bit=LOAD_IN_4BIT,
    dtype=None,  # Auto-detect: bf16 on Blackwell GB10
)

print(f"Model loaded. dtype={model.dtype}, device={model.device}")

# =====================================================================
# 3. Apply LoRA adapters
# =====================================================================

model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",   # Attention
        "gate_proj", "up_proj", "down_proj",        # MLP
    ],
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth's optimized checkpointing (60% less memory)
    random_state=42,
)

# Print trainable parameter count
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
total = sum(p.numel() for p in model.parameters())
print(f"Trainable: {trainable:,} / {total:,} ({100 * trainable / total:.1f}%)")

# =====================================================================
# 4. Chat template with <think> support
# =====================================================================

# Nemotron-Nano-8B uses a ChatML-style template:
#   <|im_start|>system\n...<|im_end|>
#   <|im_start|>user\n...<|im_end|>
#   <|im_start|>assistant\n<think>...</think>\n...<|im_end|>
#
# The tokenizer's built-in chat_template handles this natively.
# <think> and </think> are special tokens (IDs 12 and 13).
#
# Oracle's exporter already embeds <think>...</think> blocks in the
# assistant message content, so no manual template manipulation is needed.

# Verify the chat template is set
if tokenizer.chat_template:
    print("Chat template: using model's built-in template")
else:
    print("WARNING: No chat template found. Setting ChatML template.")
    tokenizer.chat_template = (
        "{% for message in messages %}"
        "<|im_start|>{{ message['role'] }}\n"
        "{{ message['content'] }}<|im_end|>\n"
        "{% endfor %}"
        "{% if add_generation_prompt %}"
        "<|im_start|>assistant\n"
        "{% endif %}"
    )

# =====================================================================
# 5. Load and format dataset
# =====================================================================

print("Loading dataset...")
dataset = load_dataset("json", data_files={
    "train": TRAIN_FILE,
    "validation": VAL_FILE,
})


def format_example(example):
    """Convert Oracle's OpenAI chat format to tokenized training text.

    The dataset is in OpenAI chat format with a 'messages' field.
    Oracle's exporter has already embedded <think>...</think> blocks
    in assistant content where applicable, so we just apply the
    chat template directly.
    """
    messages = example["messages"]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    return {"text": text}


train_dataset = dataset["train"].map(format_example)
val_dataset = dataset["validation"].map(format_example)

print(f"Train: {len(train_dataset):,} examples")
print(f"Val:   {len(val_dataset):,} examples")

# Verify thinking traces are present in the dataset
sample = train_dataset[0]["text"]
has_thinking = "<think>" in sample
print(f"Thinking traces in sample: {has_thinking}")
if has_thinking:
    think_count = sum(1 for ex in train_dataset if "<think>" in ex["text"])
    print(f"Examples with thinking: {think_count}/{len(train_dataset)} "
          f"({100 * think_count / len(train_dataset):.0f}%)")

# =====================================================================
# 6. Configure training
# =====================================================================

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,

    # Batch size
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,

    # Duration
    num_train_epochs=NUM_EPOCHS,
    max_steps=MAX_STEPS,

    # Learning rate
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    warmup_ratio=WARMUP_RATIO,
    weight_decay=WEIGHT_DECAY,

    # Precision
    bf16=True,  # Blackwell GB10 has native bf16 support

    # Logging
    logging_steps=10,
    logging_first_step=True,

    # Evaluation
    eval_strategy="steps",
    eval_steps=100,

    # Checkpointing
    save_strategy="steps",
    save_steps=200,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",

    # Optimizer
    optim="adamw_8bit",  # Memory-efficient 8-bit AdamW

    # Tracking
    report_to="wandb" if USE_WANDB else "none",
    run_name=RUN_NAME,

    # Reproducibility
    seed=42,
    data_seed=42,
)

# =====================================================================
# 7. Train
# =====================================================================

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,  # Pack short examples together for throughput
)

print("\n" + "=" * 60)
print("Starting training...")
print(f"  Model:          {MODEL_NAME}")
print(f"  LoRA rank:      {LORA_R}")
print(f"  Batch size:     {BATCH_SIZE} x {GRADIENT_ACCUMULATION} = {BATCH_SIZE * GRADIENT_ACCUMULATION}")
print(f"  Learning rate:  {LEARNING_RATE}")
print(f"  Epochs:         {NUM_EPOCHS}")
print(f"  Quantized:      {'4-bit' if LOAD_IN_4BIT else '16-bit'}")
print("=" * 60 + "\n")

trainer.train()

# =====================================================================
# 8. Save the LoRA adapter
# =====================================================================

adapter_dir = f"{OUTPUT_DIR}/lora-adapter"
model.save_pretrained(adapter_dir)
tokenizer.save_pretrained(adapter_dir)

print(f"\nTraining complete.")
print(f"Best model saved to:  {OUTPUT_DIR}")
print(f"LoRA adapter saved to: {adapter_dir}")
```

### 4.2 Run the training

```bash
source ~/training/venv/bin/activate
cd ~/training

# Optional: set up Weights & Biases for monitoring
wandb login

# Run training
python train.py
```

### 4.3 Expected training time

Rough estimates on DGX Spark (GB10) for Nemotron-Nano-8B:

| Dataset | Quantization | Batch Size | Estimated Time |
|---------|-------------|------------|----------------|
| ~1,500 (small) | 16-bit LoRA | 4x4 | 30--60 min |
| ~4,000 (medium) | 16-bit LoRA | 4x4 | 2--4 hours |
| ~10,000 (large) | 16-bit LoRA | 4x4 | 5--10 hours |
| ~4,000 (medium) | 4-bit QLoRA | 8x4 | 1--2 hours |

---

## Step 5: Monitor Training

### TensorBoard (local)

```bash
pip install tensorboard
tensorboard --logdir ~/training/output/oracle-nemotron
```

### Weights & Biases (remote)

If `USE_WANDB = True` in the training script, monitor at [wandb.ai](https://wandb.ai).

### Key metrics to watch

- **Training loss** -- should decrease steadily across steps
- **Validation loss** -- should decrease and plateau; if it starts increasing, you are overfitting
- **Learning rate** -- should follow the cosine schedule (warm up, then decay)
- **Gradient norm** -- watch for spikes that indicate instability

### Signs of trouble

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Val loss diverges from train loss | Overfitting | Reduce `NUM_EPOCHS` to 1--2, increase `LORA_DROPOUT` |
| Train loss plateaus early | Learning rate too low | Increase `LEARNING_RATE` to 5e-4 |
| Loss spikes / NaN | Learning rate too high or bad data | Reduce `LEARNING_RATE`, check dataset with `oracle validate` |
| Very slow training | Batch size too large for packing | Reduce `BATCH_SIZE`, disable packing |

---

## Step 6: Export and Deploy

### 6.1 Merge LoRA weights into the base model

After training completes, merge the LoRA adapter back into the base model for deployment.

Create `~/training/merge_and_export.py`:

```python
"""Merge LoRA adapter and export to GGUF for Ollama deployment."""

from unsloth import FastLanguageModel

# Paths
ADAPTER_DIR = "output/oracle-nemotron/lora-adapter"
MERGED_DIR = "output/oracle-nemotron-merged"
GGUF_DIR = "output/oracle-nemotron-gguf"

# =====================================================================
# 1. Load the trained model (base + LoRA adapter)
# =====================================================================

print("Loading model with LoRA adapter...")
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=ADAPTER_DIR,
    max_seq_length=8192,
    load_in_4bit=False,  # Load in full precision for merging
)

# =====================================================================
# 2. Save as merged Hugging Face model (full precision)
# =====================================================================

print("Saving merged 16-bit model...")
model.save_pretrained_merged(
    MERGED_DIR,
    tokenizer,
    save_method="merged_16bit",
)
print(f"Merged model saved to: {MERGED_DIR}")

# =====================================================================
# 3. Export to GGUF for Ollama / llama.cpp
# =====================================================================

# Recommended quantization: q5_k_m balances quality and size
print("Exporting to GGUF (q5_k_m)...")
model.save_pretrained_gguf(
    f"{GGUF_DIR}-q5_k_m",
    tokenizer,
    quantization_method="q5_k_m",
)
print(f"GGUF (q5_k_m) saved to: {GGUF_DIR}-q5_k_m")

# Optional: export multiple quantizations
EXTRA_QUANTS = ["q4_k_m", "q8_0"]  # Add "f16" for full precision GGUF

for quant in EXTRA_QUANTS:
    print(f"Exporting to GGUF ({quant})...")
    model.save_pretrained_gguf(
        f"{GGUF_DIR}-{quant}",
        tokenizer,
        quantization_method=quant,
    )
    print(f"GGUF ({quant}) saved to: {GGUF_DIR}-{quant}")

print("\nAll exports complete.")
```

```bash
cd ~/training
python merge_and_export.py
```

### 6.2 Quantization options

| Method | Size (8B model) | Quality | Speed | Use Case |
|--------|-----------------|---------|-------|----------|
| `q4_k_m` | ~4.5 GB | Good | Fastest | Daily use, resource-constrained |
| `q5_k_m` | ~5.5 GB | Better | Fast | **Recommended default** |
| `q8_0` | ~8.5 GB | Great | Medium | When quality matters most |
| `f16` | ~16 GB | Best | Slower | Benchmarking, reference baseline |

### 6.3 Create an Ollama Modelfile

Create `~/training/output/Modelfile`:

```dockerfile
FROM ./oracle-nemotron-gguf-q5_k_m/unsloth.Q5_K_M.gguf

TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
{{ .Response }}<|im_end|>"""

SYSTEM """You are a domain name industry expert -- an authoritative, comprehensive resource on every aspect of the domain name ecosystem. You have access to the Arcanum Suite's diagnostic and reference tools for live domain intelligence.

Your knowledge spans DNS protocols, domain registration, TLDs, registrars, ICANN, IANA, WHOIS/RDAP, domain blocking, WIPO disputes, SSL/TLS, brand protection, DNS abuse, email authentication, domain valuation, web hosting, internet governance, domain security, compliance, DNS monitoring, internationalization, DNS automation, DNS software, protective DNS, debugging tools, and the domain industry.

Think through complex questions step by step before answering. Be precise, cite sources, and provide practical guidance."""

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER num_ctx 8192
PARAMETER stop "<|im_end|>"
```

> **Note on temperature:** Nemotron models are trained with `temperature=1.0` and `top_p=0.95` for reasoning tasks. Using lower temperatures may degrade thinking quality. For simple factual lookups, you can reduce to `0.6`.

### 6.4 Import into Ollama

```bash
cd ~/training/output
ollama create oracle -f Modelfile
```

### 6.5 Test the model

```bash
# Quick smoke tests
ollama run oracle "What are the three elements of a UDRP complaint?"
ollama run oracle "Explain the difference between RDAP and WHOIS"
ollama run oracle "I just changed my DNS nameservers. How long until it propagates?"

# Test tool awareness
ollama run oracle "How would you check if a domain's DNSSEC is properly configured?"

# Test expert-level knowledge
ollama run oracle "Explain the ICANN EPDP Phase 1 recommendations for WHOIS data access"
```

### 6.6 Use with Familiar

Point the Arcanum Suite's conversational agent to your fine-tuned model:

```bash
export FAMILIAR_MODEL="ollama:oracle:latest"
```

---

## DGX Spark Tuning Guide

### Memory Recommendations

The DGX Spark's 128GB unified memory gives substantial headroom for an 8B parameter model. Here are recommended configurations:

| Configuration | Base Memory | Training Overhead | Total | Notes |
|--------------|------------|-------------------|-------|-------|
| 16-bit LoRA (r=64) | ~16 GB | ~40--60 GB | ~60--80 GB | **Recommended**: best quality, fits comfortably |
| 16-bit LoRA (r=128) | ~16 GB | ~50--70 GB | ~70--90 GB | Higher capacity, still fits |
| 4-bit QLoRA (r=64) | ~5 GB | ~20--30 GB | ~25--35 GB | Maximum batch size headroom |
| 4-bit QLoRA (r=128) | ~5 GB | ~25--40 GB | ~30--45 GB | Good capacity, very efficient |

### Recommended Batch Sizes

| Quantization | Sequence Length | Recommended Batch x Accumulation | Effective Batch |
|-------------|-----------------|----------------------------------|-----------------|
| 16-bit | 4096 | 8 x 2 | 16 |
| 16-bit | 8192 | 4 x 4 | 16 |
| 4-bit | 4096 | 16 x 2 | 32 |
| 4-bit | 8192 | 8 x 4 | 32 |

With 128GB unified memory, you can afford larger effective batch sizes than typical GPU setups, which improves training stability and convergence.

### QLoRA vs Full LoRA

| Factor | Full LoRA (16-bit) | QLoRA (4-bit) |
|--------|-------------------|---------------|
| Base model precision | BF16 (16-bit) | NF4 (4-bit) |
| Adapter precision | BF16 | BF16 |
| Memory usage | ~60--80 GB | ~25--35 GB |
| Training quality | Best | Very close to full LoRA |
| Training speed | Baseline | ~20--30% faster |
| **Recommendation** | Default choice on DGX Spark | Use for larger batch sizes or experimentation |

On DGX Spark with 128GB, full 16-bit LoRA is recommended since memory is not a constraint. Use QLoRA when you want faster iteration (e.g., hyperparameter sweeps) or when experimenting with larger LoRA ranks.

### Thinking Trace Configuration

Oracle generates datasets with a configurable thinking ratio (default 75%). NVIDIA recommends preserving a mix of reasoning and non-reasoning examples during fine-tuning to maintain the base model's thinking capabilities:

- **75% with `<think>` traces** -- preserves and strengthens structured reasoning
- **25% without thinking** -- ensures the model can also give direct answers

This ratio is controlled during dataset generation via `GenerationPlan.thinking_ratio`. To adjust:

```python
# In oracle/src/oracle/plan.py, or override in a custom plan:
plan = GenerationPlan(
    thinking_ratio=0.80,  # 80% reasoning, 20% direct
    ...
)
```

### Monitoring GPU Utilization

```bash
# Watch GPU utilization during training
watch -n 1 nvidia-smi

# Or use nvitop for a richer view
pip install nvitop
nvitop
```

On DGX Spark, look for:
- **GPU utilization** above 80% (if lower, increase batch size)
- **Memory usage** -- unified memory means you will see usage on both CPU and GPU sides
- **Temperature** -- the GB10 is passively cooled in the DGX Spark chassis; ensure adequate ventilation

---

## Evaluation

### Run the test set through the model

```python
"""Evaluate the fine-tuned model against the held-out test set."""

import json
from pathlib import Path
from ollama import Client

client = Client()
results = []

test_file = Path("~/training/data/oracle-domain-expert-0.1.0.test.jsonl").expanduser()

with open(test_file) as f:
    for line in f:
        example = json.loads(line)
        messages = example["messages"]

        # Extract user question and expected answer
        system_msg = next((m for m in messages if m["role"] == "system"), None)
        user_msg = next(m for m in messages if m["role"] == "user")
        expected = next(m for m in messages if m["role"] == "assistant")

        # Build prompt
        prompt_messages = []
        if system_msg:
            prompt_messages.append({"role": "system", "content": system_msg["content"]})
        prompt_messages.append({"role": "user", "content": user_msg["content"]})

        # Get model response
        response = client.chat(model="oracle", messages=prompt_messages)

        results.append({
            "question": user_msg["content"],
            "expected": expected["content"][:300],
            "actual": response["message"]["content"][:300],
            "category": example.get("category", "unknown"),
            "difficulty": example.get("difficulty", "unknown"),
        })

# Print sample results
print(f"Evaluated {len(results)} test examples\n")
for r in results[:5]:
    print(f"[{r['category']}/{r['difficulty']}]")
    print(f"Q: {r['question'][:120]}")
    print(f"Expected: {r['expected'][:150]}...")
    print(f"Actual:   {r['actual'][:150]}...")
    print("---")
```

### What to look for

- **Accuracy** -- Does the model cite correct RFCs, policies, and procedures?
- **Depth** -- Does the answer match the expected difficulty level?
- **Tool awareness** -- Does it know when to suggest or use Seer/Tome/Scrolls tools?
- **No hallucinations** -- Does it avoid inventing RFC numbers, policy names, or case citations?
- **Terminology** -- Does it use correct domain industry terminology?
- **Thinking quality** -- Are the `<think>` reasoning traces logical and well-structured?

### Iterate

If results are unsatisfactory:

1. **More data** -- Scale up: `oracle plan --size large --provider anthropic`
2. **More epochs** -- Increase `NUM_EPOCHS` to 4--5 (watch validation loss for overfitting)
3. **Higher LoRA rank** -- Increase `LORA_R` to 128 for more adapter capacity
4. **Augmentation** -- Run `oracle augment` to diversify question phrasing
5. **Targeted generation** -- Generate more data for weak categories:
   ```bash
   oracle generate --category disputes --difficulty advanced --count 20 --provider anthropic
   oracle generate --category dns --difficulty expert --count 15 --provider anthropic
   ```
6. **Lower learning rate** -- If answers are incoherent, the model may have overfit; try `1e-4` or `5e-5`

---

## Troubleshooting

### Out of memory during training

Even with 128GB unified memory, OOM can occur with aggressive settings:

- Reduce `BATCH_SIZE` to 2 or 1
- Enable 4-bit quantization: `LOAD_IN_4BIT = True`
- Reduce `MAX_SEQ_LENGTH` to 4096 or 2048
- Reduce `LORA_R` to 32
- Disable packing: set `packing=False` in SFTTrainer

### Training loss not decreasing

- Increase `LEARNING_RATE` to 5e-4
- Verify the dataset format matches the chat template: print a formatted sample and inspect it
- Check that `format_example()` produces correctly templated text
- Ensure the training data is not empty or malformed: `oracle validate data/generated/`

### Model outputs are generic / not domain-specific

- Train for more epochs (3--5)
- Increase dataset size with `oracle plan --size large`
- Increase `LORA_R` to 128 for more adapter capacity
- Verify seed examples in `data/seeds/` set a strong quality baseline
- Check that the system prompt is included in training examples

### Chat template mismatch

If the model ignores the system prompt or formats responses oddly:

- Check the base model's expected chat template on its Hugging Face page
- Verify `tokenizer.chat_template` matches (should be ChatML for Nemotron)
- Update the Ollama `TEMPLATE` in the Modelfile to match
- Inspect a formatted training example: `print(train_dataset[0]["text"])`

### GGUF export fails

- Ensure `llama.cpp` is installed (Unsloth uses it for GGUF conversion)
- Try: `pip install llama-cpp-python`
- If the model architecture is unsupported, export as Hugging Face format and convert manually with `llama.cpp/convert.py`

### Ollama import fails

- Verify the GGUF file path in the Modelfile is correct (relative to where you run `ollama create`)
- Check the GGUF file is not corrupted: `ls -la` should show a reasonable file size (4--16 GB)
- Try a different quantization method if one fails
