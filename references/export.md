# Export instructions

Requires Python 3 + Pillow (`python -m pip install Pillow`). Script: `scripts/sprite_tool.py`.

## Examples
```bash
python scripts/sprite_tool.py slice --sheet my_sheet.png --cols 4 --rows 2 --count 8 --out sliced --prefix walk --trim no
python scripts/sprite_tool.py qa --input sliced --config character.json --report qa.json
python scripts/sprite_tool.py pack --input sliced --out exported --character hero --action walk --direction right --fps 8 --columns 4 --zip
```

`--config` is optional JSON with keys `canvas` (two positive integers), `frame_count`, `baseline_y`, `palette` (list of exact hex RGB swatches), `require_alpha` (default true), `require_transparent_border` (default true), `alpha_mode` (`binary` default; `allow_partial` permits semitransparency), and `palette_tolerance` (0 means exact). Palette checking counts colors outside allowed RGB values; reserve exact palette enforcement for art that has already been palette-indexed.

## File outputs
```
exported/
  frames/frame_000.png ...
  atlas.png
  atlas.json
  contact_sheet.png
  README.txt
  [optional] exported.zip
```
Frame ordering: filenames sorted naturally. Atlas is uniform-grid row-major; frames retain entire canvas (no cropping). `atlas.json` includes image, frame dimensions, origin convention, animation name, direction, fps, loop, and frame rectangles. If JSON is imported into a specific engine, write an adapter only after verifying the engine version and exact format.

## Integration
- Phaser: load atlas JSON using a custom coordinates parser or convert to Phaser-compatible JSON Hash; do not assume this generic JSON is already Phaser's schema. Create animation using frame keys, fps, and loop metadata.
- Godot: import `atlas.png` as an `AtlasTexture` per rectangle or use individual PNG frames in `AnimatedSprite2D` / `SpriteFrames`. Disable texture filtering / use nearest-neighbor. Respect pivot positions in world-space.
- Unity: Sprite Mode Multiple and slice according to atlas grid, point filtering and no texture compression that smears pixel edges.

## Caveats
Atlas packing cannot repair bad drawings, pose direction, semantic anatomy, palette drift, antialiasing baked into the source, or a fake transparency grid. QA is deterministic raster inspection, not artistic certification.
