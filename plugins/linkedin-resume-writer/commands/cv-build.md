---
description: End-to-end workflow - LinkedIn export → profile audit → tailored EN + PL CV → PDFs in Documents\CV_<FirstLast>\<Company|Ogólne>\<dd.mm.yyyy>
argument-hint: "[optional: path to job ad or short target description]"
---

Run the full CV workflow. Talk to the user in their language (default Polish). Target: $ARGUMENTS

Everything is saved in the CV library in the Windows Documents folder (layout and helper script
`cv_store.py`: see the `cv-edit` skill). `<person>` = `Documents/CV_<FirstLast>`, `<cv>` = this CV's folder
`<person>/<Company>/<dd.mm.yyyy>` or `<person>/Ogólne/<dd.mm.yyyy>`. Nothing is written to the project folder.
If the user wants to change a CV that already exists, use the `cv-edit` skill instead of this workflow.

1. **Inputs.** Look for inputs where the user points, otherwise in `input/` of the current folder: the LinkedIn
   export ZIP or folder, a profile PDF, job ads. Run `cv_store.py people`: if the person folder already has
   `_data/linkedin-raw.json` and `_data/career-facts.md`, offer to reuse them instead of a new export. If
   `legacy_career_facts` is reported, offer the migration described in the `cv-edit` skill first.
   If the export is missing, walk the user through LinkedIn → Settings → Data privacy →
   "Get a copy of your data". Selecting only "Profile" is NOT enough (it gives just Profile.csv).
   Select Positions, Education, Skills, Certifications, Languages, Projects, Recommendations too, or the
   full archive. Fastest alternative: profile page → More → Save to PDF. Then wait.
2. **Parse** with the `linkedin-export-parse` skill → `<person>/_data/linkedin-raw.json`. Summarise what's there and what's thin.
3. **Target.** Ask who the CV is for if it isn't clear: the company from the job ad (or none → `Ogólne`), the role,
   and optionally a contact (recruiter or person it will be sent to). Create the folder:
   `cv_store.py new --name "<First Last>" --company "<Company>" --role "<role>" --contact "<who>" --job-ad "<source>"`
   (omit `--company` for a general CV). Copy the job ad into `<cv>` as `job-ad.<ext>` (or save pasted text /
   the URL's text as `job-ad.md`). Then run the `job-ad-analysis` skill → `<cv>/job-analysis.md`. With no job ad,
   ask for the target role, seniority and market and note them in `job-analysis.md`.
4. **Interview + audit** with the `linkedin-profile-audit` skill. For each section (positions, education,
   skills, etc.) summarise what is known and let the user choose: use it, edit it, rewrite it or start over.
   Save facts to `<person>/_data/career-facts.md` (persistent across CVs; read it first), and produce
   `<cv>/linkedin-improvements.md`. Pause so the user can review and update LinkedIn.
5. **Write** with the `cv-builder` skill → `<cv>/cv-data.en.json`. Then the `pl-localizer` subagent
   → `<cv>/cv-data.pl.json`.
6. **Review** with the `recruiter-reviewer` subagent and save its findings to `<cv>/review.md`. Apply agreed
   fixes and ask the user about the "ASK CANDIDATE" items.
7. **Render** with the `cv-render` skill: both languages × both layouts → `<cv>`. Read each PDF to verify,
   run `cv_store.py log "<cv>" "rendered"`, then report the folder and the file paths.

Pause for user confirmation after steps 2, 4 and 6. Never invent facts.
