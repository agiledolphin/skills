#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
import os
import re
import argparse

def find_split_points(lines):
    """
    Return (priority, index) pairs meaning "a chunk may end before lines[index]".
    Priority 1: before a heading (#, ##); 2: after a blank line; 3: after a sentence end.
    Lines inside fenced code blocks are never split points.
    """
    points = []
    in_code_block = False
    code_block_fence = ""
    for i, line in enumerate(lines):
        fence_match = re.match(r'^(\s{0,3})(```+|~~~+)', line)
        if fence_match:
            if not in_code_block:
                in_code_block = True
                code_block_fence = fence_match.group(2)
            elif fence_match.group(2).startswith(code_block_fence):
                in_code_block = False
            continue
        if in_code_block:
            continue
        if re.match(r'^#{1,2}\s', line):
            points.append((1, i))
        elif line.strip() == "":
            points.append((2, i + 1))
        elif re.search(r'[。！？.!?]\s*$', line):
            points.append((3, i + 1))
    return points


def split_markdown(file_path, min_chars=5000, max_chars=8000):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    # offsets[i] = number of characters before lines[i]
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    points = find_split_points(lines)

    chunks = []
    start = 0
    while offsets[-1] - offsets[start] > max_chars:
        candidates = [(prio, idx) for prio, idx in points if idx > start]
        # Prefer chunks between min and max; otherwise anything under max; otherwise the first point past max
        in_window = [c for c in candidates if min_chars <= offsets[c[1]] - offsets[start] <= max_chars]
        under_max = [c for c in candidates if offsets[c[1]] - offsets[start] <= max_chars]
        pool = in_window or under_max
        if pool:
            # Best priority first; among equal priority, the latest point keeps chunks as large as possible
            _, split_idx = min(pool, key=lambda c: (c[0], -c[1]))
        elif candidates:
            # Emergency split: an oversized code block or table with no point under max
            split_idx = min(idx for _, idx in candidates)
        else:
            break
        chunks.append("".join(lines[start:split_idx]))
        start = split_idx

    # Add final chunk
    if start < len(lines):
        chunks.append("".join(lines[start:]))

    # Write files
    base_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    
    for i, chunk in enumerate(chunks):
        part_name = f"{base_name}.part{i+1}.tmp.md"
        part_path = os.path.join(dir_name, part_name)
        with open(part_path, 'w', encoding='utf-8') as f:
            f.write(chunk)
        print(f"Created {part_path} ({len(chunk)} characters)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split Markdown files into chunks.")
    parser.add_argument("input", help="Path to the input Markdown file")
    parser.add_argument("--min", type=int, default=5000, help="Minimum characters per chunk")
    parser.add_argument("--max", type=int, default=8000, help="Maximum characters per chunk")
    args = parser.parse_args()
    
    if os.path.exists(args.input):
        split_markdown(args.input, args.min, args.max)
    else:
        print(f"Error: File {args.input} not found.")
