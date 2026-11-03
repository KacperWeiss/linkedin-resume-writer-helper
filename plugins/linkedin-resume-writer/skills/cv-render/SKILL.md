---
name: cv-render
description: Render cv-data JSON (EN/PL) into PDF CVs in two layouts, ATS single-column and modern two-column, using headless Edge/Chrome, saved to the Windows Documents\CV folder. Use when the CV content is ready and PDFs are needed.
---

# Render CV to PDF

From this skill's base directory:
```
python scripts/render.py <path>/cv-data.en.json            # both layouts → Documents\CV
python scripts/render.py <path>/cv-data.pl.json --layout ats
python scripts/render.py <file> --suffix LowLatency          # tag a version for a specific job ad
python scripts/render.py <file> --out-dir <dir> --keep-html  # preview / debug
```
- Output name: `CV_<Name>_<EN|PL>_<ATS|Modern>[_suffix].pdf`. The Documents folder is
  resolved through the Windows shell API, so it works when Documents is redirected (e.g. to OneDrive).
- Needs only Python 3 and Microsoft Edge or Chrome. Set `CV_BROWSER` to override the browser.
- Templates live in `templates/` (`base.css` + `ats.css` / `modern.css`). Section headings for
  each language are in `LABELS` in `scripts/render.py`.

## Always verify
After rendering, **read every PDF** (Read tool) and check:
- at most 2 pages and no orphaned headings at page breaks,
- Polish diacritics render correctly,
- the ATS version has a sensible linear text order,
- no leftover placeholder or sample text.

If the CV goes over 2 pages, shorten the content in cv-data rather than shrinking the font.
