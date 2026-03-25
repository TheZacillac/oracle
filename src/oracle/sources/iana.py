"""IANA data source fetcher.

Fetches structured data from IANA registries for use in training data generation.
"""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass, field
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Key IANA data sources
IANA_URLS = {
    "tlds": "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
    "root_db": "https://www.iana.org/domains/root/db",
    "dns_parameters": "https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml",
    "rdap_bootstrap": "https://data.iana.org/rdap/dns.json",
    "special_use_domains": "https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml",
    "rr_types_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-4.csv",
    "opcodes_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-5.csv",
    "rcodes_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-6.csv",
}


@dataclass
class DnsRrType:
    """A DNS resource record type from the IANA registry."""

    type_name: str
    value: int
    meaning: str
    reference: str


@dataclass
class IanaData:
    """Collection of fetched IANA data."""

    tld_list: list[str] = field(default_factory=list)
    rr_types: list[DnsRrType] = field(default_factory=list)
    rdap_services: dict = field(default_factory=dict)


class IanaFetcher:
    """Fetches data from IANA registries."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def _fetch_url(self, url: str, cache_name: str) -> str | None:
        """Fetch a URL with caching."""
        cache_file = self.cache_dir / cache_name

        if cache_file.exists():
            return cache_file.read_text()

        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                text = response.text
                cache_file.write_text(text)
                logger.info("Fetched and cached %s", cache_name)
                return text
            except httpx.HTTPError as e:
                logger.error("Failed to fetch %s: %s", url, e)
                return None

    async def fetch_tld_list(self) -> list[str]:
        """Fetch the current list of TLDs from IANA."""
        text = await self._fetch_url(IANA_URLS["tlds"], "tlds-alpha-by-domain.txt")
        if not text:
            return []

        tlds = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                tlds.append(line.lower())

        logger.info("Fetched %d TLDs from IANA", len(tlds))
        return tlds

    async def fetch_rr_types(self) -> list[DnsRrType]:
        """Fetch DNS resource record types from IANA registry."""
        text = await self._fetch_url(IANA_URLS["rr_types_csv"], "dns-rr-types.csv")
        if not text:
            return []

        rr_types = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            try:
                type_name = row.get("TYPE", row.get("Type", "")).strip()
                value_str = row.get("Value", row.get("VALUE", "")).strip()
                meaning = row.get("Meaning", row.get("MEANING", "")).strip()
                reference = row.get("Reference", row.get("REFERENCE", "")).strip()

                if not type_name or not value_str:
                    continue

                # Handle ranges like "128-255"
                if "-" in value_str:
                    continue

                rr_types.append(
                    DnsRrType(
                        type_name=type_name,
                        value=int(value_str),
                        meaning=meaning,
                        reference=reference,
                    )
                )
            except (ValueError, KeyError):
                continue

        logger.info("Fetched %d RR types from IANA", len(rr_types))
        return rr_types

    async def fetch_rdap_bootstrap(self) -> dict:
        """Fetch the RDAP bootstrap data (which RDAP servers serve which TLDs)."""
        import json

        text = await self._fetch_url(IANA_URLS["rdap_bootstrap"], "rdap-dns.json")
        if not text:
            return {}

        try:
            return json.loads(text)
        except Exception as e:
            logger.error("Failed to parse RDAP bootstrap JSON: %s", e)
            return {}

    async def fetch_all(self) -> IanaData:
        """Fetch all IANA data sources."""
        data = IanaData()
        data.tld_list = await self.fetch_tld_list()
        data.rr_types = await self.fetch_rr_types()
        data.rdap_services = await self.fetch_rdap_bootstrap()
        return data
