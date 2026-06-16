---
name: knowledge-skills-data-analysis
description: >
  Covers data analysis skills: Excel/CSV analysis via DuckDB SQL engine and
  consulting-grade research report generation.
  Navigate when: analyzing uploaded data files, running SQL queries on spreadsheets,
  generating statistical summaries, creating consulting reports, or building
  analysis frameworks with data requirements.
  Excludes: chart visualization (see ../content-creation/), web research (see ../research/).
  Keywords: data-analysis, consulting-analysis, DuckDB, Excel, CSV, SQL, pivot,
  analysis framework, McKinsey, BCG, report generation, Phase 1, Phase 2.
---

## Module Structure

Two complementary skills for structured data work: data-analysis handles raw file
processing and SQL queries; consulting-analysis produces professional research reports
with a two-phase workflow (framework → report).

### Directory Layout
- `skills/public/data-analysis/` — Excel/CSV analysis via DuckDB
  - `scripts/analyze.py` — Schema inspection, SQL queries, statistical summaries, export
- `skills/public/consulting-analysis/` — Consulting-grade report generation
  - (no scripts — purely LLM-driven workflow)

### Key Entry Points
- `analyze.py --action inspect` — Inspect file structure (sheets, columns, types)
- `analyze.py --action query --sql "..."` — Execute arbitrary SQL against loaded data
- `analyze.py --action summary --table <name>` — Statistical summary of a table
- consulting-analysis Phase 1 — Analysis framework generation
- consulting-analysis Phase 2 — Report generation from collected data

## Gotchas
- Data-analysis auto-installs duckdb and openpyxl via pip if they're missing at import time — this means first invocation has a cold-start delay and requires network access (`skills/public/data-analysis/scripts/analyze.py`)
- Data-analysis caches loaded data using SHA256 of file contents — if you modify a file in-place without changing its path, the cache becomes stale because the hash changes but the old cache persists until evicted (`skills/public/data-analysis/scripts/analyze.py`)
- Consulting-analysis Phase 2 has a strict "no hallucination" policy — every number and chart must be traceable to the input Data Summary; fabricated data is explicitly forbidden (`skills/public/consulting-analysis/SKILL.md`)
- Consulting-analysis Phase 1 and Phase 2 are separated by an external data collection step — this skill does NOT perform data collection itself; it only produces the framework (Phase 1) and the final report (Phase 2) (`skills/public/consulting-analysis/SKILL.md`)
- Excel sheet names with spaces or special characters are auto-sanitized to underscores — queries must use the sanitized name, not the original sheet name (`skills/public/data-analysis/scripts/analyze.py`)
- Consulting-analysis requires the References section as the final section — the report MUST NOT stop after the Conclusion (`skills/public/consulting-analysis/SKILL.md`)

## Architecture
- Data-analysis uses DuckDB's in-process columnar SQL engine — all data stays local, no external database server needed; supports cross-file JOINs between Excel sheets and CSV files in the same query context (`skills/public/data-analysis/scripts/analyze.py`)
- Data-analysis caching: files are parsed once into a persistent DuckDB database under a temp directory, keyed by SHA256 hash of all input file contents — subsequent queries against the same files are near-instant (`skills/public/data-analysis/scripts/analyze.py`)
- Consulting-analysis follows a "Visual Anchor → Data Contrast → Integrated Analysis" flow per sub-chapter — charts are embedded first, then comparison tables, then narrative analysis (`skills/public/consulting-analysis/SKILL.md`)
- Consulting-analysis chart generation (Step 2.3) must complete before report writing (Step 2.4) — this ensures consistent visual narrative and avoids interleaving generation with writing (`skills/public/consulting-analysis/SKILL.md`)

## Decisions
- DuckDB was chosen over pandas for data-analysis because it supports full SQL (window functions, CTEs, subqueries) and handles 100MB+ files efficiently without loading everything into memory (`skills/public/data-analysis/SKILL.md`)
- Consulting-analysis uses McKinsey/BCG consulting voice standards with GB/T 7714-2015 citation format — the default output locale is zh_CN (`skills/public/consulting-analysis/SKILL.md`)

## Patterns
- Data-analysis supports three actions via a single script: `inspect`, `query`, `summary` — the `--action` parameter determines behavior, with `--sql` required for query and `--table` for summary (`skills/public/data-analysis/scripts/analyze.py`)
- Consulting-analysis chapter titles follow strict constraints: no "Chapter/Part/Section" prefixes, no forbidden words like "Decoding/DNA/Secrets", standard numbering only (`skills/public/consulting-analysis/SKILL.md`)
- Consulting-analysis insights must follow the "Data → User Psychology → Strategy Implication" chain — surface-level observations without strategic depth are rejected (`skills/public/consulting-analysis/SKILL.md`)
- Data-analysis table naming: Excel sheets become tables named after the sheet, CSV files use the filename without extension, names starting with digits get a `t_` prefix (`skills/public/data-analysis/scripts/analyze.py`)

## Dependencies
- Data-analysis requires DuckDB and openpyxl — both are auto-installed if missing, but the auto-install uses subprocess to call pip which may fail in restricted environments (`skills/public/data-analysis/scripts/analyze.py`)
- Consulting-analysis depends on external data collection skills (deep-research, data-analysis, web search) to populate the Data Summary between Phase 1 and Phase 2 (`skills/public/consulting-analysis/SKILL.md`)

## Report Generation Constraints
- Consulting-analysis sub-chapter conclusions require a minimum 200-word analytical paragraph synthesizing data points and revealing underlying tensions or opportunities (`skills/public/consulting-analysis/SKILL.md`)
- The Conclusion section must use flowing prose with NO bullet points — detailed recommendations belong in preceding body chapters (`skills/public/consulting-analysis/SKILL.md`)
- Numbers in consulting reports must use English commas for thousands separators (1,000 not 1，000) regardless of output locale (`skills/public/consulting-analysis/SKILL.md`)
- Horizontal rules (`---`) are forbidden in consulting reports (`skills/public/consulting-analysis/SKILL.md`)
