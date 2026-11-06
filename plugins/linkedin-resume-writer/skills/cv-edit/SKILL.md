---
name: cv-edit
description: Find and modify a CV created earlier, from any working folder, e.g. "Zmodyfikujmy moją ostatnią CV dla Google", "Chcę wprowadzić zmiany w CV napisanym dla Szymona", "edit my latest CV", "retarget my Google CV to Amazon". Also manages the CV library in Documents (CV_<FirstLast>/<Company|Ogólne>/<dd.mm.yyyy>) that every other skill in this plugin writes to.
---

# Edit an existing CV

Talk to the user in their language (default Polish). All commands below run from this skill's base directory.

## The CV library
Everything lives in the Windows Documents folder, so it works from any working directory:
```
Documents/CV_<FirstLast>/
  _data/career-facts.md        confirmed facts, shared by all of this person's CVs
  _data/linkedin-raw.json      parsed LinkedIn export (+ _data/sources/ with the original files)
  <Company>/<dd.mm.yyyy>/      one CV per job ad   (same day twice → dd.mm.yyyy_2)
  Ogólne/<dd.mm.yyyy>/         a CV without a specific job ad
    cv-meta.json  job-ad.*  job-analysis.md  linkedin-improvements.md  review.md
    cv-data.en.json  cv-data.pl.json  CV_<Name>_<EN|PL>_<ATS|Modern>.pdf
```
`cv-meta.json` records the person, company, role, contact (the recruiter or person the CV was sent to),
the job ad source, notes and a change history. Helper: `scripts/cv_store.py` (`--help` lists every command).

## 1. Find the CV
Turn the request into a search and run it:
```
python scripts/cv_store.py list --company "google" --latest   # "my latest CV for Google"
python scripts/cv_store.py list --query "Szymon"               # "the CV I wrote for Szymon"
python scripts/cv_store.py list                                 # everything, newest first
```
- `--query` matches the person, company, role, contact and notes, ignoring case and Polish diacritics.
  Use the base form of a name ("Szymon", not "Szymona"). A person ("CV for Szymon") can be either the CV's owner
  (`CV_Szymon…`) or the contact it was sent to. Search with `--query` so both are covered.
- "Moje"/"my" CV means the user's own person folder. If several person folders exist and it's not clear
  which one is the user's, ask once.
- **Exactly one match** (or "latest"/"ostatnie" was asked for): say which CV you opened (person, company, date, role).
- **Several matches**: ask with AskUserQuestion, one option per CV labelled "Company · dd.mm.yyyy · role/contact"
  (max 4 options, newest first; if there are more, narrow the search first or list them in text).
- **No match**: show the closest CVs from the plain `list` and ask.

## 2. Load the context
Read `cv-meta.json`, `cv-data.en.json`, `cv-data.pl.json`, `job-analysis.md` (if any) and the person's
`_data/career-facts.md`. Summarise the CV in 2–3 lines and ask what to change, unless the request already says.

## 3. In place or a new version
If PDFs already exist, ask once (AskUserQuestion):
1. **Edit this CV in place**: overwrite its files (good for fixes before it was sent).
2. **Save as a new version**: `python scripts/cv_store.py copy "<cv_dir>"` creates `<Company>/<today>` seeded
   with the JSON and analysis files; keep the old one as it was sent.

Retargeting to another company ("make my Google CV fit Amazon") is always a new CV:
`python scripts/cv_store.py copy "<cv_dir>" --company "Amazon" --role "..."`, then run the `job-ad-analysis`
skill for the new ad into the new folder before editing the content.

## 4. Apply the changes
- Edit `cv-data.en.json` following the `cv-builder` skill rules (schema, length, never invent facts).
- Keep `cv-data.pl.json` in sync: apply small edits directly in natural Polish; for large rewrites hand the EN
  file to the `pl-localizer` subagent.
- New or corrected facts go to `_data/career-facts.md` too, so future CVs get them.
- For substantial content changes with a job analysis present, run the `recruiter-reviewer` subagent and save
  its findings to `review.md`.
- Changes to the contact, role or notes go into `cv-meta.json`.

## 5. Render and record
Render with the `cv-render` skill (PDFs land next to the cv-data files), read every PDF to verify, then log it:
```
python scripts/cv_store.py log "<cv_dir>" "short description of the change"
```
Report the folder and the PDF paths.

## Legacy layout
Older versions of this plugin used `Documents/CV/` (facts in `Documents/CV/data/career-facts.md`, PDFs flat
in `Documents/CV`) and `work/` in the project. `python scripts/cv_store.py people` reports
`legacy_career_facts` when the old file exists. In that case offer to migrate: move the facts to
`CV_<FirstLast>/_data/`, and move each old CV set into `<Company>/<dd.mm.yyyy>` (ask the user which company
and date each set belongs to; use the files' modification date as the default). Never delete without confirmation.
