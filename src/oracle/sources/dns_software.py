"""DNS software and implementation documentation source fetcher.

Provides access to documentation for major DNS server implementations,
DNS management tools, and DNS automation frameworks. A domain expert
needs to understand the operational tools used to run DNS infrastructure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

# =============================================================================
# Authoritative DNS Servers
# =============================================================================
AUTHORITATIVE_DNS_SOURCES = {
    # BIND (ISC)
    "bind_arm": {
        "name": "BIND 9 Administrator Reference Manual (ARM)",
        "url": "https://bind9.readthedocs.io/en/latest/",
        "category": "dns_software",
    },
    "bind_security": {
        "name": "ISC BIND Security Advisories",
        "url": "https://www.isc.org/bind/",
        "category": "dns_software",
    },
    "bind_dnssec_guide": {
        "name": "ISC BIND DNSSEC Guide",
        "url": "https://bind9.readthedocs.io/en/latest/dnssec-guide.html",
        "category": "dns_software",
    },
    # Knot DNS (CZ.NIC)
    "knot_dns": {
        "name": "Knot DNS Documentation",
        "url": "https://www.knot-dns.cz/docs/latest/html/",
        "category": "dns_software",
    },
    "knot_resolver": {
        "name": "Knot Resolver Documentation",
        "url": "https://knot-resolver.readthedocs.io/en/latest/",
        "category": "dns_software",
    },
    # NSD (NLnet Labs)
    "nsd": {
        "name": "NSD (Name Server Daemon) Documentation",
        "url": "https://nsd.docs.nlnetlabs.nl/en/latest/",
        "category": "dns_software",
    },
    # PowerDNS
    "powerdns_auth": {
        "name": "PowerDNS Authoritative Server Documentation",
        "url": "https://doc.powerdns.com/authoritative/",
        "category": "dns_software",
    },
    "powerdns_recursor": {
        "name": "PowerDNS Recursor Documentation",
        "url": "https://doc.powerdns.com/recursor/",
        "category": "dns_software",
    },
    "powerdns_dnsdist": {
        "name": "dnsdist (PowerDNS) DNS Load Balancer Documentation",
        "url": "https://dnsdist.org/",
        "category": "dns_software",
    },
}

# =============================================================================
# Recursive / Resolver DNS Software
# =============================================================================
RESOLVER_DNS_SOURCES = {
    # Unbound (NLnet Labs)
    "unbound": {
        "name": "Unbound DNS Resolver Documentation",
        "url": "https://unbound.docs.nlnetlabs.nl/en/latest/",
        "category": "dns_software",
    },
    "unbound_dnssec": {
        "name": "Unbound Configuration and DNSSEC Setup Guide",
        "url": "https://unbound.docs.nlnetlabs.nl/en/latest/getting-started/configuration.html",
        "category": "dns_software",
    },
    # CoreDNS
    "coredns": {
        "name": "CoreDNS Documentation",
        "url": "https://coredns.io/manual/toc/",
        "category": "dns_software",
    },
    "coredns_plugins": {
        "name": "CoreDNS Plugin Documentation",
        "url": "https://coredns.io/plugins/",
        "category": "dns_software",
    },
    "coredns_k8s": {
        "name": "CoreDNS in Kubernetes",
        "url": "https://kubernetes.io/docs/tasks/administer-cluster/coredns/",
        "category": "dns_software",
    },
    # systemd-resolved
    "systemd_resolved": {
        "name": "systemd-resolved Documentation",
        "url": "https://www.freedesktop.org/software/systemd/man/systemd-resolved.service.html",
        "category": "dns_software",
    },
    # Windows DNS
    "windows_dns": {
        "name": "Microsoft Windows DNS Server Documentation",
        "url": "https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-top",
        "category": "dns_software",
    },
}

# =============================================================================
# DNSSEC Tools
# =============================================================================
DNSSEC_TOOL_SOURCES = {
    "ldns": {
        "name": "ldns — DNS Library and Tools (NLnet Labs)",
        "url": "https://www.nlnetlabs.nl/projects/ldns/about/",
        "category": "dns_software",
    },
    "dnsviz": {
        "name": "DNSViz — DNSSEC Visualization and Analysis",
        "url": "https://dnsviz.net/",
        "category": "dns_tools",
    },
    "opendnssec": {
        "name": "OpenDNSSEC — Automated DNSSEC Signing",
        "url": "https://www.opendnssec.org/",
        "category": "dns_software",
    },
    "dnssec_tools_nist": {
        "name": "DNSSEC Tools (NIST/Parsons)",
        "url": "https://www.dnssec-tools.org/",
        "category": "dns_software",
    },
}

# =============================================================================
# DNS Management & Automation Tools
# =============================================================================
DNS_AUTOMATION_SOURCES = {
    # Infrastructure as Code
    "octodns": {
        "name": "OctoDNS — DNS as Code (GitHub)",
        "url": "https://github.com/octodns/octodns",
        "category": "automation",
    },
    "dnscontrol": {
        "name": "dnscontrol — DNS Configuration Management (Stack Exchange)",
        "url": "https://docs.dnscontrol.org/",
        "category": "automation",
    },
    "terraform_dns": {
        "name": "Terraform DNS Provider Documentation",
        "url": "https://registry.terraform.io/providers/hashicorp/dns/latest/docs",
        "category": "automation",
    },
    "terraform_cloudflare": {
        "name": "Terraform Cloudflare Provider — DNS Resources",
        "url": "https://registry.terraform.io/providers/cloudflare/cloudflare/latest/docs",
        "category": "automation",
    },
    "terraform_route53": {
        "name": "Terraform AWS Route 53 Resources",
        "url": "https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record",
        "category": "automation",
    },
    "cli53": {
        "name": "cli53 — Command Line Tool for Route 53",
        "url": "https://github.com/barnybug/cli53",
        "category": "automation",
    },
    "denominator": {
        "name": "Denominator — Portable DNS Client (Netflix)",
        "url": "https://github.com/Netflix/denominator",
        "category": "automation",
    },
}

# =============================================================================
# Cloud DNS Provider Documentation
# =============================================================================
CLOUD_DNS_SOURCES = {
    "aws_route53": {
        "name": "Amazon Route 53 Developer Guide",
        "url": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/",
        "category": "hosting",
    },
    "aws_route53_health": {
        "name": "Amazon Route 53 Health Checks and DNS Failover",
        "url": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html",
        "category": "hosting",
    },
    "gcp_cloud_dns": {
        "name": "Google Cloud DNS Documentation",
        "url": "https://cloud.google.com/dns/docs",
        "category": "hosting",
    },
    "azure_dns": {
        "name": "Azure DNS Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/dns/",
        "category": "hosting",
    },
    "cloudflare_dns": {
        "name": "Cloudflare DNS Documentation",
        "url": "https://developers.cloudflare.com/dns/",
        "category": "hosting",
    },
    "cloudflare_proxy": {
        "name": "Cloudflare Proxy (Orange Cloud) Documentation",
        "url": "https://developers.cloudflare.com/dns/manage-dns-records/reference/proxied-dns-records/",
        "category": "hosting",
    },
    "ns1_docs": {
        "name": "NS1 (IBM) Managed DNS Documentation",
        "url": "https://ns1.com/resources",
        "category": "hosting",
    },
    "dnsimple_docs": {
        "name": "DNSimple Documentation",
        "url": "https://support.dnsimple.com/",
        "category": "hosting",
    },
    "akamai_edgedns": {
        "name": "Akamai Edge DNS Documentation",
        "url": "https://techdocs.akamai.com/edge-dns/docs",
        "category": "hosting",
    },
}

# =============================================================================
# DNS Hosting Provider Documentation (for dns_providers taxonomy)
# =============================================================================
DNS_PROVIDER_SOURCES = {
    # ---- Provider-specific docs ----
    "cloudflare_dns_overview": {
        "name": "Cloudflare DNS — How Cloudflare DNS Works",
        "url": "https://developers.cloudflare.com/dns/concepts/",
        "category": "dns_providers",
    },
    "cloudflare_cname_flattening": {
        "name": "Cloudflare CNAME Flattening",
        "url": "https://developers.cloudflare.com/dns/cname-flattening/",
        "category": "dns_providers",
    },
    "route53_routing_policies": {
        "name": "Amazon Route 53 Routing Policies",
        "url": "https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy.html",
        "category": "dns_providers",
    },
    "route53_pricing": {
        "name": "Amazon Route 53 Pricing",
        "url": "https://aws.amazon.com/route53/pricing/",
        "category": "dns_providers",
    },
    "gcp_cloud_dns_overview": {
        "name": "Google Cloud DNS Overview and Concepts",
        "url": "https://cloud.google.com/dns/docs/overview",
        "category": "dns_providers",
    },
    "azure_dns_overview": {
        "name": "Azure DNS Overview",
        "url": "https://learn.microsoft.com/en-us/azure/dns/dns-overview",
        "category": "dns_providers",
    },
    "azure_traffic_manager": {
        "name": "Azure Traffic Manager Documentation",
        "url": "https://learn.microsoft.com/en-us/azure/traffic-manager/",
        "category": "dns_providers",
    },
    "ns1_filter_chains": {
        "name": "NS1 Filter Chains — Advanced DNS Traffic Steering",
        "url": "https://www.ibm.com/products/ns1-connect",
        "category": "dns_providers",
    },
    "akamai_edgedns_overview": {
        "name": "Akamai Edge DNS Product Overview",
        "url": "https://www.akamai.com/products/edge-dns",
        "category": "dns_providers",
    },
    "ultradns_overview": {
        "name": "UltraDNS (Vercara) Product Overview",
        "url": "https://www.vercara.com/ultradns",
        "category": "dns_providers",
    },
    "dnsimple_api": {
        "name": "DNSimple API Documentation",
        "url": "https://developer.dnsimple.com/",
        "category": "dns_providers",
    },
    "dns_made_easy": {
        "name": "DNS Made Easy Documentation",
        "url": "https://dnsmadeeasy.com/technology",
        "category": "dns_providers",
    },
    "he_dns": {
        "name": "Hurricane Electric Free DNS Hosting",
        "url": "https://dns.he.net/",
        "category": "dns_providers",
    },
    "constellix_docs": {
        "name": "Constellix DNS Documentation",
        "url": "https://constellix.com/docs/",
        "category": "dns_providers",
    },
    "bunny_dns": {
        "name": "Bunny DNS Documentation",
        "url": "https://docs.bunny.net/docs/dns-overview",
        "category": "dns_providers",
    },
    "porkbun_dns": {
        "name": "Porkbun DNS Management and API",
        "url": "https://porkbun.com/api/json/v3/documentation",
        "category": "dns_providers",
    },
    # ---- Comparison and evaluation resources ----
    "dnsperf_rankings": {
        "name": "DNSPerf — DNS Provider Performance Rankings",
        "url": "https://www.dnsperf.com/",
        "category": "dns_providers",
    },
    "cdnperf_dns": {
        "name": "CDNPerf DNS Performance Monitor",
        "url": "https://www.cdnperf.com/dns-providers",
        "category": "dns_providers",
    },
}

# =============================================================================
# DNS Debugging Tools Documentation
# =============================================================================
DNS_DEBUG_SOURCES = {
    "dig_man": {
        "name": "dig (Domain Information Groper) — ISC",
        "url": "https://bind9.readthedocs.io/en/latest/manpages.html#dig-dns-lookup-utility",
        "category": "dns_tools",
    },
    "delv_man": {
        "name": "delv — DNSSEC Validation Utility (ISC)",
        "url": "https://bind9.readthedocs.io/en/latest/manpages.html#delv-dns-lookup-and-validation-utility",
        "category": "dns_tools",
    },
    "drill_man": {
        "name": "drill — DNS Query Tool (Debian Man Page)",
        "url": "https://manpages.debian.org/testing/ldnsutils/drill.1.en.html",
        "category": "dns_tools",
    },
    "dog_dns": {
        "name": "dog — Command-Line DNS Client (GitHub)",
        "url": "https://github.com/ogham/dog",
        "category": "dns_tools",
    },
    "doggo": {
        "name": "doggo — Modern DNS Client for Humans",
        "url": "https://doggo.mrkaran.dev/",
        "category": "dns_tools",
    },
    "whatsmydns": {
        "name": "whatsmydns.net — Global DNS Propagation Checker",
        "url": "https://www.whatsmydns.net/",
        "category": "dns_tools",
    },
    "mxtoolbox": {
        "name": "MXToolbox — DNS, Email, and Network Diagnostic Tools",
        "url": "https://mxtoolbox.com/",
        "category": "dns_tools",
    },
    "dnscheck": {
        "name": "Zonemaster — DNS Delegation Quality Checker (IIS/AFNIC)",
        "url": "https://www.zonemaster.net/",
        "category": "dns_tools",
    },
    "intodns": {
        "name": "intoDNS — DNS and Mail Server Health Check",
        "url": "https://intodns.com/",
        "category": "dns_tools",
    },
}


def _all_dns_software_sources() -> dict:
    """Combine all DNS software source dictionaries."""
    return {
        **AUTHORITATIVE_DNS_SOURCES,
        **RESOLVER_DNS_SOURCES,
        **DNSSEC_TOOL_SOURCES,
        **DNS_AUTOMATION_SOURCES,
        **CLOUD_DNS_SOURCES,
        **DNS_PROVIDER_SOURCES,
        **DNS_DEBUG_SOURCES,
    }


@dataclass
class DnsSoftwareDocument:
    """A reference to a DNS software documentation page."""

    key: str
    name: str
    url: str
    category: str
    content: str = ""
    cached: bool = False


class DnsSoftwareFetcher:
    """Fetches DNS software and tooling documentation.

    Covers authoritative servers (BIND, Knot, NSD, PowerDNS),
    resolvers (Unbound, CoreDNS, systemd-resolved, Windows DNS),
    DNSSEC tools, automation frameworks, cloud DNS providers,
    and debugging/diagnostic tools.
    """

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def fetch_document(self, key: str) -> DnsSoftwareDocument | None:
        """Fetch a specific DNS software document by key."""
        sources = _all_dns_software_sources()
        if key not in sources:
            logger.error("Unknown DNS software document key: %s", key)
            return None

        info = sources[key]
        cache_file = self.cache_dir / f"dns_sw_{key}.html"

        doc = DnsSoftwareDocument(
            key=key,
            name=info["name"],
            url=info["url"],
            category=info["category"],
        )

        if cache_file.exists():
            doc.content = cache_file.read_text()
            doc.cached = True
            return doc

        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            try:
                response = await client.get(info["url"])
                response.raise_for_status()
                doc.content = response.text
                cache_file.write_text(doc.content)
                doc.cached = True
                logger.info("Fetched and cached DNS software document %s", key)
            except httpx.HTTPError as e:
                logger.error("Failed to fetch DNS software document %s: %s", key, e)
                return None

        return doc

    async def fetch_category_documents(self, category: str) -> list[DnsSoftwareDocument]:
        """Fetch all DNS software documents related to a taxonomy category."""
        sources = _all_dns_software_sources()
        docs = []
        for key, info in sources.items():
            if info["category"] == category:
                doc = await self.fetch_document(key)
                if doc:
                    docs.append(doc)
        return docs

    async def fetch_all(self) -> list[DnsSoftwareDocument]:
        """Fetch all DNS software documents."""
        docs = []
        for key in _all_dns_software_sources():
            doc = await self.fetch_document(key)
            if doc:
                docs.append(doc)
        return docs

    def list_available_sources(self) -> list[dict[str, str]]:
        """List all available DNS software document sources."""
        return [
            {"key": key, "name": info["name"], "category": info["category"], "url": info["url"]}
            for key, info in _all_dns_software_sources().items()
        ]
