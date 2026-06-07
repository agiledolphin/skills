# HTML Slide Deck Interaction Reference

Use this reference when a user asks for a slide deck that should behave like the standard local HTML slide deck: full-screen slides, thumbnail overview, fullscreen shortcut, edit mode, local save, and export.

## Core Structure

- Use a root `#deck` element containing direct child `.slide` sections.
- Each slide should occupy a 16:9 viewport and use `.active` to control visibility.
- Keep slide content in a `.content` or `.canvas` wrapper.
- Add `#nav` for bottom progress dots.
- Add `#overview` with `#overviewGrid` for thumbnail overview mode.
- Add page numbers automatically from slide index, not manually.

## Navigation Behavior

- Right / Down / Space / PageDown: reveal current slide step first; if no step remains, go to next slide.
- Left / Up / PageUp: previous slide.
- Home: first slide.
- End: last slide.
- Mouse wheel: next or previous slide with a short lockout.
- Click on empty slide area: next slide.
- Touch vertical swipe: next or previous slide.

## Presentation Controls

- `F`: toggle fullscreen.
- `S`: toggle overview / slide index.
- `E`: toggle edit mode when the deck supports editing.
- `Escape`: close edit mode, exit fullscreen, or close overview.
- `F5`: refresh current slide animation while fullscreen.

## Overview Mode

- Overview mode should show scaled thumbnails grouped by section when the deck is large.
- Clicking a thumbnail closes overview and jumps to that slide.
- The active slide thumbnail and active bottom dot should be highlighted.

## Step Reveal Pattern

- Use `data-step="0"` on a slide or module.
- On next action, increment or set `data-step`.
- CSS should reveal hidden emphasis, zoomed screenshots, or second-stage examples using `[data-step="1"]`.
- When navigating back to a slide, reset its step state if the deck is designed for repeatable presenting.

## Editing Pattern

Only include editing controls when the deck is intended to be edited in-browser.

- Mark editable text with `.editable-text`.
- Mark draggable objects with `.editable-module`.
- Persist edits in `localStorage` using a deck-specific key.
- Support undo/redo for edit state.
- Keep editing separate from normal presentation navigation.

## Design Takeaway From The Reference Deck

- Use full-screen slide pages rather than a scrolling web article for presentation mode.
- Put navigation UI outside slide content so it does not disturb layout.
- Preserve page-level hierarchy: cover, transition pages, content pages, summary, closing.
- Use animations and step reveals to support live explanation, not as decoration.
