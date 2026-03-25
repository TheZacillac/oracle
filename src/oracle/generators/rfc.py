"""RFC-based training data extraction.

Fetches RFCs referenced in the taxonomy, parses them into sections,
and generates Q&A pairs grounded in specific RFC text.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import httpx

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

RFC_BASE_URL = "https://www.rfc-editor.org/rfc"


def parse_rfc_number(ref: str) -> str | None:
    """Extract RFC number from a reference like 'RFC 1035' or 'RFC 1035 Section 3.2'."""
    match = re.match(r"RFC\s*(\d+)", ref, re.IGNORECASE)
    return match.group(1) if match else None


def split_rfc_sections(text: str) -> list[dict[str, str]]:
    """Split an RFC into sections based on numbered headings.

    Returns a list of {heading, number, content} dicts.
    """
    # Match patterns like "3.2.1.  Section Title" or "3.  Title"
    section_pattern = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", re.MULTILINE)

    sections = []
    matches = list(section_pattern.finditer(text))

    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()

        # Skip very short sections (likely just a heading with no content)
        if len(content) < 50:
            continue

        sections.append({
            "number": match.group(1).rstrip("."),
            "heading": match.group(2).strip(),
            "content": content[:3000],  # Cap section length
        })

    return sections


class RfcGenerator(BaseGenerator):
    """Generate training data from RFC documents.

    This generator fetches RFCs, splits them into sections, and creates
    Q&A pairs where the answer is grounded in specific RFC text. It can
    optionally use an LLM to reformulate the raw RFC content into more
    natural Q&A format.
    """

    def __init__(
        self,
        output_dir: Path,
        cache_dir: Path | None = None,
        system_prompt: str | None = None,
    ):
        super().__init__(output_dir, system_prompt)
        self.cache_dir = cache_dir or (output_dir.parent / "sources" / "rfcs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_rfc(self, rfc_number: str) -> str | None:
        """Fetch an RFC as plain text, using cache if available."""
        cache_file = self.cache_dir / f"rfc{rfc_number}.txt"

        if cache_file.exists():
            logger.debug("Using cached RFC %s", rfc_number)
            return cache_file.read_text()

        url = f"{RFC_BASE_URL}/rfc{rfc_number}.txt"
        logger.info("Fetching RFC %s from %s", rfc_number, url)

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text
                cache_file.write_text(text)
                return text
            except httpx.HTTPError as e:
                logger.error("Failed to fetch RFC %s: %s", rfc_number, e)
                return None

    def _section_to_example(
        self,
        section: dict[str, str],
        rfc_number: str,
        category: Category,
        subcategory: Subcategory,
        topic: Topic,
        seq: int,
    ) -> TrainingExample | None:
        """Convert an RFC section into a training example."""
        heading = section["heading"]
        content = section["content"]

        # Generate a natural question from the section heading
        question = f"What does RFC {rfc_number} specify about {heading.lower()}?"

        # Format the answer with the RFC content
        answer = (
            f"RFC {rfc_number}, Section {section['number']} ({heading}) specifies the following:\n\n"
            f"{content}\n\n"
            f"This is defined in RFC {rfc_number}, which covers {topic.description.lower()}"
        )

        try:
            return TrainingExample(
                id=self.make_id(category.slug, subcategory.slug, seq),
                category=category.slug,
                subcategory=subcategory.slug,
                topic=topic.name,
                difficulty="advanced",
                format=ExampleFormat.INSTRUCTION,
                messages=[
                    Message(role=MessageRole.SYSTEM, content=self.system_prompt),
                    Message(role=MessageRole.USER, content=question),
                    Message(role=MessageRole.ASSISTANT, content=answer),
                ],
                sources=[f"RFC {rfc_number} Section {section['number']}"],
                generated_by=GenerationMethod.RFC_EXTRACTION,
            )
        except Exception as e:
            logger.warning("Failed to create example from RFC %s section %s: %s", rfc_number, section["number"], e)
            return None

    async def generate(
        self,
        category: Category,
        subcategory: Subcategory,
        topic: Topic,
        difficulty: str = "advanced",
        count: int = 10,
    ) -> list[TrainingExample]:
        """Generate training examples from RFCs referenced by a topic."""
        examples: list[TrainingExample] = []
        next_seq = self._get_next_seq(category.slug, subcategory.slug)

        for rfc_ref in topic.rfcs:
            rfc_number = parse_rfc_number(rfc_ref)
            if not rfc_number:
                continue

            text = await self.fetch_rfc(rfc_number)
            if not text:
                continue

            sections = split_rfc_sections(text)
            logger.info("RFC %s: found %d sections", rfc_number, len(sections))

            for section in sections[:count]:
                example = self._section_to_example(
                    section=section,
                    rfc_number=rfc_number,
                    category=category,
                    subcategory=subcategory,
                    topic=topic,
                    seq=next_seq + len(examples),
                )
                if example:
                    examples.append(example)

                if len(examples) >= count:
                    break

            if len(examples) >= count:
                break

        return examples

    async def fetch_all_taxonomy_rfcs(self) -> dict[str, Path]:
        """Fetch and cache all RFCs referenced anywhere in the taxonomy.

        Returns a mapping of RFC number to cache file path.
        """
        from oracle.taxonomy import all_topics

        rfc_numbers: set[str] = set()
        for _cat, _sub, topic in all_topics():
            for ref in topic.rfcs:
                num = parse_rfc_number(ref)
                if num:
                    rfc_numbers.add(num)

        logger.info("Fetching %d unique RFCs from taxonomy", len(rfc_numbers))

        results: dict[str, Path] = {}
        for num in sorted(rfc_numbers):
            text = await self.fetch_rfc(num)
            if text:
                results[num] = self.cache_dir / f"rfc{num}.txt"

        return results
