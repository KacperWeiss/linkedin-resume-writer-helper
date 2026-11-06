---
name: cv-render
description: Render cv-data JSON (EN/PL) into PDF CVs in two layouts, ATS single-column and modern two-column, using headless Edge/Chrome, saved next to the cv-data files in the CV's library folder (Documents\CV_<FirstLast>\<Company|Ogólne>\<dd.mm.yyyy>). Use when the CV content is ready and PDFs are needed.
---

# Render CV to PDF

From this skill's base directory:
```
python scripts/render.py <cv>/cv-data.en.json              # both layouts → <cv> (the data file's folder)
python scripts/render.py <path>/cv-data.pl.json --layout ats
python scripts/render.py <file> --suffix LowLatency          # tag a version for a specific job ad
python scripts/render.py <file> --out-dir <dir> --keep-html  # preview / debug
```
- Output name: `CV_<Name>_<EN|PL>_<ATS|Modern>[_suffix].pdf`, written to the folder that holds the
  cv-data file, i.e. the CV's own folder in the CV library (see the `cv-edit` skill). Company and date are
  in the folder path, so `--suffix` is rarely needed.
- After rendering, record it: `python ../cv-edit/scripts/cv_store.py log "<cv>" "rendered"`.
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
