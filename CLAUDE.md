# CLAUDE.md - Oracle

Oracle is the domain name industry training dataset generator for the Arcanum Suite. It produces high-quality instruction/response pairs for fine-tuning LLMs (targeting Nemotron) to be expert-level domain name professionals.

## Purpose

Generate comprehensive, accurate training data covering the entire domain name ecosystem: DNS, registration, TLDs, ICANN, IANA, WHOIS/RDAP, SSL/TLS, WIPO disputes, brand protection, and DNS abuse.

## Architecture

```
oracle/
├── src/oracle/
│   ├── taxonomy.py          # Topic taxonomy (categories, subcategories, topics)
│   ├── schema.py            # Training example data models (Pydantic)
│   ├── difficulty.py        # Difficulty level definitions
│   ├── cli.py               # Click CLI entry point
│   ├── generators/          # Data generation strategies
│   │   ├── base.py          # Abstract generator interface
│   │   ├── synthetic.py     # LLM-powered Q&A generation
│   │   └── rfc.py           # RFC document extraction
│   ├── sources/             # Source document fetchers
│   │   ├── rfc.py           # IETF RFC fetcher/parser
│   │   ├── icann.py         # ICANN document fetcher
│   │   └── iana.py          # IANA data fetcher
│   ├── validators/          # Quality assurance
│   │   └── quality.py       # Dedup, format, accuracy checks
│   └── exporters/           # Training format exporters
│       └── nemo.py          # NeMo/OpenAI chat JSONL format
├── data/
│   ├── sources/             # Cached source documents
│   ├── generated/           # Generated examples by category
│   └── exports/             # Training-ready datasets
├── prompts/
│   └── system.txt           # System prompt for the trained model
└── tests/
```

## Data Format

Each training example is a JSONL record:

```jsonl
{
  "id": "dns-record_types-0042",
  "category": "dns",
  "subcategory": "record_types",
  "topic": "CNAME records and restrictions",
  "difficulty": "intermediate",
  "format": "instruction",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ],
  "sources": ["RFC 1034 Section 3.6.2"],
  "token_count": 847,
  "generated_by": "synthetic",
  "version": "0.1.0"
}
```

## Generation Strategies

1. **Synthetic** — LLM generates expert Q&A pairs given a topic + difficulty + context
2. **RFC Extraction** — Parse RFCs into structured knowledge, generate Q&A from sections
3. **Source Extraction** — Transform ICANN/IANA documents into training pairs

## Key Conventions

- All data models use Pydantic v2
- Async-first for network operations (httpx)
- Rich for CLI output
- Click for CLI framework
- Taxonomy is the single source of truth for topic coverage
- Every generated example must reference its source material
- Token counts use tiktoken for accurate budgeting

## Commands

```bash
# Install
pip install -e ".[all,dev]"

# Generate synthetic data for a category
oracle generate --category dns --difficulty intermediate --count 50

# Fetch source documents
oracle fetch-sources --type rfc

# Export to NeMo format
oracle export --format nemo --output data/exports/

# Validate dataset
oracle validate data/generated/

# Show taxonomy coverage
oracle taxonomy --stats
```

## Testing

```bash
pytest                    # Run all tests
pytest tests/ -v          # Verbose
ruff check src/           # Lint
```
