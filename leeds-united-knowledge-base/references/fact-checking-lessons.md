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

- **GLM-4.7-Flash** (Z.AI free tier): Produces well-structured, good-quality prose but is prone to factual hallucinations on career details, tournament results, and honours. The writing quality masks the errors. Always run fact-verification after.
- **Owl Alpha** (OpenRouter free tier): Not yet tested for this task as of June 2026.
- The fact-checking gate is more important than model selection — even a good model can hallucinate specifics.
