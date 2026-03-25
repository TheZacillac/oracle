"""Data augmentation for training examples.

Paraphrases questions to increase diversity and prevent the model from
memorizing phrasing patterns rather than learning concepts.
"""

from __future__ import annotations

import json
import logging
from copy import deepcopy

from oracle.schema import ExampleFormat, MessageRole, TrainingExample

logger = logging.getLogger(__name__)


PARAPHRASE_PROMPT = """Paraphrase the following question {count} different ways. Each paraphrase should:
- Ask about the same core topic
- Use a different sentence structure or phrasing
- Vary the level of specificity (some more direct, some more contextual)
- Sound natural — like a real person asking

Original question: {question}

Output as a JSON array of strings. No markdown fencing, just raw JSON.
"""


async def paraphrase_questions(
    examples: list[TrainingExample],
    provider: str = "anthropic",
    model: str | None = None,
    paraphrases_per_example: int = 2,
) -> list[TrainingExample]:
    """Generate paraphrased versions of existing training examples.

    Creates new examples with the same answers but differently-phrased questions.
    Only works with INSTRUCTION format (single user question → answer).

    Args:
        examples: Source examples to paraphrase.
        provider: LLM provider for paraphrasing.
        model: Model name override.
        paraphrases_per_example: Number of paraphrases per example.

    Returns:
        New examples with paraphrased questions (originals NOT included).
    """
    if model is None:
        model = {
            "anthropic": "claude-sonnet-4-20250514",
            "openai": "gpt-4o",
            "ollama": "nemotron-3-nano:latest",
        }.get(provider, "claude-sonnet-4-20250514")

    client = await _get_client(provider)
    augmented: list[TrainingExample] = []

    # Only paraphrase instruction format
    candidates = [e for e in examples if e.format == ExampleFormat.INSTRUCTION]
    logger.info("Paraphrasing %d instruction examples (%d paraphrases each)", len(candidates), paraphrases_per_example)

    for example in candidates:
        # Find the user message
        user_msg = next((m for m in example.messages if m.role == MessageRole.USER), None)
        if not user_msg:
            continue

        prompt = PARAPHRASE_PROMPT.format(
            question=user_msg.content,
            count=paraphrases_per_example,
        )

        try:
            response_text = await _call_llm(client, provider, model, prompt)
            text = response_text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[: text.rfind("```")]
            paraphrases = json.loads(text)

            if not isinstance(paraphrases, list):
                continue

            for i, para in enumerate(paraphrases[:paraphrases_per_example]):
                new_example = deepcopy(example)
                new_example.id = f"{example.id}-aug{i}"

                # Replace the user message content
                for msg in new_example.messages:
                    if msg.role == MessageRole.USER:
                        msg.content = para
                        break

                augmented.append(new_example)

        except Exception as e:
            logger.warning("Paraphrase failed for %s: %s", example.id, e)
            continue

    logger.info("Generated %d augmented examples", len(augmented))
    return augmented


async def _get_client(provider: str, ollama_base_url: str = "http://localhost:11434/v1"):
    """Get the LLM client."""
    if provider == "anthropic":
        import anthropic
        return anthropic.AsyncAnthropic()
    elif provider == "openai":
        import openai
        return openai.AsyncOpenAI()
    elif provider == "ollama":
        import openai
        return openai.AsyncOpenAI(base_url=ollama_base_url, api_key="ollama")
    raise ValueError(f"Unknown provider: {provider}")


async def _call_llm(client, provider: str, model: str, prompt: str) -> str:
    """Call the LLM."""
    if provider == "anthropic":
        response = await client.messages.create(
            model=model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    elif provider in ("openai", "ollama"):
        response = await client.chat.completions.create(
            model=model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    raise ValueError(f"Unknown provider: {provider}")
