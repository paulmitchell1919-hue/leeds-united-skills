# Fact-Checking Lessons — AI-Generated Player Biographies

Documented hallucination patterns from LLM-generated Leeds United player bios. These are real errors caught during quality review. Use as a checklist when reviewing any AI-generated bio.

## Case Study: Lucas Radebe (GLM-4.7-Flash, June 2026)

### Errors Found

| Error | Bio Claimed | Reality | Source |
|-------|------------|---------|--------|
| **Fabricated club** | Bolton Wanderers (loan, 2005-06, 3 apps) | Radebe never played for Bolton. He retired at Leeds in 2005. | Transfermarkt career history — no Bolton entry |
| **Reversed tournament result** | 1996 AFCON: "Runner-up, lost 2-0 to Egypt" | South Africa WON the 1996 AFCON, beating Tunisia 2-0 in the final. Egypt didn't even make the final. | Wikipedia 1996 AFCON article, RSSSF |
| **Invented physical honour** | "Statue at Elland Road unveiled 2023" | No Radebe statue exists. The only statue at Elland Road is Billy Bremner. | Leeds United official, physical reality |
| **Extended competition history** | "Champions League semi-finals 2000-01 AND 2002-03" | Leeds only reached CL semi in 2000-01. Were not in the competition in 2002-03. | UEFA records, Wikipedia |
| **Dubious "first" claim** | "First Black South African to play for Bafana Bafana" | Bafana Bafana was formed in 1992 post-apartheid and was predominantly Black from inception. The claim is misleading. | Historical context |

### Pattern Analysis

1. **Fabricated club stint** — The model invented a plausible-sounding late-career loan. This is the most dangerous pattern because it creates an entire section of fictional narrative. **Mitigation**: verify EVERY club against Transfermarkt or Wikipedia career table.

2. **Reversed result** — The model confused "runner-up" with "winner" for a major tournament. This is particularly damaging for a player's legacy bio. **Mitigation**: always check tournament outcomes against the actual tournament page.

3. **Invented statue** — The model created a physical artifact that doesn't exist. These are especially dangerous because they sound verifiable but aren't. **Mitigation**: any physical claim (statue, plaque, renamed stand, hall of fame) must be sourced.

4. **Extended timeline** — The model doubled the Champions League semi-final appearance. **Mitigation**: cross-reference competition participation against club season records.

## Case Study: John Sheridan (GLM-4.7-Flash, June 2026)

### Supabase Data Integrity Issues (not factual errors, but quality issues)

| Issue | What Happened | Fix |
|-------|--------------|-----|
| **Stats double-counting** | DB showed 853 apps / 159 goals vs markdown's 622 / 89. Agent entered BOTH aggregate career totals AND per-season breakdowns for the same clubs. | Use ONE approach per club (aggregate is fine). Never enter both "1982-89: 230 apps" AND "1986-87: 35 apps" for the same club. |
| **Duplicate rows** | Career and international tables had duplicate entries from retrying POSTs without GET-first checks. | Always GET before POST. See Anti-Duplicate Rules in SKILL.md. |
| **Missing parents** | 0 rows in player_parents despite the skill saying parents must always be inserted. | Insert parents even when names unknown (name = "Unknown"). |
| **Missing friendly stats** | Section 6b content not entered into DB. | Insert friendly stats with competition_type 'friendly'. |

## Case Study: Eddie Gray (GLM-4.7-Flash, June 2026)

### Errors Found

| Error | Bio Claimed | Reality | Source |
|-------|------------|---------|--------|
| **Fabricated death date** | date_of_death = 2024-11-17 | Eddie Gray is ALIVE. Born 1948, no death documented. | Wikipedia — no death mentioned, still active as pundit |
| **Fabricated parent names** | Father = "Johannes Radebe", Mother = "Emily Radebe" | No parent names documented in any scraped source. | Wikipedia Eddie Gray page — no family section with parent names |
| **Duplicate player records** | 3 separate rows in players table (id=5, 6, 8) for same person, with contradictory death data | Should be ONE record. id=5 had fabricated death date, id=6 had different known_as, id=8 was a silent duplicate. | Supabase query: `GET players?last_name=eq.Gray` returned 3+ rows |
| **is_competitive in POST payload** | Included `"is_competitive": true` in player_stats POST | This is a GENERATED column — the DB computes it from competition_type. Including it triggers `428C9` error. | Supabase error response |
| **honour_type='international'** | Used `'international'` for British Home Championship honours | Check constraint only allows `'club'` and `'individual'`. International honours must use `honour_type='club'` with `club_id=null`. | Supabase error response: `23514` constraint violation |

### Pattern Analysis

1. **Fabricated death date** — The model assigned a death date to a living player. This is the most dangerous pattern: it changes the fundamental status of the subject. **Mitigation**: if Wikipedia doesn't mention a death, the player is alive. Never set `date_of_death` unless a source explicitly confirms it.

2. **Fabricated parent names** — The model invented plausible-sounding parent names ("Johannes" and "Emily" — common South African names) that don't appear in any source. **Mitigation**: parent names must come from scraped sources ONLY. Default to "Unknown" with notes "Not publicly documented".

3. **Duplicate player records** — The model created multiple player rows for the same person during retry attempts, each with slightly different data. This created orphaned child records (stats, honours pointing to deleted player_ids). **Mitigation**: always `GET` by `last_name` before creating a player. If duplicates exist, consolidate before inserting any new data.

4. **Code-enforcement lesson** — The agent had 180 lines of SOUL.md rules saying "don't fabricate" and still fabricated. Prose rules alone don't work. Only a **code-enforced validation gate** (`validate_bio.py` with exit code 0 required) prevents these errors from reaching "complete" status.

### Resolution

Built `validate_bio.py` — a 9-check hard-stop validator that billresearch MUST run before reporting complete. Catches: duplicate players, fabricated parents, fabricated death dates, stats mismatch, orphaned records, invalid honour_type, missing sections, duplicate entries, "gold standard" template notes.

## Verification Protocol

After any AI-generated bio, run this checklist:

```
For each club in section 5 (career):
  [ ] Does this club appear in Transfermarkt/Wikipedia career table?
  [ ] Are the years roughly correct?

For each tournament in section 7 (international):
  [ ] Is the result (won/lost/round reached) correct per RSSSF/Wikipedia?

For each honour in section 9:
  [ ] Is the honour real? (not invented)
  [ ] Is the season correct?

For any physical claim (statue, plaque, renamed stand):
  [ ] Verified against club announcement or news source?

For any "first" or "only" claim:
  [ ] Verified against historical record?
```

## Model Quality Notes

- **GLM-4.7-Flash** (Z.AI free tier): Produces well-structured, good-quality prose but is prone to factual hallucinations on career details, tournament results, honours, parent names, and death dates. The writing quality masks the errors. Always run fact-verification + `validate_bio.py` after.
- **Owl Alpha** (OpenRouter free tier): Not yet tested for this task as of June 2026.
- The fact-checking gate is more important than model selection — even a good model can hallucinate specifics.
- **Prose rules don't work** — billresearch had 180 lines of SOUL.md anti-hallucination rules and still fabricated parent names, death dates, and duplicate records. Only the code-enforced `validate_bio.py` gate (exit 0 required) actually prevents errors from reaching "complete" status.
