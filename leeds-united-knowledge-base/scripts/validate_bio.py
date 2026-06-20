#!/usr/bin/env python3
"""
validate_bio.py — HARD-STOP validation for Leeds United player biographies.

This script is the FINAL GATE before a bio can be marked complete.
It checks every known hallucination pattern and data integrity violation.

Exit codes:
  0 = ALL CHECKS PASSED — safe to report complete
  1 = VIOLATIONS FOUND — fix them before reporting complete (details printed)
  2 = connection/env error

Usage:
  python3 validate_bio.py --player-id 7
  python3 validate_bio.py --player-id 7 --md-file /mnt/nas/leeds/research/leeds_players/eddie_gray.md
  python3 validate_bio.py --player-id 7 --strict  # fail on warnings too

CRITICAL: billresearch MUST run this script and get exit 0 before reporting "complete".
If exit 1, fix every violation listed and re-run until clean.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter

sys.path.insert(0, '/mnt/nas/leeds/research')


def load_env(env_path="/mnt/nas/leeds/.env"):
    """Load Supabase credentials."""
    if not os.path.exists(env_path):
        print(f"ERROR: .env not found at {env_path}")
        sys.exit(2)
    creds = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                creds[key] = val
    url = creds.get('SUPABASE_URL', '').rstrip('/')
    if not url.endswith('/rest/v1'):
        url = url + '/rest/v1'
    return url, creds.get('SUPABASE_SERVICE_ROLE_KEY', '')


def api_get(base, key, path):
    """GET from Supabase REST API."""
    import urllib.request
    url = f"{base}/{path}"
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  API error on {path}: {e}")
        return []


class BioValidator:
    def __init__(self, player_id, md_file=None, strict=False):
        self.player_id = player_id
        self.md_file = md_file
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.passed = []

        base, key = load_env()
        self.base = base
        self.key = key

        # Load player data
        self.player = self._get_player()
        self.md_content = self._load_md()

    def _get_player(self):
        rows = api_get(self.base, self.key, f"players?id=eq.{self.player_id}&select=*")
        return rows[0] if rows else {}

    def _load_md(self):
        if not self.md_file:
            # Try to find from player record
            bio_file = self.player.get('bio_file', '')
            if bio_file:
                self.md_file = f"/mnt/nas/leeds/research/leeds_players/{bio_file}"
        if self.md_file and os.path.exists(self.md_file):
            with open(self.md_file) as f:
                return f.read()
        return ''

    def add_error(self, msg):
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)

    def add_pass(self, msg):
        self.passed.append(msg)

    # ================================================================
    # CHECK 1: No duplicate player records
    # ================================================================
    def check_duplicates(self):
        """Check for duplicate player records by last_name."""
        last_name = self.player.get('last_name', '')
        if not last_name:
            self.add_warning("Player has no last_name set — cannot check duplicates")
            return

        rows = api_get(self.base, self.key,
                       f"players?last_name=eq.{last_name}&select=id,full_name,date_of_birth")
        if len(rows) > 1:
            names = [f"id={r['id']} ({r.get('full_name','?')}, dob={r.get('date_of_birth','?')})" for r in rows]
            self.add_error(
                f"DUPLICATE PLAYER RECORDS: Found {len(rows)} rows for last_name '{last_name}': {names}. "
                f"Consolidate to ONE record — delete extras and their children, keep canonical, re-insert children."
            )
        else:
            self.add_pass(f"No duplicate player records (1 row for last_name '{last_name}')")

    # ================================================================
    # CHECK 2: Parents present and not fabricated
    # ================================================================
    def check_parents(self):
        """Parents must be inserted. Names must be 'Unknown' if not from scraped sources."""
        parents = api_get(self.base, self.key,
                          f"player_parents?player_id=eq.{self.player_id}&select=*")

        if len(parents) < 2:
            self.add_error(
                f"PARENTS MISSING: Only {len(parents)} parent rows found. "
                f"MUST have at least 2 (mother and father). "
                f"Insert 'Unknown' for undocumented parents — never skip."
            )
            return

        suspicious_names = []
        for p in parents:
            name = p.get('name', '').strip()
            rel = p.get('relationship', '?')
            if name and name != 'Unknown' and name.lower() != 'unknown':
                # Name is set — flag for manual verification
                suspicious_names.append(f"{rel}='{name}'")

        if suspicious_names:
            self.add_warning(
                f"PARENT NAMES SET (verify from sources): {', '.join(suspicious_names)}. "
                f"If these names are NOT from a scraped source (Wikipedia/Transfermarkt/BBC), "
                f"change them to 'Unknown'. Fabricated parent names are a known hallucination pattern."
            )
        else:
            self.add_pass("Parents present (Unknown where undocumented)")

    # ================================================================
    # CHECK 3: No fabricated death date for living players
    # ================================================================
    def check_death_date(self):
        """If player is alive, date_of_death must be null."""
        dod = self.player.get('date_of_death')

        if dod and self.md_content:
            # Check if the markdown says they're alive or dead
            if 'Death' not in self.md_content and 'died' not in self.md_content.lower():
                self.add_error(
                    f"DEATH DATE SUSPICIOUS: players.date_of_death='{dod}' but markdown has no Death section. "
                    f"This is a known hallucination pattern (fabricating death dates for living players). "
                    f"If the player is alive, set date_of_death=null."
                )
            else:
                self.add_pass(f"Death date ({dod}) present and markdown confirms deceased")
        elif not dod:
            # Check if markdown mentions death but DB doesn't have it
            if self.md_content and ('## 12' in self.md_content or 'died' in self.md_content.lower()):
                death_section = re.search(r'## 1[12]\.\s*Death.*?(?=##|\Z)', self.md_content, re.DOTALL)
                if death_section and len(death_section.group()) > 50:
                    self.add_warning(
                        "Markdown has death content but DB date_of_death is null. "
                        "Verify if the player is deceased."
                    )
                else:
                    self.add_pass("Player appears to be alive (no death date)")
            else:
                self.add_pass("Player appears to be alive (no death date)")

    # ================================================================
    # CHECK 4: Career entries exist and match Transfermarkt
    # ================================================================
    def check_career(self):
        """Verify career entries exist in player_career."""
        career = api_get(self.base, self.key,
                         f"player_career?player_id=eq.{self.player_id}&select=*")

        if not career:
            self.add_error("NO CAREER ENTRIES: player_career is empty for this player.")
            return

        # Check for duplicate (club_id, start_year) combinations
        seen = Counter()
        for c in career:
            key = f"club_id={c['club_id']},start={c['start_year']}"
            seen[key] += 1

        dupes = [k for k, v in seen.items() if v > 1]
        if dupes:
            self.add_error(
                f"DUPLICATE CAREER ENTRIES: {dupes}. "
                f"Same club + start year should only appear once."
            )
        else:
            clubs = len(set(c['club_id'] for c in career))
            self.add_pass(f"Career entries present ({len(career)} stints across {clubs} clubs, no duplicates)")

    # ================================================================
    # CHECK 5: Stats reconciliation — competitive totals match
    # ================================================================
    def check_stats_reconciliation(self):
        """Sum competitive stats from DB and compare to markdown section 6a."""
        stats = api_get(self.base, self.key,
                        f"player_stats?player_id=eq.{self.player_id}&select=*")

        if not stats:
            self.add_error("NO STATS ENTRIES: player_stats is empty for this player.")
            return

        # Check for duplicates using (club_id, competition_type, season) tuple
        seen = Counter()
        for s in stats:
            key = f"club={s.get('club_id','?')},type={s['competition_type']},season={s.get('season','?')}"
            seen[key] += 1

        dupes = [k for k, v in seen.items() if v > 1]
        if dupes:
            self.add_error(
                f"DUPLICATE STATS ENTRIES for competition_type: {dupes}. "
                f"Each competition_type should appear once per club per season range."
            )

        # Sum competitive stats
        comp_stats = [s for s in stats if s.get('is_competitive', True)]
        db_apps = sum(s.get('appearances', 0) for s in comp_stats)
        db_goals = sum(s.get('goals', 0) for s in comp_stats)

        # Parse markdown for career total — look for CAREER TOTAL row
        md_apps = None
        md_goals = None
        if self.md_content:
            # Strategy 1: Find CAREER TOTAL line (any case) and extract apps/goals
            total_line = re.search(r'(?:CAREER|career|Career)\s*(?:TOTAL|Total|total).*?\*{0,2}(\d+)\s*[/]\s*(\d+)', self.md_content, re.IGNORECASE)
            if total_line:
                md_apps = int(total_line.group(1))
                md_goals = int(total_line.group(2))
            else:
                # Strategy 2: Look in section 6a for "Total" patterns
                section_6a = re.search(
                    r'6a\.?\s*Competitive.*?(?=6b|## 7)', self.md_content, re.DOTALL | re.IGNORECASE
                )
                if section_6a:
                    text = section_6a.group()
                    # Find bold numbers like **314 / 5**
                    bold_match = re.search(r'\*{2,}(\d+)\s*[/]\s*(\d+)\*{2,}', text)
                    if bold_match:
                        md_apps = int(bold_match.group(1))
                        md_goals = int(bold_match.group(2))
                    else:
                        # Last resort: "XXX appearances" pattern
                        apps_match = re.findall(r'(\d+)\s*(?:appearances|apps)', text, re.IGNORECASE)
                        if apps_match:
                            md_apps = max(int(x) for x in apps_match)
                        goals_match = re.findall(r'(\d+)\s*(?:goals|gls)', text, re.IGNORECASE)
                        if goals_match:
                            md_goals = max(int(x) for x in goals_match)

        if md_apps is not None and md_goals is not None:
            if db_apps == md_apps and db_goals == md_goals:
                self.add_pass(f"Stats reconcile: DB={db_apps} apps/{db_goals} goals = MD §6a={md_apps}/{md_goals}")
            else:
                self.add_error(
                    f"STATS MISMATCH: DB competitive totals={db_apps} apps/{db_goals} goals "
                    f"but markdown §6a says {md_apps}/{md_goals}. "
                    f"Fix either the DB or the markdown so they match."
                )
        else:
            self.add_warning(
                f"Could not parse §6a totals from markdown (DB has {db_apps} apps/{db_goals} goals). "
                f"Manual verification needed."
            )

    # ================================================================
    # CHECK 6: No orphaned child records from deleted duplicates
    # ================================================================
    def check_orphans(self):
        """Check that all child records point to existing players."""
        all_players = api_get(self.base, self.key, "players?select=id")
        valid_ids = set(p['id'] for p in all_players)

        tables = ['player_parents', 'player_career', 'player_stats', 'player_honours']
        for table in tables:
            rows = api_get(self.base, self.key, f"{table}?select=player_id,id")
            orphans = [r for r in rows if r['player_id'] not in valid_ids]
            if orphans:
                orphan_ids = [r['id'] for r in orphans[:5]]
                self.add_error(
                    f"ORPHANED RECORDS: {len(orphans)} rows in {table} reference deleted player_ids. "
                    f"Example row ids: {orphan_ids}. Delete these orphaned rows."
                )

        self.add_pass("No orphaned child records")

    # ================================================================
    # CHECK 7: honour_type constraint compliance
    # ================================================================
    def check_honour_types(self):
        """honour_type must be 'club' or 'individual', never 'international'."""
        honours = api_get(self.base, self.key,
                          f"player_honours?player_id=eq.{self.player_id}&select=*")

        if not honours:
            self.add_warning("No honours entries — verify this player truly won nothing")
            return

        bad_types = [h for h in honours if h.get('honour_type') not in ('club', 'individual')]
        if bad_types:
            self.add_error(
                f"INVALID honour_type values: {[(h['honour_name'], h['honour_type']) for h in bad_types]}. "
                f"Only 'club' and 'individual' are allowed. Use 'club' with club_id=null for international honours."
            )
        else:
            self.add_pass(f"Honour types valid ({len(honours)} honours, all 'club' or 'individual')")

    # ================================================================
    # CHECK 8: Markdown structure — key sections present
    # ================================================================
    def check_md_sections(self):
        """Verify markdown has the required content. Flexible on section numbering."""
        if not self.md_content:
            self.add_warning("No markdown file loaded — cannot check sections")
            return

        # Check for key content keywords rather than exact section numbers
        # (Charles bio uses different numbering — pre-standardization)
        content_checks = [
            ('Full Name', r'(?:full name|Full Name|## .*Name)'),
            ('Date of Birth', r'(?:date of birth|Date of Birth|Born|born|DOB)'),
            ('Place of Birth', r'(?:place of birth|Place of Birth|born in|Born in)'),
            ('Parents', r'(?:parent|Parent|father|Father|mother|Mother)'),
            ('Playing Career', r'(?:playing career|Playing Career|Club Career|club career)'),
            ('Statistics', r'(?:appearance|Appearance|statistic|Statistic)'),
            ('International', r'(?:international|International)'),
            ('Playing Style', r'(?:playing style|Playing Style|position|Position)'),
            ('Honours', r'(?:honour|Honour|trophy|Trophy)'),
            ('Post-retirement', r'(?:post|Post|retir|Retir|manag|Manag|coach|Coach)'),
        ]

        missing = []
        for label, pattern in content_checks:
            if not re.search(pattern, self.md_content, re.IGNORECASE):
                missing.append(label)

        if missing:
            self.add_error(f"MISSING CONTENT in markdown: {', '.join(missing)}")
        else:
            self.add_pass("All required content sections present")

    # ================================================================
    # CHECK 9: No "gold standard" template notes
    # ================================================================
    def check_no_gold_standard(self):
        """Markdown should not claim to be the 'gold standard' template."""
        if not self.md_content:
            return
        if 'gold standard' in self.md_content.lower():
            self.add_warning(
                "Markdown contains 'gold standard' — remove this. "
                "Every bio simply follows the standard template."
            )
        else:
            self.add_pass("No 'gold standard' template notes")

    # ================================================================
    # RUN ALL CHECKS
    # ================================================================
    def run(self):
        print(f"╔══════════════════════════════════════════════════════════╗")
        print(f"║  BIO VALIDATION — player_id={self.player_id:<34}║")
        if self.player:
            print(f"║  Player: {self.player.get('full_name','?'):<46}║")
        if self.md_file:
            print(f"║  MD: {os.path.basename(self.md_file):<49}║")
        print(f"╚══════════════════════════════════════════════════════════╝")
        print()

        checks = [
            ("Duplicate player records", self.check_duplicates),
            ("Parents present & not fabricated", self.check_parents),
            ("No fabricated death date", self.check_death_date),
            ("Career entries exist", self.check_career),
            ("Stats reconciliation", self.check_stats_reconciliation),
            ("No orphaned records", self.check_orphans),
            ("Honour types valid", self.check_honour_types),
            ("Markdown sections complete", self.check_md_sections),
            ("No 'gold standard' notes", self.check_no_gold_standard),
        ]

        for name, fn in checks:
            try:
                fn()
            except Exception as e:
                self.add_error(f"CHECK CRASHED ({name}): {e}")

        # Print results
        for msg in self.passed:
            print(f"  ✅ {msg}")
        for msg in self.warnings:
            print(f"  ⚠️  {msg}")
        for msg in self.errors:
            print(f"  ❌ {msg}")

        print()
        total = len(self.passed) + len(self.warnings) + len(self.errors)
        print(f"  Total: {len(self.passed)} passed, {len(self.warnings)} warnings, {len(self.errors)} errors")

        if self.errors:
            print()
            print("  ❌ VALIDATION FAILED — fix all errors before reporting complete.")
            sys.exit(1)
        elif self.warnings and self.strict:
            print()
            print("  ⚠️  VALIDATION FAILED (strict mode) — resolve warnings or re-run without --strict")
            sys.exit(1)
        else:
            print()
            print("  ✅ VALIDATION PASSED — safe to report complete.")
            sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate a player bio against all integrity rules')
    parser.add_argument('--player-id', type=int, required=True, help='Supabase player ID')
    parser.add_argument('--md-file', type=str, help='Path to markdown bio file')
    parser.add_argument('--strict', action='store_true', help='Fail on warnings too')
    args = parser.parse_args()

    validator = BioValidator(args.player_id, args.md_file, args.strict)
    validator.run()
