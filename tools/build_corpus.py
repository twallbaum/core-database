#!/usr/bin/env python3
"""Regenerate content/papers/*.md from the CORE master sheet.

The sheet is the single ground truth: it carries every corpus version
(v1 2024, v2 2025, v3 2026, ...). Running this rebuilds all entries.

Existing entries keep their file name, and therefore their URL - matched on
(Name, Publication Year), which is unique across the whole sheet. Rows with no
existing file are appended with the next free index.

    python3 tools/build_corpus.py --sheet <file.xlsx>          # dry run
    python3 tools/build_corpus.py --sheet <file.xlsx> --write  # write files
"""
import argparse
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from schema import FIELDS, LIST_KEYS, MARKER_COLUMN, normalise_tags  # noqa: E402

PAPERS_DIR = os.path.join("content", "papers")
TZ = timezone(timedelta(hours=1))


def load_sheet(path):
    """Header on row 2, per-column description on row 3, data from row 4."""
    df = pd.read_excel(path, sheet_name=0, header=1, skiprows=[2])
    df.columns = [str(c) for c in df.columns]
    missing = [h for h, _, _, _ in FIELDS if h not in df.columns]
    if missing:
        sys.exit(
            "Sheet is missing expected columns:\n  "
            + "\n  ".join(repr(m) for m in missing)
            + "\n\nSiegen renamed something. Update tools/schema.py."
        )
    return df


def toml_escape(value):
    """Escape for a TOML basic string. Newlines matter: the sheet has 22 cells
    containing them, and a raw newline makes the front matter invalid."""
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r\n", "\\n")
        .replace("\r", "\\n")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )


def cell(row, header):
    value = row[header]
    if pd.isna(value):
        return ""
    return " ".join(str(value).split()) if not isinstance(value, str) else str(value).strip()


def split_list(raw):
    return [" ".join(p.split()) for p in str(raw).split(";") if p.strip()]


def slug_name(name):
    safe = "".join(c for c in name if c.isalnum() or c in " -_").strip()
    return safe.replace(" ", "_") or "default_name"


def existing_files():
    """(name, publication_year) -> filename, for entries already published."""
    index = {}
    for fname in os.listdir(PAPERS_DIR):
        if not fname.endswith(".md") or fname == "chart.md":
            continue
        text = open(os.path.join(PAPERS_DIR, fname), encoding="utf-8").read()
        name = re.search(r'(?m)^name = "(.*?)"', text)
        year = re.search(r'(?m)^publication_year = "(.*?)"', text)
        if name and year:
            index[(name.group(1).strip(), year.group(1).strip())] = fname
    return index


def render(row, created):
    lines = ["+++", f'date = "{created}"', "draft = false"]
    for header, key, kind, _ in FIELDS:
        raw = cell(row, header)
        if kind == "list":
            values = normalise_tags(raw) if key == "tags" else split_list(raw)
            items = ", ".join(f'"{toml_escape(v)}"' for v in values)
            lines.append(f"{key} = [{items}]")
        else:
            lines.append(f'{key} = "{toml_escape(raw)}"')
    lines.append("+++")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--write", action="store_true", help="write files (default: dry run)")
    args = ap.parse_args()

    df = load_sheet(args.sheet)
    published = existing_files()
    next_index = max((int(f.split("_")[0]) for f in published.values()), default=-1) + 1
    created = datetime.now(TZ).isoformat()

    updated, added, unchanged = [], [], []
    for _, row in df.iterrows():
        name = cell(row, "Name")
        year = cell(row, "Online Publication Year")
        key = (name, year)

        if key in published:
            fname = published[key]
            bucket = updated
        else:
            fname = f"{next_index}_{slug_name(name)}.md"
            next_index += 1
            bucket = added

        path = os.path.join(PAPERS_DIR, fname)
        body = render(row, created)

        if os.path.exists(path):
            # Ignore the date line when deciding whether anything really changed.
            old = open(path, encoding="utf-8").read()
            strip = lambda t: re.sub(r'(?m)^date = ".*"\n', "", t)
            if strip(old) == strip(body):
                unchanged.append(fname)
                continue
            body = re.sub(
                r'(?m)^date = ".*"$',
                re.search(r'(?m)^date = ".*"$', old).group(0),
                body,
                count=1,
            )

        bucket.append(fname)
        if args.write:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(body)

    marker = df[MARKER_COLUMN].notna().sum() if MARKER_COLUMN in df.columns else 0
    print(f"sheet rows       : {len(df)}  ({marker} marked NEW by Siegen)")
    print(f"already current  : {len(unchanged)}")
    print(f"updated in place : {len(updated)}")
    print(f"newly added      : {len(added)}")
    for fname in added:
        print(f"    + {fname}")
    total = len(unchanged) + len(updated) + len(added)
    print(f"total entries    : {total}")
    if total != len(df):
        sys.exit(f"ERROR: {len(df)} rows produced {total} entries - an entry was dropped.")
    if not args.write:
        print("\ndry run - nothing written. Re-run with --write.")


if __name__ == "__main__":
    main()
