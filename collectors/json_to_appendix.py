#!/usr/bin/env python3
"""Convert bills-combined.json into appendix-a-bills.md Markdown table."""

from __future__ import annotations

import json
from pathlib import Path

INPUT = Path("sources/nevada/water-scarcity/processed/bills-combined.json")
OUTPUT = Path("briefs/nevada/water-scarcity/version-0/appendix-a-bills.md")
ISSUE_TITLE = "Growth, Water Scarcity, and Long-Term Supply in Nevada"
STATE = "nevada"


def disposition(bill: dict) -> str:
    actions = bill.get("actions") or []
    if not actions:
        return "Unknown"
    text = " ".join((a.get("description") or "").lower() for a in actions)
    if any(word in text for word in ("enacted", "signed", "chaptered", "became law")):
        return "Enacted"
    if "veto" in text:
        return "Vetoed"
    if any(word in text for word in ("failed", "defeated", "died")):
        return "Failed"
    return "In Progress"


def sponsors(bill: dict) -> tuple[str, str]:
    primary = ""
    cosponsors: list[str] = []
    for sponsorship in bill.get("sponsorships") or []:
        name = sponsorship.get("name") or ""
        if sponsorship.get("primary"):
            primary = name
        else:
            cosponsors.append(name)
    return primary, ", ".join(cosponsors)


def bill_url(bill: dict) -> str:
    return bill.get("openstates_url") or bill.get("source_url") or "—"


def source_key(bill: dict) -> str:
    if bill.get("source") == "nevada_nelis":
        return "S-NELIS"
    return "S-OPENSTATES"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    bills = json.loads(INPUT.read_text(encoding="utf-8"))

    lines = [
        "# Appendix A: Bills Related to Water Scarcity in Nevada",
        f"**Issue:** {ISSUE_TITLE}",
        f"**State:** {STATE}",
        f"**Record count:** {len(bills)}",
        "",
        "| Session | Bill Number | Title | Primary Sponsor | Co-Sponsors | "
        "First Action Date | Last Action Date | Last Action Description | "
        "Final Disposition | Source URL | Source Key |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]

    for bill in sorted(bills, key=lambda b: (str(b.get("session", "")), str(b.get("identifier", "")))):
        actions = bill.get("actions") or []
        first_date = actions[0].get("date", "—") if actions else "—"
        last_date = actions[-1].get("date", "—") if actions else "—"
        last_desc = (actions[-1].get("description") or "—").replace("|", "/") if actions else "—"
        primary, cos = sponsors(bill)
        title = (bill.get("title") or "").replace("|", "/")
        lines.append(
            "| {session} | {identifier} | {title} | {primary} | {cos} | {first} | {last} | "
            "{desc} | {disp} | {url} | {skey} |".format(
                session=bill.get("session", "—"),
                identifier=bill.get("identifier", "—"),
                title=title,
                primary=primary or "—",
                cos=cos or "—",
                first=first_date,
                last=last_date,
                desc=last_desc,
                disp=disposition(bill),
                url=bill_url(bill),
                skey=source_key(bill),
            )
        )

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
