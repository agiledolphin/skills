#!/usr/bin/env python3
import os
import re
import argparse

def split_markdown(file_path, min_chars=5000, max_chars=8000):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)
    chunks = []
    current_chunk_lines = []
    current_chunk_len = 0
    
    in_code_block = False
    code_block_fence = ""
    
    # Potential split points: (priority, line_index)
    # Priority 1: Headings (#, ##)
    # Priority 2: Blank lines
    # Priority 3: Sentence ends (approximate)
    split_points = []

    for i, line in enumerate(lines):
        # Track code block state
        fence_match = re.match(r'^(\s{0,3})(```+|~~~+)', line)
        if fence_match:
            if not in_code_block:
                in_code_block = True
                code_block_fence = fence_match.group(2)
            else:
                if fence_match.group(2).startswith(code_block_fence):
                    in_code_block = False
        
        current_chunk_lines.append(line)
        current_chunk_len += len(line)
        
        # Identify split points (only when NOT in a code block)
        if not in_code_block:
            if re.match(r'^#{1,2}\s', line):
                # Priority 1: Headings. Heading starts a NEW chunk.
                # So we record the index BEFORE this line as a split point.
                split_points.append((1, len(current_chunk_lines) - 1))
            elif line.strip() == "":
                # Priority 2: Blank lines. Split AFTER the blank line.
                split_points.append((2, len(current_chunk_lines)))
            elif re.search(r'[。！？.!?]\s*$', line):
                # Priority 3: Sentence ends. Split AFTER the line.
                split_points.append((3, len(current_chunk_lines)))

        # Check if we should split
        if current_chunk_len >= min_chars:
            # We are in the target window. Try to find the best split point.
            best_point = None
            
            # If we exceed max_chars, we MUST split at the best point found so far.
            if current_chunk_len > max_chars:
                # Filter points within current chunk
                valid_points = [p for p in split_points if p[1] > 0]
                if valid_points:
                    # Sort by priority (lower number is higher priority)
                    valid_points.sort(key=lambda x: x[0])
                    best_point = valid_points[0]
                else:
                    # Emergency split if no points found but we exceeded max
                    # (Should only happen in extremely long code blocks/tables)
                    pass 

            if best_point:
                split_idx = best_point[1]
                # Split the lines
                chunk_lines = current_chunk_lines[:split_idx]
                remaining_lines = current_chunk_lines[split_idx:]
                
                if chunk_lines:
                    chunks.append("".join(chunk_lines))
                    current_chunk_lines = remaining_lines
                    current_chunk_len = sum(len(l) for l in current_chunk_lines)
                    split_points = [] # Reset points for new chunk
                    # Re-populate split points for the carried-over lines
                    # (Simplification: just continue)
            
    # Add final chunk
    if current_chunk_lines:
        chunks.append("".join(current_chunk_lines))

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
