#!/usr/bin/env python3
"""Parse a LinkedIn "Download your data" export (ZIP or extracted folder) into one JSON file.

Only CV-relevant CSVs are kept (messages, connections, ads data etc. are skipped).

Usage: python parse_export.py <export.zip | export_dir> [out.json] [--name "First Last"]

Without out.json the result goes to the person's CV library folder:
Documents/CV_<FirstLast>/_data/linkedin-raw.json (the name comes from Profile.csv or --name),
and a copy of the export is kept in _data/sources/.
"""
import argparse
import csv
import io
import json
import pathlib
import shutil
import sys
import zipfile

# Shared CV library helpers live in the cv-edit skill.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "cv-edit" / "scripts"))
import cv_store  # noqa: E402

RELEVANT = {
    "profile", "profile summary", "positions", "education", "skills", "certifications",
    "languages", "projects", "courses", "honors", "publications", "patents",
    "volunteering", "organizations", "test scores", "recommendations_received",
    "endorsement_received_info", "email addresses", "phonenumbers", "rich_media",
    "causes you care about", "whatsapp phone numbers",
}


def read_csv_text(text: str) -> list[dict]:
    lines = text.splitlines()
    # Some LinkedIn CSVs start with a "Notes:" preamble before the header row.
    start = 0
    if lines and lines[0].lower().startswith("notes"):
        for i, line in enumerate(lines):
            if not line.strip():
                start = i + 1
                break
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])))
    rows = []
    for row in reader:
        clean = {k.strip(): (v or "").strip() for k, v in row.items() if k}
        if any(clean.values()):
            rows.append(clean)
    return rows


def iter_csvs(src: pathlib.Path):
    if src.is_file() and src.suffix.lower() == ".zip":
        with zipfile.ZipFile(src) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    yield pathlib.PurePosixPath(name).stem, zf.read(name).decode("utf-8-sig", "replace")
    elif src.is_dir():
        for p in src.rglob("*.csv"):
            yield p.stem, p.read_text(encoding="utf-8-sig", errors="replace")
    else:
        sys.exit(f"Not a ZIP or directory: {src}")


def profile_name(data: dict) -> str:
    for row in data.get("Profile", []):
        name = " ".join(filter(None, [row.get("First Name"), row.get("Last Name")]))
        if name:
            return name
    return ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--name", help="person's full name, when Profile.csv is missing from the export")
    a = ap.parse_args()
    src = pathlib.Path(a.src)
    data, skipped = {}, []
    for stem, text in iter_csvs(src):
        if stem.lower() in RELEVANT:
            data[stem] = read_csv_text(text)
        else:
            skipped.append(stem)
    if a.out:
        out = pathlib.Path(a.out)
    else:
        name = a.name or profile_name(data)
        if not name:
            sys.exit("No name in Profile.csv. Pass --name \"First Last\" or an explicit out.json path.")
        data_dir = cv_store.person_dir(name) / cv_store.DATA
        out = data_dir / "linkedin-raw.json"
        sources = data_dir / "sources"
        sources.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            shutil.copy2(src, sources / src.name)
        else:
            shutil.copytree(src, sources / src.name, dirs_exist_ok=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    for k in sorted(data):
        print(f"  {k}: {len(data[k])} rows")
    if skipped:
        print(f"Skipped (not CV-relevant): {', '.join(sorted(skipped))}")


if __name__ == "__main__":
    main()
