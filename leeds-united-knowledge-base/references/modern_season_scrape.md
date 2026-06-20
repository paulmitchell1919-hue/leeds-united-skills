# Leeds KB raw-source notes

## Local Firecrawl continuation for 11v11 modern seasons
When default web access to 11v11/worldfootball is blocked by Cloudflare, use the local scrape service:

- Endpoint: `POST http://127.0.0.1:3002/v0/scrape`
- Body: `{"url": "<season_page_url>", "formats": ["markdown"], "onlyMainContent": true}`
- Save field: `data.content`
- Destination: `/home/paul/leeds-results/raw/11v11/<ending_year>.md`
- Do not persist the full response envelope.

This was used successfully for Leeds United 2025-26 season page and should be preferred next time shell scraping fails.