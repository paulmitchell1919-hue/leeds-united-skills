# generate_leeds_transfer_urls.py — Leeds Transfer URL Generator

Formerly: `scripts/generate_leeds_transfer_urls.py` inside the standalone
`leeds-united-transfers-research` skill. Lives here under
`scripts/generate_leeds_transfer_urls.py`.

## CLI (unchanged from original)

```bash
python scripts/generate_leeds_transfer_urls.py \
  --start 1992 --end 2026 \
  --out ~/leeds-transfers/transfer_source_urls.csv
```

Outputs: one URL per season pointing at Transfermarkt's Leeds United transfers
page so the scraper loop can iterate without hand-crafting season IDs.
