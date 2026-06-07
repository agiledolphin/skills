# Internal Report Design

Use this reference for the visual system of internal business reports, leadership reviews, finance/AI reports, and management mechanism decks.

## Visual Positioning

- Tone: calm, professional, light technology, readable for leadership review.
- Palette: pale blue base, cyan/violet accents, deep navy text.
- Surface: glass-like white cards with subtle borders and soft shadows.
- Background: soft gradient, blue abstract cover visual, and restrained translucent geometry.
- Typography: Source Han Sans / Noto Sans CJK first. Avoid unstable system fallback where possible.
- Browser playback uses full-viewport layout by default. Use `1920 x 1080` only for PNG/PPTX export capture.

## Page System

- Cover: report category, report title, month/date. No page header.
- Cover background: keep the generic blue abstract SVG inlined in the HTML template; do not require an external image file for the template cover.
- Content: consistent top-left title bar with small blue mark, page number top-right.
- Section divider: part label, section kicker, section title, short guide sentence.
- Back cover: same visual system as cover, usually closing only.

## Template Page Types

- Cover page.
- Opening point page.
- Center statement page.
- Section divider.
- Three-focus page.
- Three-card strategy page.
- Two-category card page.
- Screenshot/case page.
- Management rhythm page.
- Summary page.
- Back cover.

Do not include all page types by default. Select the smallest set that matches the user's content shape.

## Layout And Composition

- Do not let tables float as small objects in large empty pages.
- For two peer modules, use equal widths unless hierarchy requires otherwise.
- For a governing principle, use a full-width band instead of a peer card.
- Center statements can sit above cards, but they should not create excessive vertical gaps.
- If a page feels empty, first adjust content area height and vertical placement before adding decorative elements.
- Keep screenshots and evidence blocks large enough to inspect.
- Keep background elements behind content and low enough contrast to avoid fighting tables or screenshots.
- Cover, section divider, agenda, quote/data-hero, and closing pages may keep deliberate whitespace. Ordinary content pages must not use large empty areas as a substitute for layout.
- Ordinary content pages should have one dominant body structure: large table, large screenshot/evidence, two-column comparison, compact card group, process/timeline, matrix, or data hero.
- If a table, card group, or screenshot occupies only a small center area, re-layout before adding decoration.
- Sparse content should become `data-hero`, `quote-statement`, `process-flow`, or a compact diagram instead of oversized empty cards.
- Large cards need layered content: title plus two points, a metric, a visual, or a divider/tag structure. Do not leave most of a card blank.

## Reusable Visual Details

- Title mark: small blue gradient folded-corner or flag shape before content-page title.
- Cards: `rgba(255,255,255,.72-.88)` backgrounds, `rgba(118,139,172,.18-.26)` borders, 14-22px radius.
- Accent chips: blue/violet gradient rounded rectangles for object labels.
- Icon style: blue/violet line illustration, light fill, small cyan/red dots only when they do not duplicate table information.
- Screenshot placeholders: dashed blue frame or pale blue evidence container, not real project imagery.

## When User Provides A Reference Image

Adapt this preset instead of rebuilding from scratch:

- Keep F/S/E deck infrastructure.
- Keep full-viewport browser playback; use `1920 x 1080` only for PNG/PPTX export capture.
- Replace palette/background/card geometry as needed.
- Preserve the content density and layout review rules.
