"""Difficulty levels for training examples.

Each level defines the expected audience, answer depth, and token budget
to guide both synthetic generation and quality validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Level(str, Enum):
    """Difficulty levels, ordered from least to most advanced."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass(frozen=True)
class DifficultyProfile:
    """Generation guidance for a difficulty level."""

    level: Level
    audience: str
    answer_depth: str
    min_tokens: int
    max_tokens: int
    example_framing: str


PROFILES: dict[Level, DifficultyProfile] = {
    Level.BEGINNER: DifficultyProfile(
        level=Level.BEGINNER,
        audience="Someone new to domain names — a small business owner, junior IT staff, or student.",
        answer_depth="Clear, jargon-light explanations with analogies. Define technical terms on first use. "
        "Focus on 'what' and 'why it matters', not implementation details.",
        min_tokens=150,
        max_tokens=600,
        example_framing="Explain in plain language, as if the reader has no prior DNS or domain knowledge.",
    ),
    Level.INTERMEDIATE: DifficultyProfile(
        level=Level.INTERMEDIATE,
        audience="A working professional who manages domains — IT admin, web developer, or brand manager.",
        answer_depth="Practical, operational detail. Assume familiarity with basic concepts. "
        "Include specific configurations, common pitfalls, and actionable guidance.",
        min_tokens=200,
        max_tokens=900,
        example_framing="Provide practical guidance suitable for someone who works with domains regularly.",
    ),
    Level.ADVANCED: DifficultyProfile(
        level=Level.ADVANCED,
        audience="A domain industry professional — registrar staff, registry engineer, IP attorney, or DNS operator.",
        answer_depth="Deep technical or policy detail. Reference specific RFCs, ICANN policies, or case law. "
        "Discuss edge cases, tradeoffs, and operational nuances.",
        min_tokens=300,
        max_tokens=1500,
        example_framing="Provide detailed, authoritative analysis suitable for an industry professional.",
    ),
    Level.EXPERT: DifficultyProfile(
        level=Level.EXPERT,
        audience="A recognized expert — protocol designer, ICANN policy veteran, UDRP panelist, or CA/B Forum member.",
        answer_depth="Comprehensive, authoritative treatment. Cite primary sources. Address competing interpretations, "
        "historical context, and forward-looking implications. This is reference-grade material.",
        min_tokens=500,
        max_tokens=2500,
        example_framing="Provide an exhaustive, reference-quality answer with citations and nuanced analysis.",
    ),
}


def get_profile(level: Level | str) -> DifficultyProfile:
    """Get the difficulty profile for a given level."""
    if isinstance(level, str):
        level = Level(level)
    return PROFILES[level]
