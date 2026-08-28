#!/usr/bin/env python3
"""Curate the keep-all Pass 1 set for south-carolina-02-responsive-elected-leaders.

Pass 1 kept every full-text/title hit (5,548 bills). This script encodes the
hand review: which bills belong to the issue set (core / adjacent / context),
one plain sentence and a citizen-facing theme per kept bill, and the explicit
exclusion rules for everything else. Ambiguous bills were verified against
their latest-version full text in sources/south-carolina/_universe/.

Four bills (the REACH Act civics family) are sourced from the certified
universe rather than Pass 1: their full text contains none of the issue's
search terms, but they are directly responsive to the voter-civics-education
constituent proposal and were found by a hand title-scan of the universe
index. They are marked source="universe".

Output: working/south-carolina/responsive-elected-leaders/curation-map.json
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PASS1 = os.path.join(ROOT, "sources/south-carolina/responsive-elected-leaders/pass1/bills.json")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")
OUT = os.path.join(HERE, "curation-map.json")

T_TERMLIM = "Term limits for elected officials"
T_CAMPFIN = "Campaign money rules"
T_RCV = "Ranked choice voting and runoffs"
T_REDIST = "Who draws the voting maps (redistricting)"
T_DISCLOSE = "Financial disclosure and ethics enforcement"
T_LOBBY = "Lobbying rules"
T_OPENGOV = "Open government: public records and meetings"
T_CIVICS = "Civics and voter education"
T_DIRECT = "Direct democracy: recall, initiative, referendum"
T_CONTEXT = "Related context"

THEMES = [T_TERMLIM, T_CAMPFIN, T_RCV, T_REDIST, T_DISCLOSE, T_LOBBY,
          T_OPENGOV, T_CIVICS, T_DIRECT, T_CONTEXT]

# (session, bill_no): (tier, theme, plain_topic)
KEEP = {
    # ------------------------------------------------------------------
    # Term limits for elected officials.
    # Three state designs verified in full text: (1) "authorize by law" -
    # a constitutional amendment letting the General Assembly set term
    # limits by ordinary law; (2) a direct constitutional limit with the
    # cap written in; (3) a statutory limit without a constitutional
    # amendment. Plus Article V applications aimed at Congress.
    (123, "H3023"): ("core", T_TERMLIM, "Proposed a constitutional amendment (for the ballot) letting the General Assembly set term limits for its own members by ordinary law."),
    (123, "H3024"): ("core", T_TERMLIM, "Would have capped service by statute: six terms in the House or four terms in the Senate."),
    (123, "H3166"): ("core", T_TERMLIM, "Article V application asking Congress to call a convention limited to proposing term limits for the U.S. House and Senate."),
    (123, "S268"):  ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (123, "S269"):  ("core", T_TERMLIM, "Would have capped General Assembly service by statute."),
    (123, "S663"):  ("core", T_TERMLIM, "Article V application (resolution form) asking Congress to call a convention limited to congressional term limits."),
    (123, "S944"):  ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (123, "S945"):  ("core", T_TERMLIM, "Would have capped service by statute: six terms in the House or three terms in the Senate."),
    (124, "H3257"): ("core", T_TERMLIM, "Proposed a constitutional amendment capping consecutive service starting with members elected in 2024 (five consecutive House terms)."),
    (124, "H3259"): ("core", T_TERMLIM, "Would have capped service by statute: six terms in the House or four terms in the Senate."),
    (124, "H3260"): ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (124, "H3663"): ("core", T_TERMLIM, "Article V application asking Congress to call a convention limited to congressional term limits."),
    (124, "H3746"): ("core", T_TERMLIM, "Proposed a constitutional amendment: three consecutive Senate terms or six consecutive House terms, counted from the 2024 election forward."),
    (124, "S302"):  ("core", T_TERMLIM, "Proposed a constitutional amendment capping service at three Senate terms or six House terms."),
    (124, "S338"):  ("core", T_TERMLIM, "Would have capped service by statute: six terms in the House or three terms in the Senate."),
    (124, "S339"):  ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (124, "S384"):  ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (125, "H3249"): ("core", T_TERMLIM, "Would have capped General Assembly service by statute."),
    (125, "H3250"): ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (125, "H3444"): ("core", T_TERMLIM, "Proposed a constitutional amendment capping consecutive service starting with members elected in 2024 (five consecutive House terms)."),
    (125, "H3574"): ("core", T_TERMLIM, "Proposed a constitutional amendment capping consecutive service at four House terms or two Senate terms - the strictest state design filed."),
    (125, "S172"):  ("core", T_TERMLIM, "Proposed a constitutional amendment capping service at three Senate terms or six House terms."),
    (125, "S213"):  ("core", T_TERMLIM, "Would have capped service by statute: six terms in the House or three terms in the Senate."),
    (125, "S214"):  ("core", T_TERMLIM, "Proposed a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (126, "H3744"): ("core", T_TERMLIM, "Proposes a constitutional amendment letting the General Assembly set term limits for its own members by ordinary law."),
    (126, "H3745"): ("core", T_TERMLIM, "Would cap service by statute: six terms in the House or four terms in the Senate."),
    (126, "H4462"): ("core", T_TERMLIM, "Would cap total General Assembly service at twelve years by statute, paired with a raise in members' in-district compensation."),
    (126, "H5360"): ("core", T_TERMLIM, "Proposes a constitutional amendment capping service at four House terms or two Senate terms."),
    (126, "S590"):  ("core", T_TERMLIM, "Proposes a constitutional amendment capping service at three Senate terms or six House terms."),
    (126, "H3008"): ("core", T_TERMLIM, "Article V application for a convention limited to a congressional term limits amendment - adopted by both chambers in May 2025, the only term-limits measure in this record to pass anything."),
    (125, "H4692"): ("adjacent", T_TERMLIM, "House rule change (not a law): committee chairmen could serve at most two consecutive two-year terms leading a committee."),
    (126, "H3102"): ("adjacent", T_TERMLIM, "Resolution calling for term limits for U.S. Supreme Court justices."),
    # Broad Convention of the States applications - their text includes
    # term limits for federal officials and members of Congress among the
    # convention subjects (verified in full text).
    (123, "H3125"): ("adjacent", T_TERMLIM, "Broad Article V Convention of States application (fiscal restraints, limits on federal power, and term limits for Congress); reported favorably, died on the House calendar when COVID ended the session."),
    (123, "S112"):  ("adjacent", T_TERMLIM, "Broad Article V Convention of States application including congressional term limits."),
    (124, "S133"):  ("adjacent", T_TERMLIM, "Broad Article V Convention of States application including congressional term limits; passed both chambers in different forms and died when the House never took up the conference report."),
    (124, "S141"):  ("adjacent", T_TERMLIM, "Broad Article V Convention of States application (resolution form); favorable committee report, no floor vote."),
    (125, "H3676"): ("adjacent", T_TERMLIM, "Broad Article V Convention of States application; passed the House 68-30 and died on the Senate calendar after a favorable committee report."),
    # ------------------------------------------------------------------
    # Campaign money rules.
    (124, "H4877"): ("core", T_CAMPFIN, "The Eradication of Corporate Money in Politics Act: would have barred corporations from making campaign contributions to candidates, committees, or parties."),
    (126, "S813"):  ("core", T_CAMPFIN, "Would require campaign reports to list the occupation and employer of anyone giving more than $100 - filed by Senate leadership of both parties."),
    (123, "S3"):    ("core", T_CAMPFIN, "Would have required independent expenditure committees to put disclosures and disclaimers on their election ads."),
    (124, "S174"):  ("core", T_CAMPFIN, "Would have required independent expenditure committees to put disclosures and disclaimers on their election ads."),
    (126, "S960"):  ("core", T_CAMPFIN, "Would require independent expenditure committees to disclose who is behind their election ads."),
    (123, "H4192"): ("core", T_CAMPFIN, "Would have required anyone spending over $500 on independent expenditures or electioneering ads to file reports with the State Ethics Commission."),
    (123, "H3097"): ("core", T_CAMPFIN, "Would have barred officials from appointing anyone who gave them a campaign contribution in the previous four years."),
    (123, "S231"):  ("core", T_CAMPFIN, "Would have barred officials from appointing anyone who gave them a campaign contribution in the previous four years."),
    (124, "S306"):  ("core", T_CAMPFIN, "Would have barred officials from appointing anyone who gave them a campaign contribution in the previous four years."),
    (125, "S199"):  ("core", T_CAMPFIN, "Would have barred officials from appointing anyone who gave them a campaign contribution in the previous four years."),
    (123, "H4333"): ("core", T_CAMPFIN, "Would have raised South Carolina's individual contribution limits to track the federal limits, which adjust for inflation."),
    (123, "S800"):  ("core", T_CAMPFIN, "Would have raised South Carolina's individual contribution limits to track the federal limits, which adjust for inflation."),
    (124, "H3197"): ("core", T_CAMPFIN, "Would have raised individual contribution limits and the limits on money from party and caucus committees."),
    (125, "H3474"): ("core", T_CAMPFIN, "Would have raised individual contribution limits and the limits on money from party and caucus committees."),
    (126, "H3554"): ("core", T_CAMPFIN, "Would raise individual contribution limits and the limits on money from party and caucus committees."),
    (123, "S184"):  ("core", T_CAMPFIN, "Would have pooled interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (123, "S986"):  ("core", T_CAMPFIN, "Would have pooled interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (124, "S187"):  ("core", T_CAMPFIN, "Would have pooled interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (124, "S214"):  ("core", T_CAMPFIN, "Would have pooled interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (125, "S137"):  ("core", T_CAMPFIN, "Would have pooled interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (126, "S84"):   ("core", T_CAMPFIN, "Would pool interest earned on campaign bank accounts (plus 1% of deposits) to fund State Ethics Commission enforcement."),
    (123, "S210"):  ("core", T_CAMPFIN, "Would have required candidates to file their actual campaign bank statements alongside each quarterly campaign report."),
    (124, "S189"):  ("core", T_CAMPFIN, "Would have required candidates to file their actual campaign bank statements alongside each quarterly campaign report."),
    (124, "S250"):  ("core", T_CAMPFIN, "Would have required candidates to file their actual campaign bank statements alongside each quarterly campaign report."),
    (125, "S159"):  ("core", T_CAMPFIN, "Would have required candidates to file their actual campaign bank statements alongside each quarterly campaign report."),
    (126, "S91"):   ("core", T_CAMPFIN, "Would require candidates to file their actual campaign bank statements alongside each quarterly campaign report."),
    (124, "H3522"): ("core", T_CAMPFIN, "Proposed a constitutional amendment creating public financing for Attorney General campaigns - the record's only public-financing bill."),
    (125, "H4561"): ("core", T_CAMPFIN, "Would have let candidates use campaign funds for dependent care while campaigning; passed the House 53-45 and died in Senate Judiciary."),
    (125, "H3242"): ("core", T_CAMPFIN, "Would have barred legislators and candidates from taking contributions from state-granted monopolies such as utilities."),
    (123, "H4203"): ("adjacent", T_CAMPFIN, "Would have rewritten the definitions of 'committee' and 'contribution' in the campaign-practices law."),
    (123, "H3723"): ("adjacent", T_CAMPFIN, "Would have set rules for candidates accepting digital currency (crypto) as campaign contributions."),
    (123, "H3305"): ("adjacent", T_CAMPFIN, "Would have barred candidates for boards the General Assembly elects from contributing to legislators."),
    (123, "S537"):  ("adjacent", T_CAMPFIN, "Would have barred legislators from using official funds for unsolicited mass mailings within 90 days of their own election."),
    (123, "S192"):  ("adjacent", T_CAMPFIN, "Article V application asking Congress to call a convention on campaign finance reform."),
    (125, "H4660"): ("adjacent", T_CAMPFIN, "Would have banned deceptive AI deepfake media in elections."),
    (126, "H3517"): ("adjacent", T_CAMPFIN, "Would ban deceptive AI deepfake media in elections."),
    # ------------------------------------------------------------------
    # Ranked choice voting and runoffs.
    (124, "H5135"): ("core", T_RCV, "Would have let cities and towns choose ranked-choice voting for municipal elections."),
    (125, "H4022"): ("core", T_RCV, "Would have added instant runoff (ranked choice) voting as an option for municipal elections."),
    (126, "H3589"): ("core", T_RCV, "Would establish the instant runoff (ranked choice) method for certain local elections and allow multi-member municipal districts."),
    (125, "H4591"): ("core", T_RCV, "Would have banned ranked choice or instant runoff voting in all South Carolina elections."),
    (126, "H3386"): ("core", T_RCV, "Would ban ranked choice or instant runoff voting in all South Carolina elections."),
    (125, "H3606"): ("adjacent", T_RCV, "Would have abolished primary runoffs: the candidate with the most primary votes wins the nomination outright."),
    (126, "H3552"): ("adjacent", T_RCV, "Would abolish primary runoffs: the candidate with the most primary votes wins the nomination outright."),
    (125, "H4592"): ("adjacent", T_RCV, "Would have eliminated runoffs in special primary elections."),
    (126, "H3318"): ("adjacent", T_RCV, "Would eliminate runoffs in special primary elections."),
    # ------------------------------------------------------------------
    # Who draws the voting maps (redistricting).
    (123, "H3044"): ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission, with plans approved by referendum."),
    (123, "S6"):    ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission, with plans approved by referendum."),
    (123, "S135"):  ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission."),
    (124, "H3279"): ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission."),
    (124, "S561"):  ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission."),
    (125, "H3173"): ("core", T_REDIST, "Proposed a constitutional amendment creating an independent reapportionment commission."),
    (123, "H3167"): ("core", T_REDIST, "Proposed a constitutional amendment creating a Citizens Redistricting Commission."),
    (123, "H3390"): ("core", T_REDIST, "Proposed a constitutional amendment creating a Citizens Redistricting Commission."),
    (123, "S249"):  ("core", T_REDIST, "Proposed a constitutional amendment creating a Citizens Redistricting Commission."),
    (124, "H4201"): ("core", T_REDIST, "Proposed a constitutional amendment creating a Citizens Redistricting Commission."),
    (125, "H3243"): ("core", T_REDIST, "Proposed a constitutional amendment creating a Citizens Redistricting Commission."),
    (123, "H3432"): ("core", T_REDIST, "Would have created a Citizens Redistricting Commission by statute to submit reapportionment plans to the General Assembly."),
    (123, "S254"):  ("core", T_REDIST, "Would have created a Citizens Redistricting Commission by statute to submit reapportionment plans to the General Assembly."),
    (124, "H4202"): ("core", T_REDIST, "Would have created a Citizens Redistricting Commission by statute to submit reapportionment plans to the General Assembly."),
    (125, "H3245"): ("core", T_REDIST, "Would have created a Citizens Redistricting Commission by statute to submit reapportionment plans to the General Assembly."),
    (123, "H3054"): ("core", T_REDIST, "Would have created an independent South Carolina Redistricting Commission by statute to draw House, Senate, and congressional maps."),
    (123, "S230"):  ("core", T_REDIST, "Would have created an independent South Carolina Redistricting Commission by statute to draw House, Senate, and congressional maps."),
    (124, "H4229"): ("core", T_REDIST, "The FAIR in Redistricting Act: binding criteria and a public process for maps the General Assembly draws (no commission)."),
    (124, "S750"):  ("core", T_REDIST, "The FAIR in Redistricting Act: binding criteria and a public process for maps the General Assembly draws (no commission)."),
    (125, "H3069"): ("core", T_REDIST, "The FAIR in Redistricting Act: binding criteria and a public process for maps the General Assembly draws (no commission)."),
    (125, "H4222"): ("core", T_REDIST, "The Anti-Gerrymandering Act: a multipartisan redistricting commission submitting plans to the General Assembly."),
    (124, "H4493"): ("adjacent", T_REDIST, "The actual 2021 House map: adopted the 2020 census and drew the new House districts (Act 117 of 2021)."),
    (124, "S865"):  ("adjacent", T_REDIST, "The actual 2022 Senate and congressional maps, drawn and passed by the General Assembly itself (Act 118 of 2022)."),
    (124, "H4492"): ("adjacent", T_REDIST, "The House's own 2022 congressional-map bill; sent back to committee when the maps moved through S865 instead."),
    (126, "H4717"): ("adjacent", T_REDIST, "Would have redrawn South Carolina's congressional districts mid-decade, starting with the 2026 election; died in House Judiciary."),
    (126, "H5683"): ("adjacent", T_REDIST, "The May 2026 mid-decade congressional redraw: passed the House 74-37 after dozens of amendment fights, then the Senate voted 26-18 to shelve it."),
    # ------------------------------------------------------------------
    # Financial disclosure and ethics enforcement.
    (126, "H3570"): ("core", T_DISCLOSE, "Rewrote who must disclose economic interests and how; passed the House 102-0 and the Senate 40-0 in different forms, then died in conference in the session's final days."),
    (123, "H4191"): ("core", T_DISCLOSE, "Would have tightened conflict-of-interest disclosure for legislators and expanded what a statement of economic interests must show."),
    (123, "S111"):  ("core", T_DISCLOSE, "Would have required officials to disclose speaking fees and event reimbursements on their statements of economic interests."),
    (123, "S339"):  ("core", T_DISCLOSE, "Would have required statewide officers and legislators to submit their income tax returns with their economic-interest filings."),
    (124, "S299"):  ("core", T_DISCLOSE, "Would have required statewide officers and legislators to submit their income tax returns with their economic-interest filings."),
    (125, "S169"):  ("core", T_DISCLOSE, "Would have required statewide officers and legislators to submit their income tax returns with their economic-interest filings."),
    (123, "H3435"): ("core", T_DISCLOSE, "Would have created an online campaign-account monitoring and auditing department at the State Ethics Commission."),
    (123, "S253"):  ("core", T_DISCLOSE, "Would have created an online campaign-account monitoring and auditing department at the State Ethics Commission."),
    (124, "S309"):  ("core", T_DISCLOSE, "Would have created an online campaign-account monitoring and auditing department at the State Ethics Commission."),
    (125, "S195"):  ("core", T_DISCLOSE, "Would have created an online campaign-account monitoring and auditing department at the State Ethics Commission."),
    (124, "S548"):  ("core", T_DISCLOSE, "Would have extended the ethics law and economic-interest filing to everyone elected or appointed to fee-charging special purpose districts."),
    (125, "S395"):  ("core", T_DISCLOSE, "Would have extended the ethics law and economic-interest filing to special purpose districts, and required the Ethics Commission to post its decisions online."),
    (123, "H3321"): ("core", T_DISCLOSE, "Would have barred anyone with unpaid ethics fines or unfiled ethics reports from running for office."),
    (124, "S188"):  ("core", T_DISCLOSE, "Would have barred anyone with outstanding debt to the ethics bodies from filing as a candidate."),
    (125, "S986"):  ("core", T_DISCLOSE, "Would have kept candidates off the ballot unless they declared ethics fines owed and enrolled in a payment plan, and reduced old fine balances to $5,000."),
    (126, "S75"):   ("core", T_DISCLOSE, "Would keep candidates off the ballot unless they declare ethics fines owed and enroll in a payment plan."),
    (123, "H3387"): ("core", T_DISCLOSE, "Would have made any ethics-law violation sufficient cause to remove an official from office."),
    (123, "S284"):  ("core", T_DISCLOSE, "Would have revised what legislative ethics committees may do with State Ethics Commission findings."),
    (124, "S375"):  ("core", T_DISCLOSE, "Would have revised what legislative ethics committees may do with State Ethics Commission findings."),
    (123, "H4193"): ("core", T_DISCLOSE, "Would have paused the statute of limitations once an ethics enforcement action begins."),
    (125, "H5181"): ("core", T_DISCLOSE, "Would have let ethics complaints be pursued past four years while the official stays in the same office."),
    (126, "S1130"): ("core", T_DISCLOSE, "Would apply the state's ethics, campaign-practices, and lobbying laws to political party chairmen."),
    (126, "S70"):   ("core", T_DISCLOSE, "The School Board Ethics Act (Act 191 of 2026): a required code of ethics and training for elected school board members - this set's one enacted ethics law."),
    (123, "H3579"): ("core", T_DISCLOSE, "Earlier school-board ethics design: a model code of ethics, nepotism policies, and conflict referrals to the Ethics Commission."),
    (123, "H4756"): ("core", T_DISCLOSE, "Earlier school-board ethics design led by the House Speaker: model code of ethics, nepotism policies, and conflict referrals."),
    (123, "S932"):  ("adjacent", T_DISCLOSE, "Would have required plain reporting manuals, administrative closure of stale filing cases, and annual ethics training."),
    (126, "H3321"): ("adjacent", T_DISCLOSE, "Would exempt unpaid appointed officials who raise no campaign funds from filing economic-interest statements - the one bill loosening a filing rule."),
    # ------------------------------------------------------------------
    # Lobbying rules.
    (126, "S632"):  ("core", T_LOBBY, "Would extend the lobbying law to lobbying of county and city governments and require an online list of registered lobbyists - filed by Senate leadership of both parties."),
    (123, "H3622"): ("core", T_LOBBY, "Would have extended the lobbying law to people paid to lobby county and municipal governments."),
    (124, "H5194"): ("core", T_LOBBY, "Would have extended lobbying registration and reporting to local government lobbying."),
    (123, "H3341"): ("core", T_LOBBY, "Would have widened the definitions of lobbying and doubled lobbyist registration fees."),
    (124, "H4876"): ("core", T_LOBBY, "The Close the Revolving Door Act: would have doubled (to two years) the wait before former officials can lobby their old colleagues."),
    (123, "H4240"): ("core", T_LOBBY, "Would have stretched the revolving-door wait from one year to five before former officials can become lobbyists."),
    (125, "H4585"): ("core", T_LOBBY, "Would have made former officials wait two years (and finish their full term) before they or family members lobby, and two years before legislators take judgeships."),
    (124, "H3920"): ("core", T_LOBBY, "Would have expanded lobbyist reporting and the ban on financial gains from lobbying contacts."),
    (125, "H3159"): ("core", T_LOBBY, "Would have expanded lobbyist reporting and the ban on financial gains from lobbying contacts."),
    (126, "H3475"): ("core", T_LOBBY, "Would require lobbyists to file extra reports on contacts with the Public Service Commission and Office of Regulatory Staff."),
    (124, "H3743"): ("adjacent", T_LOBBY, "Would have barred state agencies from spending public funds to hire contract lobbyists."),
    (125, "H4713"): ("adjacent", T_LOBBY, "Would have barred state agencies from spending public funds to hire contract lobbyists."),
    (124, "H3967"): ("adjacent", T_LOBBY, "Would have required school districts that hire lobbyists to notify parents and report the spending."),
    # ------------------------------------------------------------------
    # Open government: public records and meetings.
    (123, "H3259"): ("core", T_OPENGOV, "Would have removed the General Assembly's own broad exemption from the Freedom of Information Act."),
    (123, "H4791"): ("core", T_OPENGOV, "Would have made legislative caucuses 'public bodies' subject to FOIA."),
    (124, "H3402"): ("core", T_OPENGOV, "Would have made legislative caucuses 'public bodies' subject to FOIA."),
    (123, "H3448"): ("core", T_OPENGOV, "Would have created a FOIA Review Office in the Administrative Law Court to resolve records disputes."),
    (124, "H3254"): ("core", T_OPENGOV, "Would have created a FOIA review process in the Administrative Law Court."),
    (125, "H3327"): ("core", T_OPENGOV, "Would have set penalties for violating the Freedom of Information Act."),
    (126, "S6"):    ("core", T_OPENGOV, "Would give public bodies a five-day deadline to produce records, with silence counting as a denial and a violation."),
    (125, "H5143"): ("core", T_OPENGOV, "Would have opened more public-employee pay information to disclosure."),
    (124, "S396"):  ("core", T_OPENGOV, "Would have deleted the FOIA exemption that keeps government business-recruitment deals secret."),
    (125, "S232"):  ("core", T_OPENGOV, "Would have deleted the FOIA exemption that keeps government business-recruitment deals secret."),
    (126, "H3646"): ("core", T_OPENGOV, "The Meeting Transparency Act: would put every legislative committee meeting and school board meeting online."),
    (126, "H3200"): ("adjacent", T_OPENGOV, "Would require school boards to livestream their meetings."),
    (123, "S453"):  ("adjacent", T_OPENGOV, "Would have revised FOIA's disclosure exemptions."),
    (124, "H3622"): ("adjacent", T_OPENGOV, "Would have revised FOIA's exemptions."),
    (125, "H3465"): ("adjacent", T_OPENGOV, "Would have revised FOIA's exemptions."),
    (126, "H3161"): ("adjacent", T_OPENGOV, "Would revise FOIA's exemptions."),
    (126, "H4728"): ("adjacent", T_OPENGOV, "Would let legislators get public records free of charge for legislative work."),
    (126, "H3647"): ("adjacent", T_OPENGOV, "The Earmark Transparency Act: every budget earmark request put in writing on a public form."),
    (126, "H3648"): ("adjacent", T_OPENGOV, "The Budget Transparency Act: agencies must publish salary detail with their budget requests."),
    (126, "H3854"): ("adjacent", T_OPENGOV, "Would require organizations receiving state earmarks to file itemized public accountings, receipts included."),
    # ------------------------------------------------------------------
    # Civics and voter education. The REACH Act family is sourced from the
    # certified universe (title scan); its text carries none of the issue's
    # search terms.
    (126, "H3547"): ("core", T_CIVICS, "Would require every middle schooler to complete a civics unit and create the Palmetto Middle School Civics Challenge for student-led civics projects."),
    (124, "S38"):   ("core", T_CIVICS, "The REACH Act (Act 26 of 2021): every public college student must complete instruction on the founding documents - the one civics-instruction law passed in this record."),
    (123, "S35"):   ("core", T_CIVICS, "The REACH Act's first run: passed the Senate in 2019 and died in the House education committee."),
    (123, "H4296"): ("core", T_CIVICS, "House version of the REACH Act; died in its first committee."),
    (124, "H3338"): ("core", T_CIVICS, "House companion of the REACH Act; the Senate version became law instead."),
    (124, "H4392"): ("adjacent", T_CIVICS, "The Keep Partisanship Out of Civics Act: limits on topics, private funding, and lobbying credit in civics classes."),
    # ------------------------------------------------------------------
    # Direct democracy: recall, initiative, referendum.
    (124, "H3256"): ("core", T_DIRECT, "Proposed a constitutional amendment letting voters recall elected officials in state and local government."),
    (124, "S39"):   ("core", T_DIRECT, "Proposed a constitutional amendment creating initiative petition and referendum, so voters could enact or repeal laws directly."),
    (126, "S95"):   ("core", T_DIRECT, "Proposes a constitutional amendment creating a ballot-initiative process for enacting or repealing laws."),
    # ------------------------------------------------------------------
    # Related context (kept for audit; excluded from headline counts).
    (124, "S108"):  ("context", T_CONTEXT, "The 2022 Election Laws overhaul (Act 150 of 2022): created permanent two-week early voting and restructured election administration, unanimously."),
    (124, "S499"):  ("context", T_CONTEXT, "Election Commission restructuring (legislative oversight of the agency); passed the Senate and died in House Judiciary."),
    (125, "S1046"): ("context", T_CONTEXT, "Judicial Merit Selection Commission reform (Act 219 of 2024): changed how the state screens judges the General Assembly elects."),
    (123, "S337"):  ("context", T_CONTEXT, "Dual office holding rules."),
    (126, "H3999"): ("context", T_CONTEXT, "Constitutional amendment exempting unpaid positions from the dual-office-holding ban."),
    (123, "S83"):   ("context", T_CONTEXT, "Boards and Commissions Election Reform Act: screening for boards the General Assembly elects."),
    (125, "H4260"): ("context", T_CONTEXT, "Election-procedure package: paper poll books, observer rights, chain-of-custody records."),
    (125, "H5303"): ("context", T_CONTEXT, "Election-procedure package: electronic records access and hand-count audits."),
    (126, "H4513"): ("context", T_CONTEXT, "Election-procedure package: free records, observer rights, equipment chain-of-custody rules."),
    (124, "S887"):  ("context", T_CONTEXT, "Rules for South Carolina's delegates if an Article V convention is ever called."),
    (125, "S391"):  ("context", T_CONTEXT, "Rules for South Carolina's delegates if an Article V convention is ever called."),
    (126, "H3007"): ("context", T_CONTEXT, "Article V application for a balanced-budget-amendment convention; adopted by both chambers in January 2026."),
}

# Bills hand-added from the certified universe (not Pass 1 hits).
UNIVERSE_ADDS = {(123, "S35"), (123, "H4296"), (124, "S38"), (124, "H3338")}

EXCLUSION_RULES = [
    "Instrument is an honorary/ceremonial resolution (House, Senate, or Concurrent Resolution) - congratulations, memorials, and awareness days whose text mentions elections, voting, or civic service.",
    "Full-text-only hit where the matched term is incidental boilerplate - 'PAC' inside compact/impact/space (interstate licensure compacts, impact fees, C-PACE, Space Force), 'disclosure' in consumer/real-estate/criminal-record contexts, 'election' in corporate or tax elections, 'ethics' in medical-ethics bills.",
    "Election administration and voting mechanics outside the six constituent proposals: voter registration, early/absentee voting, voter ID, poll workers, precinct maps, election dates, protests, and audits (three transparency-package examples kept as context).",
    "County and school-district reapportionment housekeeping bills that redraw one local body's lines after the census (statewide who-draws-the-maps bills are kept).",
    "Judicial selection and judicial-election bills (JMSC cluster) - governance of the judiciary, not the elected-leader accountability proposals; the enacted 2024 JMSC reform is kept as context.",
    "Curriculum-content bills whose only tie is the word 'civics' in a broader education fight (Academic Integrity Act, Critical Race Theory, testing bills); civics-instruction bills are kept.",
    "Transparency-branded bills about private industries or courts (asbestos trusts, air ambulances, consumer legal funding, education curricula) rather than government accountability.",
    "Internal chamber housekeeping: officer elections, committee assignments, special orders, sine die resolutions (the chairmen-term-limit rule H4692 is kept as adjacent).",
]


def load_universe_bill(session, bill_no):
    with gzip.open(os.path.join(UNIVERSE, str(session), "bills.jsonl.gz"), "rt") as f:
        for line in f:
            b = json.loads(line)
            if b["bill_no"] == bill_no:
                return b
    raise SystemExit("universe bill not found: %s:%s" % (session, bill_no))


def main():
    pass1 = json.load(open(PASS1))
    bills = {(b["session"], b["bill_no"]): b for b in pass1["bills"]}
    missing = [k for k in KEEP if k not in bills and k not in UNIVERSE_ADDS]
    if missing:
        raise SystemExit("curation keys not in pass1: %r" % missing)

    kept = []
    for (session, bill_no), (tier, theme, plain) in sorted(KEEP.items()):
        key = (session, bill_no)
        if key in UNIVERSE_ADDS:
            u = load_universe_bill(session, bill_no)
            row = {
                "bill_key": "%s:%s" % (session, bill_no),
                "session": session, "bill_no": bill_no,
                "title": u["title"], "instrument_type": u["instrument_type"],
                "plain_topic": plain, "theme": theme, "relevance": tier,
                "found_by_terms": [], "source": "universe",
                "url": u["url"],
            }
        else:
            b = bills[key]
            row = {
                "bill_key": "%s:%s" % (session, bill_no),
                "session": session, "bill_no": bill_no,
                "title": b["title"], "instrument_type": b["instrument_type"],
                "plain_topic": plain, "theme": theme, "relevance": tier,
                "found_by_terms": b["found_by_terms"], "source": "pass1",
                "url": b["url"],
            }
        kept.append(row)

    counts = {"total_pass1": len(bills), "kept": len(kept),
              "universe_adds": len(UNIVERSE_ADDS),
              "by_relevance": {}, "by_theme": {}}
    for r in kept:
        counts["by_relevance"][r["relevance"]] = counts["by_relevance"].get(r["relevance"], 0) + 1
        counts["by_theme"][r["theme"]] = counts["by_theme"].get(r["theme"], 0) + 1
    counts["excluded"] = counts["total_pass1"] - (counts["kept"] - counts["universe_adds"])

    out = {
        "issue": pass1["issue"],
        "note": ("Hand curation of the keep-all Pass 1 discovery (nothing was dropped upstream). "
                 "Tiers: core = bills squarely on the six constituent proposals plus the ethics/"
                 "campaign-finance/open-government accountability agenda; adjacent = same lanes "
                 "but narrower, procedural, federal-target, or deregulatory; context = kept for "
                 "audit only, excluded from headline counts. Ambiguous bills verified against "
                 "latest-version full text in _universe/. Four REACH Act civics bills were "
                 "hand-added from the certified universe (marked source=universe) because their "
                 "text contains none of the issue's search terms. All other Pass 1 hits are "
                 "excluded under the rules below."),
        "themes": THEMES,
        "counts": counts,
        "exclusion_rules": EXCLUSION_RULES,
        "bills": kept,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("kept", len(kept), "|", counts["by_relevance"])
    for t in THEMES:
        print("  %-52s %d" % (t, counts["by_theme"].get(t, 0)))


if __name__ == "__main__":
    main()
