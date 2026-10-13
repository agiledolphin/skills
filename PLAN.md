# 后续任务

最后更新：2026-10-13

## 待办

### 1. 运行 evals
- 用 skill-creator 把 5 个技能的 evals 实际跑一遍，记录未通过的检查项，再据此修改技能。
- 目前只验证了 `evals.json` 的格式和测试材料，evals 本身还没跑过。
- 测试输出保存到 `./output/`。

### 2. transcript-diarizer：支持更多时间戳写法
- `verify_lossless.py` 目前只会去掉 `**0:00** ·` 这一种时间戳标签。
- 其他来源的稿子如果用 `[00:12]`、`(00:12)` 等写法，拆分时去掉时间戳会被当成删减内容，导致无损校验失败。
- 先确认手头稿子常见的时间戳写法，再加进识别规则（`split_transcript.py` 的时间戳分块规则也要同步）。

### 3. wechat-article-reviewer：补充链接抓取用例
- 现有 evals 只覆盖粘贴全文和内容不完整两种情况。
- 需要一个真实的 `mp.weixin.qq.com` 文章链接，用来测试 Agent Browser 抓取（方式 A）。

### 4. 同步笔记库中已部署的技能
- `wechat-article-review` 目录改名为 `wechat-article-reviewer`。
- 删除 `youtube-transcript`（2026-10-13 因限制较多已从本仓库移除）。
- `sentence-translator`、`transcript-diarizer` 换成修复后的脚本。

## 待定（暂不处理）

- **git 历史中的大文件**：早期提交过一个约 29MB 的测试 PDF（`pdf-translator` 的测试材料），已从当前文件中删除，但仍在历史里。清理需要改写历史并强制推送，暂不处理。
