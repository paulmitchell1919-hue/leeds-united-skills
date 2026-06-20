---
name: social-media-alternatives-research
description: Research and document free alternatives to social media APIs for content monitoring, search, and data collection without paying for API access.
triggers:
  - User wants to monitor social media without APIs
  - Need to search X/Twitter, Facebook, Reddit, LinkedIn without official APIs
  - User asks "how do I search social media without paying for APIs?"
---

# Social Media Alternatives Research

## Overview

Research and document free alternatives to paid social media APIs. Most platforms aggressively block automated access, but viable options exist when you understand the landscape.

## Research Methodology

### Step 1: Check Current Tool Capabilities

Verify what your environment already has:
```bash
# Check browser tool
hermes tool browser

# Check web search capabilities
hermes tool web_search

# Check Firecrawl/API restrictions
curl http://localhost:3002/status
# Note: Firecrawl explicitly blocks social media URLs
```

### Step 2: Research Platform-Specific Alternatives

For each platform (Twitter/X, Facebook, Reddit, LinkedIn, Instagram):

**Key research points:**
- Are there open-source frontends? (Nitter, Teddit, etc.)
- Are RSS feeds available? (Reddit, some others)
- Is there a free API tier? (Reddit)
- What are the platform's anti-automation measures?
- Are there public instances available? (Check for CAPTCHA issues)

**Research sources:**
- GitHub (search for "twitter frontend", "reddit alternative")
- Platform documentation (Reddit API docs, etc.)
- Community forums (Hacker News, Reddit)
- Alternative frontends documentation

### Step 3: Evaluate Feasibility

Create a comparison matrix:

| Approach | Difficulty | Reliability | Cost | Setup Time |
|----------|------------|-------------|------|-------------|
| RSS Feeds | Easy | High | Free | 0 minutes |
| Self-hosted frontend | Hard | Medium | Free | 2-3 hours |
| Free API | Medium | High | Free | 10-30 minutes |
| Public instances | Medium | Low | Free | 5 minutes |

### Step 4: Document Implementation Approach

For each viable option, document:

**Self-hosted Frontend (e.g., Nitter):**
```bash
# Clone and setup
git clone https://github.com/zedeus/nitter.git
cd nitter
docker-compose up -d

# Create session tokens (crucial step)
python tools/create_session_browser.py <username> <password> --append ../sessions.jsonl
```

**RSS Feeds:**
```bash
# Reddit
https://reddit.com/r/subreddit.rss
https://reddit.com/r/subreddit/new.rss
https://reddit.com/r/subreddit/top.rss

# Parse with standard RSS libraries
```

**Free API (Reddit):**
```bash
# Basic access, no OAuth required
curl -A "YourApp/1.0" https://www.reddit.com/r/subreddit/new.json

# Limits: 60 requests/minute, read-only
```

### Step 5: Create Implementation Plan

Structure the plan into phases:

**Phase 1: Quick Wins** (today/this week)
- RSS feeds (zero setup)
- Web search for indexed content
- Test free APIs

**Phase 2: Build Infrastructure** (holiday project)
- Self-host alternative frontends
- Create aggregator dashboard
- Set up automated monitoring

**Phase 3: Enhance and Expand** (later)
- Add more platforms
- Improve reliability
- Build custom scrapers

### Step 6: Document Limitations

Be clear about what won't work:

**Browser Automation:**
- Most social platforms detect and block headless browsers
- Requires residential proxies (costs money)
- Sophisticated fingerprint spoofing needed

**Public Instances:**
- Most have CAPTCHA protection
- Aggressive rate limiting
- Unreliable for automated access

**Legal/ToS:**
- Scraping may violate platform terms of service
- Respect robots.txt and rate limits
- Don't do mass scraping (will get banned)

## Common Platforms

### Twitter/X
- **Nitter:** Open-source frontend, needs session tokens
- **RSS:** No native RSS (Nitter provides it)
- **API:** No free tier
- **Reliability:** Medium (session tokens expire)

### Reddit
- **RSS:** Built-in and reliable
- **API:** Free tier available (60 req/min, read-only)
- **Teddit:** Alternative frontend (public instances available)
- **Reliability:** High

### Facebook
- **RSS:** Limited to public pages
- **API:** Requires business verification
- **Alternative frontends:** Limited options
- **Reliability:** Low

### LinkedIn
- **RSS:** No native RSS
- **API:** No free tier
- **Alternative frontends:** None widely available
- **Reliability:** Very Low

### Instagram
- **Bibliogram:** Alternative frontend (unmaintained)
- **API:** No free tier
- **Reliability:** Very Low

## Output Format

Document your research findings in markdown:

```markdown
# Platform Name

## Current Status
- What works: [list viable options]
- What doesn't work: [list blocked approaches]
- Reliability: [Low/Medium/High]
- Difficulty: [Easy/Medium/Hard]

## Recommended Approach
[Best option with setup instructions]

## Alternatives
[Other options with brief notes]

## Limitations
[What won't work and why]
```

## Verification

After documenting, test your recommendations:

```bash
# Test RSS feeds
curl "https://reddit.com/r/subreddit.rss"

# Test self-hosted frontend
curl "http://localhost:8080"

# Test free API
curl -A "TestApp/1.0" "https://www.reddit.com/r/subreddit/new.json"
```

## Common Pitfalls

1. **Ignoring rate limits** → Platforms block aggressive scraping
2. **Not respecting ToS** → Legal/compliance risks
3. **Assuming public instances work** → Most have CAPTCHA
4. **Forgetting session maintenance** → Frontend tokens expire
5. **Over-promising reliability** → Social platforms constantly change anti-bot measures

## When to Use This Skill

- User asks "how do I search Twitter without API?"
- User wants to monitor social media for free
- Need to gather social content without paid services
- Building social media aggregator or monitoring system
