#!/usr/bin/env python3
"""CV library: one folder per person, one folder per CV.

Layout (under the Windows Documents folder):
  CV_<FirstLast>/
    _data/                      person-level data shared by all CVs
      career-facts.md           confirmed facts (single source of truth)
      linkedin-raw.json         parsed LinkedIn export
      sources/                  copies of the LinkedIn export ZIP / profile PDF
    <Company>/<dd.mm.yyyy>/     one CV for a job ad from that company
    Ogólne/<dd.mm.yyyy>/        a general CV without a specific job ad
      cv-meta.json              who / for whom / which ad / change history
      job-ad.*, job-analysis.md, linkedin-improvements.md, review.md
      cv-data.en.json, cv-data.pl.json, CV_*.pdf

Commands (all print JSON or a path):
  person-dir --name "Jan Kowalski"                       create/return CV_<FirstLast> (with _data/)
  new --name N [--company C] [--role R] [--contact P] [--job-ad SRC] [--note T]
                                                         create a new CV folder + cv-meta.json
  list [--name N] [--company C] [--query Q] [--latest]   find CVs (newest first); Q matches person,
                                                         company, role, contact and notes
  people                                                 list person folders
  log <cv_dir> "what changed"                            append to the CV's change history
  copy <cv_dir> [--company C] [--role R] [--contact P]   new version (today) seeded from an existing CV
"""
import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import sys
import unicodedata

GENERAL = "Ogólne"
DATA = "_data"
META = "cv-meta.json"
DATE_RE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})(?:_(\d+))?$")
# Files that make up a CV's working state; PDFs are rebuilt, so they are not copied to a new version.
SEED_FILES = ("cv-data.en.json", "cv-data.pl.json", "job-analysis.md", "linkedin-improvements.md")


def documents_dir() -> pathlib.Path:
    """The real Documents folder, also when it is redirected (e.g. to OneDrive)."""
    if os.environ.get("CV_LIBRARY_ROOT"):
        return pathlib.Path(os.environ["CV_LIBRARY_ROOT"])
    if os.name == "nt":
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf) == 0:  # CSIDL_PERSONAL
            return pathlib.Path(buf.value)
    return pathlib.Path.home() / "Documents"


def ascii_fold(s: str) -> str:
    s = s.replace("ł", "l").replace("Ł", "L")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def norm(s: str) -> str:
    """Case- and diacritic-insensitive form for matching ("Szymona" contains "szymon")."""
    return ascii_fold(s or "").lower()


def person_folder_name(name: str) -> str:
    parts = re.findall(r"[A-Za-z0-9]+", ascii_fold(name))
    if not parts:
        sys.exit(f"Can't build a folder name from: {name!r}")
    return "CV_" + "".join(p[:1].upper() + p[1:] for p in parts)


def safe_folder(name: str) -> str:
    """Keep the company name readable, drop only what Windows forbids in a folder name."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', " ", name or "")
    s = re.sub(r"\s+", " ", s).strip(" .")
    return s or GENERAL


def person_dir(name: str, create: bool = True) -> pathlib.Path:
    p = documents_dir() / person_folder_name(name)
    if create:
        (p / DATA).mkdir(parents=True, exist_ok=True)
    return p


def folder_date(name: str):
    m = DATE_RE.match(name)
    if not m:
        return None
    try:
        return dt.date(int(m[3]), int(m[2]), int(m[1])), int(m[4] or 1)
    except ValueError:
        return None


def next_cv_dir(parent: pathlib.Path, today: dt.date) -> pathlib.Path:
    base = today.strftime("%d.%m.%Y")
    d, n = parent / base, 2
    while d.exists():
        d, n = parent / f"{base}_{n}", n + 1
    return d


def read_meta(cv_dir: pathlib.Path) -> dict:
    f = cv_dir / META
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def write_meta(cv_dir: pathlib.Path, meta: dict) -> None:
    (cv_dir / META).write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def now() -> str:
    return dt.datetime.now().isoformat(timespec="minutes")


def make_cv(name, company, role, contact, job_ad, note, derived_from=None) -> pathlib.Path:
    root = person_dir(name)
    company = (company or "").strip()
    cv_dir = next_cv_dir(root / (safe_folder(company) if company else GENERAL), dt.date.today())
    cv_dir.mkdir(parents=True)
    meta = {
        "person": name,
        "company": company or None,
        "role": role or None,
        "contact": contact or None,
        "job_ad": job_ad or None,
        "notes": note or None,
        "created": now(),
        "updated": now(),
        "derived_from": derived_from,
        "history": [{"at": now(), "change": "created" + (f" from {derived_from}" if derived_from else "")}],
    }
    write_meta(cv_dir, meta)
    return cv_dir


def iter_cvs():
    docs = documents_dir()
    if not docs.is_dir():
        return
    for person in sorted(docs.glob("CV_*")):
        if not person.is_dir():
            continue
        for group in person.iterdir():
            if not group.is_dir() or group.name == DATA:
                continue
            for cv_dir in group.iterdir():
                fd = folder_date(cv_dir.name) if cv_dir.is_dir() else None
                if not fd:
                    continue
                meta = read_meta(cv_dir)
                yield {
                    "path": str(cv_dir),
                    "person_dir": str(person),
                    "person": meta.get("person") or person.name[3:],
                    "company": meta.get("company") or (None if group.name == GENERAL else group.name),
                    "general": group.name == GENERAL,
                    "date": cv_dir.name,
                    "role": meta.get("role"),
                    "contact": meta.get("contact"),
                    "notes": meta.get("notes"),
                    "updated": meta.get("updated"),
                    "pdfs": sorted(p.name for p in cv_dir.glob("*.pdf")),
                    "_sort": (fd[0].isoformat(), fd[1], meta.get("created") or ""),
                }


def cmd_list(a) -> None:
    rows = list(iter_cvs())
    if a.name:
        want = norm(a.name)
        rows = [r for r in rows if want in norm(r["person"]) or want in norm(pathlib.Path(r["person_dir"]).name)]
    if a.company:
        want = norm(a.company)
        rows = [r for r in rows if want in norm(r["company"] or GENERAL)]
    if a.query:
        terms = norm(a.query).split()
        def hay(r):
            return norm(" ".join(str(r[k] or "") for k in ("person", "company", "role", "contact", "notes", "date"))
                        + (" " + GENERAL if r["general"] else ""))
        # Polish inflection ("Szymona", "Google'a"): match on a 4+ letter stem as well as the full word.
        rows = [r for r in rows if all(t in hay(r) or (len(t) > 4 and t[:-1] in hay(r)) or
                                       (len(t) > 5 and t[:-2] in hay(r)) for t in terms)]
    rows.sort(key=lambda r: r["_sort"], reverse=True)
    if a.latest:
        rows = rows[:1]
    for r in rows:
        r.pop("_sort")
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_people(_a) -> None:
    docs = documents_dir()
    out = []
    for p in sorted(docs.glob("CV_*")) if docs.is_dir() else []:
        if p.is_dir():
            out.append({"path": str(p), "has_career_facts": (p / DATA / "career-facts.md").exists(),
                        "cvs": sum(1 for g in p.iterdir() if g.is_dir() and g.name != DATA
                                   for c in g.iterdir() if c.is_dir() and folder_date(c.name))})
    legacy = docs / "CV" / "data" / "career-facts.md"
    print(json.dumps({"people": out, "legacy_career_facts": str(legacy) if legacy.exists() else None},
                     ensure_ascii=False, indent=2))


def cmd_log(a) -> None:
    cv_dir = pathlib.Path(a.cv_dir)
    meta = read_meta(cv_dir)
    meta.setdefault("history", []).append({"at": now(), "change": a.change})
    meta["updated"] = now()
    write_meta(cv_dir, meta)
    print(cv_dir / META)


def cmd_copy(a) -> None:
    src = pathlib.Path(a.cv_dir)
    meta = read_meta(src)
    name = meta.get("person") or a.name
    if not name:
        sys.exit("Source has no cv-meta.json with a person; pass --name.")
    company = a.company if a.company is not None else (meta.get("company") or "")
    dst = make_cv(name, company, a.role or meta.get("role"), a.contact or meta.get("contact"),
                  meta.get("job_ad"), meta.get("notes"), derived_from=str(src))
    for f in SEED_FILES:
        if (src / f).exists():
            shutil.copy2(src / f, dst / f)
    for f in src.glob("job-ad.*"):
        shutil.copy2(f, dst / f.name)
    print(dst)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("person-dir"); p.add_argument("--name", required=True)
    p = sub.add_parser("new")
    p.add_argument("--name", required=True); p.add_argument("--company", default="")
    p.add_argument("--role"); p.add_argument("--contact"); p.add_argument("--job-ad"); p.add_argument("--note")
    p = sub.add_parser("list")
    p.add_argument("--name"); p.add_argument("--company"); p.add_argument("--query"); p.add_argument("--latest", action="store_true")
    sub.add_parser("people")
    p = sub.add_parser("log"); p.add_argument("cv_dir"); p.add_argument("change")
    p = sub.add_parser("copy")
    p.add_argument("cv_dir"); p.add_argument("--name"); p.add_argument("--company")
    p.add_argument("--role"); p.add_argument("--contact")

    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "person-dir":
        print(person_dir(a.name))
    elif a.cmd == "new":
        print(make_cv(a.name, a.company, a.role, a.contact, a.job_ad, a.note))
    elif a.cmd == "list":
        cmd_list(a)
    elif a.cmd == "people":
        cmd_people(a)
    elif a.cmd == "log":
        cmd_log(a)
    elif a.cmd == "copy":
        cmd_copy(a)


if __name__ == "__main__":
    main()
