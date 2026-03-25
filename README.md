# Oracle

**Domain Name Industry Training Dataset Generator**

Oracle generates high-quality training data for fine-tuning LLMs into domain name industry experts. It is part of the [Arcanum Suite](https://github.com/TheZacillac), a domain intelligence ecosystem.

The target model is NVIDIA Nemotron-3-Nano, fine-tuned via [Unsloth](https://github.com/unslothai/unsloth) on [NVIDIA DGX Spark](https://www.nvidia.com/en-us/products/workstations/dgx-spark/).

## Overview

- **423 topics** across **26 categories** and **90 subcategories**
- **338 source documents** from ICANN, WIPO, IANA, CA/Browser Forum, IETF RFCs, industry organizations, governance bodies, and DNS software documentation
- **4 training data formats**: instruction, multi-turn, scenario, tool-use
- **4 difficulty levels**: beginner, intermediate, advanced, expert
- **Thinking traces**: DeepSeek-R1 style `<think>` tags for reasoning-capable models
- **3 export formats**: NeMo SFT, OpenAI chat, Alpaca
- **Built-in splitting**: stratified train/val/test splits (85/10/5)
- **Data augmentation**: question paraphrasing to increase diversity
- **3 generation plans**: small (~1,500), medium (~4,000), large (~10,000+ examples)
- **3 LLM providers**: Anthropic, OpenAI, Ollama (local, no API key)

## Installation

```bash
# Full install (all providers + dev tools)
pip install -e ".[all,dev]"

# For Ollama generation only (no API key needed)
pip install -e ".[synthetic]"

# Minimal install (no LLM generation, just validation/export)
pip install -e .
```

Requires Python 3.11+.

## Quick Start

```bash
# View the taxonomy
oracle taxonomy --stats

# Fetch source documents (RFCs, IANA data, ICANN docs)
oracle fetch-sources --type all

# Generate data for a specific category
oracle generate --category dns --difficulty intermediate --count 50 --provider ollama

# Execute a full generation plan
oracle plan --size medium --provider ollama --model nemotron-3-nano:latest

# Validate generated data
oracle validate data/generated/

# Augment with paraphrased questions
oracle augment data/generated/ --provider ollama

# Export to training format
oracle export data/generated/ --format openai_chat

# Export with train/val/test splits
oracle export-splits data/generated/ --format openai_chat

# Show dataset statistics
oracle stats data/generated/
```

## Topic Coverage

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

Oracle generates four types of training examples, balanced across each generation plan:

| Format | Share | Description |
|--------|-------|-------------|
| **Instruction** | 55% | Single-turn Q&A with expert answers |
| **Multi-turn** | 15% | Conversational exchanges with follow-up questions |
| **Scenario** | 15% | Real-world problem-solving with structured analysis |
| **Tool-use** | 15% | Tool-calling sequences with result interpretation |

### Thinking Traces

Oracle supports DeepSeek-R1 style `<think>` reasoning tags. By default, 75% of generated examples include thinking traces, preserving the base model's reasoning capabilities during fine-tuning:

```
<|im_start|>assistant
<think>
The user is asking about CNAME record restrictions. I need to explain the key
constraint from RFC 1034 Section 3.6.2: a CNAME record cannot coexist with
other record types at the same name...
</think>
A CNAME record has a critical restriction defined in RFC 1034...
<|im_end|>
```

Nemotron-3-Nano uses dedicated token IDs (12 for `<think>`, 13 for `</think>`) for native reasoning support.

### Difficulty Levels

| Level | Audience | Token Budget |
|-------|----------|-------------|
| Beginner | New to domains -- business owners, students | 150--600 |
| Intermediate | Working professionals -- IT admins, developers | 200--900 |
| Advanced | Industry professionals -- registrar staff, DNS operators | 300--1,500 |
| Expert | Domain authorities -- protocol designers, UDRP panelists | 500--2,500 |

## Source Documents

Oracle draws from 338 authoritative source documents across 9 modules:

| Source Module | Documents | Coverage |
|---------------|-----------|----------|
| **RFC** (IETF) | All DNS/domain-related | Protocol standards, best current practices, informational |
| **ICANN** | 63 | Registrar/registry agreements, consensus policies, GNSO/ccNSO outputs, SSAC/RSSAC advisories |
| **WIPO** | 9 | UDRP/URS resources, Overview 3.0, case search, supplemental rules, statistics |
| **Other Dispute Providers** | 4 | Forum (NAF), ADNDRC, CIIDRC decision databases |
| **CA/Browser Forum** | 23 | Baseline Requirements, EV guidelines, CT policy, root store policies, ACME/Let's Encrypt |
| **IANA** | 37 | TLD list, DNS parameters, DNSSEC algorithms, RDAP bootstrap, EPP extensions, TLS parameters |
| **Industry Orgs** | 47 | M3AAWG, APWG, DNS-OARC, FIRST, CENTR, protective DNS providers, threat intelligence |
| **Governance** | 30 | IETF working groups (DNSOP, DPRIVE, REGEXT, ADD), IGF/WSIS, RIRs, CERTs/CSIRTs |
| **DNS Software** | 45 | BIND, Knot DNS, NSD, PowerDNS, Unbound, CoreDNS, cloud DNS (Route 53, Cloud DNS, Azure DNS), debug tools |
| **PSL** | 1 | Public Suffix List (ICANN and private domains) |

## LLM Providers

Oracle supports three providers for synthetic data generation:

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

No API key needed. Uses your local Ollama instance at `localhost:11434`:

```bash
# Ensure Ollama is running with a model pulled
ollama pull nemotron-3-nano

# Generate with the default Ollama model (nemotron-3-nano:latest)
oracle generate --category dns --provider ollama

# Use a specific model
oracle generate --category dns --provider ollama --model qwen3:14b
oracle generate --category dns --provider ollama --model gemma3:27b
```

Larger models produce higher-quality training data. For best results with Ollama, use the largest model your hardware supports. Smaller models may struggle with the structured JSON output required for multi-turn and tool-use formats.

## Generation Plans

Three preset plans control the scale and distribution of generated data:

| Plan | Per Topic | Estimated Total | Use Case |
|------|-----------|-----------------|----------|
| `small` | 3 | ~1,500 | Testing and pipeline validation |
| `medium` | 10 | ~4,000 | Initial training runs |
| `large` | 25 | ~10,000+ | Production dataset |

Each plan specifies a difficulty distribution (20% beginner, 35% intermediate, 30% advanced, 15% expert) and format mix. Preview a plan before running:

```bash
oracle plan --size medium --dry-run
oracle plan --size large --provider anthropic
oracle plan --size medium --provider ollama --model nemotron-3-nano:latest
```

## Generation Strategies

### Synthetic Generation

An LLM generates expert Q&A pairs given topic context, difficulty guidance, and format instructions. This is the primary generation method and supports all four formats and all three providers.

### RFC Extraction

Fetches RFCs referenced in the taxonomy, parses them into sections, and generates Q&A pairs grounded in specific RFC text. Documents are cached locally to avoid repeat fetches.

### Source Extraction

Fetches and caches ICANN policy documents, WIPO references, CA/Browser Forum documents, IANA registry data, and other authoritative sources for context-enriched generation.

### Data Augmentation

Paraphrases existing questions to increase diversity and prevent phrasing memorization while preserving expert answers:

```bash
oracle augment data/generated/ --count 2 --provider ollama
```

## Export Formats

| Format | File | Compatible With |
|--------|------|-----------------|
| `openai_chat` | JSONL with `messages` array | Unsloth, Hugging Face TRL, OpenAI fine-tuning |
| `nemo_sft` | NeMo SFT JSONL | NVIDIA NeMo Framework |
| `alpaca` | JSONL with `instruction`/`input`/`output` | Alpaca-style trainers |

### Train/Val/Test Splitting

Export with stratified splits for proper evaluation:

```bash
oracle export-splits data/generated/ \
  --format openai_chat \
  --name oracle-domain-expert \
  --version 0.1.0
```

Produces three files (default 85/10/5 split):
- `oracle-domain-expert-0.1.0.train.jsonl`
- `oracle-domain-expert-0.1.0.val.jsonl`
- `oracle-domain-expert-0.1.0.test.jsonl`

## Dataset Quality

### Validation

Oracle validates every generated example before export:

- **Structure** -- Pydantic model validation for format and field correctness
- **Depth** -- Minimum answer token counts per difficulty level
- **Artifacts** -- Filters generation artifacts ("as an AI", "I cannot", etc.)
- **Deduplication** -- SHA-256 content hashing removes duplicate examples
- **Token counting** -- tiktoken-based estimation for accurate budgeting

```bash
oracle validate data/generated/
oracle validate data/generated/ --strict
```

### Seed Examples

Hand-crafted gold-standard examples in `data/seeds/` for each format type serve as quality benchmarks and few-shot generation context.

## Tool-Use Training

Oracle generates training data that teaches the model to use the Arcanum Suite's diagnostic and reference tools. The model learns to reason about when tools are needed, call them with correct parameters, and interpret results with expert analysis.

### Seer -- Domain Diagnostics (13 tools)

Live domain intelligence: WHOIS lookup, RDAP queries, DNS record resolution, global propagation checks, domain health status (HTTP + SSL + expiry), and bulk operations for portfolio-level assessments.

| Tool | Purpose |
|------|---------|
| `seer_lookup` | Smart registration lookup (RDAP with WHOIS fallback) |
| `seer_whois` | Raw WHOIS registration data |
| `seer_rdap_domain` | Structured RDAP domain data |
| `seer_rdap_ip` | IP address registration info |
| `seer_rdap_asn` | Autonomous System info |
| `seer_dig` | DNS record queries (A, AAAA, MX, TXT, NS, SOA, CNAME, CAA) |
| `seer_propagation` | Global DNS propagation (29 servers) |
| `seer_status` | Domain health check (HTTP + SSL + expiry) |
| `seer_bulk_lookup` | Bulk registration lookup (up to 100 domains) |
| `seer_bulk_whois` | Bulk WHOIS lookup |
| `seer_bulk_dig` | Bulk DNS queries |
| `seer_bulk_status` | Bulk health checks |
| `seer_bulk_propagation` | Bulk propagation checks |

### Tome -- Reference Data (8 tools)

Static reference lookups: TLD information (type, registry, WHOIS/RDAP servers), DNS record type details, and domain industry glossary.

| Tool | Purpose |
|------|---------|
| `tome_tld_lookup` | TLD info (type, registry, WHOIS/RDAP servers) |
| `tome_tld_search` | Search TLDs by keyword |
| `tome_tld_overview` | Comprehensive TLD detail |
| `tome_tld_list_by_type` | List TLDs by category |
| `tome_tld_count` | Total TLD count |
| `tome_record_lookup` | DNS record type details |
| `tome_record_search` | Search record types |
| `tome_glossary_lookup` | Domain term definitions |

### Scrolls -- Analytical Skills (11 skills)

Higher-level workflows that compose Seer and Tome tools into structured analytical tasks:

| Skill | Purpose |
|-------|---------|
| `email-auth` | Audit SPF/DKIM/DMARC configuration |
| `zone-health` | DNS zone best-practice audit |
| `portfolio-audit` | Multi-domain health report |
| `typosquatting` | Generate and triage lookalike domains |
| `phishing-analysis` | Detect threat indicators across registration, DNS, SSL |
| `http-recon` | Redirect tracing, security headers, technology fingerprinting |
| `cdn-detection` | Identify infrastructure providers |
| `migration-planner` | Five-phase DNS migration workflow |
| `pentest` | Domain vulnerability scan |
| `registration-compliance` | ICANN policy compliance check |
| `rfc-reference` | Plain-language RFC summaries |

### Tool-Use Training Pattern

Each tool-use example follows the full interaction pattern:

1. User asks a question requiring live data
2. Assistant reasons about which tools to use (with `<think>` trace)
3. Tool calls are made with appropriate parameters
4. Tool results are returned
5. Assistant interprets results with expert analysis

## CLI Reference

| Command | Description |
|---------|-------------|
| `oracle taxonomy` | Display the topic taxonomy |
| `oracle taxonomy --stats` | Show topic counts per category |
| `oracle generate` | Generate synthetic training data for a category |
| `oracle plan` | Execute a generation plan (small/medium/large) |
| `oracle fetch-sources` | Fetch and cache source documents |
| `oracle validate` | Validate a generated dataset |
| `oracle augment` | Augment dataset with paraphrased questions |
| `oracle export` | Export to a training-ready format |
| `oracle export-splits` | Export with train/val/test splits |
| `oracle stats` | Show dataset statistics |

## Project Structure

```
oracle/
├── src/oracle/
│   ├── taxonomy.py            # 423 topics across 26 categories
│   ├── schema.py              # Pydantic models (supports tool-call messages)
│   ├── difficulty.py          # 4 difficulty levels with generation profiles
│   ├── plan.py                # Generation plans and executor
│   ├── augment.py             # Question paraphrasing for data augmentation
│   ├── cli.py                 # Click CLI (10 commands)
│   ├── generators/
│   │   ├── base.py            # Abstract generator interface
│   │   ├── synthetic.py       # LLM-powered generation (all formats)
│   │   ├── tool_use.py        # Tool-calling training data generator
│   │   └── rfc.py             # RFC document extraction
│   ├── sources/
│   │   ├── rfc.py             # IETF RFC fetcher and parser
│   │   ├── icann.py           # ICANN/WIPO document fetcher (63 + 9 + 4 docs)
│   │   ├── iana.py            # IANA registry data fetcher (37 registries)
│   │   ├── cabforum.py        # CA/Browser Forum documents (23 docs)
│   │   ├── industry.py        # M3AAWG, APWG, DNS-OARC, FIRST (47 docs)
│   │   ├── governance.py      # IETF WGs, IGF/WSIS, RIRs, CERTs (30 docs)
│   │   ├── dns_software.py    # BIND, Knot, NSD, PowerDNS, etc. (45 docs)
│   │   └── psl.py             # Public Suffix List
│   ├── validators/
│   │   └── quality.py         # Dedup, format, depth, artifact checks
│   └── exporters/
│       └── nemo.py            # OpenAI chat, NeMo SFT, Alpaca + splits
├── data/
│   ├── seeds/                 # Hand-crafted gold-standard examples
│   ├── sources/               # Cached RFCs, IANA data, ICANN docs
│   ├── generated/             # Generated examples by category
│   └── exports/               # Training-ready datasets
├── prompts/
│   └── system.txt             # System prompt for the trained model
├── docs/
│   └── TRAINING.md            # Step-by-step fine-tuning guide
└── tests/
```

## Testing

```bash
pytest                    # Run all tests
pytest tests/ -v          # Verbose
ruff check src/           # Lint
```

## Part of the Arcanum Suite

Oracle is the training data layer of the [Arcanum Suite](https://github.com/TheZacillac) -- a domain intelligence ecosystem:

| Project | Purpose |
|---------|---------|
| [**seer**](https://github.com/TheZacillac/seer) | Domain diagnostics (WHOIS, RDAP, DNS, SSL, status) |
| [**tome**](https://github.com/TheZacillac/tome) | Reference database (TLDs, record types, glossary) |
| [**scrolls**](https://github.com/TheZacillac/scrolls) | AI agent skill definitions |
| [**tower**](https://github.com/TheZacillac/tower) | Unified MCP server (19 tools) |
| [**familiar**](https://github.com/TheZacillac/familiar) | Conversational AI agent (LangGraph) |
| **oracle** | Training dataset generator (this project) |
| [**arcanum**](https://github.com/TheZacillac/arcanum) | Meta-package & unified CLI |
| [**arcanum.domains**](https://arcanum.domains) | Documentation website |

The fine-tuned model learns to use Seer for live diagnostics, Tome for reference lookups, and Scrolls skills for structured analytical workflows -- bridging expert knowledge with real-time domain intelligence.

## License

[MIT](LICENSE)
