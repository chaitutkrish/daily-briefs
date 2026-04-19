#!/usr/bin/env python3
"""
Daily Content Briefings Generator
Runs every day at 6 AM via GitHub Actions.
Produces two text files — AI brief and Mythology brief.
Uses Claude API (Anthropic) to write in narrator/creator style.
Falls back to scrape-only mode if no API key available.
"""

import os, sys, re, ssl, json, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path

DATE      = datetime.now().strftime("%B %d, %Y")
DATE_SLUG = datetime.now().strftime("%Y-%m-%d")
OUT_DIR   = Path(__file__).parent / "output"
OUT_DIR.mkdir(exist_ok=True)

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode    = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── HTTP helper ───────────────────────────────────────────────────────────────
def fetch(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  [fetch] {url} → {e}")
        return ""

def clean(html):
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<style[^>]*>.*?</style>',  '', html, flags=re.S)
    html = re.sub(r'<[^>]+>', ' ', html)
    html = re.sub(r'&amp;', '&', html)
    html = re.sub(r'&nbsp;', ' ', html)
    html = re.sub(r'&lt;',  '<', html)
    html = re.sub(r'&gt;',  '>', html)
    html = re.sub(r'[ \t]+', ' ', html)
    lines = [l.strip() for l in html.splitlines() if len(l.strip()) > 40]
    return "\n".join(lines[:120])


# ── AI NEWS SOURCES ───────────────────────────────────────────────────────────
AI_SOURCES = [
    ("Anthropic News",          "https://www.anthropic.com/news"),
    ("Anthropic Research",      "https://www.anthropic.com/research"),
    ("OpenAI Blog",             "https://openai.com/news/"),
    ("Google DeepMind Blog",    "https://deepmind.google/discover/blog/"),
    ("Google AI Blog",          "https://blog.google/technology/ai/"),
    ("Mistral News",            "https://mistral.ai/news/"),
    ("Meta AI Blog",            "https://ai.meta.com/blog/"),
    ("Hugging Face Blog",       "https://huggingface.co/blog"),
    ("ElevenLabs Blog",         "https://elevenlabs.io/blog"),
    ("Runway Blog",             "https://runwayml.com/research"),
]

# ── MYTHOLOGY REFERENCE SOURCES ───────────────────────────────────────────────
MYTH_SOURCES = [
    ("Britannica Mythology",    "https://www.britannica.com/topic/mythology"),
    ("World History Mythology", "https://www.worldhistory.org/mythology/"),
    ("Sacred Texts Hindu",      "https://www.sacred-texts.com/hin/"),
]

def scrape_ai_news():
    print("  Scraping AI sources...")
    chunks = []
    for name, url in AI_SOURCES:
        html = fetch(url)
        if html:
            text = clean(html)[:2000]
            chunks.append(f"SOURCE: {name}\nURL: {url}\n{text}\n")
            print(f"  ✅  {name}")
        else:
            print(f"  ⚠   {name} — no content")
    return "\n\n".join(chunks)

def scrape_myth_refs():
    print("  Scraping mythology sources...")
    chunks = []
    for name, url in MYTH_SOURCES:
        html = fetch(url)
        if html:
            text = clean(html)[:1500]
            chunks.append(f"SOURCE: {name}\nURL: {url}\n{text}\n")
            print(f"  ✅  {name}")
    return "\n\n".join(chunks)


# ── CLAUDE API CALL ───────────────────────────────────────────────────────────
def claude(system_prompt, user_content, model="claude-opus-4-5"):
    payload = json.dumps({
        "model": model,
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_content}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key":         API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type":      "application/json",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, context=ctx, timeout=180) as r:
        data = json.loads(r.read())
    return data["content"][0]["text"]


# ══════════════════════════════════════════════════════════════════════════════
# AI BRIEFING
# ══════════════════════════════════════════════════════════════════════════════
AI_SYSTEM = """
You are a daily AI briefing writer for a content creator who makes YouTube Shorts and Instagram Reels about AI tools and trends.

Your job:
- Write a daily AI briefing based on the scraped content from official AI company sources provided
- Write in a narrator/creator style — engaging, cinematic, curious, teaching-oriented
- Sound like a smart person briefing another smart person on a fast-moving space
- Do NOT write like a report analyst — no flat corporate phrases
- ALWAYS cite the exact source URL next to each item you reference

Output format (plain text, no markdown headers with #):
---
AI DAILY BRIEF — [DATE]

OPENING: One punchy paragraph — the single biggest AI story today and why it matters

SECTION: Agentic AI and Coding
[items from sources with explanation + video angle + source URL]

SECTION: AI Creator Tools
[items with explanation + video angle + source URL]

SECTION: AI Video and Image Tools
[items with explanation + video angle + source URL]

SECTION: New Model Releases and Features
[items with explanation + video angle + source URL]

SECTION: AI Productivity and Business Tools
[items with explanation + video angle + source URL]

TODAY'S PRIORITY
What to make content about first today — and exactly why

TOP 3 VIDEO IDEAS TODAY
1. [idea with hook + why it works]
2. [idea with hook + why it works]
3. [idea with hook + why it works]
---

Rules:
- Only include items actually found in the scraped sources
- If a source had no new news, skip that company
- Every item must have a source URL
- Write in narration style — someone learning something interesting, not reading a report
- If an item could become a 60-second Short, say so and explain how
""".strip()

def make_ai_brief(scraped):
    print("  Writing AI brief with Claude...")
    user_msg = f"Today is {DATE}.\n\nHere is the scraped content from official AI company sources:\n\n{scraped[:12000]}"
    return claude(AI_SYSTEM, user_msg)


# ══════════════════════════════════════════════════════════════════════════════
# MYTHOLOGY BRIEFING
# ══════════════════════════════════════════════════════════════════════════════
MYTH_SYSTEM = """
You are a daily mythology briefing writer for a content creator who makes YouTube Shorts and Instagram Reels about mythology — primarily Indian mythology, then Greek, Norse, Egyptian, and cross-cultural comparisons.

Your job:
- Write a daily mythology briefing that helps the creator pick the best story to make content about today
- Prioritize Indian mythology first, then expand to other traditions
- Write in a narrator/educator style — cinematic, curious, discovery-oriented
- Make it feel like you are uncovering something, not explaining a textbook
- Every section should feel like it could directly become a voiceover Short

Important honesty:
- There is no clean "trending mythology Shorts feed"
- So this briefing is based on high-interest recurring themes, strong teachable figures, emotionally powerful conflicts, and source-backed mythology
- Be transparent about this — the goal is strong content ideas, not pretend-trending data

Output format (plain text, no markdown headers with #):
---
MYTHOLOGY DAILY BRIEF — [DATE]

OPENING: One punchy paragraph — the single most powerful mythology story to tell today and why

SECTION: Indian Mythology — Tragic Heroes
[characters, their story, why it works as a Short, source tradition]

SECTION: Indian Mythology — Misunderstood Powers
[figures who are commonly misunderstood, the real story, source]

SECTION: Indian Mythology — Divine Dialogues and Decisions
[moments of debate, choice, or revelation in the texts, source]

SECTION: Cross-Myth Comparisons
[interesting parallels across traditions — be precise about which figures and why]

SECTION: Punishment, Prophecy, and Fate
[stories involving curses, boons, prophecy across traditions]

SECTION: Gods with Similar Powers Across Cultures
[precise comparisons, e.g. Indra + Zeus + Thor for thunder — not vague groupings]

For each item include:
- the mythology figure or idea explained in an interesting way
- the source tradition (e.g. Mahabharata, Bhagavad Gita, Rigveda, Poetic Edda, Hesiod's Theogony)
- why it works as short-form content
- how to frame it as a video (hook suggestion)
- reference link if available

TODAY'S PRIORITY
The single best mythology story to make content about today — and exactly why

TOP 3 VIDEO IDEAS TODAY
1. [idea with hook + source + why it works]
2. [idea with hook + source + why it works]
3. [idea with hook + source + why it works]
---

Rules:
- Indian mythology takes priority
- Cross-myth comparisons must be precise — say exactly which figures and which texts
- Source traditions must be named
- Write in narration style — not analytical, not academic
- Every item should feel like it could become a voiceover Short immediately
""".strip()

def make_myth_brief(scraped):
    print("  Writing Mythology brief with Claude...")
    user_msg = (
        f"Today is {DATE}.\n\n"
        f"Here is some reference content from mythology sources:\n\n{scraped[:6000]}\n\n"
        "Now write a full mythology daily briefing following the format. "
        "Use your deep knowledge of Indian, Greek, Norse, and Egyptian mythology. "
        "Prioritize Indian mythology. Include source traditions and reference links where available."
    )
    return claude(MYTH_SYSTEM, user_msg)


# ══════════════════════════════════════════════════════════════════════════════
# FALLBACK: no API key — write structured placeholder
# ══════════════════════════════════════════════════════════════════════════════
def fallback_ai(scraped):
    return f"""AI DAILY BRIEF — {DATE}
(Fallback mode — add ANTHROPIC_API_KEY secret to GitHub to enable Claude-written briefs)

SCRAPED SOURCES TODAY:
{scraped[:3000]}

To enable full AI-written briefings:
1. Go to your GitHub repo → Settings → Secrets → Actions
2. Add secret: ANTHROPIC_API_KEY = your key from console.anthropic.com
"""

def fallback_myth():
    return f"""MYTHOLOGY DAILY BRIEF — {DATE}
(Fallback mode — add ANTHROPIC_API_KEY secret to GitHub to enable Claude-written briefs)

PRIORITY TODAY: Indian Mythology

TOP RECURRING HIGH-INTEREST THEMES:
- Karna (Mahabharata) — tragic hero, loyalty, identity
- Draupadi's humiliation — justice, dharma, divine intervention
- Shiva as destroyer and creator — duality, cosmic balance
- Arjuna's crisis in the Bhagavad Gita — duty vs emotion
- Krishna's Vishwaroopa — the moment of revelation

CROSS-MYTH COMPARISONS (high-interest):
- Thunder gods: Indra (Rigveda) + Zeus (Iliad) + Thor (Poetic Edda)
- Flood myths: Manu (Shatapatha Brahmana) + Noah + Deucalion (Hesiod)
- Trickster figures: Narada + Loki (Prose Edda) + Hermes (Homeric Hymns)

To enable full Claude-written briefings:
1. Go to your GitHub repo → Settings → Secrets → Actions
2. Add secret: ANTHROPIC_API_KEY = your key from console.anthropic.com
"""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    print(f"\n=== Daily Briefs — {DATE} ===\n")

    # 1. Scrape sources
    ai_scraped   = scrape_ai_news()
    myth_scraped = scrape_myth_refs()

    # 2. Generate briefs
    if API_KEY:
        print("\n  Claude API key found — writing smart briefs...")
        try:
            ai_text = make_ai_brief(ai_scraped)
        except Exception as e:
            print(f"  Claude API error (AI brief): {e} — falling back")
            ai_text = fallback_ai(ai_scraped)
        try:
            myth_text = make_myth_brief(myth_scraped)
        except Exception as e:
            print(f"  Claude API error (Myth brief): {e} — falling back")
            myth_text = fallback_myth()
    else:
        print("\n  No ANTHROPIC_API_KEY — using fallback mode")
        ai_text   = fallback_ai(ai_scraped)
        myth_text = fallback_myth()

    # 3. Save files
    ai_path   = OUT_DIR / f"AI_Brief_{DATE_SLUG}.txt"
    myth_path = OUT_DIR / f"Mythology_Brief_{DATE_SLUG}.txt"

    ai_path.write_text(ai_text,   encoding="utf-8")
    myth_path.write_text(myth_text, encoding="utf-8")

    print(f"\n  ✅  {ai_path.name}")
    print(f"  ✅  {myth_path.name}")
    print(f"\nDone.\n")

if __name__ == "__main__":
    main()
