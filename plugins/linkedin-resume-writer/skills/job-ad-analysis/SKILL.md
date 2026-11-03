---
name: job-ad-analysis
description: Analyse a target job advertisement (PDF, text, or URL) into must-haves, nice-to-haves, ATS keywords and a candidate gap map. Use before tailoring a CV or LinkedIn profile to a specific role.
---

# Job ad analysis

Input: job ad(s) in `input/` (PDF/TXT) or pasted text or a URL.

Write `work/job-analysis.md` with:

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
- Fill the evidence column only from the LinkedIn data or from what the user said. Never invent experience.
- Keep the ad's original language for keywords. The EN CV keeps them verbatim; the PL CV
  keeps technical terms in English as well.
