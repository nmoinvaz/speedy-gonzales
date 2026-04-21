#!/usr/bin/env python3
"""Download all attachments and inline media from a Jira ticket.

Fetches the issue JSON with renderedFields and changelog, finds every
attachment ID and filename, downloads each attachment via its 303 redirect to
the signed media URL, and extracts any .zip archives into sibling subdirectories.

Sources merged for attachment discovery (in priority order):
  1. fields.attachment[] — explicit attachments on the issue (authoritative
     filenames). May be null when the Attachment system field is hidden by
     the project's field configuration, even though attachments exist.
  2. changelog histories — every attachment add/remove event. Authoritative
     even when fields.attachment[] is null. Each surviving entry is confirmed
     to still exist via a metadata fetch so deleted files are skipped.
  3. Rendered HTML in renderedFields.description and each comment body —
     inline images and file links. Recovers filenames when (1) and (2) miss
     something.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

JIRA_API_BASE = "https://api.atlassian.com/ex/jira"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_issue(cloud_id: str, issue_key: str, token: str, out_path: Path) -> dict:
    url = (
        f"{JIRA_API_BASE}/{cloud_id}/rest/api/3/issue/{issue_key}"
        "?expand=renderedFields,changelog&fields=attachment,description,comment"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    out_path.write_bytes(data)
    return json.loads(data)


def attachment_exists(cloud_id: str, aid: str, token: str) -> bool:
    url = f"{JIRA_API_BASE}/{cloud_id}/rest/api/3/attachment/{aid}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


def extract(data: dict, cloud_id: str, token: str) -> dict[str, str]:
    attachments: dict[str, str] = {}

    for a in data.get("fields", {}).get("attachment") or []:
        aid = str(a.get("id"))
        filename = a.get("filename")
        if aid and filename:
            attachments[aid] = filename

    # The changelog is authoritative even when fields.attachment[] is null
    # (which happens when the Attachment field is hidden by the project's
    # field configuration). Each "Attachment" history item records an add
    # (from=null, to=<id>) or a remove (to=null, from=<id>). Walking the
    # history in order lets us track which adds were not later removed.
    live_ids: dict[str, str] = {}
    for history in (data.get("changelog") or {}).get("histories") or []:
        for item in history.get("items") or []:
            if item.get("field") != "Attachment":
                continue
            added_id = item.get("to")
            added_name = item.get("toString")
            removed_id = item.get("from")
            if added_id and added_name:
                live_ids[str(added_id)] = added_name
            if removed_id:
                live_ids.pop(str(removed_id), None)

    # Cross-check against the metadata endpoint to skip attachments that were
    # deleted without a corresponding changelog remove, or that the caller
    # lacks permission to download.
    for aid, name in live_ids.items():
        if aid in attachments:
            continue
        if attachment_exists(cloud_id, aid, token):
            attachments[aid] = name

    rendered = data.get("renderedFields") or {}
    parts: list[str] = []
    desc = rendered.get("description") or ""
    if isinstance(desc, str):
        parts.append(desc)
    for c in (rendered.get("comment") or {}).get("comments") or []:
        body = c.get("body", "")
        if isinstance(body, str) and body:
            parts.append(body)
    html = "\n".join(parts)

    for m in re.finditer(r'attachment/content/(\d+)"[^>]*?alt="([^"]+)"', html):
        attachments.setdefault(m.group(1), m.group(2))
    for m in re.finditer(
        r'attachment/content/(\d+)"[^>]*?data-attachment-name="([^"]+)"', html
    ):
        attachments.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r"attachment/content/(\d+)", html):
        attachments.setdefault(m.group(1), f"attachment-{m.group(1)}")

    return attachments


def download_attachment(cloud_id: str, aid: str, token: str, dest: Path) -> int:
    # The attachment content endpoint returns a 303 redirect to a signed media
    # URL. The signed URL rejects the Authorization header, so we resolve the
    # redirect ourselves and issue a second, unauthenticated request.
    url = f"{JIRA_API_BASE}/{cloud_id}/rest/api/3/attachment/content/{aid}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    opener = urllib.request.build_opener(_NoRedirect)
    redirect_url: str | None = None
    try:
        with opener.open(req) as resp:
            redirect_url = resp.headers.get("Location")
    except urllib.error.HTTPError as e:
        if 300 <= e.code < 400:
            redirect_url = e.headers.get("Location")
        else:
            raise
    if not redirect_url:
        raise RuntimeError(f"no redirect returned for attachment {aid}")

    size = 0
    with urllib.request.urlopen(redirect_url) as resp, dest.open("wb") as f:
        while chunk := resp.read(64 * 1024):
            f.write(chunk)
            size += len(chunk)
    return size


def extract_zip(zip_path: Path) -> Path:
    dest = zip_path.with_suffix("")
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    return dest


def _fmt_size(n: float) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024 or unit == "G":
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}G"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--issue-key", required=True)
    ap.add_argument("--cloud-id", required=True)
    ap.add_argument("--token", required=True)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()

    out: Path = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    data = fetch_issue(args.cloud_id, args.issue_key, args.token, out / "_issue.json")

    attachments = extract(data, args.cloud_id, args.token)
    if not attachments:
        print("No attachments or inline media found.")
        return 0

    downloaded: list[tuple[str, int]] = []
    for aid, raw_name in sorted(attachments.items()):
        # Guard against path traversal from unexpected filenames.
        name = Path(raw_name).name or f"attachment-{aid}"
        dest = out / name
        size = download_attachment(args.cloud_id, aid, args.token, dest)
        downloaded.append((name, size))
        print(f"  {name} ({_fmt_size(size)})")

    extracted: list[Path] = []
    for name, _ in downloaded:
        if name.lower().endswith(".zip"):
            dest = extract_zip(out / name)
            extracted.append(dest)
            print(f"  extracted {name} -> {dest.name}/")

    total = sum(s for _, s in downloaded)
    print()
    print(f"Downloaded {len(downloaded)} file(s), {_fmt_size(total)} total, to {out}")
    if extracted:
        print(f"Extracted {len(extracted)} zip archive(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
