#!/usr/bin/env python3
"""Validate local Markdown image references in the knowledge repository."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_IMG = re.compile(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', re.IGNORECASE)
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

def clean_target(raw: str) -> str:
    target = raw.strip().split()[0].strip("<>")
    return unquote(target)

def strip_fenced_code(text: str) -> str:
    """Ignore examples inside fenced Markdown code blocks."""
    return re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", text)

def main() -> int:
    markdown_files = [p for p in ROOT.rglob("*.md")
                      if ".git" not in p.parts and ".venv" not in p.parts]
    referenced = set()
    broken = []
    unsupported = []

    for md in markdown_files:
        text = md.read_text(encoding="utf-8", errors="replace")
        text = strip_fenced_code(text)
        # Ignore inline-code examples such as `![diagram](images/example.svg)`;
        # these document Markdown syntax and are not actual asset references.
        text = re.sub(r"(?<!`)`+[^`\\n]*`+(?!`)", "", text)
        targets = IMAGE_LINK.findall(text) + HTML_IMG.findall(text)
        for raw in targets:
            target = clean_target(raw)
            if not target or target.startswith(("http://", "https://", "data:", "//", "#")):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0]
            candidate = (md.parent / target).resolve()
            try:
                candidate.relative_to(ROOT.resolve())
            except ValueError:
                broken.append(f"{md.relative_to(ROOT)} -> path escapes repository: {target}")
                continue
            if not candidate.is_file():
                # Distinguish case-only path mismatch where possible.
                parent = candidate.parent
                suggestion = ""
                if parent.is_dir():
                    matches = [p.name for p in parent.iterdir() if p.name.lower() == candidate.name.lower()]
                    if matches:
                        suggestion = f" (case mismatch? actual: {', '.join(matches)})"
                broken.append(f"{md.relative_to(ROOT)} -> missing: {target}{suggestion}")
                continue
            referenced.add(candidate)
            if candidate.suffix.lower() not in SUPPORTED:
                unsupported.append(f"{md.relative_to(ROOT)} -> unusual image format: {target}")

    all_images = {p.resolve() for p in ROOT.rglob("*")
                  if p.is_file() and p.suffix.lower() in SUPPORTED
                  and ".git" not in p.parts and ".venv" not in p.parts}
    orphaned = sorted(all_images - referenced)

    print(f"Markdown files scanned: {len(markdown_files)}")
    print(f"Image files found: {len(all_images)}")
    print(f"Referenced image files: {len(referenced)}")
    if unsupported:
        print("\nWarnings: unusual image formats")
        print("\n".join(f"  - {item}" for item in unsupported))
    if orphaned:
        print("\nWarnings: image files not referenced by Markdown (not a failure)")
        print("\n".join(f"  - {p.relative_to(ROOT)}" for p in orphaned))
    if broken:
        print("\nERROR: broken local image references")
        print("\n".join(f"  - {item}" for item in broken))
        return 1
    print("\nPASS: all local Markdown image references resolve to existing files.")
    # The existing GitHub Actions workflow invokes this script, so run the
    # repository-wide Markdown link check here without needing workflow edits.
    from check_markdown_links import main as check_markdown_links
    return check_markdown_links()

if __name__ == "__main__":
    sys.exit(main())
