# Leeds KB Population Lessons

## `populate_kb.py` re-run policy
- Run `populate_kb.py` only after changes to `leeds-results/leeds_results_clean.csv`, to add new entity types dependent on season aggregations, or after edits that break per-season object derivations.
- It replays the full entity graph every run; full source entities therefore overwrite hand-written facts. Hand-written people/events should be preserved separately.

## Auto-generated placeholder link behavior
- `build_awards_for_season` infers a top scorer from scorer mention counts in match data. This is structural placeholder scaffolding; strip before runtime/publishing.
- `club_captain` auto-derived `captain_hold` from first scorer in a season is another placeholder and should be replaced by researched captain histories under `captains/`.

## `squad_registration` is match-derived draft
- Per-season `squad_registration` is populated from `home_team`/`away_team` columns and contains opponent seeds rather than player instances. Treat it as regenerable draft only.
- Authoritative squad/registration data should come from tracked documents or per-season transfer research, not auto-generation from fixtures.

## People slug normalization
- Slugs should be stable, pronouncable, and human-readable. Normalize by stripping tags such as `(pen)`, round tags like `(LCR2-1)`/`(ZDSR2)`, then `re.sub(r'[^a-z0-9]','-',name.lower())`.
- Keep `display_name` for presentation. Auto-generated scorer placeholders frequently need cleaning before committing to `people/`.
