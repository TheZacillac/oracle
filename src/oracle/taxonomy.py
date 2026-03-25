"""Comprehensive topic taxonomy for the domain name industry.

This is the single source of truth for what the training dataset covers.
Every generated example maps to a (category, subcategory, topic) triple.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Topic:
    """A specific knowledge topic within a subcategory."""

    name: str
    description: str
    key_concepts: list[str] = field(default_factory=list)
    rfcs: list[str] = field(default_factory=list)
    difficulty_range: tuple[str, str] = ("beginner", "expert")


@dataclass(frozen=True)
class Subcategory:
    """A grouping of related topics within a category."""

    name: str
    slug: str
    description: str
    topics: list[Topic] = field(default_factory=list)


@dataclass(frozen=True)
class Category:
    """A top-level knowledge domain."""

    name: str
    slug: str
    description: str
    subcategories: list[Subcategory] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Full taxonomy
# ---------------------------------------------------------------------------

TAXONOMY: list[Category] = [
    # ===================================================================
    # 1. DNS PROTOCOL & STANDARDS
    # ===================================================================
    Category(
        name="DNS Protocol & Standards",
        slug="dns",
        description="The Domain Name System protocol, its architecture, record types, extensions, and security mechanisms.",
        subcategories=[
            Subcategory(
                name="DNS Fundamentals",
                slug="fundamentals",
                description="Core DNS architecture and resolution process.",
                topics=[
                    Topic(
                        name="DNS architecture overview",
                        description="Hierarchical namespace, distributed database, root-TLD-authoritative model. RFC 8499 is the authoritative DNS terminology reference.",
                        key_concepts=["hierarchical namespace", "distributed database", "root zone", "delegation", "authority"],
                        rfcs=["RFC 1034", "RFC 1035", "RFC 8499"],
                    ),
                    Topic(
                        name="Name resolution process",
                        description="Recursive vs iterative resolution, stub resolvers, full resolvers, caching.",
                        key_concepts=["recursive resolution", "iterative resolution", "stub resolver", "full resolver", "caching", "TTL"],
                        rfcs=["RFC 1034", "RFC 1035"],
                    ),
                    Topic(
                        name="DNS namespace and labels",
                        description="Label rules, FQDN structure, maximum lengths, case insensitivity. RFC 2181 clarifies multiple edge cases.",
                        key_concepts=["FQDN", "labels", "253-character limit", "63-character label limit", "case-insensitive"],
                        rfcs=["RFC 1035", "RFC 2181", "RFC 4343"],
                    ),
                    Topic(
                        name="Zones and delegation",
                        description="Zone cuts, delegation via NS records, glue records, zone authority.",
                        key_concepts=["zone", "zone cut", "delegation", "NS records", "glue records", "zone of authority"],
                        rfcs=["RFC 1034", "RFC 1035"],
                    ),
                    Topic(
                        name="Root server system",
                        description="13 root server identifiers (A-M), anycast, root zone management, priming. Over 1,500 anycast instances worldwide.",
                        key_concepts=["root servers", "anycast", "root hints", "priming query", "RSSAC", "root server letters", "anycast instances"],
                        rfcs=["RFC 8109", "RFC 7720"],
                    ),
                    Topic(
                        name="Caching and TTL",
                        description="Response caching, TTL semantics, negative caching, minimum TTL.",
                        key_concepts=["TTL", "positive caching", "negative caching", "NXDOMAIN", "minimum TTL"],
                        rfcs=["RFC 1035", "RFC 2308"],
                    ),
                    Topic(
                        name="DNS message format",
                        description="Header, question, answer, authority, additional sections, compression. RFC 2181 clarifies TTL interpretation, RDATA canonicalization, and other DNS edge cases.",
                        key_concepts=["header", "QR flag", "opcode", "RCODE", "message compression", "EDNS"],
                        rfcs=["RFC 1035", "RFC 2181", "RFC 6895"],
                    ),
                ],
            ),
            Subcategory(
                name="Record Types",
                slug="record_types",
                description="DNS resource record types, their formats, and use cases.",
                topics=[
                    Topic(
                        name="A and AAAA records",
                        description="IPv4 and IPv6 address records, dual-stack resolution.",
                        key_concepts=["A record", "AAAA record", "IPv4", "IPv6", "dual-stack", "happy eyeballs"],
                        rfcs=["RFC 1035", "RFC 3596"],
                    ),
                    Topic(
                        name="CNAME records",
                        description="Canonical name aliases, CNAME restrictions, CNAME at zone apex problem.",
                        key_concepts=["CNAME", "canonical name", "alias", "zone apex restriction", "CNAME chain"],
                        rfcs=["RFC 1034", "RFC 1035"],
                    ),
                    Topic(
                        name="MX records",
                        description="Mail exchange records, priority, fallback, null MX.",
                        key_concepts=["MX record", "preference value", "mail routing", "null MX", "fallback"],
                        rfcs=["RFC 1035", "RFC 7505"],
                    ),
                    Topic(
                        name="NS records",
                        description="Name server delegation, NS at zone apex, NS in delegations.",
                        key_concepts=["NS record", "delegation", "authoritative nameserver", "zone apex"],
                        rfcs=["RFC 1035"],
                    ),
                    Topic(
                        name="SOA records",
                        description="Start of authority, zone parameters, serial number conventions.",
                        key_concepts=["SOA", "MNAME", "RNAME", "serial number", "refresh", "retry", "expire", "minimum TTL"],
                        rfcs=["RFC 1035", "RFC 2308"],
                    ),
                    Topic(
                        name="TXT records",
                        description="Text records, common uses (SPF, DKIM, domain verification), size limits.",
                        key_concepts=["TXT record", "character string", "255-byte limit", "multiple strings", "verification"],
                        rfcs=["RFC 1035", "RFC 7208"],
                    ),
                    Topic(
                        name="SRV records",
                        description="Service location records, priority, weight, port, target.",
                        key_concepts=["SRV record", "service", "protocol", "priority", "weight", "port"],
                        rfcs=["RFC 2782"],
                    ),
                    Topic(
                        name="PTR records",
                        description="Pointer records for reverse DNS, in-addr.arpa, ip6.arpa.",
                        key_concepts=["PTR record", "reverse DNS", "in-addr.arpa", "ip6.arpa", "rDNS"],
                        rfcs=["RFC 1035", "RFC 3596"],
                    ),
                    Topic(
                        name="CAA records",
                        description="Certification Authority Authorization, issuance control, iodef reporting.",
                        key_concepts=["CAA record", "issue", "issuewild", "iodef", "CA authorization"],
                        rfcs=["RFC 8659"],
                    ),
                    Topic(
                        name="NAPTR records",
                        description="Naming Authority Pointer, ENUM, regex rewriting, service discovery.",
                        key_concepts=["NAPTR", "ENUM", "DDDS", "regex", "replacement", "service field"],
                        rfcs=["RFC 3403", "RFC 6116"],
                    ),
                    Topic(
                        name="DNAME records",
                        description="Delegation name records, subtree redirection, differences from CNAME.",
                        key_concepts=["DNAME", "subtree redirection", "non-terminal delegation"],
                        rfcs=["RFC 6672"],
                    ),
                    Topic(
                        name="DS and DNSKEY records",
                        description="Delegation signer and DNSSEC key records, trust chain.",
                        key_concepts=["DS record", "DNSKEY", "key tag", "algorithm", "digest", "trust anchor"],
                        rfcs=["RFC 4034", "RFC 4035"],
                    ),
                    Topic(
                        name="TLSA records",
                        description="TLS authentication via DNS (DANE), certificate association.",
                        key_concepts=["TLSA", "DANE", "certificate usage", "selector", "matching type"],
                        rfcs=["RFC 6698", "RFC 7671"],
                    ),
                    Topic(
                        name="SVCB and HTTPS records",
                        description="Service binding records, HTTPS resource record, ECH, AliasMode.",
                        key_concepts=["SVCB", "HTTPS RR", "AliasMode", "ServiceMode", "alpn", "ECH", "priority"],
                        rfcs=["RFC 9460"],
                    ),
                    Topic(
                        name="SSHFP records",
                        description="SSH fingerprint records for host key verification via DNS.",
                        key_concepts=["SSHFP", "SSH host key", "fingerprint", "algorithm", "digest type"],
                        rfcs=["RFC 4255", "RFC 6594"],
                    ),
                ],
            ),
            Subcategory(
                name="DNSSEC",
                slug="dnssec",
                description="DNS Security Extensions for authentication and integrity.",
                topics=[
                    Topic(
                        name="DNSSEC overview and purpose",
                        description="Origin authentication, data integrity, authenticated denial of existence.",
                        key_concepts=["authentication", "integrity", "chain of trust", "signed zone"],
                        rfcs=["RFC 4033"],
                    ),
                    Topic(
                        name="DNSSEC signing process",
                        description="Zone signing, ZSK/KSK model, RRSIG generation, signature validity. Online vs offline signing: online signing keeps the KSK always available; offline signing uses air-gapped HSMs with periodic re-signing.",
                        key_concepts=["ZSK", "KSK", "RRSIG", "signature inception", "expiration", "zone signing", "online signing", "offline signing", "HSM"],
                        rfcs=["RFC 4034", "RFC 4035", "RFC 6781"],
                    ),
                    Topic(
                        name="DNSSEC validation",
                        description="Resolver validation, trust anchor configuration, chain of trust walkthrough.",
                        key_concepts=["validation", "trust anchor", "chain of trust", "DNSKEY", "DS", "RRSIG"],
                        rfcs=["RFC 4035"],
                    ),
                    Topic(
                        name="NSEC and NSEC3",
                        description="Authenticated denial of existence, zone walking, opt-out. NSEC5 is a newer proposal to prevent offline dictionary attacks against NSEC3.",
                        key_concepts=["NSEC", "NSEC3", "NSEC3PARAM", "zone walking", "opt-out", "white lies", "NSEC5"],
                        rfcs=["RFC 4034", "RFC 5155"],
                    ),
                    Topic(
                        name="Key management and rollovers",
                        description="Key lifecycle, ZSK rollover, KSK rollover, algorithm rollover, timing.",
                        key_concepts=["key rollover", "pre-publish", "double-sign", "RFC 7583 timers", "algorithm rollover"],
                        rfcs=["RFC 7583", "RFC 6781"],
                    ),
                    Topic(
                        name="DNSSEC deployment challenges",
                        description="Operational complexity, response size, middlebox issues, adoption barriers.",
                        key_concepts=["response size", "UDP truncation", "middlebox interference", "adoption rate"],
                        rfcs=["RFC 6781"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNSSEC algorithm selection and deprecation",
                        description="Algorithm recommendation matrix per RFC 8624. RSA/SHA-1 (algorithms 5, 7) deprecated. ECDSA P-256 (algorithm 13) is current recommendation. Ed25519 (algorithm 15) and Ed448 (algorithm 16) for future. HSM considerations for algorithm choice.",
                        key_concepts=["algorithm 8", "algorithm 13", "algorithm 15", "RFC 8624", "ECDSA P-256", "Ed25519", "RSA deprecation", "MUST NOT sign"],
                        rfcs=["RFC 8624"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="CDS/CDNSKEY automated DNSSEC delegation",
                        description="Automated DNSSEC delegation maintenance using CDS and CDNSKEY records. Child-to-parent signaling for DS record updates. RFC 7344 defines the mechanism, RFC 8078 defines the bootstrapping process. Reduces operational burden of DNSSEC key management.",
                        key_concepts=["CDS", "CDNSKEY", "automated delegation", "DS record updates", "child-to-parent signaling", "DNSSEC bootstrapping"],
                        rfcs=["RFC 7344", "RFC 8078"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="DNS Transport",
                slug="transport",
                description="DNS transport protocols and encrypted DNS.",
                topics=[
                    Topic(
                        name="DNS over UDP and TCP",
                        description="Traditional transports, UDP truncation, TCP fallback, persistent connections.",
                        key_concepts=["UDP", "TCP", "truncation", "TC flag", "512 bytes", "persistent TCP"],
                        rfcs=["RFC 1035", "RFC 7766"],
                    ),
                    Topic(
                        name="DNS over HTTPS (DoH)",
                        description="DNS queries over HTTPS, privacy, bypassing, content-type, wire format.",
                        key_concepts=["DoH", "HTTPS", "privacy", "content-type", "centralization concerns", "application/dns-message"],
                        rfcs=["RFC 8484"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS over TLS (DoT)",
                        description="Encrypted DNS on port 853, opportunistic vs strict mode.",
                        key_concepts=["DoT", "TLS", "port 853", "opportunistic", "strict mode", "privacy"],
                        rfcs=["RFC 7858"],
                    ),
                    Topic(
                        name="DNS over QUIC (DoQ)",
                        description="DNS over QUIC transport, 0-RTT, connection migration.",
                        key_concepts=["DoQ", "QUIC", "0-RTT", "connection migration", "port 853"],
                        rfcs=["RFC 9250"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Extensions",
                slug="extensions",
                description="Protocol extensions and operational enhancements.",
                topics=[
                    Topic(
                        name="EDNS(0)",
                        description="Extension mechanisms for DNS, larger UDP, OPT record, options. The DO bit (DNSSEC OK) enables DNSSEC validation.",
                        key_concepts=["EDNS0", "OPT record", "UDP payload size", "extended RCODE", "version", "DO bit"],
                        rfcs=["RFC 6891"],
                    ),
                    Topic(
                        name="EDNS Client Subnet (ECS)",
                        description="Client subnet information for geo-aware DNS responses.",
                        key_concepts=["ECS", "client subnet", "source prefix", "scope prefix", "privacy"],
                        rfcs=["RFC 7871"],
                    ),
                    Topic(
                        name="DNS cookies",
                        description="Lightweight transaction authentication to mitigate amplification and forgery.",
                        key_concepts=["DNS cookies", "client cookie", "server cookie", "amplification mitigation"],
                        rfcs=["RFC 7873"],
                    ),
                    Topic(
                        name="TSIG authentication",
                        description="Transaction signatures for server-to-server authentication.",
                        key_concepts=["TSIG", "HMAC", "shared secret", "zone transfer auth", "dynamic update auth"],
                        rfcs=["RFC 8945"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Security Threats",
                slug="security_threats",
                description="Attacks against DNS and their mitigations.",
                topics=[
                    Topic(
                        name="Cache poisoning",
                        description="Kaminsky attack, birthday attacks, source port randomization, DNSSEC mitigation.",
                        key_concepts=["cache poisoning", "Kaminsky attack", "source port randomization", "TXID", "bailiwick checking"],
                        rfcs=["RFC 5452"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS amplification attacks",
                        description="Reflective DDoS using open resolvers, response rate limiting.",
                        key_concepts=["amplification", "reflection", "open resolver", "RRL", "BCP 38"],
                        rfcs=["RFC 5358"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS tunneling",
                        description="Data exfiltration through DNS queries, detection techniques.",
                        key_concepts=["DNS tunneling", "exfiltration", "encoded payloads", "detection", "anomaly analysis"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS hijacking and interception",
                        description="BGP hijacking, rogue resolvers, NXDOMAIN rewriting, transparent proxies.",
                        key_concepts=["DNS hijacking", "BGP hijack", "NXDOMAIN rewriting", "transparent proxy"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Zone Management",
                slug="zone_management",
                description="DNS zone file operations and best practices.",
                topics=[
                    Topic(
                        name="Zone file format",
                        description="Master file syntax, directives ($ORIGIN, $TTL, $INCLUDE), resource record syntax.",
                        key_concepts=["zone file", "$ORIGIN", "$TTL", "$INCLUDE", "master file format"],
                        rfcs=["RFC 1035"],
                    ),
                    Topic(
                        name="Zone transfers (AXFR/IXFR)",
                        description="Full and incremental zone transfers, NOTIFY, TSIG authentication.",
                        key_concepts=["AXFR", "IXFR", "NOTIFY", "TSIG", "zone replication"],
                        rfcs=["RFC 5936", "RFC 1995", "RFC 1996"],
                    ),
                    Topic(
                        name="Dynamic DNS updates",
                        description="RFC 2136 dynamic updates, prerequisites, security considerations.",
                        key_concepts=["dynamic update", "prerequisites", "TSIG auth", "update policy"],
                        rfcs=["RFC 2136", "RFC 3007"],
                    ),
                    Topic(
                        name="Anycast DNS",
                        description="Anycast routing for DNS, benefits, operational considerations.",
                        key_concepts=["anycast", "BGP", "load distribution", "resilience", "catchment"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="ZONEMD (Zone Message Digest)",
                        description="Zone file integrity verification via a cryptographic digest stored in a DNS record. Growing in importance for signed zone distribution and offline zone file validation.",
                        key_concepts=["ZONEMD", "zone digest", "integrity verification", "zone distribution", "cryptographic hash"],
                        rfcs=["RFC 8976"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="DNS Privacy & Modern Extensions",
                slug="privacy",
                description="Privacy-enhancing DNS technologies and modern protocol extensions.",
                topics=[
                    Topic(
                        name="DNS query name minimisation",
                        description="Sending only necessary labels to each resolver in the chain, QNAME minimisation.",
                        key_concepts=["QNAME minimisation", "privacy", "minimal query", "resolver behavior"],
                        rfcs=["RFC 9156"],
                    ),
                    Topic(
                        name="DNS64 and NAT64 interaction",
                        description="DNS64 synthesis of AAAA records for IPv4-only hosts, NAT64 translation.",
                        key_concepts=["DNS64", "NAT64", "AAAA synthesis", "IPv6 transition", "464XLAT"],
                        rfcs=["RFC 6147"],
                    ),
                    Topic(
                        name="mDNS (Multicast DNS)",
                        description="Link-local name resolution without a DNS server, .local domain, Bonjour/Avahi.",
                        key_concepts=["mDNS", "multicast", ".local", "link-local", "Bonjour", "Avahi"],
                        rfcs=["RFC 6762"],
                    ),
                    Topic(
                        name="DNS-SD (DNS Service Discovery)",
                        description="Service discovery using DNS records, _tcp/_udp conventions, SRV+TXT patterns.",
                        key_concepts=["DNS-SD", "service discovery", "_tcp", "_udp", "SRV", "TXT", "browse domain"],
                        rfcs=["RFC 6763"],
                    ),
                    Topic(
                        name="Oblivious DNS over HTTPS (ODoH)",
                        description="Privacy-preserving DNS via proxied DoH, preventing resolver from seeing client IP.",
                        key_concepts=["ODoH", "oblivious", "proxy", "target", "client privacy", "HPKE"],
                        rfcs=["RFC 9230"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS privacy in practice: trade-offs and deployment",
                        description="Synthesizing QNAME minimisation, DoH/DoT, and ECS into a practical privacy view. Real-world privacy trade-offs between performance (ECS for CDN routing) and privacy (minimisation).",
                        key_concepts=["privacy trade-offs", "QNAME minimisation + DoH", "ECS privacy cost", "practical privacy", "deployment choices"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 2. DOMAIN NAME REGISTRATION
    # ===================================================================
    Category(
        name="Domain Name Registration",
        slug="registration",
        description="The domain name registration lifecycle, processes, and protocols.",
        subcategories=[
            Subcategory(
                name="Registration Lifecycle",
                slug="lifecycle",
                description="Domain states from registration through deletion.",
                topics=[
                    Topic(
                        name="Domain lifecycle overview",
                        description="Complete lifecycle: available → registered → active → expired → redemption → pending delete → available.",
                        key_concepts=["registration", "active", "expiry", "auto-renew grace", "redemption grace", "pending delete"],
                    ),
                    Topic(
                        name="Grace periods",
                        description="Add grace, renew grace, auto-renew grace, transfer grace, redemption grace period. ERRP (Expired Registration Recovery Policy) covers 40-day redemption period notification requirements.",
                        key_concepts=["AGP", "renew grace", "auto-renew grace", "transfer grace", "RGP", "ICANN policy", "ERRP"],
                    ),
                    Topic(
                        name="Domain expiry and redemption",
                        description="What happens when a domain expires, redemption process, restoration fees.",
                        key_concepts=["expiry", "hold", "redemption", "restore", "pending delete", "30-day redemption"],
                    ),
                    Topic(
                        name="Domain deletion and release",
                        description="Pending delete period, drop catching, backorder services.",
                        key_concepts=["pending delete", "5-day delete", "drop catching", "backorder"],
                    ),
                    Topic(
                        name="Domain renewal",
                        description="Renewal process, multi-year registration, auto-renewal, maximum registration period.",
                        key_concepts=["renewal", "auto-renew", "10-year maximum", "renewal reminder"],
                    ),
                ],
            ),
            Subcategory(
                name="Domain Transfers",
                slug="transfers",
                description="Inter-registrar and inter-registrant domain transfers.",
                topics=[
                    Topic(
                        name="Registrar transfer process",
                        description="Auth code, gaining/losing registrar workflow, 5-day pendency, ICANN transfer policy.",
                        key_concepts=["auth code", "EPP auth info", "gaining registrar", "losing registrar", "FOA", "transfer policy"],
                    ),
                    Topic(
                        name="Transfer restrictions",
                        description="60-day lock after registration/transfer, registrar lock, transfer disputes. Many ccTLDs have different transfer rules (no auth code, different lock periods).",
                        key_concepts=["60-day lock", "transfer lock", "TDRP", "transfer dispute", "ccTLD transfer rules"],
                    ),
                    Topic(
                        name="Transfer fraud and hijacking risks",
                        description="Vulnerabilities in the transfer process: registrar social engineering, unauthorized transfer initiation, auth code theft. Case studies of domain hijacking via transfer fraud.",
                        key_concepts=["transfer fraud", "social engineering", "unauthorized transfer", "auth code theft", "registrar verification"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Change of registrant (IRTP-C)",
                        description="Material change of registrant, 60-day lock opt-out, designated agent.",
                        key_concepts=["change of registrant", "material change", "designated agent", "60-day lock"],
                    ),
                    Topic(
                        name="Bulk and portfolio transfers",
                        description="Transferring large domain portfolios, bulk transfer mechanisms.",
                        key_concepts=["bulk transfer", "portfolio transfer", "registrar migration"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="EPP Protocol",
                slug="epp",
                description="Extensible Provisioning Protocol for domain registration.",
                topics=[
                    Topic(
                        name="EPP overview",
                        description="Client-server protocol for provisioning, object types, transport over TCP/TLS.",
                        key_concepts=["EPP", "provisioning", "XML", "TLS transport", "TCP/TLS"],
                        rfcs=["RFC 5730", "RFC 5734"],
                    ),
                    Topic(
                        name="EPP domain operations",
                        description="Domain check, create, info, update, delete, transfer, renew commands.",
                        key_concepts=["domain:check", "domain:create", "domain:info", "domain:update", "domain:transfer", "domain:renew"],
                        rfcs=["RFC 5731"],
                    ),
                    Topic(
                        name="EPP contact and host objects",
                        description="Contact provisioning, host objects, linked vs unlinked hosts.",
                        key_concepts=["contact object", "host object", "linked host", "superordinate domain"],
                        rfcs=["RFC 5732", "RFC 5733"],
                    ),
                    Topic(
                        name="EPP status codes",
                        description="Client and server status codes, their meanings and effects on domain operations.",
                        key_concepts=[
                            "clientHold", "serverHold", "clientTransferProhibited", "serverTransferProhibited",
                            "clientDeleteProhibited", "serverDeleteProhibited", "clientUpdateProhibited",
                            "serverUpdateProhibited", "ok", "pendingCreate", "pendingDelete", "pendingTransfer",
                        ],
                        rfcs=["RFC 5731"],
                    ),
                    Topic(
                        name="EPP extensions",
                        description="Registry-specific extensions, DNSSEC extension, fee extension.",
                        key_concepts=["EPP extension", "secDNS extension", "fee extension", "launch extension", "RGCE"],
                        rfcs=["RFC 5910", "RFC 8748"],
                    ),
                ],
            ),
            Subcategory(
                name="Registration Data",
                slug="registration_data",
                description="Domain registration information and data accuracy.",
                topics=[
                    Topic(
                        name="WHOIS data fields",
                        description="Registrant, admin, tech, billing contacts, dates, nameservers, status.",
                        key_concepts=["registrant", "admin contact", "tech contact", "creation date", "expiry date", "nameservers"],
                    ),
                    Topic(
                        name="Registration data accuracy",
                        description="ICANN WHOIS accuracy program, validation, verification requirements.",
                        key_concepts=["WDRP", "accuracy", "validation", "verification", "RAA 2013"],
                    ),
                    Topic(
                        name="Domain privacy and proxy services",
                        description="Privacy services, proxy registrations, ICANN accreditation, relay obligations.",
                        key_concepts=["privacy service", "proxy registration", "accredited privacy", "relay", "reveal"],
                    ),
                    Topic(
                        name="Registration data and GDPR",
                        description="Impact of GDPR on registration data, temporary specification, EPDP outcomes.",
                        key_concepts=["GDPR", "temporary specification", "EPDP Phase 1", "legitimate purpose", "redacted data"],
                    ),
                ],
            ),
            Subcategory(
                name="Pricing and Premium Domains",
                slug="pricing",
                description="Domain pricing models, premium names, and reserved names.",
                topics=[
                    Topic(
                        name="Domain pricing models",
                        description="Standard pricing, tiered pricing, registry premium names, aftermarket premiums.",
                        key_concepts=["standard pricing", "premium pricing", "tiered registration", "renewal pricing"],
                    ),
                    Topic(
                        name="Reserved and restricted names",
                        description="ICANN-reserved names, registry-reserved names, two-character restrictions.",
                        key_concepts=["reserved names", "restricted names", "two-character labels", "ICANN specification 5"],
                    ),
                    Topic(
                        name="Internationalized domain names (IDNs)",
                        description="Punycode, IDN tables, script mixing, IDNA 2008.",
                        key_concepts=["IDN", "Punycode", "xn--", "IDNA 2008", "IDN tables", "script mixing"],
                        rfcs=["RFC 5890", "RFC 5891", "RFC 5892", "RFC 5893"],
                    ),
                    Topic(
                        name="Domain hacks and creative TLD usage",
                        description="Using ccTLDs creatively (del.icio.us, bit.ly, youtu.be), brand domain hacks.",
                        key_concepts=["domain hack", "creative TLD", ".ly", ".io", ".ai", ".tv", "ccTLD as gTLD"],
                    ),
                    Topic(
                        name="ccTLD-as-gTLD usage patterns",
                        description="Country code TLDs used globally (.io, .ai, .co, .tv, .me), risks and governance.",
                        key_concepts=[".io", ".ai", ".co", ".tv", ".me", "global usage", "sovereignty risk", "ccTLD repurposing"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 3. TLD ECOSYSTEM
    # ===================================================================
    Category(
        name="TLD Ecosystem",
        slug="tlds",
        description="Top-level domain types, operators, policies, and governance.",
        subcategories=[
            Subcategory(
                name="TLD Types",
                slug="types",
                description="Classification of top-level domains.",
                topics=[
                    Topic(
                        name="Generic TLDs (gTLDs)",
                        description="Original gTLDs (.com, .net, .org), their history and current operators.",
                        key_concepts=["gTLD", ".com", ".net", ".org", ".info", ".biz", "Verisign", "PIR"],
                    ),
                    Topic(
                        name="Country code TLDs (ccTLDs)",
                        description="ISO 3166-1 based TLDs, sovereignty, local policies, IDN ccTLDs.",
                        key_concepts=["ccTLD", "ISO 3166-1", "sovereignty", "local presence", "IDN ccTLD"],
                    ),
                    Topic(
                        name="New gTLDs (2012+ program)",
                        description="New gTLD program, application process, categories, objection mechanisms.",
                        key_concepts=["new gTLD", "applicant guidebook", "string contention", "objection", "delegation"],
                    ),
                    Topic(
                        name="Sponsored TLDs (sTLDs)",
                        description="TLDs with sponsoring organizations (.gov, .edu, .museum, .aero, .coop).",
                        key_concepts=["sTLD", "sponsoring organization", "eligibility", ".gov", ".edu"],
                    ),
                    Topic(
                        name="Brand TLDs",
                        description="Corporate brand TLDs (.google, .amazon, .apple), spec 13, operational models. Fully closed registries (only the brand's own domains), Specification 13 requirements differ from open registries, some brands use their TLD internally only.",
                        key_concepts=["brand TLD", ".brand", "spec 13", "closed generic", "defensive TLD", "closed registry", "internal-only TLD", "dotBrand operational model"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Geographic TLDs",
                        description="City and regional TLDs (.london, .nyc, .berlin, .paris), GAC advice.",
                        key_concepts=["geographic TLD", "geoTLD", "GAC advice", "community priority"],
                    ),
                    Topic(
                        name="Infrastructure TLD (.arpa)",
                        description="Address and Routing Parameter Area, in-addr.arpa, ip6.arpa, home.arpa.",
                        key_concepts=[".arpa", "in-addr.arpa", "ip6.arpa", "home.arpa", "infrastructure"],
                        rfcs=["RFC 3172"],
                    ),
                ],
            ),
            Subcategory(
                name="Registry Operations",
                slug="registry_ops",
                description="How TLD registries operate.",
                topics=[
                    Topic(
                        name="Registry operator role",
                        description="SRS operation, zone generation, WHOIS/RDAP, abuse handling. SRS is specific to gTLDs with multiple registrars; ccTLDs with direct registration models may not use this architecture.",
                        key_concepts=["registry operator", "SRS", "shared registration system", "zone file", "escrow", "direct registration model"],
                    ),
                    Topic(
                        name="Registry agreements with ICANN",
                        description="Base Registry Agreement, specifications (Spec 4: registration data, Spec 6: registry services, Spec 13: brand TLDs), amendments, renewals.",
                        key_concepts=["Registry Agreement", "base agreement", "specification 1-13", "Spec 4", "Spec 6", "Spec 13", "PIR", "Verisign"],
                    ),
                    Topic(
                        name="Registry data escrow",
                        description="Data escrow requirements, ICANN-approved escrow agents, escrow format.",
                        key_concepts=["data escrow", "ICANN-approved escrow agents", "Iron Mountain", "RDE", "ICANN specification 2"],
                    ),
                    Topic(
                        name="Emergency back-end registry operators (EBERO)",
                        description="Continuity planning, EBERO testing, failover procedures.",
                        key_concepts=["EBERO", "continuity", "failover", "critical functions"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Registry service evaluations (RSEP)",
                        description="Process for registries to introduce new services.",
                        key_concepts=["RSEP", "new service", "evaluation", "security/stability impact"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="TLD Policies",
                slug="policies",
                description="Registration policies specific to TLD types.",
                topics=[
                    Topic(
                        name="Launch phases",
                        description="Sunrise, landrush, claims, general availability, early access programs.",
                        key_concepts=["sunrise", "landrush", "claims period", "general availability", "EAP"],
                    ),
                    Topic(
                        name="Eligibility requirements",
                        description="Local presence, citizenship, industry membership, validation.",
                        key_concepts=["eligibility", "local presence", "nexus requirements", "validation"],
                    ),
                    Topic(
                        name="ccTLD delegation and redelegation",
                        description="IANA delegation/redelegation of ccTLDs, GAC principles, RFC 1591.",
                        key_concepts=["delegation", "redelegation", "RFC 1591", "GAC principles", "significantly interested parties"],
                        rfcs=["RFC 1591"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="New gTLD objection procedures",
                        description="Four types of objections in new gTLD applications: Legal Rights Objection, Community Objection, Limited Public Interest Objection, and String Confusion Objection. Panel processes and outcomes.",
                        key_concepts=["Legal Rights Objection", "Community Objection", "Limited Public Interest", "String Confusion", "objection panel", "ICDR", "ICC"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="New gTLD Round 2 (Subsequent Procedures)",
                        description="ICANN's next round of new gTLD applications based on the SubPro PDP recommendations. Changes from Round 1: updated applicant guidebook, revised auction mechanisms, enhanced GAC advice processes, geographic name protections, closed generic restrictions, application fees and timeline.",
                        key_concepts=["SubPro", "Round 2", "applicant guidebook v2", "auction mechanisms", "GAC advice", "geographic names", "closed generics", "application timeline"],
                    ),
                    Topic(
                        name="TLD abuse rates and reputation",
                        description="Abuse prevalence across TLDs, DAAR data, TLD reputation impact on deliverability.",
                        key_concepts=["TLD abuse rate", "DAAR", "reputation", "deliverability", "abuse prevalence"],
                    ),
                    Topic(
                        name="TLD retirement and sunsetting",
                        description="Retiring TLDs (.su debates), winding down failed new gTLDs, registrant impact.",
                        key_concepts=["TLD retirement", "sunsetting", ".su", "failed TLD", "registrant notification"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Industry-specific TLD usage",
                        description="TLD adoption patterns by industry — tech (.io, .dev), finance (.bank), health (.health).",
                        key_concepts=["industry TLD", ".io", ".dev", ".bank", ".health", "vertical TLD", "adoption patterns"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 4. REGISTRARS
    # ===================================================================
    Category(
        name="Registrars",
        slug="registrars",
        description="Domain name registrars, accreditation, and the registrar-registry model.",
        subcategories=[
            Subcategory(
                name="Registrar Model",
                slug="model",
                description="How the registrar system works.",
                topics=[
                    Topic(
                        name="Registry-registrar model",
                        description="Separation of registry and registrar functions, competitive registrar market.",
                        key_concepts=["registry", "registrar", "registrant", "reseller", "separation of functions"],
                    ),
                    Topic(
                        name="ICANN accreditation",
                        description="RAA 2013, accreditation process, obligations, compliance.",
                        key_concepts=["RAA 2013", "accreditation", "registrar obligations", "compliance", "data escrow"],
                    ),
                    Topic(
                        name="Registrar responsibilities",
                        description="Customer data handling, WHOIS provision, transfer compliance, abuse handling.",
                        key_concepts=["data handling", "WHOIS accuracy", "transfer policy", "abuse contact", "WDRP"],
                    ),
                    Topic(
                        name="Reseller model",
                        description="Registrar reseller relationships, accountability, branding.",
                        key_concepts=["reseller", "registrar of record", "reseller accountability"],
                    ),
                    Topic(
                        name="Registrar mergers and acquisitions",
                        description="Industry consolidation: GoDaddy acquiring smaller registrars, Tucows acquiring Enom, Squarespace acquiring Google Domains. Implications for domain holders: service migration, policy changes, portfolio continuity.",
                        key_concepts=["registrar M&A", "acquisition", "consolidation", "service migration", "portfolio continuity", "Google Domains to Squarespace"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Thick vs thin registry model",
                        description="Where registration data is stored, thick WHOIS transition.",
                        key_concepts=["thick registry", "thin registry", "thick WHOIS", "data storage", "Verisign transition"],
                    ),
                ],
            ),
            Subcategory(
                name="Registrar Operations",
                slug="operations",
                description="Operational aspects of running a registrar.",
                topics=[
                    Topic(
                        name="Registrar DNS and nameservers",
                        description="Registrar-provided DNS, default nameservers, managed DNS services.",
                        key_concepts=["registrar DNS", "default nameservers", "managed DNS", "parking"],
                    ),
                    Topic(
                        name="Domain locking mechanisms",
                        description="Registrar lock, registry lock, transfer lock, premium DNS lock services.",
                        key_concepts=["registrar lock", "registry lock", "transfer lock", "clientTransferProhibited"],
                    ),
                    Topic(
                        name="ICANN contractual compliance",
                        description="Compliance audits, enforcement actions, breach notices, termination. Includes registrar suspension and revocation processes for portfolio continuity planning.",
                        key_concepts=["compliance", "audit", "breach notice", "enforcement", "ICANN compliance", "accreditation termination", "registrar suspension"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Registrar Selection & Comparison",
                slug="selection",
                description="Evaluating and selecting domain registrars.",
                topics=[
                    Topic(
                        name="Registrar selection criteria",
                        description="Evaluating registrars by security, pricing, DNS features, support, API access, portfolio size.",
                        key_concepts=["selection criteria", "security features", "pricing", "DNS hosting", "API", "support quality"],
                    ),
                    Topic(
                        name="Registrar pricing models",
                        description="Registration vs renewal pricing, transfer pricing, add-on fees, bundled services.",
                        key_concepts=["pricing model", "renewal pricing", "transfer fee", "add-on services", "upselling"],
                    ),
                    Topic(
                        name="White-label and reseller platforms",
                        description="Building a registrar business on top of accredited registrar infrastructure.",
                        key_concepts=["white-label", "reseller platform", "branded registrar", "Enom", "OpenSRS", "LogicBoxes"],
                    ),
                    Topic(
                        name="Corporate vs retail registrars",
                        description="Differences between enterprise-grade and consumer registrars, feature comparison.",
                        key_concepts=["corporate registrar", "retail registrar", "enterprise features", "SLA", "dedicated support"],
                    ),
                ],
            ),
            Subcategory(
                name="Retail Registrars",
                slug="retail_registrars",
                description="Major retail/consumer ICANN-accredited registrars, their product offerings, and market positions.",
                topics=[
                    Topic(
                        name="GoDaddy",
                        description="World's largest registrar by domain volume. Products: domain registration, website builder, hosting, email, SSL. Auction platform, domain brokerage, investor tools. Publicly traded (GDDY).",
                        key_concepts=["GoDaddy", "largest registrar", "aftermarket", "domain auctions", "website builder", "upselling", "GoDaddy Auctions", "bulk tools"],
                    ),
                    Topic(
                        name="Namecheap",
                        description="Value-focused registrar popular with developers and small businesses. Products: domains, shared/VPS hosting, EasyWP, FreeDNS, WhoisGuard privacy, email hosting, VPN (FastVPN). Known for competitive pricing and transparent renewals.",
                        key_concepts=["Namecheap", "WhoisGuard", "FreeDNS", "competitive pricing", "EasyWP", "developer-friendly", "transparent renewal"],
                    ),
                    Topic(
                        name="Tucows / Enom / Hover",
                        description="Tucows ecosystem: Enom (wholesale/reseller backend), Hover (retail brand, simplicity-focused), OpenSRS (reseller platform). One of the largest wholesale registrar operations.",
                        key_concepts=["Tucows", "Enom", "Hover", "OpenSRS", "wholesale registrar", "reseller backend", "EPAG"],
                    ),
                    Topic(
                        name="Porkbun",
                        description="Fast-growing value registrar known for low prices, free WHOIS privacy, free SSL, free email forwarding, and a modern user interface. Developer-friendly API.",
                        key_concepts=["Porkbun", "low-cost registrar", "free WHOIS privacy", "free SSL", "API access", "modern UX"],
                    ),
                    Topic(
                        name="Squarespace Domains (formerly Google Domains)",
                        description="Google Domains acquisition by Squarespace (2023). Simple pricing, free WHOIS privacy, Google Workspace integration. Domain management within the Squarespace ecosystem.",
                        key_concepts=["Squarespace Domains", "Google Domains", "acquisition", "Google Workspace", "simple pricing", "transparent renewal"],
                    ),
                    Topic(
                        name="Gandi",
                        description="French registrar with strong privacy stance ('No Bullshit' philosophy). Products: domains (750+ TLDs), email, SSL, hosting. Known for ethical approach and developer-friendly API. Now part of WHC group.",
                        key_concepts=["Gandi", "No Bullshit", "privacy focus", "French registrar", "ethical registrar", "LiveDNS", "WHC acquisition"],
                    ),
                    Topic(
                        name="IONOS (1&1) and European retail registrars",
                        description="IONOS/1&1 as a major European registrar and hosting provider. OVHcloud domains, Infomaniak, Strato. European market dynamics and regulatory differences.",
                        key_concepts=["IONOS", "1&1", "OVHcloud", "Infomaniak", "European registrar", "Strato", "hosting bundled"],
                    ),
                    Topic(
                        name="Dynadot, Name.com, and mid-tier registrars",
                        description="Mid-tier registrars with loyal followings: Dynadot (investor-friendly, auction marketplace), Name.com (Identity Digital subsidiary), Internet.bs, Epik, Rebel.com.",
                        key_concepts=["Dynadot", "Name.com", "Internet.bs", "Epik", "Rebel.com", "Identity Digital", "mid-tier registrar"],
                    ),
                    Topic(
                        name="Regional and country-specific registrars",
                        description="Registrars serving specific markets: Alibaba Cloud / Wanwang (China), GMO (Japan), Netim (France), Key-Systems (Germany), domain.com.au (Australia). Local compliance and language requirements.",
                        key_concepts=["regional registrar", "Alibaba Cloud", "Wanwang", "GMO", "Key-Systems", "local compliance", "ccTLD requirements"],
                    ),
                ],
            ),
            Subcategory(
                name="Corporate Registrars",
                slug="corporate_registrars",
                description="Enterprise-grade ICANN-accredited registrars specializing in corporate domain portfolio management, brand protection, and high-security services.",
                topics=[
                    Topic(
                        name="Corporate registrar overview",
                        description="What distinguishes corporate registrars from retail: dedicated account management, registry lock, legal support, brand monitoring, consolidated billing, SLAs, custom reporting, enterprise API access.",
                        key_concepts=["corporate registrar", "enterprise DNS", "account management", "registry lock", "SLA", "consolidated billing", "brand protection"],
                    ),
                    Topic(
                        name="MarkMonitor (Clarivate)",
                        description="Industry-leading corporate registrar for Fortune 500 brands. Products: domain management, brand protection monitoring, anti-fraud solutions, SSL management, paid search monitoring. Part of Clarivate Analytics.",
                        key_concepts=["MarkMonitor", "Clarivate", "Fortune 500", "brand protection", "anti-fraud", "domain management platform", "enterprise"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="CSC Digital Brand Services",
                        description="Corporate registrar and brand protection specialist. Products: DBS platform for domain/DNS/SSL management, brand monitoring, domain security (MultiLock, registry lock), DMARC enforcement, online brand protection.",
                        key_concepts=["CSC", "DBS platform", "MultiLock", "DMARC enforcement", "domain security", "brand monitoring", "corporate portfolio"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Com Laude",
                        description="UK-based corporate registrar specializing in premium domain management, registry lock services, brand protection, and DNS hosting for enterprise clients. Comprehensive portfolio management platform.",
                        key_concepts=["Com Laude", "UK registrar", "premium management", "registry lock", "portfolio management", "brand protection", "enterprise DNS"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Safenames",
                        description="Corporate registrar focused on brand protection and domain portfolio management. Products: domain management, watch services, enforcement, SSL, DNS hosting. Part of CentralNic Group.",
                        key_concepts=["Safenames", "CentralNic", "brand protection", "watch services", "enforcement", "portfolio management"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="BRANDIT and BrandShelter",
                        description="European corporate registrars: BRANDIT (Swiss, TMCH-integrated brand protection), BrandShelter (domain and brand management platform, blocking services). Specialized blocking and monitoring products.",
                        key_concepts=["BRANDIT", "BrandShelter", "TMCH integration", "blocking services", "Swiss registrar", "European corporate"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Wholesale and backend registrar infrastructure",
                        description="Registrars providing backend infrastructure: CentralNic (registry + registrar platform), Identity Digital (formerly Donuts/Afilias), Gname, RealTime Register, Ascio (Tucows). White-label and reseller platform architecture.",
                        key_concepts=["CentralNic", "Identity Digital", "Gname", "RealTime Register", "Ascio", "backend registrar", "platform infrastructure", "wholesale"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Corporate registrar security services",
                        description="Enterprise security offerings: registry lock implementation, two-factor domain changes, out-of-band verification, DNSSEC management, domain seizure prevention, domain monitoring and alerting.",
                        key_concepts=["registry lock", "two-factor changes", "out-of-band verification", "DNSSEC management", "seizure prevention", "domain monitoring", "security SLA"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Corporate domain portfolio management",
                        description="Managing large domain portfolios: consolidation strategies, renewal optimization, defensive registration audits, cost rationalization, reporting and analytics, compliance workflows, multi-stakeholder governance.",
                        key_concepts=["portfolio management", "consolidation", "renewal optimization", "defensive audit", "cost rationalization", "compliance workflow", "stakeholder governance"],
                        difficulty_range=("beginner", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 5. ICANN
    # ===================================================================
    Category(
        name="ICANN",
        slug="icann",
        description="The Internet Corporation for Assigned Names and Numbers — governance, policies, and processes.",
        subcategories=[
            Subcategory(
                name="ICANN Structure",
                slug="structure",
                description="Organizational structure and constituencies.",
                topics=[
                    Topic(
                        name="ICANN organizational overview",
                        description="Board, staff, supporting organizations, advisory committees, multistakeholder model.",
                        key_concepts=["ICANN Board", "CEO/staff", "SO", "AC", "multistakeholder", "bottom-up"],
                    ),
                    Topic(
                        name="GNSO (Generic Names Supporting Organization)",
                        description="Policy development for gTLDs, council, stakeholder groups, constituencies. Split between contracted parties (registrars, registries) and non-contracted parties (IPC, NCSG, BC).",
                        key_concepts=["GNSO", "GNSO Council", "registrar stakeholder group", "registry stakeholder group", "IPC", "NCSG", "contracted parties", "non-contracted parties", "house votes", "supermajority"],
                    ),
                    Topic(
                        name="ccNSO (Country Code Names Supporting Organization)",
                        description="ccTLD policy coordination, ccPDP, membership.",
                        key_concepts=["ccNSO", "ccPDP", "ccTLD managers", "delegation/redelegation"],
                    ),
                    Topic(
                        name="GAC (Governmental Advisory Committee)",
                        description="Government advice to ICANN Board, GAC advice, public policy issues.",
                        key_concepts=["GAC", "GAC advice", "public policy", "sovereign interests"],
                    ),
                    Topic(
                        name="ALAC (At-Large Advisory Committee)",
                        description="End user representation, five RALOs (regional At-Large organizations), At-Large community.",
                        key_concepts=["ALAC", "At-Large", "RALO", "end users", "individual interests", "NARALO", "EURALO", "APRALO", "LACRALO", "AFRALO"],
                    ),
                    Topic(
                        name="SSAC and RSSAC",
                        description="Security/Stability and Root Server System advisory committees.",
                        key_concepts=["SSAC", "RSSAC", "security advice", "stability", "root server operations"],
                    ),
                ],
            ),
            Subcategory(
                name="ICANN Policy Processes",
                slug="policy",
                description="How ICANN consensus policies are developed.",
                topics=[
                    Topic(
                        name="Policy Development Process (PDP)",
                        description="GNSO PDP stages, working groups, public comment, Board adoption.",
                        key_concepts=["PDP", "issue report", "working group", "initial report", "final report", "Board adoption"],
                    ),
                    Topic(
                        name="Expedited PDP (EPDP)",
                        description="Faster policy track, EPDP on registration data, Phase 1 and Phase 2.",
                        key_concepts=["EPDP", "expedited", "registration data", "Phase 1", "Phase 2", "SSAD"],
                    ),
                    Topic(
                        name="Consensus policies",
                        description="Binding policies on contracted parties, transfer policy, UDRP, WHOIS.",
                        key_concepts=["consensus policy", "contracted parties", "binding", "transfer policy"],
                    ),
                    Topic(
                        name="Public comment and review mechanisms",
                        description="Public comment periods, independent review, reconsideration, ombudsman.",
                        key_concepts=["public comment", "review", "reconsideration", "ombudsman", "accountability"],
                    ),
                    Topic(
                        name="Cross-community working groups (CCWGs)",
                        description="How ICANN handles cross-constituency issues. CCWG-Accountability designed the IANA transition accountability mechanisms. CCWGs bring together multiple SOs and ACs.",
                        key_concepts=["CCWG", "CCWG-Accountability", "cross-constituency", "IANA transition", "accountability mechanisms"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="ICANN Programs",
                slug="programs",
                description="Major ICANN initiatives and programs.",
                topics=[
                    Topic(
                        name="New gTLD program",
                        description="2012 round, application process, evaluation, objections, subsequent procedures.",
                        key_concepts=["new gTLD", "applicant guidebook", "evaluation", "string contention", "subsequent procedures"],
                    ),
                    Topic(
                        name="ICANN WHOIS/RDAP policy",
                        description="Evolution from WHOIS to RDAP, registration data policies.",
                        key_concepts=["WHOIS", "RDAP", "registration data policy", "gated access"],
                    ),
                    Topic(
                        name="Domain abuse initiatives",
                        description="DNS abuse framework, DAAR, abuse reporting, contract enforcement.",
                        key_concepts=["DNS abuse", "DAAR", "abuse reporting", "framework", "mitigation"],
                    ),
                    Topic(
                        name="IANA stewardship transition",
                        description="Transition from US government oversight, NTIA, PTI, empowered community.",
                        key_concepts=["IANA transition", "NTIA", "PTI", "empowered community", "accountability"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="ICANN Operations & Accountability",
                slug="operations",
                description="ICANN's operational and accountability mechanisms.",
                topics=[
                    Topic(
                        name="ICANN budget and funding model",
                        description="Revenue from registry/registrar fees, budget process, financial transparency.",
                        key_concepts=["ICANN budget", "registry fees", "registrar fees", "financial transparency", "operating plan"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="ICANN accountability mechanisms",
                        description="Independent Review Process (IRP), reconsideration requests, ombudsman, empowered community.",
                        key_concepts=["IRP", "reconsideration", "ombudsman", "empowered community", "accountability"],
                    ),
                    Topic(
                        name="ICANN meetings and participation",
                        description="Three annual meetings, virtual participation, policy sessions, constituency days.",
                        key_concepts=["ICANN meeting", "policy session", "constituency day", "virtual participation", "schedule"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 6. IANA
    # ===================================================================
    Category(
        name="IANA",
        slug="iana",
        description="The Internet Assigned Numbers Authority — root zone, protocol parameters, and special-use names.",
        subcategories=[
            Subcategory(
                name="IANA Functions",
                slug="functions",
                description="Core IANA responsibilities.",
                topics=[
                    Topic(
                        name="IANA overview and role",
                        description="Protocol parameters, number resources, DNS root zone management.",
                        key_concepts=["IANA", "protocol parameters", "number resources", "root zone", "PTI"],
                    ),
                    Topic(
                        name="Root zone management",
                        description="Root zone file, delegation changes, RZMS, Verisign as root zone maintainer.",
                        key_concepts=["root zone", "RZMS", "root zone maintainer", "delegation", "Verisign"],
                    ),
                    Topic(
                        name="TLD delegation process",
                        description="How new TLDs are added to the root zone, technical checks, signing.",
                        key_concepts=["delegation", "technical check", "nameserver validation", "DNSSEC signing"],
                    ),
                    Topic(
                        name="Special-use domain names",
                        description="Reserved names (.localhost, .test, .example, .invalid, .onion), RFC 6761 process.",
                        key_concepts=["special-use", ".localhost", ".test", ".example", ".invalid", ".onion", "RFC 6761"],
                        rfcs=["RFC 6761", "RFC 7686"],
                    ),
                    Topic(
                        name="Protocol parameter registries",
                        description="DNS parameters registry, RR types, opcodes, RCODEs, EDNS option codes. Assignment policies: First Come First Served, IETF Review, Standards Action.",
                        key_concepts=["DNS parameters", "RR type registry", "opcode", "RCODE", "EDNS option code", "assignment policy", "IETF Review", "Standards Action"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Root zone KSK rollover",
                        description="History and process of the 2018 root zone KSK rollover from KSK-2010 to KSK-2017. Why it was delayed (insufficient DNSSEC resolver data). Impact on ISP resolvers. RSSAC023 guidance. Future rollover planning and automation. Significance for DNSSEC trust chain.",
                        key_concepts=["2018 KSK rollover", "KSK-2010", "KSK-2017", "delay reasons", "resolver impact", "RSSAC023", "trust anchor", "key ceremony"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="IANA Governance & History",
                slug="governance",
                description="IANA's institutional history and governance evolution.",
                topics=[
                    Topic(
                        name="IANA transition from US government oversight",
                        description="History of US government role, NTIA contract, 2016 transition, PTI creation.",
                        key_concepts=["IANA transition", "NTIA", "PTI", "ICANN accountability", "stewardship transition"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="PTI (Public Technical Identifiers)",
                        description="PTI as IANA functions operator, relationship to ICANN, SLA, reporting.",
                        key_concepts=["PTI", "IANA functions", "SLA", "performance reporting", "ICANN affiliate"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Root zone KSK ceremonies",
                        description="DNSSEC key signing ceremonies for the root zone, trusted community representatives, HSMs.",
                        key_concepts=["KSK ceremony", "key signing", "HSM", "trusted community representative", "root DNSSEC"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 7. WHOIS & RDAP
    # ===================================================================
    Category(
        name="WHOIS & RDAP",
        slug="whois_rdap",
        description="Domain registration data lookup protocols and policies.",
        subcategories=[
            Subcategory(
                name="WHOIS Protocol",
                slug="whois",
                description="The legacy WHOIS protocol.",
                topics=[
                    Topic(
                        name="WHOIS protocol and history",
                        description="RFC 3912, port 43, text-based protocol, limitations.",
                        key_concepts=["WHOIS", "port 43", "text protocol", "no authentication", "no standardized format"],
                        rfcs=["RFC 3912"],
                    ),
                    Topic(
                        name="Thick vs thin WHOIS",
                        description="Where data is stored, registry vs registrar WHOIS, Verisign thin-to-thick transition.",
                        key_concepts=["thick WHOIS", "thin WHOIS", "registry WHOIS", "registrar WHOIS"],
                    ),
                    Topic(
                        name="WHOIS output parsing",
                        description="Common fields, inconsistent formatting, multi-referral queries.",
                        key_concepts=["parsing", "field mapping", "referral", "inconsistent format", "registrar WHOIS URL"],
                    ),
                ],
            ),
            Subcategory(
                name="RDAP Protocol",
                slug="rdap",
                description="Registration Data Access Protocol — the modern replacement for WHOIS.",
                topics=[
                    Topic(
                        name="RDAP overview and advantages",
                        description="RESTful JSON protocol, standardized output, authentication support, internationalization.",
                        key_concepts=["RDAP", "RESTful", "JSON", "standardized", "authentication", "i18n"],
                        rfcs=["RFC 7480", "RFC 7481", "RFC 9082", "RFC 9083"],
                    ),
                    Topic(
                        name="RDAP query types",
                        description="Domain, nameserver, entity, IP network lookups, search queries.",
                        key_concepts=["domain lookup", "entity lookup", "nameserver lookup", "search", "RDAP URL"],
                        rfcs=["RFC 9082"],
                    ),
                    Topic(
                        name="RDAP response format",
                        description="JSON response structure, objectClassName, links, events, notices, remarks.",
                        key_concepts=["objectClassName", "links", "events", "notices", "remarks", "status"],
                        rfcs=["RFC 9083"],
                    ),
                    Topic(
                        name="RDAP bootstrap and service discovery",
                        description="IANA RDAP bootstrap registries, service URLs, redirect model.",
                        key_concepts=["bootstrap", "service registry", "redirect", "IANA bootstrap"],
                        rfcs=["RFC 9224"],
                    ),
                    Topic(
                        name="RDAP authentication and differentiated access",
                        description="HTTP authentication, role-based access, tiered responses.",
                        key_concepts=["authentication", "differentiated access", "tiered access", "EPDP"],
                        rfcs=["RFC 7481"],
                    ),
                    Topic(
                        name="RDAP profiles and extensions",
                        description="ICANN gTLD RDAP profile mandates specific fields and extensions beyond the base RFC. Federated RDAP, partial search, redacted fields. Critical for building RDAP clients.",
                        key_concepts=["gTLD RDAP profile", "RDAP extensions", "redacted fields", "federated RDAP", "partial search"],
                        rfcs=["RFC 9537"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="WHOIS rate limiting and query restrictions",
                        description="Registries and registrars rate-limit WHOIS queries significantly. Tor/proxy blocking, decline of bulk WHOIS access, practical implications for domain research.",
                        key_concepts=["WHOIS rate limiting", "query restrictions", "Tor blocking", "bulk WHOIS decline", "abuse prevention"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Registration Data Policy",
                slug="data_policy",
                description="Policies governing access to registration data.",
                topics=[
                    Topic(
                        name="GDPR impact on WHOIS/RDAP",
                        description="Data redaction, legitimate interest, temporary specification, compliance challenges.",
                        key_concepts=["GDPR", "redaction", "legitimate interest", "temporary specification", "data minimization"],
                    ),
                    Topic(
                        name="EPDP on registration data",
                        description="Phase 1 outcomes, Phase 2/SSAD, data elements, purposes, retention.",
                        key_concepts=["EPDP", "Phase 1", "Phase 2", "SSAD", "data elements", "retention"],
                    ),
                    Topic(
                        name="WHOIS accuracy requirements",
                        description="RAA accuracy obligations, WDRP, validation/verification, inaccuracy complaints.",
                        key_concepts=["accuracy", "WDRP", "validation", "verification", "inaccuracy complaint"],
                    ),
                    Topic(
                        name="SSAD (System for Standardized Access/Disclosure)",
                        description="Phase 2 EPDP output creating a gated access system for non-public registration data. Standardized request/response process for legitimate access to redacted WHOIS/RDAP data.",
                        key_concepts=["SSAD", "gated access", "EPDP Phase 2", "standardized disclosure", "non-public data", "accreditation"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 8. DOMAIN BLOCKING & PROTECTION
    # ===================================================================
    Category(
        name="Domain Blocking & Protection",
        slug="blocking",
        description="Mechanisms for protecting trademarks and blocking domain registrations.",
        subcategories=[
            Subcategory(
                name="Trademark Clearinghouse (TMCH)",
                slug="tmch",
                description="The ICANN Trademark Clearinghouse and rights protection mechanisms.",
                topics=[
                    Topic(
                        name="TMCH overview",
                        description="Purpose, operation, trademark record submission, validation.",
                        key_concepts=["TMCH", "trademark record", "SMD file", "validation", "Deloitte", "IBM"],
                    ),
                    Topic(
                        name="Sunrise periods",
                        description="Pre-launch registration for trademark holders, sunrise dispute resolution.",
                        key_concepts=["sunrise", "SMD", "sunrise registration", "SDRP", "sunrise dispute"],
                    ),
                    Topic(
                        name="Claims periods",
                        description="Post-launch notification, trademark claims notice, acknowledgment.",
                        key_concepts=["claims", "claims notice", "trademark claims", "NRPM", "90-day claims"],
                    ),
                ],
            ),
            Subcategory(
                name="Domain Blocking Services",
                slug="blocking_services",
                description="Commercial and registry-level domain blocking mechanisms for brand protection.",
                topics=[
                    Topic(
                        name="Domain blocking overview",
                        description="What domain blocking is, how it differs from defensive registration, the registry-level blocking model. Blocking prevents third-party registration without requiring the brand owner to register the domain. History and evolution of blocking services in the new gTLD program.",
                        key_concepts=["domain blocking", "blocking vs registration", "registry-level block", "preventive protection", "new gTLD RPMs", "cost efficiency"],
                    ),
                    Topic(
                        name="DPML (Domains Protected Marks List)",
                        description="Identity Digital's (formerly Donuts) blocking service across their new gTLD portfolio (~240 TLDs). DPML blocks exact-match registrations. DPML+ (Block+) blocks exact match plus common variations. Coverage scope, override process, pricing structure, TMCH integration, renewal requirements.",
                        key_concepts=["DPML", "DPML+", "Block+", "Identity Digital", "Donuts", "exact match block", "variation blocking", "override", "240+ TLDs", "annual renewal"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="AdultBlock",
                        description="ICM Registry's multi-TLD blocking service covering .xxx, .porn, .sex, and .adult. Designed to prevent brand names from appearing in adult-content TLDs. Trademark validation requirements, TMCH SMD file usage, sunrise block vs ongoing block, pricing tiers, coverage scope and limitations.",
                        key_concepts=["AdultBlock", ".xxx", ".porn", ".sex", ".adult", "ICM Registry", "adult content TLDs", "trademark validation", "SMD file", "brand reputation"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="GlobalBlock (Consolidated Blocking Service)",
                        description="Cross-registry domain blocking service providing protection across multiple registry operators through a single subscription. How GlobalBlock differs from DPML (multi-registry vs single-registry). GoDaddy Registry, Radix, and other participating registries. Coverage analysis, gap assessment, ICANN policy context around consolidated RPMs.",
                        key_concepts=["GlobalBlock", "consolidated blocking", "cross-registry", "multi-registry block", "GoDaddy Registry", "coverage scope", "ICANN RPMs", "single subscription"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Registry-specific blocking products",
                        description="Individual registry operator blocking offerings beyond DPML and GlobalBlock: Radix Block, CentralNic blocking, Afilias/Identity Digital blocks, Minds + Machines blocks, UniRegistry blocks. How each registry's blocking product works, TLD coverage, pricing differences, and overlap between services.",
                        key_concepts=["Radix Block", "CentralNic block", "registry blocking", "TLD-specific block", "coverage overlap", "provider comparison", "blocking portfolio"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Blocking vs defensive registration cost-benefit analysis",
                        description="Decision framework: when to block, when to defensively register, when to monitor and enforce. Cost comparison across strategies (blocking fees vs registration + renewal costs vs UDRP/URS costs). Risk assessment matrices, coverage gaps in blocking services, portfolio optimization strategies.",
                        key_concepts=["cost-benefit analysis", "blocking vs registration", "monitoring vs enforcement", "risk matrix", "portfolio optimization", "coverage gaps", "total cost of protection"],
                    ),
                    Topic(
                        name="Blocking service coverage and gap analysis",
                        description="Assessing which TLDs are covered by which blocking service, identifying gaps. No single blocking service covers all TLDs. Combining DPML + GlobalBlock + AdultBlock + defensive registrations for comprehensive coverage. Tools and methods for auditing blocking coverage across a brand portfolio.",
                        key_concepts=["coverage gap analysis", "TLD mapping", "combined blocking strategy", "DPML coverage", "GlobalBlock coverage", "uncovered TLDs", "audit methodology"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="TMCH integration with blocking services",
                        description="How the Trademark Clearinghouse interacts with blocking services. SMD file requirements for blocks, TMCH mark validation as a prerequisite for blocking eligibility, maintaining active TMCH records for block renewals. Relationship between sunrise registrations, claims notices, and blocking.",
                        key_concepts=["TMCH", "SMD file", "mark validation", "blocking eligibility", "sunrise interaction", "claims interaction", "TMCH renewal", "Deloitte validation"],
                    ),
                    Topic(
                        name="Registry lock services",
                        description="Server-side lock requiring manual, out-of-band verification (phone call/fax/in-person) for any domain changes. Registry lock sets serverTransferProhibited, serverUpdateProhibited, and serverDeleteProhibited statuses. The process for activating and deactivating locks, operational procedures, which registries support it, corporate registrar lock implementations (CSC MultiLock, MarkMonitor registry lock).",
                        key_concepts=["registry lock", "serverDeleteProhibited", "serverTransferProhibited", "serverUpdateProhibited", "out-of-band verification", "phone/fax verification", "CSC MultiLock", "manual unlock", "high-value domain protection"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="EPP Status Codes",
                slug="epp_status",
                description="Domain status codes and their protective effects.",
                topics=[
                    Topic(
                        name="Client-side EPP status codes",
                        description="Registrar-set statuses: clientHold, clientTransferProhibited, etc.",
                        key_concepts=["clientHold", "clientTransferProhibited", "clientDeleteProhibited", "clientUpdateProhibited", "clientRenewProhibited"],
                    ),
                    Topic(
                        name="Server-side EPP status codes",
                        description="Registry-set statuses: serverHold, serverTransferProhibited, etc.",
                        key_concepts=["serverHold", "serverTransferProhibited", "serverDeleteProhibited", "serverUpdateProhibited"],
                    ),
                    Topic(
                        name="Pending and informational statuses",
                        description="pendingCreate, pendingDelete, pendingTransfer, pendingUpdate, redemptionPeriod.",
                        key_concepts=["pendingCreate", "pendingDelete", "pendingTransfer", "pendingUpdate", "redemptionPeriod", "addPeriod"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 9. WIPO & DOMAIN DISPUTES
    # ===================================================================
    Category(
        name="WIPO & Domain Disputes",
        slug="disputes",
        description="Domain name dispute resolution — UDRP, URS, ccTLD DRPs, and court proceedings.",
        subcategories=[
            Subcategory(
                name="UDRP",
                slug="udrp",
                description="Uniform Domain-Name Dispute-Resolution Policy.",
                topics=[
                    Topic(
                        name="UDRP overview and process",
                        description="Filing, response, panel appointment, decision, implementation timeline.",
                        key_concepts=["UDRP", "complaint", "response", "panel", "decision", "10-day implementation"],
                    ),
                    Topic(
                        name="UDRP three elements",
                        description="Identical/confusingly similar, no rights/legitimate interests, bad faith registration and use.",
                        key_concepts=["confusingly similar", "rights or legitimate interests", "bad faith", "three elements"],
                    ),
                    Topic(
                        name="Confusing similarity analysis",
                        description="Trademark comparison, TLD disregard, typosquatting, prefix/suffix additions.",
                        key_concepts=["confusing similarity", "standing test", "TLD disregarded", "typosquatting", "prefix/suffix"],
                    ),
                    Topic(
                        name="Rights and legitimate interests",
                        description="Bona fide offering, fair use, legitimate noncommercial use, prima facie case.",
                        key_concepts=["bona fide offering", "fair use", "fan sites", "criticism", "prima facie case"],
                    ),
                    Topic(
                        name="Bad faith registration and use",
                        description="Pattern of conduct, disruption, attraction for commercial gain, passive holding.",
                        key_concepts=["bad faith indicators", "pattern of conduct", "passive holding", "Telstra test", "disruption"],
                    ),
                    Topic(
                        name="UDRP remedies and limitations",
                        description="Transfer, cancellation, no damages, court challenge, RDNH.",
                        key_concepts=["transfer", "cancellation", "no damages", "court action", "reverse domain name hijacking"],
                    ),
                    Topic(
                        name="WIPO Overview of Panel Views (WIPO Overview 3.0)",
                        description="Consensus views on key UDRP issues, jurisprudential guidance.",
                        key_concepts=["WIPO Overview 3.0", "consensus view", "panel views", "UDRP jurisprudence"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="UDRP providers",
                        description="WIPO, NAF, ADNDRC, CAC — approved providers and their roles.",
                        key_concepts=["WIPO Arbitration Center", "NAF", "ADNDRC", "CAC", "provider rules"],
                    ),
                    Topic(
                        name="UDRP panels and panelist selection",
                        description="Panel composition: single vs three-member panels, how panelists are appointed, panelist selection strategy, panelist bias concerns and statistics.",
                        key_concepts=["single panelist", "three-member panel", "panelist appointment", "panelist selection", "panelist bias", "respondent selection"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="UDRP jurisprudence on new gTLDs",
                        description="Application of existing UDRP precedents to new gTLDs. Generic term disputes (.app, .shop), whether the TLD itself adds meaning, geographic terms in new gTLDs.",
                        key_concepts=["new gTLD UDRP", "generic term disputes", "TLD meaning", "geographic TLD disputes", "precedent applicability"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="URS",
                slug="urs",
                description="Uniform Rapid Suspension system for new gTLDs.",
                topics=[
                    Topic(
                        name="URS overview and process",
                        description="Faster, lower-cost alternative to UDRP for clear-cut cases in new gTLDs.",
                        key_concepts=["URS", "rapid suspension", "clear and convincing", "new gTLDs", "MFSD"],
                    ),
                    Topic(
                        name="URS vs UDRP comparison",
                        description="Scope, burden of proof, remedies, cost, timelines, applicability.",
                        key_concepts=["URS vs UDRP", "preponderance vs clear/convincing", "suspension vs transfer", "scope"],
                    ),
                ],
            ),
            Subcategory(
                name="Other Dispute Mechanisms",
                slug="other_disputes",
                description="Alternative and supplementary dispute resolution mechanisms.",
                topics=[
                    Topic(
                        name="ccTLD dispute resolution policies",
                        description="DRS (.uk), CDRP (.ca), .au DRP — local variations on UDRP principles.",
                        key_concepts=["DRS", "Nominet DRS", "CDRP", ".au DRP", "local DRP"],
                    ),
                    Topic(
                        name="ACPA (Anticybersquatting Consumer Protection Act)",
                        description="US federal law, in rem actions, statutory damages, differences from UDRP.",
                        key_concepts=["ACPA", "15 USC 1125(d)", "in rem", "statutory damages", "bad faith intent"],
                    ),
                    Topic(
                        name="Court proceedings and UDRP",
                        description="Relationship between UDRP and courts, challenging UDRP decisions, mutual jurisdiction.",
                        key_concepts=["court challenge", "mutual jurisdiction", "de novo review", "10-day window"],
                    ),
                    Topic(
                        name="Reverse domain name hijacking (RDNH)",
                        description="Abuse of UDRP process, panel findings, consequences.",
                        key_concepts=["RDNH", "abuse of process", "panel finding", "bad faith complaint"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Notable UDRP case categories",
                        description="Landmark cases: generic terms, free speech/criticism, fan sites, geographic terms, personal names.",
                        key_concepts=["generic terms", "criticism sites", "fan sites", "geographic names", "personal names", "landmark cases"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Enforcement cost-benefit analysis",
                        description="Comparing costs of UDRP, URS, court action, negotiation — choosing the right remedy.",
                        key_concepts=["cost analysis", "UDRP cost", "URS cost", "court costs", "negotiation", "remedy selection"],
                    ),
                    Topic(
                        name="Trademark dilution and domain names",
                        description="Dilution claims (blurring/tarnishment) in domain disputes, relationship to UDRP.",
                        key_concepts=["dilution", "blurring", "tarnishment", "famous marks", "TDRA"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="TDRP (Transfer Dispute Resolution Policy)",
                        description="ICANN policy for disputing improper domain transfers. Available when a domain has been transferred without proper authorization. Distinct from UDRP which addresses trademark disputes.",
                        key_concepts=["TDRP", "transfer dispute", "improper transfer", "unauthorized transfer", "ICANN policy"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="PDDRP (Post-Delegation Dispute Resolution)",
                        description="Procedure for challenging registry operators' conduct after TLD delegation. Available to trademark holders and others who believe a registry operator is causing harm through its practices.",
                        key_concepts=["PDDRP", "post-delegation", "registry operator conduct", "trademark harm", "registry challenge"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="ccTLD dispute resolution variation",
                        description="Significant variation in ccTLD dispute mechanisms: some use UDRP equivalents, others have no formal dispute mechanism, some rely entirely on national court jurisdiction.",
                        key_concepts=["ccTLD DRP variation", "no dispute mechanism", "national courts", "UDRP equivalent", "jurisdictional differences"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 10. SSL/TLS & CERTIFICATES
    # ===================================================================
    Category(
        name="SSL/TLS & Certificates",
        slug="ssl",
        description="Digital certificates, certificate authorities, and TLS in relation to domain names.",
        subcategories=[
            Subcategory(
                name="Certificate Types",
                slug="cert_types",
                description="Validation levels and certificate categories.",
                topics=[
                    Topic(
                        name="Domain Validation (DV) certificates",
                        description="Automated domain control validation, Let's Encrypt, low assurance.",
                        key_concepts=["DV", "domain validation", "automated", "low assurance", "Let's Encrypt"],
                    ),
                    Topic(
                        name="Organization Validation (OV) certificates",
                        description="Organization identity verification, vetting process, use cases.",
                        key_concepts=["OV", "organization validation", "identity vetting", "business verification"],
                    ),
                    Topic(
                        name="Extended Validation (EV) certificates",
                        description="Highest assurance level, strict vetting, browser treatment changes.",
                        key_concepts=["EV", "extended validation", "green bar (deprecated)", "strict vetting", "legal entity"],
                    ),
                    Topic(
                        name="Wildcard certificates",
                        description="Single certificate for all subdomains, limitations, security considerations.",
                        key_concepts=["wildcard", "*.domain", "single-level", "security implications"],
                    ),
                    Topic(
                        name="SAN (Subject Alternative Name) certificates",
                        description="Multi-domain certificates, UCC, SAN field usage.",
                        key_concepts=["SAN", "Subject Alternative Name", "multi-domain", "UCC"],
                    ),
                ],
            ),
            Subcategory(
                name="Certificate Authorities",
                slug="cas",
                description="The CA ecosystem and trust model.",
                topics=[
                    Topic(
                        name="CA trust model",
                        description="Root CAs, intermediate CAs, chain of trust, browser root programs.",
                        key_concepts=["root CA", "intermediate CA", "chain of trust", "root program", "cross-signing"],
                    ),
                    Topic(
                        name="CA/Browser Forum",
                        description="Baseline requirements, ballots, membership, EV guidelines.",
                        key_concepts=["CA/B Forum", "Baseline Requirements", "ballot", "EV Guidelines"],
                    ),
                    Topic(
                        name="Let's Encrypt and ACME",
                        description="Free automated certificates, ACME protocol, challenge types (HTTP-01, DNS-01).",
                        key_concepts=["Let's Encrypt", "ACME", "HTTP-01", "DNS-01", "automated issuance", "certbot"],
                        rfcs=["RFC 8555"],
                    ),
                    Topic(
                        name="Certificate Transparency (CT)",
                        description="Public audit logs, SCTs, monitoring, Merkle trees.",
                        key_concepts=["CT", "certificate transparency", "SCT", "CT log", "Merkle tree", "monitoring"],
                        rfcs=["RFC 9162"],
                    ),
                ],
            ),
            Subcategory(
                name="Certificate Lifecycle",
                slug="cert_lifecycle",
                description="Issuance, management, and revocation of certificates.",
                topics=[
                    Topic(
                        name="Certificate issuance process",
                        description="CSR generation, domain validation methods, issuance, installation.",
                        key_concepts=["CSR", "private key", "validation", "issuance", "installation", "chain"],
                    ),
                    Topic(
                        name="Certificate renewal and automation",
                        description="Renewal process, ACME automation, certificate lifetime trends (90-day, 47-day). CA/B Forum ballot SC-081 and the industry debate on maximum lifetimes.",
                        key_concepts=["renewal", "automation", "ACME", "short-lived certificates", "47-day proposal", "SC-081", "lifetime reduction"],
                    ),
                    Topic(
                        name="Certificate revocation",
                        description="CRL, OCSP, OCSP stapling, reasons for revocation, key compromise.",
                        key_concepts=["revocation", "CRL", "OCSP", "OCSP stapling", "key compromise"],
                        rfcs=["RFC 5280", "RFC 6960"],
                    ),
                    Topic(
                        name="CAA DNS records for certificate control",
                        description="Using CAA records to restrict which CAs can issue, mandatory checking.",
                        key_concepts=["CAA", "issue", "issuewild", "iodef", "mandatory CA checking"],
                        rfcs=["RFC 8659"],
                    ),
                    Topic(
                        name="Certificate monitoring and alerting",
                        description="Monitoring CT logs for unauthorized certificates, expiry alerting, inventory management.",
                        key_concepts=["CT monitoring", "certificate inventory", "expiry alerting", "unauthorized issuance", "crt.sh"],
                    ),
                    Topic(
                        name="TLS version history and domain implications",
                        description="SSL 3.0 through TLS 1.3, deprecation timeline, impact on domain configurations.",
                        key_concepts=["TLS 1.0", "TLS 1.1", "TLS 1.2", "TLS 1.3", "deprecation", "backward compatibility"],
                    ),
                    Topic(
                        name="PKI ecosystem beyond web certificates",
                        description="S/MIME, code signing, client certificates, IoT certificates — PKI breadth as it relates to domains.",
                        key_concepts=["S/MIME", "code signing", "client certificate", "IoT PKI", "private PKI"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DANE for HTTPS",
                        description="Using DNSSEC-validated TLSA records for web server certificate authentication. Provides an alternative trust path independent of the traditional CA model.",
                        key_concepts=["DANE HTTPS", "TLSA", "certificate association", "CA-independent trust", "DNSSEC dependency"],
                        rfcs=["RFC 7671", "RFC 6698"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Post-quantum cryptography and TLS",
                        description="Industry transition to post-quantum algorithms. NIST selections (FIPS 203 ML-KEM, FIPS 204 ML-DSA) appearing in certificate profiles. Impact on TLS handshake sizes and performance.",
                        key_concepts=["post-quantum TLS", "ML-KEM", "ML-DSA", "FIPS 203", "FIPS 204", "quantum-safe certificates", "hybrid key exchange"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 11. BRAND PROTECTION
    # ===================================================================
    Category(
        name="Brand Protection",
        slug="brand_protection",
        description="Strategies and tools for protecting brand identity in the domain name space.",
        subcategories=[
            Subcategory(
                name="Threat Landscape",
                slug="threats",
                description="Types of brand abuse in domain names.",
                topics=[
                    Topic(
                        name="Typosquatting",
                        description="Registration of misspelled brand domains, keyboard adjacency, missing letters.",
                        key_concepts=["typosquatting", "keyboard adjacency", "missing letter", "doubled letter", "transposition"],
                    ),
                    Topic(
                        name="Homoglyph and IDN attacks",
                        description="Visual lookalike characters, Punycode abuse, script confusion.",
                        key_concepts=["homoglyph", "IDN homograph", "Punycode", "script mixing", "visual similarity"],
                    ),
                    Topic(
                        name="Combosquatting",
                        description="Combining brand names with common words (brand-login.com, brand-support.com).",
                        key_concepts=["combosquatting", "brand + keyword", "deceptive domains"],
                    ),
                    Topic(
                        name="TLD squatting",
                        description="Registering brand names across many TLDs, defensive registration limits.",
                        key_concepts=["TLD squatting", "defensive registration", "cross-TLD protection"],
                    ),
                    Topic(
                        name="Domain tasting and front-running",
                        description="Exploiting AGP for testing, allegations of query-based front-running.",
                        key_concepts=["domain tasting", "AGP abuse", "front-running", "ICANN AGP limits"],
                    ),
                    Topic(
                        name="Bitsquatting",
                        description="Attack where single-bit memory errors in client hardware lead users to unintended domains. Documented attack category targeting high-traffic domains.",
                        key_concepts=["bitsquatting", "bit-flip", "memory error", "hardware fault", "high-traffic targets"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Subdomain takeover as brand threat",
                        description="Dangling CNAME records pointing to unclaimed cloud services create subdomain takeover opportunities that directly impact brand reputation and trust.",
                        key_concepts=["subdomain takeover", "dangling CNAME", "brand reputation", "cloud service takeover", "trust abuse"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="AI-generated lookalike domains",
                        description="Rapidly growing attack vector using AI/LLMs to generate convincing phishing domains at scale. Goes beyond traditional DGA by creating human-plausible brand impersonations.",
                        key_concepts=["AI domain generation", "LLM phishing", "automated impersonation", "scalable attacks", "AI brand abuse"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Protection Strategies",
                slug="strategies",
                description="Approaches to brand protection in the domain space.",
                topics=[
                    Topic(
                        name="Defensive registration strategies",
                        description="Core TLDs, risk-based registration, cost-benefit analysis.",
                        key_concepts=["defensive registration", "core TLDs", "risk matrix", "cost-benefit"],
                    ),
                    Topic(
                        name="Domain monitoring and watch services",
                        description="New registration monitoring, zone file access, CT log monitoring.",
                        key_concepts=["monitoring", "watch service", "CZDS", "zone file access", "CT monitoring"],
                    ),
                    Topic(
                        name="Enforcement workflows",
                        description="Cease and desist, UDRP, URS, registrar abuse reporting, takedown.",
                        key_concepts=["C&D", "UDRP filing", "URS filing", "abuse report", "takedown"],
                    ),
                    Topic(
                        name="Portfolio management",
                        description="Domain portfolio optimization, consolidation, renewal decisions, registrar diversity.",
                        key_concepts=["portfolio management", "consolidation", "renewal strategy", "registrar selection"],
                    ),
                    Topic(
                        name="Social media and domain coordination",
                        description="Aligning domain names with social media handles, cross-platform brand consistency.",
                        key_concepts=["social media handles", "username squatting", "cross-platform", "brand consistency", "name matching"],
                    ),
                    Topic(
                        name="Brand TLD strategies",
                        description="Leveraging .brand TLDs for corporate identity, internal use, customer-facing domains.",
                        key_concepts=[".brand strategy", "corporate TLD", "internal domains", "customer-facing", "spec 13"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Takedown services and providers",
                        description="Professional takedown services, response times, registrar relationships, success rates.",
                        key_concepts=["takedown service", "abuse takedown", "response time", "success rate", "provider network"],
                    ),
                    Topic(
                        name="Industry-specific brand protection",
                        description="Brand protection strategies tailored to pharma, finance, luxury, and tech sectors. Regulated industries have specific requirements (FDA/FCA domain compliance).",
                        key_concepts=["pharma", "finance", "luxury brands", "tech", "industry-specific", "regulatory overlay", "regulated industry requirements", "FDA/FCA domain compliance"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 12. DNS ABUSE
    # ===================================================================
    Category(
        name="DNS Abuse",
        slug="dns_abuse",
        description="Abuse of the domain name system — types, detection, and mitigation.",
        subcategories=[
            Subcategory(
                name="Abuse Types",
                slug="types",
                description="Categories of DNS abuse.",
                topics=[
                    Topic(
                        name="Phishing domains",
                        description="Deceptive domains used for credential harvesting, brand impersonation.",
                        key_concepts=["phishing", "credential harvesting", "brand impersonation", "deceptive similarity"],
                    ),
                    Topic(
                        name="Malware distribution via DNS",
                        description="Domains hosting malware, drive-by downloads, exploit kits.",
                        key_concepts=["malware", "drive-by download", "exploit kit", "payload hosting"],
                    ),
                    Topic(
                        name="Botnet command and control",
                        description="C2 domains, DGA-generated domains, fast-flux networks.",
                        key_concepts=["C2", "botnet", "DGA", "fast-flux", "command and control"],
                    ),
                    Topic(
                        name="Spam and unsolicited communications",
                        description="Domains used for spam campaigns, snowshoe spam.",
                        key_concepts=["spam domains", "snowshoe spam", "bulk registration"],
                    ),
                    Topic(
                        name="DNS-based DDoS",
                        description="DNS amplification, water torture attacks, NXDOMAIN floods.",
                        key_concepts=["DNS amplification", "water torture", "NXDOMAIN flood", "random subdomain attack"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Fast flux networks",
                        description="Evasion technique using rapidly changing DNS records to hide malicious infrastructure. Single-flux (rotating A records) and double-flux (rotating both A and NS records). Distinct detection characteristics.",
                        key_concepts=["fast flux", "single-flux", "double-flux", "rapid DNS changes", "flux detection", "bulletproof hosting"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Detection and Mitigation",
                slug="mitigation",
                description="Tools and processes for combating DNS abuse.",
                topics=[
                    Topic(
                        name="Domain reputation and blocklists",
                        description="Reputation scoring, Spamhaus, SURBL, Google Safe Browsing.",
                        key_concepts=["reputation", "blocklist", "Spamhaus", "SURBL", "Safe Browsing"],
                    ),
                    Topic(
                        name="Abuse reporting and handling",
                        description="Registrar abuse contacts, abuse complaint handling, ICANN obligations.",
                        key_concepts=["abuse contact", "abuse complaint", "registrar obligations", "response time"],
                    ),
                    Topic(
                        name="RPZ (Response Policy Zones)",
                        description="DNS firewall, policy-based filtering, threat intelligence feeds.",
                        key_concepts=["RPZ", "DNS firewall", "policy zone", "NXDOMAIN override", "threat feed"],
                    ),
                    Topic(
                        name="ICANN DAAR (Domain Abuse Activity Reporting)",
                        description="ICANN's abuse measurement system, methodology, reporting.",
                        key_concepts=["DAAR", "abuse rates", "ICANN measurement", "security threat information"],
                    ),
                    Topic(
                        name="Registrar and registry abuse mitigation",
                        description="Suspension, hold, takedown, anti-abuse policies, verified registration.",
                        key_concepts=["suspension", "serverHold", "takedown", "anti-abuse policy"],
                    ),
                    Topic(
                        name="Newly registered domain (NRD) indicators",
                        description="Using domain age as abuse signal, NRD blocklists, registration velocity monitoring.",
                        key_concepts=["NRD", "domain age", "registration velocity", "NRD blocklist", "early abuse detection"],
                    ),
                    Topic(
                        name="Domain generation algorithms (DGAs) deep dive",
                        description="How DGAs work, types (deterministic, seed-based), detection via NXDomain analysis, ML approaches.",
                        key_concepts=["DGA", "algorithmic generation", "seed-based", "NXDomain analysis", "ML detection", "dictionary DGA"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Protective DNS services for abuse mitigation",
                        description="Using resolver-level filtering (Quad9, CISA Protective DNS) to block known-bad domains.",
                        key_concepts=["protective DNS", "Quad9", "CISA", "resolver filtering", "threat feed integration"],
                    ),
                    Topic(
                        name="DNSSEC amplification as a DDoS vector",
                        description="Large DNSSEC-signed responses are particularly effective DDoS amplifiers due to RRSIG, DNSKEY, and DS records increasing response size. Intersection of DNSSEC deployment and amplification risk.",
                        key_concepts=["DNSSEC amplification", "large responses", "RRSIG size", "DNSKEY amplification", "response size ratio"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 13. EMAIL & DOMAINS
    # ===================================================================
    Category(
        name="Email Authentication & Domains",
        slug="email",
        description="Email authentication technologies that rely on DNS and domain names.",
        subcategories=[
            Subcategory(
                name="Email Authentication",
                slug="authentication",
                description="SPF, DKIM, DMARC, and related technologies.",
                topics=[
                    Topic(
                        name="SPF (Sender Policy Framework)",
                        description="Authorized sender IP specification, mechanisms, qualifiers, 10-lookup limit.",
                        key_concepts=["SPF", "TXT record", "mechanisms", "include", "ip4", "ip6", "all", "10-lookup limit"],
                        rfcs=["RFC 7208"],
                    ),
                    Topic(
                        name="DKIM (DomainKeys Identified Mail)",
                        description="Cryptographic email signing, selector, public key in DNS, signature verification.",
                        key_concepts=["DKIM", "selector", "public key", "d= tag", "s= tag", "signature", "body hash"],
                        rfcs=["RFC 6376"],
                    ),
                    Topic(
                        name="DMARC (Domain-based Message Authentication)",
                        description="SPF/DKIM alignment, policy (none/quarantine/reject), aggregate and forensic reports.",
                        key_concepts=["DMARC", "alignment", "policy", "p=none", "p=quarantine", "p=reject", "rua", "ruf"],
                        rfcs=["RFC 7489"],
                    ),
                    Topic(
                        name="DMARC aggregate reporting (RUA)",
                        description="XML report format for DMARC aggregate reports. How to parse reports, what they tell about email stream health, report processors, and volume analysis.",
                        key_concepts=["DMARC-RUA", "aggregate report", "XML format", "report parsing", "email stream health", "report processors"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="BIMI (Brand Indicators for Message Identification)",
                        description="Brand logo display in email clients, VMC certificates, DNS TXT record. Logo must be SVG Tiny 1.2 format.",
                        key_concepts=["BIMI", "VMC", "brand logo", "default._bimi", "verified mark certificate", "SVG Tiny 1.2"],
                    ),
                    Topic(
                        name="ARC (Authenticated Received Chain)",
                        description="Preserving authentication through indirect mail flows, particularly mailing list forwarding.",
                        key_concepts=["ARC", "ARC-Seal", "ARC-Message-Signature", "ARC-Authentication-Results", "mailing list forwarding"],
                        rfcs=["RFC 8617"],
                    ),
                    Topic(
                        name="MTA-STS (Mail Transfer Agent Strict Transport Security)",
                        description="Enforcing TLS for email transport, policy via HTTPS, DNS TXT record.",
                        key_concepts=["MTA-STS", "SMTP TLS", "_mta-sts", "policy file", "enforce mode"],
                        rfcs=["RFC 8461"],
                    ),
                    Topic(
                        name="SMTP STARTTLS and opportunistic TLS",
                        description="Baseline SMTP TLS behavior: STARTTLS is opportunistic and downgrade-susceptible. Distinction from MTA-STS enforced TLS. Foundational email-DNS knowledge.",
                        key_concepts=["STARTTLS", "opportunistic TLS", "downgrade attack", "SMTP encryption", "implicit TLS", "port 465 vs 587"],
                    ),
                    Topic(
                        name="DANE for email (TLSA)",
                        description="Using DNSSEC-validated TLSA records for SMTP TLS verification.",
                        key_concepts=["DANE", "TLSA", "SMTP DANE", "certificate pinning via DNS"],
                        rfcs=["RFC 7672"],
                    ),
                    Topic(
                        name="Google/Yahoo bulk sender requirements (2024+)",
                        description="New requirements for bulk email senders (5,000+ messages/day to Gmail/Yahoo): mandatory SPF and DKIM authentication, DMARC policy (at minimum p=none), one-click unsubscribe via List-Unsubscribe header, spam rate threshold below 0.3%. Impact on domain DNS configuration and email deliverability.",
                        key_concepts=["bulk sender requirements", "5000 messages/day", "p=none minimum", "one-click unsubscribe", "List-Unsubscribe", "spam rate threshold", "0.3% complaint rate", "Gmail requirements", "Yahoo requirements"],
                    ),
                ],
            ),
            Subcategory(
                name="Email Routing",
                slug="routing",
                description="DNS records for email delivery.",
                topics=[
                    Topic(
                        name="MX record configuration",
                        description="Mail exchange records, priority, multiple MX, null MX.",
                        key_concepts=["MX", "priority", "fallback", "null MX", "implicit MX"],
                        rfcs=["RFC 5321", "RFC 7505"],
                    ),
                    Topic(
                        name="Email-related DNS troubleshooting",
                        description="Common misconfigurations, SPF too many lookups, missing rDNS, DKIM key issues.",
                        key_concepts=["troubleshooting", "permerror", "temperror", "missing rDNS", "key rotation"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Email provider DNS configuration",
                        description="DNS setup for Google Workspace, Microsoft 365, Fastmail — provider-specific MX, SPF, DKIM records.",
                        key_concepts=["Google Workspace", "Microsoft 365", "Fastmail", "provider MX", "provider SPF"],
                    ),
                    Topic(
                        name="Email deliverability and DNS",
                        description="How DNS configuration impacts email deliverability, IP reputation, domain reputation.",
                        key_concepts=["deliverability", "IP reputation", "domain reputation", "warmup", "blocklist impact"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 14. DOMAIN VALUATION & AFTERMARKET
    # ===================================================================
    Category(
        name="Domain Valuation & Aftermarket",
        slug="aftermarket",
        description="Domain name valuation, trading, and the secondary market.",
        subcategories=[
            Subcategory(
                name="Valuation",
                slug="valuation",
                description="Factors that determine domain name value.",
                topics=[
                    Topic(
                        name="Domain valuation factors",
                        description="Length, keywords, TLD, brandability, search volume, comparable sales.",
                        key_concepts=["length", "keywords", "brandability", "TLD premium", "comparable sales", "search volume"],
                    ),
                    Topic(
                        name="Premium and reserved names",
                        description="Registry premium names, keyword premiums, tiered renewal pricing.",
                        key_concepts=["registry premium", "keyword premium", "tiered pricing", "high-renewal premium"],
                    ),
                ],
            ),
            Subcategory(
                name="Aftermarket",
                slug="market",
                description="Secondary market for domain names.",
                topics=[
                    Topic(
                        name="Aftermarket platforms",
                        description="Sedo, Afternic, Dan.com, GoDaddy Auctions — marketplace models.",
                        key_concepts=["aftermarket", "marketplace", "listing", "escrow", "commission"],
                    ),
                    Topic(
                        name="Domain auctions",
                        description="Expired domain auctions, private auctions, bidding strategies.",
                        key_concepts=["auction", "expired auction", "backorder", "proxy bidding"],
                    ),
                    Topic(
                        name="Domain parking",
                        description="Monetizing parked domains, PPC revenue, parking services.",
                        key_concepts=["parking", "PPC", "monetization", "landing page", "lander"],
                    ),
                    Topic(
                        name="Domain brokerage",
                        description="Professional domain acquisition, outbound contact, negotiation, escrow.",
                        key_concepts=["broker", "acquisition", "negotiation", "escrow", "commission"],
                    ),
                    Topic(
                        name="Domain leasing and rent-to-own",
                        description="Leasing domains instead of buying, rent-to-own models, legal considerations.",
                        key_concepts=["domain lease", "rent-to-own", "monthly payments", "lease agreement", "ownership transfer"],
                    ),
                    Topic(
                        name="Domain investment strategies",
                        description="Domain investing as an asset class, portfolio building, holding costs, exit strategies.",
                        key_concepts=["domain investing", "domaining", "portfolio building", "holding cost", "ROI", "exit strategy"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Drop catching and backorder services",
                        description="Automated capture of expiring domains, backorder platforms, auction mechanics.",
                        key_concepts=["drop catching", "backorder", "pending delete", "SnapNames", "NameJet", "timing"],
                    ),
                    Topic(
                        name="Domain escrow services",
                        description="Third-party escrow for domain transactions. Escrow.com is the ICANN-approved escrow for domain sales. Process steps: buyer deposits, seller transfers, buyer confirms, funds released.",
                        key_concepts=["domain escrow", "Escrow.com", "ICANN-approved", "buyer protection", "seller protection", "transaction process"],
                    ),
                    Topic(
                        name="Domain name as intellectual property",
                        description="How domains are classified as assets, treatment in bankruptcy proceedings, status in corporate acquisitions and M&A due diligence.",
                        key_concepts=["domain as asset", "intellectual property", "bankruptcy", "corporate acquisition", "M&A due diligence", "asset valuation"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 15. WEB HOSTING & CONTENT DELIVERY
    # ===================================================================
    Category(
        name="Web Hosting & Content Delivery",
        slug="hosting",
        description="Website hosting infrastructure and DNS-based content delivery mechanisms.",
        subcategories=[
            Subcategory(
                name="Hosting Fundamentals",
                slug="fundamentals",
                description="Types of web hosting and their DNS configuration.",
                topics=[
                    Topic(
                        name="Hosting types and DNS configuration",
                        description="Shared, VPS, dedicated, and cloud hosting — how DNS connects domains to each model.",
                        key_concepts=["shared hosting", "VPS", "dedicated server", "cloud hosting", "A record", "CNAME to host"],
                    ),
                    Topic(
                        name="IP-based vs name-based virtual hosting",
                        description="How web servers distinguish sites by IP address or Host header, SNI for TLS.",
                        key_concepts=["virtual hosting", "Host header", "SNI", "IP-based", "name-based", "shared IP"],
                    ),
                    Topic(
                        name="DNS configuration for hosting providers",
                        description="Pointing domains to hosting platforms, verification records, platform-specific DNS.",
                        key_concepts=["A record", "CNAME", "verification TXT", "nameserver delegation", "custom domain"],
                    ),
                    Topic(
                        name="Domain parking and default pages",
                        description="Registrar and hosting parking pages, under construction, holding pages. Distinct from aftermarket parking which focuses on domain monetization.",
                        key_concepts=["parking page", "default page", "holding page", "registrar parking", "hosting default", "under construction"],
                    ),
                    Topic(
                        name="Static site hosting and DNS",
                        description="GitHub Pages, Netlify, Vercel, S3 — DNS patterns for static hosting platforms.",
                        key_concepts=["GitHub Pages", "Netlify", "Vercel", "S3 static hosting", "CNAME flattening"],
                    ),
                    Topic(
                        name="IPv6-only hosting and DNS considerations",
                        description="DNS challenges with IPv6-only hosting: AAAA record requirements, Happy Eyeballs behavior, IPv6 reverse DNS, dual-stack fallback considerations.",
                        key_concepts=["IPv6-only hosting", "AAAA records", "Happy Eyeballs", "IPv6 rDNS", "dual-stack", "NAT64"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="CDN Architecture & DNS",
                slug="cdn",
                description="Content delivery networks and their DNS integration.",
                topics=[
                    Topic(
                        name="CDN overview and DNS integration",
                        description="How CDNs use DNS for edge routing, CNAME chains, anycast, and edge selection.",
                        key_concepts=["CDN", "edge server", "POP", "origin server", "DNS routing", "edge selection"],
                    ),
                    Topic(
                        name="CNAME-based CDN configuration",
                        description="Setting up CDN via CNAME, zone apex challenges, ALIAS/ANAME records.",
                        key_concepts=["CNAME to CDN", "zone apex", "ALIAS record", "ANAME", "CNAME flattening"],
                    ),
                    Topic(
                        name="Anycast CDN networks",
                        description="Anycast routing for CDN, BGP anycast, latency-based routing.",
                        key_concepts=["anycast", "BGP", "latency-based routing", "nearest POP", "anycast DNS"],
                    ),
                    Topic(
                        name="CDN provider ecosystem",
                        description="Major CDN providers, their DNS models, and integration patterns.",
                        key_concepts=["Cloudflare", "Akamai", "AWS CloudFront", "Fastly", "Azure CDN", "Google Cloud CDN"],
                    ),
                    Topic(
                        name="Multi-CDN strategies and DNS",
                        description="Using DNS to distribute traffic across multiple CDNs, failover between CDNs.",
                        key_concepts=["multi-CDN", "DNS-based failover", "traffic splitting", "CDN switching"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="DNS-Based Traffic Management",
                slug="traffic_management",
                description="Using DNS for load balancing, failover, and geographic routing.",
                topics=[
                    Topic(
                        name="DNS round-robin load balancing",
                        description="Multiple A/AAAA records, limitations, client behavior, TTL considerations.",
                        key_concepts=["round-robin", "multiple A records", "TTL", "client caching", "uneven distribution"],
                    ),
                    Topic(
                        name="Weighted and latency-based DNS routing",
                        description="Weighted record sets, latency-based routing, provider implementations.",
                        key_concepts=["weighted routing", "latency-based", "Route 53 policies", "traffic distribution"],
                    ),
                    Topic(
                        name="GeoDNS and geographic routing",
                        description="Routing users to nearest server by geographic location via DNS.",
                        key_concepts=["GeoDNS", "geographic routing", "GeoIP", "EDNS Client Subnet", "regional endpoints"],
                    ),
                    Topic(
                        name="Global Server Load Balancing (GSLB)",
                        description="DNS-based global load balancing across data centers, health-aware routing.",
                        key_concepts=["GSLB", "global load balancing", "health checks", "data center failover", "active-active"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS failover and health checking",
                        description="Automated DNS failover based on health checks, active-passive, TTL implications.",
                        key_concepts=["failover", "health check", "active-passive", "low TTL", "automated failover"],
                    ),
                    Topic(
                        name="Split-horizon DNS (split-brain)",
                        description="Serving different DNS responses for internal vs external queries.",
                        key_concepts=["split-horizon", "split-brain", "views", "internal DNS", "external DNS"],
                    ),
                ],
            ),
            Subcategory(
                name="Cloud & Managed DNS",
                slug="cloud_dns",
                description="Cloud provider and managed DNS services.",
                topics=[
                    Topic(
                        name="Cloud provider DNS services",
                        description="AWS Route 53, Google Cloud DNS, Azure DNS — features, pricing, integration.",
                        key_concepts=["Route 53", "Cloud DNS", "Azure DNS", "hosted zones", "alias records"],
                    ),
                    Topic(
                        name="Managed DNS providers",
                        description="Cloudflare DNS, NS1, Dyn, DNSimple, UltraDNS — features and differentiators.",
                        key_concepts=["managed DNS", "Cloudflare", "NS1", "Dyn", "DNSimple", "UltraDNS", "SLA"],
                    ),
                    Topic(
                        name="DNS for containerized environments",
                        description="CoreDNS, Kubernetes DNS, service discovery, internal cluster DNS.",
                        key_concepts=["CoreDNS", "kube-dns", "Kubernetes", "service discovery", "cluster.local"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS migration between providers",
                        description="Migrating DNS hosting, zone export/import, TTL pre-lowering, cutover strategies.",
                        key_concepts=["DNS migration", "zone export", "BIND format", "TTL lowering", "cutover"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Hosting Providers",
                slug="dns_providers",
                description="Major DNS hosting providers, their product offerings, technological capabilities, and how to evaluate them.",
                topics=[
                    Topic(
                        name="DNS provider landscape overview",
                        description="Categories of DNS hosting providers: cloud-integrated, independent managed, registrar-bundled, enterprise-grade. Market dynamics and consolidation trends.",
                        key_concepts=["managed DNS", "cloud DNS", "registrar DNS", "enterprise DNS", "independent providers", "market consolidation"],
                    ),
                    Topic(
                        name="Cloudflare DNS",
                        description="Cloudflare's free and paid DNS offerings, proxy mode (orange cloud), 1.1.1.1 resolver, Workers integration, DDoS protection, analytics, CNAME flattening, zero-TTL propagation.",
                        key_concepts=["Cloudflare", "orange cloud", "proxy mode", "CNAME flattening", "Cloudflare Workers", "1.1.1.1", "zero-TTL", "free DNS", "Universal SSL"],
                    ),
                    Topic(
                        name="Amazon Route 53",
                        description="Route 53 features: alias records, health checks, routing policies (simple, weighted, latency, geolocation, failover, multivalue), Traffic Flow, private hosted zones, DNSSEC signing, pricing model.",
                        key_concepts=["Route 53", "alias records", "health checks", "routing policies", "latency routing", "geolocation", "Traffic Flow", "private hosted zones", "per-query pricing"],
                    ),
                    Topic(
                        name="Google Cloud DNS",
                        description="Cloud DNS features: 100% SLA, public and private zones, DNSSEC, integration with GKE and Cloud CDN, peering zones, forwarding zones, response policies.",
                        key_concepts=["Cloud DNS", "100% SLA", "private zones", "peering zones", "forwarding zones", "response policies", "GKE integration"],
                    ),
                    Topic(
                        name="Azure DNS",
                        description="Azure DNS features: alias record sets, private DNS zones, DNS forwarding rulesets, Azure Traffic Manager integration, Azure Front Door DNS, zone delegation.",
                        key_concepts=["Azure DNS", "alias records", "private DNS zones", "Traffic Manager", "Azure Front Door", "forwarding rulesets"],
                    ),
                    Topic(
                        name="NS1 (IBM)",
                        description="NS1's advanced traffic steering: Filter Chains, Pulsar active traffic steering, managed DNS with RUM-based routing, DDoS protection, dedicated DNS networks, API-first design.",
                        key_concepts=["NS1", "Filter Chains", "Pulsar", "RUM-based routing", "traffic steering", "API-first", "dedicated networks", "IBM acquisition"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Akamai Edge DNS and enterprise DNS",
                        description="Akamai Edge DNS (formerly Fast DNS): enterprise-grade authoritative DNS, DDoS resilience, SiteShield integration, global anycast, zone apex CNAME support.",
                        key_concepts=["Akamai", "Edge DNS", "Fast DNS", "SiteShield", "enterprise DNS", "anycast", "DDoS resilience"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="UltraDNS (Vercara)",
                        description="UltraDNS features: enterprise DNS with DDoS protection, traffic management, sitebacker failover, directory services, UltraDDoS Protect, proactive monitoring.",
                        key_concepts=["UltraDNS", "Vercara", "Neustar", "DDoS Protect", "sitebacker", "traffic management", "enterprise"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNSimple and developer-focused providers",
                        description="DNSimple, DNS Made Easy, ClouDNS, Hetzner DNS, Bunny DNS, Hurricane Electric — developer-focused and independent DNS providers, their APIs, pricing, and specializations.",
                        key_concepts=["DNSimple", "DNS Made Easy", "ClouDNS", "Hetzner DNS", "Bunny DNS", "Hurricane Electric", "developer API", "independent DNS"],
                    ),
                    Topic(
                        name="Registrar DNS vs dedicated DNS hosting",
                        description="Comparing registrar-bundled DNS (GoDaddy, Namecheap, Porkbun) with dedicated DNS hosting. Performance, feature, reliability, and security differences.",
                        key_concepts=["registrar DNS", "bundled DNS", "dedicated DNS", "GoDaddy DNS", "Namecheap DNS", "performance comparison", "DNS delegation"],
                    ),
                    Topic(
                        name="DNS provider technology comparison",
                        description="Comparing provider capabilities: anycast network size, PoP locations, DNSSEC support, ALIAS/ANAME records, GeoDNS, failover, health checks, API quality, Terraform support, secondary DNS.",
                        key_concepts=["anycast network", "PoP locations", "ALIAS records", "ANAME records", "GeoDNS", "failover", "API quality", "Terraform provider", "secondary DNS", "zone transfer"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS provider pricing models",
                        description="Pricing comparison across DNS providers: free tiers, per-query pricing (Route 53), flat-rate (Cloudflare), tiered plans, enterprise contracts, overage charges, zone/record limits.",
                        key_concepts=["per-query pricing", "flat-rate DNS", "free tier", "zone limits", "record limits", "query volume", "enterprise pricing", "overage charges"],
                    ),
                    Topic(
                        name="Choosing a DNS provider",
                        description="Decision framework for selecting a DNS hosting provider based on requirements: reliability/SLA, performance, features, automation, security, cost, vendor lock-in, migration ease.",
                        key_concepts=["provider selection", "SLA requirements", "query volume", "feature needs", "vendor lock-in", "migration", "evaluation criteria", "RFP process"],
                    ),
                    Topic(
                        name="Multi-provider DNS and secondary DNS strategies",
                        description="Running DNS across multiple providers for redundancy: primary/secondary setups, zone transfer (AXFR/IXFR) between providers, NS record delegation patterns, hidden primary architecture.",
                        key_concepts=["multi-provider DNS", "secondary DNS", "AXFR", "IXFR", "hidden primary", "NS delegation", "provider redundancy", "DNS resilience"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Web Security via DNS",
                slug="web_security",
                description="DNS-layer security for web properties.",
                topics=[
                    Topic(
                        name="DDoS protection via DNS proxy",
                        description="DNS-based DDoS mitigation, traffic scrubbing, always-on vs on-demand.",
                        key_concepts=["DDoS protection", "DNS proxy", "traffic scrubbing", "always-on", "Cloudflare", "Akamai Prolexic"],
                    ),
                    Topic(
                        name="Web Application Firewalls via DNS",
                        description="WAF deployment via DNS CNAME/proxy, request filtering, bot protection.",
                        key_concepts=["WAF", "DNS proxy", "CNAME to WAF", "request filtering", "bot protection"],
                    ),
                    Topic(
                        name="Reverse proxy DNS patterns",
                        description="The Cloudflare model — proxying traffic via DNS, orange cloud, origin hiding.",
                        key_concepts=["reverse proxy", "origin hiding", "proxied DNS", "Cloudflare orange cloud", "origin IP protection"],
                    ),
                    Topic(
                        name="HSTS and domain security headers",
                        description="HTTP Strict Transport Security, HSTS preload list, domain-level security headers.",
                        key_concepts=["HSTS", "preload list", "max-age", "includeSubDomains", "Strict-Transport-Security"],
                        rfcs=["RFC 6797"],
                    ),
                ],
            ),
            Subcategory(
                name="Advanced Hosting Patterns",
                slug="advanced_hosting",
                description="Modern and complex DNS hosting patterns.",
                topics=[
                    Topic(
                        name="Serverless and edge computing DNS patterns",
                        description="DNS for Lambda@Edge, Cloudflare Workers, Deno Deploy — edge function routing.",
                        key_concepts=["serverless", "edge computing", "Lambda@Edge", "Cloudflare Workers", "edge routing"],
                    ),
                    Topic(
                        name="Multi-region and multi-cloud DNS architecture",
                        description="Designing DNS for multi-region deployments, cross-cloud failover, latency optimization.",
                        key_concepts=["multi-region", "multi-cloud", "cross-cloud", "latency optimization", "global architecture"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="SaaS custom domain onboarding patterns",
                        description="Technical patterns for SaaS platforms accepting customer custom domains.",
                        key_concepts=["custom domain", "SaaS DNS", "SNI routing", "CNAME verification", "wildcard TLS"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 16. INTERNET GOVERNANCE & STANDARDS BODIES
    # ===================================================================
    Category(
        name="Internet Governance & Standards Bodies",
        slug="governance",
        description="Organizations and processes that govern internet naming, numbering, and protocol standards.",
        subcategories=[
            Subcategory(
                name="Standards Organizations",
                slug="standards",
                description="Bodies that create and maintain internet standards.",
                topics=[
                    Topic(
                        name="IETF and the RFC process",
                        description="Internet Engineering Task Force, working groups, RFC publication, internet drafts, rough consensus.",
                        key_concepts=["IETF", "RFC", "working group", "internet draft", "rough consensus", "running code"],
                    ),
                    Topic(
                        name="IETF DNS-related working groups",
                        description="DNSOP, DPRIVE, ADD, DNSSD — active working groups shaping DNS evolution.",
                        key_concepts=["DNSOP", "DPRIVE", "ADD", "DNSSD", "DNS standards evolution"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="W3C and web standards relating to domains",
                        description="URL standards, origin model, same-origin policy, public suffix list. The WHATWG URL Standard (not W3C) is what browsers actually implement for URL parsing.",
                        key_concepts=["W3C", "URL spec", "origin", "same-origin policy", "public suffix list", "eTLD+1", "WHATWG URL Standard"],
                    ),
                    Topic(
                        name="IETF working group participation",
                        description="How to participate in IETF: mailing lists, datatracker, in-person meetings. Difference between contributor and WG chair. How rough consensus is reached.",
                        key_concepts=["IETF participation", "mailing lists", "datatracker", "WG chair", "rough consensus", "hum", "last call"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="ISO 3166 and country codes",
                        description="ISO 3166-1 alpha-2 codes underlie the ccTLD namespace. How country codes become ccTLD candidates, special cases (.uk vs .gb, .eu as regional TLD).",
                        key_concepts=["ISO 3166-1", "alpha-2 codes", "ccTLD mapping", ".uk vs .gb", ".eu regional", "country code assignment"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Regional Internet Registries",
                slug="rirs",
                description="Organizations managing IP address and AS number allocation.",
                topics=[
                    Topic(
                        name="RIR system overview",
                        description="ARIN, RIPE NCC, APNIC, LACNIC, AFRINIC — roles, regions, membership.",
                        key_concepts=["RIR", "ARIN", "RIPE NCC", "APNIC", "LACNIC", "AFRINIC", "NRO"],
                    ),
                    Topic(
                        name="IP address allocation and reverse DNS delegation",
                        description="How IP blocks are allocated and rDNS is delegated through the RIR hierarchy.",
                        key_concepts=["IP allocation", "rDNS delegation", "in-addr.arpa", "ip6.arpa", "SWIP", "assignment"],
                    ),
                    Topic(
                        name="RIR policy development",
                        description="Bottom-up policy process, policy proposals, regional meetings.",
                        key_concepts=["RIR PDP", "policy proposal", "regional meetings", "community consensus"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="RPKI and BGP security",
                        description="Resource Public Key Infrastructure managed by RIRs for routing security. ROA (Route Origin Authorization) prevents BGP hijacking. Increasingly relevant to DNS infrastructure security.",
                        key_concepts=["RPKI", "ROA", "Route Origin Authorization", "BGP hijacking prevention", "ARIN RPKI", "RIPE RPKI"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Internet Governance",
                slug="governance_forums",
                description="Multilateral and multistakeholder governance processes.",
                topics=[
                    Topic(
                        name="Internet Governance Forum (IGF)",
                        description="UN-mandated multistakeholder forum, workshops, best practice forums.",
                        key_concepts=["IGF", "United Nations", "multistakeholder", "workshops", "best practice forums"],
                    ),
                    Topic(
                        name="ITU and sovereign internet debates",
                        description="ITU's role, WCIT, proposals for DNS governance changes, national sovereignty debates.",
                        key_concepts=["ITU", "WCIT", "sovereign internet", "national DNS", "multilateral governance"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Multistakeholder vs multilateral governance",
                        description="Contrasting models for internet governance, ICANN's multistakeholder approach.",
                        key_concepts=["multistakeholder", "multilateral", "bottom-up", "government-led", "WSIS"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Internet fragmentation and DNS",
                        description="Splinternet risks, national DNS roots, censorship via DNS, great firewall.",
                        key_concepts=["fragmentation", "splinternet", "alternate roots", "DNS censorship", "great firewall"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="WSIS process and NETmundial",
                        description="World Summit on the Information Society, NETmundial principles, WSIS+20 review.",
                        key_concepts=["WSIS", "NETmundial", "Tunis Agenda", "WSIS+20", "internet governance principles"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 17. DOMAIN SECURITY & HIJACKING PREVENTION
    # ===================================================================
    Category(
        name="Domain Security & Hijacking Prevention",
        slug="domain_security",
        description="Protecting domains from unauthorized access, hijacking, and infrastructure attacks.",
        subcategories=[
            Subcategory(
                name="Domain Hijacking",
                slug="hijacking",
                description="Techniques and case studies of domain hijacking.",
                topics=[
                    Topic(
                        name="Domain hijacking techniques and case studies",
                        description="Methods attackers use to steal domains, notable incidents and lessons learned.",
                        key_concepts=["domain hijacking", "account compromise", "social engineering", "expired domain capture"],
                    ),
                    Topic(
                        name="Registrar account compromise",
                        description="Credential theft, phishing registrar accounts, insider threats.",
                        key_concepts=["account compromise", "credential theft", "phishing", "insider threat", "session hijacking"],
                    ),
                    Topic(
                        name="Social engineering attacks on registrars",
                        description="Pretexting, impersonation, support desk exploitation to gain domain control.",
                        key_concepts=["social engineering", "pretexting", "impersonation", "support desk", "identity verification"],
                    ),
                    Topic(
                        name="DNS infrastructure attacks",
                        description="Attacks against DNS servers, zone poisoning, BGP hijacking of DNS traffic. Notable incidents: 2010 China Telecom BGP hijack, 2019 BGP hijacks affecting Amazon Route 53.",
                        key_concepts=["DNS server attack", "zone poisoning", "BGP hijack", "NS record manipulation", "route hijacking", "Route 53 incident"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Subdomain takeover vulnerabilities",
                        description="Dangling CNAMEs, unclaimed cloud services, third-party subdomain risks.",
                        key_concepts=["subdomain takeover", "dangling CNAME", "unclaimed service", "cloud resource", "stale DNS"],
                    ),
                    Topic(
                        name="Expired domain exploitation",
                        description="Capturing expired domains for residual traffic, trust, backlinks, or impersonation.",
                        key_concepts=["expired domain", "residual traffic", "domain reputation", "backlink exploitation", "let-expire risk"],
                    ),
                ],
            ),
            Subcategory(
                name="Preventive Measures",
                slug="prevention",
                description="Securing domains against unauthorized access and changes.",
                topics=[
                    Topic(
                        name="Registrar account security",
                        description="Two-factor authentication, IP restrictions, access controls, account alerts.",
                        key_concepts=["2FA", "MFA", "IP whitelisting", "access controls", "account alerts", "audit log"],
                    ),
                    Topic(
                        name="Registry lock (detailed operations)",
                        description="How registry lock works operationally, the manual verification process, cost-benefit.",
                        key_concepts=["registry lock", "manual verification", "out-of-band confirmation", "lock/unlock process"],
                    ),
                    Topic(
                        name="DNSSEC as hijacking mitigation",
                        description="How DNSSEC prevents certain hijacking scenarios, limitations, what it doesn't protect.",
                        key_concepts=["DNSSEC protection", "response validation", "DS record", "limitations", "not encryption"],
                    ),
                    Topic(
                        name="Monitoring for unauthorized changes",
                        description="DNS change monitoring, WHOIS/RDAP monitoring, CT log monitoring, alert systems.",
                        key_concepts=["DNS monitoring", "WHOIS monitoring", "CT log alerts", "change detection", "unauthorized change"],
                    ),
                    Topic(
                        name="Incident response for domain compromise",
                        description="Steps to take when a domain is hijacked, registrar contacts, legal options, recovery.",
                        key_concepts=["incident response", "domain recovery", "registrar escalation", "legal action", "evidence preservation"],
                    ),
                ],
            ),
            Subcategory(
                name="Law Enforcement & Domain Seizures",
                slug="seizures",
                description="Government and law enforcement actions involving domains.",
                topics=[
                    Topic(
                        name="Domain seizure processes",
                        description="FBI, DOJ, Europol domain seizures, legal basis, operational mechanics.",
                        key_concepts=["domain seizure", "FBI", "DOJ", "Europol", "court order", "forfeiture"],
                    ),
                    Topic(
                        name="Court-ordered domain actions",
                        description="TROs, preliminary injunctions, domain transfers by court order.",
                        key_concepts=["TRO", "preliminary injunction", "court-ordered transfer", "in rem seizure"],
                    ),
                    Topic(
                        name="Sinkholing by law enforcement",
                        description="Redirecting malicious domains to law enforcement-controlled servers for intelligence.",
                        key_concepts=["sinkhole", "traffic redirection", "botnet takedown", "intelligence collection"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 18. COMPLIANCE & REGULATORY
    # ===================================================================
    Category(
        name="Compliance & Regulatory",
        slug="compliance",
        description="Legal, regulatory, and compliance frameworks affecting domain names and DNS operations.",
        subcategories=[
            Subcategory(
                name="DNS Operator Regulations",
                slug="dns_regulations",
                description="Regulatory requirements for DNS service operators.",
                topics=[
                    Topic(
                        name="NIS2 directive and DNS operators",
                        description="EU Network and Information Security Directive 2, obligations for DNS providers and TLD registries.",
                        key_concepts=["NIS2", "essential entities", "DNS service providers", "incident reporting", "security measures"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS4EU initiative",
                        description="EU sovereign DNS resolver initiative, goals, privacy, filtering.",
                        key_concepts=["DNS4EU", "sovereign DNS", "EU resolver", "privacy", "content filtering"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Critical infrastructure designation for DNS",
                        description="When DNS is classified as critical national infrastructure, implications and obligations.",
                        key_concepts=["critical infrastructure", "CNI", "DNS resilience", "national security", "redundancy requirements"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Registration Regulations",
                slug="registration_regs",
                description="Country and region-specific domain registration regulations.",
                topics=[
                    Topic(
                        name="Country-specific registration requirements",
                        description="Local presence, citizenship, business registration requirements by jurisdiction.",
                        key_concepts=["local presence", "citizenship requirement", "business registration", "jurisdiction"],
                    ),
                    Topic(
                        name="Real-name registration requirements",
                        description="Identity verification mandates (e.g., China .cn), KYC for domains.",
                        key_concepts=["real-name registration", "identity verification", "KYC", ".cn requirements"],
                    ),
                    Topic(
                        name="Age and eligibility restrictions",
                        description="Minimum age, organizational eligibility, restricted-use TLD requirements.",
                        key_concepts=["eligibility", "age restriction", "organizational requirement", "restricted TLD"],
                    ),
                ],
            ),
            Subcategory(
                name="Sanctions & Restrictions",
                slug="sanctions",
                description="Domain-related sanctions, seizures, and geopolitical restrictions.",
                topics=[
                    Topic(
                        name="OFAC and EU domain sanctions",
                        description="US OFAC and EU sanctions affecting domain registrations and services.",
                        key_concepts=["OFAC", "EU sanctions", "SDN list", "sanctioned countries", "registrar compliance"],
                    ),
                    Topic(
                        name="Domain seizure for sanctions violations",
                        description="Government seizure of domains violating sanctions regimes.",
                        key_concepts=["seizure", "sanctions violation", "forfeiture", "compliance failure"],
                    ),
                    Topic(
                        name=".eu and Brexit implications",
                        description="Impact of Brexit on .eu domain eligibility, EURid policy changes.",
                        key_concepts=[".eu", "Brexit", "EURid", "eligibility", "UK registrants"],
                    ),
                ],
            ),
            Subcategory(
                name="Data Protection & Privacy",
                slug="data_protection",
                description="Data protection laws affecting domain services beyond WHOIS.",
                topics=[
                    Topic(
                        name="GDPR impact on domain services",
                        description="GDPR beyond WHOIS — consent, data processing, DPAs, registrar obligations. Article 28 requires DPAs between registrars and their customers, and between registrars and ICANN.",
                        key_concepts=["GDPR", "data controller", "data processor", "DPA", "consent", "legitimate interest", "Article 28"],
                    ),
                    Topic(
                        name="GDPR right to erasure vs WHOIS retention",
                        description="Conflict between GDPR Article 17 right to erasure and ICANN's WHOIS retention requirements (RAA requires 2-year post-expiry retention). A specific compliance tension for registrars.",
                        key_concepts=["right to erasure", "Article 17", "WHOIS retention", "RAA retention", "2-year post-expiry", "compliance conflict"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="CCPA and domain registrations",
                        description="California Consumer Privacy Act impact on domain registrars serving US residents.",
                        key_concepts=["CCPA", "CPRA", "California", "consumer rights", "data sale"],
                    ),
                    Topic(
                        name="Data localization and DNS",
                        description="Requirements to store DNS or registration data within specific jurisdictions.",
                        key_concepts=["data localization", "data sovereignty", "cross-border transfer", "Schrems II"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Sector-Specific Regulations",
                slug="sector_regs",
                description="Regulations affecting DNS in specific industries.",
                topics=[
                    Topic(
                        name="DORA and financial sector DNS",
                        description="Digital Operational Resilience Act requirements for ICT services including DNS.",
                        key_concepts=["DORA", "financial sector", "ICT resilience", "third-party risk", "DNS as critical ICT"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Children's privacy and domain restrictions",
                        description="COPPA, age-gated TLDs, content restrictions via domain policy.",
                        key_concepts=["COPPA", "children's privacy", "age-gated", "content restrictions", ".kids"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 19. DNS MONITORING & OBSERVABILITY
    # ===================================================================
    Category(
        name="DNS Monitoring & Observability",
        slug="monitoring",
        description="Tools and techniques for monitoring, measuring, and analyzing DNS infrastructure and data.",
        subcategories=[
            Subcategory(
                name="DNS Analytics",
                slug="analytics",
                description="Query analysis, logging, and traffic intelligence.",
                topics=[
                    Topic(
                        name="DNS query analytics and logging",
                        description="Query logging, analysis of query types, response codes, client distribution.",
                        key_concepts=["query logging", "RCODE analysis", "qtype distribution", "client analysis", "dnstap"],
                    ),
                    Topic(
                        name="Passive DNS databases and intelligence",
                        description="Passive DNS collection, historical resolution data, threat intelligence use cases.",
                        key_concepts=["passive DNS", "pDNS", "historical resolution", "Farsight DNSDB", "threat intel"],
                    ),
                    Topic(
                        name="DNS traffic analysis and baselining",
                        description="Establishing DNS traffic baselines, anomaly detection, capacity planning.",
                        key_concepts=["traffic baseline", "anomaly detection", "capacity planning", "query volume trends"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNSTAP protocol",
                        description="Standard binary logging format for DNS servers, replacing older text-based logging. How to configure and use DNSTAP for high-performance DNS query capture and analysis.",
                        key_concepts=["DNSTAP", "binary logging", "DNS capture", "protobuf", "Frame Streams", "high-performance logging"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Propagation & Availability",
                slug="propagation",
                description="Monitoring DNS changes and infrastructure availability.",
                topics=[
                    Topic(
                        name="DNS propagation monitoring",
                        description="How DNS changes propagate, tools for checking propagation, TTL's role.",
                        key_concepts=["propagation", "TTL", "cache expiry", "global checking", "propagation delay"],
                    ),
                    Topic(
                        name="DNS change verification",
                        description="Verifying DNS changes took effect, checking authoritative vs recursive responses.",
                        key_concepts=["change verification", "authoritative query", "recursive query", "dig", "nslookup"],
                    ),
                    Topic(
                        name="DNS uptime and availability monitoring",
                        description="Monitoring authoritative server health, SLA tracking, redundancy verification.",
                        key_concepts=["uptime monitoring", "SLA", "nameserver health", "redundancy", "alerting"],
                    ),
                    Topic(
                        name="Global DNS check tools and methodology",
                        description="Tools and approaches for verifying DNS from multiple global locations.",
                        key_concepts=["global check", "distributed probes", "regional resolution", "whatsmydns", "DNS checker"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Intelligence",
                slug="intelligence",
                description="Using DNS data for security intelligence and asset discovery.",
                topics=[
                    Topic(
                        name="Passive DNS for threat intelligence",
                        description="Using historical DNS data to track threat actors, infrastructure mapping.",
                        key_concepts=["threat intelligence", "infrastructure mapping", "actor tracking", "domain pivoting"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS-based asset discovery",
                        description="Enumerating subdomains, certificate transparency for discovery, zone walking.",
                        key_concepts=["subdomain enumeration", "CT log mining", "zone walking", "asset inventory", "attack surface"],
                    ),
                    Topic(
                        name="Historical DNS records and analysis",
                        description="Tracking DNS changes over time, ownership analysis, infrastructure evolution.",
                        key_concepts=["historical DNS", "DNS history", "ownership changes", "infrastructure tracking"],
                    ),
                    Topic(
                        name="ICANN CZDS (Centralized Zone Data Service)",
                        description="Zone file access for research and monitoring. CZDS provides bulk access to gTLD zone files for approved researchers, brand protection teams, and security researchers.",
                        key_concepts=["CZDS", "zone file access", "zone data", "research access", "new registration monitoring", "ICANN CZDS"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 20. INTERNATIONALIZATION & UNIVERSAL ACCEPTANCE
    # ===================================================================
    Category(
        name="Internationalization & Universal Acceptance",
        slug="internationalization",
        description="Internationalized domain names, universal acceptance, and multilingual internet access.",
        subcategories=[
            Subcategory(
                name="Universal Acceptance (UA)",
                slug="ua",
                description="The initiative to ensure all domain names and email addresses work everywhere.",
                topics=[
                    Topic(
                        name="Universal Acceptance overview",
                        description="What UA is, why it matters, the UASG, current state of acceptance.",
                        key_concepts=["Universal Acceptance", "UASG", "UA readiness", "new TLD acceptance", "IDN acceptance"],
                    ),
                    Topic(
                        name="UA readiness of applications and systems",
                        description="Testing applications for UA compliance, common failure modes, remediation.",
                        key_concepts=["UA readiness", "validation failures", "TLD rejection", "email validation", "URL parsing"],
                    ),
                    Topic(
                        name="New TLD acceptance challenges",
                        description="Software rejecting new/long TLDs, hardcoded TLD lists, regex-based validation.",
                        key_concepts=["TLD rejection", "hardcoded list", "regex validation", ".email rejection", "long TLD"],
                    ),
                    Topic(
                        name="UA compliance testing frameworks",
                        description="Tools and methodologies for testing UA compliance, UASG documentation.",
                        key_concepts=["UA testing", "UASG guides", "compliance framework", "test cases"],
                    ),
                ],
            ),
            Subcategory(
                name="Internationalized Domain Names (Advanced)",
                slug="idn_advanced",
                description="Deep-dive into IDN complexities beyond basic registration.",
                topics=[
                    Topic(
                        name="IDN variant management and policies",
                        description="Variant TLDs, variant domain allocation, registry policies for variants.",
                        key_concepts=["IDN variants", "variant TLD", "variant allocation", "blocked variants", "allocatable variants"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Right-to-left scripts in domain names",
                        description="Arabic, Hebrew scripts in domains, BiDi handling, display challenges.",
                        key_concepts=["RTL", "Arabic script", "Hebrew", "BiDi", "display order", "logical vs visual"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Script mixing and confusability",
                        description="Homoglyph risks across scripts, whole-label evaluation, registration policies.",
                        key_concepts=["script mixing", "confusability", "whole-label evaluation", "single-script policy"],
                    ),
                    Topic(
                        name="IDN tables and label validation",
                        description="Reference Label Generation Rulesets, code point repertoires, registry IDN tables.",
                        key_concepts=["IDN table", "LGR", "code point", "repertoire", "reference LGR"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="IDNA 2008 vs IDNA 2003",
                        description="Protocol differences, deviation characters (ß, ς), browser behavior divergence. Chrome follows IDNA 2008; Firefox has nuanced handling of deviation characters.",
                        key_concepts=["IDNA 2008", "IDNA 2003", "deviation characters", "ß mapping", "browser divergence", "Chrome IDNA 2008", "Firefox handling"],
                        rfcs=["RFC 5890", "RFC 5891"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="CJK script challenges in domain names",
                        description="Specific challenges for Chinese (simplified vs traditional character variants), Japanese (three scripts: Hiragana, Katakana, Kanji), and Korean (Hangul vs Hanja). The three largest non-Latin internet user populations.",
                        key_concepts=["Chinese simplified/traditional", "Japanese scripts", "Hiragana", "Katakana", "Kanji", "Korean Hangul", "CJK variants", "character mapping"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Emoji domains",
                        description="Technical possibility of emoji in domain names, ICANN's position prohibiting emoji in new gTLDs, why they are not delegated. Common misconceptions and edge cases.",
                        key_concepts=["emoji domains", "ICANN position", "emoji prohibition", "Punycode encoding", "IDN table exclusion"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Email Address Internationalization",
                slug="eai",
                description="Internationalized email addresses and their DNS dependencies.",
                topics=[
                    Topic(
                        name="EAI overview and standards",
                        description="Email Address Internationalization, SMTPUTF8, UTF-8 in email headers. Downgrade to ASCII fallback mechanism for non-EAI-capable mail servers.",
                        key_concepts=["EAI", "SMTPUTF8", "UTF-8 headers", "internationalized mailbox", "RFC 6531", "downgrade to ASCII"],
                        rfcs=["RFC 6531", "RFC 6532"],
                    ),
                    Topic(
                        name="EAI and DNS interaction",
                        description="How internationalized email addresses interact with MX records, SPF, DKIM, DMARC.",
                        key_concepts=["EAI + MX", "EAI + SPF", "EAI + DKIM", "internationalized local-part"],
                    ),
                    Topic(
                        name="EAI adoption challenges",
                        description="Software support, interoperability, fallback mechanisms, deployment status.",
                        key_concepts=["EAI adoption", "software support", "downgrade", "fallback", "interoperability"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 21. DNS AUTOMATION & INFRASTRUCTURE AS CODE
    # ===================================================================
    Category(
        name="DNS Automation & Infrastructure as Code",
        slug="automation",
        description="Automating DNS management through code, APIs, and modern DevOps practices.",
        subcategories=[
            Subcategory(
                name="DNS as Code",
                slug="dns_as_code",
                description="Managing DNS configuration through version-controlled code.",
                topics=[
                    Topic(
                        name="Infrastructure as Code for DNS",
                        description="Terraform, Pulumi, and CloudFormation for DNS zone and record management.",
                        key_concepts=["Terraform", "Pulumi", "CloudFormation", "declarative DNS", "state management"],
                    ),
                    Topic(
                        name="DNS management tools",
                        description="OctoDNS, dnscontrol, cli53 — purpose-built DNS-as-code tools.",
                        key_concepts=["OctoDNS", "dnscontrol", "cli53", "zone sync", "multi-provider"],
                    ),
                    Topic(
                        name="Version control for DNS zones",
                        description="Git-based DNS management, code review for DNS changes, audit trails.",
                        key_concepts=["git", "version control", "code review", "audit trail", "change history"],
                    ),
                    Topic(
                        name="CI/CD pipelines for DNS changes",
                        description="Automated testing, validation, and deployment of DNS changes.",
                        key_concepts=["CI/CD", "automated testing", "DNS validation", "deployment pipeline", "dry run"],
                    ),
                    Topic(
                        name="DNS drift detection and reconciliation",
                        description="Detecting out-of-band DNS changes, reconciling desired vs actual state.",
                        key_concepts=["drift detection", "reconciliation", "desired state", "actual state", "out-of-band changes"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Registrar & Registry APIs",
                slug="apis",
                description="Programmatic interfaces for domain management.",
                topics=[
                    Topic(
                        name="EPP as an automation protocol",
                        description="Using EPP programmatically for domain lifecycle operations at scale.",
                        key_concepts=["EPP", "programmatic access", "EPP client libraries", "session management"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="Registrar REST APIs",
                        description="Modern REST APIs from registrars, common operations, authentication.",
                        key_concepts=["REST API", "registrar API", "API key", "domain CRUD", "DNS API"],
                    ),
                    Topic(
                        name="Domain management automation",
                        description="Scripting domain renewals, transfers, DNS updates, bulk operations.",
                        key_concepts=["automation", "bulk operations", "scripting", "renewal automation", "DNS updates"],
                    ),
                    Topic(
                        name="DNS provider API rate limiting and backoff",
                        description="Practical concern for DNS automation at scale: understanding provider rate limits, implementing exponential backoff, managing concurrent API calls, handling 429 responses.",
                        key_concepts=["API rate limiting", "exponential backoff", "429 Too Many Requests", "concurrent requests", "rate budget", "retry strategy"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Change Management",
                slug="change_management",
                description="Processes and practices for safe DNS changes.",
                topics=[
                    Topic(
                        name="DNS change workflows and approval",
                        description="Change request processes, peer review, approval gates, emergency changes.",
                        key_concepts=["change management", "peer review", "approval", "emergency change", "change window"],
                    ),
                    Topic(
                        name="DNS rollback strategies",
                        description="Planning for rollback, TTL considerations, pre-change snapshots.",
                        key_concepts=["rollback", "TTL planning", "snapshot", "pre-change state", "recovery"],
                    ),
                    Topic(
                        name="Blue-green and canary DNS deployments",
                        description="Using DNS for zero-downtime deployments, weighted routing for canary releases.",
                        key_concepts=["blue-green", "canary", "weighted routing", "zero-downtime", "traffic shifting"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="DNS audit trails and compliance",
                        description="Logging DNS changes, compliance requirements, audit evidence for SOC2/ISO.",
                        key_concepts=["audit trail", "change log", "SOC2", "ISO 27001", "compliance evidence"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Automated DNSSEC signing and key management",
                        description="Tools for automated DNSSEC signing: OpenDNSSEC, Knot DNS auto-signing, BIND automated key management. Key lifetime policies and automated rollover.",
                        key_concepts=["OpenDNSSEC", "Knot auto-sign", "BIND inline-signing", "key lifetime policies", "automated rollover", "DNSSEC automation"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 22. DNS SOFTWARE & IMPLEMENTATIONS
    # ===================================================================
    Category(
        name="DNS Software & Implementations",
        slug="dns_software",
        description="DNS server software, resolver implementations, and operational deployment.",
        subcategories=[
            Subcategory(
                name="Authoritative DNS Servers",
                slug="authoritative",
                description="Software for serving authoritative DNS responses.",
                topics=[
                    Topic(
                        name="BIND (Berkeley Internet Name Domain)",
                        description="ISC BIND, the most widely deployed DNS server — configuration, zones, views, security.",
                        key_concepts=["BIND", "named", "ISC", "named.conf", "zone files", "views", "BIND 9"],
                    ),
                    Topic(
                        name="PowerDNS Authoritative Server",
                        description="PowerDNS with database backends, API, Lua scripting, DNSSEC support.",
                        key_concepts=["PowerDNS", "pdns", "database backend", "API", "Lua", "gmysql", "gpgsql"],
                    ),
                    Topic(
                        name="NSD (Name Server Daemon)",
                        description="NLnet Labs' high-performance authoritative-only server, zone compilation.",
                        key_concepts=["NSD", "NLnet Labs", "authoritative-only", "nsd.conf", "zone compilation"],
                    ),
                    Topic(
                        name="Knot DNS",
                        description="CZ.NIC's authoritative server, automatic DNSSEC signing, catalog zones.",
                        key_concepts=["Knot DNS", "CZ.NIC", "automatic signing", "catalog zones", "knotd"],
                    ),
                    Topic(
                        name="Windows DNS Server",
                        description="Microsoft DNS integrated with Active Directory, AD-integrated zones, conditional forwarding.",
                        key_concepts=["Windows DNS", "Active Directory", "AD-integrated zones", "conditional forwarder", "dnscmd"],
                    ),
                    Topic(
                        name="Catalog zones (RFC 9432)",
                        description="New mechanism for automatically configuring secondary DNS servers with zone lists. Eliminates manual per-zone configuration on secondary servers. Supported by Knot DNS and BIND.",
                        key_concepts=["catalog zones", "automatic secondary configuration", "zone catalog", "Knot DNS catalog", "BIND catalog", "secondary provisioning"],
                        rfcs=["RFC 9432"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="dnsdist (PowerDNS load balancer)",
                        description="PowerDNS's DNS load balancer and proxy for front-ending DNS infrastructure. Traffic routing, load balancing, DoH/DoT termination, Lua scripting, DDoS mitigation.",
                        key_concepts=["dnsdist", "DNS load balancer", "DNS proxy", "DoH termination", "traffic routing", "Lua scripting", "PowerDNS"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Recursive Resolvers",
                slug="resolvers",
                description="Software for recursive DNS resolution.",
                topics=[
                    Topic(
                        name="Unbound",
                        description="NLnet Labs' validating, recursive, caching DNS resolver.",
                        key_concepts=["Unbound", "NLnet Labs", "DNSSEC validation", "caching", "unbound.conf", "prefetch"],
                    ),
                    Topic(
                        name="PowerDNS Recursor",
                        description="PowerDNS recursive resolver, Lua scripting, RPZ support, performance tuning.",
                        key_concepts=["PowerDNS Recursor", "pdns_recursor", "Lua hooks", "RPZ", "DNSSEC validation"],
                    ),
                    Topic(
                        name="BIND as recursive resolver",
                        description="Configuring BIND for recursion, forwarding, DNSSEC validation, rate limiting.",
                        key_concepts=["BIND recursion", "forwarders", "allow-recursion", "DNSSEC validation", "RRL"],
                    ),
                    Topic(
                        name="CoreDNS",
                        description="Pluggable DNS server written in Go, Kubernetes default, plugin architecture.",
                        key_concepts=["CoreDNS", "Go", "plugins", "Corefile", "Kubernetes", "middleware chain"],
                    ),
                    Topic(
                        name="Public recursive resolvers",
                        description="Google Public DNS (8.8.8.8), Cloudflare (1.1.1.1), Quad9 (9.9.9.9) — features and privacy.",
                        key_concepts=["8.8.8.8", "1.1.1.1", "9.9.9.9", "public resolver", "privacy policy", "EDNS Client Subnet"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Server Operations",
                slug="operations",
                description="Common operational tasks across DNS implementations.",
                topics=[
                    Topic(
                        name="DNS server hardening",
                        description="Security best practices: access control, rate limiting, version hiding, chroot.",
                        key_concepts=["hardening", "access control", "rate limiting", "version hiding", "chroot", "minimal exposure"],
                    ),
                    Topic(
                        name="DNS server performance tuning",
                        description="Cache sizing, thread tuning, TCP pipeline, connection limits, benchmarking.",
                        key_concepts=["performance", "cache size", "threads", "TCP pipeline", "dnsperf", "queryperf"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS logging and diagnostics",
                        description="Query logging, dnstap, response logging, debug levels, log rotation.",
                        key_concepts=["query logging", "dnstap", "debug logging", "log rotation", "audit logging"],
                    ),
                    Topic(
                        name="DNS high availability configurations",
                        description="Primary/secondary, hidden primary, anycast deployment, failover strategies.",
                        key_concepts=["primary/secondary", "hidden primary", "anycast", "failover", "NOTIFY"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 23. PROTECTIVE DNS & FILTERING
    # ===================================================================
    Category(
        name="Protective DNS & Filtering",
        slug="protective_dns",
        description="DNS-based security filtering, threat blocking, and content control services.",
        subcategories=[
            Subcategory(
                name="Protective DNS Services",
                slug="services",
                description="DNS resolvers that block malicious or unwanted content.",
                topics=[
                    Topic(
                        name="Protective DNS overview",
                        description="Concept of security-aware DNS resolution, threat blocking at the DNS layer.",
                        key_concepts=["protective DNS", "PDNS", "threat blocking", "DNS layer security", "resolver filtering"],
                    ),
                    Topic(
                        name="Quad9",
                        description="Quad9's threat intelligence-backed DNS, privacy focus, Swiss jurisdiction.",
                        key_concepts=["Quad9", "9.9.9.9", "threat intelligence", "GDPR", "Swiss privacy", "no logging"],
                    ),
                    Topic(
                        name="Cloudflare 1.1.1.1 family filtering",
                        description="Cloudflare's filtered DNS variants (1.1.1.2, 1.1.1.3), malware and adult content blocking.",
                        key_concepts=["1.1.1.2", "1.1.1.3", "malware blocking", "family filter", "Cloudflare for Families"],
                    ),
                    Topic(
                        name="OpenDNS and Cisco Umbrella",
                        description="OpenDNS filtering, Cisco Umbrella enterprise DNS security, custom policies.",
                        key_concepts=["OpenDNS", "Cisco Umbrella", "DNS security", "custom policy", "roaming clients"],
                    ),
                    Topic(
                        name="Enterprise protective DNS",
                        description="Enterprise DNS security platforms, policy enforcement, logging, compliance.",
                        key_concepts=["enterprise DNS", "policy enforcement", "DNS firewall", "compliance logging", "SASE"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="CISA Protective DNS",
                        description="US government protective DNS service for federal agencies. Integrates threat intelligence from US-CERT feeds. Mandatory for many federal civilian executive branch agencies.",
                        key_concepts=["CISA PDNS", "federal agencies", "threat intelligence integration", "US-CERT feeds", "FCEB agencies"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="DNS Filtering Mechanisms",
                slug="mechanisms",
                description="Technical approaches to DNS-based filtering.",
                topics=[
                    Topic(
                        name="RPZ (Response Policy Zones) in depth",
                        description="RPZ configuration, trigger types, actions, feed integration, performance impact.",
                        key_concepts=["RPZ", "QNAME trigger", "IP trigger", "NXDOMAIN action", "NODATA", "passthru", "feed"],
                    ),
                    Topic(
                        name="DNS sinkholing",
                        description="Redirecting malicious domains to controlled IPs, walled gardens, detection use cases.",
                        key_concepts=["sinkhole", "walled garden", "redirect", "detection", "honeypot DNS"],
                    ),
                    Topic(
                        name="DNS allowlists and blocklists",
                        description="Curating and applying domain lists, list sources, false positive management.",
                        key_concepts=["allowlist", "blocklist", "false positive", "list management", "threat feed"],
                    ),
                    Topic(
                        name="Pi-hole and local DNS filtering",
                        description="Self-hosted DNS filtering, ad blocking, network-wide filtering, gravity lists.",
                        key_concepts=["Pi-hole", "ad blocking", "gravity list", "local DNS", "network-wide filter"],
                    ),
                    Topic(
                        name="DNS filtering and encryption challenges",
                        description="Tension between enterprise DNS filtering (requiring DNS query visibility) and encrypted DNS (DoH/DoT hiding queries). A critical operational challenge with split-tunnel issues and enterprise bypass concerns.",
                        key_concepts=["DoH bypass", "encrypted DNS", "enterprise control", "split tunnel", "canary domain", "visibility vs privacy", "managed DoH"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Content & Parental Controls",
                slug="content_controls",
                description="DNS-based content filtering and access control.",
                topics=[
                    Topic(
                        name="DNS-based parental controls",
                        description="Family-safe DNS services, category blocking, time-based controls.",
                        key_concepts=["parental controls", "family filter", "safe search", "category blocking", "CleanBrowsing"],
                    ),
                    Topic(
                        name="Government DNS censorship",
                        description="State-level DNS blocking, court-ordered filtering, circumvention techniques.",
                        key_concepts=["DNS censorship", "government blocking", "court-ordered filter", "circumvention", "DNS leak"],
                        difficulty_range=("advanced", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 24. DNS DEBUGGING & TOOLING
    # ===================================================================
    Category(
        name="DNS Debugging & Tooling",
        slug="dns_tools",
        description="Command-line tools, diagnostic techniques, and online services for DNS troubleshooting.",
        subcategories=[
            Subcategory(
                name="Command-Line DNS Tools",
                slug="cli_tools",
                description="Essential CLI tools for DNS diagnostics.",
                topics=[
                    Topic(
                        name="dig (Domain Information Groper)",
                        description="The standard DNS query tool — query types, +trace, +short, @server, DNSSEC flags. Modern alternatives include dog and doggo.",
                        key_concepts=["dig", "+trace", "+short", "+dnssec", "@server", "query type", "dig output format", "dog", "doggo"],
                    ),
                    Topic(
                        name="nslookup",
                        description="Cross-platform DNS lookup tool, interactive mode, server selection, record types.",
                        key_concepts=["nslookup", "interactive mode", "set type", "server", "Windows default tool"],
                    ),
                    Topic(
                        name="host command",
                        description="Simple DNS lookup utility, reverse lookups, verbose mode.",
                        key_concepts=["host", "reverse lookup", "verbose", "simple output", "SOA query"],
                    ),
                    Topic(
                        name="drill",
                        description="DNSSEC-aware DNS query tool from NLnet Labs, trace mode, DNSSEC chain validation.",
                        key_concepts=["drill", "DNSSEC", "trace", "chase", "NLnet Labs", "DNSSEC validation"],
                    ),
                    Topic(
                        name="delv (DNS Enhanced Lookup Vetting)",
                        description="ISC's DNSSEC validation tool, trust anchor configuration, chain of trust display.",
                        key_concepts=["delv", "DNSSEC validation", "trust anchor", "ISC", "chain of trust"],
                    ),
                    Topic(
                        name="whois and rdap command-line tools",
                        description="CLI tools for domain registration data lookup, jwhois, rdap-client.",
                        key_concepts=["whois CLI", "jwhois", "rdap CLI", "registration data", "bulk WHOIS"],
                    ),
                ],
            ),
            Subcategory(
                name="Network Diagnostic Tools",
                slug="network_tools",
                description="Network tools with DNS relevance.",
                topics=[
                    Topic(
                        name="tcpdump and Wireshark for DNS",
                        description="Capturing and analyzing DNS packets, filtering DNS traffic, protocol analysis.",
                        key_concepts=["tcpdump", "Wireshark", "packet capture", "DNS filter", "protocol analysis", "port 53"],
                    ),
                    Topic(
                        name="mtr and traceroute for DNS path analysis",
                        description="Tracing network paths to DNS servers, diagnosing routing issues.",
                        key_concepts=["mtr", "traceroute", "network path", "latency", "packet loss", "DNS server routing"],
                    ),
                    Topic(
                        name="curl and DNS diagnostics",
                        description="Using curl for DNS-related testing — resolve override, DoH queries, timing.",
                        key_concepts=["curl --resolve", "curl --doh-url", "DNS timing", "connect-to", "HTTP DNS"],
                    ),
                ],
            ),
            Subcategory(
                name="Online DNS Tools & Services",
                slug="online_tools",
                description="Web-based DNS diagnostic and monitoring services.",
                topics=[
                    Topic(
                        name="DNS propagation checkers",
                        description="whatsmydns.net, dnschecker.org — global propagation verification.",
                        key_concepts=["propagation checker", "global DNS check", "whatsmydns", "dnschecker"],
                    ),
                    Topic(
                        name="DNS diagnostic services",
                        description="DNSViz (DNSSEC visualization), IntoDNS, Zonemaster — comprehensive DNS auditing.",
                        key_concepts=["DNSViz", "IntoDNS", "Zonemaster", "DNS audit", "health check"],
                    ),
                    Topic(
                        name="WHOIS and RDAP lookup services",
                        description="who.is, ICANN Lookup, RDAP web clients, bulk lookup tools.",
                        key_concepts=["ICANN Lookup", "who.is", "RDAP web client", "bulk lookup"],
                    ),
                    Topic(
                        name="SSL/TLS testing tools",
                        description="SSL Labs, crt.sh (CT logs), Hardenize — certificate and domain security testing.",
                        key_concepts=["SSL Labs", "crt.sh", "Hardenize", "certificate test", "security grade"],
                    ),
                    Topic(
                        name="Email authentication testing tools",
                        description="MXToolbox, dmarcian, DKIM validator — email DNS configuration verification.",
                        key_concepts=["MXToolbox", "dmarcian", "DKIM validator", "SPF check", "DMARC check"],
                    ),
                ],
            ),
            Subcategory(
                name="DNS Troubleshooting Techniques",
                slug="troubleshooting",
                description="Systematic approaches to diagnosing DNS issues.",
                topics=[
                    Topic(
                        name="Systematic DNS troubleshooting methodology",
                        description="Step-by-step approach: check local, check recursive, check authoritative, check propagation.",
                        key_concepts=["methodology", "local resolver", "recursive", "authoritative", "systematic diagnosis"],
                    ),
                    Topic(
                        name="Common DNS misconfigurations",
                        description="Lame delegations, missing glue, CNAME at apex, SOA serial issues, TTL mistakes.",
                        key_concepts=["lame delegation", "missing glue", "CNAME at apex", "SOA serial", "TTL too high/low"],
                    ),
                    Topic(
                        name="DNSSEC troubleshooting",
                        description="Diagnosing DNSSEC validation failures, expired signatures, DS/DNSKEY mismatch, algorithm issues.",
                        key_concepts=["SERVFAIL", "expired RRSIG", "DS mismatch", "algorithm rollover", "bogus response"],
                        difficulty_range=("advanced", "expert"),
                    ),
                    Topic(
                        name="DNS resolution latency troubleshooting",
                        description="Diagnosing slow DNS, identifying bottlenecks, recursive vs authoritative delays.",
                        key_concepts=["latency", "slow DNS", "query time", "resolver performance", "authoritative delay"],
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 25. DOMAIN NAME INDUSTRY & BUSINESS
    # ===================================================================
    Category(
        name="Domain Name Industry & Business",
        slug="industry",
        description="The domain name industry as a business — market dynamics, key players, events, and professional roles.",
        subcategories=[
            Subcategory(
                name="Market Landscape",
                slug="market",
                description="The domain name industry's business landscape.",
                topics=[
                    Topic(
                        name="Domain industry market overview",
                        description="Market size, growth trends, registration volumes, revenue streams.",
                        key_concepts=["market size", "registration volume", "growth trends", "revenue", "industry reports"],
                    ),
                    Topic(
                        name="Major registries and their portfolios",
                        description="Verisign, Identity Digital, Radix, CentralNic, PIR — who operates what.",
                        key_concepts=["Verisign", "Identity Digital", "Radix", "CentralNic", "PIR", "registry operator"],
                    ),
                    Topic(
                        name="Major registrars and market share",
                        description="GoDaddy, Namecheap, Tucows, Google Domains, regional leaders.",
                        key_concepts=["GoDaddy", "Namecheap", "Tucows", "market share", "regional registrar"],
                    ),
                    Topic(
                        name="Corporate domain management providers",
                        description="CSC, MarkMonitor, Safenames, Com Laude — enterprise domain services.",
                        key_concepts=["corporate registrar", "CSC", "MarkMonitor", "Safenames", "Com Laude", "managed services"],
                    ),
                    Topic(
                        name="DNS hosting market",
                        description="Cloudflare, AWS Route 53, NS1, Dyn, Akamai — managed DNS as a business.",
                        key_concepts=["DNS hosting", "managed DNS", "Cloudflare", "Route 53", "NS1", "market segments"],
                    ),
                    Topic(
                        name="Domain industry consolidation trends",
                        description="How the industry is consolidating: fewer but larger registrars, registry consolidation (Identity Digital/Donuts acquisition of Afilias). Implications for competition and choice.",
                        key_concepts=["consolidation", "registrar M&A", "registry consolidation", "Identity Digital", "Donuts/Afilias", "market concentration"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                    Topic(
                        name="Domain industry trade associations",
                        description="Where industry advocacy happens: Internet Commerce Association (ICA), ICANN Registrar Stakeholder Group, TLDops community, DNS-OARC.",
                        key_concepts=["ICA", "Internet Commerce Association", "Registrar Stakeholder Group", "TLDops", "industry advocacy"],
                        difficulty_range=("intermediate", "expert"),
                    ),
                ],
            ),
            Subcategory(
                name="Industry Events & Community",
                slug="events",
                description="Industry conferences, meetings, and professional community.",
                topics=[
                    Topic(
                        name="ICANN meetings",
                        description="Three annual ICANN meetings, AGM, policy forums, community forums, participation.",
                        key_concepts=["ICANN meeting", "AGM", "policy forum", "community forum", "remote participation"],
                    ),
                    Topic(
                        name="Domain industry conferences",
                        description="NamesCon, WHD (WebhostingDay), DNS-OARC, RIPE meetings, regional events.",
                        key_concepts=["NamesCon", "WHD", "DNS-OARC", "RIPE", "regional conference"],
                    ),
                    Topic(
                        name="ICANN fellowship and NextGen programs",
                        description="Programs for newcomers to ICANN, fellowship, NextGen@ICANN, onboarding.",
                        key_concepts=["fellowship", "NextGen", "newcomer", "onboarding", "capacity building"],
                    ),
                ],
            ),
            Subcategory(
                name="Professional Roles",
                slug="roles",
                description="Career roles in the domain name industry.",
                topics=[
                    Topic(
                        name="Domain name industry career paths",
                        description="Registry operations, registrar services, DNS engineering, policy, legal, brand protection.",
                        key_concepts=["career paths", "DNS engineer", "policy analyst", "domain manager", "brand protection analyst"],
                    ),
                    Topic(
                        name="Corporate domain management role",
                        description="What a corporate domain manager does — portfolio management, vendor relations, policy compliance.",
                        key_concepts=["domain manager", "portfolio management", "vendor management", "compliance", "budget"],
                    ),
                    Topic(
                        name="DNS engineer and operator role",
                        description="Running DNS infrastructure, capacity planning, incident response, automation.",
                        key_concepts=["DNS engineer", "infrastructure", "capacity planning", "incident response", "SRE"],
                    ),
                ],
            ),
            Subcategory(
                name="Subdomain Strategy & Architecture",
                slug="subdomain_strategy",
                description="Strategic and architectural use of subdomains.",
                topics=[
                    Topic(
                        name="Subdomain architecture patterns",
                        description="Environment subdomains (dev/staging/prod), service subdomains, geographic subdomains.",
                        key_concepts=["environment subdomains", "service subdomains", "geographic subdomains", "naming conventions"],
                    ),
                    Topic(
                        name="Subdomain delegation",
                        description="Delegating subdomains to different nameservers, teams, or providers.",
                        key_concepts=["subdomain delegation", "NS records", "team ownership", "provider delegation"],
                    ),
                    Topic(
                        name="SaaS custom domain onboarding",
                        description="Enabling customers to use custom domains with SaaS platforms, CNAME/A verification, TLS provisioning.",
                        key_concepts=["custom domain", "SaaS", "CNAME verification", "TLS provisioning", "domain onboarding"],
                    ),
                    Topic(
                        name="Public Suffix List",
                        description="Mozilla's PSL, eTLD+1 concept, cookie scoping, registrable domain determination.",
                        key_concepts=["Public Suffix List", "PSL", "eTLD+1", "cookie scoping", "registrable domain", "effective TLD"],
                    ),
                ],
            ),
            Subcategory(
                name="Emerging Trends",
                slug="emerging_trends",
                description="Emerging technologies and trends affecting the domain name industry.",
                topics=[
                    Topic(
                        name="AI and domain names",
                        description="Impact of AI on the domain industry: AI-powered domain generation for phishing, AI-generated brand impersonation, AI in UDRP/dispute analysis, AI-assisted domain valuation, LLM-powered domain tools, ICANN's developing policies on AI-generated content in disputes.",
                        key_concepts=["AI phishing", "AI brand impersonation", "AI domain generation", "LLM domain tools", "AI dispute analysis", "deepfake domains"],
                    ),
                    Topic(
                        name="Blockchain and alternative naming systems",
                        description="Ethereum Name Service (ENS), Handshake (HNS), Unstoppable Domains — how blockchain-based naming works, .eth and .crypto domains, ICANN's position on alternative roots, name collision risks with ICANN TLDs, cryptocurrency wallet address resolution, browser support status.",
                        key_concepts=["ENS", "Ethereum Name Service", ".eth", "Handshake", "HNS", "Unstoppable Domains", ".crypto", "alternative roots", "name collision", "ICANN position", "wallet resolution"],
                    ),
                    Topic(
                        name="Privacy-focused DNS evolution",
                        description="The trajectory of DNS privacy: from cleartext to encrypted DNS (DoH, DoT, DoQ), Oblivious DoH, encrypted client hello (ECH), privacy-preserving WHOIS/RDAP, DNS data minimization trends, regulatory drivers (GDPR impact on DNS data).",
                        key_concepts=["DNS privacy evolution", "encrypted DNS adoption", "ODoH", "ECH", "WHOIS privacy", "data minimization", "GDPR DNS impact"],
                    ),
                    Topic(
                        name="Post-quantum DNS and DNSSEC",
                        description="Impact of quantum computing on DNS security: post-quantum cryptography for DNSSEC signatures, larger key/signature sizes and DNS message constraints, NIST PQC standards, transition planning for DNSSEC algorithm migration, timeline considerations.",
                        key_concepts=["post-quantum", "PQC", "DNSSEC quantum", "larger signatures", "NIST PQC", "algorithm migration", "quantum-safe DNS"],
                        difficulty_range=("expert", "expert"),
                    ),
                ],
            ),
        ],
    ),
    # ===================================================================
    # 26. ARCANUM SUITE TOOL USAGE
    # ===================================================================
    Category(
        name="Arcanum Suite Tool Usage",
        slug="tools",
        description="How to use the Arcanum Suite's diagnostic and reference tools for domain intelligence tasks.",
        subcategories=[
            Subcategory(
                name="Seer Diagnostics — Single Domain",
                slug="seer_single",
                description="Using seer's single-domain diagnostic tools.",
                topics=[
                    Topic(
                        name="seer_lookup — smart domain registration lookup",
                        description="Use seer_lookup for registration data. Tries RDAP first, falls back to WHOIS. Returns registrar, dates, nameservers, status.",
                        key_concepts=["seer_lookup", "RDAP fallback", "registration data", "domain parameter", "registrar identification", "creation date", "expiry date", "nameserver list"],
                    ),
                    Topic(
                        name="seer_whois — WHOIS registration data",
                        description="Use seer_whois for raw WHOIS data. Returns registrar, creation/expiry dates, nameservers, status codes. 15s timeout.",
                        key_concepts=["seer_whois", "WHOIS", "registrar", "expiry date", "status codes", "raw text output", "15s timeout", "port 43"],
                    ),
                    Topic(
                        name="seer_rdap_domain — RDAP domain lookup",
                        description="Use seer_rdap_domain for structured RDAP data. Returns registrar, dates, nameservers, DNSSEC status. 30s timeout.",
                        key_concepts=["seer_rdap_domain", "RDAP", "structured data", "DNSSEC status", "JSON response", "30s timeout", "bootstrap discovery"],
                    ),
                    Topic(
                        name="seer_rdap_ip — RDAP IP address lookup",
                        description="Use seer_rdap_ip for IP registration info. Accepts IPv4 or IPv6. Returns network range, country, organization.",
                        key_concepts=["seer_rdap_ip", "IP lookup", "network range", "organization", "IPv4", "IPv6", "RIR data", "CIDR block"],
                    ),
                    Topic(
                        name="seer_rdap_asn — RDAP ASN lookup",
                        description="Use seer_rdap_asn for Autonomous System info. Takes ASN integer. Returns organization and network ranges.",
                        key_concepts=["seer_rdap_asn", "ASN", "autonomous system", "organization", "network range"],
                    ),
                    Topic(
                        name="seer_dig — DNS record query",
                        description="Use seer_dig for DNS lookups. Parameters: domain (required), record_type (default 'A'), nameserver (optional). Returns DNS records.",
                        key_concepts=["seer_dig", "record_type", "A", "AAAA", "MX", "TXT", "NS", "SOA", "CNAME", "CAA", "nameserver"],
                    ),
                    Topic(
                        name="seer_propagation — global DNS propagation check",
                        description="Use seer_propagation to check DNS consistency across 29 global servers. Returns propagation percentage and per-server results.",
                        key_concepts=["seer_propagation", "29 servers", "propagation percentage", "consistency", "global check", "regional variation", "cache expiry"],
                    ),
                    Topic(
                        name="seer_status — domain health check",
                        description="Use seer_status for comprehensive health: HTTP status, SSL certificate validity, expiration date, combined health indicators.",
                        key_concepts=["seer_status", "HTTP status", "SSL validity", "expiry", "health check", "redirect following", "certificate chain", "10s timeout"],
                    ),
                ],
            ),
            Subcategory(
                name="Seer Diagnostics — Bulk Operations",
                slug="seer_bulk",
                description="Using seer's bulk diagnostic tools for multiple domains.",
                topics=[
                    Topic(
                        name="Bulk operations overview",
                        description="All bulk tools accept domains array (max 100) and concurrency parameter (default 10, max 50). Semaphore-based rate limiting.",
                        key_concepts=["bulk operations", "max 100 domains", "concurrency", "semaphore", "rate limiting", "domains array", "concurrent execution"],
                    ),
                    Topic(
                        name="seer_bulk_lookup — bulk registration data",
                        description="Use seer_bulk_lookup for registration data on multiple domains simultaneously. RDAP with WHOIS fallback per domain.",
                        key_concepts=["seer_bulk_lookup", "bulk RDAP", "concurrent lookups", "portfolio check"],
                    ),
                    Topic(
                        name="seer_bulk_dig — bulk DNS queries",
                        description="Use seer_bulk_dig for DNS records across many domains. Accepts record_type parameter applied to all domains.",
                        key_concepts=["seer_bulk_dig", "bulk DNS", "record_type", "multi-domain query"],
                    ),
                    Topic(
                        name="seer_bulk_status — bulk health checks",
                        description="Use seer_bulk_status for health checks across a portfolio. Returns HTTP, SSL, and expiry status per domain.",
                        key_concepts=["seer_bulk_status", "portfolio health", "bulk SSL check", "bulk HTTP check"],
                    ),
                    Topic(
                        name="seer_bulk_propagation — bulk propagation checks",
                        description="Use seer_bulk_propagation to verify DNS propagation for many domains. Default concurrency 5 (lower due to 29 servers per domain).",
                        key_concepts=["seer_bulk_propagation", "bulk propagation", "lower concurrency", "29 servers per domain"],
                    ),
                ],
            ),
            Subcategory(
                name="Tome Reference Data",
                slug="tome",
                description="Using tome's reference database tools for TLD, record type, and glossary lookups.",
                topics=[
                    Topic(
                        name="tome_tld_lookup — TLD information",
                        description="Use tome_tld_lookup for detailed TLD info: type, registry, WHOIS/RDAP servers, DNSSEC, restrictions. Pass TLD without leading dot.",
                        key_concepts=["tome_tld_lookup", "TLD info", "registry", "WHOIS server", "RDAP URL", "no leading dot", "DNSSEC support", "IDN support"],
                    ),
                    Topic(
                        name="tome_tld_search — search TLDs by keyword",
                        description="Use tome_tld_search to find TLDs matching a keyword. Searches across names, registries, and descriptions.",
                        key_concepts=["tome_tld_search", "keyword search", "TLD discovery", "partial match"],
                    ),
                    Topic(
                        name="tome_tld_overview — comprehensive TLD overview",
                        description="Use tome_tld_overview for rich TLD detail: registry operator, country mapping, WHOIS/RDAP, registration model, transfer rules.",
                        key_concepts=["tome_tld_overview", "comprehensive", "registry operator", "registration model", "transfer rules"],
                    ),
                    Topic(
                        name="tome_tld_list_by_type and tome_tld_count",
                        description="Use tome_tld_list_by_type to list all TLDs by category (gTLD, ccTLD, nTLD). Use tome_tld_count for total count.",
                        key_concepts=["tome_tld_list_by_type", "tome_tld_count", "gTLD", "ccTLD", "nTLD", "enumeration"],
                    ),
                    Topic(
                        name="tome_record_lookup and tome_record_search",
                        description="Use tome_record_lookup for DNS record type details by name or IANA code. Use tome_record_search for keyword search across record types.",
                        key_concepts=["tome_record_lookup", "tome_record_search", "record type", "IANA code", "RFC reference", "record format", "usage examples"],
                    ),
                    Topic(
                        name="tome_glossary_lookup and tome_glossary_search",
                        description="Use tome_glossary_lookup for domain industry term definitions. Use tome_glossary_search to search by keyword.",
                        key_concepts=["tome_glossary_lookup", "tome_glossary_search", "definition", "category", "related terms", "acronym expansion", "context"],
                    ),
                ],
            ),
            Subcategory(
                name="Tool Selection & Workflows",
                slug="workflows",
                description="Choosing the right tools and combining them for complex domain intelligence tasks.",
                topics=[
                    Topic(
                        name="Choosing the right lookup tool",
                        description="When to use seer_lookup vs seer_whois vs seer_rdap_domain. RDAP is preferred for structured data; WHOIS for legacy TLDs or when RDAP is unavailable.",
                        key_concepts=["tool selection", "RDAP vs WHOIS", "seer_lookup fallback", "structured vs raw", "ccTLD RDAP gaps", "WHOIS for legacy"],
                    ),
                    Topic(
                        name="Domain health audit workflow",
                        description="Combining seer_status + seer_dig + seer_propagation for a comprehensive domain health assessment.",
                        key_concepts=["health audit", "combined tools", "status + dig + propagation", "comprehensive check", "SSL expiry check", "DNS consistency", "HTTP redirect chain"],
                    ),
                    Topic(
                        name="Portfolio assessment workflow",
                        description="Using bulk tools for portfolio-wide assessments: bulk_status for health, bulk_lookup for registration, bulk_dig for DNS consistency.",
                        key_concepts=["portfolio assessment", "bulk tools", "registration audit", "DNS audit", "health audit", "expiry calendar", "registrar distribution", "nameserver diversity"],
                    ),
                    Topic(
                        name="DNS migration verification workflow",
                        description="Using seer_propagation and seer_dig with specific nameservers to verify DNS migrations and changes.",
                        key_concepts=["migration verification", "propagation check", "nameserver parameter", "before/after comparison", "TTL awareness", "cutover validation"],
                    ),
                    Topic(
                        name="TLD research workflow",
                        description="Using tome_tld_search to discover TLDs, tome_tld_overview for details, then seer tools for live diagnostics.",
                        key_concepts=["TLD research", "tome + seer", "discovery to diagnostics", "reference + live data", "TLD comparison", "registration requirements"],
                    ),
                    Topic(
                        name="Investigating domain ownership and infrastructure",
                        description="Combining seer_rdap_domain + seer_dig (NS, A, MX) + seer_rdap_ip to map a domain's full infrastructure.",
                        key_concepts=["infrastructure mapping", "ownership", "RDAP + dig + IP lookup", "full picture", "hosting provider identification", "email provider identification", "network owner"],
                    ),
                    Topic(
                        name="Interpreting tool results and error handling",
                        description="Understanding tool output formats, handling timeouts, dealing with unavailable RDAP/WHOIS, rate limit errors. Specific error codes: WHOIS rate limit errors, RDAP bootstrap failures, DNS SERVFAIL vs NXDOMAIN interpretation.",
                        key_concepts=["error handling", "timeouts", "unavailable data", "rate limits", "result interpretation", "SERVFAIL vs NXDOMAIN", "RDAP bootstrap failure", "WHOIS rate limit"],
                    ),
                    Topic(
                        name="Tool limitations and known gaps",
                        description="What seer tools cannot do: cannot perform zone transfers, cannot access ccTLD registrar EPP systems directly, WHOIS parsing may miss non-standard formats, RDAP coverage varies by TLD.",
                        key_concepts=["tool limitations", "no zone transfer", "no EPP access", "WHOIS parsing limits", "RDAP coverage gaps", "ccTLD limitations"],
                    ),
                ],
            ),
            Subcategory(
                name="Scrolls — Analytical Skills",
                slug="scrolls_skills",
                description="Higher-level analytical skills from scrolls that compose base tools into domain intelligence workflows.",
                topics=[
                    Topic(
                        name="Email authentication analysis skill",
                        description="Using the email-auth skill to audit SPF, DKIM, DMARC configuration. Combines seer_dig TXT queries with policy analysis.",
                        key_concepts=["email-auth skill", "SPF audit", "DKIM validation", "DMARC analysis", "policy gaps", "alignment check", "reporting configuration"],
                    ),
                    Topic(
                        name="Zone health audit skill",
                        description="Using the zone-health skill to audit DNS zones against best-practice checklists: SOA, NS, MX, CNAME, CAA, DNSSEC, TTL consistency.",
                        key_concepts=["zone-health skill", "best practices", "checklist", "severity levels", "recommendations", "lame delegation check", "DNSSEC validation"],
                    ),
                    Topic(
                        name="Portfolio audit skill",
                        description="Using the portfolio-audit skill for multi-domain health assessment across registration, DNS, SSL, security, and consistency dimensions.",
                        key_concepts=["portfolio-audit skill", "multi-domain", "scoring", "report template", "dimension analysis", "risk scoring", "expiry tracking"],
                    ),
                    Topic(
                        name="Typosquatting detection skill",
                        description="Using the typosquatting skill to generate lookalike domains via omission, transposition, homoglyphs, bitsquatting, TLD swaps, then triage results.",
                        key_concepts=["typosquatting skill", "lookalike generation", "homoglyphs", "bitsquatting", "triage", "TLD swaps", "keyboard adjacency", "registration check"],
                    ),
                    Topic(
                        name="Phishing and abuse analysis skill",
                        description="Using the phishing-analysis skill to detect threat indicators across registration, DNS, SSL, and infrastructure signals.",
                        key_concepts=["phishing-analysis skill", "threat indicators", "abuse scoring", "registration signals", "reporting", "domain age signal", "registrar reputation"],
                    ),
                    Topic(
                        name="HTTP recon skill",
                        description="Using the http-recon skill for redirect tracing, security header auditing (HSTS, CSP, X-Content-Type-Options), and technology fingerprinting.",
                        key_concepts=["http-recon skill", "redirect chain", "security headers", "HSTS", "CSP", "fingerprinting", "X-Content-Type-Options", "server header"],
                    ),
                    Topic(
                        name="CDN and hosting detection skill",
                        description="Using the cdn-detection skill to identify infrastructure providers from DNS patterns, HTTP headers, IP ranges, and SSL certificates.",
                        key_concepts=["cdn-detection skill", "provider identification", "DNS patterns", "CNAME signatures", "IP ranges", "certificate issuer", "header analysis"],
                    ),
                    Topic(
                        name="Migration planner skill",
                        description="Using the migration-planner skill for five-phase DNS provider migrations: audit, prepare, execute, validate, cleanup.",
                        key_concepts=["migration-planner skill", "five phases", "pre-flight checks", "validation", "TTL lowering", "rollback plan", "cutover checklist"],
                    ),
                    Topic(
                        name="Penetration testing skill",
                        description="Using the pentest skill for domain vulnerability scanning: subdomain takeover, HTTP security, email auth gaps, SSL/TLS, DNS zone security.",
                        key_concepts=["pentest skill", "subdomain takeover", "vulnerability scanning", "exposure report", "security assessment", "dangling CNAME detection", "open relay check"],
                    ),
                    Topic(
                        name="Registration compliance skill",
                        description="Using the registration-compliance skill to check ICANN policy adherence: lifecycle, transfers, disputes, registration data requirements.",
                        key_concepts=["registration-compliance skill", "ICANN policy", "lifecycle", "transfer rules", "EPP status", "WHOIS accuracy", "lock status"],
                    ),
                    Topic(
                        name="RFC reference skill",
                        description="Using the rfc-reference skill to look up domain-relevant RFCs with plain-language summaries across DNS, DNSSEC, email auth, WHOIS/RDAP, and operations.",
                        key_concepts=["rfc-reference skill", "RFC lookup", "plain-language summary", "cross-reference", "RFC by topic", "obsoleted RFC tracking"],
                    ),
                ],
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_category(slug: str) -> Category | None:
    """Look up a category by slug."""
    return next((c for c in TAXONOMY if c.slug == slug), None)


def all_topics() -> list[tuple[Category, Subcategory, Topic]]:
    """Yield every (category, subcategory, topic) triple in the taxonomy."""
    result = []
    for cat in TAXONOMY:
        for sub in cat.subcategories:
            for topic in sub.topics:
                result.append((cat, sub, topic))
    return result


def topic_count() -> int:
    """Total number of topics in the taxonomy."""
    return sum(
        len(sub.topics)
        for cat in TAXONOMY
        for sub in cat.subcategories
    )


def category_stats() -> dict[str, dict[str, int]]:
    """Return {category_slug: {subcategories: N, topics: N}} for each category."""
    return {
        cat.slug: {
            "subcategories": len(cat.subcategories),
            "topics": sum(len(sub.topics) for sub in cat.subcategories),
        }
        for cat in TAXONOMY
    }
