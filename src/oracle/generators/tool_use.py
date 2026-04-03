"""Tool-use training data generator.

Generates training examples that teach the model to use Arcanum Suite tools
(seer, tome) and scrolls skills. Each example follows the flow:
  user question → assistant decides to call tool → tool returns result → assistant interprets
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from oracle.difficulty import get_profile
from oracle.generators.base import BaseGenerator
from oracle.schema import (
    ExampleFormat,
    FailedGeneration,
    GenerationMethod,
    Message,
    MessageRole,
    ToolCall,
    TrainingExample,
)
from oracle.taxonomy import Category, Subcategory, Topic

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Tool definitions for the generation prompt
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = """
## Available Tools

### Seer — Domain Diagnostics
- seer_lookup(domain) → Registration data (RDAP with WHOIS fallback)
- seer_whois(domain) → Raw WHOIS registration data
- seer_rdap_domain(domain) → Structured RDAP domain data
- seer_rdap_ip(ip) → IP address registration info (IPv4 or IPv6)
- seer_rdap_asn(asn) → Autonomous System info (integer)
- seer_dig(domain, record_type="A", nameserver=None) → DNS records
- seer_propagation(domain, record_type="A") → Propagation across 29 global servers
- seer_status(domain) → Health check (HTTP + SSL + expiry)
- seer_bulk_lookup(domains, concurrency=10) → Bulk registration data (max 100)
- seer_bulk_whois(domains, concurrency=10) → Bulk WHOIS data
- seer_bulk_dig(domains, record_type="A", concurrency=10) → Bulk DNS queries
- seer_bulk_status(domains, concurrency=10) → Bulk health checks
- seer_bulk_propagation(domains, record_type="A", concurrency=5) → Bulk propagation

### Tome — Reference Data
- tome_tld_lookup(tld) → TLD info (type, registry, WHOIS/RDAP servers)
- tome_tld_search(query) → Search TLDs by keyword
- tome_tld_overview(tld) → Comprehensive TLD detail
- tome_tld_list_by_type(tld_type) → List TLDs by category (gTLD/ccTLD/nTLD)
- tome_tld_count() → Total TLD count
- tome_record_lookup(query) → DNS record type details (by name or IANA code)
- tome_record_search(query) → Search record types by keyword
- tome_glossary_lookup(term) → Domain industry term definition
- tome_glossary_search(query) → Search glossary by keyword
"""


def _build_tool_use_prompt(
    topic: Topic,
    subcategory: Subcategory,
    category: Category,
    difficulty: str,
    count: int,
) -> str:
    """Build the meta-prompt for generating tool-use training examples."""
    profile = get_profile(difficulty)

    concepts_context = ""
    if topic.key_concepts:
        concepts_context = f"\nKey concepts: {', '.join(topic.key_concepts)}"

    return f"""You are generating TOOL-USE training data for a domain name expert AI model that has access to the Arcanum Suite tools.

{TOOL_DEFINITIONS}

## Topic
- Category: {category.name}
- Subcategory: {subcategory.name}
- Topic: {topic.name}
- Description: {topic.description}
{concepts_context}

## Difficulty: {difficulty.upper()}
- Target audience: {profile.audience}
- Answer depth: {profile.answer_depth}

## Instructions

Generate exactly {count} tool-use training example(s). Each example must follow this exact flow:

1. **user_question**: A natural question that requires using one or more tools to answer properly
2. **thinking**: The expert's internal reasoning about which tools to use and why (2-5 sentences showing the thought process: what data is needed, which tools provide it, what order to call them)
3. **assistant_reasoning**: The assistant's visible explanation of what they'll do (1-2 sentences)
4. **tool_calls**: Array of tool calls, each with "name" and "arguments" (valid JSON)
5. **tool_results**: Array of realistic tool responses (valid JSON strings — invent plausible data)
6. **interpretation_thinking**: The expert's internal reasoning about the results (2-4 sentences analyzing what the data means, spotting issues, connecting to domain knowledge)
7. **assistant_interpretation**: The assistant's visible interpretation with expert analysis

The assistant should:
- Think through which tools are needed and why before acting
- Choose the most appropriate tool(s) for the question
- After receiving results, reason about what the data means before responding
- Provide expert-level interpretation — not just parroting the data
- Add context, flag issues, suggest next steps where appropriate

Output as a JSON array of objects with those 7 fields. No markdown fencing, just raw JSON.

Important:
- Tool results must be realistic — invent plausible domain data (real TLD structures, believable WHOIS dates, realistic DNS records)
- The assistant interpretation is where the real expertise shows — connect raw data to meaning
- Vary the questions: some simple lookups, some multi-tool investigations, some troubleshooting
- For multi-tool examples, include multiple entries in tool_calls and tool_results arrays
"""


class ToolUseGenerator(BaseGenerator):
    """Generate tool-use training data showing how to use Arcanum Suite tools."""

    def __init__(
        self,
        output_dir: Path,
        provider: str = "anthropic",
        model: str | None = None,
        system_prompt: str | None = None,
        ollama_base_url: str = "http://localhost:11434/v1",
    ):
        super().__init__(output_dir, system_prompt)
        self.provider = provider
        self.ollama_base_url = ollama_base_url

        if model is None:
            self.model = {
                "anthropic": "claude-sonnet-4-20250514",
                "openai": "gpt-4o",
                "ollama": "nemotron-3-nano:latest",
            }.get(provider, "claude-sonnet-4-20250514")
        else:
            self.model = model

        self._client = None

    async def _get_client(self):
        """Lazy-initialize the API client."""
        if self._client is not None:
            return self._client

        if self.provider == "anthropic":
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic()
            except ImportError:
                raise RuntimeError(
                    "anthropic package required for tool-use generation. "
                    "Install with: pip install oracle[synthetic]"
                )
        elif self.provider == "openai":
            try:
                import openai
                self._client = openai.AsyncOpenAI()
            except ImportError:
                raise RuntimeError(
                    "openai package required for tool-use generation. "
                    "Install with: pip install oracle[synthetic]"
                )
        elif self.provider == "ollama":
            try:
                import openai
                self._client = openai.AsyncOpenAI(
                    base_url=self.ollama_base_url,
                    api_key="ollama",
                )
            except ImportError:
                raise RuntimeError(
                    "openai package required for Ollama support (OpenAI-compatible API). "
                    "Install with: pip install oracle[synthetic]"
                )
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        return self._client

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return the response text."""
        client = await self._get_client()

        if self.provider == "anthropic":
            response = await client.messages.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        elif self.provider in ("openai", "ollama"):
            response = await client.chat.completions.create(
                model=self.model,
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("LLM returned null content (finish_reason may be 'tool_calls' or 'length')")
            return content
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def generate(
        self,
        category: Category,
        subcategory: Subcategory,
        topic: Topic,
        difficulty: str = "intermediate",
        count: int = 1,
    ) -> list[TrainingExample]:
        """Generate tool-use training examples."""
        prompt = _build_tool_use_prompt(
            topic=topic,
            subcategory=subcategory,
            category=category,
            difficulty=difficulty,
            count=count,
        )

        logger.info(
            "Generating %d tool-use examples for %s/%s/%s [%s]",
            count, category.slug, subcategory.slug, topic.name, difficulty,
        )

        raw_response = await self._call_llm(prompt)

        # Parse LLM response with repair strategies
        from oracle.json_repair import parse_llm_json

        raw_examples = parse_llm_json(raw_response)
        if raw_examples is None:
            error_msg = (
                f"JSON parse failed (all repair strategies failed) [{len(raw_response)} chars]"
            )
            logger.error(
                "Failed to parse tool-use LLM response (all repair strategies failed) "
                "[%d chars]:\n%s", len(raw_response), raw_response[:1000],
            )
            self.save_failure(FailedGeneration(
                category=category.slug,
                subcategory=subcategory.slug,
                topic=topic.name,
                difficulty=difficulty,
                format=ExampleFormat.TOOL_USE,
                count=count,
                include_thinking=True,
                error=error_msg,
                provider=self.provider,
                model=self.model,
            ))
            return []

        # Convert to TrainingExample records
        examples: list[TrainingExample] = []
        next_seq = self._get_next_seq(category.slug, subcategory.slug)

        for i, raw in enumerate(raw_examples):
            if not isinstance(raw, dict):
                logger.warning(
                    "Skipping tool-use example %d: expected dict, got %s (%s)",
                    i, type(raw).__name__, str(raw)[:100],
                )
                continue

            try:
                messages = self._build_messages(raw)
                example = TrainingExample(
                    id=self.make_id(category.slug, subcategory.slug, next_seq + i),
                    category=category.slug,
                    subcategory=subcategory.slug,
                    topic=topic.name,
                    difficulty=difficulty,
                    format=ExampleFormat.TOOL_USE,
                    messages=messages,
                    sources=[],
                    generated_by=GenerationMethod.SYNTHETIC,
                )
                examples.append(example)
            except Exception as e:
                keys = list(raw.keys())
                logger.warning("Skipping invalid tool-use example %d (keys=%s): %s", i, keys, e)
                continue

        if not examples and raw_examples:
            error_msg = f"All {len(raw_examples)} parsed tool-use examples failed validation"
            self.save_failure(FailedGeneration(
                category=category.slug,
                subcategory=subcategory.slug,
                topic=topic.name,
                difficulty=difficulty,
                format=ExampleFormat.TOOL_USE,
                count=count,
                include_thinking=True,
                error=error_msg,
                provider=self.provider,
                model=self.model,
            ))

        logger.info("Generated %d valid tool-use examples (requested %d)", len(examples), count)
        return examples

    def _build_messages(self, raw: dict) -> list[Message]:
        """Convert raw LLM output into the tool-use message sequence."""
        messages: list[Message] = [
            Message(role=MessageRole.SYSTEM, content=self.system_prompt),
            Message(role=MessageRole.USER, content=raw["user_question"]),
        ]

        # Assistant reasoning + tool calls (with thinking about tool selection)
        tool_calls_raw = raw.get("tool_calls", [])
        tool_calls = [
            ToolCall(
                name=tc["name"],
                arguments=tc.get("arguments", {}),
            )
            for tc in tool_calls_raw
        ]

        messages.append(
            Message(
                role=MessageRole.ASSISTANT,
                content=raw["assistant_reasoning"],
                thinking=raw.get("thinking"),
                tool_calls=tool_calls if tool_calls else None,
            )
        )

        # Tool results
        tool_results = raw.get("tool_results", [])
        for j, result in enumerate(tool_results):
            result_str = json.dumps(result) if not isinstance(result, str) else result
            messages.append(
                Message(
                    role=MessageRole.TOOL,
                    content=result_str,
                    tool_call_id=f"call_{j}",
                )
            )

        # Assistant interpretation (with thinking about what results mean)
        messages.append(
            Message(
                role=MessageRole.ASSISTANT,
                content=raw["assistant_interpretation"],
                thinking=raw.get("interpretation_thinking"),
            )
        )

        return messages
