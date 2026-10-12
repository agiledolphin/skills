#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
verify_lossless.py

Compares an original transcript with a diarized (speaker-attributed) transcript
to guarantee 100% text fidelity (0 diff) and verify structural formatting.
"""

import sys
import re
import difflib
import argparse
from pathlib import Path

# Level-2 headings that open the transcript body. Any suffix on the same line is allowed
# (e.g. "## 逐字稿 (Transcript)", "## 访谈实录（全文）"), since transcripts come from many sources.
TRANSCRIPT_HEADING_NAMES = ['访谈实录', '逐字记录', '文字记录', '逐字稿', '对话记录', '实录', 'Transcript']
TRANSCRIPT_HEADING_RE = re.compile(
    r'^##[ \t]+(?:' + '|'.join(map(re.escape, TRANSCRIPT_HEADING_NAMES)) + r').*$',
    flags=re.MULTILINE | re.IGNORECASE,
)


def find_transcript_heading(text: str):
    """Return the match for the first transcript heading line, or None."""
    return TRANSCRIPT_HEADING_RE.search(text)

def extract_content_text(text: str) -> str:
    """
    Strips metadata, section headings, timestamp markers, and speaker prefixes,
    returning the canonical text sequence with all whitespace removed.
    """
    # If document has a transcript section heading, check only the transcript portion (after the whole heading line)
    heading = find_transcript_heading(text)
    if heading:
        text = text[heading.end():]

    # Strip markdown headers (##, ###)
    text = re.sub(r'^#{2,4}\s+.*$', '', text, flags=re.MULTILINE)
    # Strip horizontal separators
    text = re.sub(r'^\s*---\s*$', '', text, flags=re.MULTILINE)
    # Strip raw timestamp labels like **00:00** · or **0:00** · or **1:10:48** ·
    text = re.sub(r'\*\*\d+:\d+(?::\d+)?\*\*\s*·\s*', '', text)
    # Strip speaker prefixes like **姓名 [时间戳]**： or **姓名**：
    text = re.sub(r'\*\*[^\*\n]+?(?:\s*\[\d+:\d+(?::\d+)?\])?\*\*[:：]', '', text)
    # Remove all whitespace
    return re.sub(r'\s+', '', text)

def verify(orig_path: str, diarized_path: str, allow_raw_timestamps: bool = False) -> bool:
    p_orig = Path(orig_path)
    p_diar = Path(diarized_path)

    if not p_orig.exists():
        print(f"Error: Original file not found: {orig_path}", file=sys.stderr)
        return False
    if not p_diar.exists():
        print(f"Error: Diarized file not found: {diarized_path}", file=sys.stderr)
        return False

    with open(p_orig, 'r', encoding='utf-8') as f:
        orig_text = f.read()
    with open(p_diar, 'r', encoding='utf-8') as f:
        diar_text = f.read()

    orig_clean = extract_content_text(orig_text)
    diar_clean = extract_content_text(diar_text)

    print(f"=== 文本无损校验 (Lossless Verification) ===")
    print(f"原稿逐字稿纯文字符数:   {len(orig_clean)}")
    print(f"精排稿逐字稿纯文字符数: {len(diar_clean)}")

    matcher = difflib.SequenceMatcher(None, orig_clean, diar_clean)
    diffs = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            diffs.append((tag, orig_clean[max(0, i1-25):i1], orig_clean[i1:i2], orig_clean[i2:i2+25], diar_clean[j1:j2]))

    if diffs:
        print(f"\n[FAILED] 发现 {len(diffs)} 处文字不一致！")
        for idx, (tag, before, orig_chunk, after, diar_chunk) in enumerate(diffs[:5], 1):
            print(f"\n--- 差异 #{idx} [{tag}] ---")
            print(f"上下文前缀: ...{before}")
            print(f"原稿文本:   {orig_chunk}")
            print(f"排版后文本: {diar_chunk}")
            print(f"上下文后缀: {after}...")
        return False

    print("\n[PASSED] 100% 文本无损对齐 (0 diff)！所有原文字词、语气词、技术术语均完整保留。")

    # Structural audit
    print(f"\n=== 结构与格式审计 (Structural Audit) ===")
    
    # Check remaining raw timestamps: in strict mode, leftover timestamps fail the verification!
    raw_ts = re.findall(r'\*\*\d+:\d+(?::\d+)?\*\*\s*·', diar_text)
    if raw_ts:
        print(f"[ERROR] 发现 {len(raw_ts)} 处未拆分的原始时间戳标签: {raw_ts[:5]}")
        if not allow_raw_timestamps:
            print("校验未通过：精排稿中仍残留未拆分的时间戳标签，说明拆分未完全完成！")
            return False
    else:
        print("[OK] 无遗留原始时间戳标签。")

    # Check speaker timestamps: speaker names should not have timestamp suffixes
    speaker_ts = re.findall(r'\*\*[^\*\n]+?\s*\[\d+:\d+(?::\d+)?\]\*\*[:：]', diar_text)
    if speaker_ts:
        print(f"[WARN] 发现 {len(speaker_ts)} 处发言人姓名后残留时间戳 (规范要求使用纯净格式 **姓名**：): {speaker_ts[:3]}")
    else:
        print("[OK] 发言人格式规范（无多余时间戳后缀）。")

    # Chapters
    orig_chapters = re.findall(r'^###\s+.*$', orig_text, re.MULTILINE)
    diar_chapters = re.findall(r'^###\s+.*$', diar_text, re.MULTILINE)
    print(f"章节数量: 原稿 {len(orig_chapters)} 章 | 排版后 {len(diar_chapters)} 章")

    # Speakers
    speaker_turns = re.findall(r'\*\*([^\*\n]+?)(?:\s*\[\d+:\d+(?::\d+)?\])?\*\*[:：]', diar_text)
    speaker_counts = {}
    for s in speaker_turns:
        speaker_counts[s] = speaker_counts.get(s, 0) + 1

    print(f"发言轮次统计 (共 {len(speaker_turns)} 轮):")
    for s, cnt in sorted(speaker_counts.items(), key=lambda x: -x[1]):
        print(f"  - {s}: {cnt} 次发言")

    return True

def main():
    parser = argparse.ArgumentParser(description="Verify 100% lossless text fidelity between original and diarized transcript.")
    parser.add_argument("original_file", help="Path to original source transcript markdown file")
    parser.add_argument("diarized_file", help="Path to diarized transcript markdown file")
    parser.add_argument("--allow-raw-timestamps", action="store_true", help="Do not fail if raw timestamps remain")
    args = parser.parse_args()

    success = verify(args.original_file, args.diarized_file, args.allow_raw_timestamps)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
