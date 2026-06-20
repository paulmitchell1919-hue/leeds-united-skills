# Supabase Schema Details (Leeds Player DB)

Date: 2026-06-20
Discovered during: Eddie Gray / Lucas Radebe manual fixes

## Generated Columns

| Table | Column | Type | Notes |
|---|---|---|---|
| `player_stats` | `is_competitive` | boolean | GENERATED ALWAYS. Computed from `competition_type` — do NOT include in POST payload. |

## Check Constraints

| Table | Constraint | Allowed Values |
|---|---|---|
| `player_career` | `player_career_status_check` | `youth`, `senior_permanent`, `manager` |
| `player_honours` | `player_honours_honour_type_check` | `club`, `individual` (NOT `international`) |

## Honour Type Rule

- International/national-team honours (AFCON medals, British Home Championship, World Cup participation) must be stored with `honour_type='club'` and `club_id=null`.
- The `notes` field records the national team context.
- Attempting `honour_type='international'` triggers `code: 23514` violation.

## DB Auth

- Service role key is in `.env` file at `/mnt/nas/leeds/.env`
- The `supabase_helper.py` script handles auth internally — never inline keys in curl.
- JWT is 200+ chars and gets truncated in terminal display.

## Duplicate Player Records

- Always `GET` by `last_name` before creating a new player.
- If multiple rows exist for the same person, consolidate: delete extras + all children, keep one canonical record, then re-insert children with the correct player_id.

## Parent Names Policy

- Parent names MUST come from scraped sources.
- If a source does not document a parent's name, insert `name="Unknown"` with `notes="Not publicly documented"`.
- Never fabricate plausible-sounding parent names from internal knowledge.