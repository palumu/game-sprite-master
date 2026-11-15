---
name: game-sprite-master
description: Create, plan, critique, validate, and export production-ready 2D pixel-art character sprites and sprite sheets for 16-bit side-scrolling beat-'em-ups and top-down/three-quarter survival-horror RPGs such as Z Bom. Use for sprite reference preservation, animation frame planning, four-direction consistency, transparency cleanup, sprite slicing, QA, sprite atlases, animation metadata, and game-engine-ready ZIP packages.
---

# Game Sprite Master

Follow a reference-first, non-destructive pipeline: **identify game profile -> freeze character contract -> plan action/direction poses -> produce artwork -> review visually -> validate raster -> package/export**. Do not equate an attractive concept sheet with production-ready sprites.

## 1. Interpret the request
- Select **beat-em-up-16bit** or **zbom-rpg**. Read the corresponding profile in `references/profiles.md`.
- Identify whether the task requests **concept**, **reference sheet**, **animation poses**, **separate PNG frames**, or a **game-ready pack**. Do not silently promise the last from the first.
- Collect supplied images, original sprites, frame specifications, prior approved reference, direction labels, and target engine. If omitted, proceed with documented defaults and mark assumptions; ask only if an essential asset or decision is missing.
- Treat previously approved character designs as binding; never reinterpret locked identity details. For Z Bom, Ton's existing gameplay sprites are already made; distinguish cinematic character reference from gameplay sprites.

## 2. Make a character contract
Record `character_id`, profile, version, facing, base canvas, visible height, head-to-body ratio, palette swatches (hex), outline thickness, hard silhouette traits, costume components with left/right placement, origin/pivot, floor baseline, direction asymmetries, and **DO NOT CHANGE** elements. Read `references/consistency.md`.
- Make a single canonical neutral pose / turnaround before an action set when no approved original exists.
- When a reference exists, favor image edit/inpainting with the supplied reference over regeneration from prose. Keep reference visible through each revision.
- Do not invent exact pixel dimensions from a picture. Use user-provided specs or explicitly propose dimensions for approval/verification.
- For generation prompts, specify per-frame direction, moving limb, foot contact, occlusion, opposite arm, face visibility, and intended action. If action is ambiguous, storyboard it first.

## 3. Plan animation
Read `references/animation.md`. Produce an action table with: `action`, `direction`, `frame_count`, `fps`, `frame_names`, timing, anticipation/contact/follow-through, anchor coordinates, intended foot position, and transitions.
- For walk/run, audit alternating planted feet, arms counter-swinging, which foot leads, and facing. Never simply duplicate frames or mirror asymmetrical details without inspection.
- For attacks, identify which hand is nearer camera and which arm is partially obscured. Keep hitbox and animation timing separate from drawn pixels.
- Z Bom uses explicit front/back/left/right by default; the beat-em-up defaults to right-facing with left mirroring only where the reference permits it.

## 4. Produce and inspect
- Generate or edit images only with an actually available image tool. A Skill does not provide an image generator by itself. Do not simulate tool success or claim that an AI sheet is pixel-perfect.
- Prefer one pose/frame at a time when strict consistency is critical, or well-spaced sheet cells with a specified grid and no touching silhouettes.
- Explicitly require hard pixels, no antialiasing where feasible, genuine RGBA alpha, no text/labels in cells, stable canvas and anchor, and no cast shadow unless specifically required.
- Inspect each delivered frame at native resolution and 8x nearest-neighbor enlargement. Use reference overlay, silhouette comparison, anchor alignment, and per-frame QA. Regenerate or manually correct defects rather than pretending scripts fix anatomy.
- If a generator returns only a composited preview or fake checkerboard, flag it as **not export ready** until alpha is truly extracted and checked.

## 5. Process files and run checks
Use `scripts/sprite_tool.py` (Python 3 + Pillow) for deterministic operations:

```bash
python scripts/sprite_tool.py slice --sheet sheet.png --cols 4 --rows 2 --count 8 --out frames --prefix walk --trim no
python scripts/sprite_tool.py qa --input frames --config character.json --report qa.json
python scripts/sprite_tool.py pack --input frames --out dist --character ton --action walk --direction front --fps 8 --columns 4 --zip
```

- `slice` assumes equal grid cells and cannot infer poses from arbitrary collages. Use `--trim yes` only when transparent padding must be removed; it can lose pivot/anchor alignment. Never auto-remove background from artwork as though it were alpha.
- `qa` checks file decode, RGBA transparency, partially transparent pixels, canvas size, empty/nontransparent borders, occupied bounding boxes, frame count (if set), baseline presence (if configured), and colors outside an optional approved palette. It is a **technical** check, not a substitute for human evaluation of animation, facing, style, or identity.
- `pack` produces consistent-size frame PNGs, a horizontal/row-major atlas, `atlas.json` with frame coordinates and animation metadata, a contact sheet, and optional ZIP. It retains frame canvases; do not pack variable-sized cells without explicit pivot transformation.
- Never upscale pixel-art via bilinear/bicubic interpolation. Use nearest-neighbor.

## 6. Gate and deliver
Require (a) reference fidelity reviewed; (b) all requested poses/directions accounted for; (c) individual RGBA PNGs; (d) dimensions and origin consistent; (e) game metadata and preview; (f) actual pass/fail QA report. If any is missing, label output **concept only**, **needs cleanup**, or **game-ready with caveats**.
- When delivering game-ready assets, package frame PNGs, atlas PNG, metadata JSON, contact sheet, `qa.json`, and a short README with engine import notes. Provide links only for files actually created.
- Keep versions immutable (`v0.2`, `v0.3`); record exact differences from approved version. If QA fails, show blockers and concrete fixes instead of giving a false pass.

## Reference files
- `references/profiles.md`: beat-em-up / Z Bom art and camera contracts.
- `references/consistency.md`: character lock checklist and image-generation prompt contract.
- `references/animation.md`: directional action planning and QA gates.
- `references/export.md`: formats, commands, manifest schema and engine integration notes.
