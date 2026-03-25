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
2. **assistant_reasoning**: The assistant explains which tool(s) to use and why (1-2 sentences)
3. **tool_calls**: Array of tool calls, each with "name" and "arguments" (valid JSON)
4. **tool_results**: Array of realistic tool responses (valid JSON strings — invent plausible data)
5. **assistant_interpretation**: The assistant interprets the results, providing expert analysis

The assistant should:
- Choose the most appropriate tool(s) for the question
- Explain WHY it's using that tool before calling it
- After receiving results, provide expert-level interpretation — not just parroting the data
- Add context, flag issues, suggest next steps where appropriate

Output as a JSON array of objects with those 5 fields. No markdown fencing, just raw JSON.

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
    ):
        super().__init__(output_dir, system_prompt)
        self.provider = provider

        if model is None:
            self.model = {
                "anthropic": "claude-sonnet-4-20250514",
                "openai": "gpt-4o",
            }.get(provider, "claude-sonnet-4-20250514")
        else:
            self.model = model

        self._client = None

    async def _get_client(self):
        """Lazy-initialize the API client."""
        if self._client is not None:
            return self._client

        if self.provider == "anthropic":
            import anthropic
            self._client = anthropic.AsyncAnthropic()
        elif self.provider == "openai":
            import openai
            self._client = openai.AsyncOpenAI()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        return self._client

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM and return the response text."""
        client = await self._get_client()

        if self.provider == "anthropic":
            response = await client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        elif self.provider == "openai":
            response = await client.chat.completions.create(
                model=self.model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
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

        # Parse LLM response
        try:
            text = raw_response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[: text.rfind("```")]
            raw_examples = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse tool-use LLM response:\n%s", raw_response[:500])
            return []

        if not isinstance(raw_examples, list):
            raw_examples = [raw_examples]

        # Convert to TrainingExample records
        examples: list[TrainingExample] = []
        next_seq = self._get_next_seq(category.slug, subcategory.slug)

        for i, raw in enumerate(raw_examples):
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
                logger.warning("Skipping invalid tool-use example %d: %s", i, e)
                continue

        logger.info("Generated %d valid tool-use examples (requested %d)", len(examples), count)
        return examples

    def _build_messages(self, raw: dict) -> list[Message]:
        """Convert raw LLM output into the tool-use message sequence."""
        messages: list[Message] = [
            Message(role=MessageRole.SYSTEM, content=self.system_prompt),
            Message(role=MessageRole.USER, content=raw["user_question"]),
        ]

        # Assistant reasoning + tool calls
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

        # Assistant interpretation
        messages.append(
            Message(
                role=MessageRole.ASSISTANT,
                content=raw["assistant_interpretation"],
            )
        )

        return messages
