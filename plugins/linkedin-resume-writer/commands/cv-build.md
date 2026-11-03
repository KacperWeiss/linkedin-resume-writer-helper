---
description: End-to-end workflow - LinkedIn export → profile audit → tailored EN + PL CV → PDFs in Documents\CV
argument-hint: "[optional: path to job ad or short target description]"
---

Run the full CV workflow. Talk to the user in their language (default Polish). Work files go to
`work/` and inputs come from `input/` in the current project (create them if missing). Target: $ARGUMENTS

1. **Inputs.** List `input/`. Identify the LinkedIn export ZIP or folder, a profile PDF, and job ads.
   If the export is missing, walk the user through LinkedIn → Settings → Data privacy →
   "Get a copy of your data". Selecting only "Profile" is NOT enough (it gives just Profile.csv).
   Select Positions, Education, Skills, Certifications, Languages, Projects, Recommendations too, or the
   full archive. Fastest alternative: profile page → More → Save to PDF. Then wait.
2. **Parse** with the `linkedin-export-parse` skill → `work/linkedin-raw.json`. Summarise what's there and what's thin.
3. **Target** with the `job-ad-analysis` skill → `work/job-analysis.md`. With no job ad, ask for
   the target role, seniority and market.
4. **Interview + audit** with the `linkedin-profile-audit` skill. Ask about gaps position by position,
   save facts to `%USERPROFILE%/Documents/CV/data/career-facts.md` (persistent across jobs and projects; read it first, append new facts), and produce `work/linkedin-improvements.md`. Pause so the user
   can review and update LinkedIn.
5. **Write** with the `cv-builder` skill → `work/cv-data.en.json`. Then the `pl-localizer` subagent
   → `work/cv-data.pl.json`.
6. **Review** with the `recruiter-reviewer` subagent. Apply agreed fixes and ask the user about the "ASK CANDIDATE" items.
7. **Render** with the `cv-render` skill: both languages × both layouts → `Documents\CV`. Read each
   PDF to verify, then report the file paths.

Pause for user confirmation after steps 2, 4 and 6. Never invent facts.
