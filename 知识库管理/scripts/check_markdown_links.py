#!/usr/bin/env python3
"""Validate local Markdown links in the knowledge repository.

Checks inline Markdown links to repository files/directories. External URLs,
mailto links, and pure in-page anchors are ignored. Fragment targets are
checked for file existence only; heading-anchor correctness is not inferred.
"""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
LINK = re.compile(r'(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)')

def clean_target(raw: str) -> str:
    target = raw.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    # Remove an optional Markdown title after the URL/path.
    target = re.split(r'\s+(?=["\'])', target, maxsplit=1)[0]
    return unquote(target)

def strip_fenced_code(text: str) -> str:
    """Ignore link examples inside fenced Markdown code blocks."""
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)

def main() -> int:
    markdown_files = sorted(p for p in ROOT.rglob("*.md")
                            if ".git" not in p.parts and ".venv" not in p.parts)
    broken = []
    checked = 0
    for md in markdown_files:
        try:
            content = strip_fenced_code(md.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            broken.append(f"{md.relative_to(ROOT)} -> cannot read Markdown: {exc}")
            continue
        for raw in LINK.findall(content):
            target = clean_target(raw)
            if not target or target.startswith(("#", "//")):
                continue
            parsed = urlparse(target)
            if parsed.scheme or parsed.netloc:
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            candidate = (md.parent / path_part).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                broken.append(f"{md.relative_to(ROOT)} -> path escapes repository: {path_part}")
                continue
            checked += 1
            if not candidate.exists():
                broken.append(f"{md.relative_to(ROOT)} -> missing: {path_part}")
    print(f"Markdown files scanned: {len(markdown_files)}")
    print(f"Local Markdown links checked: {checked}")
    if broken:
        print("\nERROR: broken local Markdown links")
        print("\n".join(f"  - {item}" for item in broken))
        return 1
    print("\nPASS: all checked local Markdown links resolve.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
