#!/usr/bin/env python3
"""
split_transcript.py

Splits a large interview/podcast transcript markdown document into manageable
chapter-aligned chunks for subagent/parallel processing.
All temporary chunk files are strictly placed in the source file's directory.
Always executed via `uv run`.
"""

import sys
import os
import re
import argparse
from pathlib import Path

# Ensure script directory is on sys.path for importing verify_lossless
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_lossless import TRANSCRIPT_MARKERS

def split_transcript(file_path: str, chapters_per_chunk: int = 5):
    p = Path(file_path).resolve()
    if not p.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()

    # Locate transcript start using shared TRANSCRIPT_MARKERS
    transcript_pos = -1
    for marker in TRANSCRIPT_MARKERS:
        pos = content.find(marker)
        if pos != -1:
            transcript_pos = pos + len(marker)
            break

    if transcript_pos == -1:
        # Fallback: look for the first ### heading
        first_h3 = content.find('\n### ')
        if first_h3 != -1:
            transcript_pos = first_h3
        else:
            transcript_pos = 0

    preamble = content[:transcript_pos].rstrip() + '\n\n'
    body = content[transcript_pos:].strip()

    # Temporary files are strictly placed in the target file's directory
    parent_dir = p.parent
    base_stem = p.name

    # Strip .zh.md or .md for clean chunk naming
    if base_stem.endswith('.zh.md'):
        stem_clean = base_stem[:-6]
        ext = '.zh.tmp.md'
    elif base_stem.endswith('.md'):
        stem_clean = base_stem[:-3]
        ext = '.tmp.md'
    else:
        stem_clean = base_stem
        ext = '.tmp.md'

    preamble_path = parent_dir / f"{stem_clean}.preamble{ext}"
    with open(preamble_path, 'w', encoding='utf-8') as f:
        f.write(preamble)
    print(f"Preamble saved: {preamble_path} ({len(preamble)} chars)")

    # Find chapters starting with `### `
    chapter_splits = list(re.finditer(r'(?=^###\s+)', body, flags=re.MULTILINE))

    if not chapter_splits:
        print("Notice: No '### ' chapter headings found. Splitting by timestamps...")
        ts_splits = list(re.finditer(r'(?=^\*\*\d+:\d+(?::\d+)?\*\*\s*·)', body, flags=re.MULTILINE))
        total_ts = len(ts_splits)
        chunk_size = max(20, total_ts // 4)
        chunks = []
        for i in range(0, total_ts, chunk_size):
            start_idx = ts_splits[i].start()
            end_idx = ts_splits[min(i + chunk_size, total_ts) - 1].start() if (i + chunk_size) < total_ts else len(body)
            chunks.append(body[start_idx:end_idx].strip())
    else:
        num_chapters = len(chapter_splits)
        print(f"Detected {num_chapters} chapters.")
        chunks = []
        for i in range(0, num_chapters, chapters_per_chunk):
            start_idx = chapter_splits[i].start()
            if i + chapters_per_chunk < num_chapters:
                end_idx = chapter_splits[i + chapters_per_chunk].start()
            else:
                end_idx = len(body)
            chunks.append(body[start_idx:end_idx].strip())

    chunk_files = []
    for idx, chunk in enumerate(chunks, 1):
        chunk_name = f"{stem_clean}.part{idx:02d}{ext}"
        chunk_path = parent_dir / chunk_name
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk + '\n')
        
        c_count = len(re.findall(r'^###\s+.*', chunk, flags=re.MULTILINE))
        print(f"Chunk {idx:02d}: {chunk_path} ({len(chunk)} chars, {c_count} chapters)")
        chunk_files.append(str(chunk_path))

    print(f"\nSuccessfully split into {len(chunks)} chunks in directory: {parent_dir}")
    return chunk_files

def main():
    parser = argparse.ArgumentParser(description="Split transcript into chapter-aligned chunks in the same directory.")
    parser.add_argument("file_path", help="Path to markdown transcript file")
    parser.add_argument("--chapters", type=int, default=5, help="Number of chapters per chunk (default: 5)")
    args = parser.parse_args()

    split_transcript(args.file_path, args.chapters)

if __name__ == '__main__':
    main()
