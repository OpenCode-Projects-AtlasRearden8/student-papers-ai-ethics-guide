#!/usr/bin/env python3
"""Build the static site/ from the markdown docs/ using only the Python stdlib.

Converts the subset of Markdown used in this manual (headings, paragraphs,
emphasis, inline code, links, unordered/ordered lists, tables, blockquotes,
code fences, hr) into plain, classroom-friendly HTML with a shared stylesheet.

Usage: python3 tools/build_site.py
"""
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

SITE_NAME = "Essays and Papers with AI, Honestly"
FOOTER_NOTE = (
    "The Massive AI Manual &mdash; Student Papers guide. "
    "Education only; not legal, medical, or institutional advice. "
    "Your school&#8217;s policy is the final word."
)


def inline(text: str) -> str:
    """Inline markdown -> HTML for the subset we use."""
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\w)\*([^*\n]+)\*(?!\w)", r"<em>\1</em>", out)
    # [label](target.md) -> .html ; keep http(s) and anchors as-is
    def link_repl(m):
        target = m.group(2)
        if target.startswith(("http://", "https://")) or target.startswith("#"):
            href = target
        else:
            href = re.sub(r"\.md$", ".html", target)
            if href.endswith("/"):
                href += "index.html"
        return f"<a href=\"{href}\">{m.group(1)}</a>"
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_repl, out)
    return out


def render_table(rows):
    header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
    body = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows[2:]]
    parts = ["<table>", "<thead><tr>"]
    parts += [f"<th>{inline(c)}</th>" for c in header]
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        parts += [f"<td>{inline(c)}</td>" for c in row]
        parts.append("</tr>")
    parts.append("</tbody></table>")
    return "".join(parts)


def markdown_to_fragment(md_text: str) -> str:
    lines = md_text.splitlines()
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Raw HTML pass-through (details/summary blocks)
        if stripped.startswith("<"):
            out.append(line)
            i += 1
            continue

        # Code fence
        if stripped.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append('<pre><code>' + html.escape("\n".join(code), quote=False) + "</code></pre>")
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # HR
        if re.match(r"^(---+|\*\*\*+)$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Table
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            rows = [line]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i])
                i += 1
            out.append(render_table(rows))
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            # blank separator inside a blockquote
            if quote and quote[-1] == "":
                quote.pop()
                i -= 1
            out.append("<blockquote>" + markdown_to_fragment("\n".join(quote)) + "</blockquote>")
            continue

        # Checkbox list (- [ ] / - [x]) — must be tested before plain bullets
        if re.match(r"^-\s+\[[ xX]\]", stripped):
            items = []
            while i < len(lines) and re.match(r"^-\s+\[[ xX]\]", lines[i].strip()):
                mark = lines[i].strip()[3].lower() == "x"
                raw = re.sub(r"^-\s+\[([ xX])\]\s*", "", lines[i].strip())
                box = "&#9745;" if mark else "&#9744;"
                items.append(f"{box} {inline(raw)}")
                i += 1
            out.append('<ul class="checklist">' + "".join(f"<li>{t}</li>" for t in items) + "</ul>")
            continue

        # Unordered list (with indented continuation lines folded into items)
        if re.match(r"^-\s+", stripped):
            items = []
            while i < len(lines):
                raw = lines[i].rstrip("\n")
                s = raw.strip()
                if re.match(r"^-\s+", s):
                    items.append(re.sub(r"^-\s+", "", s))
                    i += 1
                elif s and raw[:1] in (" ", "\t") and items:
                    items[-1] += " " + s
                    i += 1
                else:
                    break
            out.append("<ul>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ul>")
            continue

        # Ordered list (with indented continuation lines folded into items)
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines):
                raw = lines[i].rstrip("\n")
                s = raw.strip()
                if re.match(r"^\d+\.\s+", s):
                    items.append(re.sub(r"^\d+\.\s+", "", s))
                    i += 1
                elif s and raw[:1] in (" ", "\t") and items:
                    items[-1] += " " + s
                    i += 1
                else:
                    break
            out.append("<ol>" + "".join(f"<li>{inline(t)}</li>" for t in items) + "</ol>")
            continue

        # Blank line
        if stripped == "":
            i += 1
            continue

        # Paragraph (collect until blank / structural line)
        para = [line.strip()]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (nxt == "" or nxt.startswith(("#", ">", "|", "- ", "```", "<")) or
                    re.match(r"^\d+\.\s+", nxt) or re.match(r"^(---+|\*\*\*+)$", nxt)):
                break
            para.append(nxt)
            i += 1
        out.append("<p>" + inline(" ".join(para)) + "</p>")

    return "\n".join(out)


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} &middot; {site_name}</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <p class="brand"><a href="index.html">{site_name}</a></p>
  <nav>
    <a href="01-what-counts-as-cheating.html">01</a>
    <a href="02-school-policy-translation.html">02</a>
    <a href="03-ai-as-tutor-not-ghostwriter.html">03</a>
    <a href="04-outlining-and-feedback-loops.html">04</a>
    <a href="05-verifying-citations.html">05</a>
    <a href="06-disclosure-statements.html">06</a>
    <a href="07-honor-code-examples.html">07</a>
  </nav>
</header>
<main>
{fragment}
<p class="subfooter">{footer_note}</p>
</main>
<footer>
  <p>Educational resource &middot; MIT licensed &middot; Copyright (c) 2026 Asdale Dynamics, LLC. May be freely printed, projected, and adapted for classroom use.</p>
</footer>
</body>
</html>
"""


def build():
    if not ADOCS_OK():
        print("ERROR: docs/ missing expected files", file=sys.stderr)
        return 1

    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()

    md_files = sorted(DOCS.glob("*.md"))
    titles = {}
    for md in md_files:
        text = md.read_text(encoding="utf-8")
        # Use the first # heading (or first line) as the page title
        m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        titles[md.name] = m.group(1) if m else md.stem

    for md in md_files:
        text = md.read_text(encoding="utf-8").strip()
        lines = text.splitlines()
        # Drop the first H1 (goes into <title>); keep everything else
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        fragment = markdown_to_fragment("\n".join(lines))
        page = PAGE_TEMPLATE.format(
            title=html.escape(titles[md.name], quote=True),
            site_name=SITE_NAME,
            fragment=fragment,
            footer_note=FOOTER_NOTE,
        )
        (SITE / (md.stem + ".html")).write_text(page, encoding="utf-8")

    shutil.copy(ROOT / "site-assets" / "style.css", SITE / "style.css")
    print(f"Built {len(md_files)} pages into site/: " + ", ".join(sorted(p.name for p in SITE.glob('*.html'))))
    return 0


def ADOCS_OK():
    needed = [
        "index.md",
        "01-what-counts-as-cheating.md",
        "02-school-policy-translation.md",
        "03-ai-as-tutor-not-ghostwriter.md",
        "04-outlining-and-feedback-loops.md",
        "05-verifying-citations.md",
        "06-disclosure-statements.md",
        "07-honor-code-examples.md",
    ]
    return all((DOCS / n).is_file() for n in needed) and (ROOT / "site-assets" / "style.css").is_file()


if __name__ == "__main__":
    sys.exit(build())
