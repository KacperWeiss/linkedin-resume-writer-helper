---
name: job-ad-analysis
description: Analyse a target job advertisement (PDF, text, or URL) into must-haves, nice-to-haves, ATS keywords and a candidate gap map. Use before tailoring a CV or LinkedIn profile to a specific role.
---

# Job ad analysis

Input: a job ad as a file (PDF/TXT, e.g. in `input/`), pasted text or a URL.

Output goes to the CV's folder in the CV library (see the `cv-edit` skill): `<cv>` = `Documents/CV_<FirstLast>/<Company>/<dd.mm.yyyy>`.
If it doesn't exist yet, create it with `cv_store.py new --name ... --company "<company from the ad>" --role ...`.
Keep a copy of the ad there as `job-ad.<ext>` (pasted text or a URL's text → `job-ad.md`, with the URL on top).

Write `<cv>/job-analysis.md` with:

1. **Role snapshot**: title, seniority, location / work mode, contract (B2B/UoP), rate, domain/end client.
2. **Must-haves**: a table with columns `Requirement | Exact keywords (as written in ad) | Evidence in profile | Status (✅ strong / 🟡 weak / ❌ missing)`.
3. **Nice-to-haves**: the same table.
4. **ATS keyword list**: exact phrases to reuse verbatim where they're true (e.g. "C++17", "low-latency",
   "L3 support", "Robot Framework"). Include common synonyms and abbreviations in both forms
   ("CI/CD", "continuous deployment").
5. **Story angles**: 3–5 achievements from the candidate's history that best prove fit.
6. **Questions for the candidate**: concrete gaps to fill. Ask about real experience with
   each ❌/🟡 item. Never assume the candidate has it.

Rules:
- Evidence sources: `<person>/_data/career-facts.md`, `<person>/_data/linkedin-raw.json` and what the user said.
- Fill the evidence column only from the LinkedIn data or from what the user said. Never invent experience.
- Keep the ad's original language for keywords. The EN CV keeps them verbatim; the PL CV
  keeps technical terms in English as well.
