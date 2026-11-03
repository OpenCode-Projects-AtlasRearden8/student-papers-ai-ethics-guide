# STATUS.md

**Project:** Essays and Papers with AI, Honestly — a classroom-friendly manual
**Owner:** Asdale Dynamics, LLC (part of The Massive AI Manual)
**Date:** 2026-11-03

## What was built

An education-only manual teaching students (and teachers) how to use AI with
school essays and papers without cheating — no API keys, no accounts, no
personal data, no network calls.

- **docs/ (Markdown, source of truth, 8 files)**
  - `index.md` — start-here route map and ground rules
  - `01-what-counts-as-cheating.md` — traffic-light table, detection hierarchy, scenario drill
  - `02-school-policy-translation.md` — decoder table for policy boilerplate, five questions to ask, risk test
  - `03-ai-as-tutor-not-ghostwriter.md` — the core rule, six reusable tutor prompts, drift warnings
  - `04-outlining-and-feedback-loops.md` — Five Prompt Outline Method, two revision loops, tracking template
  - `05-verifying-citations.md` — 5-step verification pass, red flags, source-first workflow
  - `06-disclosure-statements.md` — one-sentence template, graded examples, teacher's disclosure sheet
  - `07-honor-code-examples.md` — school policy draft, syllabus insert, student pledge, honest detection methods
- **site/ (static HTML, generated, 8 pages + style.css)** — same manual as a
  no-JavaScript, no-tracker mini-site; clean print styles for classroom handouts.
- **site-assets/style.css** — shared stylesheet used by the build.
- **tools/build_site.py** — stdlib-only Markdown → HTML converter (subscript: headings,
  paragraphs, emphasis, links, lists, tables, blockquotes, code fences, details blocks).
- **tools/verify.py** — self-check suite (structure, link resolution, HTML balance,
  license/readme requirements, secret scanning).
- **README.md** — usage, build from source, classroom-use note; credits Asdale Dynamics, LLC.
- **LICENSE** — MIT with the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`.

## How to run it

```bash
# Read the manual
open site/index.html            # or any docs/*.md

# Preview the site locally (optional)
python3 -m http.server 8000 --directory site

# Rebuild the site from docs/
python3 tools/build_site.py     # requires Python 3.10+, stdlib only

# Run the self-checks
python3 tools/verify.py         # exit 0 = all green
```

## Verification results (actual output, 2026-11-03)

- `tools/build_site.py` — "Built 8 pages into site/" for all 8 docs pages, plus style.css.
- `tools/verify.py` — **all checks passed**: docs present, every internal markdown and
  HTML link resolves, each page has doctype + balanced tags + Asdale credit, LICENSE
  copyright line exact, README credit present, no obvious secrets in text files.
- Local server smoke test: `index.html`, guide pages, and `style.css` all return HTTP 200.
- Content spot checks: details/answers block renders, checklists render, honor-code
  blockquotes render 3 blocks with nested lists intact.

Two converter bugs were found and fixed during verification: multi-line list items
previously split into orphan paragraphs/renumbered lists, and checkbox items were
shadowed by the plain-bullet rule. Both fixed and re-verified.

## Known gaps

- HTML is generated fresh each build; hand edits to `site/` will be lost — edit `docs/`
  and rebuild.
- The converter supports the manual's Markdown subset only (not full CommonMark); new
  constructs (footnote syntax, nested numbered lists with letters, images) are untested.
- No downloadable PDF of the printouts; printing from the browser is the current path.
- `docs/index.md` table of contents lists guides by title, and titles could drift from
  filenames if pages are renamed (verify.py catches dead links, not stale labels).
- The manual is opinion-based guidance, not a survey of named schools' actual policies;
  example honor codes are explicitly marked "adapt before adopting."

## Boundaries

- Education only; no cheating assistance of any kind.
- No secrets, no API keys, no personal data anywhere in this repo.
- Zero external services: no network access is needed to read, build, or verify.
