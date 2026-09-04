# Independent fact-check — SC1 Slow Wage Growth Lege Brief v1.1 + childcare scan

Run 2026-09-04 at the user's request. Every check below was made against
**live external sources fetched fresh today** — not against the repo's own
mirrored data. Result: **all checks pass; zero discrepancies found.** One
nuance noted (below), no corrections required.

## 1. Bills: 31/31 verified against live official pages

Each cited bill's page at scstatehouse.gov was fetched live and checked for
the exact act number, the exact cited vote pair(s), the committee stop, and —
for bills the brief says never received a vote — the **absence** of any roll
call and act number on the page.

| Verified | Bills |
|---|---|
| Act numbers + vote pairs (enacted) | S533 (Act 209; 43–0, 104–4), S557 (Act 188; 42–0, 111–0), S1001 (Act 192; 45–0, 109–0), H3144 (Act 204; 105–1, 40–0), H3605 (Act 13; 114–0, 39–0), H3726 (Act 67; 102–3, 108–5, 41–2), H3863 (Act 142; 103–0, 43–0), H4766 (Act 194; 104–1, 40–0), S901 (Act 237; 41–0, 91–0), H4087 (Act 222; 45–0, 84–12), H3247 (Act 156; 107–0, 43–0), S700 (Act 190), S862 (Act 216), S595 (Act 52), H4023 (Act 81) |
| High-support non-enactments | H3368 (121–0 then Second Reading Failed 16–27), H3244 (106–9, 44–0, conference), H3576 (105–0), H3759 (100–3), S419 (40–4), H3348 (106–0, Senate Finance), S859 (42–0, House LCI), S946 (45–0, 105–0, conference) |
| No-vote assertions (page shows committee referral and **no** roll call, **no** act) | H4603, H3809, H3735, S147, H5794, H4394, S47, S770 |

Full machine results: `/tmp` run logged in this file's git commit; script
inline in commit history.

## 2. Votes double-checked on a second official system

The per-bill **vote-history database** (`votehistory.php`, a separate
system from the bill-history pages) was queried for four load-bearing bills.
It independently confirms: H3368 — Senate 2nd Reading **Failed 16–27**
(03/31/2026), House Passage **121–0**; S533 — 43–0 and 104–4; S946 — 45–0
and 105–0; S557 — 42–0 and 111–0. The same rows confirm chamber sizes
(vote totals of 124 and 46).

## 3. FY 2026-27 provisos verified on the official ratified Part IB

Fetched `sess126_2025-2026/appropriations2026/tap1b.htm` (the ratified/
enacted version) and confirmed verbatim: **117.155** (GP: Lead
Apprenticeship Agency, including the "SBTCE shall be recognized as the lead
agency" text), **25.4** (TEC: Critical Statewide Workforce Needs), **25.7**
(IDD Workforce Pilot), **25.8** (SC Workforce Competitiveness Initiative),
**117.138** (Employee Compensation — "increased by 2 percent"), the SC WINS
lottery line **$24,717,545**, **38.17** (DSS: Child Care Voucher), and
**38.28** (DSS: Childcare Provider Fraud).

## 4. Statutory and institutional facts

- **§6-1-130 local preemption** — live SC Code page confirms: "A political
  subdivision of this State may not establish, mandate, or otherwise require
  a minimum wage rate that exceeds the federal minimum wage."
- **No state minimum wage** — U.S. DOL's state minimum wage page states:
  "South Carolina: No state minimum wage law. Employers subject to the Fair
  Labor Standards Act must pay the current federal minimum wage of $7.25 per
  hour."
- **Federal floor $7.25** — DOL minimum-wage page, confirmed.
- **Federal youth wage** — DOL Fact Sheet #32, confirmed verbatim: "a youth
  minimum wage of not less than $4.25 an hour to employees who are under 20
  years of age during the first 90 consecutive calendar days after initial
  employment."
- **FLSA Section 14(c)** subminimum-wage certificates for workers with
  disabilities — DOL Workers with Disabilities page, confirmed.
- **Chamber sizes** — official member rosters count exactly **124 House**
  and **46 Senate** entries.
- **16 technical colleges** — confirmed by the SC Technical College System's
  own SC WINS materials ("one of the SC Technical College System's 16
  colleges").
- **SC WINS design** — the system's program page and procedure 3-2-306.1
  confirm: statewide scholarship for workforce-shortage/high-demand
  programs, **funded by lottery funds appropriated to the SBTCE**, up to
  $5,000/year — matching the brief's description; the procedure also
  confirms the DEW link (colleges must inform unemployment-insurance
  recipients about programs).

## 5. Third-party corroboration of the headline enactment

Able SC, Hire Me SC, and Disability Rights SC (advocacy organizations
independent of the legislature) confirm the S533 story as the brief tells
it: signed May 23, 2022; prohibits use of FLSA 14(c) subminimum wages;
merged with the Employment First Initiative Act **originally filed as
H3244** — corroborating the brief's H3244-died-in-conference →
S533-carried-it narrative.

**Nuance noted (no correction needed):** S533 included a task-force
transition that phased out existing subminimum wages by **August 1, 2024**.
The brief's statement that S533 "banned subminimum pay" is accurate; the
phase-out timing is an implementation detail available in the act's text if
reviewers want it added.

## Limitations

- LegiScan (bot-blocked), Open States (JS/API key), and FastDemocracy were
  not reachable from this environment, so aggregator cross-checks were
  substituted with: fresh fetches of official pages, a structurally separate
  official endpoint (the vote-history database), U.S. DOL pages, the SC
  Technical College System's own documents, and third-party advocacy
  sources.
- Committee vote tallies cannot be verified anywhere because South Carolina
  does not publish them — consistent with the brief's own statement, which
  is itself the claim.
