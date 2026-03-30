# Slow Creator Scout — Documentation
### AI Tooling Assignment | Michael Hirsch | April 1, 2026

---

## What This Is

**Slow Creator Scout** is a Python tool that monitors a curated list of founder-depth podcasts and surfaces creator-entrepreneurs who match Slow Ventures' investment thesis — before they become obvious.

The insight behind it: Slow's target creators don't show up on "Top Influencer" lists. They show up on podcasts like *How I Built This* or *Creator Science* talking about the business they're building. The moment a niche creator gets invited onto one of these shows is often the moment they're at an inflection point — and the moment Slow should be paying attention.

This tool automates that scan. Every week, it reads the latest episodes from 12 curated podcasts, sends each one to Claude for signal analysis, flags the strongest matches, and outputs a prioritized report.

---

## How It Works

### Step 1 — Feed Parsing
The script uses `feedparser` to pull RSS feeds from 12 podcasts. Each feed returns episode titles, publish dates, and descriptions going back 12 months. The tool filters to the last 12 months and analyzes up to 15 most recent episodes per podcast.

### Step 2 — Signal Analysis (Claude)
Each episode is sent to Claude with a structured prompt grounded in Slow's actual investment thesis. Claude evaluates each guest against **5 signals**:

| Signal | What It Catches |
|---|---|
| **Industry Disruption** | Creator attacking something broken, not just doing it better |
| **Hyper-Niche** | Deep vertical with defined, passionate community |
| **Momentum** | First appearance on a major show = inflection point |
| **Founder Obsession** | Talks about work like a calling, not a job |
| **Flywheel** | Proven conversion: hardware, software, physical products, IRL vertical |

Each signal is scored 0–2. Total score out of 10:
- **HIGH PRIORITY:** 6–10
- **MEDIUM:** 4–5
- **LOW:** < 4

### Step 3 — Creator Score (Claude, HIGH priority only)
Every HIGH priority guest gets a deeper evaluation using Slow's 6-dimension **Creator Score** framework (from the Slow Creator Lens):

1. Disruption Angle
2. Community Depth
3. Conversion Proof
4. Operator Signals
5. Category Expansion Logic
6. Franchise Ceiling

Each dimension scored 1–10. Max 60 points. This puts the guest on the same scoring plane as Slow's existing portfolio — JKM scored 47, Tayla Cannon scored 49, Steven Bartlett scored 58.

### Step 4 — Multi-Show Detection
The tool flags any creator who appears on multiple monitored podcasts in the same scan period. Appearing on 2+ shows simultaneously is a strong momentum signal — something is happening.

### Step 5 — Report Output
Saves a plain-text report to the Desktop with:
- Summary counts (HIGH/MEDIUM/LOW)
- Multi-show momentum section
- Full breakdown for each flagged creator
- Investment thesis and comparable portfolio match for HIGH priority guests
- Next steps checklist

---

## The 12 Podcasts and Why

The list was built to maximize signal-to-noise for Slow's specific thesis: niche creators building real businesses. These shows are divided into two buckets:

**Creator-Specific** (guests most likely to be in Slow's target range):
- **The Colin and Samir Show** — the premier creator economy podcast; guests are creators actively building businesses
- **Creator Science** — Jay Clouse goes deep on how creators build sustainable business models
- **Creator Economy Live** — industry operators discussing creator business infrastructure
- **The Upload with Rob Balasabas** — niche creator guests building toward the JKM profile

**Founder-Depth** (hosts who extract how people think, not just what they've done):
- **Diary of a CEO** — Steven Bartlett (Slow portfolio company) goes deep on mindset and obsession
- **Operators** — founder-to-founder conversations; The Bentist appeared here
- **How I Built This** — surfaces creators at scale moments, origin story framing
- **My First Million** — business model obsession; guests are builders not performers
- **Tetragrammaton** — Rick Rubin selects guests by instinct, signals cultural depth
- **Modern Wisdom** — Chris Williamson extracts philosophy and process from builders
- **The Knowledge Project** — Shane Parrish on mental models and decision-making
- **Tim Ferriss Show** — deep deconstruction of world-class performers

---

## Why This Approach Works for Slow

Megan Lightcap has described her sourcing workflow as "long tail searches on articles to surface creators building social-first businesses." This tool is the systematic version of that — except instead of articles, it scans the conversations where creators reveal exactly how they think about their businesses.

The key insight: podcast episode titles and descriptions already contain the signal. A title like *"How I Turned My YouTube Channel Into a $6M Tool Business"* or *"Building the First Science-Backed Oral Care Brand"* is a lead. Claude reads thousands of these per scan and surfaces the ones that match Slow's actual investment criteria.

This scales what one person can realistically review in a week from ~20 episodes to 180+ episodes across 12 shows.

---

## The Knowledge Base

The Claude prompts are grounded in `slow-creator-lens.md` — a structured synthesis of Slow's public investment thesis built from:
- Megan Lightcap's interviews and quotes
- Press releases from JKM, Tayla Cannon, and Steven Bartlett investments
- Creator CEO Summit I and II recaps
- Slow's published framework content

This means every analysis decision Claude makes is traceable back to something Slow has actually said publicly.

---

## Files in This Submission

| File | What It Is |
|---|---|
| `creator_scout.py` | The main Python script |
| `slow-creator-lens.md` | Slow's investment framework — knowledge base for Claude prompts |
| `documentation.md` | This file |
| `slow_creator_report_[date].txt` | Sample output report from a live scan |

---

## Running the Tool

**Requirements:**
```
pip install feedparser anthropic
```

**Set your API key** in `creator_scout.py` line 27, or use an environment variable:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Run:**
```bash
python3 creator_scout.py
```

The scan takes approximately 5–15 minutes depending on episode volume. A report is saved to the Desktop automatically.

---

## What Would Make This Better (v2 Ideas)

- **Automated social verification** — after flagging a creator, automatically pull their follower counts via platform APIs to filter below 250K threshold
- **Historical tracking** — store results in a database and flag when a creator's signal score increases week over week
- **Slack integration** — push HIGH priority alerts to a Slow team channel in real time
- **Expanded podcast list** — add more niche-specific shows as Slow's thesis expands to athletes and musicians
- **Full transcript analysis** — when transcript APIs are available, analyze the full conversation not just the description

---

*Built for Slow Ventures Creator Fund by Michael Hirsch, March 2026.*
*Model: Claude Opus 4.6 | Framework: Slow Creator Lens v1*
