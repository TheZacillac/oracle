"""Source document fetchers and parsers.

Oracle sources provide structured access to authoritative reference material
for training data generation. Each fetcher caches documents locally and
provides category-based access aligned with the taxonomy.

Source coverage:
- RFCs: IETF RFC Editor (all DNS/domain-related RFCs referenced in taxonomy)
- ICANN: Policy documents, agreements, GNSO/ccNSO outputs, SSAC/RSSAC advisories
- WIPO: UDRP/URS resources, case search, statistics, supplemental rules
- IANA: TLD list, DNS parameters, DNSSEC algorithms, RDAP bootstrap, EPP extensions
- CA/Browser Forum: Baseline Requirements, EV guidelines, CT, root store policies
- PSL: Public Suffix List (ICANN and private domains)
- Industry: M3AAWG, APWG, DNS-OARC, FIRST, protective DNS, threat intel
- Governance: IETF working groups, IGF/WSIS, RIRs, cybersecurity agencies
- DNS Software: BIND, Knot, NSD, PowerDNS, Unbound, CoreDNS, cloud DNS, debug tools
"""

from oracle.sources.cabforum import CaBrowserForumFetcher
from oracle.sources.dns_software import DnsSoftwareFetcher
from oracle.sources.governance import GovernanceFetcher
from oracle.sources.iana import IanaFetcher
from oracle.sources.icann import IcannFetcher
from oracle.sources.industry import IndustryFetcher
from oracle.sources.psl import PslFetcher
from oracle.sources.rfc import RfcFetcher, collect_taxonomy_rfcs

__all__ = [
    "RfcFetcher",
    "IcannFetcher",
    "IanaFetcher",
    "CaBrowserForumFetcher",
    "PslFetcher",
    "IndustryFetcher",
    "GovernanceFetcher",
    "DnsSoftwareFetcher",
    "collect_taxonomy_rfcs",
]
