#!/usr/bin/env python3
"""Archive staged technical images into target Markdown documents.

Queue format:
  06-创新、扩展与职业竞争/技术图片资产库/待归档/<file>.<ext>
  06-创新、扩展与职业竞争/技术图片资产库/待归档/<file>.json

JSON required fields: title, document. Optional: source, status, filename.
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "06-创新、扩展与职业竞争" / "技术图片资产库" / "待归档"
ASSET_INDEX = ROOT / "06-创新、扩展与职业竞争" / "技术图片资产库" / "README.md"
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
MAX_BYTES = 20 * 1024 * 1024

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9一-龥_-]+", "-", value.strip()).strip("-_")
    return value[:100] or "technical-image"

def inside_root(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False

def relative_url(from_dir: Path, target: Path) -> str:
    return Path(__import__("os").path.relpath(target, from_dir)).as_posix()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Perform the archive; without this flag, validate only")
    args = parser.parse_args()
    if not QUEUE.exists():
        print(f"Queue directory does not exist: {QUEUE.relative_to(ROOT)}")
        return 0
    images = sorted(p for p in QUEUE.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not images:
        print("No staged images found; nothing to archive.")
        return 0
    plans = []
    errors = []
    for image in images:
        sidecar = image.with_suffix(".json")
        if not sidecar.is_file():
            errors.append(f"{image.relative_to(ROOT)}: missing metadata sidecar {sidecar.name}")
            continue
        try:
            metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{sidecar.relative_to(ROOT)}: invalid JSON ({exc})")
            continue
        title = metadata.get("title")
        document_rel = metadata.get("document")
        if not isinstance(title, str) or not title.strip() or not isinstance(document_rel, str):
            errors.append(f"{sidecar.relative_to(ROOT)}: required fields 'title' and 'document' must be non-empty strings")
            continue
        target = (ROOT / PurePosixPath(document_rel)).resolve()
        if not inside_root(target) or target.suffix.lower() != ".md" or not target.is_file():
            errors.append(f"{sidecar.relative_to(ROOT)}: target document must be an existing Markdown file inside the repository")
            continue
        if image.stat().st_size > MAX_BYTES:
            errors.append(f"{image.relative_to(ROOT)}: image exceeds 20 MiB limit")
            continue
        filename = metadata.get("filename") or f"{slugify(title)}{image.suffix.lower()}"
        if Path(filename).name != filename or Path(filename).suffix.lower() not in SUPPORTED:
            errors.append(f"{sidecar.relative_to(ROOT)}: invalid filename")
            continue
        destination_dir = target.parent / "images"
        destination = destination_dir / filename
        if destination.exists():
            errors.append(f"{sidecar.relative_to(ROOT)}: destination already exists: {destination.relative_to(ROOT)}")
            continue
        plans.append((image, sidecar, target, destination, metadata))
    if errors:
        print("ERROR: image archive validation failed:")
        print("\n".join(f" - {e}" for e in errors))
        return 1
    print(f"Validated {len(plans)} staged image(s).")
    for image, sidecar, target, destination, metadata in plans:
        print(f"  {image.relative_to(ROOT)} -> {destination.relative_to(ROOT)} -> {target.relative_to(ROOT)}")
    if not args.apply:
        print("Dry run only. Re-run with --apply to archive.")
        return 0
    index_lines = []
    for image, sidecar, target, destination, metadata in plans:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(image), str(destination))
        image_ref = relative_url(target.parent, destination)
        title = metadata["title"].strip()
        source = metadata.get("source", "Not specified")
        status = metadata.get("status", "Draft")
        block = f"![{title}]({image_ref})\n\n**图示说明：** {title}。来源：{source}。审核状态：{status}。请核对图中文字、单位、信号方向及适用标准版本。"
        text = target.read_text(encoding="utf-8")
        heading = "## 图片资料"
        if re.search(r"^## 图片资料\s*$", text, flags=re.MULTILINE):
            text = re.sub(r"(^## 图片资料\s*$)", lambda m: m.group(1) + "\n\n" + block, text, count=1, flags=re.MULTILINE)
        else:
            text = text.rstrip() + "\n\n" + heading + "\n\n" + block + "\n"
        target.write_text(text, encoding="utf-8")
        doc_link = relative_url(ASSET_INDEX.parent, target)
        img_link = relative_url(ASSET_INDEX.parent, destination)
        index_lines.append(f"- [{title}]({doc_link}) · [图片文件]({img_link}) · 状态：{status} · 来源：{source}")
        sidecar.unlink()
    if index_lines:
        index = ASSET_INDEX.read_text(encoding="utf-8") if ASSET_INDEX.exists() else "# 技术图片资产库\n"
        heading = "## 自动归档记录"
        if heading not in index:
            index = index.rstrip() + "\n\n" + heading + "\n"
        index = index.rstrip() + "\n" + "\n".join(index_lines) + "\n"
        ASSET_INDEX.parent.mkdir(parents=True, exist_ok=True)
        ASSET_INDEX.write_text(index, encoding="utf-8")
    for directory in sorted((p for p in QUEUE.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            directory.rmdir()
        except OSError:
            pass
    try:
        QUEUE.rmdir()
    except OSError:
        pass
    print(f"PASS: archived {len(plans)} image(s), updated Markdown and asset index.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
