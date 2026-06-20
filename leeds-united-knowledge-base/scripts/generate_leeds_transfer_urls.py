#!/usr/bin/env python3
"""Generate direct Leeds United transfer research URLs.

No network calls. Produces a CSV of primary/fallback source URLs for each season
so agents can work season-by-season without broad web search.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def season_label(start_year: int) -> str:
    return f"{start_year}-{str(start_year + 1)[-2:]}"


def wiki_season_url(start_year: int) -> str:
    # enwiki uses an en dash in the title.
    label = f"{start_year}%E2%80%93{str(start_year + 1)[-2:]}_Leeds_United_F.C._season"
    return f"https://en.wikipedia.org/wiki/{label}"


def rows(start: int, end: int):
    for year in range(start, end + 1):
        season = season_label(year)
        yield {
            "season": season,
            "season_start_year": year,
            "source_name": "Transfermarkt UK",
            "source_type": "primary_transfer_ledger",
            "url": f"https://www.transfermarkt.co.uk/leeds-united/transfers/verein/399/saison_id/{year}",
            "notes": "If shell gets 403, use browser or web_extract. season_id is season starting year.",
        }
        yield {
            "season": season,
            "season_start_year": year,
            "source_name": "Transfermarkt COM",
            "source_type": "primary_transfer_ledger_fallback",
            "url": f"https://www.transfermarkt.com/leeds-united/transfers/verein/399/saison_id/{year}",
            "notes": "Fallback host for same club ID 399.",
        }
        yield {
            "season": season,
            "season_start_year": year,
            "source_name": "Wikipedia season page",
            "source_type": "cross_check_transfers",
            "url": wiki_season_url(year),
            "notes": "Use for transfer tables and references; prefer original linked sources where possible.",
        }
        yield {
            "season": season,
            "season_start_year": year,
            "source_name": "Official Leeds search query",
            "source_type": "official_confirmation_query",
            "url": f"site:leedsunited.com/news/team-news \"{season}\" \"Leeds United\" \"sign\" OR \"released\" OR \"loan\"",
            "notes": "Use with web_search when available; otherwise search Leeds site/browser manually.",
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1992, help="first season start year")
    ap.add_argument("--end", type=int, default=2026, help="last season start year")
    ap.add_argument("--out", default="transfer_source_urls.csv")
    args = ap.parse_args()

    if args.end < args.start:
        raise SystemExit("--end must be >= --start")

    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["season", "season_start_year", "source_name", "source_type", "url", "notes"]
    data = list(rows(args.start, args.end))
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(data)
    print(f"wrote {len(data)} source URLs to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
