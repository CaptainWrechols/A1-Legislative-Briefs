#!/usr/bin/env python3
"""Curate the keep-all Pass 1 set for south-carolina-03-rising-cost-of-living.

Pass 1 kept every full-text/title hit (6,814 bills — the broadest of the four
SC issues, because 'rent' matches 'parental', 'insurance' matches every health
insurance mandate, and 'utility' matches utility-terrain vehicles). This
script encodes the hand review: which bills belong to the issue set
(core / adjacent / context), one plain sentence and a citizen-facing theme
per kept bill, and the explicit exclusion rules for everything else.
Ambiguous and headline bills were verified against their latest-version full
text in sources/south-carolina/_universe/.

Two bills relevant to the financial-education proposal did not match any
Pass 1 search term and were found by a hand full-text scan of the certified
universe ('personal finance'); they are added from the universe with
provenance marked (see UNIVERSE_ADD).

Output: working/south-carolina/rising-cost-of-living/curation-map.json
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PASS1 = os.path.join(ROOT, "sources/south-carolina/rising-cost-of-living/pass1/bills.json")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")
OUT = os.path.join(HERE, "curation-map.json")

T_RATES = "How electric and gas rates are watched and set"
T_SANTEE = "Santee Cooper, the state-owned utility"
T_ENERGY = "Big energy bills that set the rate rules"
T_COMP = "Opening the electricity market to competition"
T_BILLS = "Utility bills, fees, and shutoffs"
T_FINED = "Money skills in school"
T_HOMETAX = "Property taxes on homes"
T_VEHTAX = "Taxes on vehicles and boats"
T_INCTAX = "Income and sales tax relief"
T_HOUSING = "Housing costs and rent"
T_INS = "Home and property insurance costs"
T_CHILDCARE = "Child care costs and assistance"
T_CONTEXT = "Related context"

THEMES = [T_RATES, T_SANTEE, T_ENERGY, T_COMP, T_BILLS, T_FINED,
          T_HOMETAX, T_VEHTAX, T_INCTAX, T_HOUSING, T_INS, T_CHILDCARE,
          T_CONTEXT]

# (session, bill_no): (tier, theme, plain_topic)
KEEP = {
    # ------------------------------------------------------------------
    # How electric and gas rates are watched and set [P-utility-transparency]
    # (PSC reform, conflict-of-interest and disclosure rules, ratepayer
    # protection acts, PSC elections). Headliners verified in full text.
    (123, "H4260"): ("core", T_RATES, "The SC Ratepayer Protection Act of 2019: whistleblower protections for utility employees, tighter conflict-of-interest rules for utility regulators, and a ban on utilities giving campaign contributions or anything of value to the legislators' committee that screens utility regulators."),
    (124, "H3683"): ("core", T_RATES, "Refile of the 2019 Ratepayer Protection Act: whistleblower protections plus conflict-of-interest, gift, and campaign-contribution bans around utility regulators."),
    (124, "H4149"): ("core", T_RATES, "Whistleblower protections for utility employees who report wrongdoing to the state's utility watchdog."),
    (125, "H3614"): ("core", T_RATES, "The Rate Payer Protection Act of 2023: whistleblower protections for utility employees who report waste or wrongdoing."),
    (124, "S344"):  ("core", T_RATES, "Would have made the Public Service Commission pause utility rate-increase requests during a declared state of emergency."),
    (125, "S218"):  ("core", T_RATES, "Would have made the Public Service Commission pause utility rate-increase requests during a declared state of emergency."),
    (123, "H3642"): ("core", T_RATES, "Would have replaced the legislative panel that screens utility regulators with a new Utility Oversight Committee."),
    (123, "H3641"): ("core", T_RATES, "Would have revised who sits on the Public Service Commission and required training for commissioners."),
    (123, "H4531"): ("core", T_RATES, "Would have made the seven Public Service Commission seats publicly elected statewide starting in 2022."),
    (123, "H4194"): ("core", T_RATES, "Rules for reimbursing Public Service Commission members' outside activities."),
    (123, "H4776"): ("core", T_RATES, "Would have extended the ban on former utility regulators going to work for utilities from one year to three."),
    (123, "H4809"): ("core", T_RATES, "Would have extended the ban on former utility regulators going to work for utilities from one year to four."),
    (123, "S947"):  ("core", T_RATES, "Would have extended the ban on former utility regulators going to work for utilities from one year to four."),
    (123, "S996"):  ("core", T_RATES, "Made the legislative screening panel reopen and extend the application window for four Public Service Commission seats."),
    (125, "S749"):  ("core", T_RATES, "Would have let the General Assembly go ahead with Public Service Commission screening and elections during 2023-24 despite a redistricting-litigation hold."),
    (126, "S271"):  ("core", T_RATES, "Let the General Assembly conduct Public Service Commission screening and elections in 2025; commissioners had been serving on expired terms."),
    (126, "H4402"): ("core", T_RATES, "Companion measure letting the General Assembly conduct Public Service Commission screening and elections in 2025."),
    (125, "S779"):  ("core", T_RATES, "The Energy Independence and Risk Reduction Act: would have shrunk the Public Service Commission from seven to five statewide seats and required the commission to publish reasons for its decisions on a deadline."),
    (125, "S909"):  ("core", T_RATES, "Energy Reform: would have shrunk the Public Service Commission from seven to five members and set new rules for how the commission issues orders and decisions."),
    (123, "S1129"): ("core", T_RATES, "Would have tightened qualifications and term limits for the Santee Cooper board and revised the Office of Regulatory Staff's role."),
    (126, "H5283"): ("core", T_RATES, "Would create a South Carolina Utility Citizens Council — an independent citizen advisory body to the Public Service Commission, funded by the regulated utilities."),
    (126, "H5282"): ("core", T_RATES, "The Utility Billing Accountability and Consumer Protection Act: utilities could not change billing or payment practices without Public Service Commission approval, with quarterly reports and an independent audit."),
    # ------------------------------------------------------------------
    # Santee Cooper, the state-owned utility (post-V.C. Summer).
    (123, "H4287"): ("core", T_SANTEE, "Set up the process for taking bids to sell some or all of Santee Cooper — and for reform proposals instead of a sale — after the V.C. Summer nuclear project failed."),
    (123, "S678"):  ("core", T_SANTEE, "Would have directed the governor to run a competitive bidding process to sell Santee Cooper."),
    (123, "H5335"): ("core", T_SANTEE, "Would have authorized selling Santee Cooper's assets or bringing in outside management, with a special legislative committee to oversee it."),
    (123, "H3751"): ("core", T_SANTEE, "Would have replaced the entire Santee Cooper board and created a Rate Reduction and Stabilization Fund for its customers."),
    (123, "S1163"): ("core", T_SANTEE, "Would have removed the Santee Cooper board and put an interim board and new oversight structure in place."),
    (124, "H3194"): ("core", T_SANTEE, "The 2021 Santee Cooper reform law: a rebuilt board, new qualifications, and — for the first time — Public Service Commission review of Santee Cooper's rates."),
    (124, "S464"):  ("core", T_SANTEE, "Would have set board term limits and qualifications for Santee Cooper and revised oversight of the authority."),
    (124, "S439"):  ("core", T_SANTEE, "Would have forced Santee Cooper to sell all its power plants by 2025 and hand its transmission lines to a regional grid operator."),
    (126, "S12"):   ("core", T_SANTEE, "Would let Santee Cooper jointly own power plants and transmission lines with private utilities — the vehicle discussed for restarting the V.C. Summer nuclear site."),
    (126, "S51"):   ("core", T_SANTEE, "Told Santee Cooper to seek proposals from companies interested in finishing the abandoned V.C. Summer nuclear reactors."),
    (126, "H4007"): ("core", T_SANTEE, "Would have authorized Santee Cooper construction of new generation capacity."),
    # ------------------------------------------------------------------
    # Big energy bills that set the rate rules.
    (123, "H3659"): ("core", T_ENERGY, "The Energy Freedom Act: opened solar-contract terms to review, listed rights every electric customer has, and reworked rooftop-solar billing after the V.C. Summer collapse."),
    (123, "S332"):  ("core", T_ENERGY, "The Clean Energy Access Act: customer rights and competitive procurement rules for electric utilities' power purchases."),
    (123, "S137"):  ("core", T_ENERGY, "Would have tied electric utilities' revenue to performance targets, with penalties, instead of guaranteed returns."),
    (123, "S620"):  ("core", T_ENERGY, "Would have required every electric provider to file a long-range power plan (integrated resource plan) at least every three years."),
    (123, "H3748"): ("adjacent", T_ENERGY, "Would have set new rooftop-solar (net metering) rates and procedures."),
    (123, "S657"):  ("adjacent", T_ENERGY, "Would have kept rooftop-solar billing credits available first-come, first-served while the legislature worked on the Energy Freedom Act."),
    (124, "S751"):  ("adjacent", T_ENERGY, "Would have adjusted solar-choice metering rules on who pays for rooftop-solar cost shifts."),
    (123, "S110"):  ("adjacent", T_ENERGY, "Would have let the Public Service Commission approve low-interest bonds to refinance storm or abandoned-project costs, lowering what customers pay."),
    (123, "H4206"): ("adjacent", T_ENERGY, "Would have let the Public Service Commission approve low-interest bonds to refinance storm or abandoned-project costs, lowering what customers pay."),
    (124, "S132"):  ("adjacent", T_ENERGY, "Would have let the Public Service Commission approve low-interest bonds to refinance storm or abandoned-project costs, lowering what customers pay."),
    (124, "H5162"): ("core", T_ENERGY, "The Extreme Weather and Energy Transition Ratepayer Protection Act: low-interest 'ratepayer protection bonds' to cut the storm and plant-closure costs rolled into electric rates."),
    (125, "H5118"): ("core", T_ENERGY, "The big 2024 energy bill: faster power-plant approvals (including a Santee Cooper/Dominion gas plant), changes to rate proceedings, and economic-development provisions."),
    (126, "H3309"): ("core", T_ENERGY, "The SC Energy Security Act of 2025: cleared the way for new power plants (including the Canadys gas plant), let customers speak as public witnesses at the Public Service Commission, and set schedules for rate cases."),
    (126, "H3928"): ("core", T_ENERGY, "The Electric Rate Stabilization Act: yearly rate reviews instead of big multi-year rate cases, promoted as smoothing rate increases."),
    (126, "S446"):  ("core", T_ENERGY, "The Electric Rate Stabilization Act (Senate version): yearly rate reviews instead of big multi-year rate cases."),
    (123, "S907"):  ("adjacent", T_ENERGY, "Would have reworked the Natural Gas Rate Stabilization Act — the mechanism that lets gas utilities adjust rates yearly outside full rate cases."),
    (124, "S244"):  ("adjacent", T_ENERGY, "Would have reworked the Natural Gas Rate Stabilization Act — the mechanism that lets gas utilities adjust rates yearly outside full rate cases."),
    (125, "S152"):  ("adjacent", T_ENERGY, "Would have reworked the Natural Gas Rate Stabilization Act — the mechanism that lets gas utilities adjust rates yearly outside full rate cases."),
    (126, "S93"):   ("adjacent", T_ENERGY, "Would rework the Natural Gas Rate Stabilization Act — the mechanism that lets gas utilities adjust rates yearly outside full rate cases."),
    (126, "H5484"): ("core", T_ENERGY, "The Energy Affordability Act: demand-side pilot programs, public comment on energy-infrastructure permits, and landowner notice before eminent domain."),
    (126, "S784"):  ("core", T_ENERGY, "Senate companion to the Energy Affordability Act: demand-side pilots and public-comment requirements for energy projects."),
    # ------------------------------------------------------------------
    # Opening the electricity market to competition [P-utility-competition].
    (123, "H4940"): ("core", T_COMP, "Created the Electricity Market Reform Measures Study Committee — an official study, with an independent expert consultant, of electricity-market reforms and their potential public benefits."),
    (123, "S998"):  ("core", T_COMP, "Senate version of the electricity-market-reform study committee."),
    (123, "H3344"): ("adjacent", T_COMP, "Would have let businesses take electric service from a supplier other than the one assigned to their territory."),
    (126, "H5439"): ("core", T_COMP, "The SC Electric Retail Choice Act: would let households and small businesses choose their electricity supplier, with Public Service Commission permits and consumer disclosures."),
    (126, "H5440"): ("core", T_COMP, "Would let eligible customers buy some or all of their electricity from third-party suppliers over the incumbent utility's wires."),
    (126, "S878"):  ("core", T_COMP, "Would set up a framework for third-party electric suppliers to serve eligible customers."),
    (126, "H5525"): ("core", T_COMP, "The Electric Cooperative Consumer Protection and Wholesale Market Access Act: Public Service Commission oversight of the co-ops' wholesale power contracts and rates."),
    # ------------------------------------------------------------------
    # Utility bills, fees, and shutoffs.
    (123, "H4738"): ("adjacent", T_BILLS, "Would have banned utilities (and their payment processors) from charging an extra fee just to pay your utility bill."),
    (124, "H3311"): ("adjacent", T_BILLS, "Would have banned utilities (and their payment processors) from charging an extra fee just to pay your utility bill."),
    (125, "H3157"): ("adjacent", T_BILLS, "Would have banned public utilities from collecting an extra service fee on customer payments."),
    (123, "H5057"): ("adjacent", T_BILLS, "Would have barred utilities from moving an unpaid balance from one account onto another person's account."),
    (124, "H4160"): ("adjacent", T_BILLS, "Would have barred utilities from moving an unpaid balance from one account onto another person's account."),
    (126, "H3546"): ("adjacent", T_BILLS, "Would bar utilities from moving an unpaid balance from one account onto another person's account."),
    (124, "H3280"): ("adjacent", T_BILLS, "Would have restricted electric utilities from shutting off service for nonpayment in dangerous conditions."),
    (125, "H3156"): ("adjacent", T_BILLS, "Would have restricted electric utilities from shutting off service for nonpayment in dangerous conditions."),
    (124, "H4164"): ("adjacent", T_BILLS, "Would have exempted customers 65 and older from utility payment surcharges."),
    (123, "S904"):  ("adjacent", T_BILLS, "Would have barred gas and electric utilities from sharing customer information with third parties without consent."),
    (124, "S247"):  ("adjacent", T_BILLS, "Would have barred gas and electric utilities from sharing customer information with third parties without consent."),
    (125, "S156"):  ("adjacent", T_BILLS, "Would have barred gas and electric utilities from sharing customer information with third parties without consent."),
    (123, "S951"):  ("adjacent", T_BILLS, "Would have made utilities, not homeowners, pay for repairs to the service line between the meter and the home."),
    (123, "S334"):  ("adjacent", T_BILLS, "Would have barred a utility from billing customers for its legal fees in cases the utility lost for breaking the law."),
    (124, "S301"):  ("adjacent", T_BILLS, "Would have barred a utility from billing customers for its legal fees in cases the utility lost for breaking the law."),
    (123, "H5232"): ("adjacent", T_BILLS, "Would have barred utilities from recovering non-allowed expenses from ratepayers, with penalties for trying."),
    (125, "H5090"): ("adjacent", T_BILLS, "Would have required utilities with drive-through windows to take bill payments there."),
    (126, "H5215"): ("adjacent", T_BILLS, "Would wall off data centers' power costs so they cannot be recovered from households and other customer classes."),
    (126, "H4583"): ("adjacent", T_BILLS, "The Data Center Responsibility Act: rules so data centers pay their own way on power and water."),
    # ------------------------------------------------------------------
    # Money skills in school [P-financial-education].
    # SC already has a financial-literacy statute (Section 59-29-410, since
    # 2005) and a required personal-finance instruction law (59-29-165).
    (123, "S15"):   ("core", T_FINED, "Would have required a half-credit personal finance course, with an end-of-year test, to graduate high school starting 2020-21."),
    (123, "H3199"): ("core", T_FINED, "Would have added college-loan topics — loan terms, monthly payments, repayment options, credit — to the state's required high school financial literacy program."),
    (124, "H3022"): ("core", T_FINED, "Refile: add more required topics to the high school financial literacy program."),
    (124, "H4582"): ("core", T_FINED, "Would have added everyday life skills to the required high school financial literacy program."),
    (124, "S16"):   ("core", T_FINED, "Would have required basic personal finance coursework for high school graduation in place of the economics requirement."),
    (124, "S405"):  ("core", T_FINED, "Companion graduation-requirements bill filed while S16 was pending."),
    (125, "S732"):  ("core", T_FINED, "Joint resolution to approve the State Board of Education regulation (Document 5130) adding a required half-credit in financial literacy to the high school diploma."),
    # ------------------------------------------------------------------
    # Property taxes on homes [P-reduce-property-vehicle-taxes].
    # Enacted:
    (123, "H3630"): ("core", T_HOMETAX, "Delayed property-tax late penalties three months for people affected by the 2019 federal government shutdown."),
    (124, "H3354"): ("core", T_HOMETAX, "Exempted small rooftop solar systems (20 kilowatts or less) from property tax."),
    (124, "H3482"): ("core", T_HOMETAX, "Let counties offer alternative installment schedules for paying property tax."),
    (124, "S233"):  ("core", T_HOMETAX, "Extended the homestead exemption to qualifying surviving spouses and heirs' property, and required local 'service fees' to actually benefit the people who pay them."),
    (125, "H3116"): ("core", T_HOMETAX, "Let totally disabled veterans (and qualifying surviving spouses) get their property tax exemption in the year the disability occurs instead of waiting."),
    (126, "H3841"): ("core", T_HOMETAX, "Kept a home's 4% owner-occupied assessment rate and exemptions in place after the owner dies, while the estate is settled."),
    (126, "S866"):  ("core", T_HOMETAX, "The Municipal Tax Relief Act: certain cities can ask voters for up to a 1% local sales tax to cut property taxes on owner-occupied homes."),
    (126, "S439"):  ("core", T_HOMETAX, "Raised the state reimbursement cap for the manufacturing property tax exemption (business property, paid for from state funds)."),
    (126, "H4187"): ("adjacent", T_HOMETAX, "Extended Lexington County's local sales-tax-for-property-tax-relief arrangement."),
    (125, "H5014"): ("adjacent", T_HOMETAX, "Earlier version of the Lexington County property-tax-relief extension."),
    # Homestead exemption bills (the $50,000 senior/disabled exemption):
    (123, "H3332"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (123, "H3687"): ("core", T_HOMETAX, "Would have extended the senior/disabled homestead exemption to the home's full value."),
    (123, "H4994"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (123, "S910"):  ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption from $50,000 to $75,000 of home value."),
    (124, "H3108"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (124, "H3452"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (124, "H4197"): ("core", T_HOMETAX, "Would have extended the senior/disabled homestead exemption to the home's full value."),
    (124, "H4222"): ("core", T_HOMETAX, "Would have added a homestead exemption for value increases caused by countywide reassessment."),
    (124, "S1027"): ("core", T_HOMETAX, "Would have extended the homestead exemption to taxpayers who are deaf."),
    (125, "H3127"): ("core", T_HOMETAX, "Would have doubled the senior/disabled homestead exemption from $50,000 to $100,000 of home value."),
    (125, "H3423"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (125, "H3927"): ("core", T_HOMETAX, "Would have raised the senior/disabled homestead exemption above the first $50,000 of home value."),
    (125, "H5264"): ("core", T_HOMETAX, "Would have set the homestead exemption at the greater of $50,000 or a share of the home's value."),
    (125, "S433"):  ("core", T_HOMETAX, "Would have extended the homestead exemption to taxpayers who are deaf."),
    (125, "S1143"): ("core", T_HOMETAX, "Would have defined owner-occupant for the legal-residence rate and revised the homestead exemption."),
    (125, "H3449"): ("adjacent", T_HOMETAX, "Would have required five years of state residency, instead of one, to claim the homestead exemption."),
    (126, "H3374"): ("adjacent", T_HOMETAX, "Would require five years of state residency, instead of one, to claim the homestead exemption."),
    (126, "H3380"): ("core", T_HOMETAX, "Would set the homestead exemption at the greater of $50,000 or a share of the home's value."),
    (126, "H3419"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "H3427"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "H3511"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "H3742"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "H4599"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "H4690"): ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "S223"):  ("core", T_HOMETAX, "Would raise the senior/disabled homestead exemption above the first $50,000 of home value."),
    (126, "S768"):  ("core", T_HOMETAX, "Would raise the homestead exemption to $100,000 and lower the qualifying age from 65 to 60."),
    # Senior full exemptions and the elimination bill:
    (123, "H3122"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 80 and older."),
    (123, "H3207"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older under an income limit."),
    (123, "H3736"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 65 and older."),
    (123, "H4818"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older."),
    (123, "S565"):  ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older."),
    (124, "S12"):   ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older who had owned it long enough."),
    (125, "S12"):   ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older who had owned it long enough."),
    (124, "H3386"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 80 and older."),
    (125, "H3086"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 80 and older."),
    (125, "H3778"): ("core", T_HOMETAX, "Would have exempted the entire home from property tax for owners 70 and older."),
    (126, "H3424"): ("core", T_HOMETAX, "The Property Tax Relief for Seniors Act: homestead exemption up to $1 million of home value, funded by an additional sales tax."),
    (126, "H3378"): ("core", T_HOMETAX, "Would eliminate property taxes entirely — every kind of property — with dollar-for-dollar state reimbursement to local governments."),
    # Reassessment and valuation:
    (123, "H4782"): ("core", T_HOMETAX, "Would have exempted value added by countywide reassessment for certain residents."),
    (124, "H3458"): ("core", T_HOMETAX, "Would have exempted value added by countywide reassessment for certain residents."),
    (123, "H3626"): ("core", T_HOMETAX, "Constitutional amendment on how real property is valued for taxes, removing the 15%-over-five-years cap on value increases."),
    (124, "H3671"): ("core", T_HOMETAX, "Constitutional amendment on how real property is valued for taxes, removing the 15%-over-five-years cap on value increases."),
    (125, "H3809"): ("core", T_HOMETAX, "Constitutional amendment on property valuation: define fair market value, remove the 15% cap, and end point-of-sale revaluation."),
    (125, "H4910"): ("core", T_HOMETAX, "Would have delayed every county's scheduled property reassessment until 2026."),
    # Millage cap (direction: easier increases):
    (124, "H3674"): ("adjacent", T_HOMETAX, "Would have let local governments override the annual property-tax millage cap by simple majority instead of a supermajority — easing tax increases, not cutting them."),
    (125, "H3806"): ("adjacent", T_HOMETAX, "Would have let local governments override the annual property-tax millage cap by simple majority instead of a supermajority — easing tax increases, not cutting them."),
    (126, "H3803"): ("adjacent", T_HOMETAX, "Would let local governments override the annual property-tax millage cap by simple majority instead of a supermajority — easing tax increases, not cutting them."),
    # Business property and fee-in-lieu transparency:
    (126, "S151"):  ("adjacent", T_HOMETAX, "Would exempt the first $30,000 of a small business's real property from property taxes."),
    (126, "S890"):  ("adjacent", T_HOMETAX, "Would exempt the first $30,000 of a small business's real property from property taxes."),
    (126, "H3358"): ("adjacent", T_HOMETAX, "Would exempt the first $10,000 of business personal property and simplify filing."),
    (126, "H4060"): ("adjacent", T_HOMETAX, "Would exempt 42.75% of business personal property value, matching the manufacturing exemption."),
    (123, "H4153"): ("adjacent", T_HOMETAX, "Would have required counties to consult affected schools and towns, and report annually, before cutting fee-in-lieu property tax deals with companies."),
    (124, "H3389"): ("adjacent", T_HOMETAX, "Would have required counties to consult affected schools and towns, and report annually, before cutting fee-in-lieu property tax deals with companies."),
    (125, "H3511"): ("adjacent", T_HOMETAX, "Would have required counties to consult affected schools and towns, and report annually, before cutting fee-in-lieu property tax deals with companies."),
    (126, "H3496"): ("adjacent", T_HOMETAX, "Would require counties to consult affected schools and towns, and report annually, before cutting fee-in-lieu property tax deals with companies."),
    (126, "H4608"): ("adjacent", T_HOMETAX, "Would extend the 4% owner-occupied rate to a second dwelling on the same property occupied by immediate family."),
    (123, "S171"):  ("core", T_HOMETAX, "The Municipal Tax Relief Act (2019 version): would have let municipalities levy up to a 1% sales tax, by referendum, for municipal tax relief."),
    # ------------------------------------------------------------------
    # Taxes on vehicles and boats [P-reduce-property-vehicle-taxes].
    (126, "H5014"): ("core", T_VEHTAX, "Would exempt one personal vehicle from property tax — fully at 70 and older, half at 65 — the broadest vehicle-tax relief bill in this record."),
    (123, "H4564"): ("core", T_VEHTAX, "Would have exempted disabled veterans' passenger vehicles from property tax."),
    (124, "H4511"): ("core", T_VEHTAX, "Would have exempted two vehicles owned by permanently disabled former law enforcement officers or firefighters."),
    (126, "H3410"): ("core", T_VEHTAX, "Would exempt two vehicles owned by permanently disabled former law enforcement officers, EMTs, or firefighters."),
    (124, "S1018"): ("core", T_VEHTAX, "Would have exempted a vehicle owned by a service member stationed out of state."),
    (125, "S943"):  ("core", T_VEHTAX, "Would have exempted up to two vehicles held in trust for a disabled veteran."),
    (126, "H4138"): ("core", T_VEHTAX, "Would exempt one vehicle owned by the legal guardian of a minor or dependent child."),
    (123, "S658"):  ("adjacent", T_VEHTAX, "Would have exempted vehicles leased by churches from property tax."),
    (124, "S37"):   ("adjacent", T_VEHTAX, "Would have exempted vehicles leased by churches from property tax."),
    (124, "H3385"): ("core", T_VEHTAX, "Would have barred county treasurers from refusing your car-tax payment (blocking registration) because you owe tax on something else."),
    (125, "H3085"): ("core", T_VEHTAX, "Would have barred county treasurers from refusing your car-tax payment (blocking registration) because you owe tax on something else."),
    (123, "H5111"): ("core", T_VEHTAX, "Would have stopped counties from billing boat property tax twice within twelve months during the switch to registration-time collection."),
    (125, "S38"):   ("core", T_VEHTAX, "Would have taxed boats in the county where they are actually kept rather than the owner's home county."),
    # ------------------------------------------------------------------
    # Income and sales tax relief (adjacent context for the tax proposal).
    (124, "S1087"): ("adjacent", T_INCTAX, "The Comprehensive Tax Cut Act of 2022: collapsed income tax brackets and set the top rate to fall from 7% to 6% as revenue allows; also exempted all military retirement pay."),
    (124, "H4880"): ("adjacent", T_INCTAX, "House version of the 2022 income tax cut (top rate to 6%)."),
    (126, "H4216"): ("adjacent", T_INCTAX, "The 2026 income tax restructuring: cuts the top rate to 5.21%, taxes lower income at 1.99%, changes the starting point to federal adjusted gross income, and schedules further cuts when revenue grows."),
    (126, "H4458"): ("adjacent", T_INCTAX, "Would cut the top income tax rate to 5%."),
    (123, "H4334"): ("adjacent", T_INCTAX, "Would have replaced the income tax schedule with a flat-tax overhaul for individuals, trusts, and estates."),
    (124, "H3393"): ("adjacent", T_INCTAX, "Would have phased in a flat 4.85% income tax over five years."),
    (124, "S925"):  ("adjacent", T_INCTAX, "The Tax Policy Modernization Act: a broad rewrite of income, sales, and property tax law."),
    (123, "H4532"): ("adjacent", T_INCTAX, "Would have broadened the sales tax to services while revising the rate."),
    (125, "H3110"): ("adjacent", T_INCTAX, "Would have expanded the August sales tax holiday."),
    (126, "S742"):  ("adjacent", T_INCTAX, "Would exempt baby formula, baby food, and baby clothes from sales tax."),
    (125, "H5307"): ("adjacent", T_INCTAX, "Would have created a tax credit for grocery stores that open in food deserts."),
    (126, "H3465"): ("adjacent", T_INCTAX, "Would create a tax credit for grocery stores that open in food deserts."),
    (126, "S273"):  ("adjacent", T_INCTAX, "Would create a tax credit for grocery stores that open in food deserts."),
    (126, "H5477"): ("adjacent", T_INCTAX, "The Working Family Child Tax Credit: a state income tax credit for families with qualifying children."),
    (125, "S1110"): ("adjacent", T_INCTAX, "Would have raised the retirement-income deduction from state income tax."),
    (126, "S207"):  ("adjacent", T_INCTAX, "Would raise the retirement-income deduction from state income tax."),
    # ------------------------------------------------------------------
    # Housing costs and rent.
    (123, "H3998"): ("adjacent", T_HOUSING, "The Workforce and Senior Affordable Housing Act: created a state housing tax credit matching the federal credit, to finance affordable housing construction."),
    (123, "S585"):  ("adjacent", T_HOUSING, "Senate version of the state housing tax credit."),
    (124, "H5075"): ("adjacent", T_HOUSING, "Tightened and capped the state housing tax credit after uptake far exceeded estimates."),
    (124, "S1120"): ("adjacent", T_HOUSING, "Senate version of the housing tax credit revisions."),
    (125, "S739"):  ("adjacent", T_HOUSING, "One-time authorization to rescue stalled affordable-housing projects with remaining housing tax credits and up to $25 million from the Housing Trust Fund."),
    (125, "S284"):  ("adjacent", T_HOUSING, "Let local governments spend tourism (accommodations) tax money on workforce housing, with a sunset."),
    (125, "H4213"): ("adjacent", T_HOUSING, "House companion to the workforce-housing accommodations-tax bill."),
    (126, "H3911"): ("adjacent", T_HOUSING, "Would add workforce housing to what county capital-project sales taxes can fund."),
    (126, "S298"):  ("adjacent", T_HOUSING, "Would add workforce housing to what county capital-project sales taxes can fund."),
    (124, "H3770"): ("adjacent", T_HOUSING, "Stood up South Carolina's share of the federal Emergency Rental Assistance Program during COVID."),
    (124, "H5176"): ("adjacent", T_HOUSING, "The SC Rent Control Act: notice requirements and restrictions on raising residential rent."),
    (125, "H3264"): ("adjacent", T_HOUSING, "Rent control: notice requirements and restrictions on raising residential rent."),
    (126, "H3346"): ("adjacent", T_HOUSING, "The SC Rent Control Act: notice requirements and restrictions on raising residential rent."),
    (123, "H3091"): ("adjacent", T_HOUSING, "The SC Inclusionary Housing Act: would let local governments adopt inclusionary housing (affordable-unit) strategies."),
    (124, "H3938"): ("adjacent", T_HOUSING, "The SC Inclusionary Housing Act: would authorize voluntary local inclusionary housing strategies."),
    (125, "S891"):  ("adjacent", T_HOUSING, "The Inclusionary Housing Act: would authorize voluntary local inclusionary housing strategies."),
    (123, "H4482"): ("adjacent", T_HOUSING, "Housing Attainability Protection: would require a housing-cost impact analysis before local ordinances or state rules that raise housing costs."),
    (123, "S757"):  ("adjacent", T_HOUSING, "Housing Attainability Protection (Senate version): housing-cost impact analyses for local ordinances and state rules."),
    (125, "H5372"): ("adjacent", T_HOUSING, "The Accessory Dwelling Unit Affordable Housing Incentive Act: property tax incentives for backyard apartments used as affordable housing."),
    (126, "H3469"): ("adjacent", T_HOUSING, "The Accessory Dwelling Unit Affordable Housing Incentive Act: property tax incentives for backyard apartments used as affordable housing."),
    (125, "H4544"): ("adjacent", T_HOUSING, "The Religious Institutions Affordable Housing Act: churches could build affordable housing on their land without losing their property tax exemption."),
    (126, "H3458"): ("adjacent", T_HOUSING, "The Religious Institutions Affordable Housing Act: churches could build affordable housing on their land without losing their property tax exemption."),
    (126, "H3737"): ("adjacent", T_HOUSING, "Would create a tax-exempt real estate investment trust to grow the supply of affordable housing statewide."),
    (126, "H3738"): ("adjacent", T_HOUSING, "Would let housing authorities use tax-increment financing to fund housing development."),
    (126, "H3750"): ("adjacent", T_HOUSING, "The Equitable Development and Affordable Housing Act: would designate certain land for affordable-housing development."),
    (126, "H3970"): ("adjacent", T_HOUSING, "Would create incentives for building affordable housing for public university students."),
    (126, "H4693"): ("adjacent", T_HOUSING, "Would add an alternative housing tax credit for preserving existing low-income housing."),
    (124, "H3373"): ("adjacent", T_HOUSING, "Would have created a housing court inside each county's magistrates court."),
    (123, "S569"):  ("adjacent", T_HOUSING, "The Healthy Rental Housing Act: remedies for tenants in rental homes with serious mold problems."),
    (126, "H3232"): ("adjacent", T_HOUSING, "The Healthy Rental Housing Act: remedies for tenants in rental homes with serious mold problems."),
    (125, "H4015"): ("adjacent", T_HOUSING, "Would have made landlords disclose all fees to prospective tenants up front."),
    (126, "H3462"): ("adjacent", T_HOUSING, "Would make landlords disclose all fees to prospective tenants up front."),
    (126, "H3229"): ("adjacent", T_HOUSING, "Would bar landlords from requiring a credit score on a rental application."),
    (124, "H3996"): ("adjacent", T_HOUSING, "Would have let assisted-housing tenants have on-time rent payments reported to credit bureaus."),
    (125, "H4158"): ("adjacent", T_HOUSING, "Would have let domestic-violence survivors end a lease early and required landlords to change locks."),
    (126, "H3569"): ("adjacent", T_HOUSING, "Let domestic-violence survivors end a lease early with protections against liability for abuse-related damage."),
    (125, "H4987"): ("adjacent", T_HOUSING, "Protected-tenants bill: lease-termination rights for survivors of domestic violence."),
    (126, "H4970"): ("adjacent", T_HOUSING, "The Renters Fairness Act: three months to relocate before eviction after certain convictions."),
    (126, "H3238"): ("adjacent", T_HOUSING, "Would require public housing authorities to house residents displaced by redevelopment."),
    (126, "H4606"): ("adjacent", T_HOUSING, "The Veteran Housing Stability and Security Act: veteran housing priority zones and a landlord risk-mitigation fund."),
    (123, "H3619"): ("adjacent", T_HOUSING, "Urged lenders to pause foreclosures and late fees for federal workers during the 2019 government shutdown."),
    (123, "H3460"): ("adjacent", T_HOUSING, "Would have created an SC Gentrification Trust Fund to help long-time residents stay in appreciating neighborhoods."),
    (126, "H4390"): ("adjacent", T_HOUSING, "Would require community impact assessments before certain zoning decisions."),
    (125, "H4639"): ("adjacent", T_HOUSING, "Would have barred housing discrimination based on source of income (such as vouchers)."),
    (126, "H3336"): ("adjacent", T_HOUSING, "Would bar housing discrimination based on disability or source of income (such as vouchers)."),
    # ------------------------------------------------------------------
    # Home and property insurance costs.
    (123, "H4733"): ("adjacent", T_INS, "Would have restricted insurers from refusing to renew homeowners insurance in certain cases."),
    (123, "S1188"): ("adjacent", T_INS, "Property insurance market bill (coastal availability)."),
    (126, "H5063"): ("adjacent", T_INS, "Would require periodic structural inspections of coastal multi-story buildings as a condition of insurance renewal."),
    (126, "H4817"): ("adjacent", T_INS, "The Insurance Rate Reduction and Policyholder Protection Act: a broad auto/liability insurance overhaul promoted as reducing rates."),
    (125, "H5066"): ("adjacent", T_INS, "Would have created an affordable state liquor-liability insurance option for bars and restaurants required to carry it."),
    (126, "H5503"): ("adjacent", T_INS, "Would repeal the $1 million liquor-liability insurance mandate that bars and restaurants say is driving them out of business."),
    (126, "S397"):  ("adjacent", T_INS, "Liquor-liability insurance relief for bars and restaurants."),
    (125, "H3977"): ("adjacent", T_INS, "Let insurers deliver policies electronically by posting them online, with notice and free paper copies on request."),
    (123, "S882"):  ("adjacent", T_INS, "The SC Private Flood Insurance Act: opened the state market to private flood insurance as an alternative to the federal program."),
    (123, "H3126"): ("adjacent", T_INS, "Would have created a study committee on flood insurance."),
    # ------------------------------------------------------------------
    # Child care costs and assistance (legislator-discussion topic added
    # 2026-09-04; not a Phase 2 proposal). Assistance designs and the
    # regulation/near-miss record; verified against full texts and the
    # slow-wage-growth childcare scan.
    (126, "H4394"): ("adjacent", T_CHILDCARE, "Would create workforce-development childcare stipends, through DSS and the state workforce agency, for unemployed parents and caregivers of children under 12."),
    (126, "S47"):   ("adjacent", T_CHILDCARE, "Would raise the cap on the existing employer childcare-program tax credit and add a new income tax credit for childcare directors and staff (a pay supplement through the tax code)."),
    (126, "H4015"): ("adjacent", T_CHILDCARE, "House companion: bigger employer childcare credit plus a new credit for childcare directors and staff."),
    (126, "H5794"): ("adjacent", T_CHILDCARE, "Would make the existing child and dependent care income tax credit refundable — filed August 2026, the newest bill in this set."),
    (125, "H4993"): ("adjacent", T_CHILDCARE, "The Childcare Advance Act: would let taxpayers defer part of their income tax against eligible childcare expenses."),
    (124, "H3079"): ("adjacent", T_CHILDCARE, "Would have created a study committee on the statewide availability of high-quality, affordable childcare."),
    (123, "S291"):  ("adjacent", T_CHILDCARE, "Would have created a Department of Early Development and Education consolidating early-childhood programs."),
    (126, "S770"):  ("adjacent", T_CHILDCARE, "The Childcare Assistance Program bill: would add employment requirements as a condition of federally funded childcare assistance."),
    (125, "S946"):  ("adjacent", T_CHILDCARE, "Childcare regulations modernization: passed the Senate 45-0 and the House 105-0 in differing versions, then died in conference at session's end."),
    (123, "S595"):  ("adjacent", T_CHILDCARE, "Background-check requirements for childcare facility staff (became law)."),
    (125, "S862"):  ("adjacent", T_CHILDCARE, "Caregiver education and preservice-training requirements for childcare centers (became law)."),
    (125, "H4023"): ("adjacent", T_CHILDCARE, "Restructured local First Steps early-childhood partnership boards (became law)."),
    (125, "H3745"): ("adjacent", T_CHILDCARE, "Childcare facility regulation changes."),
    (126, "H4632"): ("adjacent", T_CHILDCARE, "The Cash Berry Childcare Safety and Quality Rating Act: safety and quality-rating rules for childcare facilities."),
    (126, "S700"):  ("adjacent", T_CHILDCARE, "Family childcare home regulation."),
    (126, "H4587"): ("adjacent", T_CHILDCARE, "Would exempt military-installation childcare centers from certain state requirements."),
    # ------------------------------------------------------------------
    # Related context (kept for audit; excluded from headline counts).
    (123, "S76"):   ("context", T_CONTEXT, "Extended the energy-efficient manufactured homes incentive program five years (became law)."),
    (123, "H4810"): ("context", T_CONTEXT, "Commercial Property Assessed Clean Energy (C-PACE) financing for energy improvements."),
    (125, "H3937"): ("context", T_CONTEXT, "Commercial Property Assessed Clean Energy and Resilience financing."),
    (126, "H3812"): ("context", T_CONTEXT, "Commercial Property Assessed Clean Energy (C-PACE) financing."),
    (123, "H3966"): ("context", T_CONTEXT, "Airline property tax proceeds redirected to the State Aviation Fund (industry, not household, taxation)."),
    (124, "H3921"): ("context", T_CONTEXT, "Regulation of transportation network companies under the utilities title (rideshare rules, not household utilities)."),
    (124, "H4547"): ("context", T_CONTEXT, "Would have limited how local governments regulate short-term vacation rentals."),
    (125, "H3253"): ("context", T_CONTEXT, "Short-term rental regulation."),
    (126, "H3861"): ("context", T_CONTEXT, "Short-term rental regulation."),
    (126, "S442"):  ("context", T_CONTEXT, "Short-term rental regulation."),
    (123, "H3145"): ("context", T_CONTEXT, "Required regular audits of electric cooperatives (became law)."),
    (126, "H3933"): ("context", T_CONTEXT, "Public service district board restructuring (became law; local special districts)."),
    (126, "H3259"): ("context", T_CONTEXT, "Auto insurance premium reductions for first responders (became law)."),
    (125, "H4832"): ("context", T_CONTEXT, "Paid Family Leave Insurance for state employees (became law; employee benefit, not household utility/tax)."),
}

# Bills confirmed relevant by a hand full-text scan of the certified universe
# that did NOT match any Pass 1 search term (so they are absent from
# pass1/bills.json). Added from _universe with provenance marked.
UNIVERSE_ADD = {
    (123, "H4149"): ("core", T_FINED, "House version of the half-credit personal finance graduation requirement with an end-of-course exam."),
    (124, "H3116"): ("core", T_FINED, "House companion: personal finance coursework as a high school graduation requirement."),
    (125, "H5205"): ("adjacent", T_CHILDCARE, "Would have created a High-Quality Prekindergarten Expansion grant program at the Department of Education."),
}

EXCLUSION_RULES = [
    "Instrument is an honorary/ceremonial resolution (House, Senate, or Concurrent Resolution) — congratulations, memorials, and awareness days that only mention housing, insurance, utility, or tax language.",
    "False-positive term hits: 'rent' inside 'parental/parent' (parental-rights and family-law bills), 'utility' in utility-terrain-vehicle and utility-trailer bills, 'rate' in magistrate-court and tuition-rate bills, 'PSC' matches inside unrelated words.",
    "Health, dental, vision, and life insurance mandates and insurance-industry housekeeping (producer licensing, guaranty associations, captive insurers, regulation-approval JRs) — insurance regulation unrelated to household property/utility costs.",
    "Auto-insurance coverage-rule bills (proof of insurance, arbitration, glass repair, commercial fleets) — kept only where the bill was framed as premium/cost relief.",
    "Sales-tax exemptions for narrow industries or products unrelated to household staples (aircraft parts, farm equipment, industrial inputs), local accommodations-tax housekeeping, and capital-project sales tax procedure bills without a household cost angle.",
    "Property-tax bills about narrow non-household classes (agricultural rollback, aircraft, watercraft dealers' inventory, nonprofit institutional campuses) unless they set precedent for household relief.",
    "Water/sewer system ownership and service-area bills (county acquisitions, special purpose districts) — utility-adjacent but not about household electric/gas rates.",
    "Landlord-tenant procedure bills without a cost dimension (ejectment process, bedbug disclosure) and vacation-rental licensing.",
    "Economic-development incentive bills (job development credits, opportunity zones, headquarters funds) — they surfaced on 'tax relief' terms but belong to the wage-growth issue set.",
    "Unemployment insurance, workers compensation, retirement-system, and state-employee benefit bills — matched 'insurance'/'rate' terms but are not household cost-of-living measures (state-employee paid leave kept once as context).",
]


def load_universe_bill(session, bill_no):
    path = os.path.join(UNIVERSE, str(session), "bills.jsonl.gz")
    with gzip.open(path) as f:
        for line in f:
            b = json.loads(line)
            if b["bill_no"] == bill_no:
                return b
    raise SystemExit("universe bill not found: %s:%s" % (session, bill_no))


def main():
    pass1 = json.load(open(PASS1))
    bills = {(b["session"], b["bill_no"]): b for b in pass1["bills"]}
    missing = [k for k in KEEP if k not in bills]
    if missing:
        raise SystemExit("curation keys not in pass1: %r" % missing)
    overlap = set(KEEP) & set(UNIVERSE_ADD)
    if overlap:
        raise SystemExit("universe adds already in pass1 keep: %r" % overlap)

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
            "source": "pass1",
        })
    for (session, bill_no), (tier, theme, plain) in sorted(UNIVERSE_ADD.items()):
        b = load_universe_bill(session, bill_no)
        kept.append({
            "bill_key": "%s:%s" % (session, bill_no),
            "session": session,
            "bill_no": bill_no,
            "title": b["title"],
            "instrument_type": b["instrument_type"],
            "plain_topic": plain,
            "theme": theme,
            "relevance": tier,
            "found_by_terms": [],
            "url": b["url"],
            "source": ("universe_hand_scan (personal-finance full-text scan)"
                       if theme == T_FINED else
                       "universe_hand_scan (childcare title/full-text scan; no Pass 1 term hit)"),
        })
    kept.sort(key=lambda r: (r["session"], r["bill_no"]))

    counts = {"total_pass1": len(bills), "kept": len(kept),
              "by_relevance": {}, "by_theme": {}}
    for r in kept:
        counts["by_relevance"][r["relevance"]] = counts["by_relevance"].get(r["relevance"], 0) + 1
        counts["by_theme"][r["theme"]] = counts["by_theme"].get(r["theme"], 0) + 1
    counts["excluded"] = counts["total_pass1"] - (counts["kept"] - len(UNIVERSE_ADD))

    out = {
        "issue": pass1["issue"],
        "note": ("Hand curation of the keep-all Pass 1 discovery (nothing was dropped upstream). "
                 "Tiers: core = the issue's headline set (utility rates/oversight/transparency, "
                 "Santee Cooper, major energy-rate bills, electricity-market competition, "
                 "personal-finance education, and property/vehicle taxes — the four constituent "
                 "proposals' lanes); adjacent = household cost-of-living bills outside the four "
                 "proposals (utility billing protections, income/sales tax relief, housing and "
                 "rent, home/property insurance); context = kept for audit only, excluded from "
                 "headline counts. Headline and ambiguous bills verified against latest-version "
                 "full text in _universe/. Two financial-education bills added from a hand "
                 "universe full-text scan (see per-bill source field). All other Pass 1 hits are "
                 "excluded under the rules below."),
        "themes": THEMES,
        "counts": counts,
        "exclusion_rules": EXCLUSION_RULES,
        "bills": kept,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("kept", len(kept), "of", len(bills), "pass1 (+%d universe adds) |" % len(UNIVERSE_ADD),
          counts["by_relevance"])
    for t in THEMES:
        print("  %-55s %d" % (t, counts["by_theme"].get(t, 0)))


if __name__ == "__main__":
    main()
