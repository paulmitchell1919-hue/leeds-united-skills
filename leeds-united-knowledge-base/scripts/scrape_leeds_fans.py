#!/usr/bin/env python3
"""Scrape Leeds United historical results from leeds-fans.org.uk.

Primary coverage: 1919-20 through 2008-09. Writes normalized CSV from Leeds
perspective and stores raw HTML when --raw-dir is provided.

Dependencies: Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BASE = "https://www.leeds-fans.org.uk"
INDEX_URL = f"{BASE}/leeds/history/Results.html"
UA = "Mozilla/5.0 (compatible; Hermes-LeedsResults/1.1)"


def fetch(url: str, raw_dir: Path | None = None, delay: float = 0.2) -> str:
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=30) as r:
        raw = r.read()
    text = raw.decode("utf-8", errors="replace")
    if raw_dir:
        raw_dir.mkdir(parents=True, exist_ok=True)
        name = url.rstrip("/").split("/")[-1] or "index.html"
        (raw_dir / name).write_text(text, encoding="utf-8", errors="replace")
    if delay:
        time.sleep(delay)
    return text


def clean_text(s: str) -> str:
    s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def discover_seasons(index_html: str) -> list[tuple[str, str]]:
    """Return [(season_label, absolute_url)] including forced 1919-20 page."""
    seasons: dict[str, str] = {"1919-20": f"{BASE}/leeds/history/1.html"}
    for m in re.finditer(r"<a\s+[^>]*href\s*=\s*[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", index_html, flags=re.I | re.S):
        href, label_html = m.group(1), m.group(2)
        label = clean_text(label_html)
        if re.fullmatch(r"\d{4}-\d{2}", label) and "/leeds/history/" in href and href.endswith(".html"):
            seasons[label] = urljoin(BASE, href)
    return sorted(seasons.items(), key=lambda item: (int(item[0][:4]), item[0]))


def season_from_html(page_html: str, fallback: str) -> str:
    text = clean_text(page_html[:3000])
    m = re.search(r"Season\s+(\d{4})\s*-\s*(\d{4})", text)
    if m:
        return f"{m.group(1)}-{m.group(2)[-2:]}"
    return fallback


def split_opponent_venue(raw: str) -> tuple[str, str]:
    raw = re.sub(r"\s+", " ", raw or "").strip()
    m = re.match(r"^(.*?)\s*\(([^()]*)\)\s*$", raw)
    if not m:
        return raw, ""
    return m.group(1).strip(), m.group(2).strip()


def parse_score(raw: str) -> tuple[int | None, int | None, str]:
    raw = (raw or "").replace("–", "-").replace("—", "-").strip()
    m = re.search(r"(\d+)\s*-\s*(\d+)", raw)
    if not m:
        return None, None, raw
    return int(m.group(1)), int(m.group(2)), raw


def result_from_score(lg: int | None, og: int | None) -> str:
    if lg is None or og is None:
        return ""
    return "W" if lg > og else "L" if lg < og else "D"


def iso_date(raw: str) -> tuple[str, str]:
    raw = (raw or "").strip()
    try:
        d, m, y = raw.split("/")
        return dt.date(int(y), int(m), int(d)).isoformat(), ""
    except Exception:
        return "", f"raw_date={raw}" if raw else "missing_date"


def iter_table_rows(page_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", page_html, flags=re.I | re.S):
        cells = [clean_text(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, flags=re.I | re.S)]
        if cells:
            rows.append(cells)
    return rows


def parse_page(season_label: str, url: str, page_html: str) -> list[dict[str, str]]:
    season = season_from_html(page_html, season_label)
    table_rows = iter_table_rows(page_html)
    out: list[dict[str, str]] = []
    in_games = False
    for cells in table_rows:
        if len(cells) >= 3 and cells[0] == "Date" and cells[1] == "Opponents" and cells[2] == "Result":
            in_games = True
            continue
        if not in_games:
            continue
        if len(cells) >= 2 and cells[0] == "Name" and cells[1] == "Apps":
            break
        if len(cells) < 3 or not re.match(r"\d{2}/\d{2}/\d{4}$", cells[0]):
            continue
        date_iso, date_note = iso_date(cells[0])
        opponent, venue = split_opponent_venue(cells[1])
        leeds_goals, opponent_goals, score_raw = parse_score(cells[2])
        result = result_from_score(leeds_goals, opponent_goals)
        crowd = cells[3] if len(cells) > 3 else ""
        points = cells[4] if len(cells) > 4 else ""
        position = cells[5] if len(cells) > 5 else ""
        scorers = cells[6] if len(cells) > 6 else ""
        notes = "; ".join(x for x in [date_note, f"points_after={points}" if points and points != "-" else "", f"position={position}" if position and position != "-" else "", f"raw_score={score_raw}" if score_raw else ""] if x)
        if venue == "H":
            home_team, away_team = "Leeds United", opponent
        elif venue == "A":
            home_team, away_team = opponent, "Leeds United"
        else:
            home_team, away_team = "", ""
        out.append({
            "season": season,
            "date": date_iso,
            "competition": "",
            "round": "",
            "home_team": home_team,
            "away_team": away_team,
            "venue": venue,
            "opponent": opponent,
            "leeds_goals": "" if leeds_goals is None else str(leeds_goals),
            "opponent_goals": "" if opponent_goals is None else str(opponent_goals),
            "result": result,
            "crowd": crowd,
            "scorers": scorers,
            "source_url": url,
            "source_name": "leeds-fans.org.uk",
            "notes": notes,
        })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="leeds_fans_1919_2009.csv")
    ap.add_argument("--raw-dir", default="")
    ap.add_argument("--limit", type=int, default=0, help="debug: only scrape first N season pages")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir).expanduser() if args.raw_dir else None
    index_html = fetch(INDEX_URL, raw_dir)
    seasons = discover_seasons(index_html)
    if args.limit:
        seasons = seasons[: args.limit]

    rows: list[dict[str, str]] = []
    failures: list[str] = []
    for season, url in seasons:
        try:
            page_html = fetch(url, raw_dir)
            page_rows = parse_page(season, url, page_html)
            if not page_rows:
                failures.append(f"{season}: no match table rows at {url}")
            rows.extend(page_rows)
            print(f"{season}: {len(page_rows)} rows", file=sys.stderr)
        except Exception as e:
            failures.append(f"{season}: {url}: {e}")

    fieldnames = ["season","date","competition","round","home_team","away_team","venue","opponent","leeds_goals","opponent_goals","result","crowd","scorers","source_url","source_name","notes"]
    out = Path(args.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    audit = out.with_suffix(".audit.md")
    with audit.open("w", encoding="utf-8") as f:
        f.write("# Leeds-fans scrape audit\n\n")
        f.write(f"- Source index: {INDEX_URL}\n")
        f.write(f"- Seasons attempted: {len(seasons)}\n")
        f.write(f"- Rows written: {len(rows)}\n")
        if failures:
            f.write("\n## Warnings\n")
            for item in failures:
                f.write(f"- {item}\n")
    print(f"wrote {len(rows)} rows to {out}")
    print(f"audit {audit}")
    if failures:
        print(f"warnings: {len(failures)}", file=sys.stderr)
    return 0 if rows else 2


if __name__ == "__main__":
    raise SystemExit(main())
