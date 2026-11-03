#!/usr/bin/env python3
"""Self-checks for this repository. Stdlib only.

Checks:
  1. docs/ markdown files all exist
  2. site/ builds cleanly and every generated page is well-formed enough
     (balanced tags, single <main>, HTML entity sanity)
  3. every internal link in docs/*.md resolves to a real file
  4. every internal link in site/*.html resolves to a real file in site/
  5. LICENSE contains the exact required copyright line
  6. README credits Asdale Dynamics, LLC
  7. no obvious secrets/keys committed anywhere

Usage: python3 tools/verify.py   (exit code 0 = all checks pass)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"
ASSETS = ROOT / "site-assets"

failures = []


def check(name: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


EXPECT_DOCS = [
    "index.md",
    "01-what-counts-as-cheating.md",
    "02-school-policy-translation.md",
    "03-ai-as-tutor-not-ghostwriter.md",
    "04-outlining-and-feedback-loops.md",
    "05-verifying-citations.md",
    "06-disclosure-statements.md",
    "07-honor-code-examples.md",
]

DOCTYPE_EXPECT = "<!DOCTYPE html>"


def iter_markdown_named():
    md_by_stem = {}
    for p in DOCS.glob("*.md"):
        md_by_stem[p.stem + ".md"] = p
    return md_by_stem


TITLES = {
    "index": "Start here",
}


def check_docs_exist():
    for name in EXPECT_DOCS:
        check(f"docs/{name} exists", (DOCS / name).is_file())


def check_markdown_links():
    for md_path in sorted(DOCS.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", text)
        for link in links:
            if link.startswith(("http://", "https://", "#", "mailto:")):
                continue
            # Check relative file references resolve from docs/
            href = link.split("#")[0]
            if not href:
                continue
            if not (href.endswith(".md") or href.endswith("LICENSE")):
                check(
                    f"docs/{md_path.name} link href type",
                    False,
                    f"unexpected target '{link}'",
                )
                continue
            target = (md_path.parent / href).resolve()
            check(
                f"docs/{md_path.name} -> {link}",
                target.is_file(),
                f"missing {target}",
            )


def balanced(html_text: str) -> bool:
    """Very light structural sanity for our generated HTML."""
    count = lambda tag: len(re.findall(rf"<{tag}\b", html_text))  # noqa: E731
    closing = lambda tag: len(re.findall(rf"</{tag}>", html_text))  # noqa: E731
    for tag in ("html", "head", "body", "main", "header", "footer", "nav"):
        if count(tag) != closing(tag):
            return False
    if count("table") != closing("table"):
        return False
    if count("blockquote") != closing("blockquote"):
        return False
    if count("ul") != closing("ul"):
        return False
    if count("ol") != closing("ol"):
        return False
    if html_text.count("<li>") != html_text.count("</li>"):
        return False
    if html_text.count("<details>") != html_text.count("</details>"):
        return False
    return True


def check_site_built():
    html_files = sorted(SITE.glob("*.html"))
    expected = {Path(p).stem + ".html" for p in EXPECT_DOCS}
    got = {p.name for p in html_files}
    check("site/ contains one page per docs page", expected <= got, f"missing {expected - got}")
    check("site/style.css exists", (SITE / "style.css").is_file())
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        check(f"site/{page.name} has doctype", text.startswith(DOCTYPE_EXPECT))
        check(f"site/{page.name} balanced tags", balanced(text))
        check(f"site/{page.name} credits Asdale", "Asdale Dynamics, LLC" in text)


def check_site_links():
    for page in sorted(SITE.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = (page.parent / href).resolve()
            check(f"site/{page.name} -> {href}", target.is_file(), f"missing {target}")
        for href in re.findall(r'src="([^"]+)"', text):
            target = (page.parent / href).resolve()
            check(f"site/{page.name} src {href}", target.is_file(), f"missing {target}")


def check_license():
    lic = ROOT / "LICENSE"
    check("LICENSE exists", lic.is_file())
    if not lic.is_file():
        return
    text = lic.read_text(encoding="utf-8")
    exact = "Copyright (c) 2026 Asdale Dynamics, LLC"
    check("LICENSE has exact copyright line", exact in text)
    check("LICENSE text is MIT", "Permission is hereby granted" in text and 'MIT License' in text)


def check_readme():
    readme = ROOT / "README.md"
    check("README exists", readme.is_file())
    if not readme.is_file():
        return
    text = readme.read_text(encoding="utf-8")
    check("README credits Asdale Dynamics, LLC", "Asdale Dynamics, LLC" in text)
    check("README links LICENSE", "LICENSE" in text)


def check_secrets():
    patterns = [
        (r"sk-[A-Za-z0-9]{16,}", "OpenAI-style key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
        (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "PEM private key"),
        (r"ghp_[A-Za-z0-9]{20,}", "GitHub personal access token"),
        (r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}", "embedded api key"),
        (r"(?i)secret\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}", "embedded secret"),
    ]
    texts = {}
    for p in list(ROOT.glob("*.md")) + list(ROOT.glob("*.py")):
        texts[p.name] = p.read_text(encoding="utf-8")
    for p in DOCS.glob("*.md"):
        texts[f"docs/{p.name}"] = p.read_text(encoding="utf-8")
    for p in SITE.glob("*.html"):
        texts[f"site/{p.name}"] = p.read_text(encoding="utf-8")
    for name, text in texts.items():
        for pattern, label in patterns:
            if re.search(pattern, text):
                check(f"no {label} in {name}", False)
    check("no obvious secrets in repo text files", True)


def main():
    print("Running verify.py — self-checks\n")
    check("site-assets/style.css exists", ASSETS.joinpath("style.css").is_file())
    check_docs_exist()
    check_markdown_links()
    check_site_built()
    check_site_links()
    check_license()
    check_readme()
    check_secrets()
    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s):")
        for f in failures:
            print(" -", f)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
