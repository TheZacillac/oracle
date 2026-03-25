"""ICANN document source fetcher.

Provides access to key ICANN policy documents, agreements, and reference
material for training data generation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# Key ICANN reference documents and their URLs
ICANN_SOURCES = {
    "raa_2013": {
        "name": "2013 Registrar Accreditation Agreement",
        "url": "https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en",
        "category": "registrars",
    },
    "base_ra": {
        "name": "Base Registry Agreement (New gTLDs)",
        "url": "https://www.icann.org/resources/pages/registries/registries-agreements-en",
        "category": "tlds",
    },
    "transfer_policy": {
        "name": "Transfer Policy",
        "url": "https://www.icann.org/resources/pages/transfer-policy-2016-06-01-en",
        "category": "registration",
    },
    "udrp_policy": {
        "name": "Uniform Domain-Name Dispute-Resolution Policy",
        "url": "https://www.icann.org/resources/pages/policy-2012-02-25-en",
        "category": "disputes",
    },
    "udrp_rules": {
        "name": "Rules for UDRP",
        "url": "https://www.icann.org/resources/pages/udrp-rules-2015-03-11-en",
        "category": "disputes",
    },
    "urs_procedure": {
        "name": "Uniform Rapid Suspension Procedure",
        "url": "https://www.icann.org/resources/pages/urs-2014-01-09-en",
        "category": "disputes",
    },
    "epdp_phase1": {
        "name": "EPDP Phase 1 Final Report",
        "url": "https://gnso.icann.org/sites/default/files/file/field-file-attach/epdp-gtld-registration-data-specs-final-20feb19-en.pdf",
        "category": "whois_rdap",
    },
    "tmch_guidelines": {
        "name": "Trademark Clearinghouse Guidelines",
        "url": "https://www.trademark-clearinghouse.com",
        "category": "blocking",
    },
    "applicant_guidebook": {
        "name": "New gTLD Applicant Guidebook",
        "url": "https://newgtlds.icann.org/en/applicants/agb",
        "category": "tlds",
    },
    "wdrp": {
        "name": "WHOIS Data Reminder Policy",
        "url": "https://www.icann.org/resources/pages/wdrp-2013-07-15-en",
        "category": "whois_rdap",
    },
}

# WIPO UDRP reference documents
WIPO_SOURCES = {
    "wipo_overview_3": {
        "name": "WIPO Overview of WIPO Panel Views on Selected UDRP Questions, Third Edition",
        "url": "https://www.wipo.int/amc/en/domains/search/overview3.0/",
        "category": "disputes",
    },
    "wipo_udrp_guide": {
        "name": "WIPO Guide to the UDRP",
        "url": "https://www.wipo.int/amc/en/domains/guide/",
        "category": "disputes",
    },
}


@dataclass
class IcannDocument:
    """A reference to an ICANN or WIPO document."""

    key: str
    name: str
    url: str
    category: str
    content: str = ""
    cached: bool = False


class IcannFetcher:
    """Fetches ICANN and WIPO reference documents.

    Note: Many ICANN documents are HTML pages rather than raw text,
    so this fetcher stores the raw HTML for downstream parsing.
    For PDF documents, only the metadata is stored.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_document(self, key: str) -> IcannDocument | None:
        """Fetch a specific ICANN/WIPO document by key."""
        sources = {**ICANN_SOURCES, **WIPO_SOURCES}
        if key not in sources:
            logger.error("Unknown document key: %s", key)
            return None

        info = sources[key]
        cache_file = self.cache_dir / f"{key}.html"

        doc = IcannDocument(
            key=key,
            name=info["name"],
            url=info["url"],
            category=info["category"],
        )

        if cache_file.exists():
            doc.content = cache_file.read_text()
            doc.cached = True
            return doc

        # Skip PDFs — just record the reference
        if info["url"].endswith(".pdf"):
            logger.info("Skipping PDF download for %s (reference only)", key)
            doc.content = f"[PDF document: {info['name']}]\nURL: {info['url']}"
            cache_file.write_text(doc.content)
            doc.cached = True
            return doc

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(info["url"])
                response.raise_for_status()
                doc.content = response.text
                cache_file.write_text(doc.content)
                doc.cached = True
                logger.info("Fetched and cached %s", key)
            except httpx.HTTPError as e:
                logger.error("Failed to fetch %s: %s", key, e)
                return None

        return doc

    async def fetch_category_documents(self, category: str) -> list[IcannDocument]:
        """Fetch all documents related to a taxonomy category."""
        sources = {**ICANN_SOURCES, **WIPO_SOURCES}
        docs = []

        for key, info in sources.items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)

        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available document sources."""
        sources = {**ICANN_SOURCES, **WIPO_SOURCES}
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in sources.items()
        ]
