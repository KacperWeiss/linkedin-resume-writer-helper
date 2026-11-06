#!/usr/bin/env python3
"""Render cv-data JSON into PDF using headless Microsoft Edge / Chrome (no extra Python deps).

Usage:
  python render.py <cv-data.json> [--layout ats|modern|both] [--out-dir DIR] [--suffix TEXT] [--keep-html]

Default out-dir: the folder that holds the cv-data file, i.e. the CV's own folder in the CV library
(Documents/CV_<FirstLast>/<Company|Ogólne>/<dd.mm.yyyy>). Output name: CV_<Name>_<LANG>_<Layout>[_suffix].pdf
"""
import argparse
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

HERE = pathlib.Path(__file__).resolve().parent
TEMPLATES = HERE.parent / "templates"

LABELS = {
    "en": dict(summary="Summary", skills="Skills", experience="Experience", projects="Projects",
               education="Education", certifications="Certifications", languages="Languages",
               present="Present", contact="Contact"),
    "pl": dict(summary="Podsumowanie", skills="Umiejętności", experience="Doświadczenie zawodowe",
               projects="Projekty", education="Wykształcenie", certifications="Certyfikaty",
               languages="Języki", present="obecnie", contact="Kontakt"),
}


def esc(s) -> str:
    return html.escape(str(s or ""))


def rich(s) -> str:
    """Escape, then allow **bold**."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(s))


def dates(item, L) -> str:
    start, end = item.get("start", ""), item.get("end", "")
    if not start and not end:
        return ""
    return f"{esc(start)} – {esc(end) if end else L['present']}"


def section(title, body, cls="") -> str:
    return f'<section class="{cls}"><h2>{esc(title)}</h2>{body}</section>' if body else ""


def ul(items) -> str:
    items = [i for i in (items or []) if i]
    return "<ul>" + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ul>" if items else ""


def tech_line(tech) -> str:
    return f'<p class="tech">{esc(" · ".join(tech))}</p>' if tech else ""


def contact_items(b) -> list[str]:
    out = []
    for key in ("location", "email", "phone"):
        if b.get(key):
            v = esc(b[key])
            if key == "email":
                v = f'<a href="mailto:{v}">{v}</a>'
            out.append(v)
    for link in b.get("links", []):
        out.append(f'<a href="{esc(link.get("url"))}">{esc(link.get("label") or link.get("url"))}</a>')
    return out


def r_experience(cv, L) -> str:
    parts = []
    for x in cv.get("experience", []):
        org = " · ".join(filter(None, [esc(x.get("company")), esc(x.get("location"))]))
        parts.append(
            '<div class="entry">'
            f'<div class="row"><h3>{esc(x.get("title"))}</h3><span class="date">{dates(x, L)}</span></div>'
            f'<div class="org">{org}</div>'
            + (f'<p class="ctx">{rich(x["summary"])}</p>' if x.get("summary") else "")
            + ul(x.get("highlights")) + tech_line(x.get("tech")) + "</div>")
    return "".join(parts)


def r_projects(cv, L) -> str:
    parts = []
    for p in cv.get("projects", []):
        name = esc(p.get("name"))
        if p.get("url"):
            name = f'<a href="{esc(p["url"])}">{name}</a>'
        parts.append('<div class="entry">'
                     f'<div class="row"><h3>{name}</h3><span class="date">{dates(p, L)}</span></div>'
                     + (f'<p class="ctx">{rich(p["description"])}</p>' if p.get("description") else "")
                     + ul(p.get("highlights")) + tech_line(p.get("tech")) + "</div>")
    return "".join(parts)


def r_education(cv, L) -> str:
    parts = []
    for e in cv.get("education", []):
        deg = ", ".join(filter(None, [esc(e.get("degree")), esc(e.get("field"))]))
        parts.append('<div class="entry">'
                     f'<div class="row"><h3>{deg or esc(e.get("institution"))}</h3><span class="date">{dates(e, L)}</span></div>'
                     + (f'<div class="org">{esc(e.get("institution"))}</div>' if deg else "")
                     + (f'<p class="ctx">{rich(e["notes"])}</p>' if e.get("notes") else "") + "</div>")
    return "".join(parts)


def r_certs(cv) -> str:
    items = []
    for c in cv.get("certifications", []):
        name = rich(c.get("name"))
        if name and c.get("url"):
            name = f'<a href="{esc(c["url"])}">{name}</a>'
        parts = [p for p in [name, rich(c.get("issuer")), rich(c.get("date"))] if p]
        if parts:
            items.append(f"<li>{' — '.join(parts)}</li>")
    return "<ul>" + "".join(items) + "</ul>" if items else ""


def r_languages(cv) -> str:
    items = [f"**{l.get('name')}**" + (f" — {l['level']}" if l.get("level") else "") for l in cv.get("languages", [])]
    return ul(items)


def r_extras(cv) -> str:
    return "".join(section(x.get("title", ""), ul(x.get("items"))) for x in cv.get("extras", []))


def r_skills_lines(cv) -> str:
    rows = [f'<p class="skill"><strong>{esc(s.get("category"))}:</strong> {esc(", ".join(s.get("items", [])))}</p>'
            for s in cv.get("skills", [])]
    return "".join(rows)


def r_skills_tags(cv) -> str:
    out = []
    for s in cv.get("skills", []):
        tags = "".join(f'<span class="tag">{esc(i)}</span>' for i in s.get("items", []))
        out.append(f'<div class="skillgroup"><h4>{esc(s.get("category"))}</h4><div class="tags">{tags}</div></div>')
    return "".join(out)


def header(cv) -> str:
    b = cv["basics"]
    return (f'<header><h1>{esc(b.get("name"))}</h1>'
            + (f'<p class="headline">{esc(b["headline"])}</p>' if b.get("headline") else ""))


def footer(cv) -> str:
    return f'<footer class="gdpr">{esc(cv["gdpr_clause"])}</footer>' if cv.get("gdpr_clause") else ""


def build_ats(cv, L) -> str:
    b = cv["basics"]
    return (header(cv) + f'<p class="contact">{" | ".join(contact_items(b))}</p></header>'
            + section(L["summary"], f'<p>{rich(b.get("summary"))}</p>' if b.get("summary") else "")
            + section(L["skills"], r_skills_lines(cv))
            + section(L["experience"], r_experience(cv, L))
            + section(L["projects"], r_projects(cv, L))
            + section(L["education"], r_education(cv, L))
            + section(L["certifications"], r_certs(cv))
            + section(L["languages"], r_languages(cv))
            + r_extras(cv) + footer(cv))


def build_modern(cv, L) -> str:
    b = cv["basics"]
    contact = "".join(f"<li>{c}</li>" for c in contact_items(b))
    side = (section(L["contact"], f'<ul class="plain">{contact}</ul>')
            + section(L["skills"], r_skills_tags(cv))
            + section(L["languages"], r_languages(cv)))
    # Certifications live in the main column: long names would overflow the narrow sidebar onto the next page.
    main = (section(L["summary"], f'<p>{rich(b.get("summary"))}</p>' if b.get("summary") else "")
            + section(L["experience"], r_experience(cv, L))
            + section(L["projects"], r_projects(cv, L))
            + section(L["education"], r_education(cv, L))
            + section(L["certifications"], r_certs(cv))
            + r_extras(cv)
            # Footer goes inside the main column: after a fragmented CSS grid, Chromium pushes
            # trailing content onto a new page even when there is room left.
            + footer(cv))
    return (header(cv) + "</header>"
            + f'<div class="grid"><aside>{side}</aside><main>{main}</main></div>')


def page(cv, layout) -> str:
    lang = cv.get("lang", "en")
    L = LABELS.get(lang, LABELS["en"])
    css = (TEMPLATES / "base.css").read_text(encoding="utf-8") + (TEMPLATES / f"{layout}.css").read_text(encoding="utf-8")
    body = build_ats(cv, L) if layout == "ats" else build_modern(cv, L)
    title = f'CV – {cv["basics"].get("name", "")}'
    return (f'<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f'<style>{css}</style></head><body class="{layout}">{body}</body></html>')


def find_browser() -> str:
    candidates = [os.environ.get("CV_BROWSER", "")]
    for base in (os.environ.get("ProgramFiles(x86)", ""), os.environ.get("ProgramFiles", ""), os.environ.get("LOCALAPPDATA", "")):
        if base:
            candidates += [os.path.join(base, r"Microsoft\Edge\Application\msedge.exe"),
                           os.path.join(base, r"Google\Chrome\Application\chrome.exe")]
    candidates += [shutil.which(n) or "" for n in ("msedge", "google-chrome", "chromium", "chrome")]
    for c in candidates:
        if c and os.path.isfile(c):
            return c
    sys.exit("No Edge/Chrome found. Set CV_BROWSER to a Chromium-based browser executable.")


def to_pdf(html_path: pathlib.Path, pdf_path: pathlib.Path, browser: str) -> None:
    with tempfile.TemporaryDirectory() as profile:
        cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
               f"--user-data-dir={profile}", f"--print-to-pdf={pdf_path}", html_path.as_uri()]
        subprocess.run(cmd, check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not pdf_path.exists():
        sys.exit(f"PDF not produced: {pdf_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--layout", choices=["ats", "modern", "both"], default="both")
    ap.add_argument("--out-dir")
    ap.add_argument("--suffix", default="")
    ap.add_argument("--keep-html", action="store_true")
    a = ap.parse_args()

    cv = json.loads(pathlib.Path(a.data).read_text(encoding="utf-8"))
    out_dir = pathlib.Path(a.out_dir) if a.out_dir else pathlib.Path(a.data).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    ascii_name = unicodedata.normalize("NFKD", cv["basics"]["name"].replace("ł", "l").replace("Ł", "L"))
    name = re.sub(r"[^A-Za-z0-9]+", "_", ascii_name.encode("ascii", "ignore").decode()).strip("_")
    lang = cv.get("lang", "en").upper()
    browser = find_browser()
    for layout in (["ats", "modern"] if a.layout == "both" else [a.layout]):
        stem = f"CV_{name}_{lang}_{'ATS' if layout == 'ats' else 'Modern'}" + (f"_{a.suffix}" if a.suffix else "")
        html_path = out_dir / f"{stem}.html"
        html_path.write_text(page(cv, layout), encoding="utf-8")
        pdf_path = out_dir / f"{stem}.pdf"
        to_pdf(html_path, pdf_path, browser)
        if not a.keep_html:
            html_path.unlink()
        print(pdf_path)


if __name__ == "__main__":
    main()
