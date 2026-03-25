# CLAUDE.md - Oracle

Oracle is the domain name industry training dataset generator for the Arcanum Suite. It produces high-quality, multi-format training data for fine-tuning LLMs (targeting NVIDIA Nemotron-3-Nano via Unsloth) to be expert-level domain name professionals.

## Purpose

Generate comprehensive, accurate training data covering the entire domain name ecosystem: 423 topics across 26 categories, backed by 338 authoritative source documents.

## Target Model

- **Base model**: `nvidia/Llama-3.1-Nemotron-Nano-8B-v1`
- **Training framework**: Unsloth (LoRA/QLoRA)
- **Target hardware**: NVIDIA DGX Spark (128GB unified memory)
- **Thinking traces**: `<think>` tags for reasoning (75% of examples)

## Architecture

```
oracle/
├── src/oracle/
│   ├── taxonomy.py          # 423 topics across 26 categories
│   ├── schema.py            # Training example data models (Pydantic v2)
│   ├── difficulty.py        # 4 difficulty levels with token budgets
│   ├── plan.py              # Generation plans (small/medium/large) + executor
│   ├── augment.py           # Question paraphrasing for data augmentation
│   ├── cli.py               # Click CLI (10 commands)
│   ├── generators/
│   │   ├── base.py          # Abstract generator interface
│   │   ├── synthetic.py     # LLM-powered Q&A (instruction, multi-turn, scenario)
│   │   ├── tool_use.py      # Tool-use training data (seer, tome, scrolls)
│   │   └── rfc.py           # RFC document extraction
│   ├── sources/             # 338 source documents across 8 fetcher modules
│   │   ├── rfc.py           # IETF RFCs (79 taxonomy-referenced)
│   │   ├── icann.py         # ICANN (63) + WIPO (9) + dispute providers (4)
│   │   ├── iana.py          # IANA registries (37 data sources)
│   │   ├── cabforum.py      # CA/Browser Forum + SSL/TLS (23)
│   │   ├── psl.py           # Public Suffix List
│   │   ├── industry.py      # M3AAWG, APWG, DNS-OARC, FIRST, threat intel (47)
│   │   ├── governance.py    # IETF WGs, IGF, WSIS, RIRs, CERTs (30)
│   │   └── dns_software.py  # BIND, Knot, NSD, PowerDNS, Unbound, CoreDNS (45)
│   ├── validators/
│   │   └── quality.py       # Dedup, format, token counting, quality scoring
│   └── exporters/
│       └── nemo.py          # NeMo SFT, OpenAI chat, Alpaca + train/val/test splits
├── data/
│   ├── seeds/               # Hand-crafted gold-standard examples (4 formats)
│   ├── sources/             # Cached source documents
│   ├── generated/           # Generated examples by category
│   └── exports/             # Training-ready datasets
├── prompts/
│   └── system.txt           # System prompt for the trained model
├── docs/
│   └── TRAINING.md          # Step-by-step Unsloth training guide for DGX Spark
└── tests/
```

## Data Formats

4 training example formats, each with optional `<think>` reasoning traces:

| Format | Description | Use Case |
|--------|-------------|----------|
| `instruction` | Single Q&A turn | Core knowledge (55% of dataset) |
| `multi_turn` | 2-4 exchange conversation | Follow-up depth (15%) |
| `scenario` | Real-world problem solving | Applied expertise (15%) |
| `tool_use` | Tool call → result → interpretation | Arcanum Suite integration (15%) |

## Generation Strategies

1. **Synthetic** — LLM generates expert Q&A pairs given topic + difficulty + format + thinking traces
2. **Tool-use** — LLM generates tool call sequences with reasoning about which tools to use and why
3. **RFC Extraction** — Parse RFCs into structured knowledge, generate Q&A from sections
4. **Source Extraction** — Transform ICANN/IANA/WIPO documents into training pairs
5. **Augmentation** — Paraphrase existing questions for diversity

## LLM Providers

| Provider | API | Default Model | API Key |
|----------|-----|---------------|---------|
| `anthropic` | Anthropic API | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| `openai` | OpenAI API | `gpt-4o` | `OPENAI_API_KEY` |
| `ollama` | OpenAI-compatible (`localhost:11434/v1`) | `nemotron-3-nano:latest` | None needed |

## Key Conventions

- All data models use Pydantic v2
- Async-first for network operations (httpx)
- Rich for CLI output, Click for CLI framework
- Taxonomy is the single source of truth for topic coverage
- Every generated example must reference its source material
- Token counts use tiktoken for accurate budgeting
- Thinking traces use `<think>...</think>` tags (Nemotron-compatible)
- 75% of examples include thinking traces, 25% without (preserves non-reasoning capability)
- Domain names are NEVER spell-corrected — always used exactly as provided

## Commands

```bash
# Install
pip install -e ".[all,dev]"

# Taxonomy
oracle taxonomy --stats                    # Show coverage stats
oracle taxonomy --category dns             # Show category detail

# Generate
oracle generate -c dns -d intermediate -n 50 --provider ollama
oracle generate -c dns --provider ollama --model qwen3:14b

# Generation plans
oracle plan --size medium --provider ollama --dry-run    # Preview
oracle plan --size large --provider anthropic            # Execute

# Fetch sources (all 338 documents)
oracle fetch-sources --type all
oracle fetch-sources --type rfc
oracle fetch-sources --type cabforum

# Validate, export, augment
oracle validate data/generated/
oracle export data/generated/ --format openai_chat
oracle export-splits data/generated/ --format openai_chat
oracle augment data/generated/ --provider ollama
oracle stats data/generated/
```

## Training Pipeline

See `docs/TRAINING.md` for the complete step-by-step guide. Summary:

```bash
# 1. Generate dataset
oracle plan --size large --provider anthropic

# 2. Validate and export with splits
oracle validate data/generated/
oracle export-splits data/generated/ --format openai_chat --output data/exports/

# 3. Train on DGX Spark with Unsloth (see docs/TRAINING.md)
python train.py

# 4. Export to GGUF and deploy with Ollama
python merge_and_export.py
ollama create oracle-domain-expert -f Modelfile
```

## Testing

```bash
pytest                    # Run all tests
pytest tests/ -v          # Verbose
ruff check src/           # Lint
```
