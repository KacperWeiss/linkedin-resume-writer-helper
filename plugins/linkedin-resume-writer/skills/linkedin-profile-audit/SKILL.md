---
name: linkedin-profile-audit
description: Audit and improve a LinkedIn profile (headline, About, experience descriptions, skills, featured, settings) based on parsed LinkedIn data and an optional target role, producing ready-to-paste texts. Use when the user wants to update or optimise their LinkedIn before writing a CV.
---

# LinkedIn profile audit

Inputs: `work/linkedin-raw.json` (from linkedin-export-parse), optionally `work/job-analysis.md`.

## Process
1. **Check each section with the user before interviewing.** Go section by section: each
   Experience position, Education, Skills, Certifications, Languages, Projects. Do this for every
   section, including ones that LinkedIn already fills in (e.g. Education). For each one:
   - First summarise what we already know: the facts from `career-facts.md` plus the LinkedIn data.
     Say "nothing yet" if both are empty, and point out obvious gaps (missing dates, no thesis, a thin description).
   - Then ask the user to choose one option (use the AskUserQuestion tool if it is available):
     1. **Use the existing data**: keep it as it is and go to the next section.
     2. **Edit**: change, add or remove specific items. Ask which ones, then apply only those.
     3. **Rewrite from the existing facts**: interview again, using what we already know as the
        starting point and as hints for the questions. Replace the section with the new answers.
     4. **Delete and start over**: drop what we know about this section and interview from scratch.
        Confirm before removing anything from `career-facts.md`.
   - Ask a second question in the same call: **"Don't ask again for the remaining sections"**
     (in Polish: "Nie pytaj ponownie dla następnych sekcji"), yes/no. The tool allows only 4 options
     per question, so this can't be a fifth option. If the user says yes, apply the chosen option to
     every remaining section without asking again. Still show each section's short summary. With
     option 2, still ask what to change in each section. With option 4, list everything that will
     be removed and confirm once. The choice lasts only for this session. If the user later asks to
     choose per section again, go back to asking.
   - In an interview (options 3 and 4, or when there's nothing yet), ask 2–4 targeted questions per batch.
     Experience: scale, latency/throughput numbers, team size, ownership, incidents solved, tech stack.
     Education: school, degree, field, dates, thesis, honours, student research groups, exchanges, unfinished
     or ongoing studies, courses not on LinkedIn, and how much of it to put on the CV.
   Record the results in `%USERPROFILE%/Documents/CV/data/career-facts.md` (persistent across jobs and projects; read it first), one `##` section per area. This file is the single source of truth for CV writing.
2. Produce `work/linkedin-improvements.md`, one section per LinkedIn field, each with:
   - **Current** (verbatim) → **Proposed** (ready to paste) → **Why** (one line).
   - Respect LinkedIn limits: headline ≤ 220 chars, About ≤ 2600 chars, position description ≤ 2000 chars.
3. Fields to cover: Headline, About, each Experience entry, Education, Skills (top 5 pinned + full
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
