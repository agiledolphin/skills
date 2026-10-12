#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""
format_transcript.py

Format a YouTube transcript extracted by extract_transcript_panel.js (via agent-browser)
into clean Markdown with Obsidian YAML frontmatter and timestamp blocks.
Video title and author are fetched from YouTube oEmbed.
"""

import sys
import re
import json
import urllib.request
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


def load_input_json(path: str) -> list[dict]:
    """
    Load the output of extract_transcript_panel.js saved from `agent-browser eval`:
    a JSON string wrapping [{text, start, duration}], or {"error": ...} on failure.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, str):
        data = json.loads(data)
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(f"Browser transcript extraction failed: {data['error']}")
    if not isinstance(data, list):
        raise ValueError(f"Unexpected transcript JSON in {path}: expected a list of segments")
    return data


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
    parser = argparse.ArgumentParser(description="Format a browser-extracted YouTube transcript as Markdown.")
    parser.add_argument("url_or_id", help="YouTube video URL or 11-character video ID")
    parser.add_argument("--input-json", required=True,
                        help="Transcript JSON saved from `agent-browser eval` running extract_transcript_panel.js")
    parser.add_argument("-o", "--output",
                        help="Output file path, or a directory to save {Sanitized_Title}.md into (default: current directory)")
    parser.add_argument("--format", choices=["timestamps", "clean", "json"], default="timestamps",
                        help="Output format: timestamps (default), clean, or json")
    parser.add_argument("--max-gap", type=float, default=2.5,
                        help="Max pause gap in seconds between captions before splitting block (default: 2.5)")

    args = parser.parse_args()

    video_id = extract_video_id(args.url_or_id)
    items = load_input_json(args.input_json)

    print(f"Fetching metadata for video ID: {video_id}...", file=sys.stderr)
    meta = fetch_oembed_metadata(video_id)
    title = meta["title"]
    author = meta["author"]

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

    # Determine destination path: explicit file, or {title}.md inside a directory (default: cwd)
    default_name = f"{sanitize_filename(title)}.md"
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir() or args.output.endswith(("/", "\\")):
            out_path = out_path / default_name
    else:
        out_path = Path(default_name)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully saved transcript to: {out_path.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, ValueError, OSError) as e:
        # Expected failures (extraction error, bad URL, missing file): show the message only, no traceback.
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
