# Project Instructions

This workspace is dedicated to the development and evaluation of **Skills**. Each skill is located in the `./skills/` directory and follows a standardized structure.

- **Python Tooling:** Use `uv` for all Python-related tasks, including package management, environment handling, and running scripts.
- **Git Policy:** Maintain a minimal `.gitignore`. Only ignore `.venv/` and `.DS_Store` unless explicitly instructed otherwise.

## Skill 标准目录结构

每个技能应位于 `skills/<skill-id>/` 目录下，并遵循以下结构：

```text
skills/<skill-id>/
├── SKILL.md           # [必需] 核心指令、触发条件及工作流定义 (包含 YAML frontmatter)
├── scripts/           # [可选] 该技能专用的辅助脚本 (使用 uv run 运行)
├── evals/             # [可选] 评测集 (包含 evals.json)
├── references/        # [可选] 大型参考文档或指南
└── assets/            # [可选] 静态资源、模板、图标等
```

### 规范说明

1. **SKILL.md**: 必须包含 `name` 和 `description` 的 YAML frontmatter。指令应简洁明了，优先解释“为什么”。
2. **scripts/**: 存放为了实现确定性或重复性任务而编写的脚本。推荐在脚本中使用内联依赖声明 (PEP 723)，以便通过 `uv run` 直接运行。
3. **evals/**: 包含 `evals.json`，用于自动化评估技能的表现。
