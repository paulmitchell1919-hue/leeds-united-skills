# Supabase Data Layer — Leeds United Player Database

## Overview

The Supabase layer is the **query layer** for the Leeds United player biography project. The markdown files are the **content layer** (human-readable). Both must be maintained per player.

## Connection

Credentials: `/mnt/nas/leeds/.env` (Linux) or `/Volumes/projects-1/leeds/.env` (macOS)

Key variables:
- `SUPABASE_URL` — REST API endpoint (normalize to end with `/rest/v1`)
- `SUPABASE_SERVICE_ROLE_KEY` — full access key (bypasses RLS). Use this for ALL writes.
- `SUPABASE_ANON_KEY` — read-only key

## Schema (7 Tables)

| Table | Purpose | FK Dependencies |
|-------|---------|-----------------|
| `players` | Core identity (1 row per player) | — |
| `player_parents` | Mother/father details | players.id |
| `clubs` | Reference table (1 row per club) | — |
| `player_career` | Club stints | players.id, clubs.id |
| `player_stats` | Stats per season per competition | players.id, clubs.id |
| `international_career` | International caps | players.id |
| `player_honours` | Trophies/awards | players.id, clubs.id (optional) |

## Insertion Order (CRITICAL — FK dependencies)

1. `clubs` — insert new clubs first (GET by name to check existing)
2. `players` — insert player, capture returned `id`
3. `player_parents` — use player_id
4. `player_career` — use player_id + club_id
5. `player_stats` — use player_id + club_id, one row per season per competition
6. `international_career` — use player_id
7. `player_honours` — use player_id

## Anti-Duplicate Pattern (GET BEFORE POST)

**This is the #1 source of Supabase errors.** Always check before inserting.

> **IMPORTANT:** When running inside an agent terminal (Hermes/billresearch), JWT keys get truncated in terminal display, causing 401 errors on raw curl. Use the helper script instead: `python3 /mnt/nas/leeds/research/supabase_helper.py check_dup <table> "<filter>"` (exit 0 = safe, exit 1 = exists). See `scripts/supabase_helper.py` for full CRUD commands.

### Preferred: helper script check_dup

```bash
# Check if career row exists (exit 0 = safe, exit 1 = already exists)
python3 /mnt/nas/leeds/research/supabase_helper.py check_dup player_career "player_id=eq.3&club_id=eq.16&start_year=eq.1989"

# Check if stats row exists
python3 /mnt/nas/leeds/research/supabase_helper.py check_dup player_stats "player_id=eq.3&club_id=eq.1&season=eq.1986-87&competition_type=eq.league"

# Check if international row exists
python3 /mnt/nas/leeds/research/supabase_helper.py check_dup international_career "player_id=eq.3&country=eq.Republic%20of%20Ireland&level=eq.senior"
```

### Fallback: raw curl (only outside agent terminals — keys truncate inline)

```bash
# Check if club exists
curl -s "$URL/rest/v1/clubs?name=eq.Leeds%20United&select=id" \
  -H "apikey: $KEY" -H "Authorization: Bearer *** 

# Check if career row exists
curl -s "$URL/rest/v1/player_career?player_id=eq.3&club_id=eq.16&start_year=eq.1989&select=id" \
  -H "apikey: $KEY" -H "Authorization: Bearer *** 

# Check if stats row exists
curl -s "$URL/rest/v1/player_stats?player_id=eq.3&club_id=eq.1&season=eq.1986-87&competition_type=eq.league&select=id" \
  -H "apikey: $KEY" -H "Authorization: Bearer *** 

# Check if international row exists
curl -s "$URL/rest/v1/international_career?player_id=eq.3&country=eq.Republic%20of%20Ireland&level=eq.senior&select=id" \
  -H "apikey: $KEY" -H "Authorization: Bearer *** 
```

If the GET returns data, the row already exists — do NOT POST again.

## Common REST API Patterns

### Insert with return=representation
```bash
curl -s -X POST "$URL/rest/v1/players" \
  -H "apikey: $KEY" \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d '{"full_name": "John Sheridan", "first_name": "John", ...}'
```

### Delete a duplicate row
```bash
curl -s -X DELETE "$URL/rest/v1/player_career?id=eq.123" \
  -H "apikey: $KEY" \
  -H "Authorization: Bearer *** 
```

### URL-encode query values
Spaces and special characters in query params MUST be URL-encoded:
- `"Leeds United"` → `Leeds%20United`
- `"Republic of Ireland"` → `Republic%20of%20Ireland`

## competition_type Values

| Value | is_competitive (auto) | Use for |
|-------|-----------------------|---------|
| `league` | true | League appearances |
| `fa_cup` | true | FA Cup |
| `league_cup` | true | EFL/League Cup |
| `other_domestic_cup` | true | Full Members' Cup, EFL Trophy, etc. |
| `european` | true | Champions League, UEFA Cup, Cup Winners' Cup |
| `playoff` | true | Play-offs, relegation play-offs |
| `friendly` | **false** | Pre-season, exhibition |
| `testimonial` | **false** | Testimonial matches |
| `other_non_competitive` | **false** | Charity matches, benefit matches |

**The `is_competitive` field is AUTO-CALCULATED from `competition_type`.** Never set it manually.

## Verification

After entering a player, run the verification script:

```bash
python3 ~/.hermes/skills/research/leeds-united-knowledge-base/scripts/verify_player_supabase.py --player-id 3
```

This checks: duplicate rows across all tables, parents present, stats reconciliation, friendly stats present.

For ad-hoc queries during data entry, use the CRUD helper:

```bash
# Quick count of rows per table for a player
python3 /mnt/nas/leeds/research/supabase_helper.py count player_stats player_id=eq.3

# Get all career rows to inspect
python3 /mnt/nas/leeds/research/supabase_helper.py get player_career player_id=eq.3
```

## Known Issues from First Runs

### John Sheridan (player_id=3) — Issues Found & Fixed

1. **Duplicate career rows**: Birmingham City loan entered twice (agent retried POST without checking)
2. **Duplicate international rows**: Republic of Ireland senior entered twice
3. **Missing parents**: 0 rows in player_parents (agent skipped because names unknown)
4. **Stats inflation**: DB total (853 apps) didn't match markdown (~622 apps)
5. **Missing friendly stats**: Section 6b content not entered into DB

**Root cause**: Agent did not GET-before-POST on retries, and skipped mandatory tables when data was sparse.

**Fix**: Anti-duplicate rules + mandatory parent insertion + stats reconciliation added to skill. Verification script created to catch all of these automatically.
