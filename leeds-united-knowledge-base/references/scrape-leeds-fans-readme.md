# scrape_leeds_fans.py — Leeds Results Scraper

Formerly: `scripts/scrape_leeds_fans.py` inside the standalone
`leeds-united-results-scraping` skill. Now lives here under
`scripts/scrape_leeds_fans.py` because match-results scraping is part of the
broader Leeds knowledge-base workflow.

## CLI (unchanged from original)

```bash
python scripts/scrape_leeds_fans.py \
  --out ~/leeds-results/leeds_fans_1919_2009.csv \
  --raw-dir ~/leeds-results/raw/leeds-fans
```

Consumes:
- https://www.leeds-fans.org.uk/leeds/history/Results.html
- Linked season pages including `1.html` (1919-20)
