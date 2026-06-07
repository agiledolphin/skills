# Editable HTML Deck

Use this reference when implementing or modifying browser edit mode, localStorage persistence, exported HTML, or handoff behavior.

## Edit Mode Contract

- `E` toggles edit mode.
- Text elements become `contenteditable`.
- Major modules/cards can be dragged.
- Selected elements show a clear blue outline.
- A floating mini toolbar appears near the selected element with bold, font-size increase/decrease, blue/ink/grey text color, and hide/delete.
- The main edit toolbar should stay simple:
  - `本机保存`: save edits to this browser's `localStorage`.
  - `另存共享`: export a new edited HTML file or prompt the browser's file picker for sharing/handoff.
- Do not show `清空本机保存` in the main toolbar by default. If reset is required, place it behind a More/advanced action, style it as destructive, and require confirmation.
- Do not show Undo/Redo buttons in the main toolbar by default. Keep undo/redo as keyboard shortcuts.

## Persistence

- Save text, simple inline style changes, hidden/deleted state, and dragged positions to `localStorage`.
- Use a clear versioned key, for example `deck-edit-state-v2`.
- Version the key when old browser edits should be ignored.
- If the user says "the file changed but the browser did not", check browser cache and old localStorage state before assuming the edit failed.
- Do not remove or reset browser-local edits unless the user asks or confirms the file version should override them.

## Interaction Safety

- Edit-mode clicks must not trigger slide navigation, reveal-state changes, or screenshot state toggles.
- Draggable modules should preserve animation transforms by using CSS variables such as `--edit-x` and `--edit-y`.
- Keyboard editing shortcuts:
  - `Ctrl+Z`: undo.
  - `Ctrl+Y` / `Ctrl+Shift+Z`: redo.
  - `Ctrl+B`: bold selected text.
- In edit mode, force animated elements to final visible state when needed so users can edit what they see.

## Export HTML

- Pure HTML cannot silently overwrite itself on disk.
- Browser file writing requires user approval via File System Access API, or fallback download.
- Exported HTML should serialize the edited DOM and remove runtime-only UI.
- Clear generated overview thumbnails and navigation controls in the cloned document before serialization.
- Query slides from `#deck > .slide` rather than global `.slide` so overview clones are not included.
- Exported HTML must not persist active edit outlines, floating toolbars, or temporary export classes.

## User-Facing Explanation

When relevant, explain:

- `本机保存` keeps edits in this browser via `localStorage`.
- `撤销` / `重做` only operate inside the current browser editing session.
- `另存共享` writes a new/overwritten file for sharing after browser approval.
- `清空本机保存`, when present, only clears this browser's saved local draft and does not modify exported files.
