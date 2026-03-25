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
    # ---- Domain & TLD Data ----
    "tlds": "https://data.iana.org/TLD/tlds-alpha-by-domain.txt",
    "root_db": "https://www.iana.org/domains/root/db",
    "root_zone_file": "https://www.internic.net/domain/root.zone",
    "root_hints": "https://www.internic.net/domain/named.root",
    "trust_anchors": "https://data.iana.org/root-anchors/root-anchors.xml",
    "special_use_domains": "https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xhtml",
    "special_use_csv": "https://www.iana.org/assignments/special-use-domain-names/special-use-domain.csv",

    # ---- DNS Parameters ----
    "dns_parameters": "https://www.iana.org/assignments/dns-parameters/dns-parameters.xhtml",
    "rr_types_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-4.csv",
    "opcodes_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-5.csv",
    "rcodes_csv": "https://www.iana.org/assignments/dns-parameters/dns-parameters-6.csv",
    "dns_classes": "https://www.iana.org/assignments/dns-parameters/dns-parameters-2.csv",
    "edns_options": "https://www.iana.org/assignments/dns-parameters/dns-parameters-11.csv",
    "edns_header_flags": "https://www.iana.org/assignments/dns-parameters/dns-parameters-13.csv",
    "dns_label_types": "https://www.iana.org/assignments/dns-parameters/dns-parameters-10.csv",
    "afsdb_rr_subtypes": "https://www.iana.org/assignments/dns-parameters/dns-parameters-1.csv",

    # ---- DNSSEC Parameters ----
    "dnskey_algorithms": "https://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers-1.csv",
    "ds_digest_types": "https://www.iana.org/assignments/ds-rr-types/ds-rr-types-1.csv",
    "nsec3_hash_algorithms": "https://www.iana.org/assignments/dnssec-nsec3-parameters/dnssec-nsec3-parameters-1.csv",
    "dnssec_parameters_page": "https://www.iana.org/assignments/dns-sec-alg-numbers/dns-sec-alg-numbers.xhtml",

    # ---- RDAP ----
    "rdap_bootstrap": "https://data.iana.org/rdap/dns.json",
    "rdap_ipv4_bootstrap": "https://data.iana.org/rdap/ipv4.json",
    "rdap_ipv6_bootstrap": "https://data.iana.org/rdap/ipv6.json",
    "rdap_asn_bootstrap": "https://data.iana.org/rdap/asn.json",
    "rdap_object_tags": "https://data.iana.org/rdap/object-tags.json",

    # NOTE: whois_servers removed — it was a duplicate of root_db
    # (same URL: https://www.iana.org/domains/root/db).
    # WHOIS server info is available on each TLD's root_db page.

    # ---- Well-Known Services ----
    "service_names_csv": "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.csv",
    "well_known_uris": "https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml",

    # ---- TLS Parameters ----
    "tls_parameters": "https://www.iana.org/assignments/tls-parameters/tls-parameters.xhtml",
    "tls_cipher_suites": "https://www.iana.org/assignments/tls-parameters/tls-parameters-4.csv",

    # ---- HTTP & URI ----
    "http_status_codes": "https://www.iana.org/assignments/http-status-codes/http-status-codes-1.csv",
    "http_methods": "https://www.iana.org/assignments/http-methods/http-methods.xhtml",
    "uri_schemes": "https://www.iana.org/assignments/uri-schemes/uri-schemes-1.csv",

    # ---- Email Parameters ----
    "email_auth_methods": "https://www.iana.org/assignments/email-auth/email-auth.xhtml",
    "spf_qualifiers": "https://www.iana.org/assignments/spf-parameters/spf-parameters.xhtml",
    "dkim_parameters": "https://www.iana.org/assignments/dkim-parameters/dkim-parameters.xhtml",

    # ---- EPP ----
    "epp_extensions": "https://www.iana.org/assignments/epp-extensions/epp-extensions.xhtml",

    # ---- RDAP & DANE ----
    "rdap_extensions": "https://www.iana.org/assignments/rdap-extensions/rdap-extensions.xhtml",
    "dane_parameters": "https://www.iana.org/assignments/dane-parameters/dane-parameters.xhtml",
}


@dataclass
class DnsRrType:
    """A DNS resource record type from the IANA registry."""

    type_name: str
    value: int
    meaning: str
    reference: str


@dataclass
class SpecialUseDomain:
    """A special-use domain name from IANA registry."""

    name: str
    reference: str


@dataclass
class DnssecAlgorithm:
    """A DNSSEC algorithm from IANA registry."""

    number: int
    description: str
    mnemonic: str
    reference: str


@dataclass
class RootHintServer:
    """A root nameserver from the root hints file."""

    hostname: str
    ipv4: str = ""
    ipv6: str = ""


@dataclass
class IanaData:
    """Collection of fetched IANA data."""

    tld_list: list[str] = field(default_factory=list)
    rr_types: list[DnsRrType] = field(default_factory=list)
    rdap_services: dict = field(default_factory=dict)
    special_use_domains: list[SpecialUseDomain] = field(default_factory=list)
    dnssec_algorithms: list[DnssecAlgorithm] = field(default_factory=list)
    root_hints: list[RootHintServer] = field(default_factory=list)


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

    async def fetch_special_use_domains(self) -> list[SpecialUseDomain]:
        """Fetch the special-use domain names registry from IANA."""
        text = await self._fetch_url(
            IANA_URLS["special_use_csv"], "special-use-domain-names.csv"
        )
        if not text:
            return []

        domains = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            try:
                name = row.get("Name", row.get("name", "")).strip()
                reference = row.get("Reference", row.get("reference", "")).strip()

                if not name:
                    continue

                domains.append(SpecialUseDomain(name=name, reference=reference))
            except (ValueError, KeyError):
                continue

        logger.info("Fetched %d special-use domain names from IANA", len(domains))
        return domains

    async def fetch_dnssec_algorithms(self) -> list[DnssecAlgorithm]:
        """Fetch DNSSEC algorithm numbers from IANA registry."""
        text = await self._fetch_url(
            IANA_URLS["dnskey_algorithms"], "dnssec-algorithms.csv"
        )
        if not text:
            return []

        algorithms = []
        reader = csv.DictReader(io.StringIO(text))
        for row in reader:
            try:
                number_str = row.get("Number", row.get("number", "")).strip()
                description = row.get("Description", row.get("description", "")).strip()
                mnemonic = row.get("Mnemonic", row.get("mnemonic", "")).strip()
                reference = row.get("Reference", row.get("reference", "")).strip()

                if not number_str or not description:
                    continue

                # Skip ranges like "123-251"
                if "-" in number_str:
                    continue

                algorithms.append(
                    DnssecAlgorithm(
                        number=int(number_str),
                        description=description,
                        mnemonic=mnemonic,
                        reference=reference,
                    )
                )
            except (ValueError, KeyError):
                continue

        logger.info("Fetched %d DNSSEC algorithms from IANA", len(algorithms))
        return algorithms

    async def fetch_root_hints(self) -> list[RootHintServer]:
        """Fetch and parse the root nameserver hints file."""
        text = await self._fetch_url(IANA_URLS["root_hints"], "named.root")
        if not text:
            return []

        servers: dict[str, RootHintServer] = {}
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith(";"):
                continue

            parts = line.split()
            if len(parts) < 4:
                continue

            hostname = parts[0].rstrip(".").upper()
            rr_type = parts[2].upper() if len(parts) >= 4 else parts[1].upper()
            address = parts[-1]

            if rr_type == "NS":
                ns_name = address.rstrip(".").upper()
                if ns_name not in servers:
                    servers[ns_name] = RootHintServer(hostname=ns_name)
            elif rr_type == "A":
                if hostname not in servers:
                    servers[hostname] = RootHintServer(hostname=hostname)
                servers[hostname].ipv4 = address
            elif rr_type == "AAAA":
                if hostname not in servers:
                    servers[hostname] = RootHintServer(hostname=hostname)
                servers[hostname].ipv6 = address

        result = sorted(servers.values(), key=lambda s: s.hostname)
        logger.info("Fetched %d root nameservers from hints file", len(result))
        return result

    async def fetch_all(self) -> IanaData:
        """Fetch all IANA data sources."""
        data = IanaData()
        data.tld_list = await self.fetch_tld_list()
        data.rr_types = await self.fetch_rr_types()
        data.rdap_services = await self.fetch_rdap_bootstrap()
        data.special_use_domains = await self.fetch_special_use_domains()
        data.dnssec_algorithms = await self.fetch_dnssec_algorithms()
        data.root_hints = await self.fetch_root_hints()
        return data
