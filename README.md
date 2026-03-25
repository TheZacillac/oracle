# Oracle

**Domain name industry training dataset generator for the [Arcanum Suite](https://github.com/TheZacillac).**

Oracle produces high-quality instruction, multi-turn, scenario, and tool-use training data for fine-tuning LLMs into domain name industry experts. It covers the complete domain ecosystem — from DNS protocol internals to ICANN governance to brand protection strategy — and teaches the model to use the Arcanum Suite's live diagnostic tools.

## Coverage

**423 topics** across **26 categories** and **90 subcategories**:

| Category | Topics | Description |
|----------|--------|-------------|
| DNS Protocol & Standards | 49 | Resolution, record types, DNSSEC, encrypted DNS, extensions, zone management, privacy |
| Domain Name Registration | 23 | Lifecycle, transfers, EPP, grace periods, pricing, IDNs |
| TLD Ecosystem | 18 | gTLDs, ccTLDs, new gTLDs, brand TLDs, registry operations, policies |
| Registrars | 12 | Accreditation, registry-registrar model, operations, selection, compliance |
| ICANN | 17 | Governance structure, policy development, programs, accountability |
| IANA | 8 | Root zone management, protocol parameters, special-use domains, governance |
| WHOIS & RDAP | 11 | Protocols, data policy, GDPR, EPDP, accuracy |
| Domain Blocking & Protection | 10 | TMCH, sunrise/claims, DPML, registry locks, EPP status codes |
| WIPO & Domain Disputes | 17 | UDRP, URS, ccTLD DRPs, ACPA, case law, enforcement cost analysis |
| SSL/TLS & Certificates | 16 | DV/OV/EV, CAs, ACME, CT logs, lifecycle, monitoring, PKI |
| Brand Protection | 13 | Typosquatting, homoglyphs, monitoring, enforcement, takedowns |
| DNS Abuse | 13 | Phishing, malware, botnets, DDoS, NRDs, DGAs, detection, mitigation |
| Email Authentication & Domains | 11 | SPF, DKIM, DMARC, BIMI, ARC, MTA-STS, DANE, deliverability |
| Domain Valuation & Aftermarket | 9 | Pricing, auctions, brokerage, parking, investing, drop catching |
| Web Hosting & Content Delivery | 27 | CDNs, GeoDNS, GSLB, failover, cloud DNS, reverse proxies, serverless |
| Internet Governance & Standards Bodies | 11 | IETF, RIRs, IGF, ITU, multistakeholder model, internet fragmentation |
| Domain Security & Hijacking Prevention | 14 | Hijacking, subdomain takeover, registrar security, incident response, seizures |
| Compliance & Regulatory | 14 | NIS2, DORA, data protection, sanctions, registration regulations |
| DNS Monitoring & Observability | 10 | Passive DNS, propagation, analytics, threat intelligence, asset discovery |
| Internationalization & Universal Acceptance | 12 | IDN variants, EAI, UA readiness, script handling, IDNA 2008 |
| DNS Automation & Infrastructure as Code | 12 | Terraform, OctoDNS, registrar APIs, CI/CD, change management |
| DNS Software & Implementations | 14 | BIND, PowerDNS, Unbound, Knot, NSD, CoreDNS, server operations |
| Protective DNS & Filtering | 12 | Quad9, Umbrella, RPZ, Pi-hole, enterprise DNS, content controls |
| DNS Debugging & Tooling | 18 | dig, nslookup, drill, Wireshark, online tools, troubleshooting methodology |
| Domain Name Industry & Business | 15 | Market dynamics, key players, events, careers, subdomain strategy, PSL |
| Arcanum Suite Tool Usage | 37 | Seer diagnostics, Tome reference, Scrolls skills, workflows |

## Training Data Formats

Oracle generates four types of training examples:

- **Instruction** (55%) — Single-turn Q&A with expert answers
- **Multi-turn** (15%) — Conversational exchanges with follow-up questions
- **Scenario** (15%) — Real-world problem-solving with structured analysis
- **Tool-use** (15%) — Tool-calling sequences with result interpretation

All examples are exported in formats compatible with:
- **Unsloth** / Hugging Face TRL (OpenAI chat JSONL)
- **NVIDIA NeMo** (NeMo SFT JSONL)
- **Alpaca** (instruction/input/output JSONL)

## Quick Start

```bash
# Install
pip install -e ".[all,dev]"

# View the taxonomy
oracle taxonomy --stats

# Preview a generation plan
oracle plan --size medium --dry-run

# Fetch source documents (RFCs, IANA data, ICANN docs)
oracle fetch-sources

# Generate data for a specific category
oracle generate --category dns --difficulty intermediate --count 5

# Execute a full generation plan
oracle plan --size medium --provider anthropic

# Validate generated data
oracle validate data/generated/

# Export with train/val/test splits
oracle export-splits data/generated/ --format openai_chat

# Augment with paraphrased questions
oracle augment data/generated/ --count 2
```

## LLM Providers

Oracle supports three providers for generating training data:

### Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
oracle generate --category dns --provider anthropic
oracle generate --category dns --provider anthropic --model claude-sonnet-4-20250514
```

### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
oracle generate --category dns --provider openai
oracle generate --category dns --provider openai --model gpt-4o
```

### Ollama (Local)

No API key needed — uses your local Ollama instance at `localhost:11434`:

```bash
# Ensure Ollama is running and the model is pulled
ollama pull nemotron-3-nano

# Generate with the default Ollama model (nemotron-3-nano:latest)
oracle generate --category dns --provider ollama

# Use a specific Ollama model
oracle generate --category dns --provider ollama --model llama3.1:8b
oracle generate --category dns --provider ollama --model qwen3:14b
oracle generate --category dns --provider ollama --model gemma3:27b

# Full generation plan with Ollama
oracle plan --size medium --provider ollama

# Augment with Ollama
oracle augment data/generated/ --provider ollama
```

All commands that accept `--provider` support all three options: `anthropic`, `openai`, and `ollama`. The `--model` flag overrides the default model for any provider.

> **Note:** Larger models produce higher-quality training data. For best results with Ollama, use the largest model your hardware can run. Smaller models may struggle with the structured JSON output format required for multi-turn and tool-use examples.

## Generation Plans

Three preset plans control the scale and distribution of generated data:

| Plan | Examples per Topic | Estimated Total | Use Case |
|------|--------------------|-----------------|----------|
| `small` | 3 | ~1,300 | Testing and iteration |
| `medium` | 10 | ~4,200 | Initial training runs |
| `large` | 25 | ~10,500 | Production dataset |

Each plan specifies a difficulty distribution (beginner through expert) and format mix (instruction, multi-turn, scenario, tool-use).

## Generation Strategies

### Synthetic Generation
An LLM generates expert Q&A pairs given topic context, difficulty guidance, and format instructions. Supports Anthropic (Claude), OpenAI, and Ollama (local models).

### RFC Extraction
Fetches RFCs referenced in the taxonomy, parses them into sections, and generates Q&A pairs grounded in specific RFC text. Caches documents locally.

### Source Extraction
Fetches and caches ICANN policy documents, WIPO references, and IANA registry data for training data generation.

### Data Augmentation
Paraphrases existing questions to increase diversity and prevent phrasing memorization while preserving expert answers.

## Tool-Use Training

Oracle generates training data that teaches the model to use the Arcanum Suite's diagnostic and reference tools:

**Seer** — 13 domain diagnostic tools (WHOIS, RDAP, DNS, propagation, SSL, health checks, bulk operations)

**Tome** — 8 reference data tools (TLD lookup, DNS record types, industry glossary)

**Scrolls** — 11 analytical skills (email auth audit, zone health, portfolio audit, typosquatting detection, phishing analysis, HTTP recon, CDN detection, migration planner, penetration testing, registration compliance, RFC reference)

Tool-use examples follow the full interaction pattern:
1. User asks a question requiring live data
2. Assistant reasons about which tools to use
3. Tool calls are made with appropriate parameters
4. Tool results are returned
5. Assistant interprets results with expert analysis

## Dataset Quality

### Validation
- Format and structure validation (Pydantic models)
- Minimum answer depth per difficulty level
- Generation artifact detection (filters "as an AI" etc.)
- Content deduplication via SHA-256 hashing
- Token count estimation (tiktoken)

### Difficulty Levels
| Level | Audience | Token Budget |
|-------|----------|-------------|
| Beginner | New to domains — business owners, students | 150-600 |
| Intermediate | Working professionals — IT admins, developers | 200-900 |
| Advanced | Industry professionals — registrar staff, DNS operators | 300-1,500 |
| Expert | Domain authorities — protocol designers, UDRP panelists | 500-2,500 |

### Seed Examples
Hand-crafted gold-standard examples in `data/seeds/` for each format type serve as quality benchmarks and few-shot generation context.

## Project Structure

```
oracle/
├── src/oracle/
│   ├── taxonomy.py            # 423 topics across 26 categories
│   ├── schema.py              # Pydantic models (supports tool-call messages)
│   ├── difficulty.py          # 4 difficulty levels with generation profiles
│   ├── plan.py                # Generation plans and executor
│   ├── augment.py             # Question paraphrasing for data augmentation
│   ├── cli.py                 # Click CLI (9 commands)
│   ├── generators/
│   │   ├── base.py            # Abstract generator interface
│   │   ├── synthetic.py       # LLM-powered Q&A generation (all formats)
│   │   ├── tool_use.py        # Tool-calling training data generator
│   │   └── rfc.py             # RFC document extraction
│   ├── sources/
│   │   ├── rfc.py             # IETF RFC fetcher and parser
│   │   ├── iana.py            # IANA registry data fetcher
│   │   └── icann.py           # ICANN/WIPO document fetcher
│   ├── validators/
│   │   └── quality.py         # Dedup, format, depth, artifact checks
│   └── exporters/
│       └── nemo.py            # OpenAI chat, NeMo SFT, Alpaca + train/val/test splits
├── data/
│   ├── seeds/                 # Hand-crafted gold-standard examples
│   ├── sources/               # Cached RFCs, IANA data, ICANN docs
│   ├── generated/             # Generated examples by category
│   └── exports/               # Training-ready datasets
├── prompts/
│   └── system.txt             # System prompt for the trained model
└── tests/
```

## Part of the Arcanum Suite

Oracle is the training data layer of the Arcanum Suite — a domain intelligence ecosystem:

| Project | Purpose |
|---------|---------|
| **[seer](https://github.com/TheZacillac/seer)** | Domain diagnostics (WHOIS, RDAP, DNS, SSL, status) |
| **[tome](https://github.com/TheZacillac/tome)** | Reference database (TLDs, record types, glossary) |
| **[scrolls](https://github.com/TheZacillac/scrolls)** | AI agent skill definitions |
| **[tower](https://github.com/TheZacillac/tower)** | Unified MCP server (21 tools) |
| **[familiar](https://github.com/TheZacillac/familiar)** | Conversational AI agent (LangGraph) |
| **oracle** | Training dataset generator (this project) |
| **[arcanum](https://github.com/TheZacillac/arcanum)** | Meta-package & unified CLI |

## License

[MIT](LICENSE)
