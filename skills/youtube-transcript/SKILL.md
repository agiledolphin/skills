---
name: youtube-transcript
description: Fetch YouTube video transcripts by driving a real browser (agent-browser) to read the video page's transcript panel, then merge fragmented caption lines into coherent timestamped paragraphs and format them as Obsidian Markdown clippings with standard YAML frontmatter. Triggers include "获取YouTube文字稿", "提取YouTube字幕", "抓取YouTube逐字稿", "获取视频文字稿", "下载视频逐字稿", or requests to ingest/transcribe YouTube videos.
---

# YouTube Transcript Fetcher

通过 Agent Browser 打开 YouTube 视频页面，从页面自带的文字稿面板提取逐字稿，再自动获取视频标题与作者、合并碎片化字幕行，并格式化为符合 Obsidian Vault 标准的 Markdown 剪藏（Clipping）。

之所以用浏览器而不是字幕 API：YouTube 会拦截机房 / VPN 出口 IP 的字幕 API 请求，而正常浏览器访问通常不受影响。

---

## 前置条件

- 已安装 `agent-browser`（`npm i -g agent-browser && agent-browser install`）。
- 下文脚本路径均相对于本技能目录（即 SKILL.md 所在目录）。
- **Python 脚本必须通过 `uv run` 执行**，严禁直接调用裸 `python` / `python3`；脚本只依赖标准库（PEP 723 内联声明）。

---

## 执行流程 (Workflow)

```bash
export AGENT_BROWSER_SESSION="$(agent-browser session id --scope worktree --prefix yt)"
agent-browser open "<youtube_url>"
agent-browser eval --stdin < scripts/extract_transcript_panel.js > "<临时目录>/raw.json"
agent-browser close
uv run scripts/format_transcript.py "<youtube_url>" --input-json "<临时目录>/raw.json" -o "<输出目录>/"
```

1. **提取**：`extract_transcript_panel.js` 会自动展开简介、打开文字稿面板并等待加载，返回 `[{text, start, duration}]`。选择器基于页面结构，与界面语言无关。
2. **排版**：`format_transcript.py` 获取标题与作者，合并字幕为段落，写出 Markdown。
3. **清理**：`raw.json` 是临时文件，放在临时目录而非输出目录，用完即可删除。

### 失败处理

- 页面要求"确认你不是机器人"，或 `raw.json` 内容为 `{"error": ...}`（视频无文字稿、YouTube 改版导致找不到面板等）时，`format_transcript.py` 会报错退出。如实告知用户原因，**不要编造或补写文字稿内容**。
- 若是 YouTube 改版导致提取失败，需要更新 `extract_transcript_panel.js` 中的选择器。

### 已知局限

- 文字稿语言为 YouTube 面板默认显示的字幕轨，不支持指定语言。
- 时间戳只精确到秒，时长由相邻时间戳推算，不影响段落合并。
- 面板通常不含 `>>` 说话人标记；如需区分说话人，交由下游技能处理。

---

## 参数说明 (`format_transcript.py`)

| 参数 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `url_or_id` | 完整的 YouTube 链接（支持 `watch?v=`, `youtu.be/`, `shorts/`, `live/`）或 11 位 Video ID，用于获取标题、作者与来源链接 | **必填** |
| `--input-json` | 浏览器提取得到的字幕 JSON | **必填** |
| `-o, --output` | 输出文件路径；也可传目录，文件名按视频标题自动生成为 `{Sanitized_Title}.md` | 当前目录下的 `{Sanitized_Title}.md` |
| `--format` | 输出格式：`timestamps`（带时间戳块）、`clean`（纯文本段落）、`json`（原始数据） | `timestamps` |
| `--max-gap` | 自动合并连续短句的最大停顿时间（秒） | `2.5` |

---

## 输出位置

输出位置在调用时确定，技能本身不预设目录：

1. 用户明确指定了路径或目录 → 直接使用；
2. 否则遵循当前工作区的约定（如 AGENTS.md / CLAUDE.md 中写明的剪藏或收件目录）；
3. 都没有时，询问用户保存到哪里。

确定目录后通过 `-o <目录>/` 传入即可，文件名会按视频标题自动生成，例如 `<输出目录>/Monday Medications October 12th 2026.md`。

---

## 输出格式

- YAML Frontmatter：`title`、`source`、`author`、`created`、`description`、`tags`（`clippings`）。
- 正文：`## 逐字稿 (Transcript)` 下的时间戳段落（`**0:00** · text`）；`--format clean` 时为无时间戳的纯文本段落，适合速读或总结。
