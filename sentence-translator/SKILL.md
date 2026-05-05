---
name: sentence-translator
description: Translate foreign language documents into Chinese sentence by sentence, preserving the original markdown structure. Use when the user wants to translate markdown content (articles, documentation, notes) from any foreign language (English, Japanese, French, etc.) into Chinese with sentence-level alignment. Triggers include requests like "translate this to Chinese", "翻译这篇文章", "逐句翻译", or any mention of translating markdown/text content into Chinese.
---

# Sentence Translator

Translate foreign language markdown documents into Chinese, sentence by sentence, preserving all markdown formatting.

## Workflow

1. Read the input markdown file
2. Check file size — if content exceeds 10,000 characters, follow the **Large File Workflow** below; otherwise proceed with the standard workflow
3. Translate sentence by sentence following the rules below
4. Review the translation for quality issues (see Review Checklist)
5. Fix any issues found during review
6. Write the final translated result to the output markdown file

## Large File Workflow

When the source file exceeds 10,000 **Unicode characters** (`wc -m` on the file), split it into chunks before translating. Process chunks strictly sequentially — do not translate chunk N+1 until chunk N is fully translated and reviewed.

### Step 1 — Split into chunks

- Split at natural boundaries in this priority order: level-1/2 headings (`#`, `##`) > blank-line paragraph breaks > sentence endings
- A heading always starts a new chunk (goes into the chunk that follows it, not the chunk before)
- Target chunk size: 5,000–8,000 characters each
- Never split inside a code block, table, or blockquote — keep them whole in one chunk
  - Exception: if a single indivisible block (code, table, blockquote) exceeds 8,000 characters on its own, place it alone in its own chunk regardless of size limit
- If a frontmatter block (`---`) is present, keep it attached to the first chunk
- Write each chunk to a temporary file named `<original_name>.part<N>.tmp.md` in the same directory (N = 1, 2, 3 …)

### Step 2 — Translate each chunk (strictly one at a time)

For each chunk in order:
- Translate using the standard translation rules
- Maintain an **in-memory glossary** of complex/obscure terms that received a parenthetical note — on all subsequent chunks, use the Chinese-only form for those terms (no repeated parenthetical)
- Write translated output to `<original_name>.part<N>.zh.tmp.md`
- Do NOT proceed to the next chunk until this chunk's translated file is written

### Step 3 — Review each translated chunk

After translating each chunk, apply the Review Checklist before translating the next chunk.

### Step 4 — Merge translated chunks

- Concatenate all `<original_name>.part<N>.zh.tmp.md` files in order into the final output file (`<original_name>.zh.md`)
- Ensure exactly one blank line between the last line of one chunk and the first line of the next (avoid double blank lines at join points)
- Verify the merge: the output file must be non-empty and must contain all major section headings from the source — if any heading is missing, stop and investigate before deleting temp files
- Delete all temporary files (`*.part*.tmp.md` and `*.part*.zh.tmp.md`) only after verifying the output

### Step 5 — Final cross-chunk review

After merging, re-read the joined output and check:
- [ ] No duplicate blank lines or stray headers at chunk join points
- [ ] Term consistency across chunks (same term translated the same way throughout)
- [ ] No sentence or paragraph was accidentally dropped at a split boundary

## Translation Rules

### Sentence-Level Alignment

Translate each sentence individually. Preserve the one-to-one correspondence between source and target sentences. Do NOT merge or split sentences.

### Preserve Paragraph Structure

Do NOT alter the paragraph structure of the original. Each paragraph break in the source must remain a paragraph break in the output. Do not merge separate paragraphs into one, and do not introduce new paragraph breaks that did not exist in the source.

### Preserve Markdown Structure

Keep all markdown formatting intact:
- Headings (`#`, `##`, etc.) — translate heading text only
- Lists (ordered/unordered) — translate list item text only
- Code blocks (`` ` ``, `` ``` ``) — do NOT translate anything inside code blocks, including comments
- Links `[text](url)` — translate display text, keep URL unchanged
- Images `![alt](url)` — translate alt text, keep URL unchanged
- Tables — translate cell content, keep table structure
- Bold, italic, strikethrough — preserve markers, translate inner text
- Blockquotes — translate quoted text, keep `>` markers
- Frontmatter (YAML between `---`) — do NOT translate

### Translation Quality

- 翻译风格遵循「信达雅」原则：以逐字对译为基础（信），确保译文通顺可读（达），并在用词上追求简洁雅正（雅）；在忠实原文的前提下，允许最小限度的调整以符合中文表达习惯
- Technical terms — apply the following tiered approach:
  - **Everyday technical terms** (e.g., API, URL, CPU, JSON, SDK): keep the original English term as-is; do not translate
  - **Common technical terms with established Chinese equivalents** (e.g., 算法、数据库、操作系统): translate directly to Chinese with no parenthetical original
  - **Complex or obscure terms** (domain-specific jargon, niche acronyms, specialised concepts unfamiliar to a general technical audience): on **first occurrence** only, append the original term in parentheses — e.g., "变分自编码器（VAE）"、"注意力机制（Attention Mechanism）"; on all subsequent occurrences, use the Chinese translation alone
- Maintain the original tone and register (formal/informal)
- Keep proper nouns in their original form unless a well-known Chinese translation exists

## Review Checklist

After completing the translation, review the full output against this checklist before writing the file:

### Language & Fluency
- [ ] No untranslated foreign words left (except proper nouns and code)
- [ ] 译文以逐字对译为基础，在不损害可读性的前提下保持与原文的字词对应关系
- [ ] No awkward or missing punctuation (e.g., missing 。or incorrect use of ，vs 。)
- [ ] No duplicate words or repeated phrases caused by translation errors

### Accuracy
- [ ] Technical terms follow the tiered rule: everyday terms kept in English as-is; common terms translated to Chinese; complex/obscure terms have the original in parentheses on first occurrence only
- [ ] No meaning distortion — check that the translated sentence matches the source intent
- [ ] Proper nouns retained correctly

### Structure Preservation
- [ ] All markdown elements intact (headings, lists, code blocks, links, tables, bold/italic, etc.)
- [ ] Paragraph breaks match the source exactly — no merges or new breaks introduced
- [ ] Code blocks unchanged — no translated content inside code blocks
- [ ] Frontmatter untouched

### Consistency
- [ ] Same term translated consistently throughout the document
- [ ] Tone and register consistent with the source (formal/informal)

If any issue is found, fix it before writing the output file.

## Output Format

Write the translated markdown to a new file. Default naming: `<original_name>.zh.md` in the same directory as the source file. If the user specifies an output path, use that instead.

## Example

**Input:**
```markdown
## Introduction

Machine learning is a subset of AI. It enables computers to learn from data.

- Supervised learning uses labeled data.
- Use the REST API to access the service.

```python
# Initialize the model
model = load_model("bert")
```
```

**Output:**
```markdown
## 简介

机器学习是 AI 的一个子集。它使计算机能够从数据中学习。

- 监督学习使用标注数据。
- 使用 REST API 来访问该服务。

```python
# Initialize the model
model = load_model("bert")
```
```

> **术语处理说明：**
> - "AI"、"REST API" → 常规技术术语，直接保留英文原文
> - "机器学习"、"监督学习" → 有通行中文译名，直接译为中文，不附括注
