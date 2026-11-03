---
name: cv-builder
description: Write tailored CV content in English and Polish as structured cv-data JSON (one file per language) from LinkedIn data, confirmed facts and a job analysis. Use when creating or tailoring a CV/resume; rendering is done afterwards by cv-render.
---

# CV content builder

Inputs: `work/linkedin-raw.json`, `%USERPROFILE%/Documents/CV/data/career-facts.md` (persistent across jobs and projects; read it first, append new facts), `work/job-analysis.md` (optional), the improved
texts in `work/linkedin-improvements.md` (if they exist).
Outputs: `work/cv-data.en.json`, then `work/cv-data.pl.json`.

## Steps
1. Write `cv-data.en.json` following the schema below (see `../cv-render/examples/sample-cv.json`).
2. Hand the EN file to the **pl-localizer** subagent → `cv-data.pl.json`.
3. Hand both files plus `job-analysis.md` to the **recruiter-reviewer** subagent. Apply
   the fixes you agree with. Ask the user about fixes that need new facts.
4. Render with the cv-render skill.

## Schema (all fields optional except basics.name)
```json
{
  "lang": "en | pl",
  "basics": {
    "name": "", "headline": "", "email": "", "phone": "", "location": "",
    "links": [{"label": "linkedin.com/in/x", "url": "https://..."}],
    "summary": "3–4 sentences"
  },
  "skills": [{"category": "Languages", "items": ["C++20", "Python"]}],
  "experience": [{
    "title": "", "company": "", "location": "", "start": "03/2021", "end": "",
    "summary": "one-line context (product, domain, team)",
    "highlights": ["achievement bullets, **bold** allowed"],
    "tech": ["C++17", "Linux"]
  }],
  "projects": [{"name": "", "url": "", "description": "", "highlights": [], "tech": []}],
  "education": [{"institution": "", "degree": "", "field": "", "start": "", "end": "", "notes": ""}],
  "certifications": [{"name": "", "issuer": "", "date": ""}],
  "languages": [{"name": "English", "level": "C1"}],
  "extras": [{"title": "Interests", "items": []}],
  "gdpr_clause": "text or omit"
}
```
An empty `end` renders as "Present" or "obecnie".

## Content rules
- Length: max 2 pages. 3–6 bullets for recent roles, 1–2 for old ones. Roles older than ~10 years get one line.
- Bullet format: action verb + scope + measurable result + tech. Put keywords from
  `job-analysis.md` verbatim where they're true.
- Order skills by relevance to the target role. The first category should mirror the ad's must-haves.
- Summary: seniority + years + domain + 2–3 strongest proofs + what you're looking for.
- **Never invent** facts, numbers, employers, dates or skills.
- **Keep the time context honest:** don't present tech from past jobs as current or main (e.g. Linux used at
  an earlier employer must not appear as the current platform). Use the exact project names from career-facts. Leave out anything unconfirmed, or ask.
- No photo, date of birth, marital status or full street address.
- GDPR clause: include it for Polish employers and Polish recruiters (this includes the EN version).
  - PL: "Wyrażam zgodę na przetwarzanie moich danych osobowych dla potrzeb niezbędnych do realizacji procesu rekrutacji zgodnie z Rozporządzeniem Parlamentu Europejskiego i Rady (UE) 2016/679 z dnia 27 kwietnia 2016 r. (RODO)."
  - EN: "I hereby consent to the processing of my personal data for the purposes of the recruitment process in accordance with Regulation (EU) 2016/679 (GDPR)."
