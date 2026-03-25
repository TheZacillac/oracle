"""Public Suffix List source fetcher and parser.

Fetches and parses the Public Suffix List (PSL) into structured data
for use in training data generation. The PSL is used to determine
effective TLDs — the boundaries at which domain registrations occur.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

PSL_URL = "https://publicsuffix.org/list/public_suffix_list.dat"


@dataclass
class PslData:
    """Parsed Public Suffix List data."""

    icann_domains: list[str] = field(default_factory=list)
    private_domains: list[str] = field(default_factory=list)
    icann_comments: list[str] = field(default_factory=list)
    private_comments: list[str] = field(default_factory=list)
    tld_count: int = 0
    effective_tld_count: int = 0
    private_suffix_count: int = 0


class PslFetcher:
    """Fetches and parses the Public Suffix List.

    The PSL has two main sections:
    - ICANN domains: TLDs and effective TLDs managed under ICANN policies
    - Private domains: Suffixes operated by private organizations (e.g., *.amazonaws.com)

    Comments (lines starting with //) provide context about each section
    and are preserved for training data extraction.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch(self) -> PslData | None:
        """Fetch and parse the Public Suffix List."""
        text = await self._fetch_raw()
        if not text:
            return None

        return self._parse(text)

    async def _fetch_raw(self) -> str | None:
        """Fetch the raw PSL text, using cache."""
        cache_file = self.cache_dir / "public_suffix_list.dat"

        if cache_file.exists():
            return cache_file.read_text()

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(PSL_URL)
                response.raise_for_status()
                text = response.text
                cache_file.write_text(text)
                logger.info("Fetched and cached Public Suffix List")
                return text
            except httpx.HTTPError as e:
                logger.error("Failed to fetch Public Suffix List: %s", e)
                return None

    def _parse(self, text: str) -> PslData:
        """Parse PSL text into structured data.

        The PSL format uses:
        - ``// ===BEGIN ICANN DOMAINS===`` / ``// ===END ICANN DOMAINS===``
        - ``// ===BEGIN PRIVATE DOMAINS===`` / ``// ===END PRIVATE DOMAINS===``
        - Lines starting with ``//`` are comments
        - Blank lines are separators
        - All other lines are suffix entries (optionally with wildcards like ``*.ck``)
        """
        data = PslData()
        section: str | None = None
        tlds: set[str] = set()

        for line in text.split("\n"):
            stripped = line.strip()

            # Detect section boundaries
            if "===BEGIN ICANN DOMAINS===" in stripped:
                section = "icann"
                continue
            elif "===END ICANN DOMAINS===" in stripped:
                section = None
                continue
            elif "===BEGIN PRIVATE DOMAINS===" in stripped:
                section = "private"
                continue
            elif "===END PRIVATE DOMAINS===" in stripped:
                section = None
                continue

            if section is None:
                continue

            # Comments
            if stripped.startswith("//"):
                comment = stripped[2:].strip()
                if comment:
                    if section == "icann":
                        data.icann_comments.append(comment)
                    elif section == "private":
                        data.private_comments.append(comment)
                continue

            # Blank lines
            if not stripped:
                continue

            # Domain entries
            if section == "icann":
                data.icann_domains.append(stripped)
                # Track TLDs (entries without a dot are actual TLDs)
                if "." not in stripped and not stripped.startswith("!") and not stripped.startswith("*"):
                    tlds.add(stripped)
            elif section == "private":
                data.private_domains.append(stripped)

        data.tld_count = len(tlds)
        data.effective_tld_count = len(data.icann_domains)
        data.private_suffix_count = len(data.private_domains)

        logger.info(
            "Parsed PSL: %d TLDs, %d effective TLDs (ICANN), %d private suffixes",
            data.tld_count,
            data.effective_tld_count,
            data.private_suffix_count,
        )
        return data
