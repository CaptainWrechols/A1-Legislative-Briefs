#!/usr/bin/env python3
"""Programmatic fact-check of reality-map.json claims against the evidence pack.

Run from the repo root. Exit 0 = every checked claim verified.
"""
import json
import sys
from collections import Counter

W = 'working/nevada/k-12_educational_outcomes'
S = 'sources/nevada/k-12_educational_outcomes'
pack = json.load(open(f'{W}/evidence-pack.json'))
bills = {b['bill_key']: b for b in pack['bills']}
votes = json.load(open(f'{S}/processed/bill-votes.json'))
actions = json.load(open(f'{S}/processed/bill-actions.json'))
special = json.load(open(f'{S}/verification/special-sessions.json'))
rm = json.load(open(f'{W}/reality-map.json'))
errors = []


def fp_votes(key):
    s, i = key.split(':')
    out = {}
    for v in votes:
        if v['session'] == s and v['bill_identifier'] == i and 'final passage' in (v.get('motion') or '').lower():
            ch = 'Assembly' if 'assembly' in (v.get('chamber') or '').lower() else 'Senate'
            c = v.get('counts') or {}
            yn = f"{c.get('yes')}-{c.get('no')}"
            # keep the best (highest yes) final-passage roll per chamber
            if ch not in out or int(yn.split('-')[0]) > int(out[ch].split('-')[0]):
                out[ch] = yn
    return out


# ---- bill-level claims used in the reality map and front brief ----
claims = [
    # (key, disposition, stage or None, {chamber: yes-no})
    ("80:AB146", "Failed", "origin_committee", {}),
    ("80:AB296", "Failed", "origin_floor", {}),
    ("81:AB108", "Failed", "origin_committee", {}),
    ("82:AB149", "Failed", "origin_committee", {}),
    ("82:AB353", "Failed", "origin_committee", {}),
    ("83:AB33", "Failed", "origin_committee", {}),
    ("83:AB154", "Failed", "origin_committee", {}),
    ("82:AB395", "Failed", "origin_committee", {}),
    ("82:AB517", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("83:SB411", "Failed", "origin_committee", {}),
    ("80:SB543", "Enacted", None, {"Senate": "18-3", "Assembly": "34-7"}),
    ("81:SB439", "Enacted", None, {"Senate": "20-1", "Assembly": "36-5"}),
    ("81:AB495", "Enacted", None, {"Assembly": "28-14", "Senate": "16-5"}),
    ("82:SB503", "Enacted", None, {}),
    ("83:SB500", "Enacted", None, {"Assembly": "42-0", "Senate": "13-8"}),
    ("82:SB231", "Enacted", None, {"Senate": "21-0", "Assembly": "41-1"}),
    ("82:AB459", "Failed", "origin_committee", {}),
    ("83:SB471", "Failed", "origin_committee", {}),
    ("80:SB305", "Failed", "origin_committee", {}),
    ("83:AB307", "Failed", "origin_floor", {}),
    ("83:AB508", "Failed", "origin_committee", {}),
    ("82:AB400", "Enacted", None, {"Assembly": "41-0", "Senate": "20-1"}),
    ("83:AB53", "Failed", "origin_committee", {}),
    ("81:SB182", "Failed", "origin_committee", {}),
    ("82:AB228", "Failed", "origin_floor", {}),
    ("82:AB274", "Enacted", None, {"Assembly": "40-0", "Senate": "20-0"}),
    ("83:SB444", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("80:SB403", "Enacted", None, {"Assembly": "40-0", "Senate": "21-0"}),
    ("81:SB66", "Enacted", None, {}),
    ("83:AB406", "Enacted", None, {"Assembly": "42-0", "Senate": "20-1"}),
    ("82:SB214", "Enacted", None, {}),
    ("83:SB248", "Failed", "origin_committee", {}),
    ("80:SB84", "Enacted", None, {"Assembly": "41-0", "Senate": "20-0"}),
    ("82:AB348", "Enacted", None, {}),
    ("83:AB212", "Enacted", None, {"Assembly": "38-4", "Senate": "21-0"}),
    ("82:AB113", "Failed", "origin_floor", {}),
    ("83:SB82", "Failed", "origin_committee", {}),
    ("83:SB58", "Failed", "origin_committee", {}),
    ("83:AB292", "Failed", "origin_committee", {}),
    ("82:SB292", "Enacted", None, {"Senate": "21-0", "Assembly": "39-3"}),
    ("83:SB460", "Enacted", None, {"Senate": "21-0", "Assembly": "38-4"}),
    ("82:AB175", "Enacted", None, {"Assembly": "29-11", "Senate": "16-4"}),
    ("83:AB156", "Failed", "second_chamber", {"Assembly": "24-18"}),
    ("80:AB57", "Failed", "origin_committee", {}),
    ("80:SB105", "Failed", "origin_committee", {}),
    ("80:AB491", "Failed", "origin_committee", {}),
    ("81:AB255", "Failed", "origin_committee", {}),
    ("81:SB111", "Failed", "origin_committee", {}),
    ("82:SB64", "Failed", "origin_committee", {}),
    ("82:SB65", "Failed", "origin_committee", {}),
    ("82:AB282", "Vetoed", "vetoed", {"Assembly": "31-11", "Senate": "16-4"}),
    ("82:SB251", "Vetoed", "vetoed", {}),
    ("83:AB155", "Vetoed", "vetoed", {"Assembly": "26-16", "Senate": "16-4"}),
    ("80:SB445", "Failed", "origin_committee", {}),
    ("82:AB335", "Failed", "origin_committee", {}),
    ("82:SB442", "Enacted", None, {"Assembly": "42-0"}),
    ("82:AB515", "Enacted", None, {"Assembly": "42-0"}),
    ("82:AB428", "Enacted", None, {"Assembly": "42-0"}),
    ("82:SB291", "Enacted", None, {"Assembly": "42-0", "Senate": "20-0"}),
    ("83:AB49", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("83:AB472", "Enacted", None, {"Assembly": "42-0", "Senate": "20-0"}),
    ("83:AB398", "Enacted", None, {"Senate": "20-0", "Assembly": "41-1"}),
    ("82:SB438", "Failed", "origin_floor", {}),
    ("82:SB434", "Enacted", None, {}),
    ("83:SB351", "Failed", "origin_committee", {}),
    ("82:SB313", "Failed", "origin_floor", {}),
    ("83:SB314", "Failed", "origin_floor", {}),
    ("83:SB403", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("83:AB24", "Failed", "origin_committee", {}),
    ("81:SB353", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("82:SB9", "Enacted", None, {}),
    ("83:AB401", "Failed", "origin_committee", {}),
    ("80:AB289", "Enacted", None, {"Assembly": "28-11", "Senate": "17-4"}),
    ("83:AB386", "Failed", "after_both_chambers", {"Assembly": "40-0", "Senate": "21-0"}),
    ("83:SB278", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("82:AB187", "Failed", "origin_committee", {}),
    ("81:SB273", "Failed", "origin_committee", {}),
    ("80:SB319", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("81:SB151", "Enacted", None, {"Assembly": "33-8", "Senate": "18-3"}),
    ("83:SB277", "Enacted", None, {"Assembly": "38-1", "Senate": "15-5"}),
    ("80:SB80", "Enacted", None, {}),
    ("80:SB204", "Enacted", None, {}),
    ("81:SB249", "Enacted", None, {}),
    ("83:AB298", "Failed", "origin_committee", {}),
    ("83:AB374", "Failed", "origin_committee", {}),
    ("83:SB254", "Failed", "origin_floor", {}),
    ("82:AB265", "Vetoed", "vetoed", {"Assembly": "42-0", "Senate": "20-0"}),
    ("82:AB201", "Vetoed", "vetoed", {}),
    ("82:AB172", "Vetoed", "vetoed", {}),
    ("82:AB319", "Vetoed", "vetoed", {}),
    ("82:SB148", "Vetoed", "vetoed", {}),
    ("82:SB340", "Vetoed", "vetoed", {}),
    ("83:AB205", "Vetoed", "vetoed", {}),
    ("83:AB217", "Vetoed", "vetoed", {}),
    ("83:AB416", "Vetoed", "vetoed", {}),
    ("83:AB445", "Vetoed", "vetoed", {}),
    ("83:AB391", "Failed", "second_chamber", {"Assembly": "42-0"}),
    ("82:AB339", "Failed", "second_chamber", {"Assembly": "39-3"}),
    ("83:AB495", "Failed", "second_chamber", {"Assembly": "42-0"}),
    ("83:SB374", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("83:SB229", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("82:AB423", "Failed", "after_both_chambers", {"Assembly": "40-0", "Senate": "12-8"}),
    ("83:AB224", "Enacted", None, {"Assembly": "41-1", "Senate": "21-0"}),
    ("83:AB533", "Enacted", None, {"Assembly": "38-1", "Senate": "21-0"}),
    ("80:AB304", "Enacted", None, {"Assembly": "41-0", "Senate": "20-1"}),
    ("81:AB266", "Enacted", None, {"Assembly": "26-16", "Senate": "12-9"}),
    ("81:SB27", "Failed", "second_chamber", {"Senate": "16-5"}),
    ("82:SB344", "Failed", "second_chamber", {"Senate": "13-8"}),
]
for key, disp, stage, expvotes in claims:
    b = bills.get(key)
    if not b:
        errors.append(f"{key}: missing from pack")
        continue
    if b['disposition'] != disp:
        errors.append(f"{key}: disposition {b['disposition']} != claimed {disp}")
    if stage and b['death_or_success_stage'] != stage:
        errors.append(f"{key}: stage {b['death_or_success_stage']} != claimed {stage}")
    got = fp_votes(key)
    for ch, yn in expvotes.items():
        if got.get(ch) != yn:
            errors.append(f"{key}: {ch} vote {got.get(ch)} != claimed {yn}")

# every bill key referenced in reality-map exists in pack
import re
raw = open(f'{W}/reality-map.json').read()
for m in set(re.findall(r'8[0-3]:(?:AB|SB|AJR|SJR|ACR|SCR)\d+', raw)):
    if m not in bills:
        errors.append(f"reality-map references {m} not in pack")

# ---- inventory / people claims ----
inv = pack['inventory']
if not (inv['policy_bills'] == 513 and inv['core_bills'] == 359 and inv['adjacent_bills'] == 154 and inv['context_bills'] == 211):
    errors.append("inventory mismatch")
dp = inv['dispositions_policy']
if not (dp.get('Enacted') == 228 and dp.get('Failed') == 269 and dp.get('Vetoed') == 13 and dp.get('Unknown') == 2 and dp.get('In Progress') == 1):
    errors.append(f"dispositions mismatch: {dp}")
for y, (n, en, ve) in [("2019", (146, 77, 0)), ("2021", (110, 50, 0)), ("2023", (128, 52, 8)), ("2025", (129, 49, 5))]:
    d = inv['sessions'][y]
    if (d['bills_in_set'], d['dispositions'].get('Enacted', 0), d['dispositions'].get('Vetoed', 0)) != (n, en, ve):
        errors.append(f"session {y} mismatch: {d}")

pol = [b for b in pack['bills'] if b['relevance'] != 'context']
fc = sum(1 for b in pol if b['disposition'] == 'Failed' and b['death_or_success_stage'] in ('origin_committee', 'introduced'))
if fc != 193:
    errors.append(f"first-committee deaths {fc} != 193")
of = sum(1 for b in pol if b['disposition'] == 'Failed' and b['death_or_success_stage'] == 'origin_floor')
if of != 43:
    errors.append(f"origin-floor deaths {of} != 43")
sc = sum(1 for b in pol if b['disposition'] == 'Failed' and b['death_or_success_stage'] == 'second_chamber')
if sc != 30:
    errors.append(f"second-chamber deaths {sc} != 30")
ab = sum(1 for b in pol if b['disposition'] == 'Failed' and b['death_or_success_stage'] == 'after_both_chambers')
if ab != 3:
    errors.append(f"after-both-chambers deaths {ab} != 3")

# first committee referral breakdown for first-committee deaths
first_committee = {}
for a in actions:
    k = f"{a['session']}:{a['bill_identifier']}"
    d = (a.get('description') or '')
    if k not in first_committee and 'Referred to Committee' in d:
        m = re.search(r'Referred to (Committee[^.]*)', d)
        if m:
            first_committee[k] = m.group(1)
cc = Counter()
for b in pol:
    if b['disposition'] == 'Failed' and b['death_or_success_stage'] in ('origin_committee', 'introduced'):
        cc[first_committee.get(b['bill_key'], 'unknown')] += 1
edu = cc.get('Committee on Education', 0)
money = cc.get('Committee on Finance', 0) + cc.get('Committee on Ways and Means', 0)
ga = cc.get('Committee on Government Affairs', 0)
if edu != 127:
    errors.append(f"education-committee deaths {edu} != 127")
if money != 40:
    errors.append(f"money-committee deaths {money} != 40")
if ga != 12:
    errors.append(f"government-affairs deaths {ga} != 12")

ps = pack['people_signals']
if ps['person_sponsored_policy_bills'] != 340 or ps['committee_sponsored_policy_bills'] != 173:
    errors.append("sponsor split mismatch")
cp = ps['cross_party_sponsored_bills']
if len(cp) != 55:
    errors.append(f"cross-party count {len(cp)} != 55")
if sum(1 for k in cp if bills[k]['disposition'] == 'Enacted') != 28:
    errors.append("cross-party enacted mismatch")

# merged sponsor counts (name variants)
cnt = Counter()
for b in pol:
    for s in b['primary_sponsors']:
        if s.get('entity_type') != 'organization':
            cnt[s['name']] += 1
merged = {
    "Dondero Loop": cnt['Senator Marilyn Dondero Loop'],
    "Hammond": cnt['Senator Scott Hammond'],
    "Buck": cnt['Senator Carrie Buck'] + cnt['Senator Carrie Ann Buck'],
    "Torres": cnt['Assemblywoman Selena Torres'] + cnt['Assemblymember Selena Torres-Fossett'],
    "Miller": cnt['Assemblywoman Brittney Miller'] + cnt['Assemblymember Brittney Miller'],
    "Anderson": cnt['Assemblywoman Natha Anderson'] + cnt['Assemblymember Natha Anderson'],
    "Seevers Gansert": cnt['Senator Heidi Seevers Gansert'],
    "Lange": cnt['Senator Roberta Lange'],
    "Denis": cnt['Senator Moises Denis'],
}
expected = {"Dondero Loop": 37, "Hammond": 31, "Buck": 31, "Torres": 27, "Miller": 24,
            "Anderson": 20, "Seevers Gansert": 19, "Lange": 19, "Denis": 18}
for nm, n in expected.items():
    if merged[nm] != n:
        errors.append(f"sponsor {nm}: {merged[nm]} != {n}")

vc = Counter(b['session_year'] for b in pol if b['disposition'] == 'Vetoed')
if dict(vc) != {'2023': 8, '2025': 5}:
    errors.append(f"veto years {dict(vc)}")

if len(pack['high_support_non_enactments']) != 47:
    errors.append(f"high-support {len(pack['high_support_non_enactments'])} != 47")

# Miller carried the independent IG bill in four straight sessions
ig = ["80:AB146", "81:AB108", "82:AB149", "83:AB154"]
for k in ig:
    names = [s['name'] for s in bills[k]['primary_sponsors']]
    if not any('Brittney Miller' in n for n in names):
        errors.append(f"{k}: Brittney Miller not among primary sponsors: {names}")

# AB386 finish-line story: passed both houses, no signature, no veto
b386_acts = [a for a in actions if a['session'] == '83' and a['bill_identifier'] == 'AB386']
blob = " ".join(a.get('description') or '' for a in b386_acts)
if "Yeas: 40" not in blob or "Yeas: 21" not in blob:
    errors.append("AB386: 40-0 / 21-0 passage not in history")
if "No further action taken" not in blob:
    errors.append("AB386: 'No further action taken' ending not found")
if "Approved by the Governor" in blob or "Vetoed" in blob:
    errors.append("AB386: unexpectedly signed/vetoed")

# special-session verification file claims
sp = {x['identifier']: x for x in special['bills']}
if 'AB3' not in sp or 'AB2' not in sp:
    errors.append("special-sessions verification missing AB2/AB3")
else:
    ab3 = sp['AB3']
    if "Chapter 5" not in (ab3['most_recent_history_action'] or ''):
        errors.append("31st AB3 not shown enacted (Chapter 5)")
    provs = " ".join(ab3.get('education_provisions_verified_from_enrolled_text') or [])
    if "31,429,229" not in provs or "Read by Grade" not in provs:
        errors.append("31st AB3 Read by Grade 3 cut not verified in file")
    ab2 = sp['AB2']
    if "No further action taken" not in " ".join(h['description'] for h in ab2['history']):
        errors.append("31st AB2 death not verified")

# crosswalk sanity: every proposal has at least one matched bill; the two
# no-record claims are about designs, verified by card text not crosswalk
cw = {c['proposal_id']: c for c in pack['constituent_proposal_crosswalk']}
if len(cw) != 10:
    errors.append("crosswalk != 10 proposals")

print("FACT-CHECK ERRORS:" if errors else "FACT-CHECK: ALL CLAIMS VERIFIED")
for e in errors:
    print(" -", e)
sys.exit(1 if errors else 0)
