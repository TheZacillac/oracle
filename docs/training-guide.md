# Training Guide: Fine-Tuning with Unsloth on DGX Spark

Step-by-step process for generating the Oracle dataset, then fine-tuning a Nemotron model using Unsloth on a DGX Spark.

---

## Prerequisites

- NVIDIA DGX Spark (Grace Blackwell GB10, 128GB unified memory)
- Oracle project installed on your primary machine (for dataset generation)
- Anthropic or OpenAI API key (for synthetic data generation)
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

### 1.2 Set your API key

```bash
# For Anthropic (recommended)
export ANTHROPIC_API_KEY="sk-ant-..."

# Or for OpenAI
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
# Test run — ~1,300 examples
oracle plan --size small --provider anthropic

# Once validated, generate the full dataset — ~4,200 examples
oracle plan --size medium --provider anthropic

# For maximum coverage — ~10,500 examples
oracle plan --size large --provider anthropic
```

This will take time depending on the plan size (the LLM generates each batch). Generated data lands in `data/generated/`.

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
oracle augment data/generated/ --count 2 --provider anthropic
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
"""Fine-tune Nemotron on Oracle domain expert dataset using Unsloth."""

from unsloth import FastLanguageModel
from unsloth.chat_templates import get_chat_template
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

# -----------------------------------------------------------------
# 1. Configuration
# -----------------------------------------------------------------

# Base model — choose based on your needs:
#   "nvidia/Nemotron-Mini-4B-Instruct"   — 4B params, fastest training
#   "nvidia/Mistral-NeMo-Minitron-8B-Instruct" — 8B, good balance
#   "nvidia/Nemotron-4-340B-Instruct"    — 340B, requires quantization
#
# For DGX Spark with 128GB unified memory, 4B-8B models work well
# in full precision, or up to ~70B with 4-bit quantization.
MODEL_NAME = "nvidia/Nemotron-Mini-4B-Instruct"

MAX_SEQ_LENGTH = 4096
LOAD_IN_4BIT = True  # QLoRA — set False for full LoRA if memory allows

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
    dtype=None,  # Auto-detect (bf16 on Blackwell)
)

# -----------------------------------------------------------------
# 3. Apply LoRA adapters
# -----------------------------------------------------------------

model = FastLanguageModel.get_peft_model(
    model,
    r=LORA_R,
    lora_alpha=LORA_ALPHA,
    lora_dropout=LORA_DROPOUT,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth optimized checkpointing
    random_state=42,
)

# -----------------------------------------------------------------
# 4. Set up chat template
# -----------------------------------------------------------------

# Use the model's native chat template if available,
# otherwise fall back to ChatML
tokenizer = get_chat_template(
    tokenizer,
    chat_template="chatml",  # Works for most Nemotron models
)

# -----------------------------------------------------------------
# 5. Load and format dataset
# -----------------------------------------------------------------

dataset = load_dataset("json", data_files={
    "train": TRAIN_FILE,
    "validation": VAL_FILE,
})


def format_example(example):
    """Convert Oracle's OpenAI chat format to the training format."""
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
    bf16=True,  # Blackwell supports bf16 natively
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
| ~1,300 (small) | 4B 4-bit | ~15-30 min |
| ~4,200 (medium) | 4B 4-bit | ~1-2 hours |
| ~10,500 (large) | 4B 4-bit | ~3-5 hours |
| ~4,200 (medium) | 8B 4-bit | ~2-4 hours |

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
    max_seq_length=4096,
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

| Method | Size (4B model) | Quality | Speed | Use Case |
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

Be precise, cite sources, and provide practical guidance."""

PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
PARAMETER stop "<|im_end|>"
```

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
