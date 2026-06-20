---
name: leeds-united-knowledge-base
description: "Class-level playbook for building and maintaining a comprehensive Leeds United encyclopedia (people, seasons, matches, trophies, transfers, events, awards, records, stadiums, kits, Hall of Fame, academy, loans, captains, injuries/memorials). Use when the task asks for long-term maintainable club history data for a website, newsletter, social channels, AI search or automated content generation."
version: 0.2.0
author: Mitch-TechWorks
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [football, leeds-united, knowledge-base, encyclopedia, structured-data]
    related_skills: [leeds-united-results-scraping, leeds-united-transfers-research]
---

# Leeds United Knowledge Base

## Overview

Build a structured, searchable encyclopedia for Leeds United, stored under `/home/paul/leeds-knowledge/`.

Target consumers: website pages, AI retrieval/RAG, newsletter generation, "On This Day", YouTube scripts, social posts, automated content generation.

## Directory layout

```
/home/paul/leeds-knowledge/
  SCHEMA.md
  global/people-index.json
  global/seasons-index.json
  global/events-index.json
  global/trophies-index.json
  people/{players,managers,staff,owners_directors}/
  seasons/
  matches/
  transfers/{in,out}/
  events/
  trophies/
  stadiums/
  kits_sponsors/
  records/
  awards/
  hall_of_fame/
  academy/
  loans/
  injuries_memorials/
  captains/
  raw_sources/
  scripts/{build_seasons.py,populate_kb.py}
```

## Proven data sources and access patterns

### Build scripts
- `scripts/build_seasons.py` — creates minimal season stubs from `leeds-tools/round_json/*.json`.
- `scripts/populate_kb.py` — bulk-generates the full entity graph from match CSV and known highlights; re-run after schema changes or new raw data.

### Club match data (already primary)
- Match history: `/home/paul/leeds-results/leeds_results_clean.csv`
- Derived round tables, season summaries, cup summaries: `/home/paul/leeds-tools/out/{seasons,leagues,cups,matches}/`
- Raw modern-season markdown: `/home/paul/leeds-results/raw/11v11/<YYYY>.md`

### Player / people scope discovery
- leeds-fans archive exposes player pages as `/leeds/players/<id>.html`; season pages such as `/leeds/history/<id>.html` contain links to played IDs. Crawl those links to enumerate historical and modern squad members.
- Wikipedia REST API is usable if a proper User-Agent is set; default requests get `403` with a robots policy notice. Use headers: `{'User-Agent': 'Mozilla/5.0 (compatible; Leeds-KB research bot; local dev)'}`.
  - Endpoints: `GET https://en.wikipedia.org/api/rest_v1/page/summary/{Title}` works with that UA for summaries.
  - Do not use Wikipedia as the sole source; capture `source_references` and flag uncertain fields in `notes`.

- Modern cloudflare-protected pages
- 11v11 and worldfootball.net often return Cloudflare challenges to shell requests.
- Reliable local fallback: `POST http://127.0.0.1:3002/v0/scrape`, body json `{\"url\": URL, \"formats\": [\"markdown\"], \"onlyMainContent\": true}`.
- Save only `data.content` from the response to normalized raw markdown files; do not store the full response envelope.

### Build scripts
- `scripts/build_seasons.py` — creates minimal season stubs from `leeds-tools/round_json/*.json`.
- `scripts/populate_kb.py` — bulk-generates the full entity graph from match CSV and known highlights; re-run after schema changes or new raw data.
- See `references/kb-population-lessons.md` for guardrails on re-running, placeholder cleanup, and normalization rules.

## Standard workflow

1. Scope discovery first
   - Enumerate people from leeds-fans player-page links.
   - Enumerate seasons from existing `/home/paul/leeds-knowledge/global/seasons-index.json`.
   - Enumerate trophies, managers, chairmen, notable events from club/national pages.
2. Research in parallel workers
   - Use delegate workers for independent axis research: players, managers/coaches, backroom staff, owners/directors, transfers in, transfers out, captains, trophies, stadiums, kits/sponsors, records, awards, Hall of Fame, academy prospects, loans, injuries/memorials, events.
3. Verify and normalize
   - For disputed facts, keep provenance and a `notes` flag.
   - Do not invent data. Leave uncertain fields null and record the gap in `notes`.
4. Bulk-create schemas from live values
   - Where possible, add all known real items from match data/scrape indexes, then enrich per-entity.
5. Re-run season-level aggregations only when schema changes
   - `populate_kb.py` is the expensive circuit breaker — run only after match CSV/schema changes or when adding new entity types that depend on season objects.
6. Auditing and provenance
   - Every entity stores `source_references`: `{title, url, accessed_date, notes}`.
   - Keep raw scrapes under `raw_sources/` for reproducible traceability.

## Transfer research workflow

Use the workflow documented in `§10 Leeds United Transfer Research` below to build a structured transfer database. The transfer skill covers source priority (Transfermarkt, official club news, Premier League/EFL retained lists, wage sites, Wikipedia), required CSV schema, confidence rules, and pitfalls.

Key points:
- Do not overwrite exact source text with your estimate; keep `fee_reported` and `fee_gbp_estimate` separate.
- Wages are estimates from salary sites — set `confidence: medium` or `low`.
- Create `source_audit.md` with gaps and caveats at the end of every scraping run.

## Match results scraping workflow

Use the repeatable scrape/validation workflow in `§9 Leeds United Match Results Scraping` to build or refresh `~/leeds-results/leeds_results_clean.csv`.

Highlights:
- `leeds-fans.org.uk` is the primary historical source for 1919-20 through 2008-09.
- Continue from 2009-10 onward through direct 11v11 season pages, falling back to worldfootball.net.
- Normalize all dates to ISO `YYYY-MM-DD`, scores from Leeds perspective, and keep `source_url` on every row.
- Save raw extracted markdown under `~/leeds-results/raw/11v11/<ending_year>.md`.

## Supabase Data Layer (Query Layer)

The Supabase PostgreSQL database is the **query layer** for structured cross-player queries (e.g. "how many players featured in 1947?", "who scored in season X?"). The markdown biography files are the **content layer** (human-readable). Both layers must be maintained per player.
Full schema, API patterns, anti-duplicate rules, and known issues are documented in:

- [references/supabase-data-layer.md](references/supabase-data-layer.md) — connection, 7-table schema, REST API patterns
- [references/supabase-schema-details.md](references/supabase-schema-details.md) — generated columns, check constraints, honour_type enum, duplicate-record consolidation, parent-name policy
- [scripts/supabase_helper.py](scripts/supabase_helper.py) — general CRUD helper (get, post, post_batch, delete, check_dup, count, tables, schema). **Use this instead of raw curl** — handles auth internally, avoids JWT truncation. Deployed at `/mnt/nas/leeds/research/supabase_helper.py`.
- [scripts/verify_player_supabase.py](scripts/verify_player_supabase.py) — **RUN THIS** after every player entry to verify data integrity

### Critical Supabase Rules

1. **GET before POST** — always check if a row exists before inserting. Retrying a failed POST without checking creates duplicates.
2. **Parents always inserted** — even when names are unknown, insert with name = "Unknown". Skipping is never acceptable. **Parent names must come from scraped sources, not the model's internal knowledge.** If a source doesn't name a player's parents, the answer is "Unknown", never rendered names.
3. **Check for duplicate player records** — before creating a new player, search by `last_name` or `full_name``. If multiple rows exist for the same person, consolidate: delete extras (with cascade on children), keep one canonical record, then re-insert all related rows (parents, career, stats, honours) with the correct player_id.
4. **Stats must reconcile** — sum of competitive appearances/goals in DB must match section 6a of the markdown. Run the verification script to confirm.
5. **Friendly stats go in DB too** — section 6b content must be inserted with competition_type 'friendly', 'testimonial', or 'other_non_competitive'.
6. **`is_competitive` is generated** — omit it from POST payloads for `player_stats`. The DB computes it from `competition_type`.
7. **`honour_type` enum is `'club'` or `'individual'`** — international/national-team honours use `honour_type='club'` + `club_id=null`. Never use `'international'`; it violates the check constraint.

### Verification Script (MANDATORY FINAL GATE)

After entering any player AND after writing the markdown, run the validation gate:

```bash
python3 /mnt/nas/leeds/research/validate_bio.py --player-id <ID> --md-file /mnt/nas/leeds/research/leeds_players/<file>.md
```

This is the **FINAL GATE** — billresearch CANNOT report a bio as "complete" until this script returns exit code 0.
If it returns exit 1, fix every violation listed and re-run until clean.

Checks: duplicate player records, fabricated parent names, fabricated death dates, stats reconciliation (DB totals must match markdown §6a), orphaned child records, invalid honour_type values, missing markdown sections, duplicate stats/career entries, "gold standard" template notes.

The older verification script is also available for deeper diagnostics:
```bash
python scripts/verify_player_supabase.py --player-id <ID>
```

## Fact-Verification Gate (MANDATORY for AI-generated research)

When an LLM agent (e.g. billresearch) writes biographies or other research content, the model's internal knowledge is NOT a reliable source for factual claims. LLMs hallucinate plausible-sounding details — invented clubs, reversed tournament results, fabricated honours. Every factual claim must be verified against actual scraped sources.

### Required verification before marking any bio complete

1. **Club career verification** — Check EACH club in the career timeline against at least one scraped source (Transfermarkt career history, Wikipedia career table). If the model says a player was at Club X, verify Club X actually appears in their career record. This is the #1 hallucination pattern: fabricating a club stint that never happened.

2. **Tournament result verification** — Verify winners, losers, scores, and rounds reached against the actual tournament page (RSSSF, Wikipedia tournament article). Models frequently reverse results (saying a team lost when they won, or vice versa).

3. **Honours and awards verification** — Each honour, trophy, individual award, or record claim must be confirmed by at least one independent source. Models invent plausible-sounding awards that don't exist.

4. **Physical claims verification** — Statues, renamed stands, plaques, hall of fame inductions, and other tangible honors are especially prone to fabrication. Verify these explicitly against club announcements or news sources.

5. **"First" or "only" claims** — Any claim of being "the first X" or "the only Y" must be verified. Models confidently make these claims without evidence.

### Known fabrication patterns (observed in GLM-4.7-Flash and billresearch runs)

- **Inventing a loan/short stint at a plausible club** (e.g., Lucas Radebe at Bolton Wanderers — never happened)
- **Reversing tournament results** (e.g., saying South Africa were 1996 AFCON runners-up when they WON it on home soil)
- **Fabricating physical honors** (e.g., claiming a statue at Elland Road that doesn't exist)
- **Extending competition history** (e.g., claiming Champions League semi-final in a year the club wasn't in the competition)
- **Plausible-but-wrong career details** (transfer fees, dates, caps that are close to reality but incorrect)
- **Fabricating parent names** (e.g., "Johannes Radebe" and "Emily Radebe" — never documented in scraped Wikipedia)
- **Impersonating a dead person** (e.g., fabricating a death date (2024-11-17) for a living player Eddie Gray)
- **Creating duplicate player records** (e.g., generating two player rows for Eddie Gray with contradictory death data)
- **Fabricating parent names** (e.g., "Johannes Radebe" and "Emily Radebe" — never documented)
- **Impersonating a dead person** (e.g., fabricating a death date for a living player)
- Using `honour_type='international'` (violates DB check constraint; only `'club'` and `'individual'` allowed)
- Including `is_competitive` in `player_stats` POST payloads (violates generated column constraint)

### Implementation

After the agent completes the research and writes the markdown file, run a second pass:
1. Re-read the bio
2. For each club in section 5, verify it appears in a scraped source
3. For each tournament result in section 7, verify the outcome
4. For each honour in section 9, verify it's real
5. Flag and correct any fabricated claims before entering data into Supabase

See [references/fact-checking-lessons.md](references/fact-checking-lessons.md) for documented cases.

### Supabase Auth — Use Helper Scripts, NEVER Raw Curl

When running as billresearch (or any agent via Hermes terminal), **do NOT inline Supabase service_role keys in curl commands.** The JWT keys are 200+ characters and get truncated in terminal display, causing 401 Unauthorized errors. The keys in `/mnt/nas/leeds/.env` are full-length — the truncation is a display artifact.

Instead, use the two helper scripts which handle auth internally:

1. **`scripts/supabase_helper.py`** — general CRUD (get, post, post_batch, delete, check_dup, count, tables, schema). Deployed copy at `/mnt/nas/leeds/research/supabase_helper.py`.

```bash
# Get data
python3 /mnt/nas/leeds/research/supabase_helper.py get players id=eq.3

# Insert (check first to avoid duplicates)
python3 /mnt/nas/leeds/research/supabase_helper.py check_dup player_career "player_id=eq.3&club_id=eq.1"
python3 /mnt/nas/leeds/research/supabase_helper.py post player_career '{"player_id": 3, ...}'

# Delete a duplicate
python3 /mnt/nas/leeds/research/supabase_helper.py delete player_career id=eq.30
```

2. **`scripts/verify_player_supabase.py`** — verification only (duplicates, parents, stats reconciliation). Run after every player entry.

```bash
python3 ~/.hermes/skills/research/leeds-united-knowledge-base/scripts/verify_player_supabase.py --player-id 3
```

## Content policy

- Prefer official club sources, reputable news (BBC, Guardian, Yorkshire Evening Post, The Athletic), and football databases when needed for cross-check.
- Flag uncertain facts explicitly in `notes`.
- Maintain stable slugs for file paths and IDs; do not retitle lightly.

## Pitfalls

1. Trusting Wikipedia alone; it's good for scope enumeration but needs secondary verification.
2. Firmly relying on shell requests to 11v11/worldfootball without Firecrawl fetch fallback.
3. Spending tokens on stylistic narrative rather than structured entity data and references.
4. Rebuilding round-table/season outputs on every schema edit; do it only for material data changes.
5. Forgetting that match CSV feeds all season objects; any schema change to match row semantics affects downstream summaries.
6. Starting transfer research with broad web search — generate direct season URLs instead.
7. Treating undisclosed as zero — `undisclosed` is not free.
8. Treating wages as official — most wage sites are estimates.
9. Mixing loan returns with paid transfers — use `loan_return` and note direction carefully.
10. Dropping released players — retained lists and official end-of-season pages matter.
11. Overwriting exact source values — keep exact text and estimates in separate columns.
12. Assuming Transfermarkt covers 1919-present perfectly — it doesn't. Use historical sources and mark gaps.
13. Starting results scraping with broad web search — use the direct URLs above.
14. Treating score as home-team score — some sources list result from Leeds perspective. Parse venue before assigning home/away goals.
15. Dropping 1919-20 — the first season page is `1.html` and may not appear as a normal linked season in the index.
16. Ignoring wartime seasons — keep them, but mark competition/season notes honestly.
17. Mixing source schemas — always normalize into one schema and keep `source_url` per row.
18. Pretending modern data is done without checking — leeds-fans stops in 2008-09. Continue via 11v11/worldfootball.
19. 11v11 date parsing — 11v11 markdown uses **abbreviated month names** (`08 Aug 2009`). Map `Jan`->`January` etc. before parsing; do not assume `%B` full-month input.
20. Player/cup/Europe misclassification — The raw leeds-fans CSV leaves `competition` blank for many older cup and European ties and embeds the competition hint in `opponent` or `notes` (`FACR3`, `CL2-4`, `LCR3`, `UCR2-1`). If these are left blank the generator defaults to "league". When summing player goals by competition, classify from `competition` + `opponent` + `notes`, not venue alone.
21. **`is_competitive` is a GENERATED column — DO NOT include it in POST payloads for `player_stats`.** Send only `competition_type`; PostgREST computes `is_competitive` automatically. Including it triggers a `428C9` error.
22. **`honour_type` check constraint only allows `'club'` and `'individual'`** — NOT `'international'`. International/national-team honours (e.g. British Home Championship, AFCON medals) must be stored with `honour_type='club'` and `club_id=null`.
23. **Template notes must not claim a file is the "gold standard"** — every bio should simply note it follows the standard 12-section template. Claiming "gold standard" status creates a daisy-chain of inflated template notes across subsequent bios.
24. **Always check for duplicate player records before creating** — after working with Eddie Gray, the DB had TWO rows for the same person, one with fabricated death data. When a name query returns multiples, consolidate first: delete extras, keep one canonical record, then re-insert children with the correct player_id.
25. **Parent names must be documented, not invented** — if scraped sources do not state parent names, insert `name="Unknown"` with `notes="Not publicly documented"`. Fabricated names violate the anti-hallucination policy.
26. **Youth club career entries need correct `status` values** — youth entries use `status='youth'`; senior transitions use `status='senior_permanent'`. The `player_career_status_check` enum rejects `'senior'` alone.

## §9 Leeds United Match Results Scraping

Use when collecting Leeds United historical match results from 1919 to present. Avoids broad web search by using known source URLs, direct season patterns, and a repeatable scrape/validation workflow.

### Overview

Source of truth for match result collection (moved here from the standalone `leeds-united-results-scraping` skill). Full source history and operational context are preserved in archived copies under `~/.hermes/skills/.archive/leeds-united-results-scraping/`.

Target deliverable: a structured dataset of Leeds United match results from club formation in 1919 to the current season.

Recommended output columns:

```csv
season,date,competition,round,home_team,away_team,venue,opponent,leeds_goals,opponent_goals,result,crowd,scorers,source_url,source_name,notes
```

Keep one raw copy and one cleaned copy:

```text
~/leeds-results/
  raw/                 # original HTML/markdown/downloads
  leeds_results_raw.csv
  leeds_results_clean.csv
  source_audit.md
```

### Source Priority

#### 1) leeds-fans.org.uk archive — best direct scrape for 1919-20 to 2008-09

Direct index:

```text
https://www.leeds-fans.org.uk/leeds/history/Results.html
```

Known first season page, not linked cleanly from the index:

```text
https://www.leeds-fans.org.uk/leeds/history/1.html   # 1919-20 Midland League
```

Other season pages are linked from the index as `/leeds/history/<id>.html`.

Strengths:
- Plain HTML, no JS, no Cloudflare.
- Includes date, opponent, venue marker, result, crowd, points, position, scorers.
- Covers the awkward early years and wartime seasons.

Limitations:
- Stops at 2008-09.
- Venue is embedded in opponent text, e.g. `Barnsley (H)` or `Silverwood Colliery (Millmoor)`.
- Some wartime season labels are irregular. Keep their labels exactly as sourced.

#### 2) 11v11 — best cross-check and modern continuation

Direct pattern:

```text
https://www.11v11.com/teams/leeds-united/tab/matches/season/1921/
https://www.11v11.com/teams/leeds-united/tab/matches/season/2026/
```

The `season` value is the ending year. Examples:
- `season/1921/` = 1920-21
- `season/2009/` = 2008-09
- `season/2026/` = 2025-26

Use `web_extract` first on these URLs. If command-line `requests` or `curl` gets a Cloudflare 403, do not keep retrying the shell. Use `web_extract` or the browser tool.

#### 3) worldfootball.net — second cross-check / current fixtures

Direct pattern:

```text
https://www.worldfootball.net/teams/leeds-united/1921/3/
https://www.worldfootball.net/teams/leeds-united/2026/3/
```

The year is also the season ending year. Use `web_extract` first. Shell requests may get Cloudflare.

#### 4) Mighty Leeds — narrative and PDFs for spot checks

Season pages:

```text
http://www.mightyleeds.co.uk/seasons/192021.htm
```

Good for resolving disputed early matches, but less convenient as a primary scrape because some result tables are PDFs.

### Standard Workflow

#### Step 1 — Create a working folder

```bash
mkdir -p ~/leeds-results/raw ~/leeds-results/reports
```

#### Step 2 — Scrape 1919-20 to 2008-09 from leeds-fans

The scraping helper script is preserved under `references/scrape-leeds-fans-readme.md`:
- Old path: `scripts/scrape_leeds_fans.py`
- Invoke directly if still present on disk.

Expected behaviour:
- Downloads the Results.html index.
- Forces inclusion of `1.html` for 1919-20.
- Parses every linked season page with a match table.
- Writes CSV rows with source URL and season label.

#### Step 3 — Continue 2009-10 to current season with direct URLs

Do not search. Generate the 11v11 URLs directly:

```python
for ending_year in range(2010, 2027):
    print(f"https://www.11v11.com/teams/leeds-united/tab/matches/season/{ending_year}/")
```

Call `web_extract` in batches of up to 5 URLs. Extract the match table from the markdown returned by the tool and append rows using the same schema.

Fallback: use worldfootball URLs with the same ending years:

```python
for ending_year in range(2010, 2027):
    print(f"https://www.worldfootball.net/teams/leeds-united/{ending_year}/3/")
```

##### 11v11 markdown caveat

11v11 season markdown uses **abbreviated month names** such as `08 Aug 2009`. Treat any date parsing as tolerant:
- accept `08 Aug 2009` and `8 August 2009`
- map `Jan` -> `January`, `Feb` -> `February`, ..., `Dec` -> `December` before parsing

The local parser/loader must handle 3-letter month codes; do not assume `%B` full-month input.

#### Step 4 — Normalize rows

Rules:
- `season`: use football season label, e.g. `1919-20`, `2025-26`.
- `date`: ISO `YYYY-MM-DD` when possible. Keep raw date in `notes` if uncertain.
- `home_team` / `away_team`:
  - venue `H`: Leeds United home.
  - venue `A`: Leeds United away.
  - venue `N`, named ground, `Unknown`, or cup final: set `venue` to the raw marker and infer home/away only when source is explicit.
- `leeds_goals` and `opponent_goals`: parse from Leeds perspective, not home-team perspective.
- `result`: `W`, `D`, `L` from Leeds perspective.
- Penalties: keep normal score in score fields and put shootout in `notes`, e.g. `pens 4-2`.
- Do not silently discard friendlies or wartime matches. Mark competition/notes clearly if the source marks them differently.

#### Step 5 — Validate counts and duplicates

Run these checks before reporting completion:

```python
import pandas as pd
p = '~/leeds-results/leeds_results_clean.csv'
df = pd.read_csv(p)
print(df.groupby('season').size().tail(25))
print('rows', len(df))
print('duplicate keys', df.duplicated(['date','opponent','leeds_goals','opponent_goals','source_name']).sum())
print(df[df['date'].isna() | df['opponent'].isna()].head(20))
```

If pandas is not installed, use Python stdlib CSV and print row counts by season.

#### Step 6 — Keep an audit trail

Create `source_audit.md` with:

```markdown
# Leeds United Results Source Audit

- Primary historical source: leeds-fans.org.uk Results archive, pages 1 + linked season pages, accessed DATE.
- Modern continuation: 11v11 season pages, ending years YYYY-YYYY, accessed DATE.
- Cross-check source: worldfootball.net / Mighty Leeds where needed.
- Known gaps / uncertainties:
  - ...
```

## Modern Continuation > Current Season

`leeds-fans.org.uk` stops at 2008-09. Continue from 2009-10 onward using direct 11v11 season pages.

### Generating modern 11v11 URLs

```python
for ending_year in range(2010, 2027):
    print(f"https://www.11v11.com/teams/leeds-united/tab/matches/season/{ending_year}/")
```

Examples:
- `season/2010/` = 2009-10
- `season/2026/` = 2025-26

### Save raw extracted markdown under `~/leeds-results/raw/11v11/`

For each modern season, save the fetched page content as `/home/paul/leeds-results/raw/11v11/<ending_year>.md`, using only the **extracted `markdown` content**, not the full API/HTTP response body. This keeps raw sources normalized and comparable across seasons.

### Structured outputs

Regenerate or refresh structured outputs with `/home/paul/leeds-tools/extract_league_tables.py`. It writes to:

```text
/home/paul/leeds-tools/out/
  seasons/YYYY-YY.json
  leagues/YYYY-YY_rounds.json
  cups/YYYY-YY_cups.json
  matches/YYYY-MM-DD-opponent.json
```

One-shot round-table generation can be found in the same `out/` tree as `leagues/YYYY-YY_rounds.json`.

### Verification checklist

- [ ] Raw HTML/markdown saved for each source used.
- [ ] 1919-20 season included.
- [ ] 2008-09 included from leeds-fans.
- [ ] 2009-10 to current season attempted via direct 11v11/worldfootball URLs.
- [ ] Each row has `source_url` and `source_name`.
- [ ] Date/opponent/score missing rows reviewed manually.
- [ ] Duplicate check run.
- [ ] `source_audit.md` created with gaps and uncertainties.

### Dealing With Cloudflare / Blocked Pages

11v11 and worldfootball may block command-line scrapers. That is expected.

Use this order:
1. `web_extract([direct_url])`
2. Browser tool against direct URL
3. Retry with worldfootball direct URL
4. Use leeds-fans / Mighty Leeds for historical cross-checks
5. Only then use web_search for a very specific query, e.g. `site:11v11.com/teams/leeds-united/tab/matches/season/2010 Leeds United match record 2010`

Preferred fallback order: if direct web access fails, then use the local Firecrawl scrape endpoint at `http://127.0.0.1:3002` with `POST /v0/scrape`, URL target, `formats=["markdown"]`, and `onlyMainContent=true`. Use only the returned `data.markdown`/`data.content` field and write that markdown directly to `~/leeds-results/raw/11v11/<ending_year>.md`. Do not store the full response envelope.

Do not burn time changing user agents in curl if the page returns Cloudflare `Just a moment...`.

### Exact URL Cheatsheet

```text
# Historical index
https://www.leeds-fans.org.uk/leeds/history/Results.html

# First Leeds United season
https://www.leeds-fans.org.uk/leeds/history/1.html

# 11v11 season pages, ending-year pattern
https://www.11v11.com/teams/leeds-united/tab/matches/season/1921/
https://www.11v11.com/teams/leeds-united/tab/matches/season/2026/

# worldfootball season pages, ending-year pattern
https://www.worldfootball.net/teams/leeds-united/1921/3/
https://www.worldfootball.net/teams/leeds-united/2026/3/

# Mighty Leeds early season example
http://www.mightyleeds.co.uk/seasons/192021.htm
```

### Common Pitfalls

1. **Starting with broad web search.** It is slower and worse. Use the direct URLs above.
2. **Treating score as home-team score.** Some sources list result from Leeds perspective. Parse venue before assigning home/away goals.
3. **Dropping 1919-20.** The first season page is `1.html` and may not appear as a normal linked season in the index.
4. **Ignoring wartime seasons.** Keep them, but mark competition/season notes honestly.
5. **Mixing source schemas.** Always normalize into one schema and keep `source_url` per row.
6. **Pretending modern data is done without checking.** leeds-fans stops in 2008-09. Continue via 11v11/worldfootball.
7. **11v11 date parsing.** 11v11 markdown uses **abbreviated month names** (`08 Aug 2009`). Map `Jan`->`January` etc. before parsing; do not assume `%B` full-month input.
8. **Player/cup/Europe misclassification.** The raw leeds-fans CSV leaves `competition` blank for many older cup and European ties and embeds the competition hint in `opponent` or `notes` (`FACR3`, `CL2-4`, `LCR3`, `UCR2-1`). If these are left blank the generator defaults to "league". When summing player goals by competition, classify from `competition` + `opponent` + `notes`, not venue alone.
9. **Wikipedia as a gap-filler, not an oracle.** If a leeds-fans season page has been legally redacted or is otherwise partial (e.g. `2007-08`), Wikipedia tables can fill league-match rows, but Wikipedia is not a reliable primary source in general. Use it only when the established pipeline is confirmed incomplete for a specific season, and keep `source_name` as the actual source used.

#### Known teammate/goal audit helper

For per-player goal audits, prefer the dedicated helper over ad hoc counting:

```bash
python scripts/verify_viduka_by_competition.py --player "Viduka"
python scripts/verify_viduka_by_competition.py --player "Viduka" --from-season 2000-01 --to-season 2003-04
```

It classifies matches as League, FA Cup, League Cup, Europe, or Friendly and prints appearances with goals by competition.

## §10 Leeds United Transfer Research

Use when collecting Leeds United player transfers in and out of the club, including transfer dates, fees, wages, contract length, loans, released/free transfers, and source confidence.

Source of truth for transfer research (moved from the standalone `leeds-united-transfers-research` skill). Archived copies contain the original full playbook.

### Target deliverable

Every player movement in and out of Leeds United from club formation to present, with clearly separated hard facts and estimates.

Recommended folders:

```text
~/leeds-transfers/
  raw/                         # saved HTML/markdown/PDF/source snippets
  leeds_transfers_raw.csv
  leeds_transfers_clean.csv
  leeds_transfer_contracts.csv
  leeds_transfer_wages.csv
  source_audit.md
```

### Required Output Schema

Use this as the main transfer CSV header:

```csv
season,window,date,player,position,direction,from_club,to_club,transfer_type,fee_reported,fee_currency,fee_gbp_estimate,wage_reported,wage_period,wage_gbp_weekly_estimate,contract_start,contract_end,contract_length_text,loan_start,loan_end,is_loan,is_permanent,is_released,is_free_transfer,is_undisclosed,is_youth,is_academy,source_name,source_url,source_date,confidence,notes
```

Definitions:
- `direction`: `in`, `out`, or `internal`.
- `transfer_type`: one of `permanent`, `loan`, `loan_return`, `free`, `released`, `retired`, `academy`, `undisclosed`, `trial`, `unknown`.
- `fee_reported`: exact text from source, e.g. `€17.80m`, `undisclosed`, `free transfer`.
- `fee_gbp_estimate`: numeric GBP if you can reasonably convert/estimate; otherwise blank.
- `wage_reported`: exact text from source, e.g. `£40,000 per week`.
- `wage_gbp_weekly_estimate`: numeric weekly GBP where available.
- `contract_length_text`: exact text, e.g. `four-year deal`, `until June 2028`.
- `confidence`: `high`, `medium`, `low`.

Never overwrite exact source text with your estimate. Keep both.

### Source Priority

#### 1) Transfermarkt — primary season-by-season transfer ledger

Club ID for Leeds United is `399`.

Direct URL pattern:

```text
https://www.transfermarkt.co.uk/leeds-united/transfers/verein/399/saison_id/2025
https://www.transfermarkt.com/leeds-united/transfers/verein/399/saison_id/2025
```

`season_id` is the season starting year:
- `2025` = 2025-26
- `2024` = 2024-25
- `1992` = 1992-93

Use UK or .com host; if one blocks, try the other. Transfermarkt commonly blocks shell scrapers, so use browser or `web_extract` first. If shell returns 403, do not waste time rotating user agents.

Typical fields available:
- player
- age / nationality / position
- from club / to club
- transfer date or window
- fee text
- incoming and outgoing sections

Limitations:
- Historical pre-1990 data may be incomplete.
- Some fees are `?`, `-`, `free transfer`, `loan`, or `End of loan`.
- Contract length and wages are usually not included.

#### 2) Official Leeds United news — contract length and confirmation

Use official site searches and direct news pages to confirm:
- signing date
- contract wording
- whether fee is undisclosed
- loan duration
- released/retained status

Useful query patterns when web search works:

```text
site:leedsunited.com/news/team-news "Leeds United" "signs" "year deal"
site:leedsunited.com/news/team-news "Leeds United" "contract" "until"
site:leedsunited.com/news/team-news "retained list" "Leeds United"
site:leedsunited.com/news/team-news "released" "Leeds United"
```

If search is failing, go direct via browser/search on the Leeds site and save snippets into `raw/official/`.

#### 3) Premier League / EFL registration and retained lists

Use for official released/retained confirmation:

```text
https://www.premierleague.com/news
https://www.efl.com/news
```

Search patterns:

```text
site:premierleague.com/news "Leeds United" "retained list"
site:efl.com/news "Leeds United" "retained list"
```

#### 4) Capology / Spotrac / SalarySport — wages and contract estimates

Wage data is usually estimated. Mark confidence accordingly.

Common sources:

```text
https://www.capology.com/club/leeds-united/salaries/
https://www.spotrac.com/epl/leeds-united-fc/payroll/
https://salarysport.com/football/premier-league/leeds-united-fc/
```

Rules:
- Wages are `medium` confidence when current and matched across two salary sites.
- Wages are `low` confidence if only from one unofficial salary site.
- Put exact wage text in `wage_reported` and numeric weekly GBP in `wage_gbp_weekly_estimate`.
- Do not pretend wages are official unless the club/player/league documents say so.

#### 5) Wikipedia season pages — quick cross-check, not primary

Useful page pattern:

```text
https://en.wikipedia.org/wiki/2025%E2%80%9326_Leeds_United_F.C._season
https://en.wikipedia.org/wiki/2024%E2%80%9325_Leeds_United_F.C._season
```

Often includes `Transfers in`, `Transfers out`, `Loans in`, `Loans out`, `Released` tables with dates and fees.

Use Wikipedia to fill gaps and find references, but prefer original linked sources where possible.

#### 6) leeds-fans / Mighty Leeds / official history — older historical movements

For pre-modern eras, fee/wage data will often be missing. Use these to find player arrivals/departures and annotate gaps honestly:

```text
https://www.leeds-fans.org.uk/leeds/players/
http://www.mightyleeds.co.uk/
```

For older players, use exact source notes like `signed from`, `joined`, `sold to`, `released`, but leave fee/wage blank if no reliable source.

### Standard Workflow

#### Step 1 — Create folder and URL lists

```bash
mkdir -p ~/leeds-transfers/raw ~/leeds-transfers/reports
```

Generate transfer season URLs — old helper script path preserved under `references/generate-leeds-transfer-urls-readme.md`:
- Former path: `scripts/generate_leeds_transfer_urls.py`
- Use direct Transfermarkt URL generation if the script is unavailable.

#### Step 2 — Scrape Transfermarkt by direct season URL

For each season, try:

```text
https://www.transfermarkt.co.uk/leeds-united/transfers/verein/399/saison_id/YYYY
```

Use browser or `web_extract` if shell gets blocked.

Normalize sections:
- `Arrivals` -> `direction=in`, `to_club=Leeds United`.
- `Departures` -> `direction=out`, `from_club=Leeds United`.
- `End of loan` returning to Leeds can be `direction=in`, `transfer_type=loan_return`.
- Player going back after Leeds loan spell can be `direction=out`, `transfer_type=loan_return`.

#### Step 3 — Add official confirmation fields

For each modern row, try to find one official or near-official source:
- Leeds United announcement
- buying/selling club announcement
- Premier League/EFL retained list
- Companies/league filing where relevant

Capture:
- official date
- contract length text
- `undisclosed fee` wording
- loan duration
- released/retained status

#### Step 4 — Add wages separately

Do not mix wage estimates into the main row without provenance. Create `leeds_transfer_wages.csv` too:

```csv
player,season,club,wage_reported,wage_period,wage_gbp_weekly_estimate,source_name,source_url,confidence,notes
```

Join later by player and season if needed.

#### Step 5 — Normalize fee text

Examples:

| Source text | transfer_type | is_free_transfer | is_undisclosed | notes |
|---|---|---:|---:|---|
| `€17.80m` | permanent | false | false | convert if needed |
| `£5.00m` | permanent | false | false | exact GBP |
| `free transfer` | free | true | false | no fee |
| `loan transfer` / `Loan` | loan | false | false | set loan fields if known |
| `End of loan` | loan_return | false | false | returning club direction matters |
| `undisclosed` | undisclosed | false | true | do not invent fee |
| `released` | released | true | false | outgoing only |
| `?` | unknown | false | false | missing, low confidence |

#### Step 6 — Confidence rules

Use these consistently:
- `high`: official club/league source, or multiple reputable sources agree on exact fact.
- `medium`: Transfermarkt/Wikipedia/reputable media agree but official wording missing.
- `low`: salary sites, rumoured fees, single-source claims, forum/archive notes.

For record-keeping, every row must include `source_name` and `source_url`.

### Wages and Contract Length: Important Rules

Wages and contract lengths are not equal to transfer facts.
- Club signing announcements often confirm contract length but not wages.
- Wage websites estimate salaries; label them as estimates.
- Media fee reports may be initial fee, total package, add-ons, or foreign currency.
- If sources disagree, keep one main row and put disagreement in `notes`, e.g. `fee reports vary: £10m initial / £15m incl add-ons`.
- Do not average rumours unless Paul explicitly asks for a modelled estimate.

### Output Quality Bar

Before reporting completion, run checks:

```python
import csv, collections
path = '~/leeds-transfers/leeds_transfers_clean.csv'
rows = list(csv.DictReader(open(path)))
print('rows', len(rows))
print('directions', collections.Counter(r['direction'] for r in rows))
print('types', collections.Counter(r['transfer_type'] for r in rows).most_common())
print('missing source_url', sum(not r['source_url'] for r in rows))
print('missing player', sum(not r['player'] for r in rows))
print('missing date', sum(not r['date'] for r in rows))
```

Also create `source_audit.md`:

```markdown
# Leeds United Transfers Source Audit

- Primary transfer ledger: Transfermarkt club 399, season IDs YYYY-YYYY, accessed DATE.
- Official confirmations: Leeds United / buying-selling club / PL / EFL pages.
- Wage sources: Capology / Spotrac / SalarySport, treated as estimates.
- Known gaps:
  - pre-1990 fees incomplete
  - wage data mostly unavailable historically
  - contract length missing where announcement not found
```

### Transfer shortcuts, pitfalls, and verification checklist

#### Pitfalls

1. **Broad web search first.** Don't. Generate direct season URLs.
2. **Treating undisclosed as zero.** Wrong. `undisclosed` is not free.
3. **Treating wages as official.** Most wage sites are estimates.
4. **Mixing loan returns with paid transfers.** Use `loan_return` and note direction carefully.
5. **Dropping released players.** Retained lists and official end-of-season pages matter.
6. **Overwriting exact source values.** Keep exact text and estimates in separate columns.
7. **Assuming Transfermarkt covers 1919-present perfectly.** It doesn't. Use historical sources and mark gaps.
8. **Not saving source URLs.** Without provenance the dataset is not trustworthy.

#### Verification Checklist

- [ ] `transfer_source_urls.csv` generated.
- [ ] Transfermarkt direct URLs attempted season-by-season.
- [ ] Official confirmations attempted for modern transfers.
- [ ] Released/free/loan/loan-return rows classified separately.
- [ ] Wage estimates kept separate from official facts.
- [ ] Contract lengths stored as exact text plus dates where possible.
- [ ] Every row has `source_name`, `source_url`, and `confidence`.
- [ ] Missing player/date/source checks run.
- [ ] `source_audit.md` created with gaps and caveats.