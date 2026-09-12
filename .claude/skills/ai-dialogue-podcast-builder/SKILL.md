---
name: ai-dialogue-podcast-builder
description: Build a single self-contained HTML "podcast" player from a multi-speaker dialogue script — auto-plays through the script with different browser TTS voice/pitch/rate per speaker, synced karaoke-style captions, a comic-panel illustration that changes expression/scene per line, adjustable playback speed, and a closing "key quote" card. Use this whenever the user hands you a dialogue/interview/podcast script (especially ones with speaker labels like 主持人/工程師/主管/客戶, Host/Guest, etc.) and asks to turn it into a web page, an audio-visual player, a "podcast website", or an "AI dialogue video" — even if they don't use those exact words. Also use this to restyle an existing player built this way into a new visual theme (manga, industrial/HUD, flat meme-comic, etc.), to fix known bugs in it, or to add a new episode using the same engine.
---

# AI Dialogue Podcast Builder

Turns a written multi-speaker script into a single downloadable `.html` file that plays itself: browser text-to-speech per line, a different voice/pitch/rate per speaker, a simple illustrated character reacting on screen, and captions that light up as they're spoken. No build step, no server — it's one file the user can open in any browser or send to someone else.

This skill captures a working pattern that was iterated on live with a user over several rounds. Follow it as a checklist rather than reinventing the architecture each time — it avoids several non-obvious bugs (see "Known pitfalls" below).

## When NOT to oversell this

Be upfront, early, in your own reply (not buried) about what this is and isn't:
- Voices are the **browser's built-in TTS** (Web Speech API), not commercial AI voices (ElevenLabs/Azure/OpenAI TTS). Distinct-sounding speakers come from assigning each role a different pitch/rate and, where available, a different installed system voice — not from generating new voices. If the user wants true AI voice acting, tell them plainly that this environment can't call a paid TTS API for them (needs their own API key, and a key can't safely live in client-side HTML), and offer the fallback path: they generate per-line audio with a service of their choice, then hand you the audio files to wire into the player instead of `speechSynthesis`.
- Illustrations are simple generated SVG shapes (faces, icons, flat scene backgrounds), not real artwork — there is no image-generation tool in this environment. Say so if asked for "real" illustrations.
- Caption-sync quality depends on the browser firing `SpeechSynthesisUtterance.onboundary` events, which is inconsistent across browsers/OSes, especially for CJK text. Treat it as a best-effort enhancement, not a guarantee.

## Inputs to gather

1. **The script itself.** Speaker-labelled dialogue, ideally already grouped into scenes/beats. If the user pastes a script with very fragmented one- or two-word lines (common when someone formats a script with a blank line per beat for their own readability), don't blindly turn every fragment into its own caption — merge fragments back into natural spoken sentences per speaker turn. Only keep a fragment as its own beat when it's a genuine dramatic pause or a quoted "gotcha" line. A wall of one-word captions reads like a lecture, not a conversation.
2. **The role list** and, if given, a color/voice/personality direction per role (e.g. "host = light blue, calm; customer = pink, angry").
3. Whether there's a **closing element** (a "key quote" / call-to-action) that should get its own special end screen rather than just being the last spoken line.
4. Which **visual theme** — if unspecified, ask or pick one and say what you picked (options that have worked well: soft manga/halftone comic, dark industrial HUD/console, flat white meme-comic-carousel). Themes only change CSS + the character illustration's color palette; the data model and playback engine underneath stay identical, which is what makes re-skinning cheap later.

## Data model

Structure the script as **scenes containing lines**, not one flat array — this is much easier to extend and to compute per-scene visuals (background, icon, carousel dot) from:

```js
const ROLES = {
  "主持人": {key:"host", color:"#8ecae6", basePitch:1.00, baseRate:1.00, avatar:"主", side:"center", voicePref:"hanhan"},
  "工程師": {key:"eng",  color:"#c8961e", basePitch:0.85, baseRate:1.05, avatar:"工", side:"left"},
  // ...one entry per speaker. voicePref (optional) is a lowercase substring matched
  // against installed voice names, e.g. "hanhan" to prefer a voice literally named that.
};
const DEFAULT_EXPR = {"主持人":"calm", "工程師":"neutral", "主管":"stern", "客戶":"angry"};

const SCRIPT = [
  {bg:"studio", tag:"開場", icon:"clock", lines:[
    ["主持人", "……line text……"],
    ["主持人", "……line text……", {expr:"stern"}],   // optional override: {expr, effect, sfx}
  ]},
  // ...more scenes
];

// flatten once at load time:
const d = [], PANELS = [], ICONS = [];
SCRIPT.forEach((scene, sceneIdx) => {
  scene.lines.forEach(([role, text, meta]) => {
    d.push([role, text]);
    PANELS.push({bg: scene.bg, expr: (meta&&meta.expr) || DEFAULT_EXPR[role] || "neutral",
                 effect: (meta&&meta.effect) || null, sfx: (meta&&meta.sfx) || "",
                 tag: scene.tag, sceneIdx});
    ICONS.push({/* left/right icon badges derived from scene.icon + ROLES[role].side */});
  });
});
```

**Match expression to content, not just to speaker.** Give every role a sensible `DEFAULT_EXPR`, but override per-line whenever a line carries a distinct emotion (realization → `spark`, being caught out → `sheepish`+`sweat`, a pointed complaint → `angry`+`impact`, a serious warning → `stern`). Re-read the script line by line for this rather than leaving everything on the role default — it's the difference between a static illustration and one that feels responsive.

## Face/character illustration

A small parametrized inline-SVG generator works well and is cheap to re-theme (just change the hex colors and body-shape paths, keep the expression logic):

- Base: an ellipse "hair/hood" shape filled with `ROLES[role].color`, an ellipse "face" in a neutral skin tone, plus brows/eyes/mouth paths that change per `expr` (confident / sheepish / calm / angry / shocked / stern / spark, at minimum).
- Keep the expression-drawing logic as pure functions of `(role, expr)` so it's reusable across every visual theme — only the surrounding CSS/scene chrome should differ between themes.

## Playback engine

- `speakCurrent(onend)`: builds one `SpeechSynthesisUtterance` per line, sets `voice`/`pitch`/`rate` from that role's config, and calls `onend` to advance. If any text needs to be spelled out letter-by-letter (e.g. an acronym like "SOP"), transform **only the TTS input string**, never the on-screen caption — e.g. replace `"SOP"` with `"S O P"` (no periods — periods force a pause between letters; plain spaces read the letters back-to-back without one).
- **Caption sync**: use `utterance.onboundary`, and since the spoken string can differ from the displayed string (see the acronym case above), map progress by *character-index ratio*, not raw index:
  ```js
  u.onboundary = (e) => {
    const ratio = Math.min(1, e.charIndex / Math.max(1, spokenText.length));
    const cut = Math.round(ratio * displayText.length);
    speechBubble.innerHTML = `<span class="said">${displayText.slice(0,cut)}</span><span class="unsaid">${displayText.slice(cut)}</span>`;
  };
  ```
  Give `.said` and `.unsaid` **visibly different CSS colors** (e.g. full ink vs. light gray, or amber vs. dim) — it's easy to accidentally ship both the same color when re-theming and silently kill this feature. Double check this after every visual restyle.
- **Scene transitions**: a quick full-panel "shutter" flash (opacity 0→1→0 over ~100ms) between lines reads as a theatrical cut rather than a hard jump. Trigger it in `next()`/`prev()` and between auto-play steps.
- **End card**: if the script has a closing quote/CTA, don't just let it play as the last ordinary line and stop — after the last line finishes speaking, transition into a dedicated static screen combining the key quote + the call-to-action, and make replaying easy (pressing play again when parked on the end screen should restart from line 0).
- **Playback speed**: expose a single global rate slider (a sensible default range is 0.75×–1.5×) that multiplies each role's own base rate, so relative pacing between speakers is preserved at any speed.
- **Voice-casting panel**: always expose a small settings panel — one card per role with a voice `<select>` (populated from `speechSynthesis.getVoices()`, filtered to the target language), plus pitch/rate sliders — because available system voices vary wildly by device/OS and the user will want to fix a bad auto-assignment. Auto-assign by round-robin across available voices by default, but let `ROLES[role].voicePref` (a name substring) override the pick when present.

## Known pitfalls (avoid re-introducing these)

1. **Never swap a live element via `outerHTML` inside a function you'll call repeatedly.** E.g. `charSvg.outerHTML = newMarkup` replaces the DOM node but leaves your JS variable pointing at the now-detached old node — every *subsequent* call silently edits an orphan that's no longer on screen, so the visual appears to freeze after the very first update. Instead, keep one persistent element (e.g. `<svg id="charSvg">`) and update only `charSvg.innerHTML` (or `.textContent`/attributes) on it. This bug is easy to miss because the *first* render always looks correct.
2. **When re-theming, re-check every color pair that carries meaning**, not just the obvious ones — it's easy to leave two states (like the said/unsaid caption colors above) both mapped to the same CSS variable after a palette swap, silently disabling a feature while everything still "looks fine" at a glance.
3. Consolidate over-fragmented scripts (see Inputs above) — don't mechanically turn every newline into its own caption beat.
4. Keep voice/pitch/rate, expression-per-line, and CSS theme as three separate layers. If asked to change colors or swap the visual theme, touch CSS/markup only. If asked to change voices/expressions, touch the `ROLES`/`DEFAULT_EXPR`/per-line `meta` only. Don't conflate the two — it's what makes both kinds of requests fast to execute.
5. **A thrown error inside `showEndCard()` silently kills the ending — check for orphan element references after every re-theme.** A leftover `document.getElementById("sceneTag")` (an element deleted during a re-theme, while the JS reference and a same-named CSS class survived) resolves to `null`; the very next line that touches it (`sceneTag.textContent = ...`) throws, and because it runs before the line that actually renders `GOLDEN_QUOTE`/`MANAGER_QUESTION`, the whole end card silently never shows its text — no console-visible symptom in casual testing, no visual sign except the quote/CTA simply never appearing. After any restyle, grep every `document.getElementById(...)` target against the current markup's `id="..."` attributes and delete dead references immediately, don't leave them "just in case".
6. **Make the end card (key quote / CTA) reachable without a perfect full autoplay.** If `next()` simply no-ops once `i` hits the last line, a user who skims manually with the prev/next buttons — or whose autoplay stalls because a `SpeechSynthesisUtterance.onend`/`onboundary` event never fires (common in real browsers over a long multi-speaker script) — will never see the closing quote/CTA at all, silently. Track an `onEndCard` flag; have `next()` transition into `showEndCard()` when pressed on the last line, and `prev()` step back out of the end card to the last line. Don't rely on the autoplay chain finishing cleanly as the only path to the ending.
7. **Don't let a theme quietly blank out the content-driven visual layers.** The bundled flat-meme-comic-carousel theme in `assets/template.html` shipped with `.bgLayer{display:none}` and `.speedlines,.impact,.sparkWrap,.iconRow{display:none!important}` — the scene backdrop, the per-line reaction effects, and the corner icon badges were fully wired up in the JS/data model (every scene already carries a `bg` and an `icon`, every line can carry an `effect`) but had zero visual expression, because an earlier restyle blanked them without ever writing this theme's own version. The symptom looks exactly like "the visuals don't reflect the dialogue" even though the data was correct all along — check for this class of bug (a data-correct-but-CSS-suppressed layer) before assuming the script/JSON needs more detail. The fix that was applied here, safe to reuse: give each `bg-*` value its own soft background tint plus a large, low-opacity (~7%) watermark of that scene's `icon` (rendered via the existing `iconSVG()`, set in `render()`/`showEndCard()` — add `icon: scene.icon` to the `PANELS` entries if it isn't already carried), restore the small `iconRowLeft`/`iconRowRight` corner badges, and give `.speedlines`/`.impact`/`.sparkWrap` a real `opacity:0` → `.on{opacity:1}` transition instead of `display:none`. None of this touches `faceSVG()`/`ROLES` — the character illustration is a separate layer and should stay untouched unless the user explicitly asks to change it.

## Output & delivery

- Single `.html` file, no external build step. External Google Fonts `<link>` tags are fine (the user's own browser fetches them). No `localStorage`/`sessionStorage`.
- Save to the outputs directory and present it with the file-sharing tool so the user gets a real file card, not just inline code.
- If the user asks for a new episode using the same engine, copy the working file, replace the `SCRIPT` (and `GOLDEN_QUOTE`/end-card text if present), and leave the engine/theme untouched unless told otherwise.

## Starter template

`assets/template.html` is a trimmed, working skeleton with all of the above already wired up (4 example roles, 2 example scenes, the flat meme-comic-carousel theme, voice-casting panel, caption sync, end card). Copy it, then:
1. Replace `ROLES` / `DEFAULT_EXPR` with the user's roles and direction.
2. Replace `SCRIPT` with the user's script, consolidated per the Inputs section.
3. Replace `GOLDEN_QUOTE` / `MANAGER_QUESTION` (or delete the end-card call in `playFrom` if there isn't a closing quote).
4. Only then, if asked, reskin the CSS `:root` variables and panel chrome for a different visual theme.
