#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
fetch_transcript.py

Fetch and process YouTube video transcripts using youtube-transcript-api via uvx.
Outputs clean Markdown formatted with Obsidian YAML frontmatter and timestamp blocks.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.parse
import subprocess
import argparse
from datetime import datetime
from pathlib import Path


def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube 11-character video ID from various URL patterns or raw ID."""
    url_or_id = url_or_id.strip()
    
    # Raw 11-char ID
    if re.fullmatch(r"[\w-]{11}", url_or_id):
        return url_or_id
        
    patterns = [
        r"(?:v=|\/v\/|youtu\.be\/|\/embed\/|\/live\/|\/shorts\/)([\w-]{11})",
        r"^([\w-]{11})$"
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
            
    raise ValueError(f"Could not extract a valid YouTube video ID from: {url_or_id}")


def fetch_oembed_metadata(video_id: str) -> dict:
    """Fetch video title and author from YouTube oEmbed API."""
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "title": data.get("title", f"YouTube Video {video_id}"),
                "author": data.get("author_name", "YouTube"),
                "author_url": data.get("author_url", "")
            }
    except Exception as e:
        print(f"Warning: failed to fetch video metadata ({e}); falling back to placeholder title/author.", file=sys.stderr)
        return {
            "title": f"YouTube Video {video_id}",
            "author": "YouTube",
            "author_url": ""
        }


def fetch_transcript_json(video_id: str, languages: list[str] = None) -> list[dict]:
    """Fetch raw transcript JSON via uvx running youtube-transcript-api."""
    cmd = [
        "uvx",
        "--from",
        "youtube-transcript-api",
        "youtube_transcript_api",
        "--format",
        "json"
    ]
    if languages:
        cmd.extend(["--languages"] + languages + ["--", video_id])
    else:
        cmd.append(video_id)

    proc = subprocess.run(cmd, capture_output=True, text=True)
    raw_output = proc.stdout.strip()

    if "Could not retrieve a transcript" in raw_output or "blocking requests from your IP" in raw_output:
        raise RuntimeError(
            f"YouTube blocked the request or transcript unavailable for {video_id}.\n"
            "YouTube frequently rate-limits cloud IPs. Retry in a few minutes, or download the raw JSON elsewhere and pass it via --input-json."
        )

    if proc.returncode != 0:
        err = proc.stderr.strip() or raw_output
        raise RuntimeError(f"youtube-transcript-api failed (exit code {proc.returncode}): {err}")

    try:
        data = json.loads(raw_output)
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
            return data[0]
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to parse transcript JSON: {e}\nRaw output: {raw_output[:300]}")


def format_timestamp(seconds: float) -> str:
    """Format seconds into MM:SS or H:MM:SS format."""
    total_sec = int(round(seconds))
    hrs = total_sec // 3600
    mins = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def group_transcript_segments(items: list[dict], max_gap: float = 2.5) -> list[dict]:
    """
    Groups fragmented subtitle segments into coherent sentences/paragraphs.
    Splits on speaker cues (>>), long pauses, or sentence-ending punctuation.
    """
    if not items:
        return []

    blocks = []
    current_block = {
        "start": items[0]["start"],
        "text_parts": [],
        "last_end": items[0]["start"] + items[0].get("duration", 0)
    }

    for item in items:
        text = item["text"].strip()
        start = item["start"]
        duration = item.get("duration", 0)
        end = start + duration

        is_speaker_switch = text.startswith(">>")
        if is_speaker_switch:
            text = text[2:].strip()

        # Decide whether to start a new block
        should_split = False
        if is_speaker_switch and current_block["text_parts"]:
            should_split = True
        elif (start - current_block["last_end"] > max_gap) and current_block["text_parts"]:
            should_split = True
        elif current_block["text_parts"] and re.search(r"[\.\?\!]$", current_block["text_parts"][-1]):
            # If previous segment ended with punctuation and length exceeds threshold
            current_len = sum(len(p) for p in current_block["text_parts"])
            if current_len > 180:
                should_split = True

        if should_split:
            full_text = " ".join(current_block["text_parts"]).strip()
            if full_text:
                blocks.append({
                    "start": current_block["start"],
                    "text": full_text
                })
            current_block = {
                "start": start,
                "text_parts": [],
                "last_end": end
            }

        if text:
            current_block["text_parts"].append(text)
        current_block["last_end"] = end

    # Flush final block
    if current_block["text_parts"]:
        full_text = " ".join(current_block["text_parts"]).strip()
        if full_text:
            blocks.append({
                "start": current_block["start"],
                "text": full_text
            })

    return blocks


def yaml_str(value: str) -> str:
    """Quote a string as a YAML double-quoted scalar (JSON strings are valid YAML)."""
    return json.dumps(value, ensure_ascii=False)


def sanitize_filename(name: str) -> str:
    """Sanitize title for file system usage."""
    s = re.sub(r'[\/\\:\*\?"<>\|]', ' ', name)
    s = re.sub(r'\s+', ' ', s).strip()
    return s[:120]


def main():
    parser = argparse.ArgumentParser(description="Fetch and format YouTube video transcripts.")
    parser.add_argument("url_or_id", nargs="?", default="", help="YouTube video URL or 11-character video ID")
    parser.add_argument("--input-json", help="Path to pre-downloaded raw transcript JSON file")
    parser.add_argument("-o", "--output", help="Output Markdown file path")
    parser.add_argument("-l", "--languages", default="en,zh-Hans,zh-Hant,zh,ja",
                        help="Comma-separated language codes to try (default: en,zh-Hans,zh-Hant,zh,ja)")
    parser.add_argument("--format", choices=["timestamps", "clean", "json"], default="timestamps",
                        help="Output format: timestamps (default), clean, or json")
    parser.add_argument("--max-gap", type=float, default=2.5,
                        help="Max pause gap in seconds between captions before splitting block (default: 2.5)")

    args = parser.parse_args()

    if not args.url_or_id and not args.input_json:
        parser.error("Either url_or_id or --input-json must be provided.")

    if args.input_json:
        with open(args.input_json, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                items = data[0]
            else:
                items = data
        video_id = extract_video_id(args.url_or_id) if args.url_or_id else "local"
        title = Path(args.input_json).stem
        author = "YouTube"
    else:
        video_id = extract_video_id(args.url_or_id)
        lang_list = [l.strip() for l in args.languages.split(",") if l.strip()]

        print(f"Fetching metadata for video ID: {video_id}...", file=sys.stderr)
        meta = fetch_oembed_metadata(video_id)
        title = meta["title"]
        author = meta["author"]

        print(f"Fetching transcript for: {title}...", file=sys.stderr)
        items = fetch_transcript_json(video_id, lang_list)
        print(f"Retrieved {len(items)} caption entries.", file=sys.stderr)

    if args.format == "json":
        output_content = json.dumps(items, indent=2, ensure_ascii=False)
    else:
        blocks = group_transcript_segments(items, max_gap=args.max_gap)
        today = datetime.now().strftime("%Y-%m-%d")

        md_lines = [
            "---",
            f"title: {yaml_str(title)}",
            f'source: "https://www.youtube.com/watch?v={video_id}"',
            "author:",
            f"  - {yaml_str(f'[[{author}]]')}",
            f"created: {today}",
            f"description: {yaml_str(f'Transcript for YouTube video: {title} by {author}.')}",
            "tags:",
            '  - "clippings"',
            '  - "voices"',
            '  - "youtube"',
            "---",
            "",
            "## 逐字稿 (Transcript)",
            ""
        ]

        for b in blocks:
            ts = format_timestamp(b["start"])
            text = b["text"]
            if args.format == "timestamps":
                md_lines.append(f"**{ts}** · {text}")
                md_lines.append("")
            else:
                md_lines.append(text)
                md_lines.append("")

        output_content = "\n".join(md_lines)

    # Determine destination path
    if args.output:
        out_path = Path(args.output)
    else:
        clean_title = sanitize_filename(title)
        out_path = Path(f"inbox/clippings/{clean_title}.md")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully saved transcript to: {out_path.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
