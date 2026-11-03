# Essays and Papers with AI, Honestly

A classroom-friendly manual for students (and their teachers) on using AI
with school essays and papers *without* cheating: what counts as cheating by
the numbers, how to translate your school's policy into plain English, how to
use AI as a tutor instead of a ghostwriter, honest outlining and feedback
loops, how to verify AI-suggested citations, ready-to-use disclosure
statements, and adapt-anything honor-code examples with two PDF printouts.

Built for **The Massive AI Manual** by Asdale Dynamics, LLC.

## What's inside

```
docs/         The manual in Markdown (source of truth)
  index.md    Start here — who it's for, how to read it
  01 … 07     Seven guides, from "what counts as cheating" to honor codes
site/         The same manual as static HTML (generated — do not hand-edit)
site-assets/  Stylesheet used to build the site
tools/        build_site.py (Markdown → HTML) and verify.py (checks)
```

## Quick start

The core of the manual is one rule: use AI as a **tutor** — it explains,
quizzes, and critiques; *you* do the reading, thinking, and writing. Read in
this order:

1. **Start here:** [`docs/index.md`](docs/index.md) — who it's for and route map.
2. **Where the honest line is:** [`docs/01-what-counts-as-cheating.md`](docs/01-what-counts-as-cheating.md) —
   a green/yellow/red table of everyday AI actions.
3. **Your school, decoded:** [`docs/02-school-policy-translation.md`](docs/02-school-policy-translation.md) —
   translate policy boilerplate into plain English, plus five questions to
   ask your teacher in week one.
4. **The key rule:** [`docs/03-ai-as-tutor-not-ghostwriter.md`](docs/03-ai-as-tutor-not-ghostwriter.md) —
   the difference between help that leaves you smarter and help that does
   the work.

Nothing here is legal or institutional advice. When your school's policy and
this manual disagree, **your school wins.**

## The classroom-ready site (HTML)

The `site/` folder is a plain static website: no JavaScript, no trackers,
no external assets, prints cleanly for handouts.

```bash
# Optional local preview
python3 -m http.server 8000 --directory site
# then open http://localhost:8000 in a browser
```

Or simply open `site/index.html` directly from disk — it works without a server.

## Build from source

```bash
python3 tools/build_site.py    # regenerate site/ from docs/
python3 tools/verify.py        # self-checks: links, HTML validity, repo hygiene
```

Requirements: Python 3.10+ (standard library only). No dependencies, no
accounts, no API keys, no network access needed.

- `docs/` and `site/` live in one repo so updates to the manual can happen in a single
  place, with `verify.py` making sure every cross-link resolves.
- Teachers may print, project, and adapt any page for classroom use; the manual is
  MIT-licensed (see below).

## Contributing

1. Edit pages in `docs/` (Markdown). Then run the build + verify commands above.
2. Commit both the Markdown source and the rebuilt `site/` output.

## Copyleft / ethics reminder

- **Education only.** This manual helps you learn and write *your own* work;
  it never helps pass machine work off as human work.
- **No secrets, no personal data.** This repo is content + Python stdlib scripts.
  Nothing here calls out to the internet, nothing stores personal data.

## License

MIT — see [`LICENSE`](LICENSE).

**Copyright (c) 2026 Asdale Dynamics, LLC.** Built as part of *The Massive AI
Manual* — clear, warm, plain-English AI education. You can also read the free
manual right in this repo, hand it straight to your students, or adapt it for
the classroom, free and unlimited.
