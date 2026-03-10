#!/usr/bin/env python3
"""
Light Phone 2 Notes Exporter (Standalone CLI)

Usage:
  1. Log into dashboard.thelightphone.com in your browser
  2. Open DevTools (F12) > Network tab > click any action
  3. Copy the Authorization header value (the part after "Bearer ")
  4. Copy your device ID from the URL (the UUID after /devices/)
  5. Run:
     python export_notes.py --token YOUR_TOKEN --device-id YOUR_DEVICE_ID --output ./my-notes
"""

import argparse
import json
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

API_BASE = "https://production.lightphonecloud.com/api"


def api_get(path, token):
    url = f"{API_BASE}/{path}"
    req = Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"  API error {e.code} for {path}: {e.read().decode()[:200]}")
        return None


def find_notes_device_tool_id(device_id, token):
    devices = api_get("devices", token)
    if not devices or "data" not in devices:
        print("Error: Could not fetch devices.")
        sys.exit(1)

    device = None
    for d in devices["data"]:
        if d["id"] == device_id:
            device = d
            break

    if not device:
        print(f"Error: Device {device_id} not found.")
        sys.exit(1)

    device_tool_ids = [
        dt["id"] for dt in device["relationships"]["device_tools"]["data"]
    ]

    print(f"Found {len(device_tool_ids)} device tools. Checking which one is Notes...")

    for dt_id in device_tool_ids:
        notes = api_get(f"notes?device_tool_id={dt_id}", token)
        if notes and "data" in notes and len(notes["data"]) > 0:
            print(f"  Found Notes tool: {dt_id} ({len(notes['data'])} notes)")
            return dt_id, notes["data"]

    print("Error: No Notes tool found for this device.")
    sys.exit(1)


def download_note_content(note_id, token):
    result = api_get(f"notes/{note_id}/generate_presigned_get_url", token)
    if not result or "presigned_get_url" not in result:
        return None
    url = result["presigned_get_url"]
    with urlopen(url) as resp:
        return resp.read().decode()


def slugify(text, max_len=40):
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:max_len] or "untitled"


def main():
    parser = argparse.ArgumentParser(description="Export Light Phone 2 notes")
    parser.add_argument("--token", required=True, help="Bearer token from dashboard")
    parser.add_argument("--device-id", required=True, help="Device UUID from dashboard URL")
    parser.add_argument("--output", default="./lp2-notes", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("=" * 50)
    print("Light Phone 2 Notes Exporter")
    print("=" * 50)

    dt_id, notes = find_notes_device_tool_id(args.device_id, args.token)
    print(f"\nDownloading {len(notes)} notes...\n")

    exported = []
    for i, note in enumerate(notes):
        note_id = note["id"]
        note_type = note["attributes"]["note_type"]
        date = note["attributes"]["updated_at"][:10]

        print(f"  [{i+1}/{len(notes)}] {date} ({note_type}) ", end="")

        if note_type == "audio":
            print("Warning: Audio - cannot export via API")
            exported.append({"id": note_id, "date": date, "type": "audio", "content": None})
            continue

        content = download_note_content(note_id, token=args.token)
        if content:
            print(f"OK ({len(content)} chars)")
            exported.append({"id": note_id, "date": date, "type": "text", "content": content})
        else:
            print("Failed")

    print(f"\nWriting {len(exported)} notes to {args.output}/")
    print("NOTE: This exports raw content only. For proofreading/translation, use the skill with Claude.\n")

    for i, note in enumerate(exported):
        slug = slugify(note["content"][:40]) if note["content"] else "audio-note"
        filename = f"{i+1:02d}_{note['date']}_{slug}.md"
        filepath = os.path.join(args.output, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            if note["type"] == "audio":
                f.write(f"# Audio Note\n**Date:** {note['date']} | **Type:** audio | **ID:** {note['id'][:8]}\n\n")
                f.write("> Audio notes cannot be exported via the Light Phone API.\n")
            else:
                first_line = note["content"].split(".")[0][:60]
                f.write(f"# {first_line}\n**Date:** {note['date']} | **Type:** text | **ID:** {note['id'][:8]}\n\n---\n\n")
                f.write(f"## Original\n{note['content']}\n")

        print(f"  Done: {filename}")

    print(f"\nDone! {len(exported)} files saved to {args.output}/")


if __name__ == "__main__":
    main()
