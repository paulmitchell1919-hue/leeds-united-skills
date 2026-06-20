# Anti-Hallucination Decision Trees for Player Biographies

## Core Principle

**"Unknown" is better than wrong.** Prose prohibitions ("don't fabricate parent names") don't work because LLMs encode the concept they're told to avoid. Decision trees prevent fabrication at generation time by making the path to "Unknown" the explicit, correct default.

## The Methodology Shift

**Old approach (prose rules):** "Do not invent parent names. If a name isn't in reliable sources, say so."
- Result: Agent reads the rule, then fabricates names anyway because the sentence activates the concept.

**New approach (decision trees):** Explicit if/then with "Unknown" as the correct terminal node.
- Result: Agent follows the tree and lands on "Unknown" without ever generating a fabricated name.

## Decision Trees (apply during Phase 2: WRITE)

### Parents (Section 4)
```
Does the Wikipedia infobox contain a "Parent(s)" or "Father"/"Mother" field?
├─ YES → Copy the names exactly as shown
└─ NO → Write "Unknown" for both parents.
         Do not search elsewhere. Do not infer names from the player's surname.
         "Unknown" is the correct and complete answer.
```

### Death (Section 12)
```
Does the Wikipedia infobox contain a "Died" field?
├─ YES → Use that date. Write Section 12.
└─ NO → The player is alive. OMIT Section 12 entirely.
         Set date_of_death=null in DB.
         Do NOT assume death based on age. Old ≠ dead.
```

### Clubs (Section 5)
```
For each club you plan to list:
  Does this club appear in the Transfermarkt career table you scraped?
├─ YES → Include it
└─ NO → Do NOT include it. Even if it "feels right."
         Even if Wikipedia mentions it in passing.
         Transfermarkt career table is ground truth.
```

### Stats (Section 6a)
```
Transfermarkt career table shows apps/goals per competition.
  Copy these EXACTLY. Do not round, adjust, or "reconcile" with Wikipedia.
  If Transfermarkt and Wikipedia disagree, use Transfermarkt and note the discrepancy.
```

### Honours (Section 9)
```
For each honour you plan to list:
  Can you point to the specific source URL where you read about this honour?
├─ YES → Include it
└─ NO → Do NOT include it. Invented honours are a documented hallucination pattern.
```

### Nationality (Section 1 / DB players.nationality)
```
What national team did the player represent internationally?
├─ Clear answer from Wikipedia/Transfermarkt → Use that nationality
├─ Played for country of birth only → Use birth nationality
└─ Born in Country A but represented Country B (e.g., Sheridan: born England, played for Ireland)
   → Use the REPRESENTED nationality, not birth nationality
   → Note birth country separately in place_of_birth
```

Real example: John Sheridan was born in Stretford, England but represented Republic of Ireland internationally. DB nationality should be "Irish", not "English".

### Tournament Results (Section 7)
```
For each tournament result:
  Did you verify the result (winner/loser/score) against the actual tournament page?
├─ YES → Include it
└─ NO → Do NOT guess. Getting a result backwards is a critical error.
```

## Observed Hallucination Patterns (with real examples)

| Pattern | Example | Prevention Decision |
|---|---|---|
| Fabricated parent names | "Johannes Radebe", "Emily Radebe" | Not in Wikipedia infobox → "Unknown" |
| Fabricated death date | Eddie Gray given 2024-11-17 death date | No Wikipedia "Died" field → alive |
| Invented club stint | Radebe at Bolton Wanderers | Not in Transfermarkt career table → excluded |
| Reversed tournament result | "South Africa were 1996 AFCON runners-up" (they WON) | Verify against tournament page |
| Fabricated physical honour | "statue at Elland Road" | No source URL → excluded |
| Duplicate player records | Eddie Gray had 3 DB rows | GET by last_name BEFORE creating |
| Wrong honour_type | `'international'` (violates constraint) | Only `'club'` or `'individual'` |
| Including is_competitive in POST | Triggers 428C9 error | Omit from POST — it's generated |
| "Gold standard" template note | Propagates across bios | Every bio just follows the standard template |
| Wrong nationality | Sheridan marked "English" but represented Ireland | Use international team nationality, not birth country |

## Integration with validate_bio.py

The decision trees are the **prevention layer** (Phase 2). `validate_bio.py` is the **detection layer** (Phase 4). Both are required:

- Decision trees reduce fabrication at generation time
- validate_bio.py catches anything that slips through (duplicates, stats mismatches, schema violations)
- Neither alone is sufficient — the combination is what makes autonomous zero-error operation possible

## Why This Works Better Than Rules

Rules tell the model what NOT to do. Decision trees tell the model exactly WHAT to do at each branch point, with "Unknown" as a valid terminal node — not a failure state. The model never has to "decide" whether to fabricate; the tree routes it to the correct answer before generation begins.
