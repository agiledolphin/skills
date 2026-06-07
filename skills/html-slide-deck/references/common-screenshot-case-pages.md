# Screenshot And Case Pages

Use this reference for slides built around product pages, internal systems, project examples, before/after cases, or evidence screenshots.

## Design Rules

- Prefer real screenshots or reconstructed HTML evidence over generic illustration.
- Give screenshots enough canvas area to be readable.
- A screenshot-plus-commentary page usually works best as about two-thirds visual and one-third interpretation.
- Use short state labels above screenshots when they help the presenter explain sequence, such as `示例一`, `示例二`, `功能已上线`, or `面向售前`.
- Keep commentary short. It should interpret the evidence, not repeat the title.
- Use consistent image frames within the same section: same border, background, radius, and caption treatment.

## Image Handling

- Keep images in a sibling `images/` folder unless the user asks for a fully embedded single file.
- Use relative paths so the deck can be packaged and moved.
- Prefer stable names tied to page and meaning, for example `P8-1.png`, `08-strategy-before.png`, or `10-presales-example.png`.
- When replacing or removing screenshots, search both CSS and JS for filename references and state-specific selectors.
- For dense UI screenshots, use `object-fit: contain` and a clean background rather than cropping away important text.
- For decorative or generated evidence visuals, use fixed aspect-ratio containers so layout does not shift.

## Interactive Case States

- If a slide has click-to-reveal or click-to-switch states, store the state on the slide with `data-step`.
- Make click and keyboard behavior explicit in the script.
- Do not let edit-mode clicks trigger slide navigation or reveal-state changes.
- When a reveal state overlays a cropped or enlarged image on top of a full screenshot, ensure the final state is visible in export and thumbnail modes.
- If arrow keys advance from a revealed state to the next slide, document that behavior in project handoff notes.

## Checks Before Delivery

- Are all screenshots visible at the intended state?
- Can the audience read the important part of each screenshot?
- Does each label describe state or audience, not decoration?
- Does the slide still work after entering and exiting edit mode?
- Do export and thumbnail modes show the completed state rather than a mid-animation or hidden state?
