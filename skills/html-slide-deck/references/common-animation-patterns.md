# Animation Patterns

Use CSS-only animations by default for internal report decks. They are stable, export-friendly, and keep the HTML self-contained.

## Default Reveal

Use a simple upward fade:

```css
@keyframes fade-rise {
  from { opacity: 0; transform: translate(var(--edit-x,0), calc(var(--edit-y,0) + 28px)); }
  to   { opacity: 1; transform: translate(var(--edit-x,0), var(--edit-y,0)); }
}
```

When edit mode supports draggable modules, animation transforms must include `--edit-x` and `--edit-y` so manual positions are not overwritten.

## Reading Order Patterns

### Statement Then Cards

Use for pages with a summary sentence and two modules.

1. Statement appears.
2. Left card appears.
3. Right card appears.

Recommended timing:

```css
.slide.active .lead { animation: fade-rise .58s ease .12s both; }
.slide.active .card:first-child { animation: fade-rise .62s ease .58s both; }
.slide.active .card:nth-child(2) { animation: fade-rise .62s ease .98s both; }
```

### Principle Then Steps

Use for pages with a top governing principle and lower steps.

1. Full-width principle band appears.
2. Step 1 appears.
3. Step 2 appears.

Recommended timing:

```css
.slide.active .principle-band { animation: fade-rise .58s ease .12s both; }
.slide.active .step-panel:first-child { animation: fade-rise .62s ease .58s both; }
.slide.active .step-panel:nth-child(2) { animation: fade-rise .62s ease .98s both; }
```

## Export And Thumbnail Safety

Always force animated elements to final state in:

- `body.export`
- overview thumbnail clones
- `prefers-reduced-motion: reduce`
- `body.edit-mode`

Example:

```css
body.export .animated,
.overview-thumb .animated,
body.edit-mode .animated {
  opacity: 1 !important;
  animation: none !important;
  transform: translate(var(--edit-x,0), var(--edit-y,0)) !important;
}
```

## When To Use Motion One

Only add a bundled animation library when the deck needs complex staged effects, timeline control, or many reusable animation recipes.

If adopting Motion One, follow the guizang pattern:

- Put `motion.min.js` in `assets/`.
- Mark elements with `data-anim`.
- Prefer local import first, CDN fallback second, static fallback last.
- Make all `[data-anim]` visible if the library fails to load.
