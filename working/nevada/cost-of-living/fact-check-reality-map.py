#!/usr/bin/env python3
"""Programmatic fact-check of reality-map.json claims against the evidence pack.

Run from the repo root. Exit 0 = every checked claim verified.
"""
import json
import re
import sys
from collections import Counter

pack = json.load(open('working/nevada/cost-of-living/evidence-pack.json'))
bills = {b['bill_key']: b for b in pack['bills']}
votes = json.load(open('sources/nevada/cost-of-living/processed/bill-votes.json'))
acts = json.load(open('sources/nevada/cost-of-living/processed/bill-actions.json'))
special = {b['identifier']: b for b in json.load(
    open('sources/nevada/cost-of-living/verification/special-sessions.json'))['bills']}
rm = json.load(open('working/nevada/cost-of-living/reality-map.json'))
errors = []


def fp_votes(key):
    s, i = key.split(':')
    out = {}
    for v in votes:
        if v['session'] == s and v['bill_identifier'] == i and \
                'final passage' in (v.get('motion') or '').lower():
            ch = 'Assembly' if 'assembly' in (v.get('chamber') or '').lower() else 'Senate'
            c = v.get('counts') or {}
            key2 = ch
            yn = f"{c.get('yes')}-{c.get('no')}"
            # keep the highest-yes roll per chamber (reprints)
            if key2 not in out or int(yn.split('-')[0]) > int(out[key2].split('-')[0]):
                out[key2] = yn
    return out


# 1) Every matched bill on every card exists in the pack / verification file
for card in rm['proposal_reality_cards']:
    for k in card['matched_bills']:
        if k.startswith('special-'):
            if k.split(':')[1] not in special:
                errors.append(f"{card['proposal_id']}: {k} not in verification file")
            continue
        if k not in bills:
            errors.append(f"{card['proposal_id']}: {k} not in evidence pack")

# 2) Dispositions, stages, and floor votes cited in the cards and scorecards
claims = [
    # licensure-compacts
    ("80:SB186", "Enacted", None, {}),
    ("83:AB248", "Enacted", None, {"Assembly": "41-1", "Senate": "21-0"}),
    ("82:AB158", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("83:AB230", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("83:AB334", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("81:AB142", "Failed", "origin_committee", {}),
    ("82:AB108", "Failed", "origin_committee", {}),
    ("83:SB34", "Failed", "origin_committee", {}),
    ("80:SB259", "Failed", "origin_floor", {}),
    ("83:SB124", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("81:SB100", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("82:SB97", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("83:AB106", "Failed", "origin_floor", {}),
    # provider-supply
    ("83:SB434", "Failed", "after_both_chambers", {"Senate": "18-2", "Assembly": "42-0"}),
    ("80:SB289", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("81:SB233", "Enacted", None, {"Assembly": "42-0", "Senate": "19-0"}),
    ("80:SB366", "Enacted", None, {}),
    ("81:AB278", "Enacted", None, {}),
    ("81:SB379", "Enacted", None, {}),
    ("82:AB248", "Failed", "origin_committee", {}),
    ("83:SB495", "Failed", "second_chamber", {"Senate": "13-8"}),
    ("83:SB425", "Failed", "origin_floor", {}),
    # gme-residencies
    ("82:SB350", "Enacted", None, {"Assembly": "40-0", "Senate": "21-0"}),
    ("83:SB262", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("82:SB369", "Failed", "origin_floor", {}),
    ("83:SB269", "Failed", "origin_floor", {}),
    ("80:AB311", "Failed", "origin_committee", {}),
    ("82:AB393", "Failed", "origin_committee", {}),
    ("83:AB170", "Failed", "origin_committee", {}),
    ("82:SB204", "Failed", "origin_floor", {}),
    # provider-loan-forgiveness
    ("82:AB45", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("83:AB269", "Enacted", None, {"Assembly": "40-2", "Senate": "21-0"}),
    ("83:SB266", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("80:AB358", "Failed", "origin_floor", {}),
    ("81:AB372", "Failed", "origin_committee", {}),
    ("82:AB69", "Failed", "origin_floor", {}),
    # prior-authorization-reform
    ("83:AB463", "Enacted", None, {"Assembly": "42-0", "Senate": "20-0"}),
    ("83:SB128", "Vetoed", None, {"Assembly": "23-16", "Senate": "15-6"}),
    ("83:AB290", "Failed", "origin_floor", {}),
    ("83:AB295", "Failed", "origin_committee", {}),
    ("83:AB470", "Failed", "origin_committee", {}),
    ("83:SB398", "Failed", "origin_committee", {}),
    ("80:AB225", "Failed", "origin_committee", {}),
    ("80:AB372", "Failed", "origin_committee", {}),
    ("80:SB359", "Failed", "origin_committee", {}),
    ("82:SB167", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("82:SB194", "Enacted", None, {"Assembly": "42-0", "Senate": "21-0"}),
    ("83:AB202", "Enacted", None, {"Assembly": "42-0", "Senate": "20-0"}),
    # pbm-middlemen
    ("80:AB141", "Enacted", None, {"Assembly": "40-0", "Senate": "21-0"}),
    ("80:SB276", "Enacted", None, {}),
    ("80:SB378", "Enacted", None, {}),
    ("82:AB434", "Enacted", None, {}),
    ("83:SB389", "Enacted", None, {"Assembly": "41-0", "Senate": "18-2"}),
    ("81:SB392", "Failed", "origin_committee", {}),
    ("82:SB352", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("83:SB316", "Failed", "after_both_chambers", {"Senate": "18-2", "Assembly": "42-0"}),
    ("83:SB149", "Failed", "origin_committee", {}),
    ("83:SB209", "Failed", "origin_committee", {}),
    # network-credentialing
    ("80:SB234", "Enacted", None, {"Assembly": "39-0", "Senate": "21-0"}),
    ("82:SB494", "Enacted", None, {"Assembly": "42-0", "Senate": "20-0"}),
    ("80:SB290", "Failed", "origin_committee", {}),
    ("81:SB90", "Failed", "second_chamber", {"Senate": "21-0"}),
    # small-business-pooling
    ("80:SB481", "Enacted", None, {"Assembly": "39-0", "Senate": "21-0"}),
    ("81:SB396", "Enacted", None, {"Assembly": "40-1", "Senate": "21-0"}),
    ("81:SB420", "Enacted", None, {"Assembly": "26-15", "Senate": "12-9"}),
    ("80:SB226", "Failed", "origin_committee", {}),
    # reimbursement-rates
    ("81:SB96", "Enacted", None, {}),
    ("82:AB197", "Failed", "origin_floor", {}),
    ("82:SB435", "Enacted", None, {}),
    ("82:SB221", "Enacted", None, {}),
    ("83:SB353", "Enacted", None, {}),
    ("83:SB185", "Enacted", None, {"Assembly": "41-1", "Senate": "21-0"}),
    ("83:AB284", "Enacted", None, {}),
    ("83:SB497", "Enacted", None, {}),
    ("80:AB116", "Failed", "origin_floor", {}),
    ("82:AB99", "Failed", "origin_floor", {}),
    ("82:SB255", "Failed", "origin_committee", {}),
    ("83:SB239", "Failed", "origin_committee", {}),
    ("83:SB150", "Failed", "origin_committee", {}),
    ("83:SB366", "Failed", "origin_committee", {}),
    ("81:AB347", "Failed", "origin_floor", {}),
    ("81:AB436", "Enacted", None, {}),
    ("83:AB448", "Enacted", None, {}),
    # care-settings
    ("80:AB469", "Enacted", None, {"Assembly": "38-3", "Senate": "21-0"}),
    ("82:SB497", "Enacted", None, {}),
    ("80:AB317", "Enacted", None, {}),
    ("82:AB277", "Enacted", None, {"Assembly": "41-0", "Senate": "21-0"}),
    ("82:AB85", "Failed", "origin_floor", {}),
    ("83:AB349", "Failed", "origin_committee", {}),
    ("81:SB5", "Enacted", None, {}),
    ("82:SB119", "Enacted", None, {}),
    ("82:AB276", "Enacted", None, {}),
    ("80:AB232", "Enacted", None, {}),
    # veto-pattern citations
    ("82:AB439", "Vetoed", None, {"Assembly": "42-0", "Senate": "14-6"}),
    ("82:AB250", "Vetoed", None, {}),
    ("83:AB259", "Vetoed", None, {}),
    ("83:AB204", "Vetoed", None, {}),
    ("83:AB282", "Vetoed", None, {}),
    ("82:AB11", "Vetoed", None, {}),
    ("83:SB182", "Vetoed", None, {}),
    ("82:SB400", "Vetoed", None, {}),
    ("82:SB302", "Vetoed", None, {}),
    ("83:SB171", "Vetoed", None, {}),
    ("83:SB352", "Vetoed", None, {}),
    ("82:AB251", "Vetoed", None, {}),
    ("82:AB437", "Vetoed", None, {}),
    # high-support list extras
    ("80:SB200", "Failed", "second_chamber", {"Senate": "21-0"}),
    ("80:SB235", "Failed", "second_chamber", {"Senate": "21-0"}),
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

# 3) Special-session claims
sb5 = special['SB5']
sv = {v['chamber'].split(' ')[0]: v['counts'] for v in sb5['votes'] if v['vote_type'] == 'Final Passage'}
if sv.get('Senate', {}).get('Yea') != 15 or sv.get('Senate', {}).get('Nay') != 6:
    errors.append("special SB5: Senate 15-6 mismatch")
if sv.get('Assembly', {}).get('Yea') != 37 or sv.get('Assembly', {}).get('Nay') != 0:
    errors.append("special SB5: Assembly 37-0 mismatch")
if 'Chapter 12' not in sb5['most_recent_history_action']:
    errors.append("special SB5: Chapter 12 missing")
if 'Statewide Health Care Access and Recruitment Grant Program' not in sb5['digest_first_1200']:
    errors.append("special SB5: program name missing from digest")
ab3 = special['AB3']
av = {v['chamber']: v['counts'] for v in ab3['votes'] if v['vote_type'] == 'Final Passage'}
best_asm = max((c for ch, c in av.items() if ch.startswith('Assembly')), key=lambda c: c['Yea'])
best_sen = max((c for ch, c in av.items() if ch.startswith('Senate')), key=lambda c: c['Yea'])
if best_asm['Yea'] != 36 or best_asm['Nay'] != 6:
    errors.append("special AB3: Assembly 36-6 mismatch")
if best_sen['Yea'] != 21 or best_sen['Nay'] != 0:
    errors.append("special AB3: Senate 21-0 mismatch")
if 'Chapter' not in ab3['most_recent_history_action']:
    errors.append("special AB3: not enacted?")

# 4) SB434 <-> SB5 same-program linkage + concurrence death (textual)
core = {f"{b['session']}:{b['identifier']}": b
        for b in json.load(open('sources/nevada/cost-of-living/processed/bills-core.json'))['bills']}
if 'Statewide Health Care Access and Recruitment' not in (core['83:SB434'].get('abstract') or ''):
    errors.append("SB434: program name missing from digest")
sb434_hist = " ".join(a['description'] for a in acts
                      if a['session'] == '83' and a['bill_identifier'] == 'SB434')
if 'not concurred in' not in sb434_hist:
    errors.append("SB434: concurrence death not in history")
# SB34 omnibus includes the Nurse Licensure Compact
if 'Nurse Licensure Compact' not in (core['83:SB34'].get('abstract') or ''):
    errors.append("SB34: NLC not in digest")
# AB290: cleared first committee then re-referred, no further action
ab290 = " ".join(a['description'] for a in acts
                 if a['session'] == '83' and a['bill_identifier'] == 'AB290')
if 'From committee: Amend, and do pass as amended' not in ab290 or '(No further action taken.)' not in ab290:
    errors.append("AB290: history narrative mismatch")
# No physician (IMLC) compact and no NLC bill besides the three cited
raw = json.load(open('sources/nevada/cost-of-living/pass1/bills.json'))['bills']
nlc = [f"{b['session']}:{b['identifier']}" for b in raw
       if 'nurse licensure compact' in ((b.get('title') or '') + ' ' + (b.get('abstract') or '')).lower()]
if sorted(nlc) != ['81:AB142', '82:AB108', '83:SB34']:
    errors.append(f"NLC bill list mismatch: {nlc}")
# IMLC: already in statute per SB34's digest; no 2019-2025 bill enacts it
if 'Interstate Medical Licensure Compact' not in (core['83:SB34'].get('abstract') or ''):
    errors.append("SB34: IMLC reference missing from digest")
imlc_enact = [b for b in raw if re.search(r'enacts the interstate medical licensure compact',
              ((b.get('title') or '') + ' ' + (b.get('abstract') or '')).lower())]
if imlc_enact:
    errors.append(f"IMLC enactment bill unexpectedly found: {[(b['session'], b['identifier']) for b in imlc_enact]}")
# 80:SCR10 adopted
scr10 = " ".join(a['description'] for a in acts
                 if a['session'] == '80' and a['bill_identifier'] == 'SCR10')
if 'adopted' not in scr10.lower() or 'File No.' not in scr10:
    errors.append("SCR10: adoption not in history")

# 5) Inventory + session snapshot
inv = pack['inventory']
if not (inv['total_bills_collected'] == 772 and inv['policy_bills'] == 409
        and inv['core_bills'] == 276 and inv['adjacent_bills'] == 133
        and inv['context_bills'] == 363):
    errors.append("inventory mismatch")
if inv['dispositions_policy'] != {'Failed': 172, 'Enacted': 221, 'Unknown': 1, 'Vetoed': 15}:
    errors.append(f"dispositions mismatch: {inv['dispositions_policy']}")
snap = rm['session_snapshot']
for y, exp in [("2019", (82, 47, 34, 0)), ("2021", (82, 46, 36, 0)),
               ("2023", (112, 61, 43, 8)), ("2025", (133, 67, 59, 7))]:
    d = inv['sessions'][y]['dispositions']
    got = (inv['sessions'][y]['bills_in_set'], d.get('Enacted', 0), d.get('Failed', 0), d.get('Vetoed', 0))
    if got != exp:
        errors.append(f"session {y} mismatch: {got} != {exp}")
    s = snap[y]
    if (s['bills_in_set'], s['enacted'], s['failed'], s['vetoed']) != exp:
        errors.append(f"reality-map snapshot {y} mismatch")

# 6) Theme scorecard counts
theme_pack = {t['theme_id']: t for t in pack['themes']}
for t in rm['theme_scorecards']:
    tp = theme_pack.get(t['theme_id'])
    if not tp or tp['bill_count'] != t['bills'] or tp['enacted_count'] != t['enacted']:
        errors.append(f"theme {t['theme_id']}: counts mismatch")

# 7) People signals
ps = pack['people_signals']
if ps['committee_sponsored_policy_bills'] != 139 or ps['person_sponsored_policy_bills'] != 270:
    errors.append("sponsor split mismatch")
if len(ps['cross_party_sponsored_bills']) != 54:
    errors.append("cross-party count mismatch")
if sum(1 for k in ps['cross_party_sponsored_bills'] if bills[k]['disposition'] == 'Enacted') != 36:
    errors.append("cross-party enacted mismatch")
freq = {f['name']: f for f in ps['frequent_primary_sponsors']}
for nm, party, n in [("Senator Pat Spearman", "Democratic", 21),
                     ("Senator Joseph Hardy", "Republican", 19),
                     ("Senator Melanie Scheible", "Democratic", 18),
                     ("Senator Nicole Cannizzaro", "Democratic", 16),
                     ("Senator Roberta Lange", "Democratic", 16),
                     ("Senator Jeff Stone", "Republican", 16),
                     ("Senator Fabian Doñate", "Democratic", 16),
                     ("Senator James Ohrenschall", "Democratic", 12)]:
    f = freq.get(nm)
    if not f or f['bill_count'] != n or f.get('party') != party:
        errors.append(f"sponsor {nm} mismatch: {f}")

# 8) Veto years + first-committee deaths + committee breakdown
vc = Counter(bills[k]['session_year'] for k in bills
             if bills[k]['relevance'] != 'context' and bills[k]['disposition'] == 'Vetoed')
if dict(vc) != {'2023': 8, '2025': 7}:
    errors.append(f"veto years {dict(vc)}")
policy = [b for b in pack['bills'] if b['relevance'] != 'context']
fc_bills = [b for b in policy if b['disposition'] == 'Failed'
            and b['death_or_success_stage'] in ('origin_committee', 'introduced')]
if len(fc_bills) != 95:
    errors.append(f"first-committee deaths {len(fc_bills)} != 95")
ref = {}
for a in acts:
    k = f"{a['session']}:{a['bill_identifier']}"
    m = re.search(r"Referred to Committee on ([A-Za-z, ]+?)(?:\.|$)", a['description'])
    if m and k not in ref:
        ref[k] = m.group(1).strip()
fc = Counter()
for b in fc_bills:
    ch = 'Assembly' if b['identifier'].startswith('A') else 'Senate'
    fc[f"{ch} {ref.get(b['bill_key'], '?')}"] += 1
checks = [("Senate Health and Human Services", 22), ("Assembly Commerce and Labor", 21),
          ("Senate Commerce and Labor", 19), ("Assembly Health and Human Services", 16)]
for cm, n in checks:
    got = sum(v for k, v in fc.items() if k.endswith(cm) and k.startswith(cm.split(' ')[0]))
    if fc.get(f"{cm.split(' ')[0]} {' '.join(cm.split(' ')[1:])}") != n:
        errors.append(f"committee {cm}: {fc}")
money = fc.get('Assembly Ways and Means', 0) + fc.get('Senate Finance', 0)
if money != 10:
    errors.append(f"money-committee deaths {money} != 10")

# 9) High-support non-enactments count
if len(pack['high_support_non_enactments']) != 43:
    errors.append(f"high-support count {len(pack['high_support_non_enactments'])} != 43")

# 10) Unanimity claim: enacted policy bills with 100% best floor vote
unan = sum(1 for b in policy if b['disposition'] == 'Enacted' and b['best_floor_yes_pct'] == 100.0)
if unan != 187:
    errors.append(f"unanimous-chamber enactments {unan} != 187")

print("FACT-CHECK ERRORS:" if errors else "FACT-CHECK: ALL CLAIMS VERIFIED")
for e in errors:
    print(" -", e)
sys.exit(1 if errors else 0)
