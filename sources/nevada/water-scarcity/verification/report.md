# Verification Report — nevada-04-water-scarcity

**Status:** PASS_WITH_WARNINGS  
**Agent:** data-verifier  
**Data source:** NELIS_ONLY  

## Summary

- 147 NELIS bills present with identifiers, sessions, and source URLs
- Sampled bill pages returned HTTP 200; spot-check titles matched
- Bill actions/votes empty by export design (WARN)
- S25 is a valid PDF; S2 and S13 agency pages stored as HTML snapshots

## Warnings

- NELIS discovery export has bill titles/URLs only; actions and votes empty
- S2 and S13 saved as `.html` (source pages are HTML, not PDF)

## Blocking issues

None — pipeline may continue.
