#!/usr/bin/env python3
"""Curate the keep-all Pass 1 set for south-carolina-04-slow-wage-growth.

Pass 1 kept every full-text/title hit (5,744 bills). This script encodes the
hand review: which bills belong to the issue set (core / adjacent / context),
one plain sentence and a citizen-facing theme per kept bill, and the explicit
exclusion rules for everything else. Ambiguous bills were verified against
their latest-version full text in sources/south-carolina/_universe/.

Output: working/south-carolina/slow-wage-growth/curation-map.json
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PASS1 = os.path.join(ROOT, "sources/south-carolina/slow-wage-growth/pass1/bills.json")
OUT = os.path.join(HERE, "curation-map.json")

T_MINWAGE = "Creating a state minimum wage"
T_GROUPS = "Wage floors for specific groups"
T_APPRENTICE = "Apprenticeships and hiring tax credits"
T_WORKFORCE = "Career training, technical colleges, and workforce programs"
T_INCENTIVE = "Employer incentives tied to pay"
T_EQUALPAY = "Equal pay for equal work"
T_TAKEHOME = "Take-home pay: overtime rules and taxes"
T_JOBRULES = "Other pay and job-rules bills"
T_CONTEXT = "Related context"

THEMES = [T_MINWAGE, T_GROUPS, T_APPRENTICE, T_WORKFORCE, T_INCENTIVE,
          T_EQUALPAY, T_TAKEHOME, T_JOBRULES, T_CONTEXT]

# (session, bill_no): (tier, theme, plain_topic)
KEEP = {
    # ------------------------------------------------------------------
    # Creating a state minimum wage (SC has no state minimum wage; these
    # bills would create one, raise it, or build wage-setting machinery).
    # Dollar figures verified against latest-version bill text.
    (123, "H3114"): ("core", T_MINWAGE, "Would have set a state minimum wage of $10.10 an hour (or the federal rate if higher) and let local governments go higher."),
    (123, "H3217"): ("core", T_MINWAGE, "Would have phased in a state minimum wage of $10.10 an hour over three years, with automatic yearly adjustments."),
    (123, "H3395"): ("core", T_MINWAGE, "Would have phased in a state minimum wage of $12 an hour over three years, with automatic yearly adjustments."),
    (123, "H3467"): ("core", T_MINWAGE, "Would have set a state minimum wage of $13 an hour (or the federal rate if higher) and let local governments go higher."),
    (123, "H4154"): ("core", T_MINWAGE, "Would have set a state minimum wage of $17 an hour starting January 2020."),
    (123, "S147"):  ("core", T_MINWAGE, "Proposed a state constitutional amendment creating a mandatory minimum wage, enforceable in court."),
    (123, "S149"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage adjusted for inflation each year by the state workforce agency."),
    (124, "H3018"): ("core", T_MINWAGE, "Would have phased in a state minimum wage of $10.10 an hour over three years, with automatic yearly adjustments."),
    (124, "H3184"): ("core", T_MINWAGE, "Would have phased in a state minimum wage of $15 an hour over three years, with automatic yearly adjustments."),
    (124, "H3341"): ("core", T_MINWAGE, "Would have set a state minimum wage of $15 an hour (or the federal rate if higher) and let local governments go higher."),
    (124, "H3480"): ("core", T_MINWAGE, "Would have set a state minimum wage of $13 an hour (or the federal rate if higher) and let local governments go higher."),
    (124, "H3675"): ("core", T_MINWAGE, "Would have set a state minimum wage of $17 an hour starting January 2022."),
    (124, "S159"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage adjusted for inflation each year by the state workforce agency."),
    (124, "S343"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage adjusted for inflation each year by the state workforce agency."),
    (124, "S633"):  ("core", T_MINWAGE, "Would have put an advisory question on the 2022 ballot asking voters whether to raise the minimum wage."),
    (124, "S634"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage with anti-retaliation protections for workers."),
    (125, "H3805"): ("core", T_MINWAGE, "Would have set a state minimum wage of $17 an hour starting January 2025."),
    (125, "H5187"): ("core", T_MINWAGE, "Would have set a state minimum wage of $10 an hour (or the federal rate if higher)."),
    (125, "S216"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage adjusted for inflation each year by the state workforce agency."),
    (125, "S28"):   ("core", T_MINWAGE, "Would have put an advisory question on the 2024 ballot asking voters whether to raise the minimum wage."),
    (125, "S291"):  ("core", T_MINWAGE, "The SC Minimum Wage Act: a state minimum wage with anti-retaliation protections for workers."),
    (126, "H3226"): ("core", T_MINWAGE, "Would phase in a state minimum wage of $10.10 an hour over three years, with automatic yearly adjustments."),
    (126, "H3809"): ("core", T_MINWAGE, "Would set a state minimum wage of $17 an hour starting January 2027."),
    (126, "H3735"): ("core", T_MINWAGE, "The Wage Board Act: would let the state workforce agency convene boards that set minimum pay rates by occupation."),
    # ------------------------------------------------------------------
    # Wage floors for specific groups (verified in full text: disability
    # subminimum-wage ban; inmate pay floors).
    (124, "S533"):  ("core", T_GROUPS, "Banned paying workers with disabilities less than the federal minimum wage under FLSA Section 14(c), and enacted the Employment First Initiative Act."),
    (123, "H4768"): ("core", T_GROUPS, "The Employment First Initiative Act: state policy supporting competitive, integrated employment for people with disabilities."),
    (124, "H3244"): ("core", T_GROUPS, "The Employment First Initiative Act (House version); its content ultimately became law through S533."),
    (125, "S1001"): ("core", T_GROUPS, "Requires that inmates working in private-industry prison programs earn at least the federal minimum wage."),
    (123, "H5061"): ("adjacent", T_GROUPS, "Would have set pay rules for inmate labor."),
    (123, "H3686"): ("adjacent", T_GROUPS, "Would have changed inmate employment rules in prison industry programs."),
    (124, "H4050"): ("adjacent", T_GROUPS, "Would have set pay rules for inmate labor."),
    (124, "H4154"): ("adjacent", T_GROUPS, "Would have changed inmate employment and pay rules."),
    (125, "H3575"): ("adjacent", T_GROUPS, "Would have reorganized the prison industries program (pay provisions included)."),
    (126, "H3559"): ("adjacent", T_GROUPS, "Would set pay rules for inmate labor."),
    (126, "H5357"): ("adjacent", T_GROUPS, "Would set a minimum wage for inmate workers."),
    # ------------------------------------------------------------------
    # Apprenticeships and hiring tax credits (all verified in full text).
    (125, "H3605"): ("core", T_APPRENTICE, "The Earn and Learn Act: connects students to registered apprenticeships and work-based learning for credit."),
    (125, "S557"):  ("core", T_APPRENTICE, "Raised the state apprenticeship tax credit and let employers claim it for more years."),
    (124, "H3348"): ("core", T_APPRENTICE, "Would have created tax credits for employers who hire formerly incarcerated people or veterans into apprenticeship programs."),
    (125, "H4600"): ("core", T_APPRENTICE, "Would have tightened the apprenticeship hiring credit for formerly incarcerated workers (sex-offender registry exclusion)."),
    (125, "S859"):  ("core", T_APPRENTICE, "The State Employment Skills-Based Hiring Act: state jobs open to skills and experience, not just degrees."),
    (126, "H3479"): ("core", T_APPRENTICE, "The Skills-Based Hiring Act: state jobs open to skills and experience, not just degrees."),
    (126, "S272"):  ("core", T_APPRENTICE, "Skills-based hiring for state government jobs."),
    # ------------------------------------------------------------------
    # Career training, technical colleges, and workforce programs.
    (123, "H3576"): ("core", T_WORKFORCE, "Would have created the SC Workforce Industry Needs Scholarship (SC WINS) for technical college students in high-demand fields."),
    (123, "H3759"): ("core", T_WORKFORCE, "SC Career Opportunity and Access for All: a statewide plan tying education to career pathways and workforce needs."),
    (123, "S419"):  ("core", T_WORKFORCE, "SC Career Opportunity and Access for All Act (Senate version): education-to-workforce overhaul with career pathways."),
    (123, "H4022"): ("core", T_WORKFORCE, "The Workforce Education Act: a five-year workforce-education school pilot run by the technical college board."),
    (123, "H3757"): ("core", T_WORKFORCE, "Would have created a Workforce and Education Data Oversight Committee to track education-to-job results."),
    (123, "S650"):  ("core", T_WORKFORCE, "Would have created a workforce diploma program for adults to finish high school with job-ready skills."),
    (124, "H3144"): ("core", T_WORKFORCE, "Created the SC Workforce Industry Needs Scholarship (SC WINS) in statute for technical college students in high-demand fields."),
    (124, "H3611"): ("core", T_WORKFORCE, "Would have created a Workforce and Education Data Oversight Committee to track education-to-job results."),
    (124, "H4766"): ("core", T_WORKFORCE, "Restructured the Coordinating Council for Workforce Development: new membership and duties."),
    (125, "H3726"): ("core", T_WORKFORCE, "The Statewide Education and Workforce Development Act: created the Office of Statewide Workforce Development and a unified state workforce plan."),
    (125, "H4060"): ("core", T_WORKFORCE, "Education and workforce readiness: would have aligned K-12 with workforce preparation."),
    (125, "S461"):  ("core", T_WORKFORCE, "Would have required tracking of post-secondary degrees and industry credentials against workforce needs."),
    (126, "H3197"): ("core", T_WORKFORCE, "Workforce readiness: would build employability skills and career readiness into K-12 education."),
    (126, "H3863"): ("core", T_WORKFORCE, "The SC STEM Opportunity Act: expands STEM education pathways toward workforce needs."),
    (126, "H4984"): ("core", T_WORKFORCE, "The Dual Enrollment Opportunity Act: would widen high-school access to college and technical courses."),
    (126, "H3225"): ("core", T_WORKFORCE, "The SC Service Year Act: a paid service-year program for young adults with education and workforce on-ramps."),
    (123, "H4414"): ("adjacent", T_WORKFORCE, "Would have expanded dual enrollment in high school."),
    (124, "H3470"): ("adjacent", T_WORKFORCE, "Would have expanded dual enrollment in high school."),
    (125, "H3326"): ("adjacent", T_WORKFORCE, "Would have expanded dual enrollment in high school."),
    (125, "H3783"): ("adjacent", T_WORKFORCE, "Made the Department of Employment and Workforce part of the restructured executive branch (agency governance)."),
    (125, "S546"):  ("adjacent", T_WORKFORCE, "Would have restructured the Department of Employment and Workforce."),
    (126, "S279"):  ("adjacent", T_WORKFORCE, "Would restructure the Department of Employment and Workforce."),
    # ------------------------------------------------------------------
    # Employer incentives tied to pay (all verified in full text).
    (126, "H4603"): ("core", T_INCENTIVE, "The Small Business Livable Wage Tax Credit Act: an income tax credit for small employers who pay at or above a livable wage."),
    (124, "S398"):  ("core", T_INCENTIVE, "Would have required companies receiving state development subsidies to meet job-creation, wage, and health-care obligations, with clawbacks."),
    (126, "H4245"): ("core", T_INCENTIVE, "The Workforce Advancement and Taxpayer Reinvestment Act: tax relief for people moving off government assistance and credits for businesses that hire and retain them."),
    (126, "H4174"): ("adjacent", T_INCENTIVE, "Would change job development credits (the state's wage-linked hiring incentive)."),
    (124, "S901"):  ("adjacent", T_INCENTIVE, "Tax package that included changes to job development credits (the state's wage-linked hiring incentive)."),
    (125, "H4087"): ("adjacent", T_INCENTIVE, "Tax-credit package: corporate headquarters credit staffing rules and job development credit updates."),
    (124, "H3774"): ("adjacent", T_INCENTIVE, "Would have extended Enterprise Zone Act tax credits to professional employer organizations."),
    (124, "S489"):  ("adjacent", T_INCENTIVE, "Would have extended Enterprise Zone Act tax credits to professional employer organizations."),
    (124, "H4252"): ("adjacent", T_INCENTIVE, "The Redline Enterprise Zone Act: targeted hiring and investment incentives for historically redlined areas."),
    (126, "H5471"): ("adjacent", T_INCENTIVE, "Would create a Headquarters Relocation and Growth Fund granting money to businesses that move or expand headquarters here."),
    (126, "S1118"): ("adjacent", T_INCENTIVE, "Would create a Headquarters Relocation and Growth Fund granting money to businesses that move or expand headquarters here."),
    # ------------------------------------------------------------------
    # Equal pay for equal work (adjacent: wage fairness, not wage growth).
    (123, "H3139"): ("adjacent", T_EQUALPAY, "The SC Equal Pay for Equal Work Act: equal pay regardless of sex or race, with enforcement."),
    (123, "H3615"): ("adjacent", T_EQUALPAY, "The Act to Establish Pay Equity: equal pay rules and pay-history protections."),
    (123, "S372"):  ("adjacent", T_EQUALPAY, "The Act to Establish Pay Equity: equal pay rules and pay-history protections."),
    (124, "H3183"): ("adjacent", T_EQUALPAY, "The Act to Establish Pay Equity: equal pay rules and pay-history protections."),
    (124, "H3188"): ("adjacent", T_EQUALPAY, "The SC Equal Pay for Equal Work Act: equal pay regardless of sex or race, with enforcement."),
    (124, "H3922"): ("adjacent", T_EQUALPAY, "Equal pay for equal work for state employees."),
    (124, "S514"):  ("adjacent", T_EQUALPAY, "The Act to Establish Pay Equity: equal pay rules and pay-history protections."),
    (125, "H3148"): ("adjacent", T_EQUALPAY, "Equal pay for equal work for state employees."),
    (125, "H3428"): ("adjacent", T_EQUALPAY, "Equal pay: would bar pay discrimination and protect pay disclosure."),
    (125, "H4212"): ("adjacent", T_EQUALPAY, "Pay equity: equal pay rules and pay-history protections."),
    (126, "H3512"): ("adjacent", T_EQUALPAY, "Equal pay for equal work for state employees."),
    # ------------------------------------------------------------------
    # Take-home pay: overtime rules and taxes.
    (125, "H3450"): ("adjacent", T_TAKEHOME, "Would have exempted overtime pay from state income tax."),
    (125, "H4811"): ("adjacent", T_TAKEHOME, "Would have exempted overtime pay from state income tax."),
    (126, "H3298"): ("adjacent", T_TAKEHOME, "Would exempt overtime pay from state income tax."),
    (126, "H3368"): ("adjacent", T_TAKEHOME, "Would exempt overtime pay from state income tax; passed the House, then failed on the Senate floor."),
    (126, "H3793"): ("adjacent", T_TAKEHOME, "Would exempt overtime pay from state income tax."),
    (126, "H4751"): ("adjacent", T_TAKEHOME, "Would require overtime pay after eight hours in a workday, with exceptions."),
    # ------------------------------------------------------------------
    # Other pay and job-rules bills.
    (124, "H3469"): ("adjacent", T_JOBRULES, "The SC Paid Sick Leave Act: earned paid sick leave for workers."),
    (125, "S700"):  ("adjacent", T_JOBRULES, "Set consumer rules for earned-wage-access services (early access to earned pay)."),
    (123, "S549"):  ("adjacent", T_JOBRULES, "The Workforce Opportunity Act: 'ban the box' — the state could not ask about criminal history until later in hiring."),
    (125, "S25"):   ("adjacent", T_JOBRULES, "The Workforce Opportunity Act: 'ban the box' — the state could not ask about criminal history until later in hiring."),
    (123, "H3389"): ("adjacent", T_JOBRULES, "Would have created a study committee on people with felony records reentering the workforce."),
    (124, "H3045"): ("adjacent", T_JOBRULES, "Would have created a study committee on people with felony records reentering the workforce."),
    (125, "H3351"): ("adjacent", T_JOBRULES, "Would have created a study committee on people with felony records reentering the workforce."),
    (124, "H3247"): ("adjacent", T_JOBRULES, "The Workforce Enhancement and Military Recognition Act: exempted all military retirement pay from state income tax to draw retirees into the workforce."),
    (123, "H3135"): ("adjacent", T_JOBRULES, "Workforce Enhancement and Military Recognition Act (earlier version): military retirement pay tax exemption."),
    (123, "S179"):  ("adjacent", T_JOBRULES, "Workforce Enhancement and Military Recognition Act (earlier version): military retirement pay tax exemption."),
    (124, "S217"):  ("adjacent", T_JOBRULES, "Workforce Enhancement and Military Recognition Act (companion version): military retirement pay tax exemption."),
    (124, "S986"):  ("adjacent", T_JOBRULES, "Workforce Enhancement and Military Recognition Act (companion version): military retirement pay tax exemption."),
    (124, "H4140"): ("adjacent", T_JOBRULES, "Would have raised pay for public school support staff."),
    (126, "H3583"): ("adjacent", T_JOBRULES, "Would raise pay for public school support staff."),
    # ------------------------------------------------------------------
    # Related context (kept for audit; excluded from headline counts).
    (123, "S1271"): ("context", T_CONTEXT, "Unemployment benefits: weekly benefit amount."),
    (124, "H3345"): ("context", T_CONTEXT, "Unemployment insurance changes."),
    (124, "S347"):  ("context", T_CONTEXT, "Unemployment benefits changes."),
    (124, "S421"):  ("context", T_CONTEXT, "Unemployment security benefits update (became law)."),
    (124, "S922"):  ("context", T_CONTEXT, "Unemployment benefits eligibility."),
    (124, "S1090"): ("context", T_CONTEXT, "Unemployment benefits update (became law)."),
    (124, "S1091"): ("context", T_CONTEXT, "Delinquent unemployment tax rates."),
    (125, "H3992"): ("context", T_CONTEXT, "Delinquent unemployment tax rates (became law)."),
    (125, "S151"):  ("context", T_CONTEXT, "Unemployment insurance eligibility period."),
    (125, "S217"):  ("context", T_CONTEXT, "Unemployment benefits changes."),
    (125, "H4439"): ("context", T_CONTEXT, "Unemployment insurance changes."),
    (126, "H4744"): ("context", T_CONTEXT, "Department of Employment and Workforce communications requirements."),
    (126, "H4745"): ("context", T_CONTEXT, "Unemployment insurance tax rate lookback period."),
    (123, "H3786"): ("context", T_CONTEXT, "Workplace Freedom Act (right-to-work provisions)."),
    (126, "H3734"): ("context", T_CONTEXT, "Would allow collective bargaining by political subdivisions."),
    (124, "S16"):   ("context", T_CONTEXT, "High school graduation requirements (career-readiness related)."),
    (124, "H3612"): ("context", T_CONTEXT, "Computer science education initiative (career pathways in K-12)."),
    (125, "H4702"): ("context", T_CONTEXT, "Computer science education initiative (career pathways in K-12)."),
    (126, "H3201"): ("context", T_CONTEXT, "Computer science education initiative (career pathways in K-12)."),
    (124, "H5158"): ("context", T_CONTEXT, "SC STEM Coalition (STEM workforce pipeline)."),
    (124, "S1247"): ("context", T_CONTEXT, "SC STEM Coalition (STEM workforce pipeline)."),
    (126, "H4394"): ("context", T_CONTEXT, "Childcare support (workforce participation)."),
    (126, "S770"):  ("context", T_CONTEXT, "Childcare Assistance Program (workforce participation)."),
    (123, "H3105"): ("context", T_CONTEXT, "Technical college enterprise campus authorities (governance)."),
    (123, "S228"):  ("context", T_CONTEXT, "Technical college enterprise campus authorities (became law; governance)."),
    (125, "H5105"): ("context", T_CONTEXT, "Technical college credit transfer."),
    (123, "H4755"): ("context", T_CONTEXT, "Technical college admissions standards."),
}

EXCLUSION_RULES = [
    "Instrument is an honorary/ceremonial resolution (House, Senate, or Concurrent Resolution) — congratulations, memorials, and awareness days that only mention workforce or apprenticeship language.",
    "Full-text-only hit where the matched term is incidental boilerplate (e.g. 'pay', 'labor', 'income', 'salary' inside unrelated subject matter such as sentencing reform, alimony, HOAs, utility regulation, or recycling).",
    "Occupational-licensing bills (midwives, barbers, physician assistants, accountants, appraisers, funeral apprentices) whose only tie is 'apprentice' as a licensure pathway term.",
    "Housing bills branded 'workforce housing' (belong to a housing issue set, not wage growth).",
    "Anti-discrimination and unrelated education-governance bills whose hit terms are incidental.",
    "Local technical-college commission membership housekeeping bills (kept only where campus/governance change was substantive).",
]


def main():
    pass1 = json.load(open(PASS1))
    bills = {(b["session"], b["bill_no"]): b for b in pass1["bills"]}
    missing = [k for k in KEEP if k not in bills]
    if missing:
        raise SystemExit("curation keys not in pass1: %r" % missing)

    kept = []
    for (session, bill_no), (tier, theme, plain) in sorted(KEEP.items()):
        b = bills[(session, bill_no)]
        kept.append({
            "bill_key": "%s:%s" % (session, bill_no),
            "session": session,
            "bill_no": bill_no,
            "title": b["title"],
            "instrument_type": b["instrument_type"],
            "plain_topic": plain,
            "theme": theme,
            "relevance": tier,
            "found_by_terms": b["found_by_terms"],
            "url": b["url"],
        })

    counts = {"total_pass1": len(bills), "kept": len(kept),
              "by_relevance": {}, "by_theme": {}}
    for r in kept:
        counts["by_relevance"][r["relevance"]] = counts["by_relevance"].get(r["relevance"], 0) + 1
        counts["by_theme"][r["theme"]] = counts["by_theme"].get(r["theme"], 0) + 1
    counts["excluded"] = counts["total_pass1"] - counts["kept"]

    out = {
        "issue": pass1["issue"],
        "note": ("Hand curation of the keep-all Pass 1 discovery (nothing was dropped upstream). "
                 "Tiers: core = the issue's headline set (minimum wage, wage floors for specific groups, "
                 "apprenticeships/hiring credits, workforce programs, employer pay incentives); "
                 "adjacent = wage-related but outside the four constituent proposals "
                 "(equal pay, overtime, job rules, inmate pay, incentive machinery); "
                 "context = kept for audit only, excluded from headline counts. "
                 "Ambiguous bills verified against latest-version full text in _universe/. "
                 "All other Pass 1 hits are excluded under the rules below."),
        "themes": THEMES,
        "counts": counts,
        "exclusion_rules": EXCLUSION_RULES,
        "bills": kept,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("kept", len(kept), "of", len(bills), "|", counts["by_relevance"])
    for t in THEMES:
        print("  %-55s %d" % (t, counts["by_theme"].get(t, 0)))


if __name__ == "__main__":
    main()
