// extract_transcript_panel.js
//
// Extracts a YouTube transcript from the watch page's transcript panel.
// Run on an open YouTube watch page via agent-browser:
//   agent-browser eval --stdin < scripts/extract_transcript_panel.js > raw.json
// Opens the transcript panel, waits for segments, and returns a JSON string of
// [{text, start, duration}] that format_transcript.py accepts via --input-json.
// On failure returns a JSON string of {error}.
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // YouTube has shipped two panel structures; selectors are structural so the UI language does not matter.
  const STRUCTURES = [
    { segment: "transcript-segment-view-model", time: ".ytwTranscriptSegmentViewModelTimestamp", text: "span.ytAttributedStringHost" },
    { segment: "ytd-transcript-segment-renderer", time: ".segment-timestamp", text: ".segment-text" },
  ];
  const findSegments = () => {
    for (const s of STRUCTURES) {
      const nodes = document.querySelectorAll(s.segment);
      if (nodes.length) return { s, nodes: [...nodes] };
    }
    return null;
  };

  if (!findSegments()) {
    const expand = document.querySelector("#description-inline-expander #expand, tp-yt-paper-button#expand");
    if (expand) expand.click();
    await sleep(500);
    const button =
      document.querySelector("ytd-video-description-transcript-section-renderer button") ||
      [...document.querySelectorAll("button")].find((b) =>
        /transcript|文字|转写|轉錄/i.test(`${b.innerText} ${b.getAttribute("aria-label") || ""}`)
      );
    if (!button) return JSON.stringify({ error: "Transcript button not found (video may have no transcript)." });
    button.click();
  }

  let found = null;
  for (let i = 0; i < 30 && !found; i++) {
    found = findSegments();
    if (!found) await sleep(500);
  }
  if (!found) return JSON.stringify({ error: "Transcript panel opened but no segments appeared within 15s." });

  const toSeconds = (t) => t.split(":").map(Number).reduce((acc, n) => acc * 60 + n, 0);
  const items = found.nodes
    .map((node) => ({
      start: toSeconds((node.querySelector(found.s.time)?.textContent || "").trim()),
      text: (node.querySelector(found.s.text)?.textContent || "").trim(),
    }))
    .filter((item) => item.text);
  // The panel only shows start times; approximate each duration as the gap to the next segment.
  items.forEach((item, i) => {
    item.duration = i + 1 < items.length ? items[i + 1].start - item.start : 5;
  });
  return JSON.stringify(items);
})();
