#!/usr/bin/env python3
"""Parse a LinkedIn "Download your data" export (ZIP or extracted folder) into one JSON file.

Only CV-relevant CSVs are kept (messages, connections, ads data etc. are skipped).

Usage: python parse_export.py <export.zip | export_dir> <out.json>
"""
import csv
import io
import json
import pathlib
import sys
import zipfile

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


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    data, skipped = {}, []
    for stem, text in iter_csvs(src):
        if stem.lower() in RELEVANT:
            data[stem] = read_csv_text(text)
        else:
            skipped.append(stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out}")
    for k in sorted(data):
        print(f"  {k}: {len(data[k])} rows")
    if skipped:
        print(f"Skipped (not CV-relevant): {', '.join(sorted(skipped))}")


if __name__ == "__main__":
    main()
