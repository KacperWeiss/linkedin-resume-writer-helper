---
name: linkedin-profile-audit
description: Audit and improve a LinkedIn profile (headline, About, experience descriptions, skills, featured, settings) based on parsed LinkedIn data and an optional target role, producing ready-to-paste texts. Use when the user wants to update or optimise their LinkedIn before writing a CV.
---

# LinkedIn profile audit

Inputs: `work/linkedin-raw.json` (from linkedin-export-parse), optionally `work/job-analysis.md`.

## Process
1. **Interview first, write second.** For every position with a thin description, ask
   the user 2–4 targeted questions (scale, latency/throughput numbers, team size, ownership,
   incidents solved, tech stack). Ask in batches per position, not one long questionnaire.
   Record answers in `%USERPROFILE%/Documents/CV/data/career-facts.md` (persistent across jobs and projects; read it first, append new facts). This file is the single source of truth for CV writing.
2. Produce `work/linkedin-improvements.md`, one section per LinkedIn field, each with:
   - **Current** (verbatim) → **Proposed** (ready to paste) → **Why** (one line).
   - Respect LinkedIn limits: headline ≤ 220 chars, About ≤ 2600 chars, position description ≤ 2000 chars.
3. Fields to cover: Headline, About, each Experience entry, Skills (top 5 pinned + full
   list ordered by target relevance), Featured, Open to Work / recruiter settings, custom URL,
   profile language(s). LinkedIn supports a secondary-language profile; suggest a PL version
   if the user targets Polish recruiters.

## Writing rules
- Headline: role + specialisation + 2–3 strongest keywords. No "Looking for opportunities".
- About: first person, 3 short paragraphs (what I do / proof with numbers / what I'm looking for), then a keyword line.
- Experience bullets: action verb + what + measurable result ("Cut order-entry latency p99
  from 40µs to 12µs by …"). Use numbers only when the user confirmed them.
- No fabricated metrics, employers, titles or dates. If unsure, ask.

## Applying changes
The user pastes changes into LinkedIn themselves, unless a browser tool (Claude in Chrome) is
connected **and** the user approves each field individually. Then edit one field at a
time and show it before saving.
