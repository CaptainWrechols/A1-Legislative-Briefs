# Tone Edit Log — Executive Summary

**State:** nevada  
**Issue slug:** water-scarcity  
**Issue ID:** nevada-04-water-scarcity  
**Brief dir:** briefs/nevada/water-scarcity/version-0  
**Agent:** tone-editor  
**Date:** 2026-07-16  

Framing changes only. No facts, bill numbers, statistics, or citations added or removed. Section structure unchanged. Disposition labels that match the dataset schema (`Failed=40`, `7 failed`, `Among 40 failed bills`, status `Failed` on AB 265) were retained as factual stall/disposition language.

| Location | Original phrase | Revised phrase | Rule applied |
|----------|-----------------|----------------|--------------|
| §2 2019 | Failures include AB 51 … | Bills that did not advance include AB 51 … | Forbidden pejorative framing (`failed` as advocacy noun); analytical non-advancement wording |
| §2 2021 | Origin-committee failures include AB 354 … | Bills that did not advance past origin committee include AB 354 … | Same; required replacement pattern (“did not advance past [stage]”) |
| §2 2021 | No multi-party sponsorship signals in extracts for this session | Available records show no multi-party sponsorship signals in extracts for this session | Humble uncertainty (“Available records suggest/show…”) |
| §2 2023 | Failures include SB 112 … | Bills that did not advance include SB 112 … | Forbidden pejorative framing; analytical non-advancement wording |
| §2 2023 | No multi-party sponsorship signals in extracts | Available records show no multi-party sponsorship signals in extracts | Humble uncertainty |
| §2 2025 | Failures concentrate in origin committee | Bills that did not advance concentrate in origin committee | Forbidden pejorative framing; analytical non-advancement wording |
| §4 patterns | SB 112, SB 176 failed | SB 112, SB 176 did not advance | Analytical disposition framing (not legislature-blame) |
| §4 patterns | all failed without enactment | did not result in enactment | Analytical; avoid pejorative “failed” outside schema labels |
| §4 patterns | AB 134 failed in 2025 origin committee | AB 134 did not advance past 2025 origin committee | Required replacement pattern (“did not advance past [stage]”) |
| §4 patterns | SB 102 failed | SB 102 did not advance | Analytical disposition framing |
| §4 patterns | each have one failed instance — insufficient for a strong conclusion | each have one non-advancing instance — available records are insufficient for a strong conclusion | Analytical + humble uncertainty |
| §4 stall points | committees alone block passage | committees alone account for non-advancement | Forbidden word `blocked`/`block` |
| §5 | do not prove single-party sponsorship | do not establish single-party sponsorship | Avoid “prove” certainty framing |
| §6 | Evidence suggests enacted water-related legislation is common | This history may indicate that enacted water-related legislation is common | Deliberation-ready / assembly-viability framing |
| §6 | groundwater-board bills failed without enactment | groundwater-board bills did not result in enactment | Analytical disposition framing |
| §6 | conservation bill failing in origin committee | conservation bill not advancing past origin committee | Required replacement pattern |
| §6 | Evidence suggests DWR appropriations enactments are common | This history may indicate that DWR appropriations enactments are common | Deliberation-ready framing |
| §6 | beyond a single failed bill | beyond a single bill that did not advance | Analytical disposition framing |

## Checklist

- [x] No forbidden advocacy phrases remain (`should`/`must`/`need to` directed at legislature; `refused`/`blocked`; certainty intensifiers; party insults; advocacy slogans)
- [x] Process input properly labeled — none present; Phase 1/Phase 2 absence noted; no improper `[P-xxx]`
- [x] All `[S-xxx]` citations preserved (188 inline citation tokens; unique keys unchanged)
- [x] All bill numbers preserved
- [x] No recommendations introduced
- [x] Section structure identical (§1–§7 + Source notes)
- [x] Sentence rewrite share under 15% (phrase-level framing edits only; no `TONE_OVERHAUL_NEEDED`)

## Handoff

Tone Editor finished. Run **General Formatter** on entire `briefs/nevada/water-scarcity/version-0/`.
