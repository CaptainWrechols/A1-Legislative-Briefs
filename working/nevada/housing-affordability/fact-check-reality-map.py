#!/usr/bin/env python3
"""Programmatic fact-check of reality-map.json claims against the evidence pack.

Run from the repo root. Exit 0 = every checked claim verified.
"""
import json, sys
from collections import Counter
pack = json.load(open('working/nevada/housing-affordability/evidence-pack.json'))
bills = {b['bill_key']: b for b in pack['bills']}
votes = json.load(open('sources/nevada/housing-affordability/processed/bill-votes.json'))
special = {b['identifier']: b for b in json.load(open('sources/nevada/housing-affordability/verification/special-sessions.json'))['bills']}
rm = json.load(open('working/nevada/housing-affordability/reality-map.json'))
errors = []

def fp_votes(key):
    s, i = key.split(':')
    out = {}
    for v in votes:
        if v['session']==s and v['bill_identifier']==i and 'final passage' in (v.get('motion') or '').lower():
            ch = 'Assembly' if 'assembly' in (v.get('chamber') or '').lower() else 'Senate'
            c = v.get('counts') or {}
            out[ch] = f"{c.get('yes')}-{c.get('no')}"
    return out

for card in rm['proposal_reality_cards']:
    for k in card['matched_bills']:
        if k.startswith('special-'):
            if k.split(':')[1] not in special: errors.append(f"{card['proposal_id']}: {k} not in verification file")
            continue
        if k not in bills: errors.append(f"{card['proposal_id']}: {k} not in evidence pack")

claims = [
 ("82:SB395","Vetoed",{"Senate":"14-6","Assembly":"28-14"}),
 ("83:SB391","Failed",{"Senate":"13-8"}),
 ("82:AB345","Failed",{"Assembly":"28-13"}),
 ("81:SB159","Failed",{}),
 ("83:AB457","Enacted",{"Assembly":"27-15","Senate":"14-7"}),
 ("83:SB193","Failed",{"Senate":"14-5"}),
 ("81:SB188","Enacted",{"Assembly":"36-5","Senate":"21-0"}),
 ("80:SB194","Failed",{}),
 ("83:SB99","Failed",{"Senate":"14-6","Assembly":"27-15"}),
 ("81:AB331","Failed",{}), ("81:AB334","Failed",{}),
 ("80:SB471","Failed",{}),
 ("80:SB103","Enacted",{"Senate":"21-0","Assembly":"36-4"}),
 ("82:SB371","Vetoed",{"Senate":"12-9","Assembly":"26-14"}),
 ("83:SB289","Failed",{}),
 ("82:AB362","Failed",{}), ("82:SB426","Failed",{}),
 ("82:SB275","Vetoed",{"Senate":"13-8","Assembly":"28-14"}),
 ("83:SB151","Failed",{}), ("83:SB123","Failed",{}), ("83:AB443","Failed",{}),
 ("80:SB151","Enacted",{"Assembly":"28-12","Senate":"13-8"}),
 ("81:AB308","Enacted",{"Assembly":"34-8","Senate":"13-8"}),
 ("82:SB381","Enacted",{"Senate":"21-0","Assembly":"42-0"}),
 ("83:AB121","Enacted",{"Assembly":"27-15","Senate":"16-5"}),
 ("82:AB298","Vetoed",{"Assembly":"36-6","Senate":"12-8"}),
 ("83:AB280","Vetoed",{"Assembly":"27-15","Senate":"13-8"}),
 ("82:AB218","Vetoed",{"Assembly":"28-14","Senate":"13-7"}),
 ("82:SB78","Vetoed",{"Assembly":"28-14","Senate":"14-7"}),
 ("80:SB256","Failed",{"Senate":"11-10"}),
 ("81:SB218","Failed",{"Senate":"12-9"}),
 ("81:AB332","Failed",{}), ("83:SB436","Failed",{}),
 ("83:AB396","Enacted",{"Assembly":"27-15","Senate":"14-7"}),
 ("83:AB241","Enacted",{"Assembly":"28-14","Senate":"15-6"}),
 ("81:SB150","Enacted",{"Senate":"20-1","Assembly":"33-8"}),
 ("82:AB416","Failed",{}),
 ("83:AB131","Failed",{"Assembly":"42-0"}),
 ("83:SB430","Failed",{}),
 ("83:AB38","Enacted",{"Assembly":"40-2","Senate":"17-3"}),
 ("82:SB47","Failed",{}),
 ("83:AB269","Enacted",{}), ("83:SB266","Enacted",{}),
 ("80:AB476","Enacted",{"Assembly":"38-2","Senate":"20-0"}),
 ("80:AB73","Enacted",{}), ("80:AB240","Enacted",{}),
 ("83:AB37","Failed",{"Assembly":"42-0"}),
 ("83:AB540","Enacted",{"Assembly":"42-0","Senate":"15-6"}),
 ("83:AB475","Enacted",{"Assembly":"42-0","Senate":"19-1"}),
 ("83:AB211","Enacted",{}),
 ("83:SB393","Failed",{}),
]
for key, disp, expvotes in claims:
    b = bills.get(key)
    if not b: errors.append(f"{key}: missing from pack"); continue
    if b['disposition'] != disp: errors.append(f"{key}: disposition {b['disposition']} != claimed {disp}")
    got = fp_votes(key)
    for ch, yn in expvotes.items():
        if got.get(ch) != yn: errors.append(f"{key}: {ch} vote {got.get(ch)} != claimed {yn}")

sb10 = special['SB10']
h = " ".join(x['description'] for x in sb10['history']) + " " + sb10['most_recent_history_action']
if "Lost" not in h or "Yeas: 27" not in h: errors.append("SB10: Assembly Lost 27-10 not in history")
if "TWO-THIRDS" not in sb10.get('vote_requirement','').upper(): errors.append("SB10: 2/3 requirement missing")
sv = [v for v in sb10['votes'] if v['chamber'].startswith('Senate')]
if not sv or sv[0]['counts'].get('Yea') != 18 or sv[0]['counts'].get('Nay') != 0: errors.append("SB10: Senate 18-0 mismatch")

inv = pack['inventory']
if not (inv['policy_bills']==149 and inv['core_bills']==93 and inv['context_bills']==282): errors.append("inventory mismatch")
if inv['dispositions_policy']!={'Enacted':63,'Failed':70,'Vetoed':16}: errors.append("dispositions mismatch")
for y, exp in [("2019",(35,22,0)),("2021",(27,14,1)),("2023",(39,12,9)),("2025",(48,15,6))]:
    d = inv['sessions'][y]; dd = d['dispositions']
    if (d['bills_in_set'], dd.get('Enacted',0), dd.get('Vetoed',0)) != exp: errors.append(f"session {y} mismatch: {d}")

cw = {c['proposal_id']: c for c in pack['constituent_proposal_crosswalk']}
if cw['inclusionary-requirements']['matched_bills']: errors.append("inclusionary should be none")

ps = pack['people_signals']
if ps['committee_sponsored_policy_bills']!=35 or ps['person_sponsored_policy_bills']!=114: errors.append("sponsor split mismatch")
if len(ps['cross_party_sponsored_bills'])!=16: errors.append("cross-party count mismatch")
if sum(1 for k in ps['cross_party_sponsored_bills'] if bills[k]['disposition']=='Enacted')!=13: errors.append("cross-party enacted mismatch")
freq = {f['name']: f for f in ps['frequent_primary_sponsors']}
for nm, n in [("Senator Julia Ratti",12),("Senator Dina Neal",10),("Senator Dallas Harris",9),("Senator Pat Spearman",8),("Senator Fabian Doñate",7)]:
    f = freq.get(nm)
    if not f or f['bill_count']!=n or f.get('party')!='Democratic': errors.append(f"sponsor {nm} mismatch")

vc = Counter(bills[k]['session_year'] for k in bills if bills[k]['relevance']!='context' and bills[k]['disposition']=='Vetoed')
if dict(vc) != {'2021':1,'2023':9,'2025':6}: errors.append(f"veto years {dict(vc)}")

fc_deaths = sum(1 for b in bills.values() if b['relevance']!='context' and b['disposition']=='Failed' and b['death_or_success_stage'] in ('origin_committee','introduced'))
if fc_deaths != 43: errors.append(f"first-committee deaths {fc_deaths} != 43")

print("FACT-CHECK ERRORS:" if errors else "FACT-CHECK: ALL CLAIMS VERIFIED")
for e in errors: print(" -", e)
sys.exit(1 if errors else 0)
