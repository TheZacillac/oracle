# Training Guide: Fine-Tuning Nemotron-3-Nano-4B with Unsloth on DGX Spark

Step-by-step process for generating the Oracle dataset, then fine-tuning NVIDIA's Nemotron-3-Nano-4B using Unsloth on a DGX Spark.

**Target Model:** `nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16` (Mamba2-Transformer hybrid, 3.97B params)
**Architecture:** Mamba-2 + MLP layers with 4 Attention layers (Nemotron-Hybrid)
**Context:** Up to 262K tokens
**Thinking:** Native `<think>`/`</think>` support (token IDs 12/13)
**Reasoning Split:** 75% with thinking traces / 25% without (preserves reasoning capability)

---

## Prerequisites

- NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory)
- Oracle project installed on your primary machine (for dataset generation)
- An LLM provider for synthetic data generation (one of):
  - **Ollama** running locally (free, no API key) — recommended if you have a capable local model
  - **Anthropic API key** — highest quality generation with Claude
  - **OpenAI API key** — alternative cloud provider
- Hugging Face account (for model access)

---

## Phase 1: Generate the Training Data (on your primary machine)

### 1.1 Install Oracle

```bash
cd ~/Projects/arcanum_suite/oracle
python -m venv .venv
source .venv/bin/activate
pip install -e ".[all,dev]"
```

### 1.2 Configure your LLM provider

Choose one of the following:

**Option A: Ollama (local, free)**

No API key needed. Just ensure Ollama is running and has a model pulled:

```bash
# Pull a model (if you haven't already)
ollama pull nemotron-3-nano

# Verify it's running
ollama list
```

**Option B: Anthropic (cloud)**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option C: OpenAI (cloud)**

```bash
export OPENAI_API_KEY="sk-..."
```

### 1.3 Fetch source documents

This caches RFCs, IANA data, and ICANN documents locally for the RFC extraction generator:

```bash
oracle fetch-sources
```

### 1.4 Run a generation plan

Start with `small` to validate the pipeline, then scale up:

```bash
# --- With Ollama (local) ---
# Test run — ~1,300 examples
oracle plan --size small --provider ollama

# Use a specific Ollama model
oracle plan --size small --provider ollama --model qwen3:14b

# --- With Anthropic (cloud) ---
oracle plan --size small --provider anthropic

# --- With OpenAI (cloud) ---
oracle plan --size small --provider openai
```

Once the small plan looks good, scale up:

```bash
# Full dataset — ~4,200 examples
oracle plan --size medium --provider ollama

# Maximum coverage — ~10,500 examples
oracle plan --size large --provider ollama
```

You can also generate a single category at a time if you want to test or iterate:

```bash
oracle generate --category dns --difficulty intermediate --count 5 --provider ollama
oracle generate --category disputes --difficulty advanced --count 3 --provider ollama --model llama3.1:8b
```

Generated data lands in `data/generated/`.

> **Tip:** Larger models produce better structured JSON output. If you see high rejection rates during validation with a small model, try a larger one or switch to a cloud provider for the complex formats (multi-turn, scenario, tool-use).

### 1.5 Validate the dataset

```bash
oracle validate data/generated/
```

Review the validation report. Check for:
- Rejection rate (should be < 10%)
- Duplicate count
- Token distribution

### 1.6 (Optional) Augment with paraphrases

This increases question diversity without needing to generate entirely new answers:

```bash
oracle augment data/generated/ --count 2 --provider ollama
```

### 1.7 Export with train/val/test splits

```bash
oracle export-splits data/generated/ \
  --format openai_chat \
  --name oracle-domain-expert \
  --version 0.1.0
```

This produces three files in `data/exports/`:
- `oracle-domain-expert-0.1.0.train.jsonl` (85%)
- `oracle-domain-expert-0.1.0.val.jsonl` (10%)
- `oracle-domain-expert-0.1.0.test.jsonl` (5%)

### 1.8 Check dataset statistics

```bash
oracle stats data/generated/
```

Verify the distribution across categories, difficulties, and formats looks balanced.

---

## Phase 2: Set Up the DGX Spark

### 2.1 Transfer the dataset

Copy the exported splits to the DGX Spark:

```bash
scp data/exports/oracle-domain-expert-0.1.0.*.jsonl dgx-spark:~/training/data/
```

### 2.2 Set up the Python environment on the DGX Spark

```bash
ssh dgx-spark

# Create a training environment
python -m venv ~/training/venv
source ~/training/venv/bin/activate

# Install Unsloth (use the CUDA 12.x version for Blackwell)
pip install unsloth

# Install additional dependencies
pip install torch transformers datasets accelerate bitsandbytes
pip install trl peft wandb  # wandb is optional but recommended for tracking
```

### 2.3 Log into Hugging Face

Some Nemotron models require accepting a license agreement on Hugging Face:

```bash
pip install huggingface_hub
huggingface-cli login
```

Visit the model page on Hugging Face and accept the license if prompted.

---

## Phase 3: Fine-Tune with Unsloth

### 3.1 Create the training script

Create `~/training/train.py` on the DGX Spark:

```python
"""Fine-tune Nemotron-3-Nano-4B on Oracle domain expert dataset using Unsloth."""

from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# -----------------------------------------------------------------
# 1. Configuration
# -----------------------------------------------------------------

# Nemotron-3-Nano-4B — Mamba2-Transformer hybrid (3.97B params)
# Official NVIDIA model from Hugging Face
MODEL_NAME = "nvidia/NVIDIA-Nemotron-3-Nano-4B-BF16"

# Nemotron-3-Nano supports up to 262K context, but 4096-8192 is
# sufficient for training and much more memory-efficient
MAX_SEQ_LENGTH = 8192

# DGX Spark has 128GB unified memory — can run full 16-bit LoRA
# Set True for QLoRA (4-bit) if you want to save memory
LOAD_IN_4BIT = False

# LoRA configuration
LORA_R = 64           # Rank — higher = more capacity, more memory
LORA_ALPHA = 64       # Scaling factor — typically equal to r
LORA_DROPOUT = 0.05

# Training hyperparameters
BATCH_SIZE = 4
GRADIENT_ACCUMULATION = 4  # Effective batch size = 4 * 4 = 16
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
WARMUP_RATIO = 0.05
MAX_STEPS = -1  # Set to a number to cap training steps, -1 for full epochs

# Paths
TRAIN_FILE = "~/training/data/oracle-domain-expert-0.1.0.train.jsonl"
VAL_FILE = "~/training/data/oracle-domain-expert-0.1.0.val.jsonl"
OUTPUT_DIR = "~/training/output/oracle-nemotron"

# -----------------------------------------------------------------
# 2. Load model with Unsloth
# -----------------------------------------------------------------

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=MODEL_NAME,
    max_seq_length=MAX_SEQ_LENGTH,
    load_in_4bit=LOAD_IN_4BIT,
    dtype=None,  # Auto-detect (bf16 on Blackwell GB10)
)

# -----------------------------------------------------------------
# 3. Apply LoRA adapters
# -----------------------------------------------------------------

# Nemotron-3-Nano is a Mamba2-Transformer hybrid — Unsloth handles
# the correct target modules automatically
model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    # Let Unsloth auto-detect target modules for hybrid architecture
    target_modules="all-linear",
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth optimized checkpointing
    random_state=42,
)

# -----------------------------------------------------------------
# 4. Chat template
# -----------------------------------------------------------------

# Nemotron-3-Nano uses ChatML-style template with <think> support:
#   <|im_start|>system\n...<|im_end|>
#   <|im_start|>user\n...<|im_end|>
#   <|im_start|>assistant\n<think>...</think>...<|im_end|>
#
# The tokenizer's built-in chat_template handles this natively.
# <think> = token ID 12, </think> = token ID 13
# No manual template setup needed — apply_chat_template works out of the box.

# -----------------------------------------------------------------
# 5. Load and format dataset
# -----------------------------------------------------------------

dataset = load_dataset("json", data_files={
    "train": TRAIN_FILE,
    "validation": VAL_FILE,
})


def format_example(example):
    """Convert Oracle's OpenAI chat format to the training format.

    The dataset already includes <think>...</think> blocks in assistant
    message content (added by Oracle's exporter), so we just apply the
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

print(f"Train: {len(train_dataset)} examples")
print(f"Val:   {len(val_dataset)} examples")

# Verify thinking traces are present
sample = train_dataset[0]["text"]
has_thinking = "<think>" in sample
print(f"Thinking traces in dataset: {has_thinking}")

# -----------------------------------------------------------------
# 6. Configure training
# -----------------------------------------------------------------

training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=BATCH_SIZE,
    gradient_accumulation_steps=GRADIENT_ACCUMULATION,
    num_train_epochs=NUM_EPOCHS,
    max_steps=MAX_STEPS,
    learning_rate=LEARNING_RATE,
    lr_scheduler_type="cosine",
    warmup_ratio=WARMUP_RATIO,
    weight_decay=0.01,
    bf16=True,  # Blackwell GB10 supports bf16 natively
    logging_steps=10,
    eval_strategy="steps",
    eval_steps=100,
    save_strategy="steps",
    save_steps=200,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    report_to="wandb",  # Set to "none" to disable
    run_name="oracle-domain-expert",
    seed=42,
    optim="adamw_8bit",  # Memory efficient optimizer
)

# -----------------------------------------------------------------
# 7. Train
# -----------------------------------------------------------------

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    packing=True,  # Pack short examples together for efficiency
)

print("Starting training...")
trainer.train()

print(f"Training complete. Best model saved to {OUTPUT_DIR}")

# -----------------------------------------------------------------
# 8. Save the LoRA adapter
# -----------------------------------------------------------------

# Save just the LoRA adapter weights (small, ~100-500MB)
model.save_pretrained(f"{OUTPUT_DIR}/lora-adapter")
tokenizer.save_pretrained(f"{OUTPUT_DIR}/lora-adapter")
print(f"LoRA adapter saved to {OUTPUT_DIR}/lora-adapter")
```

### 3.2 Run the training

```bash
source ~/training/venv/bin/activate

# Optional: set up Weights & Biases for monitoring
wandb login

# Run training
python ~/training/train.py
```

**Expected training time** (rough estimates):

| Dataset Size | Model | DGX Spark (GB10) |
|-------------|-------|-------------------|
| ~1,300 (small) | Nano 4B 16-bit | ~15-30 min |
| ~4,200 (medium) | Nano 4B 16-bit | ~1-2 hours |
| ~10,500 (large) | Nano 4B 16-bit | ~3-5 hours |
| ~4,200 (medium) | Nano 4B 4-bit | ~45 min - 1.5 hours |

### 3.3 Monitor training

If using Weights & Biases, check your dashboard at [wandb.ai](https://wandb.ai).

Key metrics to watch:
- **Training loss** — should decrease steadily
- **Validation loss** — should decrease and then plateau; if it starts increasing, you're overfitting
- **Learning rate** — should follow the cosine schedule

If validation loss diverges from training loss, consider:
- Reducing `NUM_EPOCHS` (try 1-2 instead of 3)
- Increasing `LORA_DROPOUT`
- Reducing `LEARNING_RATE`

---

## Phase 4: Merge and Export

### 4.1 Merge LoRA into base model

After training, merge the LoRA adapter back into the base model for deployment:

```python
"""Merge LoRA adapter and export to various formats."""

from unsloth import FastLanguageModel

MODEL_DIR = "~/training/output/oracle-nemotron"
MERGED_DIR = "~/training/output/oracle-nemotron-merged"

# Load the trained model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=f"{MODEL_DIR}/lora-adapter",
    max_seq_length=8192,
    load_in_4bit=False,  # Load in full precision for merging
)

# Option A: Save as merged HuggingFace model (full precision)
model.save_pretrained_merged(
    MERGED_DIR,
    tokenizer,
    save_method="merged_16bit",
)

# Option B: Save as GGUF for Ollama/llama.cpp (recommended for deployment)
model.save_pretrained_gguf(
    f"{MERGED_DIR}-gguf",
    tokenizer,
    quantization_method="q4_k_m",  # Good balance of quality and size
)

# Option C: Save as GGUF in multiple quantizations
for quant in ["q4_k_m", "q5_k_m", "q8_0", "f16"]:
    model.save_pretrained_gguf(
        f"{MERGED_DIR}-gguf-{quant}",
        tokenizer,
        quantization_method=quant,
    )
```

### 4.2 Quantization options

| Method | Size (Nano 4B) | Quality | Speed | Use Case |
|--------|-----------------|---------|-------|----------|
| `q4_k_m` | ~2.5 GB | Good | Fast | Daily use, Ollama default |
| `q5_k_m` | ~3.2 GB | Better | Fast | Recommended balance |
| `q8_0` | ~4.5 GB | Great | Medium | When quality matters |
| `f16` | ~8 GB | Best | Slower | Benchmarking, reference |

---

## Phase 5: Deploy with Ollama

### 5.1 Create an Ollama Modelfile

Create `~/training/output/Modelfile`:

```dockerfile
FROM ./oracle-nemotron-merged-gguf-q5_k_m/unsloth.Q5_K_M.gguf

TEMPLATE """<|im_start|>system
{{ .System }}<|im_end|>
<|im_start|>user
{{ .Prompt }}<|im_end|>
<|im_start|>assistant
{{ .Response }}<|im_end|>"""

SYSTEM """You are a domain name industry expert — an authoritative, comprehensive resource on every aspect of the domain name ecosystem. You have access to the Arcanum Suite's diagnostic and reference tools for live domain intelligence.

Your knowledge spans DNS protocols, domain registration, TLDs, registrars, ICANN, IANA, WHOIS/RDAP, domain blocking, WIPO disputes, SSL/TLS, brand protection, DNS abuse, email authentication, domain valuation, web hosting, internet governance, domain security, compliance, DNS monitoring, internationalization, DNS automation, DNS software, protective DNS, debugging tools, and the domain industry.

Think through complex questions step by step before answering. Be precise, cite sources, and provide practical guidance."""

PARAMETER temperature 1.0
PARAMETER top_p 0.95
PARAMETER num_ctx 8192
PARAMETER stop "<|im_end|>"
```

> **Note on temperature**: Nemotron-3-Nano is trained with `temperature=1.0` and `top_p=0.95` for reasoning tasks. Using lower temperatures may degrade thinking quality. For simple lookups, you can reduce to `0.6`.

### 5.2 Import into Ollama

```bash
cd ~/training/output
ollama create oracle -f Modelfile
```

### 5.3 Test the model

```bash
ollama run oracle "What are the three elements of a UDRP complaint?"
ollama run oracle "Explain the difference between RDAP and WHOIS"
ollama run oracle "I just changed my DNS nameservers. How long until it propagates?"
```

### 5.4 Use with Familiar

Update your Familiar environment to use the new model:

```bash
export FAMILIAR_MODEL="ollama:oracle:latest"
```

---

## Phase 6: Evaluate

### 6.1 Run the test set through the model

```python
"""Evaluate the fine-tuned model against the held-out test set."""

import json
from ollama import Client

client = Client()
results = []

with open("~/training/data/oracle-domain-expert-0.1.0.test.jsonl") as f:
    for line in f:
        example = json.loads(line)
        messages = example["messages"]

        # Extract the user question (skip system prompt)
        user_msg = next(m for m in messages if m["role"] == "user")
        expected = next(m for m in messages if m["role"] == "assistant")

        # Get model response
        response = client.chat(
            model="oracle",
            messages=[
                {"role": "system", "content": messages[0]["content"]},
                {"role": "user", "content": user_msg["content"]},
            ],
        )

        results.append({
            "question": user_msg["content"],
            "expected": expected["content"][:200],
            "actual": response["message"]["content"][:200],
        })

# Review results manually or with an LLM-as-judge
for r in results[:5]:
    print(f"Q: {r['question'][:100]}")
    print(f"Expected: {r['expected']}")
    print(f"Actual:   {r['actual']}")
    print("---")
```

### 6.2 What to look for

- **Accuracy** — Does the model cite correct RFCs, policies, and procedures?
- **Depth** — Does it match the expected difficulty level?
- **Tool awareness** — Does it know when to suggest using seer/tome tools?
- **No hallucinations** — Does it avoid making up RFC numbers or policy names?
- **Terminology** — Does it use correct industry terminology?

### 6.3 Iterate

If results are unsatisfactory:

1. **More data** — Run `oracle plan --size large` and retrain
2. **More epochs** — Increase `NUM_EPOCHS` to 4-5 (watch for overfitting)
3. **Higher LoRA rank** — Increase `LORA_R` to 128 for more model capacity
4. **Augmentation** — Run `oracle augment` to diversify question phrasing
5. **Targeted generation** — Generate more data for weak categories:
   ```bash
   oracle generate --category disputes --difficulty advanced --count 20
   oracle generate --category dns --difficulty expert --count 15
   ```

---

## Troubleshooting

### Out of memory during training
- Reduce `BATCH_SIZE` to 2 or 1
- Ensure `LOAD_IN_4BIT = True`
- Reduce `MAX_SEQ_LENGTH` to 2048
- Reduce `LORA_R` to 32

### Training loss not decreasing
- Increase `LEARNING_RATE` to 5e-4
- Check that the dataset format matches the chat template
- Verify `format_example()` is producing the expected tokenized output

### Model outputs are generic / not domain-specific
- Train for more epochs
- Increase dataset size with `oracle plan --size large`
- Increase `LORA_R` for more adapter capacity
- Review seed examples to ensure quality baseline is high

### Chat template mismatch
If the model ignores the system prompt or formats responses oddly:
- Check the base model's expected chat template on its HuggingFace page
- Update `get_chat_template()` to match (options: `chatml`, `llama-3`, `mistral`, `zephyr`)
- Update the Ollama `TEMPLATE` to match
