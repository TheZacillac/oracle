"""RFC source document fetcher and parser.

Fetches RFCs from the IETF RFC Editor and provides structured access
to their content for training data generation.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

RFC_TEXT_URL = "https://www.rfc-editor.org/rfc/rfc{number}.txt"
RFC_JSON_URL = "https://www.rfc-editor.org/rfc/rfc{number}.json"
RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.txt"


@dataclass
class RfcSection:
    """A parsed section from an RFC."""

    number: str
    heading: str
    content: str
    depth: int = 0


@dataclass
class RfcDocument:
    """A parsed RFC document."""

    number: str
    title: str
    authors: list[str] = field(default_factory=list)
    date: str = ""
    abstract: str = ""
    sections: list[RfcSection] = field(default_factory=list)
    raw_text: str = ""
    obsoletes: list[str] = field(default_factory=list)
    updated_by: list[str] = field(default_factory=list)


class RfcFetcher:
    """Fetches and parses RFCs from the IETF RFC Editor."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch(self, rfc_number: str) -> RfcDocument | None:
        """Fetch and parse an RFC by number."""
        text = await self._fetch_text(rfc_number)
        if not text:
            return None

        doc = self._parse(rfc_number, text)
        return doc

    async def _fetch_text(self, rfc_number: str) -> str | None:
        """Fetch RFC plain text, using cache."""
        cache_file = self.cache_dir / f"rfc{rfc_number}.txt"

        if cache_file.exists():
            return cache_file.read_text()

        url = RFC_TEXT_URL.format(number=rfc_number)
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text
                cache_file.write_text(text)
                logger.info("Fetched and cached RFC %s", rfc_number)
                return text
            except httpx.HTTPError as e:
                logger.error("Failed to fetch RFC %s: %s", rfc_number, e)
                return None

    def _parse(self, rfc_number: str, text: str) -> RfcDocument:
        """Parse RFC plain text into structured document."""
        doc = RfcDocument(number=rfc_number, raw_text=text, title="")

        # Extract title (usually on early lines, centered)
        lines = text.split("\n")
        for i, line in enumerate(lines[:30]):
            stripped = line.strip()
            # Title lines are usually centered and appear after header metadata
            if stripped and not stripped.startswith("Request for Comments") and not stripped.startswith("RFC"):
                if len(stripped) > 10 and not re.match(r"^(Category|Status|ISSN|Updates|Obsoletes):", stripped):
                    doc.title = stripped
                    break

        # Extract abstract
        abstract_match = re.search(
            r"Abstract\s*\n(.*?)(?=\nTable of Contents|\n\d+\.\s)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if abstract_match:
            doc.abstract = re.sub(r"\s+", " ", abstract_match.group(1)).strip()

        # Parse sections
        section_pattern = re.compile(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", re.MULTILINE)
        matches = list(section_pattern.finditer(text))

        for i, match in enumerate(matches):
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()

            number = match.group(1).rstrip(".")
            depth = number.count(".")

            doc.sections.append(
                RfcSection(
                    number=number,
                    heading=match.group(2).strip(),
                    content=content,
                    depth=depth,
                )
            )

        return doc

    async def fetch_batch(self, rfc_numbers: list[str]) -> list[RfcDocument]:
        """Fetch multiple RFCs."""
        docs = []
        for num in rfc_numbers:
            doc = await self.fetch(num)
            if doc:
                docs.append(doc)
        return docs


def collect_taxonomy_rfcs() -> list[str]:
    """Collect all unique RFC numbers referenced in the taxonomy."""
    from oracle.taxonomy import all_topics

    numbers: set[str] = set()
    for _cat, _sub, topic in all_topics():
        for ref in topic.rfcs:
            match = re.match(r"RFC\s*(\d+)", ref, re.IGNORECASE)
            if match:
                numbers.add(match.group(1))

    return sorted(numbers)
