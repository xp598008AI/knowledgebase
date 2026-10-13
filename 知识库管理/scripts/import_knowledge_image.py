#!/usr/bin/env python3
"""Import an image into the knowledge base and embed it in a Markdown document.

Run from a local clone of the repository:
  python 知识库管理/scripts/import_knowledge_image.py /path/to/image.png 04-process/ASPICE.md --title "ASPICE process mind map"
Add --commit to create a local git commit after staging the image and Markdown file.
"""
from __future__ import annotations
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "technical-image"

def run_git(args: list[str]) -> None:
    subprocess.run(["git", *args], cwd=ROOT, check=True)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="Path to a local image file")
    parser.add_argument("document", help="Markdown document path relative to repository root")
    parser.add_argument("--title", required=True, help="Human-readable image title")
    parser.add_argument("--filename", help="Optional destination filename; defaults to title + original extension")
    parser.add_argument("--commit", action="store_true", help="Stage and commit image + Markdown changes locally")
    args = parser.parse_args()

    source = Path(args.image).expanduser().resolve()
    document = (ROOT / args.document).resolve()
    try:
        document.relative_to(ROOT.resolve())
    except ValueError:
        parser.error("document must be inside the repository")
    if not source.is_file():
        parser.error(f"image file does not exist: {source}")
    if source.suffix.lower() not in SUPPORTED:
        parser.error(f"unsupported image extension: {source.suffix}; supported: {', '.join(sorted(SUPPORTED))}")
    if not document.is_file() or document.suffix.lower() != ".md":
        parser.error(f"document must be an existing Markdown file inside the repository: {document}")

    image_dir = document.parent / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    name = args.filename or f"{slugify(args.title)}{source.suffix.lower()}"
    if Path(name).name != name or Path(name).suffix.lower() not in SUPPORTED:
        parser.error("--filename must be a filename with a supported image extension, not a path")
    destination = image_dir / name
    if destination.exists():
        parser.error(f"destination already exists; choose another --filename to avoid overwriting: {destination.relative_to(ROOT)}")
    shutil.copy2(source, destination)

    relative_image = destination.relative_to(document.parent).as_posix()
    markdown = document.read_text(encoding="utf-8")
    reference = f"![{args.title}]({relative_image})"
    if reference in markdown:
        destination.unlink()
        parser.error("the same image reference already exists in the document; no changes made")
    block = f"\n\n## 图片资料\n\n{reference}\n\n**图示说明：** {args.title}。请核对图中文字、单位、信号方向和适用标准版本；AI 生成图应作为概念示意，不替代正式标准或实测证据。\n"
    if re.search(r"^## 图片资料\s*$", markdown, flags=re.MULTILINE):
        markdown = re.sub(r"(^## 图片资料\s*$)", r"\1" + f"\n\n{reference}\n\n**图示说明：** {args.title}。请核对图中文字、单位、信号方向和适用标准版本；AI 生成图应作为概念示意，不替代正式标准或实测证据。", markdown, count=1, flags=re.MULTILINE)
    else:
        markdown = markdown.rstrip() + block
    document.write_text(markdown, encoding="utf-8")

    print(f"Image copied: {destination.relative_to(ROOT)}")
    print(f"Markdown updated: {document.relative_to(ROOT)}")
    print(f"Reference: {reference}")
    if args.commit:
        run_git(["add", str(destination.relative_to(ROOT)), str(document.relative_to(ROOT))])
        run_git(["commit", "-m", f"docs: add image to {document.stem}"])
        print("Local git commit created. Push it with: git push")
    else:
        print("Next: review the Markdown, then git add / git commit / git push.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Git command failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode)
