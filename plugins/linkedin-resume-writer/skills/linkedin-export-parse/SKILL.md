---
name: linkedin-export-parse
description: Parse a LinkedIn "Download your data" export (ZIP or folder, e.g. Basic_LinkedInDataExport_*.zip) and/or a LinkedIn profile "Save to PDF" file into structured JSON for CV work. Use when the user drops a LinkedIn export into the project or asks to read their LinkedIn data offline.
---

# LinkedIn export → JSON

1. Find inputs wherever the user says, otherwise in `input/` of the current folder:
   - `*LinkedInDataExport*.zip` or an extracted folder with `Profile.csv`, `Positions.csv`, …
   - optionally a profile PDF (`Profile.pdf` from "More → Save to PDF").
2. Run the parser from this skill's base directory:
   ```
   python scripts/parse_export.py "<zip-or-dir>"                     # → Documents/CV_<FirstLast>/_data/linkedin-raw.json
   python scripts/parse_export.py "<zip-or-dir>" --name "First Last" # when the export has no Profile.csv
   ```
   The name comes from `Profile.csv`. A copy of the export is kept in `_data/sources/`, so the CV library
   (see the `cv-edit` skill) has everything needed later. Copy a profile PDF there as well.
   It keeps only CV-relevant CSVs (Profile, Positions, Education, Skills, Certifications,
   Languages, Projects, Courses, Honors, Publications, Recommendations_Received, contact
   data…) and prints row counts.
3. If a profile PDF exists, read it too. It shows the section order and formatting that
   the user actually sees, and sometimes text missing from the CSVs.
4. Report to the user in a short table: what was found (number of positions, skills,
   etc.) and what is **missing or thin** (e.g. positions with no description, no
   metrics, no About section). These gaps feed the profile audit and the interview.

Notes:
- `Positions.csv` columns: Company Name, Title, Description, Location, Started On, Finished On
  (an empty Finished On means a current role).
- Dates are like `Mar 2021` and may be in the profile's language.
- Never send export contents to external services; work locally.
