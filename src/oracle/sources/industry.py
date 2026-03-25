"""Industry organization source fetcher.

Provides access to key documents from DNS/domain industry organizations
including M3AAWG, APWG, DNS-OARC, FIRST, CENTR, and domain industry
associations. These are critical for DNS abuse, email auth, security,
and operational best practices training data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# Anti-Abuse & Security Organizations
# =============================================================================
M3AAWG_SOURCES = {
    # M3AAWG (Messaging, Malware and Mobile Anti-Abuse Working Group)
    "m3aawg_best_practices": {
        "name": "M3AAWG Best Practices and Resources",
        "url": "https://www.m3aawg.org/published-documents",
        "category": "email",
    },
    "m3aawg_dmarc_training": {
        "name": "M3AAWG DMARC Training",
        "url": "https://www.m3aawg.org/activities/training/dmarc-training-series",
        "category": "email",
    },
    "m3aawg_sending_practices": {
        "name": "M3AAWG Sender Best Practices (Version 3.0)",
        "url": "https://www.m3aawg.org/documents/en/m3aawg-sender-best-common-practices-version-30",
        "category": "email",
    },
    "m3aawg_phishing": {
        "name": "M3AAWG Anti-Phishing and Published Documents",
        "url": "https://www.m3aawg.org/published-documents",
        "category": "dns_abuse",
    },
    "m3aawg_dns_practices": {
        "name": "M3AAWG DNS Abuse Prevention for Registrars and Registries (2024)",
        "url": "https://www.m3aawg.org/DNSAbusePreventionRegReg2024",
        "category": "dns",
    },
}

APWG_SOURCES = {
    # APWG (Anti-Phishing Working Group)
    "apwg_phishing_trends": {
        "name": "APWG Phishing Activity Trends Reports",
        "url": "https://apwg.org/trendsreports/",
        "category": "dns_abuse",
    },
    "apwg_ecrime": {
        "name": "APWG/eCrime Research Papers",
        "url": "https://ecrimeresearch.org/ecrime-research-papers/",
        "category": "dns_abuse",
    },
    "apwg_unifying_framework": {
        "name": "APWG (Anti-Phishing Working Group) Resources",
        "url": "https://apwg.org/",
        "category": "dns_abuse",
    },
}

DNS_OARC_SOURCES = {
    # DNS-OARC (DNS Operations, Analysis, and Research Center)
    "dns_oarc_overview": {
        "name": "DNS-OARC Overview and Resources",
        "url": "https://www.dns-oarc.net/",
        "category": "dns",
    },
    "dns_oarc_tools": {
        "name": "DNS-OARC Tools and Data",
        "url": "https://www.dns-oarc.net/oarc/tools",
        "category": "dns_tools",
    },
    "dns_flag_day": {
        "name": "DNS Flag Day Events and Requirements (GitHub Mirror)",
        "url": "https://dns-violations.github.io/dnsflagday/",
        "category": "dns",
    },
    "ditl_data": {
        "name": "DNS-OARC Day in the Life of the Internet (DITL) Data Collections",
        "url": "https://www.dns-oarc.net/oarc/data/ditl",
        "category": "monitoring",
    },
}

FIRST_SOURCES = {
    # FIRST (Forum of Incident Response and Security Teams)
    "first_dns_abuse": {
        "name": "FIRST DNS Abuse Special Interest Group",
        "url": "https://www.first.org/global/sigs/dns/",
        "category": "domain_security",
    },
    "first_incident_response": {
        "name": "FIRST Incident Response Resources",
        "url": "https://www.first.org/resources/guides/",
        "category": "domain_security",
    },
}

# =============================================================================
# Regional & Industry Associations
# =============================================================================
REGISTRY_REGISTRAR_ORGS = {
    # CENTR (Council of European National TLD Registries)
    "centr_overview": {
        "name": "CENTR Library and Publications",
        "url": "https://centr.org/library/library.html",
        "category": "tlds",
    },
    "centr_stats": {
        "name": "CENTRstats — Domain Statistics Analytics",
        "url": "https://stats.centr.org/",
        "category": "tlds",
    },
    # LACTLD (Latin American and Caribbean TLD Association)
    "lactld_overview": {
        "name": "LACTLD Resources",
        "url": "https://lactld.org/en/",
        "category": "tlds",
    },
    # AFTLD (African TLD Organization)
    "aftld_overview": {
        "name": "AFTLD Resources",
        "url": "https://aftld.org/",
        "category": "tlds",
    },
}

# =============================================================================
# Email Provider Guidelines
# =============================================================================
EMAIL_PROVIDER_SOURCES = {
    "google_postmaster": {
        "name": "Google Postmaster Tools & Email Sender Guidelines",
        "url": "https://support.google.com/a/answer/81126",
        "category": "email",
    },
    "google_bulk_sender": {
        "name": "Google & Yahoo Bulk Sender Requirements (2024+)",
        "url": "https://blog.google/products/gmail/gmail-security-authentication-spam-protection/",
        "category": "email",
    },
    "microsoft_sender": {
        "name": "Microsoft Outlook.com Sender Requirements",
        "url": "https://sendersupport.olc.protection.outlook.com/",
        "category": "email",
    },
    "dmarc_org": {
        "name": "DMARC.org Resources and Deployment Guides",
        "url": "https://dmarc.org/resources/",
        "category": "email",
    },
    "bimi_group": {
        "name": "BIMI Group — Brand Indicators for Message Identification",
        "url": "https://bimigroup.org/",
        "category": "email",
    },
}

# =============================================================================
# DNS Abuse & Protective DNS
# =============================================================================
PROTECTIVE_DNS_SOURCES = {
    "quad9": {
        "name": "Quad9 — Protective DNS Documentation",
        "url": "https://www.quad9.net/about/",
        "category": "protective_dns",
    },
    "quad9_threat_blocking": {
        "name": "Quad9 Threat Blocking Methodology",
        "url": "https://www.quad9.net/service/threat-blocking/",
        "category": "protective_dns",
    },
    "cloudflare_1111": {
        "name": "Cloudflare 1.1.1.1 DNS Resolver Documentation",
        "url": "https://developers.cloudflare.com/1.1.1.1/",
        "category": "protective_dns",
    },
    "cloudflare_families": {
        "name": "Cloudflare 1.1.1.1 for Families (Malware/Adult Content Filtering)",
        "url": "https://developers.cloudflare.com/1.1.1.1/setup/#1111-for-families",
        "category": "protective_dns",
    },
    "cisa_protective_dns": {
        "name": "CISA Protective DNS Resolver Service",
        "url": "https://www.cisa.gov/resources-tools/services/protective-domain-name-system-dns-resolver",
        "category": "protective_dns",
    },
    "opendns": {
        "name": "OpenDNS (Cisco Umbrella) Documentation",
        "url": "https://docs.umbrella.com/",
        "category": "protective_dns",
    },
    "cleanbrowsing": {
        "name": "CleanBrowsing DNS Filtering",
        "url": "https://cleanbrowsing.org/guides/",
        "category": "protective_dns",
    },
    "pihole": {
        "name": "Pi-hole DNS Sinkhole Documentation",
        "url": "https://docs.pi-hole.net/",
        "category": "protective_dns",
    },
    "nextdns": {
        "name": "NextDNS Documentation",
        "url": "https://nextdns.io/",
        "category": "protective_dns",
    },
}

# =============================================================================
# Threat Intelligence
# =============================================================================
THREAT_INTEL_SOURCES = {
    "spamhaus": {
        "name": "Spamhaus Resource Hub — DNS Blocklists and Reputation Data",
        "url": "https://www.spamhaus.org/resource-hub/",
        "category": "dns_abuse",
    },
    "spamhaus_dbl": {
        "name": "Spamhaus Domain Block List (DBL)",
        "url": "https://www.spamhaus.org/dbl/",
        "category": "dns_abuse",
    },
    "surbl": {
        "name": "SURBL — URI Reputation Data",
        "url": "https://surbl.org/",
        "category": "dns_abuse",
    },
    "farsight_dnsdb": {
        "name": "Farsight DNSDB — Passive DNS Database",
        "url": "https://www.farsightsecurity.com/solutions/dnsdb/",
        "category": "monitoring",
    },
    "passive_dns_info": {
        "name": "ENISA — Security and Privacy for Public DNS Resolvers",
        "url": "https://www.enisa.europa.eu/publications/security-and-privacy-for-public-dns-resolvers",
        "category": "monitoring",
    },
    "phishtank": {
        "name": "PhishTank — Community Phishing Verification",
        "url": "https://phishtank.org/",
        "category": "dns_abuse",
    },
    "urlhaus": {
        "name": "URLhaus — Malware URL Exchange (abuse.ch)",
        "url": "https://urlhaus.abuse.ch/",
        "category": "dns_abuse",
    },
}

# =============================================================================
# Domain Industry & Business
# =============================================================================
INDUSTRY_BUSINESS_SOURCES = {
    "domaintools_research": {
        "name": "DomainTools Investigations — Threat Intelligence Research",
        "url": "https://dti.domaintools.com/",
        "category": "industry",
    },
    "verisign_domain_brief": {
        "name": "Verisign Domain Name Industry Brief",
        "url": "https://www.verisign.com/en_US/domain-names/dnib/index.xhtml",
        "category": "industry",
    },
    "icann_registrar_list": {
        "name": "ICANN Accredited Registrar List",
        "url": "https://www.icann.org/en/accredited-registrars",
        "category": "registrars",
    },
    "namescon": {
        "name": "NamesCon — Domain Name Industry Conference",
        "url": "https://namescon.com/",
        "category": "industry",
    },
}

# =============================================================================
# Registrar Sources (Retail & Corporate)
# =============================================================================
RETAIL_REGISTRAR_SOURCES = {
    "godaddy_about": {
        "name": "GoDaddy — About and Investor Relations",
        "url": "https://aboutus.godaddy.net/",
        "category": "registrars",
    },
    "godaddy_api": {
        "name": "GoDaddy Developer API Documentation",
        "url": "https://developer.godaddy.com/",
        "category": "registrars",
    },
    "namecheap_kb": {
        "name": "Namecheap Knowledge Base",
        "url": "https://www.namecheap.com/support/knowledgebase/",
        "category": "registrars",
    },
    "namecheap_api": {
        "name": "Namecheap API Documentation",
        "url": "https://www.namecheap.com/support/api/intro/",
        "category": "registrars",
    },
    "porkbun_about": {
        "name": "Porkbun — About and Features",
        "url": "https://porkbun.com/about",
        "category": "registrars",
    },
    "tucows_opensrs": {
        "name": "OpenSRS (Tucows) — Reseller Platform Documentation",
        "url": "https://opensrs.com/resources/documentation/",
        "category": "registrars",
    },
    "gandi_docs": {
        "name": "Gandi Documentation",
        "url": "https://docs.gandi.net/en/",
        "category": "registrars",
    },
    "squarespace_domains": {
        "name": "Squarespace Domains Help (formerly Google Domains)",
        "url": "https://support.squarespace.com/hc/en-us/categories/205815928-Domains",
        "category": "registrars",
    },
    "dynadot_api": {
        "name": "Dynadot API Documentation",
        "url": "https://www.dynadot.com/domain/api3.html",
        "category": "registrars",
    },
    "ionos_domains": {
        "name": "IONOS Domain Management Help",
        "url": "https://www.ionos.com/help/domains/",
        "category": "registrars",
    },
}

CORPORATE_REGISTRAR_SOURCES = {
    "markmonitor": {
        "name": "MarkMonitor (Clarivate) — Domain Management Solutions",
        "url": "https://clarivate.com/products/ip-intelligence/trademark-research-and-protection/markmonitor-domain-management/",
        "category": "registrars",
    },
    "csc_dbs": {
        "name": "CSC Digital Brand Services — Domain Security",
        "url": "https://www.cscdbs.com/",
        "category": "registrars",
    },
    "csc_domain_security": {
        "name": "CSC Domain Security Intelligence",
        "url": "https://www.cscdbs.com/domain-security/",
        "category": "registrars",
    },
    "comlaude": {
        "name": "Com Laude — Corporate Domain Management",
        "url": "https://comlaude.com/",
        "category": "registrars",
    },
    "safenames": {
        "name": "Safenames — Domain and Brand Protection Services",
        "url": "https://www.safenames.net/",
        "category": "registrars",
    },
    "brandit": {
        "name": "BRANDIT — Domain and Brand Management",
        "url": "https://www.brandit.com/",
        "category": "registrars",
    },
    "brandshelter": {
        "name": "BrandShelter — Corporate Domain Protection",
        "url": "https://www.brandshelter.com/",
        "category": "registrars",
    },
    "centralnic_registrar": {
        "name": "CentralNic — Registry and Registrar Platform",
        "url": "https://www.centralnic.com/",
        "category": "registrars",
    },
    "identity_digital": {
        "name": "Identity Digital (formerly Donuts/Afilias) — Registry and Registrar Services",
        "url": "https://www.identity.digital/",
        "category": "registrars",
    },
    "realtime_register": {
        "name": "RealTime Register — Wholesale Domain Platform",
        "url": "https://www.realtimeregister.com/en",
        "category": "registrars",
    },
}


def _all_industry_sources() -> dict:
    """Combine all industry source dictionaries."""
    return {
        **M3AAWG_SOURCES,
        **APWG_SOURCES,
        **DNS_OARC_SOURCES,
        **FIRST_SOURCES,
        **REGISTRY_REGISTRAR_ORGS,
        **EMAIL_PROVIDER_SOURCES,
        **PROTECTIVE_DNS_SOURCES,
        **THREAT_INTEL_SOURCES,
        **INDUSTRY_BUSINESS_SOURCES,
        **RETAIL_REGISTRAR_SOURCES,
        **CORPORATE_REGISTRAR_SOURCES,
    }


@dataclass
class IndustryDocument:
    """A reference to an industry organization document."""

    key: str
    name: str
    url: str
    category: str
    content: str = ""
    cached: bool = False


class IndustryFetcher:
    """Fetches documents from DNS/domain industry organizations.

    Covers anti-abuse organizations, regional TLD associations,
    email provider guidelines, protective DNS services, threat
    intelligence sources, and industry business resources.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_document(self, key: str) -> IndustryDocument | None:
        """Fetch a specific industry document by key."""
        sources = _all_industry_sources()
        if key not in sources:
            logger.error("Unknown industry document key: %s", key)
            return None

        info = sources[key]
        cache_file = self.cache_dir / f"industry_{key}.html"

        doc = IndustryDocument(
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
                logger.info("Fetched and cached industry document %s", key)
            except httpx.HTTPError as e:
                logger.error("Failed to fetch industry document %s: %s", key, e)
                return None

        return doc

    async def fetch_category_documents(self, category: str) -> list[IndustryDocument]:
        """Fetch all industry documents related to a taxonomy category."""
        sources = _all_industry_sources()
        docs = []

        for key, info in sources.items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)

        return docs

    async def fetch_all(self) -> list[IndustryDocument]:
        """Fetch all industry documents."""
        docs = []
        for key in _all_industry_sources():
            doc = await self.fetch_document(key)
            if doc:
                docs.append(doc)
        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available industry document sources."""
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in _all_industry_sources().items()
        ]

    def list_sources_by_org(self) -> dict[str, list[dict[str, str]]]:
        """List sources grouped by organization."""
        return {
            "M3AAWG": [
                {"key": k, **v} for k, v in M3AAWG_SOURCES.items()
            ],
            "APWG": [
                {"key": k, **v} for k, v in APWG_SOURCES.items()
            ],
            "DNS-OARC": [
                {"key": k, **v} for k, v in DNS_OARC_SOURCES.items()
            ],
            "FIRST": [
                {"key": k, **v} for k, v in FIRST_SOURCES.items()
            ],
            "Registry/Registrar Orgs": [
                {"key": k, **v} for k, v in REGISTRY_REGISTRAR_ORGS.items()
            ],
            "Email Providers": [
                {"key": k, **v} for k, v in EMAIL_PROVIDER_SOURCES.items()
            ],
            "Protective DNS": [
                {"key": k, **v} for k, v in PROTECTIVE_DNS_SOURCES.items()
            ],
            "Threat Intelligence": [
                {"key": k, **v} for k, v in THREAT_INTEL_SOURCES.items()
            ],
            "Industry Business": [
                {"key": k, **v} for k, v in INDUSTRY_BUSINESS_SOURCES.items()
            ],
        }
