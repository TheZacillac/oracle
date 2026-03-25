"""Internet governance and standards body source fetcher.

Provides access to documents from internet governance forums, standards
organizations, and regional bodies relevant to DNS and domain name policy.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# Standards Organizations
# =============================================================================
IETF_SOURCES = {
    "ietf_overview": {
        "name": "IETF Overview — How the Internet Engineering Task Force Works",
        "url": "https://www.ietf.org/about/introduction/",
        "category": "governance",
    },
    "ietf_rfc_process": {
        "name": "The Internet Standards Process (RFC 2026)",
        "url": "https://www.rfc-editor.org/rfc/rfc2026",
        "category": "governance",
    },
    "ietf_tao": {
        "name": "The Tao of IETF: A Novice's Guide",
        "url": "https://www.ietf.org/about/participate/tao/",
        "category": "governance",
    },
    # DNS-related IETF Working Groups
    "ietf_dnsop": {
        "name": "IETF DNSOP (DNS Operations) Working Group",
        "url": "https://datatracker.ietf.org/wg/dnsop/about/",
        "category": "dns",
    },
    "ietf_dprive": {
        "name": "IETF DPRIVE (DNS PRIVate Exchange) Working Group",
        "url": "https://datatracker.ietf.org/wg/dprive/about/",
        "category": "dns",
    },
    "ietf_dnssd": {
        "name": "IETF DNSSD (Extensions for Scalable DNS Service Discovery) WG",
        "url": "https://datatracker.ietf.org/wg/dnssd/about/",
        "category": "dns",
    },
    "ietf_add": {
        "name": "IETF ADD (Adaptive DNS Discovery) Working Group",
        "url": "https://datatracker.ietf.org/wg/add/about/",
        "category": "dns",
    },
    "ietf_regext": {
        "name": "IETF REGEXT (Registration Protocols Extensions) WG",
        "url": "https://datatracker.ietf.org/wg/regext/about/",
        "category": "registration",
    },
    "ietf_acme_wg": {
        "name": "IETF ACME (Automated Certificate Management Environment) WG",
        "url": "https://datatracker.ietf.org/wg/acme/about/",
        "category": "ssl",
    },
}

# =============================================================================
# Internet Governance Forums
# =============================================================================
GOVERNANCE_FORUM_SOURCES = {
    "igf_overview": {
        "name": "Internet Governance Forum (IGF) Overview",
        "url": "https://www.intgovforum.org/en/about",
        "category": "governance",
    },
    "igf_messages": {
        "name": "IGF Annual Messages and Output Documents",
        "url": "https://www.intgovforum.org/en/content/igf-outputs",
        "category": "governance",
    },
    "igf_bpf_cybersecurity": {
        "name": "IGF Best Practice Forum on Cybersecurity",
        "url": "https://www.intgovforum.org/en/content/bpf-cybersecurity",
        "category": "governance",
    },
    "netmundial": {
        "name": "NETmundial Multistakeholder Statement",
        "url": "https://netmundial.org/",
        "category": "governance",
    },
    "wsis_outcomes": {
        "name": "WSIS Outcome Documents (World Summit on the Information Society)",
        "url": "https://www.itu.int/net/wsis/outcome/booklet.pdf",
        "category": "governance",
    },
    "wsis_forum": {
        "name": "WSIS Forum Annual Resources",
        "url": "https://www.itu.int/net/wsis/",
        "category": "governance",
    },
    "itu_internet_resolutions": {
        "name": "ITU Resolutions on Internet Governance",
        "url": "https://www.itu.int/en/action/internet/Pages/default.aspx",
        "category": "governance",
    },
    "freedom_online": {
        "name": "Freedom Online Coalition — Joint Statements on Internet Freedom",
        "url": "https://freedomonlinecoalition.com/",
        "category": "governance",
    },
}

# =============================================================================
# Regional Internet Registries (RIRs)
# =============================================================================
RIR_SOURCES = {
    "nro_overview": {
        "name": "Number Resource Organization (NRO) — RIR Coordination",
        "url": "https://www.nro.net/about/",
        "category": "governance",
    },
    "arin": {
        "name": "ARIN (American Registry for Internet Numbers)",
        "url": "https://www.arin.net/about/",
        "category": "governance",
    },
    "arin_rdns": {
        "name": "ARIN Reverse DNS Delegation",
        "url": "https://www.arin.net/resources/manage/reverse/",
        "category": "dns",
    },
    "ripe_ncc": {
        "name": "RIPE NCC (Réseaux IP Européens Network Coordination Centre)",
        "url": "https://www.ripe.net/about-us/",
        "category": "governance",
    },
    "ripe_dns": {
        "name": "RIPE NCC DNS Services and Reverse DNS",
        "url": "https://www.ripe.net/manage-ips-and-asns/dns/",
        "category": "dns",
    },
    "apnic": {
        "name": "APNIC (Asia-Pacific Network Information Centre)",
        "url": "https://www.apnic.net/about-apnic/",
        "category": "governance",
    },
    "lacnic": {
        "name": "LACNIC (Latin America and Caribbean Network Information Centre)",
        "url": "https://www.lacnic.net/en/web/lacnic/about-lacnic",
        "category": "governance",
    },
    "afrinic": {
        "name": "AFRINIC (African Network Information Centre)",
        "url": "https://afrinic.net/about",
        "category": "governance",
    },
}

# =============================================================================
# National CERTs & Cybersecurity Agencies (DNS guidance)
# =============================================================================
CYBERSECURITY_AGENCY_SOURCES = {
    "ncsc_dns_guidance": {
        "name": "UK NCSC — DNS Security Guidance",
        "url": "https://www.ncsc.gov.uk/collection/dns",
        "category": "domain_security",
    },
    "ncsc_pdns": {
        "name": "UK NCSC — Protective DNS",
        "url": "https://www.ncsc.gov.uk/information/pdns",
        "category": "protective_dns",
    },
    "cisa_dns": {
        "name": "CISA DNS Infrastructure Guidance",
        "url": "https://www.cisa.gov/dns-infrastructure",
        "category": "domain_security",
    },
    "enisa_dns": {
        "name": "ENISA (EU Agency for Cybersecurity) — DNS Best Practices",
        "url": "https://www.enisa.europa.eu/topics/dns",
        "category": "domain_security",
    },
    "bsi_dns": {
        "name": "BSI (German Federal Cyber Security Authority) — DNS Security",
        "url": "https://www.bsi.bund.de/EN/Topics/IT-Crisis-Management/DNS/dns_node.html",
        "category": "domain_security",
    },
}


def _all_governance_sources() -> dict:
    """Combine all governance source dictionaries."""
    return {
        **IETF_SOURCES,
        **GOVERNANCE_FORUM_SOURCES,
        **RIR_SOURCES,
        **CYBERSECURITY_AGENCY_SOURCES,
    }


@dataclass
class GovernanceDocument:
    """A reference to a governance/standards body document."""

    key: str
    name: str
    url: str
    category: str
    content: str = ""
    cached: bool = False


class GovernanceFetcher:
    """Fetches documents from internet governance and standards bodies.

    Covers IETF working groups, IGF/WSIS/ITU governance forums,
    Regional Internet Registries, and national cybersecurity agencies.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_document(self, key: str) -> GovernanceDocument | None:
        """Fetch a specific governance document by key."""
        sources = _all_governance_sources()
        if key not in sources:
            logger.error("Unknown governance document key: %s", key)
            return None

        info = sources[key]
        cache_file = self.cache_dir / f"governance_{key}.html"

        doc = GovernanceDocument(
            key=key,
            name=info["name"],
            url=info["url"],
            category=info["category"],
        )

        if cache_file.exists():
            doc.content = cache_file.read_text()
            doc.cached = True
            return doc

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
                logger.info("Fetched and cached governance document %s", key)
            except httpx.HTTPError as e:
                logger.error("Failed to fetch governance document %s: %s", key, e)
                return None

        return doc

    async def fetch_category_documents(self, category: str) -> list[GovernanceDocument]:
        """Fetch all governance documents related to a taxonomy category."""
        sources = _all_governance_sources()
        docs = []
        for key, info in sources.items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)
        return docs

    async def fetch_all(self) -> list[GovernanceDocument]:
        """Fetch all governance documents."""
        docs = []
        for key in _all_governance_sources():
            doc = await self.fetch_document(key)
            if doc:
                docs.append(doc)
        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available governance document sources."""
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in _all_governance_sources().items()
        ]
