# Human Review Checklist — Legislative Brief Version 0

Use this checklist when reviewing a Pull Request for a Legislative Brief.

## Bill and citation integrity

- [ ] Every bill number in the executive summary appears in `appendix-a-bills.md`
- [ ] Every `[S-xxx]` citation exists in `sources-registry.json`
- [ ] Every `[P-xxx]` citation is framed as Forum process input, not verified fact
- [ ] No uncited factual claims remain in the executive summary

## Forum voice and scope

- [ ] Tone is nonpartisan — no party blame without vote record citation
- [ ] No recommendations (no "should", "must", "recommend", "urge" directed at legislature)
- [ ] Version 0 scope respected — no invented assembly proposals
- [ ] Executive summary is 1–3 pages (approximately 600–1800 words)

## Data quality

- [ ] Appendix row counts match source JSON files
- [ ] Data gaps are documented in `appendix-f-data-gaps.md` where applicable
- [ ] Dead or failed URLs from verification are noted
- [ ] 20-year impact claims have agency or fiscal source citations, or say INSUFFICIENT DATA

## Process

- [ ] `edit-log.md` and `tone-edit-log.md` are present
- [ ] `final-review-report.md` status is READY FOR HUMAN REVIEW (or blocking issues are resolved)
- [ ] At least two team members have reviewed

## Reviewers (Nevada water pilot)

- Ryan Echols
- Jodi Stephens (Nevada Legislative Liaison)
- Ashley Lovell (Nevada Policy Director)

## Approval

- [ ] **Approved for assembly viability use** — merge Pull Request
- [ ] **Changes requested** — leave comments on Pull Request
