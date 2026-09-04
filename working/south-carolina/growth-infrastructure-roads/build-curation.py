#!/usr/bin/env python3
"""Curate the keep-all Pass 1 set for south-carolina-01-growth-infrastructure-roads.

Pass 1 kept every full-text/title hit (5,618 bills). This script encodes the
hand review: which bills belong to the issue set (core / adjacent / context),
one plain sentence and a citizen-facing theme per kept bill, and the explicit
exclusion rules for everything else. Ambiguous bills were verified against
their latest-version full text in sources/south-carolina/_universe/ (the
"A BILL TO AMEND..." long titles were read for every candidate).

Nine bills are sourced from the certified universe rather than Pass 1: their
full text contains none of the issue's search terms in a form Pass 1 matched
(the config had no "sales tax", "annexation", or "hospitality tax" search
terms), but they are directly responsive to the local-funding-tools and
state-master-planning constituent proposals and were found by a hand
title-scan of the universe index. They are marked source="universe".

Output: working/south-carolina/growth-infrastructure-roads/curation-map.json
"""
import gzip
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
PASS1 = os.path.join(ROOT, "sources/south-carolina/growth-infrastructure-roads/pass1/bills.json")
UNIVERSE = os.path.join(ROOT, "sources/south-carolina/_universe")
OUT = os.path.join(HERE, "curation-map.json")

T_LOCALFUND = "Local tools to pay for growth (penny taxes, tolls, local fees)"
T_IMPACT = "Making developers pay (impact fees)"
T_STATEFUND = "State road money (gas tax, road fees, infrastructure funds)"
T_MAINT = "Fixing and maintaining existing roads"
T_SCDOT = "Who runs SCDOT (governance and accountability)"
T_CONTRACT = "Road contracts and contractor accountability"
T_TRANSIT = "Transit, rail, and other ways to get around"
T_PLAN = "Planning for growth (zoning, comprehensive plans, annexation)"
T_WSB = "Water, sewer, and broadband infrastructure"
T_CONTEXT = "Related context"

THEMES = [T_LOCALFUND, T_IMPACT, T_STATEFUND, T_MAINT, T_SCDOT, T_CONTRACT,
          T_TRANSIT, T_PLAN, T_WSB, T_CONTEXT]

# (session, bill_no): (tier, theme, plain_topic)
KEEP = {
    # ------------------------------------------------------------------
    # Local tools to pay for growth. Three families verified in full
    # text: (1) the Title 4 Chapter 37 "transportation sales tax" (the
    # local-option penny for roads and transit) and county transportation
    # authorities; (2) the Title 4 Chapter 10 capital project / green
    # space / education local-option sales taxes; (3) tolls, local fees,
    # and tourism-tax flexibility.
    (123, "S594"):  ("core", T_LOCALFUND, "Would have revised how county transportation authorities are funded, including the local sales taxes and tolls that pay for transportation projects."),
    (123, "S611"):  ("core", T_LOCALFUND, "Would have made clear that a county's local transportation sales tax and tolls can fund mass transit service, with the same procurement rules as roads."),
    (123, "H4389"): ("core", T_LOCALFUND, "House version: would have made clear county transportation authorities and their local sales taxes and tolls can fund mass transit systems."),
    (124, "H3535"): ("core", T_LOCALFUND, "Refile: would have made clear county transportation authorities and their local sales taxes and tolls can fund mass transit systems."),
    (124, "S437"):  ("core", T_LOCALFUND, "Would have defined 'mass transit system' in the local transportation sales tax law so penny-tax revenue could clearly fund transit."),
    (125, "S290"):  ("core", T_LOCALFUND, "Refile: would have defined 'mass transit system' in the local transportation sales tax law."),
    (125, "S562"):  ("core", T_LOCALFUND, "Would have expanded what a county transportation penny tax can pay for - adding ferries, aviation, railways, greenbelts, and drainage projects."),
    (125, "H4059"): ("core", T_LOCALFUND, "House version: would have expanded what a county transportation penny tax can pay for, including greenbelts and drainage."),
    (125, "H5188"): ("core", T_LOCALFUND, "Would have exempted groceries (unprepared food) from county transportation penny taxes."),
    (125, "S1113"): ("core", T_LOCALFUND, "Senate version: would have exempted groceries from county transportation penny taxes."),
    (126, "S979"):  ("core", T_LOCALFUND, "Would let a county transportation penny tax fund greenways and flood-prevention drainage, and let counties put a tax extension or replacement purpose on the ballot."),
    (123, "S449"):  ("adjacent", T_LOCALFUND, "Would have let capital project sales tax (penny) revenue also fund infrastructure for economic development projects."),
    (125, "S116"):  ("core", T_LOCALFUND, "Would have let counties reimpose a capital project sales tax (penny) for eleven years instead of seven."),
    (124, "H3129"): ("core", T_LOCALFUND, "Would have removed the rule that keeps a county from stacking a capital project penny tax on top of a transportation penny tax."),
    (126, "S298"):  ("adjacent", T_LOCALFUND, "Would add workforce housing to the projects a capital project penny tax can fund."),
    (126, "H3911"): ("adjacent", T_LOCALFUND, "House version: would add workforce housing to the projects a capital project penny tax can fund."),
    (126, "S1006"): ("adjacent", T_LOCALFUND, "Would add greenspace and greenbelt programs to the projects a capital project penny tax can fund."),
    (126, "H5744"): ("adjacent", T_LOCALFUND, "Would add police, fire, and EMS operations to the purposes a capital project penny tax can fund."),
    (124, "S152"):  ("core", T_LOCALFUND, "The County Green Space Sales Tax Act (Act 166 of 2022): created a new voter-approved local penny tax counties can use to buy and preserve green space - the one new local funding tool enacted in this record."),
    (125, "S792"):  ("adjacent", T_LOCALFUND, "Would have let a small share of green space penny-tax money pay for conservation management of the land bought."),
    (126, "H4589"): ("adjacent", T_LOCALFUND, "Expanded which counties may impose the local-option education capital improvements sales tax for school buildings (Act 203 of 2026)."),
    (123, "S178"):  ("core", T_LOCALFUND, "Would have required SCDOT to toll Interstate 95 at Lake Marion and use the money for repairs in that corridor."),
    (123, "H3739"): ("core", T_LOCALFUND, "House version: would have required a toll on Interstate 95 at Lake Marion, with the revenue spent on that corridor."),
    (123, "S780"):  ("core", T_LOCALFUND, "Would have required SCDOT to review every highway and bridge project for the possibility of financing it with tolls."),
    (125, "S499"):  ("core", T_LOCALFUND, "Refile: would have required SCDOT to toll Interstate 95 at Lake Marion for maintenance funding."),
    (125, "S674"):  ("core", T_LOCALFUND, "The Interstate 95 Bridge Toll Act: would have authorized toll booths at four I-95 bridges, with resident and commercial-carrier relief, to fund corridor improvements."),
    (123, "S172"):  ("core", T_LOCALFUND, "The Local Option Motor Fuel User Fee Act: would have let a county, by referendum, add one cent a gallon to the gas tax for beach renourishment - a local-option gas tax."),
    (123, "S217"):  ("adjacent", T_LOCALFUND, "Let local tourism (hospitality) tax revenue also pay for flooding and drainage repairs in tourism areas (Act 146 of 2020)."),
    (123, "H3132"): ("adjacent", T_LOCALFUND, "Would have let state and local tourism tax revenue pay for flooding and drainage control in tourism areas."),
    (123, "H4674"): ("adjacent", T_LOCALFUND, "Would have let state and local tourism tax revenue pay for flooding and drainage control in tourism areas."),
    (123, "S629"):  ("adjacent", T_LOCALFUND, "Would have lowered the collections threshold that lets a county spend accommodations tax revenue on additional purposes."),
    (123, "H4597"): ("adjacent", T_LOCALFUND, "Would have let a county keep imposing a pre-1997 hospitality fee at its original rate - the fee family that funds Horry County's RIDE road projects."),
    (124, "S40"):   ("adjacent", T_LOCALFUND, "Required SCDOT approval before municipalities restrict state highway rights of way, and set rules for paid beach parking and how the parking money is used (Act 89 of 2022)."),
    (124, "H3483"): ("core", T_LOCALFUND, "Would have required a county's local road use fee to sit in a separate account, spent only on the county's existing transportation system and identified in the annual audit."),
    (123, "H3775"): ("context", T_LOCALFUND, "Would have revised the petition procedure for creating a special tax district - one of the older tools for funding neighborhood infrastructure."),
    # ------------------------------------------------------------------
    # Making developers pay (impact fees). Both directions were filed:
    # bills expanding what impact fees can fund, and bills narrowing the
    # fees on the development industry's side.
    (124, "H3460"): ("core", T_IMPACT, "Would have let counties and cities charge developers a one-time impact fee per new unit to fund a Gentrification Trust Fund helping longtime residents stay, with an exemption for projects with 15% low-income housing."),
    (126, "H4008"): ("core", T_IMPACT, "Refile: a one-time developer impact fee per new unit funding a Gentrification Trust Fund."),
    (124, "H4943"): ("core", T_IMPACT, "Would have let governments with pre-1999 impact fees use the revenue to pay down debt for system improvements."),
    (125, "H4659"): ("core", T_IMPACT, "Would have let a city or county impose an impact fee on residential development only, commercial only, or both - loosening the all-or-nothing rule."),
    (125, "H4981"): ("core", T_IMPACT, "Would have narrowed the Development Impact Fee Act: fees could not cover repair, operation, or maintenance of improvements, or the government's administrative costs."),
    (125, "S856"):  ("core", T_IMPACT, "Senate version: would have narrowed what development impact fees can cover, excluding repair, maintenance, and administrative costs."),
    (125, "H5017"): ("core", T_IMPACT, "Package: counties would report residential development plans to affected cities, annexation notices would go to the county, and impact fee definitions would be narrowed."),
    (126, "H3165"): ("core", T_IMPACT, "Refile of the package narrowing impact fee definitions and requiring development and annexation notices between counties and cities."),
    (126, "H4672"): ("core", T_IMPACT, "Would exempt home buyers who already owned a home in the same school district for fifteen years from impact fees."),
    (126, "H5088"): ("core", T_IMPACT, "Would add road resurfacing to what development impact fees can fund and give governments more time to spend fee revenue."),
    # ------------------------------------------------------------------
    # State road money. The 2017 gas-tax act (Act 40) is the backdrop:
    # this record holds the attempts to freeze, repeal, or suspend the
    # phased-in gas user fee, one bill to raise the county share, the
    # infrastructure maintenance fee (the car-sales fee that funds
    # roads), "C" funds for county roads, and the infrastructure bank.
    (124, "H4091"): ("core", T_STATEFUND, "Would have stopped the 2017 gas-tax phase-in early, freezing the user fee at eight cents of the planned twelve-cent increase."),
    (124, "H4092"): ("core", T_STATEFUND, "Would have repealed the state gas user fee and the road tax outright."),
    (124, "H5103"): ("core", T_STATEFUND, "Would have suspended the gas user fee and road tax for one year during the 2022 gas-price spike."),
    (124, "H5112"): ("core", T_STATEFUND, "Would have suspended the gas user fee whenever average gas prices exceeded $3.25 per gallon."),
    (126, "S1045"): ("core", T_STATEFUND, "Would suspend the gas tax for thirty days, extended another thirty if pump prices had not fallen fifteen percent."),
    (126, "H5398"): ("core", T_STATEFUND, "Would suspend part of the gas user fee and road tax for sixty days - one of five near-identical suspension resolutions filed in 2026."),
    (126, "H5419"): ("core", T_STATEFUND, "Gas-fee suspension resolution (one of five near-identical 2026 filings)."),
    (126, "H5422"): ("core", T_STATEFUND, "Gas-fee suspension resolution (one of five near-identical 2026 filings)."),
    (126, "H5443"): ("core", T_STATEFUND, "Gas-fee suspension resolution (one of five near-identical 2026 filings)."),
    (126, "H5475"): ("core", T_STATEFUND, "Gas-fee suspension resolution (one of five near-identical 2026 filings)."),
    (126, "H5331"): ("core", T_STATEFUND, "Would more than double the share of the gas user fee that goes to counties for local roads ('C' funds) and delete the rule steering part of it back to state highways."),
    (124, "S1043"): ("core", T_STATEFUND, "Would have required fifteen percent of each county's 'C' fund gas-tax apportionment to be spent on rural roads."),
    (126, "H4971"): ("core", T_STATEFUND, "Would make SCDOT transfer certain roads to the counties and delete the rule that a quarter of county 'C' funds be spent on the state highway system."),
    (123, "H5150"): ("core", T_STATEFUND, "Would have applied the infrastructure maintenance fee (the road-funding fee paid when a vehicle is first registered) to first titling too, closing a collection gap."),
    (123, "S819"):  ("adjacent", T_STATEFUND, "Would have exempted returning South Carolina residents from paying the infrastructure maintenance fee again on vehicles they registered here before."),
    (124, "S148"):  ("core", T_STATEFUND, "Senate version of the titling fix for the infrastructure maintenance fee."),
    (124, "H3505"): ("core", T_STATEFUND, "Closed the collection gap in the road-funding infrastructure maintenance fee by applying it at first titling (Act 70 of 2021)."),
    (123, "S5"):    ("core", T_STATEFUND, "Would have created an Interstate Lane Expansion Fund - dedicating part of the infrastructure maintenance fee to adding lanes on existing interstates, with projects picked through the Transportation Infrastructure Bank."),
    (124, "H4945"): ("core", T_STATEFUND, "Would have repealed the special road use fee charged to electric and hybrid vehicle owners."),
    (125, "H3177"): ("core", T_STATEFUND, "Would have repealed the electric-vehicle road use fee and added a tax deduction for solar panels powering EV charging stations."),
    (123, "H4732"): ("adjacent", T_STATEFUND, "Would have required EV charging at all state welcome centers and rest areas."),
    (124, "S304"):  ("adjacent", T_STATEFUND, "Set rules for who counts as an electric utility when selling EV charging, and created a joint legislative committee on the electrification of transportation (Act 46 of 2021)."),
    (124, "H4768"): ("adjacent", T_STATEFUND, "Would have created a state tax credit matching half the federal alternative-fuel infrastructure credit for EV charging and similar property."),
    (123, "H3418"): ("core", T_STATEFUND, "Would have put the SCDOT Commission in charge of the Transportation Infrastructure Bank's board - merging control of the state's big-project loan fund."),
    (126, "H4031"): ("core", T_STATEFUND, "Would abolish the State Transportation Infrastructure Bank and send its fines and fees straight to the State Highway Fund."),
    (125, "H4004"): ("context", T_STATEFUND, "House resolution urging Congress to create a National Infrastructure Bank."),
    # ------------------------------------------------------------------
    # Fixing and maintaining existing roads.
    (126, "H5363"): ("core", T_MAINT, "The 'Fix Our Roads Accountability Act': would create a statewide pavement preservation program run through SCDOT's engineering districts, with annual reports to the General Assembly."),
    (125, "H4610"): ("core", T_MAINT, "Would require SCDOT to properly maintain roads it accepts into the state highway system from counties and cities."),
    (124, "H3871"): ("core", T_MAINT, "Would have required SCDOT to run a toll-free pothole hotline so motorists whose cars are damaged by road hazards can file complaints and get information."),
    (125, "H3451"): ("core", T_MAINT, "Refile of the SCDOT road-hazard damage hotline bill."),
    (126, "H4687"): ("core", T_MAINT, "Would have county sheriffs report hazardous road segments to SCDOT, which must respond about closures or repairs and keep a public database."),
    (125, "H3516"): ("adjacent", T_MAINT, "Would have set the conditions under which a county may maintain or improve a private road that is the only access for residents."),
    (123, "H3358"): ("adjacent", T_MAINT, "Would have required SCDOT mowing contractors to remove trash along the highway before mowing."),
    (125, "H5348"): ("adjacent", T_MAINT, "Would have created a study committee on bridge safety for large ships entering ports, after the Baltimore Key Bridge collapse."),
    (126, "H3357"): ("adjacent", T_MAINT, "Refile of the port bridge safety study committee."),
    # ------------------------------------------------------------------
    # Who runs SCDOT. The governance fight: governor-appointed secretary
    # vs. the seven-member commission - ending in Act 177 of 2026.
    (126, "S831"):  ("core", T_SCDOT, "The SCDOT Modernization Act (Act 177 of 2026): the Governor now appoints the Secretary of Transportation and the seven-member commission is abolished January 1, 2027, its duties devolved to the secretary - plus a Pothole Mitigation Program (seven-day repairs, $15 million a year), phased design-build contracting, 'choice lane' toll rules, public-private partnership authority, a four-year outside audit, and a rewritten county 'C'-funds split."),
    (126, "H5071"): ("core", T_SCDOT, "House companion to the SCDOT governance overhaul: the Governor, not the commission, would appoint the Secretary of Transportation."),
    (126, "H5362"): ("core", T_SCDOT, "Would dissolve the SCDOT Commission entirely and transfer its responsibilities to the Secretary of Transportation."),
    (123, "H3111"): ("core", T_SCDOT, "The same design six years earlier: governor appoints the secretary and the commission's duties devolve - filed in 2019, never heard."),
    (125, "H5045"): ("core", T_SCDOT, "The governor-appoints-the-secretary, dissolve-the-commission design, filed again in 2024."),
    (125, "H4969"): ("core", T_SCDOT, "Would have moved the power to appoint the Secretary of Transportation from the SCDOT Commission to the Governor."),
    (125, "H4629"): ("core", T_SCDOT, "A different design: the Lieutenant Governor would serve as Secretary of Transportation starting in 2027."),
    (126, "H3282"): ("core", T_SCDOT, "Refile: the Lieutenant Governor would serve as Secretary of Transportation starting in 2028."),
    (124, "H4090"): ("core", T_SCDOT, "Would have required the transportation secretary to certify and publish SCDOT's annual expenditure report, including money transferred to the infrastructure bank."),
    (123, "H4369"): ("adjacent", T_SCDOT, "Joint resolution to approve SCDOT's project prioritization regulation - the ranking rules for which roads get built first."),
    # ------------------------------------------------------------------
    # Road contracts and contractor accountability.
    (125, "H5312"): ("core", T_CONTRACT, "Would have let SCDOT pilot 'progressive design-build' contracting - picking a contractor on qualifications first, then negotiating the price."),
    (126, "H3560"): ("core", T_CONTRACT, "Refile: would let SCDOT award contracts using the phase design-build delivery method."),
    (123, "S1069"): ("core", T_CONTRACT, "Joint resolution to approve SCDOT's contractor performance evaluation regulation - the scoring system for how road contractors performed."),
    (123, "S1070"): ("core", T_CONTRACT, "Joint resolution to approve SCDOT's regulation for disqualifying and suspending contractors from SCDOT contracts."),
    (123, "S385"):  ("adjacent", T_CONTRACT, "Would have extended the rule steering a share of highway construction funds to firms owned by women and minorities, covering subcontracts and setting participation goals."),
    (123, "H4401"): ("adjacent", T_CONTRACT, "House version of the disadvantaged-business highway contracting bill."),
    (123, "H4823"): ("adjacent", T_CONTRACT, "Refile of the disadvantaged-business highway contracting bill."),
    (124, "H3559"): ("adjacent", T_CONTRACT, "The Partnership for Public Facilities and Infrastructure Act: a framework for public-private partnerships to build and operate public projects."),
    (123, "S401"):  ("adjacent", T_CONTRACT, "Made the entity building a transportation improvement project bear the cost of relocating water and sewer lines, with a sunset date (Act 36 of 2019)."),
    (123, "H3799"): ("adjacent", T_CONTRACT, "House version of the water-and-sewer line relocation cost rule for transportation projects."),
    (126, "H3768"): ("adjacent", T_CONTRACT, "Extended the Act 36 utility-relocation cost rule to 2032 and consented to federal-court suits under the national environmental review assignment program (Act 244 of 2026)."),
    (125, "H5315"): ("adjacent", T_CONTRACT, "Would have added broadband lines to the utility-relocation cost rule for federal highway projects."),
    (126, "H3845"): ("adjacent", T_CONTRACT, "Refile: broadband line relocation costs on federal highway projects, and removal of the Act 36 sunset."),
    (125, "H3119"): ("adjacent", T_CONTRACT, "Would have barred contracts with certain foreign-owned companies in connection with critical infrastructure."),
    (126, "H3344"): ("adjacent", T_CONTRACT, "Refile of the foreign-owned company critical-infrastructure contracting ban."),
    (125, "H4115"): ("context", T_CONTRACT, "Rewrote the contractor licensing law - definitions, thresholds, and penalties for construction contractors (Act 69 of 2023)."),
    # ------------------------------------------------------------------
    # Transit, rail, and other ways to get around.
    (123, "H3656"): ("core", T_TRANSIT, "Would have required SCDOT to adopt a 'Complete Streets' policy - designing roads to safely accommodate pedestrians, cyclists, and transit riders."),
    (124, "H3051"): ("core", T_TRANSIT, "Would have made SCDOT's required feasibility review before road projects cover all roads and use measurable standards, including dedicated bus lanes."),
    (123, "H3654"): ("adjacent", T_TRANSIT, "Would have required governments building or improving public facilities to study whether transit riders can safely reach the site."),
    (123, "H3655"): ("core", T_TRANSIT, "Would have let counties and cities create transit-oriented redevelopment agencies to develop areas around planned or existing transit."),
    (125, "H4013"): ("core", T_TRANSIT, "Refile of the transit-oriented development agency bill."),
    (123, "H3828"): ("core", T_TRANSIT, "The Developer-Provided Transit Stop Act: would have let local governments give developers incentives (including a tax credit) to build bus stops and walkable paths in projects near transit lines."),
    (123, "S216"):  ("core", T_TRANSIT, "Would have created a Commuter Rail System Commission to plan for high-speed rail in the state."),
    (123, "H3189"): ("core", T_TRANSIT, "Would have created a High Speed Rail System Commission to develop a plan of action for high-speed rail."),
    (124, "H3937"): ("core", T_TRANSIT, "Refile of the High Speed Rail System Commission bill."),
    (126, "H4122"): ("core", T_TRANSIT, "Would create a high-speed rail study committee tied to the Southeast High-Speed Rail Corridor."),
    (123, "S730"):  ("core", T_TRANSIT, "Would have created a study committee on connecting to Charlotte's mass transit system and providing mass transit statewide."),
    (125, "H5347"): ("core", T_TRANSIT, "Would have required SCDOT to study widening highway rights of way to add commuter rail lines alongside existing highways."),
    (124, "H4817"): ("adjacent", T_TRANSIT, "The Shortline Railroad Modernization Act: a tax credit for half of small railroads' track reconstruction and replacement spending."),
    (125, "H3737"): ("adjacent", T_TRANSIT, "Refile of the shortline railroad modernization tax credit."),
    (125, "S269"):  ("adjacent", T_TRANSIT, "Senate version of the shortline railroad modernization tax credit."),
    (126, "S399"):  ("adjacent", T_TRANSIT, "Made refusing to leave a public transit facility after a warning a misdemeanor, with a warning-and-appeal process (Act 222 of 2026)."),
    (126, "H4057"): ("adjacent", T_TRANSIT, "Would set standardized fees and a dispute process for utility lines crossing railroad property."),
    # ------------------------------------------------------------------
    # Planning for growth. Concurrency (making development wait for
    # infrastructure), comprehensive-plan elements, permitting rules,
    # and the annexation fights.
    (123, "S259"):  ("core", T_PLAN, "The Disaster Relief and Resilience Act (Act 163 of 2020): created the state Office of Resilience with a statewide resilience plan, and required local comprehensive plans to add a resiliency element."),
    (123, "H4731"): ("core", T_PLAN, "Would have required every local comprehensive plan to include a resiliency element - the idea enacted the same year in Act 163."),
    (125, "H5562"): ("core", T_PLAN, "Would have defined 'concurrency programs' in the zoning law - letting local governments require that infrastructure keep pace before new development is approved."),
    (126, "S227"):  ("core", T_PLAN, "Would define 'concurrency programs' in the zoning law so local governments can tie new development approvals to infrastructure keeping pace."),
    (126, "H4050"): ("core", T_PLAN, "House version of the concurrency-programs zoning bill."),
    (126, "H4390"): ("core", T_PLAN, "The Community Impact and Opportunity Assessment Act: would require community impact assessments - covering infrastructure, affordability, and displacement - before major zoning and development decisions."),
    (126, "H5742"): ("core", T_PLAN, "Would let a county council block municipal annexations in the county until a comprehensive infrastructure impact study and mitigation plan is approved."),
    (125, "H4651"): ("adjacent", T_PLAN, "The Annexation Fairness Act: counties would get legal standing to challenge municipal annexations, with new limits on noncontiguous annexation."),
    (124, "H5196"): ("adjacent", T_PLAN, "Would have let a municipality annex 'donut hole' areas it completely surrounds by ordinance."),
    (125, "H3236"): ("adjacent", T_PLAN, "Refile of the donut-hole annexation bill."),
    (126, "H4726"): ("adjacent", T_PLAN, "Refile of the donut-hole annexation bill."),
    (124, "S528"):  ("adjacent", T_PLAN, "The Home Attainability Act: would have cut local permitting costs and barriers to housing construction, including third-party building inspectors."),
    (124, "H3863"): ("adjacent", T_PLAN, "House version of the Home Attainability Act permitting package."),
    (125, "S4"):    ("adjacent", T_PLAN, "Refile of the Home Attainability Act permitting package."),
    (126, "S4"):    ("adjacent", T_PLAN, "Refile of the Home Attainability Act permitting package."),
    (123, "H4482"): ("adjacent", T_PLAN, "Would have required local governments and state agencies to prepare a housing impact analysis before adopting rules that change housing costs."),
    (123, "S757"):  ("adjacent", T_PLAN, "Senate version of the housing impact analysis requirement."),
    (123, "H4598"): ("adjacent", T_PLAN, "Would have revised local planning definitions and let compliant land surveys be filed without local planning review."),
    (123, "S833"):  ("adjacent", T_PLAN, "Senate version of the plat and subdivision definitions bill."),
    (123, "H4721"): ("adjacent", T_PLAN, "Would have aligned appeals from planning commission decisions with the process used for zoning appeals."),
    (125, "H4652"): ("adjacent", T_PLAN, "Would have given local permitting bodies forty-five days to decide building permit and zoning applications, after which the application is deemed approved."),
    (126, "H3215"): ("adjacent", T_PLAN, "Refile of the forty-five-day permit shot-clock bill."),
    (125, "H4996"): ("adjacent", T_PLAN, "Would have let local governments allow transfers of development rights between parcels by ordinance."),
    (126, "H4146"): ("adjacent", T_PLAN, "Refile of the transferable development rights bill."),
    (126, "S288"):  ("adjacent", T_PLAN, "Senate version of the transferable development rights bill."),
    (126, "S530"):  ("adjacent", T_PLAN, "Would void permits and stop construction when zoning officials determine a property's use is not permitted under its zoning."),
    (126, "H4293"): ("adjacent", T_PLAN, "House version of the zoning permit-invalidation bill."),
    # ------------------------------------------------------------------
    # Water, sewer, and broadband infrastructure.
    (125, "H3075"): ("adjacent", T_WSB, "Would have made the Rural Infrastructure Authority staff the state's water-and-sewer loan authorities - consolidating water infrastructure financing support."),
    (125, "H3076"): ("adjacent", T_WSB, "Would have defined 'environmental facilities' (water, sewer, solid waste projects) in the Rural Infrastructure Authority law."),
    (125, "H3077"): ("adjacent", T_WSB, "Would have expanded the Rural Infrastructure Authority's corporate purposes."),
    (125, "H3078"): ("adjacent", T_WSB, "Would have repealed a restriction on how Rural Infrastructure Authority funds are used."),
    (125, "H3079"): ("adjacent", T_WSB, "Would have updated the definition of a rural infrastructure project."),
    (126, "H3373"): ("adjacent", T_WSB, "Refile of the Rural Infrastructure Authority consolidation package."),
    (123, "S1076"): ("adjacent", T_WSB, "The Broadband Accessibility Act: would have set up a framework to extend broadband into unserved areas, including using electric cooperative infrastructure."),
    (123, "S1080"): ("adjacent", T_WSB, "Companion version of the Broadband Accessibility Act."),
    (123, "S1235"): ("adjacent", T_WSB, "Would have created a Broadband Development Office to coordinate extending high-speed internet."),
    (124, "S519"):  ("adjacent", T_WSB, "Would have created an Office of Broadband Development."),
    (123, "H4943"): ("adjacent", T_WSB, "Would have created a Rural Communications Infrastructure Study Committee on rural broadband gaps."),
    (123, "H4993"): ("adjacent", T_WSB, "Would have set the conditions for local governments to provide broadband internet service themselves."),
    (123, "H4262"): ("adjacent", T_WSB, "The Small Wireless Facilities Deployment Act: statewide rules for placing small 5G cells in rights of way, limiting local zoning control over them."),
    (123, "S638"):  ("adjacent", T_WSB, "Senate version of the small wireless facilities deployment rules."),
    # ------------------------------------------------------------------
    # Related context (kept for audit; excluded from headline counts).
    (123, "H4819"): ("context", T_CONTEXT, "Union County Transportation Committee membership - the county boards that spend gas-tax 'C' funds on local roads."),
    (123, "H5030"): ("context", T_CONTEXT, "Dorchester County Transportation Committee membership increase."),
    (123, "S988"):  ("context", T_CONTEXT, "Kershaw County Transportation Committee membership."),
    (123, "S994"):  ("context", T_CONTEXT, "Lee County Transportation Committee membership."),
    (124, "H3277"): ("context", T_CONTEXT, "Union County Transportation Committee membership."),
    (124, "S447"):  ("context", T_CONTEXT, "Lee County Transportation Committee membership."),
    (125, "S383"):  ("context", T_CONTEXT, "Lee County Transportation Committee membership."),
    (126, "S586"):  ("context", T_CONTEXT, "Kershaw County Transportation Committee membership."),
    (126, "S1050"): ("context", T_CONTEXT, "Hampton County Transportation Committee membership."),
    (126, "S1051"): ("context", T_CONTEXT, "Colleton County Transportation Committee membership."),
    (126, "S1052"): ("context", T_CONTEXT, "Jasper County Transportation Committee membership."),
    (123, "S175"):  ("context", T_CONTEXT, "Would have limited the General Assembly's naming of highways after living elected officials - the naming resolutions dominate this issue's raw search results."),
    (123, "S953"):  ("context", T_CONTEXT, "Would have barred naming roads, bridges, and public buildings for living persons."),
    (124, "S178"):  ("context", T_CONTEXT, "Would have revised the road and building naming rules."),
}

# Bills hand-added from the certified universe (not Pass 1 hits) - found
# by a title scan for sales-tax/annexation/hospitality phrases the Pass 1
# search terms did not cover.
UNIVERSE_ADDS = {
    (123, "S172"), (123, "H4597"), (123, "H3775"),
    (124, "H3129"), (124, "H5196"),
    (125, "H3236"),
    (126, "S1006"), (126, "H4726"), (126, "H5744"),
}

EXCLUSION_RULES = [
    "Road, bridge, and highway NAMING resolutions - several hundred concurrent resolutions asking SCDOT to name a road or bridge for a person - plus honorary/memorial/retirement resolutions whose text incidentally matches (Cambridge, trailblazer, 'transition', 'toll' in church names).",
    "False-positive full-text hits: 'traffic(king)' in human/drug trafficking bills; 'transit' inside transition/transitional; 'toll' inside tolling a statute of limitations; 'developer' and 'bridge' in honorary resolutions; 'multimodal' in AI chatbot bills; 'gas tax' in renewable natural gas; 'impact fee' in the SUPERB petroleum fund and opportunity-zone bills.",
    "Traffic safety, enforcement, and vehicle regulation: speed/red-light cameras, license plate readers, DUI, left-lane and right-half rules, ATV/utility-vehicle rules, trailer specs, railroad crossing stops, school bus passing, street takeovers (Act 148 of 2026), pedestrian signals, driver conduct.",
    "Housing policy bills whose lever is not growth infrastructure: inclusionary housing/zoning, ADU incentives, workforce housing development, school-district surplus land for teacher housing, co-ownership rules (the rising-cost-of-living issue's lane); the Home Attainability and housing-impact-analysis bills are kept as adjacent because their lever is the local permitting/planning system.",
    "Utility regulation and energy: electric rates, PSC oversight, energy facility siting, data centers, net neutrality, underground utility damage prevention, water/sewer rate disputes, wastewater spills; special-purpose-district and single-district local legislation (Broadway Water & Sewer).",
    "Vehicle sales 'Maximum Sales Tax' cap bills (livestock/watercraft trailers, musical instruments) - they amend the capped sales tax on vehicles, not local-option infrastructure taxes.",
    "General property-tax millage-cap and tax-relief bills (millage override, homestead reimbursement, TABOR-style spending caps) - local revenue policy without an infrastructure lever.",
    "Transportation Network Company (Uber/Lyft) regulation, commercial ad benches at bus stops, billboard relocation, scenic byway designations, DOT signage regulations, and airport/port authority board governance.",
    "Railroad operations and taxation details: trains blocking intersections (federal preemption), municipal license taxes on railroads, obstructing-highway penalties.",
    "Security-framed 'infrastructure' bills: critical-infrastructure trespass and drone bills (16-11), offshore-oil infrastructure bans, foreign-adversary land rules (the foreign-company contracting ban is kept as adjacent because its lever is contracting).",
    "Hyper-local road matters: Hunting Island park roads, Paris Mountain curb cuts, single-bridge study committees, county recreation commission appointments, school district consolidations.",
    "Criminal penalties for crimes against transportation workers and transit trespass predecessors (the enacted transit trespass act S399 is kept as adjacent).",
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
    wrong = [k for k in UNIVERSE_ADDS if k in bills]
    if wrong:
        raise SystemExit("universe adds actually in pass1: %r" % wrong)

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
                 "Tiers: core = bills squarely on the seven constituent proposals plus the "
                 "road-funding/SCDOT-governance agenda; adjacent = same lanes but narrower, "
                 "procedural, or industry-side; context = kept for audit only, excluded from "
                 "headline counts. Every ambiguous bill was verified against its latest-version "
                 "full text in _universe/. Nine bills were hand-added from the certified "
                 "universe (marked source=universe) because the Pass 1 search terms did not "
                 "cover 'sales tax', 'annexation', or 'hospitality tax' phrasings. All other "
                 "Pass 1 hits are excluded under the rules below."),
        "themes": THEMES,
        "counts": counts,
        "exclusion_rules": EXCLUSION_RULES,
        "bills": kept,
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print("kept", len(kept), "|", counts["by_relevance"])
    for t in THEMES:
        print("  %-62s %d" % (t, counts["by_theme"].get(t, 0)))


if __name__ == "__main__":
    main()
