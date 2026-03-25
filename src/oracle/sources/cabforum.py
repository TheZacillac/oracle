"""CA/Browser Forum and SSL/TLS source document fetcher.

Provides access to key CA/Browser Forum documents, certificate transparency
resources, root store policies, ACME/Let's Encrypt documentation, and other
PKI-related resources for training data generation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# CA/Browser Forum Documents
# =============================================================================
CABFORUM_SOURCES = {
    # ---- Core Requirements ----
    "baseline_requirements": {
        "name": "CA/Browser Forum Baseline Requirements for TLS Certificates",
        "url": "https://cabforum.org/baseline-requirements-documents/",
        "category": "ssl",
    },
    "ev_guidelines": {
        "name": "CA/Browser Forum EV SSL Certificate Guidelines",
        "url": "https://cabforum.org/extended-validation/",
        "category": "ssl",
    },
    "network_security": {
        "name": "CA/Browser Forum Network and Certificate System Security Requirements",
        "url": "https://cabforum.org/network-security-requirements/",
        "category": "ssl",
    },
    "code_signing_requirements": {
        "name": "CA/Browser Forum Code Signing Baseline Requirements",
        "url": "https://cabforum.org/working-groups/code-signing/requirements/",
        "category": "ssl",
    },
    "smime_requirements": {
        "name": "CA/Browser Forum S/MIME Baseline Requirements",
        "url": "https://cabforum.org/smime-br/",
        "category": "ssl",
    },
    "cabforum_bylaws": {
        "name": "CA/Browser Forum Bylaws",
        "url": "https://cabforum.org/bylaws/",
        "category": "ssl",
    },

    # ---- Certificate Transparency ----
    "ct_policy": {
        "name": "Certificate Transparency Overview",
        "url": "https://certificate.transparency.dev/",
        "category": "ssl",
    },
    "ct_howctworks": {
        "name": "Certificate Transparency: How CT Works",
        "url": "https://certificate.transparency.dev/howctworks/",
        "category": "ssl",
    },
    "ct_google_policy": {
        "name": "Google Chrome Certificate Transparency Policy",
        "url": "https://googlechrome.github.io/CertificateTransparency/ct_policy.html",
        "category": "ssl",
    },
    "ct_logs_list": {
        "name": "Certificate Transparency Known Logs",
        "url": "https://www.gstatic.com/ct/log_list/v3/log_list.json",
        "category": "ssl",
    },

    # ---- Root Store Policies ----
    "mozilla_ca_policy": {
        "name": "Mozilla Root Store Policy",
        "url": "https://wiki.mozilla.org/CA/Included_Certificates",
        "category": "ssl",
    },
    "mozilla_root_store": {
        "name": "Mozilla Root Store — Included CA Certificate Report (CCADB)",
        "url": "https://ccadb.my.salesforce-sites.com/mozilla/IncludedCACertificateReport",
        "category": "ssl",
    },
    "google_root_store": {
        "name": "Google Chrome Root Store Policy",
        "url": "https://www.chromium.org/Home/chromium-security/root-ca-policy/",
        "category": "ssl",
    },
    "apple_root_store": {
        "name": "Apple Root Certificate Program",
        "url": "https://www.apple.com/certificateauthority/ca_program.html",
        "category": "ssl",
    },
    "microsoft_root_store": {
        "name": "Microsoft Trusted Root Certificate Program",
        "url": "https://learn.microsoft.com/en-us/security/trusted-root/program-requirements",
        "category": "ssl",
    },
    "ccadb": {
        "name": "Common CA Database (CCADB)",
        "url": "https://www.ccadb.org/",
        "category": "ssl",
    },

    # ---- ACME & Let's Encrypt ----
    "letsencrypt_docs": {
        "name": "Let's Encrypt Documentation",
        "url": "https://letsencrypt.org/docs/",
        "category": "ssl",
    },
    "letsencrypt_how_it_works": {
        "name": "Let's Encrypt: How It Works",
        "url": "https://letsencrypt.org/how-it-works/",
        "category": "ssl",
    },
    "letsencrypt_rate_limits": {
        "name": "Let's Encrypt Rate Limits",
        "url": "https://letsencrypt.org/docs/rate-limits/",
        "category": "ssl",
    },
    "letsencrypt_challenge_types": {
        "name": "Let's Encrypt Challenge Types",
        "url": "https://letsencrypt.org/docs/challenge-types/",
        "category": "ssl",
    },
    "certbot_docs": {
        "name": "Certbot Documentation (EFF)",
        "url": "https://certbot.eff.org/docs/",
        "category": "ssl",
    },

    # ---- Certificate Monitoring & Tools ----
    "crtsh": {
        "name": "crt.sh — Certificate Transparency Search",
        "url": "https://crt.sh/",
        "category": "ssl",
    },
    "ssllabs": {
        "name": "Qualys SSL Labs — SSL Server Test Documentation",
        "url": "https://www.ssllabs.com/projects/documentation/",
        "category": "ssl",
    },
}


@dataclass
class CaBrowserForumDocument:
    """A reference to a CA/Browser Forum or SSL/TLS document."""

    key: str
    name: str
    url: str
    category: str
    content: str = ""
    cached: bool = False


class CaBrowserForumFetcher:
    """Fetches CA/Browser Forum and SSL/TLS reference documents.

    Note: Most documents are HTML pages; this fetcher stores the raw HTML
    for downstream parsing and extraction.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _all_sources(self) -> dict:
        """Get all sources."""
        return CABFORUM_SOURCES

    async def fetch_document(self, key: str) -> CaBrowserForumDocument | None:
        """Fetch a specific CA/Browser Forum document by key."""
        if key not in self._all_sources():
            logger.error("Unknown document key: %s", key)
            return None

        info = self._all_sources()[key]
        cache_file = self.cache_dir / f"{key}.html"

        doc = CaBrowserForumDocument(
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

    async def fetch_all(self) -> list[CaBrowserForumDocument]:
        """Fetch all CA/Browser Forum documents."""
        docs = []
        for key in self._all_sources():
            doc = await self.fetch_document(key)
            if doc:
                docs.append(doc)
        return docs

    async def fetch_category_documents(self, category: str) -> list[CaBrowserForumDocument]:
        """Fetch all documents related to a taxonomy category."""
        docs = []
        for key, info in self._all_sources().items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)
        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available CA/Browser Forum document sources."""
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in self._all_sources().items()
        ]
