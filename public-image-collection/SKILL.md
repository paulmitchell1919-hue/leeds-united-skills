---
name: public-image-collection
description: >
  Collect legally-reusable photographs from open sources (e.g. Wikimedia Commons,
  Geograph UK) for a set of real-world venues/locations. Enforces commercial-use
  licence gating, real-image verification, and honest blocker reporting.
  Use when the task is "find images for X venues", "image audit", or "build
  a photo library for app use".
---

# Public Image Collection

## When to load
- User asks for an image database / photo library for real places/venues.
- Need commercial-use, attributed images (CC BY, CC BY-SA, CC0, Public Domain).
- Sources: Wikimedia Commons + Geograph UK (or similar open repositories).

## Do not do
- Do **not** fabricate filenames, URLs, authors, or licences.
- Do **not** download "placeholder" or generic images when a venue-specific image cannot be found.
- Do **not** keep wrong-location images just to inflate counts.
- Do **not** guess direct upload URLs from file titles — Commons redirect URLs are
  not trivially guessable from title text.

## Required workflow

1. Agree the destination path with the user first.
   - On this Linux orchestrator, NAS mounts are typically `/mnt/nas/...`.
   - If the user requests a path like `/Volumes/projects-1/...`, treat that as the real output location. Create or bind-mount the share onto that path ASAP, then use it for all writes.
   - Do not silently substitute `/mnt/nas` for a user-requested path — reconcile the mount before the first folder creation.

2. List every venue and create the folder scaffold up front.

3. Query Wikimedia Commons with `action=query&list=search&srnamespace=6`.
   - After every request, sleep **0.45–0.6 s**.
   - If you receive `429 Too Many Requests`, stop the batch.
     Do not hammer the endpoint; pause or switch to a different source.

4. Resolve each candidate file title through `action=query&prop=imageinfo`.
   - Parse `imageinfo[0].url` — this is the actual file URL to download.
   - Parse `extmetadata.License.value` and `extmetadata.Artist.value`.
   - Licence must contain one of: `Public Domain`, `CC0`, `CC BY`, `CC BY-SA`.
     Reject everything else (including NC variants and unknown licences).

5. Download only the verified direct URLs.
   - File extension must be image-like: `.jpg`, `.jpeg`, `.png`, `.gif`.
   - Store each venue’s images in its own folder.

6. Write `metadata.json` per venue with exactly the entries downloaded.
   - `image_count` = number of files successfully saved.
   - `images` array entries: filename, source, author, licence, direct url,
     `commercial_use: true`, `attribution_required: true`.
   - If no image was found for a venue, write an empty `images` array and a
     `note` explaining the blocker. Do **not** invent rows.

7. Write a `summary_report.json` at the root listing counts and blockers per venue.

## Pitfalls

### Wikimedia rate limits
- The Commons API enforces burst limits aggressively.
- A safe single-threaded cadence is ~0.5 s between `search` and `imageinfo`
  calls. Hammering it causes 429s and you lose the batch.

### Geograph UK API instability
- Historically, `/api/grid-references` and `/api/search` have returned
  `Unknown method` 400s from this environment. Do not treat this as a
  required source; rely primarily on Commons, and surface Geograph ONLY if
  a working endpoint is confirmed.

### Commons direct-URL guessing
- Upload URLs follow an unpredictable hash-based path.
- Always use `imageinfo` to obtain `url`. Never reconstruct the path by hand.

### Wrong-location matches
- A Commons search for `"The New Inn"` can return pubs in Winchelsea, Bilbao,
  or elsewhere. Always check the title context (street, city) before keeping
  an image. Title strings containing the venue name **plus** `Headingley` or
  `Leeds` are the trustworthy ones.

## Output contract
- Root folder: agreed with user (e.g. `/mnt/nas/pubrun/famous_run_pub_history/`)
- Per-venue: `<venue_id>/img.<ext>` (or a clear filename), `metadata.json`.
- Root: `summary_report.json`.

## Escalation
- If after 2–3 verified Commons hits per venue you still have gaps, stop
  and report the shortfall with the blocker reason. Do not loop into
  unverified guesswork.
