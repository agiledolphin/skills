---
name: youtube-transcript
description: Fetch and process YouTube video transcripts/subtitles using youtube-transcript-api. Extracts clean transcripts with timestamps, preserves speaker change cues (>>), merges fragmented caption lines into coherent paragraphs, and formats as Obsidian Markdown clippings with standard YAML frontmatter. Triggers include "获取YouTube文字稿", "提取YouTube字幕", "抓取YouTube逐字稿", "获取视频文字稿", "下载视频逐字稿", or requests to ingest/transcribe YouTube videos.
---

# YouTube Transcript Fetcher

通过 `youtube-transcript-api` 与 YouTube TimedText 协议高效提取 YouTube 视频字幕与逐字稿。不受网页端登录弹窗风控干扰，自动抓取视频元数据，智能合并碎片化字幕行，并格式化为符合 Obsidian Vault 标准的 Markdown 剪藏（Clipping）。

---

## 核心执行方式 (Execution)

使用专用提取脚本运行（下文脚本路径均相对于本技能目录，即 SKILL.md 所在目录）：

```bash
uv run scripts/fetch_transcript.py "<youtube_url_or_id>" [OPTIONS]
```

- **必须通过 `uv run` 执行**，严禁直接调用裸 `python` / `python3`。
- 脚本本身只依赖标准库（PEP 723 内联声明），底层通过 `uvx` 调用 `youtube-transcript-api`，无需在系统全局或虚拟环境中预装该包。

---

## 参数说明 (CLI Options)

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `url_or_id` | 完整的 YouTube 链接（支持 `watch?v=`, `youtu.be/`, `shorts/`, `live/`）或 11 位 Video ID | **必填**（使用 `--input-json` 时可省略） |
| `-o, --output` | 指定输出 Markdown 文件路径 | `inbox/clippings/{Sanitized_Title}.md` |
| `-l, --languages` | 优先尝试的语言代码列表（逗号分隔） | `en,zh-Hans,zh-Hant,zh,ja` |
| `--format` | 输出格式：`timestamps`（带时间戳块）、`clean`（纯文本段落）、`json`（原始数据） | `timestamps` |
| `--max-gap` | 自动合并连续短句的最大停顿时间（秒） | `2.5` |
| `--input-json` | 使用已下载的原始字幕 JSON（跳过在线抓取；此时 `url_or_id` 可省略） | — |

---

## 常用工作流范例

### 1. 基础抓取（保存至 inbox/clippings）
```bash
uv run scripts/fetch_transcript.py "https://www.youtube.com/watch?v=o8B0_OlCL78"
```
自动生成文件：
- 路径：`inbox/clippings/Monday Medications October 12th 2026.md`
- 结构：包含 YAML Frontmatter（title, source, author, tags 等）以及标准时间戳段落（`**0:00** · text`）。

### 2. 指定输出路径与优先中文轨
```bash
uv run scripts/fetch_transcript.py "https://youtu.be/VIDEO_ID" -o "inbox/clippings/Target.md" -l "zh-Hans,zh,en"
```

### 3. 获取纯净正文（无时间戳，适合速读或总结）
```bash
uv run scripts/fetch_transcript.py "VIDEO_ID" --format clean
```
