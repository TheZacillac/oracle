"""Quality validation for training examples.

Checks format, deduplicates, estimates token counts, and filters
low-quality examples before export.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from oracle.difficulty import Level, get_profile
from oracle.schema import TrainingExample

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a set of training examples."""

    valid: list[TrainingExample] = field(default_factory=list)
    rejected: list[tuple[TrainingExample, str]] = field(default_factory=list)
    duplicates_removed: int = 0
    token_counts_set: int = 0


def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars per token heuristic).

    For accurate counts, use tiktoken when available.
    """
    try:
        import tiktoken

        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return len(text) // 4


def validate_example(example: TrainingExample) -> tuple[bool, str]:
    """Validate a single training example.

    Returns (is_valid, reason_if_invalid).
    """
    # Check message content isn't empty/trivial
    for msg in example.messages:
        if len(msg.content.strip()) < 10:
            return False, f"Message too short: role={msg.role.value}, len={len(msg.content)}"

    # Check assistant response meets minimum depth for difficulty
    assistant_messages = [m for m in example.messages if m.role.value == "assistant"]
    if not assistant_messages:
        return False, "No assistant message found"

    total_assistant_text = " ".join(m.content for m in assistant_messages)
    token_count = estimate_tokens(total_assistant_text)

    try:
        profile = get_profile(example.difficulty)
        if token_count < profile.min_tokens * 0.5:  # Allow 50% slack
            return False, (
                f"Assistant response too short for {example.difficulty}: "
                f"{token_count} tokens (min ~{profile.min_tokens})"
            )
    except (ValueError, KeyError):
        pass  # Unknown difficulty level, skip this check

    # Check for obvious generation artifacts
    artifacts = [
        "as an ai",
        "i cannot",
        "i don't have access",
        "i'm not able to",
        "i apologize, but",
    ]
    lower_text = total_assistant_text.lower()
    for artifact in artifacts:
        if artifact in lower_text:
            return False, f"Contains generation artifact: '{artifact}'"

    return True, ""


def validate_and_deduplicate(
    examples: list[TrainingExample],
    strict: bool = False,
) -> ValidationResult:
    """Validate a batch of examples, removing duplicates and low-quality entries.

    Args:
        examples: List of examples to validate.
        strict: If True, apply stricter quality thresholds.

    Returns:
        ValidationResult with valid examples and rejection details.
    """
    result = ValidationResult()
    seen_hashes: set[str] = set()

    for example in examples:
        # Deduplication
        content_hash = example.content_hash
        if content_hash in seen_hashes:
            result.duplicates_removed += 1
            continue
        seen_hashes.add(content_hash)

        # Set token count
        total_text = " ".join(m.content for m in example.messages)
        token_count = estimate_tokens(total_text)
        example.token_count = token_count
        result.token_counts_set += 1

        # Validate
        is_valid, reason = validate_example(example)

        if strict and is_valid:
            # Additional strict checks
            if token_count > 5000:
                is_valid = False
                reason = f"Example too long: {token_count} tokens"

        if is_valid:
            result.valid.append(example)
        else:
            result.rejected.append((example, reason))
            logger.debug("Rejected %s: %s", example.id, reason)

    logger.info(
        "Validation complete: %d valid, %d rejected, %d duplicates removed",
        len(result.valid),
        len(result.rejected),
        result.duplicates_removed,
    )

    return result
