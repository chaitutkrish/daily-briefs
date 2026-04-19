# Daily Content Briefs — Claude Context

## What this repo does
Generates two text briefings every day at 6 AM EST via GitHub Actions:
- `output/AI_Brief_YYYY-MM-DD.txt`
- `output/Mythology_Brief_YYYY-MM-DD.txt`

## Style rules (DO NOT change without asking)

### Both briefs must:
- Be written in narrator style — not analyst, not academic
- Feel like a smart creator briefing another creator
- Sound like it could be read as a voiceover immediately
- Use category-based sections for easy scanning
- Avoid flat phrases like "strong signal" without explanation
- Always cite sources with URLs

### AI Brief:
- Fetch from official primary sources only (Anthropic, OpenAI, Google DeepMind, Meta AI, Mistral, HuggingFace, ElevenLabs, Runway)
- Label any secondary source clearly
- Sections: Agentic AI, Creator Tools, Video Tools, Model Releases, Productivity
- End with: Today's Priority + Top 3 Video Ideas

### Mythology Brief:
- Indian mythology is ALWAYS first priority
- Then Greek, Norse, Egyptian, cross-cultural comparisons
- No pretend "trending" data — honest about being curated, not live-scraped
- Must cite source tradition (Mahabharata, Bhagavad Gita, Rigveda, Poetic Edda, etc.)
- Cross-myth comparisons must be precise (Indra + Zeus + Thor, not vague groupings)
- Sections: Tragic Heroes, Misunderstood Powers, Divine Dialogues, Cross-Myth Comparisons, Fate and Prophecy
- End with: Today's Priority + Top 3 Video Ideas

## Output rules
- Text files only
- No PDF unless explicitly requested
- Save to `output/` folder
- One file per brief per day

## GitHub Actions schedule
- Runs daily at 6 AM EST (11:00 UTC)
- Can be triggered manually via GitHub Actions UI

## Secrets required
- `ANTHROPIC_API_KEY` — set in GitHub repo Settings → Secrets → Actions
