# Slow Creator Scout — Documentation
### AI Tooling Assignment | Michael Hirsch | April 1, 2026

---

## Why Case 2

The prompt gave three options. I picked Case 2 because it's the one that actually resonates with how I think about finding creators.

Reddit users yapping behind screen names and scraping a surface-level list of people who attended an event — that's not signal. A podcast appearance is something different. These creators were selected to be on that show for a reason. If Slow trusts the podcast host, we should trust why they're featuring that guest. A 60-minute conversation is an unfiltered founder interview. It's the deepest due diligence signal that exists at the discovery stage.

When I think about the creators I've come across that fit Slow's thesis, they almost always showed up on a podcast first. Knees Over Toes Guy on Joe Rogan told you everything about Ben Patrick's founder mindset before you even looked at his business. The Bentist on Operators with Mike Beckham — he was talking about unit economics and scaling, not content. That's the whole point. You're not just hearing what someone built. You're hearing how they think about it.

That depth of signal doesn't exist in a Reddit username or an event badge. This is the type of storytelling that has the most depth of the three cases, and it maps directly to how Slow actually evaluates people.

---

## The Most Important Question: What Counts as a "Popular" Podcast?

Popularity is not the same as quality and impact. This was the first thing I worked through with Claude when building the tool.

Rick Rubin's Tetragrammaton has at least 10x fewer listens than Call Her Daddy. But the quality of the conversation is completely different. I first learned about Knees Over Toes Guy through Rick Rubin — and Rick tends to have way more niche guests who speak with real depth. Call Her Daddy doesn't have niche guests. The guests are celebrities.

This is where the differentiation lies. The tool I built is sourcing from a completely different body of water than someone who reads the prompt as "find popular podcasts." I chose to interpret it as: **appearances on transcendent podcasts** — shows that go beyond surface-level popularity markers and extract how someone actually thinks.

The podcast list was the most important design decision in this whole exercise.

---

## The 5 Signals

These are the signals Claude looks for in every episode description. Each one maps directly to something Slow has said publicly about what they look for.

**1. Industry Disruption**
Not "doing it better" — attacking something broken in a genuinely novel way. The Bentist didn't make better toothpaste. He declared that 150 years of oral care is built on lies. Knees Over Toes didn't offer better physical therapy. He said conventional knee surgery advice is wrong. That's the level of disruption the tool is looking for.

**2. Hyper-Niche**
A specific vertical with a defined, passionate community. High spend propensity. Not broad lifestyle content. The 250K+ social following threshold exists because below that, the creator hasn't yet proven they can hold a niche audience at scale.

**3. Momentum**
First appearance on a major show in the last year. This is a creator at an inflection point — someone who might actually be looking for capital right now, not someone who peaked three years ago.

**4. Founder Obsession (Riz & Tiz)**
Does this creator think and talk like a founder? Delusional intensity and optimism. They talk about their work like it's a calling, not a job. Systems thinking, market framing, willingness to turn down deals that don't fit the long-term vision.

**5. Flywheel**
Has this creator proven conversion beyond content? Do they sell hardware, software, physical products? Do they have an IRL vertical? An unmonetized audience is a hypothesis. A monetized audience is a business. This is the Slow filter that separates a great storyteller from an actual investment.

Each signal is scored 0–2 per episode. Total out of 10. HIGH priority = 6+.

---

## How It Works

### Step 1 — Feed Parsing
The script uses `feedparser` to pull RSS feeds from the curated podcast list. Each feed returns episode titles, publish dates, and descriptions. The tool filters to the last 12 months and analyzes up to 15 most recent episodes per podcast.

### Step 2 — Signal Analysis (Claude)
Each episode is sent to Claude with a structured prompt grounded in Slow's actual investment thesis. Claude scores the guest against the 5 signals, identifies their niche, writes a summary of why they're interesting, and flags whether a social check is needed.

### Step 3 — Creator Score (Claude, HIGH priority only)
Every HIGH priority guest gets a deeper evaluation using Slow's 6-dimension **Creator Score** framework — built from the Slow Creator Lens:

1. Disruption Angle
2. Community Depth
3. Conversion Proof
4. Operator Signals
5. Category Expansion Logic
6. Franchise Ceiling

Each dimension scored 1–10. Max 60 points. This puts every flagged guest on the same scoring plane as Slow's existing portfolio — JKM scored 47, Tayla Cannon scored 49, Steven Bartlett scored 58.

### Step 4 — Multi-Show Detection
The tool flags any creator who appears on multiple monitored podcasts in the same scan period. Two shows in the same month means something is happening right now.

### Step 5 — Report Output
A plain-text report saved to the Desktop with:
- Summary counts (HIGH/MEDIUM/LOW)
- Multi-show momentum section
- Full breakdown for each flagged creator
- Investment thesis and portfolio comparable for HIGH priority guests
- Next steps checklist

---

## The Podcast List and Why

The list is divided into two buckets. The goal was to maximize signal-to-noise for Slow's specific thesis — not to include the biggest podcasts, but the right ones.

**Creator-Specific** (guests most likely to be in Slow's target range):
- **The Colin and Samir Show** — the premier creator economy podcast; guests are creators actively building businesses
- **Creator Science** — Jay Clouse goes deep on how creators build sustainable business models
- **Creator Economy Live** — industry operators discussing creator business infrastructure
- **The Upload with Rob Balasabas** — niche creator guests building toward the JKM profile

**Founder-Depth** (hosts who extract how people think, not just what they've done):
- **Diary of a CEO** — Steven Bartlett (Slow portfolio) goes deep on mindset and obsession
- **Operators** — founder-to-founder conversations; this is where The Bentist appeared with Mike Beckham
- **How I Built This** — surfaces creators at scale moments, origin story framing
- **My First Million** — business model obsession; guests are builders not performers
- **Tetragrammaton** — Rick Rubin selects guests by instinct; signals cultural and creative depth; where I first encountered Knees Over Toes Guy
- **Modern Wisdom** — Chris Williamson extracts philosophy and process from builders
- **The Knowledge Project** — Shane Parrish on mental models and decision-making
- **Tim Ferriss Show** — deep deconstruction of world-class performers

---

## The Process: How This Was Built

**Stage 1 — Building the plan with Claude**

The first conversation was about what podcasts to source from and what signals to look for. The podcast selection was the most important decision — popularity vs. transcendence. From there, Claude and I mapped the signals directly to Slow's framework and defined what "first appearance" means as a momentum signal.

**Stage 2 — Shipping the tool**

Downloaded Python and set up the Anthropic API. Built `creator_scout.py` — the main script. While building the podcast scanner, I also had Claude build a scoring chart (the Creator Score) so every flagged guest gets evaluated on the same 6-dimension framework Slow uses internally.

**The Slow Creator Lens**

The night before this assignment, I came across the Snailmeal post referencing Slow's public thinking. I used that as the foundation to build `slow-creator-lens.md` — a structured synthesis of Slow's investment thesis grounded in Megan Lightcap's quotes, press releases from the JKM, Tayla Cannon, and Steven Bartlett investments, and Creator CEO Summit recaps. This file is the knowledge base that powers every Claude analysis in the tool. Every scoring decision Claude makes is traceable back to something Slow has said publicly.

---

## The Knowledge Base

`slow-creator-lens.md` was built from:
- Megan Lightcap's interviews and public quotes
- Press releases from the JKM, Tayla Cannon, and Steven Bartlett investments
- Creator CEO Summit I and II recaps
- Slow's published framework content

---

## Files in This Submission

| File | What It Is |
|---|---|
| `creator_scout.py` | The main Python script |
| `slow-creator-lens.md` | Slow's investment framework — knowledge base for Claude prompts |
| `documentation.md` | This file |
| `slow_creator_report_20260330_1339.txt` | Live output report from today's scan |

---

## Running the Tool

**Requirements:**
```
pip install feedparser anthropic
```

**Set your API key** in `creator_scout.py` line 27:
```
ANTHROPIC_API_KEY = "your-key-here"
```

**Run:**
```bash
python3 creator_scout.py
```

The scan takes approximately 20–30 minutes across all 12 podcasts. A report is saved to the Desktop automatically.

---

## What Would Make This Better (v2 Ideas)

- **Automated social verification** — automatically pull follower counts via platform APIs to filter below 250K threshold
- **Historical tracking** — store results in a database and flag when a creator's signal score increases week over week
- **Slack integration** — push HIGH priority alerts to a Slow team channel in real time
- **Full transcript analysis** — when transcript APIs are available, analyze the full conversation not just the description
- **Expanded podcast list** — add niche-specific shows as Slow's thesis expands to athletes and musicians

---

*Built for Slow Ventures Creator Fund by Michael Hirsch, March 2026.*
*Model: Claude Opus 4.6 | Framework: Slow Creator Lens v1*
