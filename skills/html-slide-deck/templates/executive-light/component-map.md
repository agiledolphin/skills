# Executive Light Component Map

`executive-light` 是浅色商务/轻科技风格。组件 HTML 实现在本目录的 `template.html` 中，`component-gallery.html` 作为后续扩展更多视觉变体的展示馆。

组件说明书位于 `../../components/`。

## 使用原则

- 组件是参考坐标系，不是固定模具。
- 生成时保留组件的核心信息关系，允许根据内容调整比例、模块高度、视觉重心和内部结构。
- 如果只是颜色、字体、背景、阴影不同，优先通过本模板的 CSS 变量和设计语言调整。
- 如果布局、层级、动效或装饰结构不同，再在 `component-gallery.html` 中沉淀新变体。

## Components

### cover

- Spec: not yet split; follow `template.html` cover section.
- Selector: `section[data-component="cover"]`
- Variant: `executive-cover`

### section-divider

- Spec: `../../components/section-divider.md`
- Selector: `section[data-component="section-divider"]`
- Variant: `part-divider`
- Use for: topic changes, chapter transitions.

### two-category-cards

- Spec: `../../components/two-category-cards.md`
- Selector: `section[data-component="two-category-cards"]`
- Current variant: `with-bottom-takeaway`
- Base classes: `.scenario-slide`, `.scenario-wrap`, `.scenario-card`, `.scenario-bottom`
- Use for: current/target, problem/action, internal/external, before/after.
- Adaptation range: card ratio, visual side, list density, bottom takeaway treatment.

### three-cards

- Spec: `../../components/three-cards.md`
- Selector: `section[data-component="three-cards"]`
- Current variant: `numbered-action-cards`
- Base classes: `.opposition-slide`, `.opposition-row`, `.opposition-card`

### three-focuses

- Spec: to be split when this component recurs.
- Selector: `section[data-component="three-focuses"]`
- Current variant: `focus-map`
- Use for: three priorities, three management objects, three levers.

### evidence-case

- Spec: `../../components/evidence-case.md`
- Selector: `section[data-component="evidence-case"]`
- Current variant: `left-points-right-screenshot`
- Base classes: `.split`, `.case-copy`, `.case-visual`, `.image-box`

### management-rhythm

- Spec: `../../components/management-rhythm.md`
- Selector: `section[data-component="management-rhythm"]`
- Current variant: `three-cadence-cards`
- Base classes: `.management-axis`, `.management-card`

### summary

- Spec: `../../components/summary.md`
- Selector: `section[data-component="summary"]`
- Current variant: `five-takeaways`
- Base classes: `.plain-summary`, `.plain-item`

### closing

- Spec: not yet split; follow `template.html` closing section.
- Selector: `section[data-component="closing"]`
- Variant: `thank-you-cover`

