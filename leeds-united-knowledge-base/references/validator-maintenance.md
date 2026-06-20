# validate_bio.py — Maintenance Guide

The validator (`scripts/validate_bio.py`, deployed at `/mnt/nas/leeds/research/validate_bio.py`) is the mandatory final gate for player biographies. This document captures bugs found during real audits and their fixes, so future maintainers don't reintroduce them.

## The 9 Checks

1. **Duplicate player records** — queries `players` by `last_name`, flags if >1 row
2. **Parents present & not fabricated** — checks ≥2 rows in `player_parents`, warns on non-"Unknown" names
3. **No fabricated death date** — checks DB `date_of_death` against markdown content for living players
4. **Career entries exist** — checks `player_career` for duplicates (club_id + start_year)
5. **Stats reconciliation** — sums competitive stats from DB, parses CAREER TOTAL from markdown, flags mismatch
6. **No orphaned records** — checks all child tables for player_ids that don't exist in `players`
7. **Honour types valid** — flags any `honour_type` not in ('club', 'individual')
8. **Markdown sections present** — checks for content keywords (flexible on section numbering)
9. **No "gold standard" notes** — flags any "gold standard" text in markdown

## Bugs Found and Fixed (June 2026 Audit)

### Bug 1: Stats dedup key was too broad

**Symptom:** Flagged legitimate per-season stat rows as duplicates for Ampadu, Charles, and Radebe.

**Root cause:** Dedup key was `(club_id, competition_type)` — but a player has multiple seasons at the same club in the same competition type (e.g., Ampadu at Leeds: league 2023-24, league 2024-25, league 2025-26 are all `club=1, type=league`).

**Fix:** Changed dedup key to `(club_id, competition_type, season)`. Each club+competition+season combination is unique.

**Lesson:** When deduplicating time-series data, always include the time dimension in the key.

### Bug 2: Section check was too rigid

**Symptom:** Flagged John Charles markdown as missing ALL sections.

**Root cause:** Charles bio was written before the 12-section standardization. It uses `## 1. Quick Reference`, `## 2. Personal Details`, etc. — different section names and numbering than the template. The validator expected `## N. <exact template keyword>`.

**Fix:** Changed from exact section-number matching to content-keyword matching. Now checks for presence of keywords like "parent", "appearance", "international" anywhere in the markdown, regardless of section numbering.

**Lesson:** Validators should check for CONTENT presence, not FORMAT compliance, when the format may vary between legacy and new files.

### Bug 3: Stats parsing couldn't find CAREER TOTAL

**Symptom:** Couldn't extract apps/goals from markdown for several players, producing "manual verification needed" warnings.

**Root cause:** The regex only searched within a `6a` section boundary. But section headers vary (`### 6a. Competitive`, `## 6. Appearance Statistics`), and some bios put the CAREER TOTAL outside the parsed section.

**Fix:** Two-strategy approach:
1. First, search the ENTIRE markdown for `CAREER TOTAL.*?(\d+)\s*/\s*(\d+)` — this finds the bold total row regardless of section boundaries.
2. Fallback: search within section 6a for bold `**314 / 5**` patterns.

**Lesson:** Parse totals from the most distinctive pattern (CAREER TOTAL keyword) rather than from section boundaries, which vary.

## Running the Validator

```bash
# Single player
python3 /mnt/nas/leeds/research/validate_bio.py --player-id <ID> --md-file /mnt/nas/leeds/research/leeds_players/<file>.md

# Strict mode (warnings also cause failure)
python3 /mnt/nas/leeds/research/validate_bio.py --player-id <ID> --md-file <file> --strict
```

Exit codes: 0 = all passed, 1 = violations found, 2 = connection/env error.

## Full-Player Audit Methodology

When asked to verify ALL players are accurate:

1. Query all players: `python3 supabase_helper.py get players "select=id,full_name,last_name,date_of_birth,date_of_death,bio_file&order=id.asc"`
2. Run validator on each player with their markdown file
3. For any failures, examine the specific error lines
4. **Independently verify dangerous fields** (validator can't check these):
   - Death dates: web_search for "[player name] footballer death" — confirm against Wikipedia/obituaries
   - Parent names: check if Wikipedia infobox has a parents/family field
   - Nationality: check which national team they represented
5. Fix issues in DB (via supabase_helper.py) and/or markdown (via patch)
6. Re-run validator until all pass
7. Push fixes to GitHub

## When to Update the Validator

- **New hallucination pattern discovered** → add a check
- **Validator false-positives a legitimate pattern** → fix the check's matching logic
- **Schema changes in Supabase** → update constraint checks
- **New field added to the template** → add to section/content check
