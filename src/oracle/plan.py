"""Generation plan — configuration and execution for balanced dataset generation.

A plan defines target counts per category, difficulty, and format, then
orchestrates generators to produce a balanced dataset.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from pathlib import Path

from oracle.difficulty import Level
from oracle.schema import ExampleFormat, FailedGeneration
from oracle.taxonomy import TAXONOMY, Category, get_category

logger = logging.getLogger(__name__)


@dataclass
class FormatMix:
    """Target format distribution (fractions must sum to 1.0)."""

    instruction: float = 0.55
    multi_turn: float = 0.15
    scenario: float = 0.15
    tool_use: float = 0.15

    def to_counts(self, total: int) -> dict[ExampleFormat, int]:
        """Convert fractions to concrete counts for a given total."""
        counts = {
            ExampleFormat.INSTRUCTION: round(total * self.instruction),
            ExampleFormat.MULTI_TURN: round(total * self.multi_turn),
            ExampleFormat.SCENARIO: round(total * self.scenario),
            ExampleFormat.TOOL_USE: round(total * self.tool_use),
        }
        # Adjust for rounding errors
        diff = total - sum(counts.values())
        counts[ExampleFormat.INSTRUCTION] += diff
        return counts


@dataclass
class DifficultyMix:
    """Target difficulty distribution (fractions must sum to 1.0)."""

    beginner: float = 0.20
    intermediate: float = 0.35
    advanced: float = 0.30
    expert: float = 0.15

    def to_counts(self, total: int) -> dict[str, int]:
        """Convert fractions to concrete counts."""
        counts = {
            "beginner": round(total * self.beginner),
            "intermediate": round(total * self.intermediate),
            "advanced": round(total * self.advanced),
            "expert": round(total * self.expert),
        }
        diff = total - sum(counts.values())
        counts["intermediate"] += diff
        return counts


@dataclass
class CategoryPlan:
    """Generation target for a single category."""

    slug: str
    total_examples: int
    difficulty_mix: DifficultyMix | None = None  # None = use plan default
    format_mix: FormatMix | None = None  # None = use plan default


@dataclass
class GenerationPlan:
    """Full generation plan for the dataset."""

    name: str = "oracle-domain-expert"
    version: str = "0.1.0"

    # Default distributions
    default_difficulty: DifficultyMix = field(default_factory=DifficultyMix)
    default_format: FormatMix = field(default_factory=FormatMix)

    # Per-category targets (if empty, uses default_per_topic for all categories)
    categories: list[CategoryPlan] = field(default_factory=list)

    # Default examples per topic when no category plan is specified
    default_per_topic: int = 10

    # Reasoning split — Nemotron-3-Nano recommends 75% reasoning / 25% non-reasoning
    # to preserve the model's reasoning capabilities during fine-tuning
    thinking_ratio: float = 0.75  # Fraction of examples that include <think> traces

    # Generation settings
    provider: str = "anthropic"
    model: str | None = None
    batch_size: int = 5  # Examples per LLM call

    def get_category_plan(self, slug: str) -> CategoryPlan | None:
        """Get the plan for a specific category."""
        return next((c for c in self.categories if c.slug == slug), None)


# ---------------------------------------------------------------------------
# Preset plans
# ---------------------------------------------------------------------------

def plan_small() -> GenerationPlan:
    """Small dataset for testing (~1,500 examples)."""
    return GenerationPlan(
        name="oracle-domain-expert",
        version="0.1.0-small",
        default_per_topic=3,
        default_difficulty=DifficultyMix(
            beginner=0.25, intermediate=0.40, advanced=0.25, expert=0.10,
        ),
        default_format=FormatMix(
            instruction=0.70, multi_turn=0.10, scenario=0.10, tool_use=0.10,
        ),
    )


def plan_medium() -> GenerationPlan:
    """Medium dataset for initial training (~4,000 examples)."""
    return GenerationPlan(
        name="oracle-domain-expert",
        version="0.1.0-medium",
        default_per_topic=10,
        default_difficulty=DifficultyMix(
            beginner=0.20, intermediate=0.35, advanced=0.30, expert=0.15,
        ),
        default_format=FormatMix(
            instruction=0.55, multi_turn=0.15, scenario=0.15, tool_use=0.15,
        ),
    )


def plan_large() -> GenerationPlan:
    """Large comprehensive dataset (~10,000+ examples)."""
    return GenerationPlan(
        name="oracle-domain-expert",
        version="0.1.0-large",
        default_per_topic=25,
        default_difficulty=DifficultyMix(
            beginner=0.20, intermediate=0.35, advanced=0.30, expert=0.15,
        ),
        default_format=FormatMix(
            instruction=0.50, multi_turn=0.15, scenario=0.20, tool_use=0.15,
        ),
    )


# ---------------------------------------------------------------------------
# Plan executor
# ---------------------------------------------------------------------------

async def execute_plan(
    plan: GenerationPlan,
    output_dir: Path,
    categories: list[str] | None = None,
) -> dict[str, int]:
    """Execute a generation plan, producing a balanced dataset.

    Args:
        plan: The generation plan to execute.
        output_dir: Directory to write generated examples.
        categories: Optional list of category slugs to generate (default: all).

    Returns:
        Dict of {category_slug: examples_generated}.
    """
    from oracle.generators.synthetic import SyntheticGenerator
    from oracle.generators.tool_use import ToolUseGenerator

    output_dir.mkdir(parents=True, exist_ok=True)

    synth = SyntheticGenerator(
        output_dir=output_dir,
        provider=plan.provider,
        model=plan.model,
    )
    tool_gen = ToolUseGenerator(
        output_dir=output_dir,
        provider=plan.provider,
        model=plan.model,
    )

    import random
    rng = random.Random(42)

    target_categories = categories or [c.slug for c in TAXONOMY]
    results: dict[str, int] = {}

    for cat_slug in target_categories:
        cat = get_category(cat_slug)
        if not cat:
            logger.warning("Unknown category: %s, skipping", cat_slug)
            continue

        cat_plan = plan.get_category_plan(cat_slug)
        diff_mix = (cat_plan.difficulty_mix if cat_plan and cat_plan.difficulty_mix else plan.default_difficulty)
        fmt_mix = (cat_plan.format_mix if cat_plan and cat_plan.format_mix else plan.default_format)

        # Calculate per-topic counts
        topic_count = sum(len(s.topics) for s in cat.subcategories)
        if cat_plan:
            per_topic = max(1, cat_plan.total_examples // max(topic_count, 1))
        else:
            per_topic = plan.default_per_topic

        diff_counts = diff_mix.to_counts(per_topic)
        cat_total = 0

        for difficulty, diff_count in diff_counts.items():
            if diff_count == 0:
                continue

            fmt_counts = fmt_mix.to_counts(diff_count)

            for fmt, fmt_count in fmt_counts.items():
                if fmt_count == 0:
                    continue

                if fmt == ExampleFormat.TOOL_USE:
                    # Only generate tool-use for the tools category or a subset of others
                    if cat_slug == "tools":
                        gen = tool_gen
                    else:
                        # For non-tool categories, convert tool_use budget to instruction
                        fmt = ExampleFormat.INSTRUCTION
                        gen = synth
                else:
                    gen = synth

                for sub in cat.subcategories:
                    for topic in sub.topics:
                        # Check difficulty range
                        levels = list(Level)
                        try:
                            min_d = Level(topic.difficulty_range[0])
                            max_d = Level(topic.difficulty_range[1])
                            req_d = Level(difficulty)
                            if levels.index(req_d) < levels.index(min_d):
                                continue
                            if levels.index(req_d) > levels.index(max_d):
                                continue
                        except ValueError:
                            pass

                        # Decide whether this batch includes thinking traces
                        # based on the plan's thinking_ratio (default 75%)
                        include_thinking = rng.random() < plan.thinking_ratio

                        batch_count = min(fmt_count, plan.batch_size)
                        try:
                            if fmt == ExampleFormat.TOOL_USE:
                                examples = await gen.generate(
                                    category=cat,
                                    subcategory=sub,
                                    topic=topic,
                                    difficulty=difficulty,
                                    count=batch_count,
                                )
                            else:
                                examples = await gen.generate(
                                    category=cat,
                                    subcategory=sub,
                                    topic=topic,
                                    difficulty=difficulty,
                                    count=batch_count,
                                    format_type=fmt,
                                    include_thinking=include_thinking,
                                )
                            gen.save_examples(examples)
                            cat_total += len(examples)
                        except Exception as e:
                            logger.error(
                                "Failed generating %s/%s/%s [%s/%s]: %s",
                                cat_slug, sub.slug, topic.name, difficulty, fmt.value, e,
                            )
                            # Record failure for retry (LLM call or unexpected error)
                            gen.save_failure(FailedGeneration(
                                category=cat_slug,
                                subcategory=sub.slug,
                                topic=topic.name,
                                difficulty=difficulty,
                                format=fmt,
                                count=batch_count,
                                include_thinking=include_thinking,
                                error=str(e),
                                provider=plan.provider,
                                model=plan.model or "",
                            ))

        results[cat_slug] = cat_total
        logger.info("Category %s: generated %d examples", cat_slug, cat_total)

    return results
