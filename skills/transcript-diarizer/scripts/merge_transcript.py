#!/usr/bin/env python3
"""
merge_transcript.py

Merges processed diarized transcript chunks with the original preamble,
runs lossless verification, and cleans up temporary chunk files.
Always executed via `uv run`.
"""

import sys
import os
import re
import argparse
from pathlib import Path

# Ensure script directory is on sys.path for importing verify_lossless
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_lossless import verify, TRANSCRIPT_MARKERS

def merge_transcript(original_file: str, output_file: str = None):
    p_orig = Path(original_file).resolve()
    if not p_orig.exists():
        print(f"Error: Original file not found: {original_file}", file=sys.stderr)
        sys.exit(1)

    # Temporary files and output are always colocated in the original file's parent directory
    parent_dir = p_orig.parent
    base_stem = p_orig.name

    if base_stem.endswith('.zh.md'):
        stem_clean = base_stem[:-6]
        ext = '.zh.tmp.md'
        default_out = parent_dir / f"{stem_clean} (精排对话版).zh.md"
    elif base_stem.endswith('.md'):
        stem_clean = base_stem[:-3]
        ext = '.tmp.md'
        default_out = parent_dir / f"{stem_clean} (精排对话版).md"
    else:
        stem_clean = base_stem
        ext = '.tmp.md'
        default_out = parent_dir / f"{stem_clean}_diarized.md"

    target_out = Path(output_file).resolve() if output_file else default_out

    # Find preamble in the target file's parent directory
    preamble_path = parent_dir / f"{stem_clean}.preamble{ext}"
    if not preamble_path.exists():
        # Fallback: extract directly from original file
        with open(p_orig, 'r', encoding='utf-8') as f:
            orig_content = f.read()
        for marker in TRANSCRIPT_MARKERS:
            pos = orig_content.find(marker)
            if pos != -1:
                preamble_content = orig_content[:pos]
                break
        else:
            first_h3 = orig_content.find('\n### ')
            preamble_content = orig_content[:first_h3] if first_h3 != -1 else ""
    else:
        with open(preamble_path, 'r', encoding='utf-8') as f:
            preamble_content = f.read()

    # Update title in frontmatter
    def update_title(match):
        title = match.group(1)
        if "精排对话版" not in title:
            return f'title: "{title} (精排对话版)"'
        return match.group(0)

    preamble_updated = re.sub(r'^title:\s*["\']?(.*?)["\']?\s*$', update_title, preamble_content, flags=re.MULTILINE)
    
    # Strip any existing transcript markers from the end of preamble to prevent duplicate headings
    for marker in TRANSCRIPT_MARKERS:
        if preamble_updated.rstrip().endswith(marker):
            preamble_updated = preamble_updated.rstrip()[:-len(marker)].rstrip()
            break

    # Ensure clean standardized section title
    preamble_updated = preamble_updated.rstrip() + '\n\n## 访谈实录 (Transcript)\n\n'

    # Find processed chunk files located in parent_dir
    chunks_diarized = sorted(list(parent_dir.glob(f"{stem_clean}.part*.diarized{ext}")))
    if chunks_diarized:
        selected_chunks = chunks_diarized
    else:
        selected_chunks = sorted([
            f for f in parent_dir.glob(f"{stem_clean}.part*{ext}")
            if "preamble" not in f.name
        ])

    if not selected_chunks:
        print(f"Error: No chunk files found in {parent_dir} matching {stem_clean}.part*{ext}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(selected_chunks)} chunk files in {parent_dir}:")
    for c in selected_chunks:
        print(f"  - {c.name}")

    # Read and join chunk contents
    body_parts = []
    for c in selected_chunks:
        with open(c, 'r', encoding='utf-8') as f:
            c_text = f.read().strip()
            if c_text:
                body_parts.append(c_text)

    # Clean intermediate duplicate separators if any
    cleaned_parts = []
    for p in body_parts:
        p_clean = re.sub(r'^\s*---\s*\n+', '', p)
        p_clean = re.sub(r'\n+\s*---\s*$', '', p_clean)
        cleaned_parts.append(p_clean)

    full_body = '\n\n---\n\n'.join(cleaned_parts) + '\n'
    # Automatically strip any speaker timestamps if present (e.g. **姓名 [00:00]**： -> **姓名**：)
    full_body = re.sub(r'\*\*([^\*\n]+?)\s*\[\d+:\d+(?::\d+)?\]\*\*([:：])', r'**\1**\2', full_body)
    full_doc = preamble_updated + full_body

    # Write merged file
    with open(target_out, 'w', encoding='utf-8') as f:
        f.write(full_doc)

    print(f"\nMerged file generated: {target_out} ({len(full_doc)} chars)")

    # Run lossless verification
    print("\nRunning automated lossless verification via verify_lossless...")
    is_valid = verify(str(p_orig), str(target_out))

    if is_valid:
        print("\nVerification PASSED! Cleaning up temporary chunk files in directory...")
        # Clean all matching temporary files for this stem in parent_dir
        cleaned_count = 0
        for tmp_file in parent_dir.glob(f"{stem_clean}*.tmp.md"):
            try:
                tmp_file.unlink()
                cleaned_count += 1
            except Exception as e:
                print(f"Warning: Failed to remove {tmp_file.name}: {e}", file=sys.stderr)
        print(f"Cleanup completed: removed {cleaned_count} temporary files.")
    else:
        print("\nVerification FAILED! Temporary chunk files are PRESERVED in directory for debugging.", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Merge processed transcript chunks and verify lossless fidelity.")
    parser.add_argument("original_file", help="Path to original source transcript markdown file")
    parser.add_argument("--output", "-o", help="Optional path for output file", default=None)
    args = parser.parse_args()

    merge_transcript(args.original_file, args.output)

if __name__ == '__main__':
    main()
