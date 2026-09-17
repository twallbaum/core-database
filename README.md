# core-database
CORE is a free-access, interactive database designed for researchers and designers, to explore relatedness technologies in a structured and engaging way. 

Shield: [![CC BY 4.0][cc-by-shield]][cc-by]

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

## Updating the corpus

The Excel sheet from Siegen is the single ground truth — it carries every corpus
version (v1 2024, v2 2025, v3 2026, …), not just the new rows.

```bash
python3 tools/build_corpus.py --sheet 260615_CORE\ Update\ 2026_ALL_Analysis\ of\ Prototypes_final.xlsx
python3 tools/build_corpus.py --sheet <sheet.xlsx> --write
hugo
```

The first command is a dry run and prints what would change. The importer matches
existing entries on `(Name, Publication Year)`, so they keep their file name and
therefore their URL; rows with no existing file are appended with the next free
index. It aborts if the entry count ever comes out below the row count.

`tools/schema.py` maps Excel headers to front-matter keys and holds the keyword
normalisation table. When Siegen renames a column the importer stops with the
offending header rather than silently writing a new key — fix it in that one file.
The search index (`layouts/_default/index.json`) and the Fuse key list are both
derived from the front matter, so they need no edit.

`data_process.ipynb` is the original one-off converter, kept for reference.
