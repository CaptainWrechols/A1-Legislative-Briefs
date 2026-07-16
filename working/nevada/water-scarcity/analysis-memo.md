# Analysis Memo — Growth, Water Scarcity, and Long-Term Supply in Nevada

**Issue ID:** nevada-04-water-scarcity  
**State:** nevada  
**Sessions analyzed:** 2019, 2021, 2023, 2025  
**Impact lookback:** 20 years  
**Analyzed at:** 2026-07-16T20:30:00Z  
**Agent:** analyzer  
**Audience:** Data Formatter / Brief Writer (assembly viability — Version 0)

---

## 1. Scope and limitations

This analysis uses only local synthesis outputs and issue config: `working/nevada/water-scarcity/synthesis.json`, `synthesis-outline.md`, and `config/issues/nevada-water-scarcity.yaml`. Processed files under `sources/nevada/water-scarcity/processed/` were consulted only to resolve fact_id / count confirmations already reflected in synthesis (for example, which bill completes the four-bill multi-party sponsorship aggregate). No web scraping and no new bill search were performed.

The underlying dataset is a **keyword-discovered** Pass 1/Pass 2 set of **88 bills** (70 with `passes_water_title_filter=true`), not a proven exhaustive universe of all Nevada water bills [F-001, F-002, F-009]. Verification status was `PASS_WITH_WARNINGS` [F-003]. OpenStates detail enrichment was largely unavailable; NELIS was the primary bill-detail source [F-004, F-005].

Overall dispositions in the set: **Enacted=45, Failed=40, In Progress=3** [F-479]. Sample size (88 bills) is large enough for within-set pattern detection; patterns are **not** generalized beyond the keyword-discovered collection.

No interim Legislative Counsel Bureau memos or agency evaluation reports were present for this synthesis run [F-006]. Forum Phase 1/Phase 2 process materials were absent; `forum_process_input` is empty [F-007]. Forum process input is therefore not treated as legislative history.

---

## 2. Session-by-session summary

Metrics below use synthesis session summaries and milestone aggregates [F-010–F-013, F-474–F-477]. “Heard in committee” = origin-committee-seen; “reaching floor” = origin-chamber-floor-vote.

| Session | Introduced | Heard in committee | Reaching floor | Enacted | Failed / stalled | In progress | Multi-party sponsorship (in-session) |
|---------|------------|--------------------|----------------|---------|------------------|-------------|--------------------------------------|
| 2019 (80th) | 20 (17 water-title) | 20 | 14 | 13 | 7 | 0 | 3 (AB 233, AB 265, SB 236) |
| 2021 (81st) | 19 (14 water-title) | 19 | 9 | 9 | 8 | 2 (AJR 2, AJR 3) | 0 in sponsorship extracts |
| 2023 (82nd) | 23 (22 water-title) | 23 | 16 | 13 | 9 | 1 (SJR 3) | 0 in sponsorship extracts |
| 2025 (83rd) | 26 (17 water-title) | 26 | 13 | 10 | 16 | 0 | 1 (SB 276; completes F-478 aggregate of 4) |

**Supporting fact_ids:** session counts [F-010, F-011, F-012, F-013]; milestones [F-474, F-475, F-476, F-477]; bipartisan aggregate [F-478]; 2019 multi-party sponsorship [F-041, F-050, F-105]; 2021 in-progress [F-217, F-222]; 2023 in-progress [F-388]; SB 276 enacted [F-456].

### 2019 (80th Session)

Twenty keyword-discovered bills; 13 enacted and 7 failed [F-010, F-474]. Fourteen reached an origin-chamber floor vote [F-474]. Enacted examples include water conservation (AB 163) [F-033], groundwater basin use (SB 140) [F-083], well diversion changes (SB 236) [F-106], water-rights dedication (SB 250) [F-113], and DWR appropriations (SB 509) [F-147]. Failures include conjunctive-management-oriented AB 51 (origin committee) [F-061], Colorado River Commission services SB 76 (origin committee) [F-161], and drought-advisory-board SB 499 (origin committee) [F-134].

### 2021 (81st Session)

Nineteen bills; 9 enacted, 8 failed, 2 in progress [F-011, F-475]. Only 9 reached an origin-chamber floor vote [F-475] — the lowest floor-reach count among the four sessions. Enacted examples include conservation cooperative measures (AB 356) [F-191], temporary change applications (AB 6) [F-210], and South Fork Dam appropriation (AB 465) [F-200]. Failures clustered in origin committee, including water banks (AB 354) [F-185], groundwater boards (SB 149) [F-228], Colorado River Commission membership (AB 15) [F-173], and community/public water systems (SB 216, SB 238) [F-245, F-248]. AJR 2 and AJR 3 are recorded In Progress after enrollment/delivery to the Secretary of State [F-217, F-222].

### 2023 (82nd Session)

Twenty-three bills; 13 enacted, 9 failed, 1 in progress [F-012, F-476]. Sixteen reached origin-chamber floor votes [F-476]. Enacted examples include conservation revisions (AB 191, AB 220) [F-284, F-298], groundwater management plans (SB 113) [F-351], economic-development-linked water measure (AB 261) [F-306], and DWR appropriations/studies (SB 472, SB 473) [F-372, F-378]. Failures include groundwater basin assessments (SB 112) [F-347], groundwater conservation (SB 176) [F-358], groundwater boards (SB 180 — post-bicameral, no signed law) [F-362], and water-resource-plan grant appropriation (SB 102) [F-343]. SJR 3 (Colorado River protection urging) is In Progress after enrollment [F-388, F-391].

### 2025 (83rd Session)

Twenty-six bills — the largest session count in the set — with 10 enacted and 16 failed [F-013, F-477]. Thirteen reached origin-chamber floor votes [F-477]. Failed volume is the highest of the four sessions. Failures again concentrate in origin committee (e.g., AB 134 conservation [F-416], AB 109 [F-403]) with additional stalls at origin chamber (e.g., AB 363 groundwater boards [F-434]) and second-chamber committee (e.g., SB 31 vested-rights adjudication [F-459], SB 324 [F-461]). Enacted examples include AB 104, AB 132, AB 26 (dams), SB 276, and SB 36 [F-397, F-412, F-423, F-456, F-466].

---

## 3. Enacted law and 20-year impact

**Enacted counts by session:** 2019=13, 2021=9, 2023=13, 2025=10 [F-010–F-013, F-479].

For enacted bills with enactment more than two years before this analysis (2019, 2021, and 2023 sessions), synthesis was searched for agency reports, fiscal notes, or evaluation documents linked to those bills. The `interim_and_agency_documents` theme bucket is empty, and synthesis records that no interim LCB memos or agency evaluation reports were present under sources for this run [F-006].

Therefore:

- **IMPACT_DATA_NOT_AVAILABLE for** AB 163, AB 233, AB 62, AB 95, SB 140, SB 150, SB 232, SB 236, SB 250, SB 433, SB 507, SB 509, SB 547 **(2019)** [F-033, F-042, F-067, F-074, F-083, F-091, F-099, F-106, F-113, F-125, F-140, F-147, F-154; F-006].
- **IMPACT_DATA_NOT_AVAILABLE for** AB 146, AB 333, AB 356, AB 465, AB 6, SB 205, SB 33, SB 67, SB 98 **(2021)** [F-165, F-177, F-191, F-200, F-210, F-239, F-251, F-259, F-265; F-006].
- **IMPACT_DATA_NOT_AVAILABLE for** AB 19, AB 191, AB 20, AB 220, AB 261, AB 34, AB 470, AB 91, SB 113, SB 258, SB 472, SB 473, SB 59 **(2023)** [F-278, F-284, F-291, F-298, F-306, F-321, F-332, F-338, F-351, F-367, F-372, F-378, F-384; F-006].

2025 enactments fall inside the two-year window and were not scored for 20-year impact under Analyzer rules [F-393, F-397, F-407, F-412, F-423, F-450, F-456, F-466, F-470, F-473].

No post-enactment outcome claims are made. No speculation is offered on whether enacted measures reduced scarcity, changed consumptive use, or altered long-term supply.

---

## 4. Recurring policy approaches

Patterns below are labeled with certainty per Analyzer rules: **high** (3+ supporting facts), **medium** (2), **low** (1 — marked insufficient for strong conclusion).

### PAT-001 — Groundwater basin and groundwater management (certainty: **high**)

Observed across 2019–2025. Enacted examples include SB 140, AB 95, SB 236 (2019) and SB 113 groundwater management plans (2023) [F-083, F-074, F-106, F-351; topic extracts F-088, F-079, F-355]. Failed examples in 2023 include SB 112 (basin assessments) and SB 176 (groundwater conservation) [F-347, F-358].  
**Typical outcome:** mixed enacted and failed.  
This is an inference from [F-074, F-083, F-106, F-347, F-351, F-358], not a primary source fact that groundwater bills as a class always pass or fail.

### PAT-002 — Groundwater boards revisions (certainty: **high**)

SB 149 (2021), SB 180 (2023), and AB 363 (2025) all failed without enactment [F-228, F-362, F-434; topics F-230, F-365, F-435].  
**Typical outcome:** stalled / failed without enactment.

### PAT-003 — Water conservation statutory revisions (certainty: **high**)

AB 163 (2019), AB 356 (2021), AB 191 (2023), and AB 220 (2023) enacted [F-033, F-191, F-284, F-298]; AB 134 (2025) failed in origin committee [F-416].  
**Typical outcome:** often enacted in 2019–2023 within this set.

### PAT-004 — DWR / water-infrastructure appropriations (certainty: **high**)

SB 509, AB 465, SB 472, and SB 473 enacted [F-147, F-200, F-372, F-378]; SB 102 (grants for water resource plans) failed [F-343].  
**Typical outcome:** often enacted.

### PAT-005 — Colorado River Commission / Colorado River measures (certainty: **high**)

SB 76 and AB 15 failed in origin committee [F-161, F-173]; SJR 3 recorded In Progress after enrollment [F-388, F-391].  
**Typical outcome:** failed in origin committee or nonbinding resolution path.

### PAT-006 — State Engineer / NRS 533 appropriation framework (certainty: **high**)

NRS 533 appears in digests/titles of 26 bills; State Engineer is referenced for 41 bills [F-014, F-026, F-030]. Outcomes mix enactment and failure (e.g., AB 6 enacted [F-210]; AB 30, AB 51, AB 5, SB 31 failed [F-055, F-061, F-207, F-459]).  
**Typical outcome:** recurring cross-session statutory focus with mixed outcomes.

### PAT-007 — Community and public water system measures (certainty: **high**)

SB 216, SB 238, and AB 186 all failed in origin committee [F-245, F-248, F-275].  
**Typical outcome:** stalled in origin committee.

### PAT-008 — Water banks authorization (certainty: **low** — INSUFFICIENT FOR STRONG CONCLUSION)

Only AB 354 (2021) appears; it failed in origin committee [F-185, F-187].

### PAT-009 — Drought planning / advisory board creation (certainty: **low** — INSUFFICIENT FOR STRONG CONCLUSION)

Only SB 499 (2019) appears; it failed in origin committee [F-134, F-136].

Legal-framework context: NRS 534 (groundwater/wells) appears in 19 bills [F-015]; NRS 540 (planning/conservation) in 3 [F-021].

---

## 5. Stall points

Among **40** failed bills [F-479], synthesis milestone stall signals distribute as follows (counts from failed_or_stalled facts):

| Stall point | Count | Share of failed |
|-------------|-------|-----------------|
| Did not pass out of origin committee | 26 | 65% |
| Did not pass origin chamber | 7 | 17.5% |
| Did not clear second-chamber committee | 5 | 12.5% |
| Did not become signed law after bicameral passage | 2 | 5% |
| Executive veto | 0 | 0% |

**By session (failed bills only):**

- **2019:** origin committee 5; origin chamber 1; post-bicameral no signed law 1 [F-061, F-121, F-131, F-134, F-161, F-051, F-055].
- **2021:** origin committee 8 (all failed bills in session) [F-173, F-185, F-207, F-228, F-233, F-245, F-248, F-272].
- **2023:** origin committee 3; origin chamber 3; second-chamber committee 2; post-bicameral no signed law 1 [F-275, F-336, F-343, F-318, F-347, F-358, F-314, F-328, F-362].
- **2025:** origin committee 10; origin chamber 3; second-chamber committee 3 [F-403, F-416, F-420, F-428, F-432, F-437, F-442, F-444, F-454, F-463, F-434, F-439, F-448, F-452, F-459, F-461].

**Inference (not a primary source fact):** This is an inference from [failed_or_stalled facts listed above], not a primary source fact that origin committees are the sole institutional cause of non-passage. Floor and second-chamber stalls exist but are less frequent in this set. No veto-based failures appear in the failed bucket.

Floor-reach rates (origin-chamber floor vote / introduced) by session: 2019 14/20; 2021 9/19; 2023 16/23; 2025 13/26 [F-474–F-477].

---

## 6. Bipartisan signals

**Bipartisan sponsorship appeared on 4 of 88 bills** [F-478].

Identified bills:

| Bill | Session | Multi-party sponsorship fact | Disposition |
|------|---------|------------------------------|-------------|
| AB 233 | 2019 | F-041 | Enacted [F-042] |
| AB 265 | 2019 | F-050 | Failed [F-051] |
| SB 236 | 2019 | F-105 | Enacted [F-106] |
| SB 276 | 2025 | Counted in F-478 aggregate; confirmed via processed sponsor party labels to resolve the fourth bill in that count | Enacted [F-456] |

Many sponsorship records show party labels as “not recorded” (often committee sponsors), so absence of a multi-party signal does not prove single-party sponsorship for every bill. Vote yes/no count gaps also limit deeper bipartisan floor analysis [F-008].

---

## 7. Data gaps

What would be needed for stronger analysis:

1. **Exhaustive bill universe** (or documented completeness audit) beyond keyword discovery [F-001, F-002, F-003, F-009].
2. **OpenStates (or equivalent) full detail enrichment** for actions/votes where NELIS is incomplete [F-004, F-005].
3. **Agency evaluation reports, fiscal notes, and interim LCB memos** linked to enacted laws for 20-year impact claims [F-006].
4. **Complete vote tallies** where yes/no counts are missing [F-008].
5. **Consistent sponsor party labeling** for committee-sponsored and later-session bills to refine bipartisan metrics beyond the 4/88 aggregate [F-478].
6. **Forum Phase 1/Phase 2 materials** if process input is later needed — currently absent and correctly kept separate from legislative history [F-007].

Until those gaps close, impact assessment and full-universe generalization remain out of scope for Version 0.

---

## 8. Viability indicators for Version 0

Tractability assessment only. No lobbying recommendations.

- Historically, bills on groundwater boards have failed without enactment across the 2021, 2023, and 2025 sessions in this dataset [PAT-002; F-228, F-362, F-434].
- Historically, bills on water conservation statutory revisions have often enacted in 2019–2023, with at least one 2025 conservation bill failing in origin committee [PAT-003; F-033, F-191, F-284, F-298, F-416].
- Historically, bills on community and public water systems in this set have stalled in origin committee [PAT-007; F-245, F-248, F-275].
- Historically, bills on Colorado River Commission membership/services have stalled in origin committee in this set, while one Colorado River resolution followed a nonbinding enrollment path [PAT-005; F-161, F-173, F-388].
- Enacted legislation on water-related subjects in this keyword-discovered set is **common** in the last 4 sessions (45 of 88 bills enacted) [F-479, F-010–F-013].
- Enacted legislation on Division of Water Resources appropriations is **common** in the last 4 sessions within this dataset [PAT-004; F-147, F-200, F-372, F-378].
- Bipartisan sponsorship appeared on **4 of 88** bills [F-478].
- Data gaps prevent assessment of post-enactment policy impact for laws in the 20-year lookback window [F-006].
- Data gaps prevent assessment of exhaustive bill-universe coverage beyond this keyword-discovered set [F-001, F-002, F-003].
- Data gaps prevent assessment of water-banks tractability beyond a single failed bill [PAT-008; F-185].

Uncertainty flags: all patterns describe the keyword-discovered set only; low-certainty patterns (PAT-008, PAT-009) are insufficient for strong conclusion; stall-point committee dominance is an inference from milestone signals, not a causal finding.

---

## Completion checklist

- [x] `analysis.json` contains session metrics with fact references
- [x] `analysis-memo.md` has all 8 sections
- [x] No recommendations language
- [x] Impact claims flagged IMPACT_DATA_NOT_AVAILABLE where no agency/fiscal evaluation sources exist
- [x] Keyword-discovered / non-exhaustive dataset noted

---

> Analyzer finished. Run **Data Formatter**, then **Brief Writer**.
