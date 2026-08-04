#!/usr/bin/env python3
"""Assemble curation-map.json for the NH housing set (the judgment step).

Each entry: plain_topic (one plain sentence), theme (one of THEMES), and
relevance tier (core / adjacent / context). Context bills stay in the set for
audit but are excluded from headline numbers. Dispositions/stages are merged
in from dispositions.json (evidence-backed; nothing invented here).

Run from repo root:
  python3 working/new-hampshire/housing-affordability/build-curation.py
"""

from __future__ import annotations

import json
from pathlib import Path

W = Path("working/new-hampshire/housing-affordability")

THEMES = {
    "T1": "Building more homes: zoning and land use",
    "T2": "Accessory dwelling units (ADUs)",
    "T3": "State housing money and programs",
    "T4": "Renting: costs, fees, and rules",
    "T5": "Eviction and tenant protections",
    "T6": "Homelessness and housing stability",
    "T7": "Manufactured, tiny, and factory-built homes",
    "T8": "Land use boards, appeals, and the courts",
    "T9": "Housing studies, plans, and data",
    "CTX": "Context: not primarily housing",
}

# (plain_topic, theme_key, relevance)
E = {
    # ---------------- 2020 ----------------
    "2020:SB721": ("Would have replaced the new Housing Appeals Board with court review of planning board appeals.", "T8", "core"),
    "2020:SB735": ("Would have repealed the Housing Appeals Board in its first year.", "T8", "core"),
    "2020:HB1160": ("Would have let towns collect an occupancy fee from operators of local short-term room rentals.", "T4", "adjacent"),
    "2020:HB1247": ("Paused evictions and mortgage foreclosures for nonpayment during the COVID-19 emergency and set repayment rules.", "T5", "core"),
    "2020:HB1391": ("Would have banned housing discrimination against people with pets.", "T4", "core"),
    "2020:HB1582": ("Veterans omnibus that included programs helping veterans access housing.", "T3", "adjacent"),
    "2020:HB1629": ("Would have expanded training and procedural requirements for local zoning and planning boards.", "T8", "core"),
    "2020:SB726": ("Veterans services omnibus that included housing-access programs.", "T3", "adjacent"),
    # ---------------- 2021 ----------------
    "2021:HB15": ("Extended the rooms and meals tax to online booking facilitators; matched by rental search terms but not a housing bill.", "CTX", "context"),
    "2021:HB503": ("Wrote the state Council on Housing Stability into law (with unrelated telehealth provisions).", "T6", "core"),
    "2021:HB586": ("Would have required land-board training and created financial incentives for affordable housing development.", "T3", "core"),
    "2021:HB610": ("Banking omnibus that also created the New Hampshire housing and conservation planning program.", "T3", "adjacent"),
    "2021:SB126": ("Omnibus rewrite of landlord-tenant court proceedings.", "T5", "core"),
    "2021:SB152": ("Would have added $10 million to the Affordable Housing Fund and extended homelessness housing supports.", "T3", "core"),
    "2021:SB73": ("Would have added green building standards to the state's low- and moderate-income housing loan program.", "T3", "adjacent"),
    "2021:SB86": ("Omnibus planning and zoning bill: land-board training, housing data, and local process changes.", "T1", "core"),
    "2021:SB102": ("Property-tax omnibus that created community revitalization (79-E) tax relief for housing development.", "T3", "adjacent"),
    "2021:HB377": ("Let the state fire marshal exempt recovery houses from certain fire code requirements.", "T6", "adjacent"),
    "2021:HB286": ("Created a study committee on law enforcement's response to homelessness.", "T6", "adjacent"),
    "2021:HB284": ("Removed the deadline for restoring involuntarily merged residential lots.", "T1", "adjacent"),
    "2021:HB332": ("Gave planning boards 30 extra days to act on developments of regional impact.", "T8", "adjacent"),
    # ---------------- 2022 ----------------
    "2022:HB1291": ("Would have barred landlords from turning away tenants because they hold a housing voucher.", "T5", "core"),
    "2022:HB1662": ("Health-department omnibus that included an appropriation for housing expenses for homeless people.", "T6", "adjacent"),
    "2022:SB400": ("Would have required land-board training and created affordable-housing development incentives (retry of 2021 HB586).", "T3", "core"),
    "2022:SB415": ("Would have raised the rates the state pays homeless shelters.", "T6", "core"),
    "2022:HB1661": ("Omnibus bill whose land-use sections made significant changes to planning, zoning, and development rules.", "T1", "core"),
    "2022:HB1021": ("Restricted zoning regulation of land or structures used primarily for religious purposes.", "T1", "adjacent"),
    "2022:SB223": ("Changed the minimum size of recovery houses.", "T6", "adjacent"),
    "2022:SB334": ("Created a committee to study property blight in municipalities.", "T9", "adjacent"),
    # ---------------- 2023 ----------------
    "2023:HB111": ("Created a study committee on electric-vehicle charging for residential renters.", "T4", "adjacent"),
    "2023:HB112": ("Would have given tenants the right to notice before their multifamily building is sold.", "T5", "core"),
    "2023:HB401": ("Would have limited evictions based on an owner's intent to renovate.", "T5", "core"),
    "2023:HB469": ("Would have barred voucher discrimination by landlords (retry of 2022 HB1291).", "T5", "core"),
    "2023:HB477": ("Would have barred municipal inspections of owner-occupied units in multi-unit housing.", "T4", "adjacent"),
    "2023:HB567": ("Would have required advance notice of rent increases in certain residential rentals.", "T4", "core"),
    "2023:HB95": ("Would have let municipalities adopt their own rental practice regulations.", "T4", "core"),
    "2023:SB145": ("Housing Champion designation and grants for municipalities that welcome housing; enacted through the HB2 budget trailer.", "T3", "core"),
    "2023:SB203": ("Would have restructured the Board of Manufactured Housing's membership and expanded its jurisdiction.", "T7", "core"),
    "2023:HB42": ("Expanded land use board authority over homeowners' associations.", "T1", "adjacent"),
    "2023:HB296": ("Altered local authority over residential driveway permits.", "T1", "adjacent"),
    "2023:HB44": ("Would have allowed four homes by right on single-family lots served by municipal water and sewer.", "T1", "core"),
    "2023:SB231": ("Workforce and affordable housing appropriations (with a proposed historic housing tax credit); its appropriations were enacted through the HB2 budget trailer.", "T3", "core"),
    # ---------------- 2024 ----------------
    "2024:HB1199": ("Child-advocate services and funding for youth experiencing homelessness.", "T6", "adjacent"),
    "2024:HB1291": ("Would have allowed two accessory dwelling units per lot by right statewide.", "T2", "core"),
    "2024:HB1359": ("Changed who counts as an 'abutter' able to appeal zoning decisions.", "T8", "core"),
    "2024:HB1396": ("Would have barred municipal inspections of owner-occupied multi-unit housing (retry of 2023 HB477).", "T4", "adjacent"),
    "2024:HB1470": ("Would have created a study committee on a state low-income housing tax credit.", "T3", "adjacent"),
    "2024:HB1545": ("Would have directed surplus state property toward affordable housing.", "T3", "core"),
    "2024:SB318": ("Would have converted the manufactured-housing installation standards board into an advisory board.", "T7", "adjacent"),
    "2024:SB538": ("Would have streamlined local zoning procedures for residential housing.", "T1", "core"),
    "2024:HB1400": ("Housing omnibus: tax incentives for office-to-housing conversions, limits on local parking mandates, alternative parking, and faster local zoning amendments.", "T1", "core"),
    "2024:HB1361": ("Required municipalities to provide realistic opportunities for manufactured housing and rewrote manufactured-home subdivision rules.", "T7", "core"),
    "2024:HB1065": ("Extended the sprinkler exemption to three- and four-family homes and barred stricter local sprinkler codes.", "T1", "adjacent"),
    "2024:HB1202": ("Required the state to issue residential driveway permits within 60 days.", "T1", "adjacent"),
    "2024:SB406": ("Appropriated $2.5 million to raise the rates paid to homeless shelter programs.", "T6", "core"),
    "2024:HB1567": ("Loosened municipal zoning rules for home-based child care.", "T1", "adjacent"),
    "2024:SB454": ("Would have doubled the real estate transfer tax revenue flowing to the Affordable Housing Fund.", "T3", "core"),
    "2024:HB1399": ("Would have let municipalities permit two residential units in certain single-family zones.", "T1", "core"),
    # ---------------- 2025 ----------------
    "2025:CACR1": ("Constitutional amendment about a lieutenant governor; matched by search terms but unrelated to housing.", "CTX", "context"),
    "2025:HB119": ("Rental-car fleet registration; not a housing bill.", "CTX", "context"),
    "2025:HB123": ("Timber tax on carbon-sequestration land; not a housing bill.", "CTX", "context"),
    "2025:HB168": ("Added municipal public works facilities to what development impact fees may fund.", "T1", "adjacent"),
    "2025:HB229": ("Would have repealed the alternative (petition-based) procedure for adopting zoning ordinances.", "T1", "adjacent"),
    "2025:HB309": ("Made electronic rent payment optional so tenants cannot be forced to pay rent electronically.", "T4", "core"),
    "2025:HB351": ("Would have required at least 60 days' notice to evict tenants at will.", "T5", "core"),
    "2025:HB399": ("Created a commission to study New Hampshire's zoning enabling act.", "T9", "core"),
    "2025:HB425": ("Tax-exempt status while renting out facilities; a tax bill, not housing.", "CTX", "context"),
    "2025:HB434": ("Rental cars after crashes; not a housing bill.", "CTX", "context"),
    "2025:HB437": ("Cleaned up the process for clearing old undischarged mortgages from property titles.", "T3", "adjacent"),
    "2025:HB444": ("Would have given tenants notice rights before sale of a multi-family home (retry of 2023 HB112).", "T5", "core"),
    "2025:HB457": ("Limited how far local zoning can restrict dwelling units.", "T1", "core"),
    "2025:HB471": ("Would have created a commission on growth, traffic, and land use planning for certain towns.", "T9", "adjacent"),
    "2025:HB490": ("Would have shielded municipalities from liability when adopting policies addressing homelessness.", "T6", "adjacent"),
    "2025:HB530": ("Would have raised the real estate transfer tax share flowing to the Affordable Housing Fund.", "T3", "core"),
    "2025:HB558": ("Would have created a public county rent registry and banned algorithmic rent-setting software.", "T4", "core"),
    "2025:HB577": ("Broadened the definition of accessory dwelling units, including detached ADUs allowed by right.", "T2", "core"),
    "2025:HB628": ("Would have barred landlords from rejecting tenants with housing choice vouchers (2025 retry).", "T5", "core"),
    "2025:HB631": ("Permitted residential building in commercial zoning.", "T1", "core"),
    "2025:HB633": ("Created a legislative study committee on housing investment trusts.", "T9", "core"),
    "2025:HB685": ("Would have allowed manufactured housing by right in all residential zones.", "T7", "core"),
    "2025:HB71": ("School facilities/shelter omnibus; 'shelter' here is not housing policy.", "CTX", "context"),
    "2025:HB731": ("Expanded supportive housing options for people with developmental disabilities.", "T3", "core"),
    "2025:HB92": ("Required zoning-board and planning-board members to recuse for conflicts of interest.", "T8", "core"),
    "2025:SB113": ("Would have funded homeless services and homelessness prevention.", "T6", "core"),
    "2025:SB114": ("Would have funded community and transitional housing through community mental health centers.", "T6", "core"),
    "2025:SB166": ("Required notice before a manufactured-housing unit in a resident-owned community is sold.", "T7", "core"),
    "2025:SB173": ("Adjusted rules for residential property under low-income housing tax credit covenants.", "T3", "core"),
    "2025:SB179": ("Updated the membership and duties of the state Council on Housing Stability.", "T6", "core"),
    "2025:SB279": ("Would have created a Housing Champion business loan program.", "T3", "core"),
    "2025:SB55": ("Would have temporarily exempted qualifying housing projects from the land use change tax.", "T3", "core"),
    "2025:SB78": ("Would have changed the zoning board of adjustment appeal window.", "T8", "core"),
    "2025:SB81": ("Would have increased transfer-tax funding for the Affordable Housing Fund.", "T3", "core"),
    "2025:SB84": ("Same bill as 2026 SB84 (introduced 2025, carried over); counted once under 2026.", "T1", "core"),
    "2025:SB86": ("Would have adjusted New Hampshire Housing's affordable housing guarantee program.", "T3", "core"),
    # ---------------- 2026 ----------------
    "2026:HB1004": ("Would have exempted certain dwelling units from automatic sprinkler requirements.", "T1", "adjacent"),
    "2026:HB1005": ("Would have repealed the zoning enabling act study commission created in 2025.", "T9", "adjacent"),
    "2026:HB1006": ("Would have eased on-site parking requirements for accessory dwelling units.", "T2", "core"),
    "2026:HB1007": ("Would have revised manufactured housing rules.", "T7", "core"),
    "2026:HB1008": ("Would have modified innovative land use controls, requirements, and appeals.", "T1", "core"),
    "2026:HB1010": ("Enabled multi-family residential development on commercially zoned land.", "T1", "core"),
    "2026:HB1011": ("Would have repealed the 2025 statute limiting local zoning restrictions on dwelling units.", "T1", "core"),
    "2026:HB1012": ("Would have repealed the accessory dwelling unit statutes, including detached ADUs.", "T2", "core"),
    "2026:HB1016": ("Would have eliminated the requirement that municipalities allow manufactured housing.", "T7", "core"),
    "2026:HB1017": ("Would have changed accessory dwelling unit and workforce housing rules.", "T2", "core"),
    "2026:HB1021": ("Adjusted a notice date under the low-income housing tax credit assessment law.", "T3", "adjacent"),
    "2026:HB1026": ("Would have changed the statutory definition of manufactured housing.", "T7", "adjacent"),
    "2026:HB1042": ("Raised the cap on the housing finance authority's outstanding obligations.", "T3", "core"),
    "2026:HB1065": ("Would have enabled multi-family and mixed-use development in commercially zoned areas.", "T1", "core"),
    "2026:HB1079": ("Allowed accessory dwelling units within or attached to certain non-conforming structures.", "T2", "core"),
    "2026:HB1093": ("Charter schools and governmental land use exemptions; education-focused, not housing.", "CTX", "context"),
    "2026:HB1136": ("Would have changed accessory dwelling unit rules.", "T2", "core"),
    "2026:HB1143": ("Would have required remediation of mold in rental housing.", "T4", "core"),
    "2026:HB1145": ("Would have changed affordable housing investment fees.", "T3", "core"),
    "2026:HB1171": ("Would have protected tenants from eviction when Social Security payments are disrupted.", "T5", "core"),
    "2026:HB1181": ("Would have changed public hearing notice requirements for zoning board appeals.", "T8", "adjacent"),
    "2026:HB1195": ("Limited municipal zoning requirements for child day care providers.", "T1", "adjacent"),
    "2026:HB1196": ("Would have repealed the state Housing Champion designation and grant program.", "T3", "core"),
    "2026:HB1218": ("Would have required disclosure of rights and responsibilities when a mobile home in a park is sold.", "T7", "core"),
    "2026:HB1251": ("Would have restricted municipal downzoning inconsistent with existing neighborhood density.", "T1", "core"),
    "2026:HB1295": ("Would have changed eligibility requirements for charitable and nonprofit housing projects.", "T3", "adjacent"),
    "2026:HB1303": ("Tree-canopy zoning ordinances; environmental zoning, not housing.", "CTX", "context"),
    "2026:HB1336": ("Would have allowed exceptions to the residential security-deposit cap for applicants who fail standard screening.", "T4", "core"),
    "2026:HB1349": ("Would have exempted small or low-density communities from multi-family zoning requirements.", "T1", "core"),
    "2026:HB1371": ("Would have prohibited application fees for residential rental agreements.", "T4", "core"),
    "2026:HB1375": ("Would have limited landlords to one application fee per tenant every 12 months.", "T4", "core"),
    "2026:HB1405": ("Would have adjusted the housing finance authority's affordable housing guarantee program (retry of 2025 SB86).", "T3", "core"),
    "2026:HB1450": ("Would have set rules for designating and controlling shared facilities in rental properties.", "T4", "adjacent"),
    "2026:HB1497": ("Would have allowed replacing local land use board members for certain conduct.", "T8", "adjacent"),
    "2026:HB1499": ("Would have added grounds for eviction under the landlord-tenant statute (with an unrelated school-meals rider).", "T5", "core"),
    "2026:HB1525": ("Would have addressed zoning restrictions on dwelling-unit occupancy.", "T1", "core"),
    "2026:HB1540": ("Would have addressed municipal health ordinances and accessory dwelling units (with an unrelated barbershop rider).", "T2", "core"),
    "2026:HB1553": ("Would have regulated pet-related fees and pet rent in residential tenancies.", "T4", "core"),
    "2026:HB1588": ("Limited local parking mandates, enabled multifamily housing in commercial districts, created special assessment districts, and expanded the housing infrastructure grant program.", "T1", "core"),
    "2026:HB1598": ("Updated notice and court proceedings for tenants and landlords in evictions.", "T5", "core"),
    "2026:HB1612": ("Would have banned landlords' use of price-fixing websites, algorithms, or software for rents.", "T4", "core"),
    "2026:HB1613": ("Would have ordered a state report on expanding lending for housing serving people with disabilities.", "T9", "adjacent"),
    "2026:HB1619": ("Would have limited municipal land use regulation of property owners and repealed the workforce housing law.", "T1", "core"),
    "2026:HB1625": ("Would have required annual state reporting on accessory dwelling unit construction and use.", "T2", "adjacent"),
    "2026:HB1660": ("Would have enabled tax increment financing and municipal credit enhancement for priority housing development.", "T3", "core"),
    "2026:HB1661": ("Would have expanded the housing finance authority's community heroes homebuying program, with funding.", "T3", "core"),
    "2026:HB1662": ("Would have provided state loan guarantees for accessory dwelling unit financing.", "T2", "core"),
    "2026:HB1681": ("Defined tiny houses and yurts as innovative housing structures and set inspection and local approval rules.", "T7", "core"),
    "2026:HB1690": ("Would have changed how municipalities may assess development impact fees.", "T1", "adjacent"),
    "2026:HB1707": ("Would have taxed certain unoccupied properties and exempted low- and moderate-income buyers from the transfer tax.", "T3", "core"),
    "2026:HB1709": ("Omnibus on unlawfully present felons occupying or renting property; immigration enforcement, not housing policy.", "CTX", "context"),
    "2026:HB1711": ("Would have addressed governmental land uses.", "T1", "adjacent"),
    "2026:HB1713": ("Would have set zoning conformity and redevelopment standards.", "T1", "core"),
    "2026:HB1732": ("Would have addressed housing accessibility and voucher allocation in new multi-unit developments.", "T3", "adjacent"),
    "2026:HB1759": ("Would have set disqualification rules for local land use board members.", "T8", "adjacent"),
    "2026:HB1764": ("Would have set community workforce housing targets and created a revolving loan fund for workforce housing.", "T3", "core"),
    "2026:HB1786": ("Would have assessed luxury second homes to fund statewide housing development programs.", "T3", "core"),
    "2026:HB1802": ("Would have required training, testing, and certification of local land use board members, with funding.", "T8", "core"),
    "2026:HB1814": ("Would have created a 10-year strategic housing and infrastructure plan.", "T9", "core"),
    "2026:HB459": ("Would have limited acreage requirements where sewer infrastructure serves single-family lots.", "T1", "core"),
    "2026:HB465": ("Would have changed the housing opportunity zone (community revitalization) program.", "T3", "core"),
    "2026:HB519": ("Would have funded the Waypoint shelter for youth and young adults.", "T6", "core"),
    "2026:HB572": ("Would have created the Partners in Housing workforce-housing program in standalone statute; a version was enacted through HB2, the 2025 budget trailer.", "T3", "core"),
    "2026:HB604": ("Would have created a loan-forgiveness program for low-income homeowners building or converting ADUs.", "T2", "core"),
    "2026:HB65": ("Would have directed landlords to offer tenants rent-payment reporting to credit agencies.", "T4", "adjacent"),
    "2026:HR25": ("Resolution on Bhutanese refugee history; matched by 'eviction' but not housing policy.", "CTX", "context"),
    "2026:HR30": ("House resolution asserting that planning and zoning should remain municipal responsibilities.", "T1", "adjacent"),
    "2026:SB27": ("Rules for dwellings over water (boathouses); shoreline structures, not housing supply.", "CTX", "context"),
    "2026:SB419": ("Housing Champion program changes and Affordable Housing Fund appropriations.", "T3", "core"),
    "2026:SB435": ("Would have changed the zoning board of adjustment variance criteria.", "T8", "core"),
    "2026:SB436": ("Would have set zoning board of adjustment membership criteria.", "T8", "adjacent"),
    "2026:SB439": ("Municipal zoning for data centers; not residential housing.", "CTX", "context"),
    "2026:SB471": ("Would have changed affordable housing investment fees (companion to HB1145).", "T3", "core"),
    "2026:SB490": ("Created a task force on developing housing at Great Bay Community College and allowed use of vacant campus property for housing.", "T3", "core"),
    "2026:SB508": ("Would have changed the zoning board appeal period (retry of 2025 SB78).", "T8", "core"),
    "2026:SB82": ("Housing opportunity project extension and 'homes for homeland heroes' grant program.", "T3", "core"),
    "2026:SB84": ("Would have streamlined zoning procedures for residential housing (third attempt after 2024 SB538).", "T1", "core"),
    "2026:SB90": ("Would have allowed high-density residential development on land zoned for commercial use.", "T1", "core"),
}


def main() -> None:
    disp = {f"{b['session_year']}:{b['bill_no']}": b
            for b in json.loads((W / "dispositions.json").read_text())["bills"]}
    missing = [k for k in disp if k not in E]
    extra = [k for k in E if k not in disp]
    assert not missing, f"bills without curation: {missing}"
    assert not extra, f"curation for unknown bills: {extra}"

    bills = []
    for key, (topic, tkey, rel) in sorted(E.items()):
        d = disp[key]
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
        "issue": "new-hampshire-01-housing-affordability",
        "note": ("Curation of the keyword-discovered set: one plain sentence, one "
                 "theme, and a relevance tier per bill. 'context' bills are kept "
                 "for audit but excluded from headline numbers; 2025:SB84 is a "
                 "carryover duplicate of 2026:SB84 and is counted once."),
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
