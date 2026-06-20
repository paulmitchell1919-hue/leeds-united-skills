---
name: web-search-options-for-ai-agents
description: Comprehensive guide to free and low-cost web search APIs for AI agents. Compare Tavily, Serper, DontBeEvil, web-scraping tools, and Common Crawl. Deep research, LLM-optimized content, broad discovery capabilities.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Research, Web Search, AI Agents, APIs, Free Tools]
    related_skills: [web-tools, browser-tool, ideation]
---

# Web Search Options for AI Agents

Comprehensive guide to free and low-cost web search APIs for AI agents, focused on deep research, LLM-optimized results, and broad discovery capabilities.

## When to Use This Skill

Use this skill when:
- You need to implement web search capabilities for an AI agent
- You're researching technical topics, competitors, or best practices
- You need to aggregate information from multiple sources
- You want LLM-optimized content (not just raw HTML)
- Budget is constrained (free/low-cost options needed)

## Top Recommendations

### 1. Tavily ⭐ (Best Overall for AI Agents)

**What it is:**
- Built specifically for AI agents
- Returns LLM-optimized, pre-chunked content
- Real-time web search with intelligent ranking
- Specialized search modes: news, finance, AI topics
- Multi-step workflows: search → extract → map → crawl → research

**Pricing:**
- **Free tier:** 1,000 credits/month
- **Pay-as-you-go:** $0.008/credit after free tier
- **Student pricing:** Free program available

**Why it's perfect for AI agents:**
- ✅ Pre-processed content for LLM consumption (saves tokens)
- ✅ Relevance scoring included
- ✅ Real-time (fresh data)
- ✅ Configurable search depth, result counts, domain filtering
- ✅ Supports deep research workflows

**Installation:**
```bash
npx skills add https://github.com/tavily-ai/skills --skill tavily-search
```

**Example usage:**
```python
result = tavily_search("mission control build challenges", 
                       topic="news", 
                       max_results=10, 
                       search_depth="basic", 
                       days=3)
```

---

### 2. Serper.dev (Best Backup/Google Access)

**What it is:**
- Google Search API wrapper
- Returns structured JSON SERP results
- Very fast (1-2 seconds)

**Pricing:**
- **Free tier:** 2,500 one-time free queries
- **Pay-as-you-go:** $1.00/1k credits (after free tier)
- No monthly subscription required

**Why it's good as backup:**
- ✅ Google results when Tavily doesn't have something
- ✅ Structured data for AI processing
- ✅ Great for specific searches ("How do I build X", "React hooks tutorial")
- ✅ Simple REST API

**Installation:**
```bash
npx skills add https://github.com/SerpApi/serper-skills --skill serper-search
```

---

### 3. DontBeEvil.rip (Best for Technical/Developer Research)

**What it is:**
- Developer-focused search engine
- Indexes quality resources: Hacker News, Stack Overflow, GitHub, ArXiv, programmer Reddit
- $10/month flat rate (no hidden fees)
- 25.8K indexed articles
- Custom search via CLI (Elasticsearch Simple Query Strings)
- REST API + CLI

**Pricing:**
- **$10/month** - Flat rate
- **First 1K queries free** (to try it out)

**Why it's good for technical research:**
- ✅ No junk content (only dev resources)
- ✅ Great for coding tutorials, documentation searches
- ✅ Perfect for finding library solutions, debugging help
- ✅ Search GitHub issues, Stack Overflow answers, ArXiv papers
- ✅ CLI tools for automation

**Installation:**
```bash
npx skills add https://github.com/DontBeEvil/riper-skills --skill search
```

**Use case examples:**
- "react hooks tutorial" → Finds high-quality Stack Overflow results
- "github issue with file upload" → Searches GitHub codebase
- "how to implement oauth" → Finds tutorials and docs

---

## What to Avoid

### ❌ Web-Scraping Skills (e.g., jamditis web-scraping)

**Why not for deep research:**
- Designed for specific URL extraction, not broad discovery
- Requires you to know which sites to scrape
- Need custom extraction rules
- No built-in search/indexing

**When to use:** Only when you need to extract structured data from a KNOWN website.

---

### ❌ Common Crawl

**Why avoid:**
- Archived project (last data from 2008-2012)
- Cannot access current web content
- Completely useless for current research

---

### ❌ Maxun

**Why not for deep research:**
- Open-source no-code web scraping platform
- Designed for specific site extraction (ecommerce, real estate, etc.)
- No built-in search/discovery
- Would require building custom index and aggregator

**When to use:** Building a custom scraper for specific, known websites.

---

## Recommended Stack for AI Agents

### Primary Stack (Free):
```bash
# Tavily (main) - 1,000 free credits/month
npx skills add https://github.com/tavily-ai/skills --skill tavily-search

# Serper.dev (backup) - 2,500 free one-time queries  
npx skills add https://github.com/SerpApi/serper-skills --skill serper-search
```

### Optional Addition (Technical Research):
```bash
# DontBeEvil.rip - $10/month (optional)
npx skills add https://github.com/DontBeEvil/riper-skills --skill search
```

---

## Integration with Hermes Agent

### Setup Tavily:

1. Sign up at https://tavily.com (free tier)
2. Get API key from dashboard
3. Add to `~/.hermes/.env`:
   ```bash
   TAVILY_API_KEY=your_key_here
   ```
4. Update `~/.hermes/config.yaml`:
   ```yaml
   web:
     backend: tavily
   ```
5. Restart Hermes gateway

### Setup Serper (Backup):

1. Sign up at https://serper.dev (2,500 free queries)
2. Get API key
3. Add to `~/.hermes/.env`:
   ```bash
   SERPER_API_KEY=your_key_here
   ```
4. Implement as fallback in Hermes web tools

---

## Cost Comparison

| Tool | Monthly Cost | Annual Cost | Free Tier |
|------|--------------|-------------|-----------|
| **Tavily** | $0 (1K free) | $0 | 1,000 credits/month |
| **Serper** | $0 (2.5K free) | $0 | 2,500 one-time queries |
| **DontBeEvil** | $0 or $10/month | $0 or $120 | 1,000 queries free |

---

## Multi-Step Research Workflow

For complex research (e.g., "mission control build challenges"):

```
1. Tavily search → discover competitors/solutions
2. Firecrawl/scrape → extract detailed features from specific URLs
3. Aggregation → compare with your approach
4. Synthesis → identify gaps and opportunities
```

---

## Key Decision Factors

Choose **Tavily** if:
- You need LLM-optimized content
- You want real-time search
- You're building for AI agents
- Budget is tight but willing to pay for quality

Choose **Serper** if:
- You need Google search results
- You want simple structured data
- You have a specific query in mind
- You want a one-time free tier

Choose **DontBeEvil.rip** if:
- You're researching technical topics
- You need Stack Overflow/GitHub/ArXiv results
- You want dev-focused results only
- $10/month is acceptable

Choose **Web Scraping** if:
- You know exactly which sites to scrape
- You need custom extraction logic
- You're building a domain-specific crawler
- You have time to maintain extraction rules

---

## Testing Recommendations

1. **Test Tavily free tier first** - 1,000 credits is plenty for research
2. **Add Serper as backup** - when Tavily doesn't have specific results
3. **Evaluate DontBeEvil.rip later** - only if you need deep technical research
4. **Avoid self-hosting initially** - setup cost outweighs free API benefits

---

## Common Pitfalls

- ❌ Don't use web scraping for broad discovery - it's for specific sites
- ❌ Don't use archived data (Common Crawl) for current research
- ❌ Don't build your own crawler unless you have very specific needs
- ❌ Don't optimize prematurely - free tiers are sufficient for most use cases
- ❌ Don't ignore rate limits - they exist even on free tiers

---

## Related Skills

- `ideation` - Generate project ideas when you have tools but no direction
- `browser-tool` - Manual browser-based search (free but slower)
- `web-tools` - Hermes built-in web search/scrape (requires Firecrawl or similar API)
