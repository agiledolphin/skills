#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
import os
import re
import argparse
import glob

def extract_headings(file_path):
    """
    Extract headings (up to Level 3) from a markdown file to check structural completeness.
    Excludes any headings found inside code blocks.
    """
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    headings = []
    in_code_block = False
    for line in content.splitlines():
        # Track code block fence state
        if line.strip().startswith(('```', '~~~')):
            in_code_block = not in_code_block
            continue
        # Only extract headings when not in a code block
        if not in_code_block:
            if re.match(r'^#{1,3}\s', line):
                headings.append(line.strip())
    return headings

def merge_markdown(source_path, output_path=None):
    """
    Merge the translated chunks in sequence, formatting them correctly and performing structural checks.
    """
    if not os.path.exists(source_path):
        print(f"Error: Source file '{source_path}' not found.")
        return False
        
    dir_name = os.path.dirname(source_path)
    base_name = os.path.basename(source_path)
    
    # 1. Discover all translated part files (*.part*.zh.tmp.md)
    pattern = os.path.join(dir_name, f"{base_name}.part*.zh.tmp.md")
    part_files = glob.glob(pattern)
    
    if not part_files:
        print(f"Error: No translated part files found matching '{pattern}'.")
        return False
        
    # Sort files numerically by the part number to ensure correct sequence
    def get_part_num(filepath):
        match = re.search(r'\.part(\d+)\.zh\.tmp\.md$', filepath)
        return int(match.group(1)) if match else 0
        
    part_files.sort(key=get_part_num)
    print(f"Found {len(part_files)} translated parts to merge.")

    # Default output path: original_name.zh.md in the same directory
    if not output_path:
        if source_path.endswith('.md'):
            output_path = source_path[:-3] + '.zh.md'
        else:
            output_path = source_path + '.zh.md'

    # 2. Merge contents with precise spacing logic
    merged_lines = []
    for i, part_path in enumerate(part_files):
        print(f"Reading: {os.path.basename(part_path)}")
        with open(part_path, 'r', encoding='utf-8') as f:
            part_content = f.read()
            
        part_lines = part_content.splitlines()
        
        # For intermediate and last chunks, strip leading blank lines to prevent padding
        if i > 0:
            while part_lines and part_lines[0].strip() == "":
                part_lines.pop(0)
        
        # For all chunks, strip trailing blank lines to control boundaries
        while part_lines and part_lines[-1].strip() == "":
            part_lines.pop()
            
        if part_lines:
            if merged_lines:
                # Ensure exactly one blank line between the last line of one chunk and the first line of the next
                merged_lines.append("")
            merged_lines.extend(part_lines)
            
    final_content = "\n".join(merged_lines) + "\n"
    
    # 3. Verify the merge
    if not final_content.strip():
        print("Error: Merged content is empty.")
        return False
        
    # Extract original headings
    orig_headings = extract_headings(source_path)
    
    # Write to final output path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    print(f"Merged output written to '{output_path}'")
    
    # Extract headings from the merged file
    merged_headings = extract_headings(output_path)
    
    print(f"Heading Count - Original: {len(orig_headings)}, Merged: {len(merged_headings)}")
    
    if len(orig_headings) != len(merged_headings):
        print("\n[WARNING] Heading count mismatch! Possible data/section loss during split or translation.")
        print("--- Original Headings ---")
        for h in orig_headings:
            print(f"  {h}")
        print("--- Merged Headings ---")
        for h in merged_headings:
            print(f"  {h}")
        print("\nVerification FAILED. Temporary part files will NOT be deleted.")
        print("Please review the logs and check if any section was dropped.")
        return False
        
    print("Verification SUCCESS: All heading counts and structures match.")
    
    # 4. Clean up temporary part files only after successful verification
    deleted_count = 0
    for part_path in part_files:
        # Delete translated part file
        if os.path.exists(part_path):
            os.remove(part_path)
            deleted_count += 1
        # Delete matching original part file
        orig_part_path = part_path.replace('.zh.tmp.md', '.tmp.md')
        if os.path.exists(orig_part_path):
            os.remove(orig_part_path)
            deleted_count += 1
            
    print(f"Successfully cleaned up {deleted_count} temporary part files.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge translated Markdown chunks and verify document structure.")
    parser.add_argument("source", help="Path to the original un-translated Markdown file (used for structure verification)")
    parser.add_argument("--output", help="Optional path to the final merged output file")
    args = parser.parse_args()
    
    success = merge_markdown(args.source, args.output)
    if not success:
        exit(1)
