#!/usr/bin/env python3
"""Assemble curation-map.json for the NH energy set (the judgment step).

Each entry: plain_topic (one plain sentence), theme (one of THEMES), and
relevance tier (core / adjacent / context). Context bills stay in the set for
audit but are excluded from headline numbers. Dispositions/stages are merged
in from dispositions.json (evidence-backed; nothing invented here).

The per-bill judgments live in ASSIGN below, keyed "YEAR:BILL" ->
(theme_key, relevance); plain topics come from OVERRIDES (hand-written for
the laws, vetoes, and every bill whose official title needs interpretation)
with a documented title-rewrite fallback for the rest - New Hampshire bill
titles are already descriptive gerund phrases, so the fallback turns the
official title into a plain past-tense sentence. This script validates the
set is fully covered and merges dispositions in.

OVERLAP RULE (documented): utility-property-tax / SWEPT-on-generators bills
(HB696 2025, SB277 2025, SB225 2023, HB410 2022, HB458 2024, SB584 2024) also
appear in the property-taxes packet; they are INCLUDED here from the energy
angle (theme T11), and the ratepayer-charge bills that packet excluded as
'utility regulation, not taxes' are core here. The reverse also holds: the
solar/renewable property-tax exemption bills the property-taxes packet
carried are kept here as T11 energy-taxation bills.

Run from repo root:
  python3 working/new-hampshire/energy/build-curation.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

W = Path("working/new-hampshire/energy")

THEMES = {
    "T1": "Electric rates, bills, and ratepayer costs",
    "T2": "Net metering, community power, and local generation",
    "T3": "Renewable generation and the RPS: solar, wind, hydro, biomass",
    "T4": "Utility regulation and governance: the PUC, the Department of Energy, and restructuring",
    "T5": "Grid infrastructure: transmission, storage, microgrids, reliability, and data",
    "T6": "Energy efficiency, weatherization, and fuel assistance",
    "T7": "Fuels: natural gas, propane, and heating oil",
    "T8": "Nuclear power",
    "T9": "Electric vehicles and charging infrastructure",
    "T10": "Climate, emissions, and RGGI",
    "T11": "Energy taxation and host-community revenue",
    "T12": "Energy facility siting and decommissioning",
    "CTX": "Context: not primarily an energy bill",
}

# "YEAR:BILL" -> (theme_key, relevance)
ASSIGN = {
    # ---------------- 2020 ----------------
    "2020:HB1116": ("T3", "core"), "2020:HB1146": ("T12", "core"),
    "2020:HB1210": ("T11", "core"), "2020:HB1215": ("T2", "adjacent"),
    "2020:HB1218": ("T2", "core"), "2020:HB1225": ("T2", "core"),
    "2020:HB1228": ("CTX", "context"), "2020:HB1229": ("T12", "core"),
    "2020:HB1237": ("T11", "adjacent"), "2020:HB1261": ("T6", "core"),
    "2020:HB1262": ("T2", "core"), "2020:HB1301": ("T5", "core"),
    "2020:HB1317": ("T6", "core"), "2020:HB1355": ("T6", "core"),
    "2020:HB1364": ("T3", "core"), "2020:HB1365": ("T6", "core"),
    "2020:HB1366": ("T3", "core"), "2020:HB1370": ("T3", "core"),
    "2020:HB1382": ("CTX", "context"), "2020:HB1396": ("T1", "adjacent"),
    "2020:HB1402": ("T2", "core"), "2020:HB1405": ("T5", "adjacent"),
    "2020:HB1406": ("T11", "core"), "2020:HB1418": ("T6", "adjacent"),
    "2020:HB1429": ("T5", "core"), "2020:HB1430": ("T5", "core"),
    "2020:HB1444": ("T10", "adjacent"), "2020:HB1478": ("T3", "core"),
    "2020:HB1479": ("T2", "adjacent"), "2020:HB1480": ("T6", "core"),
    "2020:HB1481": ("T2", "core"), "2020:HB1496": ("T10", "core"),
    "2020:HB1503": ("CTX", "context"), "2020:HB1515": ("T2", "core"),
    "2020:HB1518": ("T3", "core"), "2020:HB1519": ("T3", "core"),
    "2020:HB1535": ("T2", "adjacent"), "2020:HB1541": ("T12", "core"),
    "2020:HB1604": ("CTX", "context"), "2020:HB1612": ("CTX", "context"),
    "2020:HB1620": ("T9", "adjacent"), "2020:HB1631": ("T11", "core"),
    "2020:HB1635": ("CTX", "context"), "2020:HB1664": ("T10", "core"),
    "2020:HB1684": ("T6", "core"), "2020:HB412": ("T8", "core"),
    "2020:HB466": ("T2", "core"), "2020:HB568": ("T4", "core"),
    "2020:HB704": ("T8", "core"), "2020:HB715": ("T5", "core"),
    "2020:HB735": ("T10", "core"), "2020:SB122": ("T6", "core"),
    "2020:SB124": ("T3", "core"), "2020:SB13": ("T2", "core"),
    "2020:SB159": ("T2", "core"), "2020:SB166": ("T2", "core"),
    "2020:SB256": ("T5", "adjacent"), "2020:SB424": ("T11", "core"),
    "2020:SB427": ("T10", "adjacent"), "2020:SB429": ("T7", "adjacent"),
    "2020:SB462": ("T6", "adjacent"), "2020:SB463": ("T2", "core"),
    "2020:SB492": ("T3", "core"), "2020:SB494": ("T2", "adjacent"),
    "2020:SB495": ("T3", "adjacent"), "2020:SB497": ("T3", "core"),
    "2020:SB498": ("T5", "core"), "2020:SB499": ("T4", "core"),
    "2020:SB518": ("T2", "core"), "2020:SB530": ("T11", "core"),
    "2020:SB583": ("CTX", "context"), "2020:SB587": ("T6", "adjacent"),
    "2020:SB590": ("T10", "core"), "2020:SB594": ("CTX", "context"),
    "2020:SB603": ("T3", "adjacent"), "2020:SB610": ("T10", "core"),
    "2020:SB626": ("T12", "adjacent"), "2020:SB668": ("T3", "core"),
    "2020:SB692": ("T4", "adjacent"), "2020:SB73": ("T4", "adjacent"),
    "2020:SB75": ("T10", "core"),
    # ---------------- 2021 ----------------
    "2021:HB106": ("T2", "core"), "2021:HB148": ("T2", "core"),
    "2021:HB167": ("T2", "core"), "2021:HB168": ("T10", "adjacent"),
    "2021:HB169": ("T5", "adjacent"), "2021:HB172": ("T10", "core"),
    "2021:HB213": ("T3", "core"), "2021:HB225": ("T2", "core"),
    "2021:HB289": ("T12", "core"), "2021:HB294": ("T2", "core"),
    "2021:HB308": ("T5", "adjacent"), "2021:HB309": ("T3", "core"),
    "2021:HB315": ("T2", "core"), "2021:HB351": ("T6", "core"),
    "2021:HB358": ("T2", "adjacent"), "2021:HB371": ("T1", "core"),
    "2021:HB373": ("T7", "core"), "2021:HB376": ("T5", "core"),
    "2021:HB382": ("T1", "core"), "2021:HB394": ("T10", "core"),
    "2021:HB396": ("T3", "adjacent"), "2021:HB399": ("T6", "core"),
    "2021:HB407": ("T2", "core"), "2021:HB410": ("T11", "adjacent"),
    "2021:HB543": ("T8", "core"), "2021:HB549": ("T6", "core"),
    "2021:HB610": ("CTX", "context"), "2021:HB614": ("T3", "adjacent"),
    "2021:HB624": ("T12", "adjacent"), "2021:HB64": ("T11", "core"),
    "2021:HB80": ("T6", "core"), "2021:SB105": ("CTX", "context"),
    "2021:SB109": ("T2", "core"), "2021:SB113": ("T3", "core"),
    "2021:SB115": ("T10", "core"), "2021:SB151": ("T3", "core"),
    "2021:SB71": ("T10", "core"), "2021:SB73": ("T6", "adjacent"),
    "2021:SB78": ("T3", "core"), "2021:SB91": ("T3", "core"),
    # ---------------- 2022 ----------------
    "2022:HB1012": ("T4", "adjacent"), "2022:HB102": ("CTX", "context"),
    "2022:HB106": ("T2", "core"), "2022:HB1116": ("T2", "core"),
    "2022:HB1123": ("T9", "adjacent"), "2022:HB1148": ("T7", "adjacent"),
    "2022:HB1168": ("T7", "adjacent"), "2022:HB1191": ("CTX", "context"),
    "2022:HB1198": ("CTX", "context"), "2022:HB1248": ("T2", "core"),
    "2022:HB1250": ("T10", "core"), "2022:HB1258": ("T4", "core"),
    "2022:HB1270": ("T4", "adjacent"), "2022:HB1285": ("T5", "core"),
    "2022:HB1316": ("CTX", "context"), "2022:HB1317": ("CTX", "context"),
    "2022:HB1328": ("T4", "core"), "2022:HB1331": ("T5", "core"),
    "2022:HB1380": ("T2", "adjacent"), "2022:HB1419": ("T10", "adjacent"),
    "2022:HB1459": ("T3", "adjacent"), "2022:HB1464": ("T9", "core"),
    "2022:HB148": ("T2", "core"), "2022:HB1491": ("T7", "core"),
    "2022:HB1506": ("T6", "core"), "2022:HB1517": ("T3", "adjacent"),
    "2022:HB1596": ("T2", "core"), "2022:HB1599": ("T3", "core"),
    "2022:HB1611": ("T12", "core"), "2022:HB1621": ("T6", "core"),
    "2022:HB1628": ("T5", "adjacent"), "2022:HB1629": ("T2", "core"),
    "2022:HB1635": ("T2", "core"), "2022:HB1645": ("T3", "adjacent"),
    "2022:HB167": ("T2", "core"), "2022:HB1675": ("T9", "core"),
    "2022:HB169": ("T5", "adjacent"), "2022:HB172": ("T10", "core"),
    "2022:HB2023": ("T6", "core"), "2022:HB213": ("T3", "core"),
    "2022:HB308": ("T5", "adjacent"), "2022:HB376": ("T5", "core"),
    "2022:HB382": ("T1", "core"), "2022:HB394": ("T10", "core"),
    "2022:HB410": ("T11", "core"), "2022:HB543": ("T8", "core"),
    "2022:HB549": ("T6", "core"), "2022:HB614": ("T3", "adjacent"),
    "2022:HB624": ("T12", "core"), "2022:HR16": ("T8", "adjacent"),
    "2022:HR17": ("T10", "core"), "2022:SB113": ("T3", "core"),
    "2022:SB151": ("T3", "core"), "2022:SB256": ("T12", "core"),
    "2022:SB257": ("CTX", "context"), "2022:SB259": ("T2", "core"),
    "2022:SB261": ("T2", "core"), "2022:SB262": ("T2", "core"),
    "2022:SB264": ("T6", "adjacent"), "2022:SB265": ("T2", "core"),
    "2022:SB268": ("T3", "core"), "2022:SB269": ("T6", "core"),
    "2022:SB270": ("T2", "core"), "2022:SB271": ("T3", "core"),
    "2022:SB321": ("T2", "core"), "2022:SB370": ("T2", "adjacent"),
    "2022:SB417": ("T9", "adjacent"), "2022:SB424": ("T3", "core"),
    "2022:SB429": ("T12", "core"), "2022:SB440": ("T3", "core"),
    "2022:SB447": ("T9", "core"), "2022:SB448": ("T6", "adjacent"),
    # ---------------- 2023 ----------------
    "2023:HB111": ("T9", "core"), "2023:HB132": ("CTX", "context"),
    "2023:HB139": ("T2", "core"), "2023:HB142": ("T3", "core"),
    "2023:HB159": ("T1", "core"), "2023:HB161": ("T2", "core"),
    "2023:HB165": ("T3", "core"), "2023:HB166": ("T3", "core"),
    "2023:HB175": ("T6", "core"), "2023:HB176": ("T12", "core"),
    "2023:HB208": ("T10", "core"), "2023:HB211": ("T6", "core"),
    "2023:HB219": ("T4", "adjacent"), "2023:HB233": ("T3", "core"),
    "2023:HB234": ("T3", "core"), "2023:HB246": ("T3", "core"),
    "2023:HB251": ("T3", "adjacent"), "2023:HB263": ("T3", "adjacent"),
    "2023:HB281": ("T4", "core"), "2023:HB369": ("T6", "adjacent"),
    "2023:HB372": ("T10", "core"), "2023:HB381": ("T6", "core"),
    "2023:HB385": ("T2", "core"), "2023:HB418": ("T6", "core"),
    "2023:HB456": ("T9", "core"), "2023:HB458": ("T2", "core"),
    "2023:HB509": ("T3", "core"), "2023:HB523": ("T2", "core"),
    "2023:HB524": ("T10", "core"), "2023:HB558": ("T5", "core"),
    "2023:HB576": ("T6", "core"), "2023:HB605": ("T3", "core"),
    "2023:HB606": ("T9", "core"), "2023:HB609": ("T12", "core"),
    "2023:HB616": ("T3", "core"), "2023:HB622": ("T6", "core"),
    "2023:HB630": ("T6", "core"), "2023:HB631": ("T5", "adjacent"),
    "2023:HB633": ("T1", "core"), "2023:HB81": ("T7", "core"),
    "2023:HB92": ("T10", "adjacent"), "2023:HCR5": ("T10", "adjacent"),
    "2023:HR9": ("CTX", "context"), "2023:SB102": ("T7", "core"),
    "2023:SB113": ("T6", "core"), "2023:SB16": ("T5", "adjacent"),
    "2023:SB161": ("T2", "core"), "2023:SB165": ("T5", "core"),
    "2023:SB166": ("T5", "core"), "2023:SB167": ("T7", "core"),
    "2023:SB168": ("T2", "core"), "2023:SB186": ("CTX", "context"),
    "2023:SB191": ("T9", "core"), "2023:SB225": ("T11", "core"),
    "2023:SB40": ("T2", "core"), "2023:SB52": ("T9", "core"),
    "2023:SB54": ("T1", "core"), "2023:SB68": ("T2", "core"),
    "2023:SB69": ("T2", "core"), "2023:SB79": ("T2", "core"),
    "2023:SB96": ("T6", "core"),
    # ---------------- 2024 ----------------
    "2024:HB1161": ("T9", "adjacent"), "2024:HB1230": ("T6", "core"),
    "2024:HB1289": ("T5", "core"), "2024:HB1332": ("T9", "adjacent"),
    "2024:HB1333": ("T9", "adjacent"), "2024:HB1395": ("T7", "core"),
    "2024:HB1398": ("T2", "core"), "2024:HB1403": ("CTX", "context"),
    "2024:HB1416": ("T9", "adjacent"), "2024:HB1430": ("T1", "core"),
    "2024:HB1431": ("T5", "core"), "2024:HB1445": ("CTX", "context"),
    "2024:HB1464": ("T9", "core"), "2024:HB1465": ("T8", "core"),
    "2024:HB1471": ("CTX", "context"), "2024:HB1472": ("T9", "core"),
    "2024:HB1486": ("T10", "core"), "2024:HB1491": ("T7", "core"),
    "2024:HB1499": ("T10", "adjacent"), "2024:HB1510": ("T9", "core"),
    "2024:HB1543": ("CTX", "context"), "2024:HB1576": ("T4", "core"),
    "2024:HB1580": ("T9", "adjacent"), "2024:HB159": ("T1", "core"),
    "2024:HB1600": ("T2", "core"), "2024:HB1617": ("T1", "core"),
    "2024:HB1623": ("T4", "core"), "2024:HB1641": ("T3", "adjacent"),
    "2024:HB1644": ("T8", "core"), "2024:HB166": ("T3", "core"),
    "2024:HB1697": ("T10", "adjacent"), "2024:HB1700": ("CTX", "context"),
    "2024:HB1709": ("T10", "adjacent"), "2024:HB175": ("T6", "core"),
    "2024:HB176": ("T12", "core"), "2024:HB369": ("T6", "adjacent"),
    "2024:HB381": ("T6", "core"), "2024:HB456": ("T9", "core"),
    "2024:HB458": ("T11", "core"), "2024:HB509": ("T3", "core"),
    "2024:HB558": ("T5", "core"), "2024:HB606": ("T9", "core"),
    "2024:HB609": ("T12", "core"), "2024:HB616": ("T3", "core"),
    "2024:HB622": ("T5", "core"), "2024:HB631": ("T5", "adjacent"),
    "2024:HR27": ("T10", "adjacent"), "2024:HR30": ("CTX", "context"),
    "2024:SB165": ("T5", "core"), "2024:SB168": ("T2", "core"),
    "2024:SB191": ("T9", "core"), "2024:SB303": ("T3", "core"),
    "2024:SB307": ("T5", "core"), "2024:SB320": ("T4", "core"),
    "2024:SB365": ("T9", "adjacent"), "2024:SB386": ("T5", "core"),
    "2024:SB388": ("T4", "core"), "2024:SB391": ("T2", "core"),
    "2024:SB430": ("T9", "adjacent"), "2024:SB450": ("T5", "core"),
    "2024:SB451": ("T12", "core"), "2024:SB475": ("CTX", "context"),
    "2024:SB496": ("CTX", "context"), "2024:SB540": ("T5", "core"),
    "2024:SB550": ("T5", "core"), "2024:SB584": ("T11", "core"),
    "2024:SB595": ("T5", "adjacent"),
    # ---------------- 2025 ----------------
    "2025:HB106": ("T10", "adjacent"), "2025:HB123": ("T10", "adjacent"),
    "2025:HB169": ("T4", "adjacent"), "2025:HB174": ("CTX", "context"),
    "2025:HB182": ("T9", "adjacent"), "2025:HB189": ("T4", "core"),
    "2025:HB219": ("T3", "core"), "2025:HB224": ("T3", "core"),
    "2025:HB243": ("T9", "adjacent"), "2025:HB278": ("T10", "core"),
    "2025:HB306": ("T10", "core"), "2025:HB342": ("T6", "core"),
    "2025:HB441": ("CTX", "context"), "2025:HB450": ("T6", "core"),
    "2025:HB460": ("T5", "core"), "2025:HB504": ("T4", "core"),
    "2025:HB526": ("T10", "adjacent"), "2025:HB535": ("T4", "core"),
    "2025:HB537": ("T1", "core"), "2025:HB539": ("T1", "core"),
    "2025:HB541": ("T5", "core"), "2025:HB560": ("T10", "adjacent"),
    "2025:HB567": ("T3", "core"), "2025:HB575": ("T3", "core"),
    "2025:HB599": ("T6", "core"), "2025:HB627": ("CTX", "context"),
    "2025:HB654": ("T2", "core"), "2025:HB658": ("T7", "adjacent"),
    "2025:HB672": ("T4", "core"), "2025:HB674": ("T1", "core"),
    "2025:HB680": ("T1", "core"), "2025:HB681": ("T5", "core"),
    "2025:HB682": ("T3", "core"), "2025:HB690": ("T4", "core"),
    "2025:HB692": ("T5", "core"), "2025:HB696": ("T11", "core"),
    "2025:HB708": ("CTX", "context"), "2025:HB710": ("T8", "core"),
    "2025:HB715": ("CTX", "context"), "2025:HB723": ("T5", "core"),
    "2025:HB755": ("T4", "core"), "2025:HB759": ("T2", "core"),
    "2025:HB760": ("T1", "core"), "2025:HB761": ("T5", "core"),
    "2025:HB764": ("CTX", "context"), "2025:HB95": ("T4", "adjacent"),
    "2025:HB96": ("T6", "core"), "2025:HCR1": ("T10", "adjacent"),
    "2025:HCR2": ("T8", "core"), "2025:HCR4": ("T3", "core"),
    "2025:HR15": ("T4", "adjacent"), "2025:SB108": ("T4", "core"),
    "2025:SB228": ("T2", "core"), "2025:SB230": ("T5", "core"),
    "2025:SB232": ("T2", "core"), "2025:SB233": ("T5", "core"),
    "2025:SB234": ("T6", "core"), "2025:SB236": ("T6", "core"),
    "2025:SB237": ("T4", "core"), "2025:SB272": ("T9", "core"),
    "2025:SB277": ("T11", "core"), "2025:SB302": ("CTX", "context"),
    "2025:SB4": ("T6", "core"), "2025:SB65": ("T3", "adjacent"),
    # ---------------- 2026 ----------------
    "2026:CACR30": ("T4", "core"), "2026:HB1002": ("T11", "core"),
    "2026:HB1028": ("T3", "core"), "2026:HB1029": ("T4", "adjacent"),
    "2026:HB1074": ("CTX", "context"), "2026:HB1095": ("CTX", "context"),
    "2026:HB1169": ("T4", "adjacent"), "2026:HB1180": ("T6", "core"),
    "2026:HB1189": ("CTX", "context"), "2026:HB1205": ("T10", "adjacent"),
    "2026:HB1262": ("T7", "core"), "2026:HB1290": ("T5", "core"),
    "2026:HB1410": ("T9", "adjacent"), "2026:HB1432": ("T1", "core"),
    "2026:HB1440": ("T10", "adjacent"), "2026:HB1455": ("T5", "core"),
    "2026:HB1475": ("T1", "core"), "2026:HB1533": ("CTX", "context"),
    "2026:HB1534": ("T1", "core"), "2026:HB1535": ("T3", "core"),
    "2026:HB1536": ("T9", "adjacent"), "2026:HB1539": ("T1", "core"),
    "2026:HB1542": ("T3", "core"), "2026:HB1577": ("T5", "adjacent"),
    "2026:HB1594": ("T9", "core"), "2026:HB1614": ("CTX", "context"),
    "2026:HB1618": ("CTX", "context"), "2026:HB1620": ("T7", "core"),
    "2026:HB1666": ("T4", "core"), "2026:HB1703": ("CTX", "context"),
    "2026:HB1718": ("T2", "core"), "2026:HB1721": ("T3", "core"),
    "2026:HB1722": ("T1", "core"), "2026:HB1723": ("T5", "core"),
    "2026:HB1724": ("T1", "core"), "2026:HB1733": ("T1", "core"),
    "2026:HB1736": ("T4", "core"), "2026:HB1738": ("T10", "core"),
    "2026:HB1739": ("T5", "core"), "2026:HB1741": ("T5", "core"),
    "2026:HB1742": ("T2", "core"), "2026:HB1743": ("T5", "adjacent"),
    "2026:HB1745": ("T1", "core"), "2026:HB1748": ("T6", "core"),
    "2026:HB1775": ("T4", "core"), "2026:HB212": ("CTX", "context"),
    "2026:HB219": ("T3", "core"), "2026:HB221": ("T8", "core"),
    "2026:HB224": ("T3", "core"), "2026:HB246": ("CTX", "context"),
    "2026:HB266": ("T4", "core"), "2026:HB454": ("T7", "adjacent"),
    "2026:HB610": ("T1", "core"), "2026:HB707": ("CTX", "context"),
    "2026:HB723": ("T5", "core"), "2026:HR35": ("CTX", "context"),
    "2026:SB106": ("T2", "core"), "2026:SB112": ("T1", "core"),
    "2026:SB150": ("T9", "core"), "2026:SB428": ("CTX", "context"),
    "2026:SB440": ("T6", "core"), "2026:SB447": ("T8", "core"),
    "2026:SB449": ("T2", "core"), "2026:SB536": ("CTX", "context"),
    "2026:SB537": ("T4", "core"), "2026:SB538": ("T2", "core"),
    "2026:SB539": ("T3", "core"), "2026:SB540": ("T2", "core"),
    "2026:SB589": ("T5", "core"), "2026:SB590": ("T2", "core"),
    "2026:SB591": ("T4", "core"), "2026:SB592": ("T12", "adjacent"),
    "2026:SB597": ("T1", "core"), "2026:SB599": ("T3", "core"),
    "2026:SB628": ("T9", "core"),
}

# Hand-written plain topics for the bills whose official titles need
# interpretation (all laws, vetoes, near-misses, context false positives, and
# the spotlight bills). Everything else falls back to a title rewrite.
OVERRIDES = {
    # ---- context false positives (say why they are context) ----
    "2020:HB1228": "Climate Change Awareness Day proclamation; a commemorative day, not energy policy.",
    "2020:HB1382": "Solar Eclipse Day proclamation; 'solar' false positive.",
    "2020:HB1503": "PFAS air-emissions study; environmental health, not energy.",
    "2020:HB1604": "Agricultural registration for utility terrain vehicles; 'utility' false positive.",
    "2020:HB1612": "Utility terrain vehicle road rules; 'utility' false positive.",
    "2020:HB1635": "Climate education in schools; education policy (in the public-education packet's universe).",
    "2020:SB583": "Climate science in the adequate-education criteria; education policy.",
    "2020:SB594": "Speech-pathologist certification; 'electrical physical agent modalities' false positive.",
    "2021:HB610": "Banking-department licensing omnibus; 'transmission of consumer complaints' false positive (became law).",
    "2021:SB105": "Solar Eclipse Day proclamation; 'solar' false positive (became law).",
    "2022:HB102": "Business-tax combined-reporting study law; 'utilities' false positive (became law).",
    "2022:HB1191": "Electrical, plumbing, and gas-fitting work in small housing; trade licensing, not energy policy.",
    "2022:HB1198": "School 'culture and climate' rules; education policy ('climate' false positive).",
    "2022:HB1316": "eFoil electric surfboard rules; recreational watercraft (became law).",
    "2022:HB1317": "Marine-patrol reporting on electric watercraft; recreational boating.",
    "2022:SB257": "Municipal stormwater utilities; water infrastructure ('utility' false positive).",
    "2023:HB132": "Trailer tire disclosure by 'utility dealers'; motor-vehicle sales ('utility' false positive).",
    "2023:HR9": "American Marshall Plan resolution; 'climate resilience' inside a broader economic resolution.",
    "2023:SB186": "Low-income e-bike incentive program; personal mobility, not the energy system.",
    "2024:HB1403": "Temporary waivers for vehicle emission-control equipment; motor-vehicle inspection mechanics.",
    "2024:HB1445": "Electric bicycles, scooters, and unicycles; personal mobility devices.",
    "2024:HB1471": "Solar-eclipse school holiday; 'solar' false positive.",
    "2024:HB1543": "Personal electric vehicles (skateboards and similar); personal mobility devices.",
    "2024:HB1700": "Cloud-seeding and weather-modification ban; atmospheric intervention, not energy ('emissions' false positive).",
    "2024:HR30": "Climate education in schools resolution; education policy.",
    "2024:SB475": "Climate-controlled state library storage; facilities design ('climate' false positive).",
    "2024:SB496": "DHHS climate and health protection program; public health.",
    "2025:HB174": "Utility terrain vehicle weight limits; 'utility' false positive.",
    "2025:HB441": "Visible diesel-exhaust ('rolling coal') enforcement; motor-vehicle law.",
    "2025:HB627": "Telephone Lifeline program providers; telecommunications assistance (became law).",
    "2025:HB708": "Telephone area-code planning by the department of energy; telecommunications.",
    "2025:HB715": "Personal electric vehicles; personal mobility devices.",
    "2025:HB764": "Cloud-seeding and weather-modification ban; atmospheric intervention.",
    "2025:SB302": "Solid-waste facility siting board; waste policy borrowing the 'site evaluation committee' name.",
    "2026:HB1074": "OHRV and snowmobile fee remission; recreation ('fuel' fee text).",
    "2026:HB1095": "Utility terrain vehicle weight limits; 'utility' false positive (became law).",
    "2026:HB1189": "Solid-waste site evaluation committee; waste policy; interim study.",
    "2026:HB1533": "Electric bicycles and micromobility devices; personal mobility; interim study.",
    "2026:HB1614": "Coal-tar sealant restrictions; environmental product regulation ('coal' false positive); interim study.",
    "2026:HB1618": "Solar-radiation-modification and weather-modification ban; atmospheric intervention.",
    "2026:HB1703": "Bike-path registration fees including e-bikes; recreation.",
    "2026:HB212": "Waiver when a vehicle fails an emission-control test; motor-vehicle inspection mechanics.",
    "2026:HB246": "Conservation-district climate resilience grants; agricultural conservation.",
    "2026:HB707": "Created a solid-waste site evaluation committee; waste policy borrowing the SEC name (became law).",
    "2026:HR35": "Cloud-seeding prohibition resolution; atmospheric intervention (adopted by the House).",
    "2026:SB428": "Electricians' board term limits; occupational licensing (became law).",
    "2026:SB536": "Solid-waste facility site evaluation committee; waste policy; interim study.",
    # ---- laws and key bills, hand-written ----
    "2020:HB715": "Set the framework for electrical energy storage installed by customers, keeping storage behind the meter exempt from utility regulation (became law).",
    "2020:SB166": "Aligned competitive electricity supplier requirements with net energy metering rules (became law).",
    "2020:HB466": "Would have raised the customer-generator capacity cap for net metering eligibility; vetoed.",
    "2020:SB122": "Would have redirected expenditures from the RGGI energy efficiency fund; vetoed.",
    "2020:SB124": "Would have raised the minimum electric renewable portfolio standards; vetoed.",
    "2020:SB159": "Would have raised net energy metering limits for customer-generators (the 2020 5-megawatt bill); vetoed.",
    "2020:SB256": "Would have required emergency generators in certain senior housing - backup power for outages; interim study.",
    "2020:SB429": "Would have studied regional plastic-to-oil conversion plants - waste-derived fuel production.",
    "2021:HB289": "Added electrical storage facilities to the 'energy facility' definition for siting review (became law).",
    "2021:HB309": "Rewrote the computation of renewable energy credits and clarified renewable energy classes (became law).",
    "2021:HB315": "Let municipal host customer-generators serve political subdivisions through aggregation - groundwork for municipal net-metering projects (became law).",
    "2021:HB373": "Addressed state participation in low-carbon fuel standards programs (became law).",
    "2021:HB64": "Let renewable generation facility property be covered by voluntary payment-in-lieu-of-taxes agreements with municipalities (became law).",
    "2021:SB91": "The omnibus renewable energy and utilities law: net metering for low-income community solar, storage, and a bundle of utility-regulation updates (became law).",
    "2021:SB109": "Would have expanded municipal host customer-generator arrangements serving political subdivisions; died on the Senate table.",
    "2021:SB78": "Would have continually appropriated the renewable energy fund and clarified renewable classes; died between the chambers.",
    "2022:HB1148": "Ordered a report on whether local governments can restrict fuel types (the gas-ban preemption question) (became law).",
    "2022:HB1168": "Studied soil-conditioner law and expanded oil discharge cleanup fund reimbursement eligibility (became law).",
    "2022:HB1258": "Implemented the Department of Energy transition and defined 'municipal host' for limited electrical energy producers (became law).",
    "2022:HB1270": "Repealed the legislative oversight committee on the electric-services transformation (became law).",
    "2022:HB1285": "Amended the multi-use energy data platform statute - the shared electric and gas usage-data infrastructure (became law).",
    "2022:HB1331": "Set power line maintenance and construction rules (became law).",
    "2022:HB1491": "Strengthened natural gas transmission pipeline safety oversight (became law).",
    "2022:HB1599": "Clarified rules for customer-generators who sell their renewable energy certificates (became law).",
    "2022:HB169": "Created a commission to study removing unused utility poles after equipment transitions (became law).",
    "2022:HB2023": "Appropriated money for a state emergency fuel assistance program and a supplemental electric benefit during the 2022 price spike (became law).",
    "2022:HB410": "Created the commission to study how power generation and utility transmission property is assessed for taxes (became law).",
    "2022:HB543": "Created the commission to study nuclear power and nuclear reactor technology in New Hampshire (became law).",
    "2022:HB549": "Restructured the system benefits charge and the energy efficiency and sustainable energy board after the 2021 efficiency-order fight (became law).",
    "2022:SB256": "Created a committee to study replacing the site evaluation committee (became law).",
    "2022:SB261": "Expanded net metering participation (became law).",
    "2022:SB262": "Updated the rules for customer generators of electric energy (became law).",
    "2022:SB265": "Extended community power aggregation of electric customers to counties (became law).",
    "2022:SB268": "Set the approval path for power purchase agreements for Gulf of Maine offshore wind energy (became law).",
    "2022:SB270": "Created the low-moderate income community solar program - carve-outs in the renewable energy fund for LMI projects (became law).",
    "2022:SB271": "Addressed the Burgess BioPower biomass plant's obligations and cumulative reduction factor (became law).",
    "2022:SB321": "Expanded purchase of limited electrical energy producers' output in intrastate commerce, including storage systems (became law).",
    "2022:SB424": "Adjusted renewable energy classes and natural gas rules (became law).",
    "2022:SB429": "Amended site evaluation committee procedures (became law).",
    "2022:SB440": "Restructured the office of offshore wind industry development (became law).",
    "2022:HB624": "Would have moved site evaluation committee monitoring to the department of energy and eased hydro net metering; died between the chambers.",
    "2023:HB111": "Created a committee to study electric vehicle charging for residential renters (became law).",
    "2023:HB139": "Refined the 'municipal host' definition for limited electrical energy producers (became law).",
    "2023:HB142": "Would have supported continued operation of the Burgess Biopower plant; vetoed over its above-market subsidy structure.",
    "2023:HB211": "Required a department of energy report on the system benefits charge's effectiveness (became law).",
    "2023:HB219": "Cleaned up public utilities statutes (became law).",
    "2023:HB233": "Adjusted useful thermal energy's treatment under the renewable portfolio standard (became law).",
    "2023:HB281": "Repealed the least-cost integrated resource plan requirement for utilities, replacing it with distribution planning hooks (became law).",
    "2023:HB385": "Streamlined department of energy approval of community power aggregation plans (became law).",
    "2023:HB576": "Enabled municipal administration of commercial property assessed clean energy (C-PACE) districts (became law).",
    "2023:SB102": "Would have studied the Jones Act's effect on New Hampshire's heating and energy fuel market.",
    "2023:SB113": "Reworked the electric utility system benefits charge - legislative approval for increases (became law).",
    "2023:SB16": "Created the stakeholders' group on utility poles and attachments (became law).",
    "2023:SB161": "Expanded low-moderate income community solar projects and their renewable-fund set-aside (became law).",
    "2023:SB166": "Directed electric grid modernization: interconnection studies and the grid modernization advisory group (became law).",
    "2023:SB225": "Created the commission to study the assessing of power generation - the utility-property-tax question towns and generators fight over (became law).",
    "2023:SB40": "Opened net energy metering participation to small hydroelectric generators (became law).",
    "2023:SB52": "Set the regulatory framework for electric vehicle charging stations - who may resell electricity at the plug (became law).",
    "2023:SB54": "Authorized purchased power agreements for electric distribution utilities' default service (became law).",
    "2023:SB79": "Would have expanded customer-generator participation in net energy metering; vetoed.",
    "2023:SB96": "Rebuilt state energy performance contracting for efficiency in public buildings (became law).",
    "2024:HB1161": "Let the public school infrastructure fund pay for energy-efficient school buses (became law).",
    "2024:HB1431": "Required utility integrated distribution planning - the forward grid-investment plans (became law).",
    "2024:HB1465": "Ordered studies of nuclear energy technologies and renamed the offshore wind office the office of energy innovation (became law).",
    "2024:HB1600": "Refined community power aggregation by municipalities and counties (became law).",
    "2024:HB1623": "Rewrote the state energy policy statute (became law).",
    "2024:HB1697": "Set rules for forest carbon credit programs (became law).",
    "2024:HB458": "Re-established the commission studying how power generation is assessed for property taxes (became law).",
    "2024:HB558": "Ordered a department of energy microgrid study (became law).",
    "2024:HB609": "Amended the site evaluation committee's energy facility siting process (became law).",
    "2024:SB303": "Redirected how the department of energy uses renewable energy fund money (became law).",
    "2024:SB388": "Consolidated department of energy administration of utilities (became law).",
    "2024:SB391": "Eased electric grid interconnection for certain customer generators (became law).",
    "2024:SB430": "Created the council on electric vehicles, e-mobility devices, and lithium-ion battery impacts (became law).",
    "2024:SB451": "Created an expedited site evaluation committee track for certain applications (became law).",
    "2024:SB595": "Set the rates framework for pole attachments (became law).",
    "2025:HB123": "Defined pre-sequestration timber tax revenue and set a carbon-sequestration moratorium with a study commission (became law).",
    "2025:HB189": "Updated the 10-year state energy strategy and removed the energy efficiency and sustainable energy board references (became law).",
    "2025:HB243": "Gut-and-amend omnibus whose energy piece regulated electric-vehicle charging stations and weights-and-measures testing fees; died between the chambers.",
    "2025:HB342": "Would have enabled municipal adoption of energy efficient and clean energy districts; passed both chambers in different forms and died on a House non-concur.",
    "2025:HB504": "Restated the state energy policy (became law).",
    "2025:HB560": "Gut-and-amend omnibus carrying the carbon-sequestration moratorium package; died between the chambers.",
    "2025:HB658": "Raised the reimbursement cap from the oil discharge and disposal cleanup fund (became law).",
    "2025:HB672": "Allowed off-grid electricity providers to operate outside utility franchises (became law).",
    "2025:HB674": "Would have required non-wire alternatives review, time-of-use tariffs, and multi-year rate settings - the record's main rate-design package; died on the House table.",
    "2025:HB682": "Reorganized the offshore wind office into the office of energy innovation and restructured the port development commission (became law).",
    "2025:HB690": "Ordered the department of energy to investigate withdrawing from ISO-New England and other regional-market strategy options (became law).",
    "2025:HB696": "Standardized how utility property taxes and the statewide education property tax apply to electric generating facilities (became law).",
    "2025:HB710": "Would have enabled electric utilities to own and offer advanced nuclear resources; died between the chambers.",
    "2025:HB723": "Repealed the multi-use energy data platform before it launched; same bill as 2026 HB723 (carried across the biennium); see the 2026 record.",
    "2025:HCR1": "Resolution calling for full consideration of climate information in policymaking (adopted by the House; no Senate action recorded).",
    "2025:HCR2": "Resolution declaring advanced nuclear energy development in the state's best interest (adopted by the House; no Senate action recorded).",
    "2025:HCR4": "Resolution rejecting all offshore wind projects off New Hampshire and in the Gulf of Maine (adopted by the House; no Senate action recorded).",
    "2025:HR15": "Resolution urging a change in Federal Energy Regulatory Commission policy (adopted by the House).",
    "2025:SB108": "Updated department of energy statutes (became law).",
    "2025:SB228": "Would have eased the limitations on community customer generators; killed on the House floor.",
    "2025:SB232": "Clarified net metering terms and conditions (became law).",
    "2025:SB233": "Restructured the grid modernization advisory group (became law).",
    "2025:SB236": "Transferred the Electric Assistance Program - the ratepayer-funded low-income bill discount - to the department of energy (became law).",
    "2025:SB277": "Would have standardized utility property taxes and SWEPT on electric generating facilities (Senate version of HB696); killed at the Senate deadline.",
    "2025:SB4": "Enabled commercial property assessed clean energy and resiliency (C-PACER) financing (became law).",
    "2025:SB65": "Set stormwater management standards for solar arrays (became law).",
    "2026:HB1262": "Regulated home heating oil and propane contracts and sales - prepaid-contract consumer protection (became law).",
    "2026:HB1535": "Clarified eligible renewable energy classes under the renewable portfolio standard (became law).",
    "2026:HB1539": "Authorized utilities to issue AAA-rated securitization bonds for storm cost recovery and grid resilience (became law).",
    "2026:HB1577": "Allowed disclosure of utility customer data to municipalities for emergency response planning (became law).",
    "2026:HB1594": "Created a weight-based tiered registration fee schedule for electric and plug-in hybrid vehicles (became law).",
    "2026:HB1620": "Required removal of long-unused residential underground heating oil tanks (became law).",
    "2026:HB1718": "Authorized energy storage in connection with net metering (became law).",
    "2026:HB1723": "Required utilities and grid operators to assess high-voltage transformers' vulnerability to geomagnetic and electromagnetic events (became law).",
    "2026:HB1733": "Reformed the reconciliation of default electric service rates (became law).",
    "2026:HB1738": "Redirected ratepayer benefits from RGGI and addressed energy procurement and nuclear options (became law).",
    "2026:HB1742": "Protected customer-generators inadvertently enrolled in municipal or county aggregation programs (became law).",
    "2026:HB221": "Would have enabled electric utilities to own and offer advanced nuclear resources (the biennium's third try); vetoed, no override recorded as of collection.",
    "2026:HB266": "Restructured the department of energy (with an unrelated recording-consent rider) (became law).",
    "2026:HB610": "Created the residential ratepayers advisory board (became law).",
    "2026:HB723": "Repealed the multi-use energy data platform before it launched (became law, Chapter 28).",
    "2026:SB440": "Enabled municipal adoption of energy efficient and clean energy districts - the C-PACE expansion HB342 attempted (became law).",
    "2026:SB538": "Extended net metering eligibility terms for municipal energy projects (became law).",
    "2026:SB540": "Legalized plug-in solar generation systems for renters and homeowners (became law).",
    "2026:SB589": "Directed port electrification, microgrid development, and cybersecurity standards for energy and water systems (became law).",
    "2026:SB590": "Refined community power electric aggregation plans (became law).",
    "2026:SB591": "Allowed utility companies to own or build generation facilities - a step back from restructuring's divestiture (became law).",
    "2026:SB592": "Enabled regional conservation and energy resource planning for habitat strongholds (became law).",
    "2026:SB599": "Amended the renewable energy fund statute (became law).",
    "2026:HB1775": "Addressed utility ownership of natural gas and nuclear power generation facilities (became law).",
    "2026:HB1205": "Prohibited state and county lands from joining timber carbon-sequestration projects (became law).",
    "2026:HB1028": "Would have changed the definition of a renewable generation facility; killed in committee.",
    "2026:CACR30": "Would have made public utilities commissioners elected rather than appointed; killed on the House floor.",
}


def _rewrite(title: str, disp: str) -> str:
    t = title.strip().rstrip(".")
    t = re.sub(r"^\((?:New Title|Second New Title|Third New Title)\)\s*", "", t)
    t = t[0].lower() + t[1:]
    past = {
        "relative to ": "changed ", "establishing ": "created ",
        "prohibiting ": "prohibited ", "requiring ": "required ",
        "repealing ": "repealed ", "allowing ": "allowed ",
        "permitting ": "permitted ", "enabling ": "enabled ",
        "directing ": "directed ", "authorizing ": "authorized ",
        "creating ": "created ", "defining ": "defined ",
        "exempting ": "exempted ", "extending ": "extended ",
        "increasing ": "increased ", "decreasing ": "decreased ",
        "raising ": "raised ", "reducing ": "reduced ",
        "declaring ": "declared ", "updating ": "updated ",
        "clarifying ": "clarified ", "adopting ": "adopted ",
        "making ": "made ", "including ": "included ",
        "urging ": "urged ", "calling for ": "called for ",
        "proclaiming ": "proclaimed ", "restricting ": "restricted ",
        "reestablishing ": "re-established ", "establishes ": "created ",
        "to allow ": "allowed ",
    }
    verb = None
    for pre, rep in past.items():
        if t.startswith(pre):
            verb = rep + t[len(pre):]
            break
    if verb is None:
        verb = "addressed " + t
    if disp == "enacted":
        s = verb[0].upper() + verb[1:] + " (became law)."
    elif disp == "vetoed":
        s = "Would have " + verb + "; vetoed."
    elif disp == "interim_study":
        s = "Would have " + verb + "; interim study."
    elif disp == "passed":
        s = verb[0].upper() + verb[1:] + " (adopted resolution)."
    else:
        s = "Would have " + verb + "."
    return s


def main() -> None:
    disp = {f"{b['session_year']}:{b['bill_no']}": b
            for b in json.loads((W / "dispositions.json").read_text())["bills"]}
    missing = [k for k in disp if k not in ASSIGN]
    extra = [k for k in ASSIGN if k not in disp]
    assert not missing, f"bills without curation ({len(missing)}): {missing[:20]}"
    assert not extra, f"curation for unknown bills: {extra[:20]}"

    bills = []
    for key, (tkey, rel) in sorted(ASSIGN.items()):
        d = disp[key]
        if key in OVERRIDES:
            topic = OVERRIDES[key]
        elif d["disposition"] == "carryover_duplicate":
            base = _rewrite(d["title"], "other")
            base = base.replace("Would have ", "", 1)
            topic = (base[0].upper() + base[1:-1] +
                     f"; same bill as {d['session_year'] + 1} {d['bill_no']} (carried across the biennium); see that record.")
        else:
            topic = _rewrite(d["title"], d["disposition"])
        bills.append({
            "bill_key": key,
            "session_year": d["session_year"],
            "bill_no": d["bill_no"],
            "title": d["title"],
            "plain_topic": topic,
            "theme": THEMES[tkey],
            "relevance": rel,
            "disposition": d["disposition"],
            "stage": d["stage"],
            "roll_call_count": d["roll_call_count"],
        })
    from collections import Counter
    out = {
        "issue": "new-hampshire-04-energy",
        "note": ("Curation of the keyword-discovered set: one plain sentence, one "
                 "theme, and a relevance tier per bill. 'context' bills are kept "
                 "for audit but excluded from headline numbers; first-year records "
                 "of biennium carryover bills are counted once, in their decision "
                 "year."),
        "themes": list(THEMES.values()),
        "counts": {
            "total": len(bills),
            "by_relevance": dict(Counter(b["relevance"] for b in bills)),
            "policy_set": sum(1 for b in bills if b["relevance"] != "context"
                              and b["disposition"] != "carryover_duplicate"),
        },
        "bills": bills,
    }
    (W / "curation-map.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["counts"], indent=1))
    print(dict(Counter(b["theme"] for b in bills)))


if __name__ == "__main__":
    main()
