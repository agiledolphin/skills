# Delivery Checklist

Use this checklist before final delivery, packaging, PNG capture, or PPTX export.

## Structure

- The browser deck uses full-viewport mode by default: slides fill `100vw x 100vh`.
- The layout uses `vw`, `vh`, `min(vw, vh)`, and fixed aspect-ratio modules carefully so it does not only work by accident on one screen.
- Browser playback/editing does not show fixed-stage side letterboxes.
- If a locked 16:9 browser stage is explicitly requested, letterbox or overflow areas inherit the deck background rather than plain white.
- Cover and back cover do not show content-page title bars unless intentionally designed.
- Content pages have consistent title position, title size, and page number treatment.

## Content And Layout

- Visible slide text matches the source copy unless the user requested rewriting.
- Each page has one clear main visual anchor.
- Tables/cards/screenshots occupy enough space to avoid floating in empty canvas.
- Left/right modules have comparable visual weight and baseline alignment.
- Bottom whitespace is not much larger than top whitespace.
- Repeated page structures have deliberate rhythm rather than accidental sameness.
- Background decorations stay behind content and do not compete with tables or screenshots.
- Template-specific cover, agenda, section/transition, and closing pages keep their original structure, logo, background, and intended whitespace unless the user explicitly asks to redesign them.
- Density checks apply mainly to ordinary content pages; do not force cover, agenda, transition, quote, data-hero, or closing pages into ordinary content-page coverage.
- Ordinary content pages do not use large empty areas as a substitute for design. If the lower half has more than `28vh` of unanchored empty space, re-layout the slide.
- Large cards must contain layered information: title plus at least two effective points, or title plus one clear metric/visual. If two thirds of a card is empty, shrink it or switch to data-hero, quote-statement, timeline, process, matrix, or compact cards.
- Tables should be the main visual anchor when used. If a table is small, floating, or sparse, convert it into a matrix, structured cards, or key-number layout.
- Screenshots and evidence visuals must be inspectable. They should usually occupy `55%` to `70%` of body width, or at least `60%` of body height in image-led pages.
- Two-column pages should not leave one side visibly underfilled. If one side has less than about `55%` body-height effective content, switch to an asymmetric visual/text layout or another page type.

## Interaction

- `F`, `S`, `E`, arrow keys, Space, PageUp/PageDown, Home, and End work.
- Slide index thumbnails are grouped and clickable.
- Edit mode makes intended text editable and intended modules draggable.
- Edit mode clicks do not trigger navigation or custom reveal states.
- Custom `data-step` slides still work after entering and exiting edit mode.
- Undo/redo and bold shortcuts work if edit mode is implemented.

## Export Safety

- Export/thumbnail modes show completed slide states, not mid-animation states.
- Runtime-generated overview thumbnails and nav buttons are not serialized into exported HTML.
- Active edit outlines, floating toolbars, and temporary classes are not serialized.
- Image paths are relative and images are included in the packaged folder.
- If packaging a deck, include `index.html` and the referenced `images/` folder together.

## PNG/PPTX Export

- Do not export PNG/PPTX while the user is still approving the HTML design.
- Capture each slide at exactly `1920 x 1080`.
- Verify every PNG dimension is `1920 x 1080`.
- Build PPTX slides as full-slide images.
- Check at least the cover, one dense content page, one screenshot page, and the closing page after PPTX generation.

## Handoff Notes

For multi-round projects, keep a short project note with:

- Current entry HTML file.
- Image folder.
- Edit storage key.
- Special page interactions and `data-step` behavior.
- Recently confirmed title bars, labels, and page-specific decisions.
- Known browser-cache or localStorage caveats.
