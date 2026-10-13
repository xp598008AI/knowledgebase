#!/usr/bin/env python3
"""Upload a local technical image and metadata to the GitHub archive queue in one commit.

Requires Python 3.10+ and a GitHub fine-grained token with Contents: read/write
permission for xp598008AI/knowledgebase. Set GH_TOKEN or GITHUB_TOKEN in the
environment; never put a token in a command-line argument or source file.

Example:
  python 知识库管理/scripts/push_technical_image.py ./evcc.svg \
    --title "EVCC 系统架构图" \
    --document "04-充电系统与产品/EVCC/README.md" \
    --source "ChatGPT generated concept illustration" --status Draft
"""
from __future__ import annotations
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path, PurePosixPath

OWNER = "xp598008AI"
REPO = "knowledgebase"
BRANCH = "main"
QUEUE = "06-创新、扩展与职业竞争/技术图片资产库/待归档"
SUPPORTED = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}
MAX_BYTES = 20 * 1024 * 1024
API = f"https://api.github.com/repos/{OWNER}/{REPO}"

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9一-龥_-]+", "-", value.strip()).strip("-_")
    return (value[:90] or "technical-image")

def request_json(url: str, token: str, method: str = "GET", payload=None):
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=body, method=method, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "knowledgebase-technical-image-uploader",
        **({"Content-Type": "application/json"} if body is not None else {}),
    })
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:1500]
        raise RuntimeError(f"GitHub API returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach GitHub API: {exc.reason}") from exc

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", help="Local image file, e.g. ./evcc.svg")
    p.add_argument("--title", required=True, help="Human-readable image title")
    p.add_argument("--document", required=True, help="Existing repository Markdown path")
    p.add_argument("--source", default="Not specified", help="Image source/provenance")
    p.add_argument("--status", default="Draft", choices=["Draft", "Reviewed", "Approved"], help="Review state")
    p.add_argument("--filename", help="Optional destination filename")
    p.add_argument("--branch", default=BRANCH, help="Target branch (default: main)")
    args = p.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: set GH_TOKEN or GITHUB_TOKEN to a repository-scoped GitHub token.", file=sys.stderr)
        return 2
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        print(f"ERROR: image file does not exist: {image}", file=sys.stderr)
        return 2
    suffix = image.suffix.lower()
    if suffix not in SUPPORTED:
        print(f"ERROR: unsupported image format {suffix!r}; use PNG/JPG/JPEG/WEBP/GIF/SVG.", file=sys.stderr)
        return 2
    size = image.stat().st_size
    if size <= 0 or size > MAX_BYTES:
        print("ERROR: image must be non-empty and no larger than 20 MiB.", file=sys.stderr)
        return 2
    document = PurePosixPath(args.document)
    if document.is_absolute() or ".." in document.parts or document.suffix.lower() != ".md":
        print("ERROR: --document must be a safe repository-relative Markdown path.", file=sys.stderr)
        return 2

    try:
        # Confirm target Markdown exists before creating any objects.
        encoded_doc_path = "/".join(urllib.parse.quote(part, safe="") for part in document.parts)
        doc_url = f"{API}/contents/{encoded_doc_path}?ref={urllib.parse.quote(args.branch, safe='')}"
        request_json(doc_url, token)

        filename = args.filename or f"{slugify(args.title)}{suffix}"
        if Path(filename).name != filename or Path(filename).suffix.lower() not in SUPPORTED:
            raise RuntimeError("--filename must be a simple filename with a supported image extension.")
        queue_image = f"{QUEUE}/{filename}"
        queue_meta = f"{QUEUE}/{Path(filename).stem}.json"
        if queue_image == queue_meta:
            raise RuntimeError("Image filename conflicts with metadata filename.")
        ref = request_json(f"{API}/git/ref/heads/{urllib.parse.quote(args.branch, safe='')}", token)
        parent_sha = ref["object"]["sha"]
        parent = request_json(f"{API}/git/commits/{parent_sha}", token)
        base_tree = parent["tree"]["sha"]

        image_b64 = base64.b64encode(image.read_bytes()).decode("ascii")
        image_blob = request_json(f"{API}/git/blobs", token, "POST", {"content": image_b64, "encoding": "base64"})
        metadata = {
            "title": args.title.strip(),
            "document": document.as_posix(),
            "source": args.source,
            "status": args.status,
            "filename": filename,
        }
        meta_blob = request_json(f"{API}/git/blobs", token, "POST", {
            "content": json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            "encoding": "utf-8",
        })
        tree = request_json(f"{API}/git/trees", token, "POST", {
            "base_tree": base_tree,
            "tree": [
                {"path": queue_image, "mode": "100644", "type": "blob", "sha": image_blob["sha"]},
                {"path": queue_meta, "mode": "100644", "type": "blob", "sha": meta_blob["sha"]},
            ],
        })
        commit = request_json(f"{API}/git/commits", token, "POST", {
            "message": f"docs: queue technical image - {args.title.strip()}",
            "tree": tree["sha"],
            "parents": [parent_sha],
        })
        request_json(f"{API}/git/refs/heads/{urllib.parse.quote(args.branch, safe='')}", token, "PATCH", {
            "sha": commit["sha"], "force": False,
        })
        print("PASS: image and metadata were pushed in one Git commit.")
        print(f"Commit: https://github.com/{OWNER}/{REPO}/commit/{commit['sha']}")
        print(f"Queue image: {queue_image}")
        print(f"Target document: {document.as_posix()}")
        print("The GitHub Actions archive workflow should now move the image, insert it into the document, update the asset index, and run link checks.")
        return 0
    except (RuntimeError, KeyError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
