#!/usr/bin/env python3
"""Reusable checker: split a player's goal tally by competition from the Leeds CSV.

Defaults to Mark Viduka on the known master CSV, but accepts --csv, --player and
optional --season / --from-season / --to-season filters.

Output is plain text only. No external dependencies.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

DEFAULT_CSV = "/home/paul/leeds-results/raw/leeds_fans_1919_2009.csv"
DEFAULT_PLAYER = "Viduka"

EURO_PATTERNS = [
    "champions league", "europa league", "uefa cup", "cup winners' cup",
    "inter-cities fairs cup", "inter cities", "texaco cup", "anglo-scottish cup",
    "icfc", "european", "ucl", "cl1", "cl2", "cl3", "cl4", "cl5", "cl6",
    "ucr", "ui",
]
FA_PATTERNS = ["fa cup", "facq", "facr"]
LEAGUE_CUP_PATTERNS = [
    "league cup", "efl cup", "carabao", "carling", "coca-cola", "milk cup",
    "littlewoods", "rumbelows", "worthington", "johnstone", "trophy", "lcr", "lcq",
]
FRIENDLY_PATTERNS = [
    "friendly", "testimonial", "charity", "benevolent", "benefit", "lysekil",
    "jonkoping", "gais", "preston north end (friendly)", "sparta rotterdam",
    "green town", "burnley (friendly)", "bray wanderers", "fcv dender",
]
EURO_CLUBS = {"besiktas", "real madrid", "lazio", "anderlecht", "troyes"}


def norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", (text or "").lower()).strip() + " "


def classify(row: dict) -> str:
    comp = norm(row.get("competition", ""))
    opp = norm(row.get("opponent", ""))
    notes = norm(row.get("notes", ""))
    text = f"{comp} {opp} {notes}"
    if any(p in text for p in EURO_PATTERNS) or any(club in opp for club in EURO_CLUBS):
        return "Europe"
    if any(p in text for p in FA_PATTERNS):
        return "FA Cup"
    if any(p in text for p in LEAGUE_CUP_PATTERNS):
        return "League Cup"
    if any(p in text for p in FRIENDLY_PATTERNS):
        return "Friendly"
    if row.get("venue") in {"H", "A"} and row.get("opponent"):
        return "League"
    return "Other"


def passes_filters(row: dict, season: str | None, from_season: str | None, to_season: str | None) -> bool:
    if season and row.get("season") != season:
        return False
    if from_season and row.get("season", "") < from_season:
        return False
    if to_season and row.get("season", "") > to_season:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Player goal split by competition from Leeds CSV.")
    ap.add_argument("--csv", default=DEFAULT_CSV)
    ap.add_argument("--player", default=DEFAULT_PLAYER)
    ap.add_argument("--season", default=None)
    ap.add_argument("--from-season", default=None)
    ap.add_argument("--to-season", default=None)
    args = ap.parse_args(argv)

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"CSV not found: {csv_path}", file=sys.stderr)
        return 2

    rows = list(csv.DictReader(csv_path.open(newline="", encoding="utf-8")))
    by_comp: dict[str, dict] = defaultdict(lambda: {"goals": 0, "appearances": 0, "matches": []})
    total_appearances = 0

    for row in rows:
        if not passes_filters(row, args.season, args.from_season, args.to_season):
            continue
        scorers = row.get("scorers") or ""
        tokens = [t.strip() for t in scorers.split(",") if t.strip()]
        goals = sum(1 for t in tokens if args.player.lower() in t.lower())
        if goals == 0:
            continue
        comp = classify(row)
        by_comp[comp]["goals"] += goals
        total_appearances += 1
        by_comp[comp]["appearances"] += 1
        by_comp[comp]["matches"].append(
            {
                "date": row.get("date", ""),
                "opponent": row.get("opponent", ""),
                "venue": row.get("venue", ""),
                "goals": goals,
            }
        )

    print(f"=== {args.player} goal split from {csv_path} ===\n")
    for comp in ["League", "FA Cup", "League Cup", "Europe", "Friendly", "Other"]:
        if comp not in by_comp:
            continue
        data = by_comp[comp]
        print(f"{comp}: {data['goals']} goals in {data['appearances']} matches")
        for m in data["matches"][:8]:
            print(f"  {m['date']} {m['venue']} vs {m['opponent']}: {m['goals']}")
        if len(data["matches"]) > 8:
            print(f"  ... +{len(data['matches']) - 8} more")
        print()

    total_goals = sum(d["goals"] for d in by_comp.values())
    print(f"TOTAL: {total_goals} goals in {total_appearances} matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
