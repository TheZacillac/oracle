"""Synthetic training data generator using LLM APIs.

Generates expert Q&A pairs by prompting an LLM with topic context,
difficulty guidance, and format instructions, then validating the output.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from oracle.difficulty import Level, get_profile
from oracle.generators.base import BaseGenerator
from oracle.schema import (
    ExampleFormat,
    GenerationMethod,
    Message,
    MessageRole,
    TrainingExample,
)
from oracle.taxonomy import Category, Subcategory, Topic

logger = logging.getLogger(__name__)


def _build_generation_prompt(
    topic: Topic,
    subcategory: Subcategory,
    category: Category,
    difficulty: str,
    format_type: ExampleFormat,
    count: int,
) -> str:
    """Build the meta-prompt that instructs the LLM to generate training examples."""
    profile = get_profile(difficulty)

    rfc_context = ""
    if topic.rfcs:
        rfc_context = f"\nRelevant RFCs: {', '.join(topic.rfcs)}"

    concepts_context = ""
    if topic.key_concepts:
        concepts_context = f"\nKey concepts to cover: {', '.join(topic.key_concepts)}"

    # Format-specific instructions and JSON schema
    if format_type == ExampleFormat.INSTRUCTION:
        format_instruction = (
            "Generate single-turn Q&A pairs. Each has one user question and one expert answer."
        )
        json_schema = (
            '- "question": The user\'s question (natural, varied phrasing)\n'
            '- "answer": The expert\'s response\n'
            '- "sources": List of source references (RFCs, ICANN documents, etc.)'
        )
    elif format_type == ExampleFormat.MULTI_TURN:
        format_instruction = (
            "Generate multi-turn conversations (2-4 exchanges). The user asks a question, "
            "gets an answer, then follows up with deeper or related questions. Each follow-up "
            "should build on the previous answer — going deeper, asking for clarification, or "
            "exploring a related aspect."
        )
        json_schema = (
            '- "turns": Array of exchanges, each with "user" and "assistant" strings\n'
            '  Example: [{"user": "...", "assistant": "..."}, {"user": "...", "assistant": "..."}]\n'
            '- "sources": List of source references'
        )
    elif format_type == ExampleFormat.SCENARIO:
        format_instruction = (
            "Generate scenario-based problems. The user describes a real-world situation "
            "(e.g., a migration gone wrong, a brand protection emergency, a DNS outage, "
            "a compliance question) and asks for expert guidance. The assistant provides "
            "structured analysis with diagnosis, recommendations, and next steps."
        )
        json_schema = (
            '- "scenario": The user\'s scenario description and question\n'
            '- "analysis": The expert\'s structured response (diagnosis + recommendations + next steps)\n'
            '- "sources": List of source references'
        )
    else:
        format_instruction = "Generate single-turn Q&A pairs."
        json_schema = '- "question": ...\n- "answer": ...\n- "sources": [...]'

    return f"""You are generating training data for a domain name industry expert AI model.

## Topic
- Category: {category.name}
- Subcategory: {subcategory.name}
- Topic: {topic.name}
- Description: {topic.description}
{rfc_context}
{concepts_context}

## Difficulty: {difficulty.upper()}
- Target audience: {profile.audience}
- Answer depth: {profile.answer_depth}
- Token budget per answer: {profile.min_tokens}-{profile.max_tokens} tokens

## Format
{format_instruction}

## Instructions
Generate exactly {count} training example(s). For each example, output a JSON object with:
{json_schema}

Vary the question/scenario style across examples. Mix direct questions, comparisons,
troubleshooting, "how does X work", and real-world situations.

The expert responses must be:
1. Technically accurate and up to date
2. Grounded in primary sources where applicable
3. Actionable and practical, not just theoretical
4. Within the token budget for this difficulty level

Output as a JSON array of objects. No markdown fencing, just raw JSON.
"""


class SyntheticGenerator(BaseGenerator):
    """Generate training data by prompting an LLM.

    Supports Anthropic (Claude) and OpenAI-compatible APIs.
    """

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
            try:
                import anthropic

                self._client = anthropic.AsyncAnthropic()
            except ImportError:
                raise RuntimeError(
                    "anthropic package required for synthetic generation. "
                    "Install with: pip install oracle[synthetic]"
                )
        elif self.provider == "openai":
            try:
                import openai

                self._client = openai.AsyncOpenAI()
            except ImportError:
                raise RuntimeError(
                    "openai package required for synthetic generation. "
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
        difficulty: str,
        count: int = 1,
        format_type: ExampleFormat = ExampleFormat.INSTRUCTION,
    ) -> list[TrainingExample]:
        """Generate synthetic training examples for a topic."""
        prompt = _build_generation_prompt(
            topic=topic,
            subcategory=subcategory,
            category=category,
            difficulty=difficulty,
            format_type=format_type,
            count=count,
        )

        logger.info(
            "Generating %d %s examples for %s/%s/%s [%s]",
            count,
            format_type.value,
            category.slug,
            subcategory.slug,
            topic.name,
            difficulty,
        )

        raw_response = await self._call_llm(prompt)

        # Parse the LLM response
        try:
            # Strip markdown code fences if present
            text = raw_response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[: text.rfind("```")]
            raw_examples = json.loads(text)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON:\n%s", raw_response[:500])
            return []

        if not isinstance(raw_examples, list):
            raw_examples = [raw_examples]

        # Convert to TrainingExample records
        examples: list[TrainingExample] = []
        next_seq = self._get_next_seq(category.slug, subcategory.slug)

        for i, raw in enumerate(raw_examples):
            try:
                messages = self._build_messages(raw, format_type)

                example = TrainingExample(
                    id=self.make_id(category.slug, subcategory.slug, next_seq + i),
                    category=category.slug,
                    subcategory=subcategory.slug,
                    topic=topic.name,
                    difficulty=difficulty,
                    format=format_type,
                    messages=messages,
                    sources=raw.get("sources", topic.rfcs),
                    generated_by=GenerationMethod.SYNTHETIC,
                )
                examples.append(example)
            except Exception as e:
                logger.warning("Skipping invalid example %d: %s", i, e)
                continue

        logger.info("Generated %d valid examples (requested %d)", len(examples), count)
        return examples

    def _build_messages(self, raw: dict, format_type: ExampleFormat) -> list[Message]:
        """Build message list from raw LLM output based on format type."""
        messages = [Message(role=MessageRole.SYSTEM, content=self.system_prompt)]

        if format_type == ExampleFormat.INSTRUCTION:
            messages.append(Message(role=MessageRole.USER, content=raw["question"]))
            messages.append(Message(role=MessageRole.ASSISTANT, content=raw["answer"]))

        elif format_type == ExampleFormat.MULTI_TURN:
            # Multi-turn: alternating user/assistant exchanges
            turns = raw.get("turns", [])
            if not turns:
                # Fallback: treat as single-turn
                messages.append(Message(role=MessageRole.USER, content=raw.get("question", "")))
                messages.append(Message(role=MessageRole.ASSISTANT, content=raw.get("answer", "")))
            else:
                for turn in turns:
                    messages.append(Message(role=MessageRole.USER, content=turn["user"]))
                    messages.append(Message(role=MessageRole.ASSISTANT, content=turn["assistant"]))

        elif format_type == ExampleFormat.SCENARIO:
            # Scenario: user describes situation, assistant provides structured analysis
            messages.append(Message(role=MessageRole.USER, content=raw["scenario"]))
            messages.append(Message(role=MessageRole.ASSISTANT, content=raw["analysis"]))

        else:
            # Default fallback
            messages.append(Message(role=MessageRole.USER, content=raw.get("question", "")))
            messages.append(Message(role=MessageRole.ASSISTANT, content=raw.get("answer", "")))

        return messages

    async def generate_category(
        self,
        category: Category,
        difficulty: str,
        count_per_topic: int = 3,
        format_type: ExampleFormat = ExampleFormat.INSTRUCTION,
    ) -> list[TrainingExample]:
        """Generate examples for every topic in a category."""
        all_examples: list[TrainingExample] = []

        for sub in category.subcategories:
            for topic in sub.topics:
                # Check if topic's difficulty range covers the requested level
                min_diff = Level(topic.difficulty_range[0])
                max_diff = Level(topic.difficulty_range[1])
                req_diff = Level(difficulty)

                levels = list(Level)
                if levels.index(req_diff) < levels.index(min_diff):
                    continue
                if levels.index(req_diff) > levels.index(max_diff):
                    continue

                examples = await self.generate(
                    category=category,
                    subcategory=sub,
                    topic=topic,
                    difficulty=difficulty,
                    count=count_per_topic,
                    format_type=format_type,
                )
                all_examples.extend(examples)
                self.save_examples(examples)

        return all_examples
