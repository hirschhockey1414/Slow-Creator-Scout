#!/usr/bin/env python3
"""
Slow Creator Scout
==================
Monitors a curated list of founder-depth podcasts for first-time guests
who show signals Slow Ventures looks for in creator investments.

5 Signals:
1. Industry Disruption — attacking something broken in a novel way
2. Hyper-Niche — specific vertical, defined community
3. Momentum — first appearance, something is happening right now
4. Founder Obsession — delusional intensity, talks about work like a calling
5. Flywheel — proven conversion beyond content (hardware, software, IRL vertical)

Usage:
    python3 creator_scout.py
"""

import feedparser
import anthropic
import json
import re
from datetime import datetime, timezone
from collections import defaultdict

# ── API KEY ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"

# ── PODCAST LIST ───────────────────────────────────────────────────────────────
# Curated for founder-depth signal, not popularity.
# These hosts go deep on HOW someone thinks, not just WHAT they've done.
PODCASTS = [
    # Creator-Specific (guests most likely to be in Slow's target range)
    {
        "name": "The Colin and Samir Show",
        "rss": "https://feeds.megaphone.fm/LI6529969937",
        "why": "Premier creator economy podcast — guests are creators building real businesses"
    },
    {
        "name": "Creator Science",
        "rss": "https://feeds.megaphone.fm/TPG4024225475",
        "why": "Jay Clouse goes deep on how creators build sustainable businesses"
    },
    {
        "name": "Creator Economy Live",
        "rss": "https://rss.buzzsprout.com/2438432.rss",
        "why": "Industry operators discussing creator business models"
    },
    {
        "name": "The Upload with Rob Balasabas",
        "rss": "https://anchor.fm/s/125c652c/podcast/rss",
        "why": "Niche creator guests building businesses — Slow's exact target profile"
    },

    # Founder-Depth (hosts extract how people think, not just their resume)
    {
        "name": "Diary of a CEO",
        "rss": "https://rss2.flightcast.com/xmsftuzjjykcmqwolaqn6mdn",
        "why": "Steven Bartlett (Slow portfolio) goes deep on mindset, obsession, and building"
    },
    {
        "name": "Operators",
        "rss": "https://anchor.fm/s/d8c3d8e4/podcast/rss/",
        "why": "Founder-to-founder depth — The Bentist appeared here discussing his business"
    },
    {
        "name": "How I Built This",
        "rss": "https://feeds.npr.org/510313/podcast.xml",
        "why": "Origin stories and founder mindset — surfaces creators at scale moments"
    },
    {
        "name": "My First Million",
        "rss": "https://feeds.megaphone.fm/HS2300184645",
        "why": "Business model obsession — guests are builders, not performers"
    },
    {
        "name": "Tetragrammaton with Rick Rubin",
        "rss": "https://feeds.megaphone.fm/tetragrammaton",
        "why": "Rick selects guests from his own instinct — signals cultural and creative depth"
    },
    {
        "name": "Modern Wisdom",
        "rss": "https://feeds.megaphone.fm/SIXMSB5088139739",
        "why": "Chris Williamson extracts philosophy and process from builders"
    },
    {
        "name": "The Knowledge Project",
        "rss": "https://feeds.megaphone.fm/FSMI7575968096",
        "why": "Shane Parrish focuses on mental models and how people make decisions"
    },
    {
        "name": "Tim Ferriss Show",
        "rss": "https://rss.art19.com/tim-ferriss-show",
        "why": "Deep deconstruction of world-class performers — signals obsession and process"
    },
]

# ── CLAUDE ANALYSIS PROMPT ─────────────────────────────────────────────────────
ANALYSIS_PROMPT = """You are a scout for Slow Ventures Creator Fund, a $60M fund that invests $1-3M into creator-entrepreneurs building real businesses on top of their audiences.

You are analyzing a podcast episode to determine if the guest is someone Slow Ventures should investigate as a potential investment.

SLOW'S INVESTMENT THESIS:
- "Distribution precedes product" — creators build audience first, then layer products on top
- Trust has shifted from institutions to individuals — creators are the beneficiaries
- They invest in holding companies, not specific products
- Target: $100-200M revenue potential businesses
- "Our capital is for 1% of creators" — extremely selective

THE 5 SIGNALS TO LOOK FOR:

1. INDUSTRY DISRUPTION
Is this creator attacking their industry in a genuinely novel, unconventional way?
Not just "doing it better" but making the old model look broken.
Examples: The Bentist declaring 150 years of oral care is built on lies. Knees Over Toes Guy saying conventional knee surgery advice is wrong.
Look for: language about broken systems, incumbent failures, "nobody is doing this right"

2. HYPER-NICHE
Is this creator deeply embedded in a specific vertical with a defined, passionate community?
Not broad lifestyle content — a specific, obsessive niche.
Look for: specific skill, hobby, profession, or knowledge domain. High audience spend propensity.

3. MOMENTUM
Is something happening RIGHT NOW with this creator?
First appearances on major podcasts signal a creator is at an inflection point.
Look for: recent product launch, revenue milestone, team expansion, viral moment, book deal

4. FOUNDER OBSESSION (Riz & Tiz)
Does this creator think and talk like a founder, not just a content creator?
Delusional intensity and optimism — they talk about their work like it's a calling, not a job.
Look for: systems thinking, market framing, team building, turning down deals that don't fit the vision

5. FLYWHEEL
Has this creator proven conversion beyond content?
Do they sell hardware, software, physical products, or have an IRL vertical?
An unmonetized audience is a hypothesis. A monetized audience is a business.
Look for: product launches, e-commerce, subscription businesses, software, physical retail

---

EPISODE TO ANALYZE:
Podcast: {podcast_name}
Episode Title: {title}
Published: {published}
Description: {description}

---

INSTRUCTIONS:
1. Extract the guest name from the episode title/description (if it's an interview episode)
2. If this is NOT an interview episode (no clear guest, solo host episode, news recap), set is_interview to false
3. Score each of the 5 signals: 0 (not present), 1 (weak signal), 2 (strong signal)
4. Calculate total score out of 10
5. Flag as HIGH PRIORITY if total >= 6, MEDIUM if 4-5, LOW if < 4

YOU MUST respond with ONLY valid JSON in this exact format, no other text:
{{
  "guest_name": "Full Name or UNKNOWN",
  "is_interview": true,
  "signal_scores": {{
    "industry_disruption": 0,
    "hyper_niche": 0,
    "momentum": 0,
    "founder_obsession": 0,
    "flywheel": 0
  }},
  "total_score": 0,
  "priority": "HIGH",
  "key_signals": "2-3 sentence summary of why this person is interesting.",
  "niche": "What specific niche does this creator operate in?",
  "social_check_needed": true
}}"""

# ── CREATOR SCORE PROMPT ───────────────────────────────────────────────────────
CREATOR_SCORE_PROMPT = """You are evaluating a creator for Slow Ventures Creator Fund using the Slow Creator Lens.

CREATOR INFO:
Name: {guest_name}
Podcast: {podcast_name}
Episode: {title}
Description: {description}
Initial Signal Score: {signal_score}/10

Score this creator across 6 dimensions (each 1-10, max 60 total):

1. DISRUPTION ANGLE: How novel is their attack on the industry?
2. COMMUNITY DEPTH: How deeply attached is the audience to what they've built?
3. CONVERSION PROOF: Have they sold something to their audience? (1-3=no product, 7-9=real revenue, 10=sold out repeatedly)
4. OPERATOR SIGNALS: Do they think like a founder? (1-3=just content, 10=vertically integrated multi-business)
5. CATEGORY EXPANSION: Can the brand grow beyond the first product?
6. FRANCHISE CEILING: What is the realistic $ ceiling? (1-3=$1-10M, 7-9=$50-200M, 10=$200M+)

YOU MUST respond with ONLY valid JSON in this exact format, no other text:
{{
  "creator_score": {{
    "disruption_angle": 7,
    "community_depth": 7,
    "conversion_proof": 7,
    "operator_signals": 7,
    "category_expansion": 7,
    "franchise_ceiling": 7,
    "total": 42
  }},
  "investment_thesis": "2-3 sentences on why Slow should or should not pursue this creator.",
  "comparable": "Which Slow portfolio creator does this most resemble and why?"
}}"""


def parse_date(entry):
    """Parse published date from feed entry."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        try:
            return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        except:
            return None
    return None


def is_within_last_year(dt):
    """Check if a datetime is within the last 12 months."""
    if not dt:
        return False
    now = datetime.now(timezone.utc)
    delta = now - dt
    return delta.days <= 365


def extract_text(entry):
    """Extract title and description from a feed entry."""
    title = entry.get('title', '')
    summary = entry.get('summary', '') or entry.get('description', '')
    summary = re.sub(r'<[^>]+>', ' ', summary)
    summary = re.sub(r'\s+', ' ', summary).strip()
    return title, summary[:2000]


def extract_json(text):
    """Robustly extract JSON from Claude's response."""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # Find the outermost JSON object using bracket matching
    start = text.find('{')
    if start == -1:
        return None

    depth = 0
    for i, char in enumerate(text[start:], start):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i+1])
                except:
                    return None
    return None


def analyze_episode(client, podcast_name, title, description, published_str):
    """Send episode to Claude for signal analysis."""
    prompt = ANALYSIS_PROMPT.format(
        podcast_name=podcast_name,
        title=title,
        published=published_str,
        description=description
    )

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()
    return extract_json(response_text)


def score_creator(client, guest_name, podcast_name, title, description, signal_score):
    """Run full Creator Score on a flagged guest."""
    prompt = CREATOR_SCORE_PROMPT.format(
        guest_name=guest_name,
        podcast_name=podcast_name,
        title=title,
        description=description,
        signal_score=signal_score
    )

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()
    return extract_json(response_text)


def check_multi_show_appearances(all_guests):
    """Flag creators appearing on multiple shows — elevated signal."""
    name_to_shows = defaultdict(list)
    for guest in all_guests:
        name = guest.get('guest_name', '')
        if name and name != 'UNKNOWN':
            name_to_shows[name.lower()].append(guest['podcast'])
    return {name: shows for name, shows in name_to_shows.items() if len(shows) > 1}


TOP_PICKS_PROMPT = """You are a partner at Slow Ventures Creator Fund, a $60M fund that invests $1-3M into creator-entrepreneurs building real businesses on top of their audiences.

You have just completed a scan of founder-depth podcasts and identified the following HIGH priority creators. Your job is to select the 3-5 who are the best fit for Slow to actually pursue — not just the highest scorers, but the ones who genuinely match Slow's thesis of backing creator-entrepreneurs with niche audiences, proven conversion, and $100-200M franchise potential.

SLOW'S INVESTMENT CRITERIA:
- Creator-first: builds audience before business, not a traditional founder who happens to podcast
- Niche community with deep attachment (skill, identity, or transformation — not entertainment)
- Proven flywheel: has sold something to their audience (physical products, software, IRL vertical)
- Founder mindset: thinks like an operator, not just a content creator
- Franchise ceiling: realistic path to $100-200M revenue

HIGH PRIORITY CREATORS FROM THIS SCAN:
{creator_summaries}

Select the 3-5 creators Slow should pursue first. For each, give:
1. Why they are the best fit for Slow specifically
2. What the investment thesis would be
3. What to verify before reaching out

Be direct and opinionated. Slow's capital is for 1% of creators.

YOU MUST respond with ONLY valid JSON in this exact format:
{{
  "top_picks": [
    {{
      "name": "Creator Name",
      "rank": 1,
      "why_slow": "2-3 sentences on why this is a Slow investment specifically.",
      "thesis": "1-2 sentence investment thesis.",
      "verify_first": "What to check before reaching out."
    }}
  ],
  "passed_on": "1-2 sentences on why the remaining HIGH priority creators were not selected."
}}"""


def select_top_picks(client, high_priority_flagged):
    """Send all HIGH priority creators to Claude for final comparative ranking."""
    if not high_priority_flagged:
        return None

    summaries = []
    for f in high_priority_flagged:
        cs = f.get('creator_score', {})
        s = cs.get('creator_score', {}) if cs else {}
        total = s.get('total', '?')
        thesis = cs.get('investment_thesis', '') if cs else ''
        summaries.append(
            f"- {f.get('guest_name', 'Unknown')} | {f.get('podcast')} | "
            f"Signal: {f.get('total_score', 0)}/10 | Creator Score: {total}/60 | "
            f"Niche: {f.get('niche', 'Unknown')} | "
            f"Thesis: {thesis[:200]}"
        )

    prompt = TOP_PICKS_PROMPT.format(creator_summaries="\n".join(summaries))

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text.strip()
    return extract_json(response_text)


def format_report(flagged, multi_show_guests, top_picks=None):
    """Format the final weekly report."""
    now = datetime.now()
    report = []
    report.append("=" * 70)
    report.append("SLOW CREATOR SCOUT — WEEKLY REPORT")
    report.append(f"Generated: {now.strftime('%B %d, %Y at %I:%M %p')}")
    report.append("=" * 70)
    report.append("")

    high_priority = [f for f in flagged if f.get('priority') == 'HIGH']
    medium_priority = [f for f in flagged if f.get('priority') == 'MEDIUM']

    report.append(f"SUMMARY: {len(high_priority)} HIGH PRIORITY | {len(medium_priority)} MEDIUM PRIORITY")
    report.append(f"Multi-show appearances: {len(multi_show_guests)} creators flagged")
    report.append("")

    if top_picks and top_picks.get('top_picks'):
        report.append("⭐ TOP PICKS — SLOW SHOULD PURSUE THESE FIRST")
        report.append("-" * 50)
        for pick in top_picks['top_picks']:
            report.append(f"\n  #{pick.get('rank', '?')} {pick.get('name', 'Unknown')}")
            report.append(f"  Why Slow: {pick.get('why_slow', '')}")
            report.append(f"  Thesis: {pick.get('thesis', '')}")
            report.append(f"  Verify first: {pick.get('verify_first', '')}")
        if top_picks.get('passed_on'):
            report.append(f"\n  Passed on: {top_picks['passed_on']}")
        report.append("")

    if multi_show_guests:
        report.append("⚡ MULTI-SHOW MOMENTUM (appeared on 2+ podcasts this year)")
        report.append("-" * 50)
        for name, shows in multi_show_guests.items():
            report.append(f"  • {name.title()} — {', '.join(shows)}")
        report.append("")

    if high_priority:
        report.append("🔴 HIGH PRIORITY CREATORS")
        report.append("-" * 50)
        for f in high_priority:
            report.append(f"\n  GUEST: {f.get('guest_name', 'Unknown')}")
            report.append(f"  Podcast: {f.get('podcast')} | {f.get('published', '')}")
            report.append(f"  Episode: {f.get('title', '')}")
            report.append(f"  Niche: {f.get('niche', 'Unknown')}")
            report.append(f"  Signal Score: {f.get('total_score', 0)}/10")
            scores = f.get('signal_scores', {})
            report.append(f"  Signals: Disruption({scores.get('industry_disruption',0)}) | "
                         f"Niche({scores.get('hyper_niche',0)}) | "
                         f"Momentum({scores.get('momentum',0)}) | "
                         f"Founder({scores.get('founder_obsession',0)}) | "
                         f"Flywheel({scores.get('flywheel',0)})")
            report.append(f"  Why: {f.get('key_signals', '')}")

            if f.get('creator_score'):
                cs = f['creator_score']
                s = cs.get('creator_score', {})
                report.append(f"  Creator Score: {s.get('total', '?')}/60")
                report.append(f"  → Disruption:{s.get('disruption_angle','?')} "
                             f"Community:{s.get('community_depth','?')} "
                             f"Conversion:{s.get('conversion_proof','?')} "
                             f"Operator:{s.get('operator_signals','?')} "
                             f"Expansion:{s.get('category_expansion','?')} "
                             f"Ceiling:{s.get('franchise_ceiling','?')}")
                report.append(f"  Thesis: {cs.get('investment_thesis', '')}")
                report.append(f"  Comparable: {cs.get('comparable', '')}")

            report.append(f"  ⚠ Social check needed (250K+ threshold): {f.get('social_check_needed', True)}")

    if medium_priority:
        report.append("\n🟡 MEDIUM PRIORITY CREATORS")
        report.append("-" * 50)
        for f in medium_priority:
            report.append(f"\n  GUEST: {f.get('guest_name', 'Unknown')}")
            report.append(f"  Podcast: {f.get('podcast')} | {f.get('published', '')}")
            report.append(f"  Niche: {f.get('niche', 'Unknown')}")
            report.append(f"  Signal Score: {f.get('total_score', 0)}/10")
            report.append(f"  Why: {f.get('key_signals', '')}")

    report.append("")
    report.append("=" * 70)
    report.append("NEXT STEPS FOR HIGH PRIORITY CREATORS:")
    report.append("1. Verify social following (250K+ threshold on primary platform)")
    report.append("2. Check if creator has appeared on any Slow-monitored podcast before")
    report.append("3. Search for product/business evidence beyond content")
    report.append("4. Run full Slow Creator Lens evaluation")
    report.append("=" * 70)

    return "\n".join(report)


def main():
    print("\n" + "="*60)
    print("SLOW CREATOR SCOUT")
    print("Scanning founder-depth podcasts for creator investment leads")
    print("="*60 + "\n")

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    all_flagged = []
    all_guests_for_multishow = []
    episodes_analyzed = 0

    for podcast in PODCASTS:
        print(f"📡 Scanning: {podcast['name']}...")

        try:
            feed = feedparser.parse(podcast['rss'])
        except Exception as e:
            print(f"   ⚠ Could not fetch feed: {e}")
            continue

        if not feed.entries:
            print(f"   ⚠ No episodes found — RSS may be incorrect")
            continue

        recent_episodes = []
        for entry in feed.entries:
            pub_date = parse_date(entry)
            if is_within_last_year(pub_date):
                recent_episodes.append((entry, pub_date))

        print(f"   Found {len(recent_episodes)} episodes in the last 12 months")

        # Analyze up to 15 most recent episodes per podcast
        for entry, pub_date in recent_episodes[:15]:
            title, description = extract_text(entry)
            published_str = pub_date.strftime('%B %d, %Y') if pub_date else 'Unknown date'

            try:
                result = analyze_episode(
                    client,
                    podcast['name'],
                    title,
                    description,
                    published_str
                )

                if not result:
                    continue

                if not result.get('is_interview', False):
                    continue

                episodes_analyzed += 1
                result['podcast'] = podcast['name']
                result['title'] = title
                result['published'] = published_str

                all_guests_for_multishow.append(result)

                priority = result.get('priority', 'LOW')

                if priority in ['HIGH', 'MEDIUM']:
                    print(f"   ✅ {priority}: {result.get('guest_name', 'Unknown')} — Score: {result.get('total_score', 0)}/10")

                    if priority == 'HIGH':
                        print(f"      Running Creator Score...")
                        creator_score = score_creator(
                            client,
                            result.get('guest_name', 'Unknown'),
                            podcast['name'],
                            title,
                            description,
                            result.get('total_score', 0)
                        )
                        result['creator_score'] = creator_score

                    all_flagged.append(result)
                else:
                    print(f"   — LOW: {result.get('guest_name', 'Unknown')}")

            except Exception as e:
                print(f"   ⚠ Error on '{title[:40]}': {e}")
                continue

    multi_show = check_multi_show_appearances(all_guests_for_multishow)

    high_priority_flagged = [f for f in all_flagged if f.get('priority') == 'HIGH']
    print(f"\nRunning Top Picks selection across {len(high_priority_flagged)} HIGH priority creators...")
    top_picks = select_top_picks(client, high_priority_flagged)

    print(f"\n{'='*60}")
    print(f"SCAN COMPLETE")
    print(f"Episodes analyzed: {episodes_analyzed}")
    print(f"Creators flagged: {len(all_flagged)}")
    print(f"Multi-show creators: {len(multi_show)}")
    print(f"{'='*60}\n")

    report = format_report(all_flagged, multi_show, top_picks)
    print(report)

    report_filename = f"/Users/michaelhirsch/Desktop/slow_creator_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(report_filename, 'w') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {report_filename}")


if __name__ == "__main__":
    main()
