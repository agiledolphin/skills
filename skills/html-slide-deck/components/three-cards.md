# Three Cards

## 用途

表达三个平级对象、动作、风险、选择、策略或判断。

## 输入参数

- `section_label`
- `title`
- `cards[]`
  - `no?`
  - `label?`
  - `title`
  - `detail`
  - `visual?`
- `note?`

## 稳定核心

- 三个卡片必须平级可比。
- 每张卡片的信息密度应接近。
- 如果第三项只是总结，不应使用该组件，应使用 `two-category-cards/with-bottom-takeaway`。

## 密度规则

- 每张卡片至少包含标题 + 2 个有效信息点，或标题 + 1 个明确指标/图形。
- 不要把三张稀疏卡片拉高来填满页面；卡片三分之二以上为空时，改成 `data-hero`、`quote-statement`、`process-flow`、紧凑卡片行或图解。
- 三张卡片视觉重量必须接近；如果某一张明显短，优先重组文案、改成非对称布局或拆页。
- 三卡页适合表达并列关系，不适合承载很少的口号、金句或单一结论。

## 常用变体

- `numbered-action-cards`: 三个编号动作或策略。
- `risk-response-cards`: 三类风险、约束或应对。
- `option-cards`: 三个方案或选择。

## 不适合

- 时间顺序特别强的内容，优先用 `timeline` 或 `process-flow`。
- 两个主对象加一个总结句，优先用 `two-category-cards/with-bottom-takeaway`。
- 内容少到无法支撑三张大卡片的页面。
