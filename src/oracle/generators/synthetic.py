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
    include_thinking: bool = True,
) -> str:
    """Build the meta-prompt that instructs the LLM to generate training examples."""
    profile = get_profile(difficulty)

    rfc_context = ""
    if topic.rfcs:
        rfc_context = f"\nRelevant RFCs: {', '.join(topic.rfcs)}"

    concepts_context = ""
    if topic.key_concepts:
        concepts_context = f"\nKey concepts to cover: {', '.join(topic.key_concepts)}"

    # Thinking trace instructions
    thinking_instruction = ""
    thinking_schema = ""
    if include_thinking:
        thinking_instruction = (
            "\n## Reasoning Traces\n"
            "Each assistant response MUST include a thinking trace — the expert's internal reasoning "
            "before formulating the answer. This should show HOW the expert arrives at the answer: "
            "which sources to consult, what factors to weigh, what the key distinctions are.\n"
            "The thinking trace should be natural reasoning, not a summary of the answer."
        )
        thinking_schema = (
            '- "thinking": The expert\'s internal reasoning process (2-5 sentences showing how they '
            'approach the question — which sources apply, what distinctions matter, what to check)\n'
        )

    # Format-specific instructions and JSON schema
    if format_type == ExampleFormat.INSTRUCTION:
        format_instruction = (
            "Generate single-turn Q&A pairs. Each has one user question and one expert answer."
        )
        json_schema = (
            '- "question": The user\'s question (natural, varied phrasing)\n'
            f'{thinking_schema}'
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
            '- "turns": Array of exchanges, each with "user", "thinking", and "assistant" strings\n'
            '  Example: [{"user": "...", "thinking": "...", "assistant": "..."}, ...]\n'
            '- "sources": List of source references'
        ) if include_thinking else (
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
            f'{thinking_schema}'
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
{thinking_instruction}

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

    Supports Anthropic (Claude), OpenAI, and Ollama (via OpenAI-compatible API).
    """

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
        elif self.provider == "ollama":
            try:
                import openai

                self._client = openai.AsyncOpenAI(
                    base_url=self.ollama_base_url,
                    api_key="ollama",  # Ollama doesn't need a real key
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
        include_thinking: bool = True,
    ) -> list[TrainingExample]:
        """Generate synthetic training examples for a topic."""
        prompt = _build_generation_prompt(
            topic=topic,
            subcategory=subcategory,
            category=category,
            difficulty=difficulty,
            format_type=format_type,
            count=count,
            include_thinking=include_thinking,
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

        # Parse the LLM response with repair strategies
        from oracle.json_repair import parse_llm_json

        raw_examples = parse_llm_json(raw_response)
        if raw_examples is None:
            logger.error("Failed to parse LLM response as JSON (all repair strategies failed):\n%s", raw_response[:500])
            return []

        # Convert to TrainingExample records
        examples: list[TrainingExample] = []
        next_seq = self._get_next_seq(category.slug, subcategory.slug)

        for i, raw in enumerate(raw_examples):
            # Skip non-dict items (LLM sometimes returns strings instead of objects)
            if not isinstance(raw, dict):
                logger.warning(
                    "Skipping example %d: expected dict, got %s (%s)",
                    i, type(raw).__name__, str(raw)[:100],
                )
                continue

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
                keys = list(raw.keys())
                logger.warning("Skipping invalid example %d (keys=%s): %s", i, keys, e)
                continue

        logger.info("Generated %d valid examples (requested %d)", len(examples), count)
        return examples

    @staticmethod
    def _get_key(raw: dict, *candidates: str) -> str:
        """Get a value by trying multiple key names.

        LLMs don't always use the exact key names from the prompt.
        Common variations: question/prompt/query/input, answer/response/output.
        """
        for key in candidates:
            if key in raw and raw[key]:
                return raw[key]
        # If nothing found, log what keys ARE present and raise
        available = list(raw.keys())
        raise KeyError(
            f"None of {list(candidates)} found in response. "
            f"Available keys: {available}"
        )

    def _build_messages(self, raw: dict, format_type: ExampleFormat) -> list[Message]:
        """Build message list from raw LLM output based on format type."""
        messages = [Message(role=MessageRole.SYSTEM, content=self.system_prompt)]

        if format_type == ExampleFormat.INSTRUCTION:
            question = self._get_key(raw, "question", "prompt", "query", "input", "user", "user_question")
            answer = self._get_key(raw, "answer", "response", "output", "assistant", "assistant_response")
            messages.append(Message(role=MessageRole.USER, content=question))
            messages.append(Message(
                role=MessageRole.ASSISTANT,
                content=answer,
                thinking=raw.get("thinking"),
            ))

        elif format_type == ExampleFormat.MULTI_TURN:
            turns = raw.get("turns", raw.get("conversation", []))
            if not turns:
                question = self._get_key(raw, "question", "prompt", "query", "input", "user")
                answer = self._get_key(raw, "answer", "response", "output", "assistant")
                messages.append(Message(role=MessageRole.USER, content=question))
                messages.append(Message(
                    role=MessageRole.ASSISTANT,
                    content=answer,
                    thinking=raw.get("thinking"),
                ))
            else:
                for turn in turns:
                    user_msg = self._get_key(turn, "user", "question", "prompt", "input")
                    asst_msg = self._get_key(turn, "assistant", "answer", "response", "output")
                    messages.append(Message(role=MessageRole.USER, content=user_msg))
                    messages.append(Message(
                        role=MessageRole.ASSISTANT,
                        content=asst_msg,
                        thinking=turn.get("thinking"),
                    ))

        elif format_type == ExampleFormat.SCENARIO:
            scenario = self._get_key(raw, "scenario", "situation", "problem", "question", "user")
            analysis = self._get_key(raw, "analysis", "answer", "response", "solution", "assistant")
            messages.append(Message(role=MessageRole.USER, content=scenario))
            messages.append(Message(
                role=MessageRole.ASSISTANT,
                content=analysis,
                thinking=raw.get("thinking"),
            ))

        else:
            question = self._get_key(raw, "question", "prompt", "query", "input", "user")
            answer = self._get_key(raw, "answer", "response", "output", "assistant")
            messages.append(Message(role=MessageRole.USER, content=question))
            messages.append(Message(
                role=MessageRole.ASSISTANT,
                content=answer,
                thinking=raw.get("thinking"),
            ))

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
