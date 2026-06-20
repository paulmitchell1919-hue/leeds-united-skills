#!/usr/bin/env python3
"""
Verify a player's Supabase entry for data integrity.

Checks:
  1. Duplicate rows in player_career, player_stats, international_career, player_honours
  2. Parents present in player_parents (at least 2 rows — mother and father)
  3. Competitive stats total (sum of appearances/goals where is_competitive=true)
  4. Friendly stats present (at least one row with is_competitive=false)
  5. Player row exists with core fields populated

Usage:
  python verify_player_supabase.py --player-id 3
  python verify_player_supabase.py --player-id 3 --env /mnt/nas/leeds/.env
  python verify_player_supabase.py --player-id 3 --verbose

Exit codes:
  0 = all checks passed
  1 = one or more checks failed (details printed)
  2 = connection/env error

Credentials are loaded from the .env file specified by --env (default: /mnt/nas/leeds/.env on Linux, /Volumes/projects-1/leeds/.env on macOS).
"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from urllib.parse import quote


def load_env(env_path):
    """Load Supabase credentials from a .env file."""
    if not os.path.exists(env_path):
        # Try macOS path
        mac_path = "/Volumes/projects-1/leeds/.env"
        if os.path.exists(mac_path):
            env_path = mac_path
        else:
            print(f"ERROR: .env not found at {env_path} or {mac_path}")
            sys.exit(2)

    creds = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                creds[key] = val

    for required in ["SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY"]:
        if required not in creds:
            print(f"ERROR: {required} not found in {env_path}")
            sys.exit(2)

    # Normalize URL to end with /rest/v1
    url = creds["SUPABASE_URL"].rstrip("/")
    if not url.endswith("/rest/v1"):
        url = url + "/rest/v1"
    creds["SUPABASE_URL"] = url

    return creds


def query(creds, table, filters=""):
    """Query a Supabase table via REST API."""
    base = creds["SUPABASE_URL"]
    key = creds["SUPABASE_SERVICE_ROLE_KEY"]
    url = f"{base}/{table}?{filters}select=*" if filters else f"{base}/{table}?select=*"

    result = subprocess.run(
        [
            "curl", "-s", url,
            "-H", f"apikey: {key}",
            "-H", f"Authorization: Bearer {key}",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse response from {table}: {result.stdout[:200]}")
        return []


def find_duplicates(rows, key_fields):
    """Find duplicate rows based on a tuple of key fields."""
    seen = {}
    duplicates = []
    for row in rows:
        key = tuple(str(row.get(f, "")) for f in key_fields)
        if key in seen:
            duplicates.append(row)
        else:
            seen[key] = row
    return duplicates


def main():
    parser = argparse.ArgumentParser(description="Verify a player's Supabase entry")
    parser.add_argument("--player-id", type=int, required=True, help="Player ID in the players table")
    parser.add_argument("--env", default="/mnt/nas/leeds/.env", help="Path to .env with Supabase credentials")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print all rows, not just failures")
    args = parser.parse_args()

    creds = load_env(args.env)
    pid = args.player_id

    failures = []
    warnings = []

    # --- Check 1: Player row exists ---
    players = query(creds, "players", f"id=eq.{pid}&")
    if not players:
        failures.append(f"❌ FAIL: No player found with id={pid}")
        print("\n".join(failures))
        sys.exit(1)

    player = players[0]
    print(f"\n{'='*60}")
    print(f"Player: {player.get('full_name', 'UNKNOWN')} (id={pid})")
    print(f"Bio file: {player.get('bio_file', 'MISSING')}")
    print(f"{'='*60}\n")

    # Check core fields
    for field in ["full_name", "date_of_birth", "place_of_birth", "position", "nationality", "bio_file"]:
        if not player.get(field):
            warnings.append(f"⚠️  WARN: players.{field} is empty/null")

    # --- Check 2: Parents present ---
    parents = query(creds, "player_parents", f"player_id=eq.{pid}&")
    parent_count = len(parents)
    if parent_count < 2:
        failures.append(f"❌ FAIL: Only {parent_count} parent row(s) — need at least 2 (mother + father). PARENTS MUST ALWAYS BE INSERTED.")
    else:
        relationships = [p.get("relationship", "") for p in parents]
        if "father" not in relationships:
            warnings.append("⚠️  WARN: No 'father' relationship found in player_parents")
        if "mother" not in relationships:
            warnings.append("⚠️  WARN: No 'mother' relationship found in player_parents")
        # Check for "Unknown" names when not documented
        for p in parents:
            if not p.get("name") or p["name"] == "":
                failures.append(f"❌ FAIL: player_parents row has empty name (should be 'Unknown' if undocumented)")
        print(f"✅ Parents: {parent_count} row(s) — {relationships}")

    if args.verbose:
        for p in parents:
            print(f"   {p.get('relationship')}: {p.get('name')} ({p.get('nationality', '?')})")

    # --- Check 3: No duplicate career rows ---
    career = query(creds, "player_career", f"player_id=eq.{pid}&")
    career_dups = find_duplicates(career, ["club_id", "start_year", "end_year", "status"])
    if career_dups:
        failures.append(f"❌ FAIL: {len(career_dups)} DUPLICATE career row(s) found!")
        for d in career_dups:
            failures.append(f"   DUP: club_id={d.get('club_id')} {d.get('start_year')}-{d.get('end_year')} status={d.get('status')}")
    else:
        print(f"✅ Career: {len(career)} stint(s), no duplicates")

    if args.verbose:
        for c in career:
            print(f"   club_id={c.get('club_id')} {c.get('start_year')}-{c.get('end_year')} status={c.get('status')}")

    # --- Check 4: Stats reconciliation ---
    stats = query(creds, "player_stats", f"player_id=eq.{pid}&")
    competitive = [s for s in stats if s.get("is_competitive")]
    friendly = [s for s in stats if not s.get("is_competitive")]

    comp_apps = sum(s.get("appearances", 0) or 0 for s in competitive)
    comp_goals = sum(s.get("goals", 0) or 0 for s in competitive)
    print(f"✅ Stats: {len(competitive)} competitive rows — {comp_apps} apps, {comp_goals} goals")
    print(f"   Competition types: {sorted(set(s.get('competition_type', '?') for s in competitive))}")

    # Check for friendly stats
    if not friendly:
        warnings.append("⚠️  WARN: No friendly/non-competitive stats in DB. Section 6b content should be inserted with competition_type 'friendly'.")
    else:
        print(f"✅ Friendly stats: {len(friendly)} row(s)")

    # Check for duplicate stats rows
    stats_dups = find_duplicates(stats, ["club_id", "season", "competition_type"])
    if stats_dups:
        failures.append(f"❌ FAIL: {len(stats_dups)} DUPLICATE stats row(s) found!")
        for d in stats_dups:
            failures.append(f"   DUP: club_id={d.get('club_id')} season={d.get('season')} comp={d.get('competition_type')}")

    if args.verbose:
        for s in stats:
            tag = "COMP" if s.get("is_competitive") else "FRND"
            print(f"   [{tag}] club={s.get('club_id')} season={s.get('season')} {s.get('competition_type')} apps={s.get('appearances')} goals={s.get('goals')}")

    # --- Check 5: No duplicate international rows ---
    intl = query(creds, "international_career", f"player_id=eq.{pid}&")
    intl_dups = find_duplicates(intl, ["country", "level"])
    if intl_dups:
        failures.append(f"❌ FAIL: {len(intl_dups)} DUPLICATE international row(s) found!")
        for d in intl_dups:
            failures.append(f"   DUP: {d.get('country')} {d.get('level')} caps={d.get('caps')}")
    else:
        print(f"✅ International: {len(intl)} row(s), no duplicates")

    if args.verbose:
        for i in intl:
            print(f"   {i.get('country')} {i.get('level')} caps={i.get('caps')} goals={i.get('goals')}")

    # --- Check 6: No duplicate honours rows ---
    honours = query(creds, "player_honours", f"player_id=eq.{pid}&")
    honours_dups = find_duplicates(honours, ["honour_name", "season"])
    if honours_dups:
        failures.append(f"❌ FAIL: {len(honours_dups)} DUPLICATE honour row(s) found!")
        for d in honours_dups:
            failures.append(f"   DUP: {d.get('honour_name')} {d.get('season')}")
    else:
        print(f"✅ Honours: {len(honours)} row(s), no duplicates")

    if args.verbose:
        for h in honours:
            print(f"   {h.get('honour_name')} {h.get('season')} type={h.get('honour_type')}")

    # --- Summary ---
    print(f"\n{'='*60}")
    if failures:
        print(f"RESULT: ❌ {len(failures)} CHECK(S) FAILED")
        print("\n".join(failures))
        print(f"\n{'='*60}")
        sys.exit(1)
    elif warnings:
        print(f"RESULT: ⚠️  {len(warnings)} WARNING(S) (no hard failures)")
        print("\n".join(warnings))
        print(f"\n{'='*60}")
        sys.exit(0)
    else:
        print("RESULT: ✅ ALL CHECKS PASSED")
        print(f"\n{'='*60}")
        sys.exit(0)


if __name__ == "__main__":
    main()
