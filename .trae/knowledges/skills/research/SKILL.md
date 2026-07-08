---
name: knowledge-skills-research
description: >
  Covers research skills: multi-angle web research, GitHub repository deep-dive
  analysis, single-paper academic peer review, and systematic literature review
  across multiple arXiv papers.
  Navigate when: conducting web research, analyzing GitHub repos, reviewing
  academic papers, performing literature surveys, or synthesizing findings
  across multiple sources.
  Excludes: data analysis of files (see ../data-analysis/), content generation
  from research (see ../content-creation/).
  Keywords: deep-research, github-deep-research, academic-paper-review,
  systematic-literature-review, SLR, arXiv, web_search, web_fetch, peer review,
  literature survey, Mermaid, citation.
---

## Module Structure

Four research skills form a layered ecosystem: deep-research provides the foundational
multi-angle web research methodology; github-deep-research specializes in repository
analysis; academic-paper-review handles single-paper deep review; systematic-literature-review
(SLR) performs breadth-first synthesis across many papers.

### Directory Layout
- `skills/public/deep-research/` — Multi-phase web research methodology
- `skills/public/github-deep-research/` — GitHub repo analysis via API + web search
  - `scripts/github_api.py` — GitHub API client (summary, readme, tree, commits, etc.)
  - `assets/report_template.md` — Structured report template
- `skills/public/academic-paper-review/` — Single-paper peer review
- `skills/public/systematic-literature-review/` — Multi-paper arXiv survey
  - `scripts/arxiv_search.py` — arXiv API search client
  - `templates/apa.md` — APA 7th edition citation format
  - `templates/ieee.md` — IEEE numeric citation format
  - `templates/bibtex.md` — BibTeX citation format
  - `evals/` — Trigger evaluation sets

### Key Entry Points
- deep-research Phase 1–4 — Broad Exploration → Deep Dive → Diversity & Validation → Synthesis Check
- `github_api.py <owner> <repo> <command>` — GitHub data retrieval
- academic-paper-review Phase 1–3 — Comprehension → Critical Analysis → Review Synthesis
- `arxiv_search.py "<query>" --max-results <N>` — arXiv paper discovery

## Gotchas
- Systematic-literature-review requires `subagent_enabled=true` at runtime — Phase 3 parallel metadata extraction hard-depends on the `task` tool; without subagents the workflow cannot execute as designed (`skills/public/systematic-literature-review/SKILL.md`)
- SLR has a hard upper bound of 50 papers — synthesis quality degrades past that; larger surveys should be split by sub-topic (`skills/public/systematic-literature-review/SKILL.md`)
- SLR arXiv search uses relevance sorting by default, not date sorting — `submittedDate` sorting returns mostly off-topic results; only use it when the user explicitly asks for chronological order (`skills/public/systematic-literature-review/SKILL.md`)
- SLR query strings must be 2-3 core keywords only — the script wraps multi-word queries in double quotes for phrase matching; long queries like "diffusion models in computer vision" return 0 results because few papers contain that exact phrase (`skills/public/systematic-literature-review/SKILL.md`)
- Academic-paper-review and SLR have distinct scopes — single-paper deep review vs. multi-paper breadth synthesis; routing to the wrong one produces inappropriate output (`skills/public/academic-paper-review/SKILL.md`, `skills/public/systematic-literature-review/SKILL.md`)
- Deep-research must be loaded BEFORE starting any content generation task — generating content without prior research is explicitly forbidden by the skill (`skills/public/deep-research/SKILL.md`)
- SLR subagent results are strings with a `Task Succeeded. Result: ` prefix — this prefix must be stripped before parsing JSON; failing to strip it causes parse errors (`skills/public/systematic-literature-review/SKILL.md`)

## Architecture
- Deep-research uses a 4-phase methodology: Broad Exploration (landscape mapping) → Deep Dive (targeted queries per dimension) → Diversity & Validation (facts, examples, opinions, trends, comparisons, challenges) → Synthesis Check (completeness verification) (`skills/public/deep-research/SKILL.md`)
- GitHub-deep-research uses a 4-round research strategy: Round 1 (GitHub API) → Round 2 (Discovery, 3-5 web searches) → Round 3 (Deep Investigation, 5-10 searches + web_fetch) → Round 4 (Deep Dive, commit/issue/PR analysis) (`skills/public/github-deep-research/SKILL.md`)
- SLR Phase 3 (parallel metadata extraction) uses a strict concurrency strategy: max 3 subagents per turn, ~5 papers per batch, split across rounds per a decision table — never dispatch more than 3 subagents in the same turn (`skills/public/systematic-literature-review/SKILL.md`)
- Academic-paper-review adapts its review focus by paper type: empirical papers emphasize experimental design and statistical rigor; theoretical papers emphasize proof correctness and assumption reasonableness; surveys emphasize comprehensiveness and taxonomy quality (`skills/public/academic-paper-review/SKILL.md`)

## Decisions
- SLR is arXiv-only by design — it does not query Semantic Scholar, PubMed, or Google Scholar; multi-source academic search belongs in a dedicated MCP server (`skills/public/systematic-literature-review/SKILL.md`)
- GitHub-deep-research uses inline citations with `[citation:Title](URL)` format immediately after each claim — this is mandatory, not optional (`skills/public/github-deep-research/SKILL.md`)
- Academic-paper-review uses a 1-5 rating scale across 6 criteria (Soundness, Novelty, Reproducibility, Experimental Design, Statistical Rigor, Scalability) with a 5-level contribution significance scale (Landmark → Below threshold) (`skills/public/academic-paper-review/SKILL.md`)

## Patterns
- All research skills produce structured Markdown reports with consistent sections — deep-research and github-deep-research include Mermaid diagrams for architecture/timelines (`skills/public/github-deep-research/SKILL.md`, `skills/public/deep-research/SKILL.md`)
- SLR citation format is selected from three templates (APA, IEEE, BibTeX) — only the matching template file is read, not all three (`skills/public/systematic-literature-review/SKILL.md`)
- GitHub-deep-research assigns confidence scores (High 90%+, Medium 70-89%, Low 50-69%) based on source quality — official docs and GitHub data get highest confidence (`skills/public/github-deep-research/SKILL.md`)
- Deep-research requires temporal awareness in all search queries — always check `<current_date>` before forming queries; use month+day+year for "today" queries, year-only for "trends" queries (`skills/public/deep-research/SKILL.md`)

## Dependencies
- GitHub-deep-research depends on the GitHub API via `scripts/github_api.py` — supports summary, info, readme, tree, languages, contributors, commits, issues, PRs, and releases commands (`skills/public/github-deep-research/scripts/github_api.py`)
- SLR depends on arXiv's API via `scripts/arxiv_search.py` — handles URL encoding, Atom XML parsing, and ID normalization (`skills/public/systematic-literature-review/scripts/arxiv_search.py`)
- Academic-paper-review recommends loading deep-research alongside it for papers that need broader field context (`skills/public/academic-paper-review/SKILL.md`)

## SLR Concurrency Rules
- Paper batches are strictly sized at ~5 papers each — the decision table maps paper counts to rounds and subagent counts (1-5 papers = 1 round/1 subagent, 46-50 papers = 4 rounds with 3+3+3+1 subagents) (`skills/public/systematic-literature-review/SKILL.md`)
- SLR subagents receive paper abstracts as text input only — they must not access the network or sandbox; their only job is to read text and return structured JSON (`skills/public/systematic-literature-review/SKILL.md`)
- SLR Phase 2 runs the arXiv search exactly once — retrying with modified queries wastes tool calls and risks hitting recursion limits (`skills/public/systematic-literature-review/SKILL.md`)
