"""ICANN document source fetcher.

Provides access to key ICANN policy documents, agreements, and reference
material for training data generation. This is the most comprehensive source
collection in Oracle, covering ICANN policies, GNSO/ccNSO outputs, registrar
and registry agreements, dispute resolution, and governance documents.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# ICANN Policy & Agreement Documents
# =============================================================================
ICANN_SOURCES = {
    # ---- Registrar Agreements & Policies ----
    "raa_2013": {
        "name": "2013 Registrar Accreditation Agreement",
        "url": "https://www.icann.org/resources/pages/approved-with-specs-2013-09-17-en",
        "category": "registrars",
    },
    "registrar_best_practices": {
        "name": "Registrar Best Practices",
        "url": "https://www.icann.org/resources/pages/registrars-0d-2012-02-25-en",
        "category": "registrars",
    },
    "registrar_data_escrow": {
        "name": "Registrar Data Escrow Requirements",
        "url": "https://www.icann.org/resources/pages/registrar-data-escrow-2015-12-01-en",
        "category": "registrars",
    },

    # ---- Registry Agreements & Operations ----
    "base_ra": {
        "name": "Base Registry Agreement (New gTLDs)",
        "url": "https://www.icann.org/resources/pages/registries/registries-agreements-en",
        "category": "tlds",
    },
    "registry_ebero": {
        "name": "Emergency Back-End Registry Operator (EBERO) Requirements",
        "url": "https://www.icann.org/resources/pages/ebero-2013-04-02-en",
        "category": "tlds",
    },
    "registry_data_escrow": {
        "name": "Registry Data Escrow Requirements",
        "url": "https://www.icann.org/en/contracted-parties/registry-operators/services/data-escrow",
        "category": "tlds",
    },
    "rsep": {
        "name": "Registry Services Evaluation Policy (RSEP)",
        "url": "https://www.icann.org/resources/pages/rsep-2014-02-19-en",
        "category": "tlds",
    },

    # ---- Transfer & Registration Policy ----
    "transfer_policy": {
        "name": "Transfer Policy",
        "url": "https://www.icann.org/resources/pages/transfer-policy-2016-06-01-en",
        "category": "registration",
    },
    "agp_limits": {
        "name": "Add Grace Period (AGP) Limits Policy",
        "url": "https://www.icann.org/en/contracted-parties/consensus-policies/add-grace-period-limits-policy/agp-add-grace-period-limits-policy-17-12-2008-en",
        "category": "registration",
    },
    "errp": {
        "name": "Expired Registration Recovery Policy (ERRP)",
        "url": "https://www.icann.org/resources/pages/errp-2013-02-28-en",
        "category": "registration",
    },
    "thick_whois_policy": {
        "name": "Thick WHOIS Transition Policy for .COM, .NET, .JOBS",
        "url": "https://www.icann.org/en/contracted-parties/consensus-policies/thick-registry-registration-data-directory-services-transition-policy/thick-whois-transition-policy-for-com-net-and-jobs-01-02-2017-en",
        "category": "registration",
    },

    # ---- New gTLD Program ----
    "applicant_guidebook": {
        "name": "New gTLD Applicant Guidebook",
        "url": "https://newgtlds.icann.org/en/applicants/agb",
        "category": "tlds",
    },
    "subpro_final": {
        "name": "SubPro Final Report (Subsequent Procedures for New gTLDs)",
        "url": "https://gnso.icann.org/sites/default/files/file/field-file-attach/subsequent-procedures-new-gtlds-final-report-19jan21-en.pdf",
        "category": "tlds",
    },
    "new_gtld_stats": {
        "name": "New gTLD Program Statistics",
        "url": "https://newgtlds.icann.org/en/program-status/statistics",
        "category": "tlds",
    },

    # ---- Dispute Resolution ----
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
    "urs_rules": {
        "name": "URS Rules and Procedures",
        "url": "https://newgtlds.icann.org/en/applicants/urs",
        "category": "disputes",
    },
    "pddrp": {
        "name": "Post-Delegation Dispute Resolution Procedure (PDDRP)",
        "url": "https://www.icann.org/en/contracted-parties/registry-operators/services/rights-protection-mechanisms-and-dispute-resolution-procedures/pddrp",
        "category": "disputes",
    },

    # ---- WHOIS / RDAP / Registration Data ----
    "epdp_phase1": {
        "name": "EPDP Phase 1 Final Report",
        "url": "https://gnso.icann.org/sites/default/files/file/field-file-attach/epdp-gtld-registration-data-specs-final-20feb19-en.pdf",
        "category": "whois_rdap",
    },
    "epdp_phase2": {
        "name": "EPDP Phase 2 Final Report (SSAD)",
        "url": "https://gnso.icann.org/en/group-activities/active/gtld-registration-data-epdp-phase-2",
        "category": "whois_rdap",
    },
    "epdp_phase2a": {
        "name": "EPDP Phase 2A Final Report (Legal vs Natural Persons)",
        "url": "https://gnso.icann.org/en/group-activities/active/gtld-registration-data-epdp-phase-2a",
        "category": "whois_rdap",
    },
    "wdrp": {
        "name": "Registration Data Reminder Policy",
        "url": "https://www.icann.org/en/contracted-parties/consensus-policies/registration-data-reminder-policy/registration-data-reminder-policy-21-02-2024-en",
        "category": "whois_rdap",
    },
    "registration_data_request_service": {
        "name": "Registration Data Request Service (RDRS)",
        "url": "https://www.icann.org/rdrs-en",
        "category": "whois_rdap",
    },
    "rdap_profile": {
        "name": "RDAP Technical Implementation Guide (gTLD RDAP Profile)",
        "url": "https://www.icann.org/rdap",
        "category": "whois_rdap",
    },

    # ---- Blocking & Brand Protection ----
    "tmch_guidelines": {
        "name": "Trademark Clearinghouse Guidelines",
        "url": "https://www.trademark-clearinghouse.com",
        "category": "blocking",
    },
    "tmch_requirements": {
        "name": "Trademark Clearinghouse Requirements",
        "url": "https://newgtlds.icann.org/en/about/trademark-clearinghouse",
        "category": "blocking",
    },
    "dpml_donuts": {
        "name": "Domains Protected Marks List (DPML) by Identity Digital",
        "url": "https://www.identitydigital.com/services/dpml",
        "category": "blocking",
    },

    # ---- ICANN Governance & Structure ----
    "icann_bylaws": {
        "name": "ICANN Bylaws",
        "url": "https://www.icann.org/resources/pages/governance/bylaws-en",
        "category": "icann",
    },
    "icann_strategic_plan": {
        "name": "ICANN Strategic Plan",
        "url": "https://www.icann.org/strategic-plan-en",
        "category": "icann",
    },
    "irp_procedures": {
        "name": "Independent Review Process (IRP) Procedures",
        "url": "https://www.icann.org/resources/pages/accountability/irp-en",
        "category": "icann",
    },
    "icann_reconsideration": {
        "name": "Reconsideration Request Process",
        "url": "https://www.icann.org/resources/pages/accountability/reconsideration-en",
        "category": "icann",
    },
    "icann_ombudsman": {
        "name": "ICANN Ombudsman",
        "url": "https://www.icann.org/ombudsman",
        "category": "icann",
    },
    "gnso_operating_procedures": {
        "name": "GNSO Operating Procedures",
        "url": "https://gnso.icann.org/en/council/procedures",
        "category": "icann",
    },
    "ccnso_framework": {
        "name": "ccNSO Framework of Interpretation",
        "url": "https://www.icann.org/en/ccnso/committees-and-working-groups/documents/framework-of-interpretation-working-group-13-06-2011-en",
        "category": "icann",
    },
    "pti_iana_functions": {
        "name": "PTI (Public Technical Identifiers) — IANA Functions Operator",
        "url": "https://pti.icann.org/",
        "category": "iana",
    },
    "iana_about": {
        "name": "IANA — About the Internet Assigned Numbers Authority",
        "url": "https://www.iana.org/about",
        "category": "iana",
    },
    "iana_ksk_ceremonies": {
        "name": "IANA Root Zone KSK Ceremonies",
        "url": "https://www.iana.org/dnssec/ceremonies",
        "category": "iana",
    },
    "iana_numbering_resources": {
        "name": "IANA — Number Resources (IP Addresses, ASNs)",
        "url": "https://www.iana.org/numbers",
        "category": "iana",
    },
    "iana_root_dnssec": {
        "name": "IANA Root Zone DNSSEC Documentation",
        "url": "https://www.iana.org/dnssec",
        "category": "iana",
    },
    "iana_time_zones": {
        "name": "IANA Time Zone Database",
        "url": "https://www.iana.org/time-zones",
        "category": "iana",
    },
    "icann_budget_ops": {
        "name": "ICANN Budget and Operations Plan",
        "url": "https://www.icann.org/resources/pages/governance/current-en",
        "category": "icann",
    },
    "icann_annual_report": {
        "name": "ICANN Annual Report",
        "url": "https://www.icann.org/resources/pages/governance/annual-report-en",
        "category": "icann",
    },
    "icann_fellowship": {
        "name": "ICANN Fellowship Program",
        "url": "https://www.icann.org/fellowshipprogram",
        "category": "icann",
    },

    # ---- SSAC & RSSAC Advisories ----
    "ssac_advisories": {
        "name": "SSAC Advisories and Publications",
        "url": "https://www.icann.org/groups/ssac/documents",
        "category": "icann",
    },
    "rssac_advisories": {
        "name": "RSSAC Advisories and Publications",
        "url": "https://www.icann.org/groups/rssac/documents",
        "category": "icann",
    },
    "ssac_dns_abuse": {
        "name": "SAC 115: SSAC Report on an Interoperable Approach to DNS Abuse",
        "url": "https://www.icann.org/en/system/files/files/sac-115-en.pdf",
        "category": "dns_abuse",
    },

    # ---- DNS Abuse ----
    "daar_report": {
        "name": "Domain Abuse Activity Reporting (DAAR)",
        "url": "https://www.icann.org/octo-ssr/daar",
        "category": "dns_abuse",
    },
    "dns_abuse_framework": {
        "name": "DNS Abuse Framework (Contracted Parties)",
        "url": "https://dnsabuseframework.org/",
        "category": "dns_abuse",
    },
    "icann_abuse_complaints": {
        "name": "ICANN Contractual Compliance: DNS Abuse Complaints",
        "url": "https://www.icann.org/compliance/complaint",
        "category": "dns_abuse",
    },

    # ---- Compliance & Regulatory ----
    "nis2_directive": {
        "name": "NIS2 Directive (EU 2022/2555)",
        "url": "https://eur-lex.europa.eu/eli/dir/2022/2555",
        "category": "compliance",
    },
    "dns4eu": {
        "name": "DNS4EU Initiative (JoinDNS4EU)",
        "url": "https://joindns4.eu/",
        "category": "compliance",
    },
    "gdpr_full_text": {
        "name": "GDPR Full Text (EU 2016/679)",
        "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        "category": "compliance",
    },
    "dora_regulation": {
        "name": "DORA — Digital Operational Resilience Act (EU 2022/2554)",
        "url": "https://eur-lex.europa.eu/eli/reg/2022/2554",
        "category": "compliance",
    },

    # ---- Domain Security ----
    "icann_domain_abuse_guide": {
        "name": "ICANN DNS Abuse Mitigation Program",
        "url": "https://www.icann.org/dnsabuse",
        "category": "domain_security",
    },
    "registrar_security_best_practices": {
        "name": "ICANN Registrar Security Best Practices",
        "url": "https://www.icann.org/resources/pages/security-2012-02-25-en",
        "category": "domain_security",
    },

    # ---- Universal Acceptance & Internationalization ----
    "ua_roadmap": {
        "name": "Universal Acceptance Steering Group Roadmap",
        "url": "https://uasg.tech/",
        "category": "internationalization",
    },
    "ua_technical_usage": {
        "name": "UASG Document Hub (Archived)",
        "url": "https://uasg.tech/document-hub/",
        "category": "internationalization",
    },
    "ua_eai_overview": {
        "name": "UASG: Email Address Internationalization Overview",
        "url": "https://uasg.tech/eai/",
        "category": "internationalization",
    },
    "ua_doc_series": {
        "name": "UASG Document Series",
        "url": "https://uasg.tech/documents/",
        "category": "internationalization",
    },
    "icann_idn_guidelines": {
        "name": "ICANN Guidelines for IDN Implementation",
        "url": "https://www.icann.org/resources/pages/implementation-guidelines-2012-02-25-en",
        "category": "internationalization",
    },
    "icann_idn_tables": {
        "name": "ICANN IDN Table Repository (Reference LGR)",
        "url": "https://www.icann.org/resources/pages/second-level-lgr-2015-06-21-en",
        "category": "internationalization",
    },
    "root_zone_lgr": {
        "name": "Root Zone Label Generation Rules (LGR)",
        "url": "https://www.icann.org/resources/pages/lgr-toolset-2015-06-21-en",
        "category": "internationalization",
    },

    # ---- Contractual Compliance ----
    "icann_compliance_overview": {
        "name": "ICANN Contractual Compliance Overview",
        "url": "https://www.icann.org/resources/pages/compliance-2012-02-25-en",
        "category": "registrars",
    },
    "consensus_policies": {
        "name": "ICANN Consensus Policies",
        "url": "https://www.icann.org/resources/pages/registrars/consensus-policies-en",
        "category": "icann",
    },
}

# =============================================================================
# WIPO UDRP & Dispute Resolution Documents
# =============================================================================
WIPO_SOURCES = {
    # ---- Core WIPO Resources ----
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
    "wipo_case_search": {
        "name": "WIPO Domain Name Case Search",
        "url": "https://www.wipo.int/amc/en/domains/search/",
        "category": "disputes",
    },
    "wipo_statistics": {
        "name": "WIPO Domain Name Dispute Statistics",
        "url": "https://www.wipo.int/amc/en/domains/statistics/",
        "category": "disputes",
    },
    # ---- WIPO Supplemental Rules ----
    "wipo_supplemental_rules": {
        "name": "WIPO Supplemental Rules for UDRP",
        "url": "https://www.wipo.int/amc/en/domains/rules/supplemental/",
        "category": "disputes",
    },
    "wipo_urs_rules": {
        "name": "WIPO Rights Protection Mechanisms for New TLDs",
        "url": "https://www.wipo.int/amc/en/domains/rpm/",
        "category": "disputes",
    },
    # ---- WIPO Legal Resources ----
    "wipo_legal_index": {
        "name": "WIPO UDRP Legal Index",
        "url": "https://www.wipo.int/amc/en/domains/search/legalindex/",
        "category": "disputes",
    },
    "wipo_cctld_policies": {
        "name": "WIPO ccTLD Dispute Resolution Policies Database",
        "url": "https://www.wipo.int/amc/en/domains/cctld/",
        "category": "disputes",
    },
}

# =============================================================================
# Other Dispute Resolution Providers
# =============================================================================
OTHER_DISPUTE_SOURCES = {
    "forum_nat_arb": {
        "name": "Forum (National Arbitration Forum) UDRP Decisions",
        "url": "https://www.adrforum.com/domain-law/udrp-decisions",
        "category": "disputes",
    },
    "adndrc": {
        "name": "Asian Domain Name Dispute Resolution Centre (ADNDRC)",
        "url": "https://www.adndrc.org/",
        "category": "disputes",
    },
    "cac_czech": {
        "name": "Czech Arbitration Court — UDRP Provider",
        "url": "https://udrp.adr.eu/",
        "category": "disputes",
    },
    "ciidrc": {
        "name": "Canadian International Internet Dispute Resolution Centre (CIIDRC)",
        "url": "https://ciidrc.com/",
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
        """Fetch a specific ICANN/WIPO/dispute provider document by key."""
        sources = {**ICANN_SOURCES, **WIPO_SOURCES, **OTHER_DISPUTE_SOURCES}
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
        sources = {**ICANN_SOURCES, **WIPO_SOURCES, **OTHER_DISPUTE_SOURCES}
        docs = []

        for key, info in sources.items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)

        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available document sources."""
        sources = {**ICANN_SOURCES, **WIPO_SOURCES, **OTHER_DISPUTE_SOURCES}
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in sources.items()
        ]
