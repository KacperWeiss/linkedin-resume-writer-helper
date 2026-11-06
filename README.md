# linkedin-resume-writer-helper

A Claude Code plugin marketplace with one plugin, **linkedin-resume-writer**. It goes from a LinkedIn data export to an
improved LinkedIn profile and a tailored CV in **English and Polish**, rendered as PDF in two layouts (ATS single-column
and modern two-column) into a per-person CV library in `Documents`.

## Install
```
/plugin marketplace add KacperWeiss/linkedin-resume-writer-helper
/plugin install linkedin-resume-writer@resume-tools
```
Requirements: Python 3.10+ and Microsoft Edge or Google Chrome (used headless to print PDFs). No pip packages are needed.

## Usage
1. In LinkedIn: Settings → Data privacy → **Get a copy of your data**. Select Positions, Education, Skills, Certifications,
   Languages, Projects and Recommendations, or the full archive. "Profile" alone gives only `Profile.csv`.
2. Put the ZIP (and optionally a job ad PDF) into `input/` in your working folder.
3. Run `/cv-build` (optionally `/cv-build input/job-ad.pdf`).
4. To change a CV later, just ask from any folder, e.g. "Zmodyfikujmy moją ostatnią CV dla Google" or
   "Chcę wprowadzić zmiany w CV napisanym dla Szymona". The `cv-edit` skill finds it and asks if several match.

### Where things are saved
```
Documents\CV_<FirstLast>\
  _data\                     career-facts.md, linkedin-raw.json, sources\ (shared by all CVs)
  <Company>\<dd.mm.yyyy>\     one CV per job ad: cv-meta.json, job ad + analysis, cv-data.en/pl.json, PDFs
  Ogólne\<dd.mm.yyyy>\        a CV without a specific job ad
```
All personal data stays on your machine. Nothing is written to the project folder.

## Contents
| Type | Name | Purpose |
|---|---|---|
| command | `/cv-build` | runs the whole workflow end to end |
| skill | `linkedin-export-parse` | ZIP/CSV export → `_data/linkedin-raw.json` |
| skill | `job-ad-analysis` | job ad → must-haves, ATS keywords, gap map |
| skill | `linkedin-profile-audit` | interview + ready-to-paste LinkedIn improvements |
| skill | `cv-builder` | writes `cv-data.<lang>.json` (schema + writing rules) |
| skill | `cv-render` | JSON → PDF (ATS / modern) via headless Edge or Chrome |
| skill | `cv-edit` | finds an existing CV (by company, person, contact, date) and edits or re-targets it |
| agent | `recruiter-reviewer` | recruiter and ATS critique |
| agent | `pl-localizer` | natural Polish version of the CV |

No MCP server is bundled: LinkedIn has no public profile API, so the workflow runs on the offline data export.

## License
Proprietary, all rights reserved. See [LICENSE](LICENSE). Copying, installing or modifying this plugin requires the
author's written permission.
