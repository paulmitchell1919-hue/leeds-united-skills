---
name: leeds-united-player-biographies
description: "Use when researching and writing comprehensive Leeds United player biographies. Covers the full 12-section template: personal details, complete career history, competitive vs friendly stats separation, international career, honours, post-retirement, and death details."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [leeds-united, player-biographies, football, research, template]
    related_skills: [leeds-united-results-scraping, leeds-united-transfers-research]
---

# Leeds United Player Biographies

## Overview

This skill produces exhaustive, gold-standard player biographies for the Leeds United player archive project. Every player who has ever played for Leeds United (first team, competitive fixture) gets a biography file.

The goal is MAXIMUM detail: not just their Leeds career, but their complete playing career across every club, their personal background, international career, what they did after football, and if they've died, when and how.

Two gold-standard reference files exist at the output path below. ALWAYS read at least one of them before starting a new bio to match the exact structure, depth, and conventions.

## When to Use

- Writing a Leeds United player biography from scratch
- Expanding or updating an existing player bio
- Training a new researcher (e.g. Bill) on the expected format and conventions

**Don't use for:** Match reports, season reviews, or non-player content.

## Data Architecture (Two Layers)

This project has TWO data layers. Both must be maintained per player:

1. **CONTENT LAYER — Markdown files** (this skill's main focus)
   - Human-readable narrative bios at `/Volumes/projects-1/leeds/research/leeds_players/`
   - Used for: "On This Day" social posts (Facebook/X), eventual website articles, human reading
   - The 12-section template below governs these files

2. **QUERY LAYER — Supabase (PostgreSQL)**
   - Cloud-hosted structured database for reliable cross-player queries
   - Used for: "How many players featured in 1947?", "How many goals did Fowler score for Leeds?", season-by-season lookups
   - Credentials in `/Volumes/projects-1/leeds/.env` (see Supabase Setup below)
   - Schema: TBD — will be designed and added as a reference file before Bill starts entering structured data
   - When the schema exists, each player bio requires BOTH the markdown file AND a Supabase data entry

Markdown alone cannot reliably answer cross-player queries (e.g. "who played in season X"). The Supabase layer exists for exactly that. Do not try to query the markdown files for structured stats — query the database.

## Supabase Setup

Credentials live in `/Volumes/projects-1/leeds/.env` (gitignored). Variables:
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (REST API access)
- `SUPABASE_DB_HOST`, `SUPABASE_DB_PORT`, `SUPABASE_DB_NAME`, `SUPABASE_DB_USER`, `SUPABASE_DB_PASSWORD` (direct PostgreSQL access)

Free tier (500MB, no card needed) — fits the project scale easily.

See [references/supabase-data-layer.md](references/supabase-data-layer.md) for setup details, schema design considerations, and the decision rationale.

## Published Location

This skill is published to GitHub (private): `Mitch-TechWorks-Skills/Leeds-United-Skills`
- Install: `npx skills add https://github.com/Mitch-TechWorks-Skills/Leeds-United-Skills --skill leeds-united-player-biographies`
- Pack source on NAS: `/Volumes/projects-1/skills/Leeds-United-Skills/`
- Local runtime copy: `~/.hermes/skills/research/leeds-united-player-biographies/`

## Output Location (Content Layer)

All player bio markdown files are saved to:

```
/Volumes/projects-1/leeds/research/leeds_players/
```

This is on the NAS and visible in Finder. DO NOT save anywhere else.

### File Naming Convention

```
firstname_surname.md
```

- All lowercase
- Underscore between first name and surname
- No spaces, no hyphens
- For players with multiple surnames, use the most commonly known form: `billy_bremner.md`, `john_charles.md`, `ethan_ampadu.md`
- For players known by a single name or nickname, use their full real name: `david_ockham.md` not `rocky.md`

## Gold-Standard Reference Files

Before starting any new bio, read one of these to match structure and depth:

1. `/Volumes/projects-1/leeds/research/leeds_players/ethan_ampadu.md` — modern player example (still active)
2. `/Volumes/projects-1/leeds/research/leeds_players/john_charles.md` — historical player example (deceased, extensive career, post-retirement)

## Required Template Structure (12 Sections)

Every bio MUST follow this structure. Do not skip or merge sections. Use `---` horizontal rules between major sections for visual separation.

### Template Header

Start every file with the player's name as H1, followed by the template note (only needed if this is the first in a batch — remove for regular bios):

```markdown
# Player Name

---

## Photos

![Descriptive alt text](image_url)
*Caption with source attribution.*

(Up to 3 photos — see Photo Convention below)

---
```

### Sections

1. **Full Name** — Complete full legal name. Include middle names if known.

2. **Date of Birth** — Exact date. Include "(age X as of Month Year)" if still living, or cross-reference to Death section if deceased.

3. **Place of Birth** — City, region/province/state, country. Include specific address if documented (e.g. John Charles: "19 Alice Street, Cwmbwrla, Swansea").

4. **Parents' Names and Nationalities** — Mother AND father, with:
   - Full names
   - Nationalities / heritage
   - Occupions / notable details
   - Lifespans if deceased
   - Table format preferred
   
   IMPORTANT: If a parent's name is genuinely undocumented in reliable public sources, state this explicitly. Do NOT guess, invent, or use unreliable blog sources. Write: "Name not publicly documented" and explain what IS known (e.g. nationality, that they were private). This is the correct convention — honest gaps over fabricated data.

5. **Full Playing Career** — Complete career timeline including:
   - Youth/academy career
   - Every senior club (permanent and loan)
   - Clearly mark loans as **Loan**
   - Player-manager or managerial roles at clubs after retiring as a player
   - Table format: Years | Club | Country | Status (permanent/loan/youth)
   - Detailed narrative paragraph(s) for each club/stint with context, key moments, transfers

6. **Appearance Statistics** — THE MOST CRITICAL SECTION. Must separate competitive from friendly:
   
   **6a. Competitive Appearances** (counted in career totals):
   - League, domestic cups (FA Cup, EFL Cup, EFL Trophy, Copa del Rey, Coppa Italia, etc.)
   - European competitions (Champions League, Europa League, Inter-Cities Fairs Cup, Cup Winners' Cup)
   - Play-offs and relegation play-offs
   - International club competitions (Super Cup, Club World Cup)
   - Table: Club | Seasons | League (apps/goals) | Domestic cups | Europe/play-offs | Total (apps/goals)
   - Include career total row
   
   **6b. Friendly / Non-Competitive Appearances** (ISOLATED — never mixed into competitive totals):
   - Pre-season friendlies
   - Testimonials
   - Exhibition matches
   - Benefit matches
   - Representative matches (e.g. Great Britain XI, League XIs)
   - Table: Date/period | Fixture type | Club at time | Notes
   - If no friendly records exist, state this explicitly: "No comprehensive friendly records documented"
   
   Include a methodology note blockquote at the top of section 6 explaining the convention, for template users.

7. **International Career** — Youth and senior:
   - Youth levels with cap counts
   - Senior debut (date, opponent, match details)
   - Tournaments (World Cup, European Championship, etc.)
   - Notable milestones (50th cap, 100th cap, records)
   - Caps and goals total
   - Table for tournament summary

8. **Playing Style and Position** — Positions, attributes, tactical role, notable quotes about their ability.

9. **Honours and Trophies** — Club honours, individual honours, records/notable firsts. Separate subsections for each.

10. **Post-Playing Career** — What they did after retiring from playing:
    - Management/coaching career
    - Business ventures
    - Media/punditry
    - Other activities
    - If still active: state "Not applicable — still an active professional" and note current contract status
    - Include failures and setbacks honestly (e.g. John Charles's tax/business troubles)

11. **Personal Life** — Family, education, off-pitch details, community work, notable life events. Keep it factual and well-sourced.

12. **Death** (if applicable) — For deceased players:
    - Exact date of death
    - Location (hospital, city)
    - Cause of death / circumstances
    - Timeline of final illness if relevant
    - Legacy and tributes
    
    If the player is still alive, omit this section entirely.

### Sources Section

End every bio with a `## Sources` section listing all URLs consulted, with brief descriptions. This is non-negotiable — it's how the project maintains quality and traceability.

### Closing Line

End with: `*File compiled: [Month Year]. Leeds United player biography project.*`

## Photo Convention

- Maximum 3 photos per player
- Use markdown image syntax with FULL descriptive alt text
- Include a caption beneath each photo with source attribution
- Prefer: Wikimedia Commons (free), official club sites, Wikipedia
- DO NOT download or save images locally — just reference the URL
- If fewer than 3 good photos exist, use what's available. Don't pad with low-quality images.

## Research Conventions

### Data Availability by Era

| Era | Competitive Stats | Friendly Stats |
|-----|-------------------|----------------|
| Pre-1950 | Good (league records, cups) | Very sparse — document what's known |
| 1950s-1980s | Comprehensive | Sparse — note that comprehensive records aren't maintained |
| 1990s-2000s | Comprehensive | Improving — some available |
| 2010s-present | Comprehensive | Most available (Transfermarkt, club sites) |

For pre-1990s players, comprehensive friendly/testimonial records are generally NOT maintained in standard reference databases. Document the famous/notable friendlies that ARE recorded, add a methodology note explaining this, and move on. Do not attempt to reconstruct missing friendly data.

### Source Discrepancies

When sources conflict on statistics (very common for older players):
- Give the most authoritative figure
- Note the discrepancy in parentheses or a footnote
- Example from John Charles: "155 apps / 108 goals (Juventus official Hall of Fame cites 181/105; difference due to Coppa Italia and Fairs Cup inclusion)"
- Document the discrepancy transparently — do NOT silently pick one figure

### Honest Gaps

If information is genuinely unavailable:
- State "Not publicly documented" or "Undocumented in reliable sources"
- Explain what IS known
- NEVER fabricate, guess, or use unreliable sources to fill a gap
- This is more valuable than a complete-looking file with wrong data

### Web Scraping / Browsing Tool

For extracting full page content from source URLs, use the self-hosted **Firecrawl** instance running on the trashcan server:

```
http://192.168.1.70:3002
```

No API key required. Use this instead of hitting external services — it's free and local. Firecrawl converts web pages to clean markdown/text, which is ideal for pulling biography content from news articles, club pages, and reference sites.

When you need to read a specific player page (Wikipedia, Transfermarkt, BBC Sport, etc.), pass the URL through Firecrawl to get the full text rather than just search snippets.

### Preferred Sources (in rough priority order)

1. Wikipedia (starting point, verify against others)
2. Transfermarkt (career stats, transfer fees)
3. Club official sites / Hall of Fame pages
4. National federation sites (FAW, FA, etc.)
5. Dictionary of Welsh Biography (for Welsh players — excellent)
6. BBC Sport, Sky Sports (for modern players)
7. RSSSF (for historical records)
8. 11v11.com (historical match and player data)
9. Contemporary newspaper archives (Guardian, Times, Yorkshire Post)
10. Published biographies/autobiographies

Cross-reference at least 3 sources per player. More for significant players.

## Supabase Database Entry (MANDATORY)

Every player bio MUST also have its structured data entered into the Supabase database. The markdown file is for humans; the database is for querying. Both are required for a bio to be considered complete.

### Connection

Credentials are in: `/Volumes/projects-1/leeds/.env`

Key values:
- `SUPABASE_URL` — REST API endpoint
- `SUPABASE_SERVICE_ROLE_KEY` — full access key (bypasses RLS)

All database interaction is via the Supabase REST API (PostgREST). No direct PostgreSQL connection needed.

### Database Schema (7 Tables)

1. **players** — core identity (one row per player)
   - full_name, first_name, last_name, known_as, date_of_birth, place_of_birth
   - date_of_death, place_of_death, cause_of_death (leave NULL if alive)
   - nationality, position, bio_file (e.g. "ethan_ampadu.md")

2. **player_parents** — one row per parent (mother/father)
   - player_id (FK), name, relationship, nationality, occupation, birth_year, death_year, notes
   - If name unknown: "Name not publicly documented"

3. **clubs** — reference table (one row per club)
   - name (unique), country, city
   - Check if club exists before inserting (GET by name)

4. **player_career** — one row per club stint
   - player_id (FK), club_id (FK), start_year, end_year, status, transfer_fee, notes
   - status values: 'youth', 'senior_permanent', 'loan', 'player_manager', 'manager'

5. **player_stats** — THE KEY TABLE (one row per player/club/season/competition)
   - player_id (FK), club_id (FK), season (e.g. "2023-24"), competition_type, competition_name
   - appearances, goals
   - is_competitive is AUTO-CALCULATED — do not set it manually
   - competition_type values: 'league', 'fa_cup', 'league_cup', 'other_domestic_cup', 'european', 'playoff', 'friendly', 'testimonial', 'other_non_competitive'
   - Friendlies MUST use competition_type 'friendly', 'testimonial', or 'other_non_competitive'

6. **international_career** — one row per player per country per level
   - player_id (FK), country, level, caps, goals, debut_date, debut_opponent, last_cap_date, tournaments
   - level values: 'youth_u16', 'youth_u17', 'youth_u19', 'youth_u21', 'youth_other', 'senior'

7. **player_honours** — one row per trophy/award
   - player_id (FK), honour_name, honour_type, season, club_id (FK), notes
   - honour_type values: 'club', 'individual', 'record'

### Insertion Order (CRITICAL)

You MUST insert in this order due to foreign key dependencies:

1. **clubs** — insert any new clubs first (GET by name to check if they exist)
2. **players** — insert the player, capture the returned player_id
3. **player_parents** — use player_id from step 2
4. **player_career** — use player_id + club_id
5. **player_stats** — use player_id + club_id, one row per season per competition
6. **international_career** — use player_id
7. **player_honours** — use player_id

### REST API Technical Notes

- URL-encode all query params (spaces in club names will break the URL)
- Use `Prefer: return=representation` header to get inserted rows back
- Use service_role key for all writes (anon key is read-only)
- Example GET: `GET /rest/v1/clubs?name=eq.Leeds%20United&select=id`
- Example POST: `POST /rest/v1/players` with JSON body

### Example: Complete Data Entry for One Player

See the Ampadu (player_id=1) and Charles (player_id=2) entries for reference. Every table is populated for both. Query examples that work:

- "Goals scored for Leeds by player X": filter player_stats by player_id + club_id=1 + is_competitive=true, sum goals
- "Who played in season Y": filter player_stats by season + club_id=1 + is_competitive=true, distinct player_ids
- "Player X total career stats": filter player_stats by player_id + is_competitive=true, group by club_id

## MANDATORY 4-PHASE WORKFLOW (follow this EXACT order, every time)

### Phase 1 — SCRAPE (gather source material, nothing else)

You MUST scrape these pages before writing ANYTHING. No exceptions.

**Step 1.1:** Scrape the FULL Wikipedia player page via Firecrawl:
```
POST http://127.0.0.1:3002/v1/scrape
{"url": "https://en.wikipedia.org/wiki/PLAYER_NAME", "formats": ["markdown"], "onlyMainContent": true}
```

**Step 1.2:** Scrape the Transfermarkt career stats page:
```
POST http://127.0.0.1:3002/v1/scrape
{"url": "https://www.transfermarkt.com/PLAYER_SLUG/leistungsdaten/spieler/ID", "formats": ["markdown"], "onlyMainContent": true}
```
This is your GROUND TRUTH for clubs and stats. If a club is not in the Transfermarkt career table, it does not go in the bio.

**Step 1.3:** Scrape at least 1 more source (pick the most relevant):
- Club Hall of Fame page
- BBC Sport profile
- RSSSF archive page
- National federation page

**Step 1.4:** Write a structured fact sheet to a temp file. For EACH field, note the source URL:
```
FULL_NAME: [value] — source: [URL]
DATE_OF_BIRTH: [value] — source: [URL]
PLACE_OF_BIRTH: [value] — source: [URL]
FATHER_NAME: [value or UNKNOWN] — source: [URL or "not in any scraped source"]
MOTHER_NAME: [value or UNKNOWN] — source: [URL or "not in any scraped source"]
IS_DEAD: [yes/no] — source: [URL]
DATE_OF_DEATH: [value or N/A] — source: [URL or "not documented"]
CLUBS: [list from Transfermarkt ONLY] — source: [Transfermarkt URL]
...
```

If a field is not in any scraped source, write UNKNOWN. Do not search further. Do not infer. UNKNOWN is the correct answer.

### Phase 2 — WRITE (from the fact sheet ONLY)

Write the markdown bio using ONLY facts from your Phase 1 fact sheet. For every sentence you write, you must be able to point to the fact sheet entry and its source URL.

**Decision trees for hallucination-prone fields:**

**Parents (Section 4):**
```
Does the Wikipedia infobox contain a "Parent(s)" or "Father"/"Mother" field?
├─ YES → Copy the names exactly as shown
└─ NO → Write "Unknown" for both parents. Do not search elsewhere. Do not infer names from the player's surname.
         "Unknown" is the correct and complete answer.
```

**Death (Section 12):**
```
Does the Wikipedia infobox contain a "Died" field?
├─ YES → Use that date. Write Section 12.
└─ NO → The player is alive. OMIT Section 12 entirely. Set date_of_death=null in DB.
         Do NOT assume death based on age. Old ≠ dead.
```

**Clubs (Section 5):**
```
For each club you plan to list:
  Does this club appear in the Transfermarkt career table you scraped?
├─ YES → Include it
└─ NO → Do NOT include it. Even if it "feels right." Even if Wikipedia mentions it in passing.
         Transfermarkt career table is ground truth.
```

**Stats (Section 6a):**
```
Transfermarkt career table shows apps/goals per competition.
  Copy these EXACTLY. Do not round, adjust, or "reconcile" with Wikipedia.
  If Transfermarkt and Wikipedia disagree, use Transfermarkt and note the discrepancy.
```

**Honours (Section 9):**
```
For each honour you plan to list:
  Can you point to the specific source URL where you read about this honour?
├─ YES → Include it
└─ NO → Do NOT include it. Invented honours are a documented hallucination pattern.
```

**Tournament results (Section 7):**
```
For each tournament result:
  Did you verify the result (winner/loser/score) against the actual tournament page?
├─ YES → Include it
└─ NO → Do NOT guess. Getting a result backwards is a critical error.
```

### Phase 3 — DB INSERT (structured data)

Insert into Supabase using the helper script. Follow the insertion order in the schema section above.

**Before EACH POST, do a GET first:**
```bash
# Check if player already exists BEFORE creating
python3 /mnt/nas/leeds/research/supabase_helper.py get players "last_name=eq.SURNAME"
# If results exist, use the existing player_id. Do NOT create a duplicate.

# Check if a career row already exists BEFORE inserting
python3 /mnt/nas/leeds/research/supabase_helper.py check_dup player_career "player_id=eq.7&club_id=eq.1"
```

**DB-specific rules (these are SCHEMA CONSTRAINTS, not preferences):**
- `player_stats.is_competitive` is GENERATED — do NOT include it in POST payloads
- `player_honours.honour_type` only accepts `'club'` or `'individual'` — NOT `'international'`
- `player_career.status` only accepts `'youth'`, `'senior_permanent'`, or `'manager'` — NOT `'senior'`
- Parents ALWAYS get inserted — name="Unknown" if not documented

### Phase 4 — VALIDATE (mandatory final gate)

```bash
python3 /mnt/nas/leeds/research/validate_bio.py --player-id <ID> --md-file /mnt/nas/leeds/research/leeds_players/<file>.md
```

If exit code is NOT 0:
1. Read the errors printed
2. Fix every single one
3. Re-run the validator
4. Repeat until exit 0

**You CANNOT report "complete" until this returns exit 0.**

## Core Principle

**"Unknown" is better than wrong.** Paul has zero tolerance for fabricated data. A bio with gaps marked "Not publicly documented" is a good bio. A bio with plausible-sounding invented details is a failure. When in doubt, write "Unknown."

## Common Pitfalls (observed hallucination patterns)

| Pattern | Example | Prevention |
|---|---|---|
| Fabricated parent names | "Johannes Radebe", "Emily Radebe" | If not in Wikipedia infobox → "Unknown" |
| Fabricated death date | Eddie Gray given 2024-11-17 death date | If no Wikipedia "Died" field → alive |
| Invented club stint | Radebe at Bolton Wanderers | Transfermarkt career table = ground truth |
| Reversed tournament result | "South Africa were 1996 AFCON runners-up" | Verify against tournament page |
| Fabricated physical honour | "statue at Elland Road" | Each honour needs a source URL |
| Duplicate player records | Eddie Gray had 3 DB rows | GET by last_name BEFORE creating |
| Wrong honour_type | `'international'` (violates constraint) | Only `'club'` or `'individual'` |
| Including is_competitive | Triggers 428C9 error | Omit from POST — it's generated |
| "Gold standard" template note | Propagates across bios | Every bio just follows the standard template |

## Verification Checklist

Before marking a bio complete:

**Phase 1 (Scrape):**
- [ ] Wikipedia full page scraped (URL saved)
- [ ] Transfermarkt career stats page scraped (URL saved)
- [ ] At least 1 additional source scraped
- [ ] Fact sheet written with source URL per field

**Phase 2 (Write):**
- [ ] Every fact in the markdown traces to a Phase 1 source
- [ ] Parents are "Unknown" if not in sources (NOT invented)
- [ ] Death section omitted if player is alive (NOT fabricated)
- [ ] Clubs match Transfermarkt career table exactly
- [ ] Competitive/friendly stats separated (6a/6b)
- [ ] All 12 sections present (omit Death if alive)
- [ ] Max 3 photos with source captions
- [ ] Sources section with full URLs

**Phase 3 (DB):**
- [ ] Checked for existing player BEFORE creating (GET by last_name)
- [ ] Player row inserted (player_id captured)
- [ ] Parents inserted (Unknown if not documented)
- [ ] Career entries for EVERY club (from Transfermarkt)
- [ ] Stats inserted (is_competitive OMITTED from payload)
- [ ] Honours inserted (honour_type is 'club' or 'individual' ONLY)
- [ ] No duplicate rows anywhere (ran check_dup before each POST)

**Phase 4 (Validate):**
- [ ] **`validate_bio.py` returns exit 0 — NOT OPTIONAL**
