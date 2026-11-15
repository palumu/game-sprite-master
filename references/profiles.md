# Game profiles

## beat-em-up-16bit
- Thai vocational / Bangkok side-scrolling beat-em-up: detailed 16-bit hard-edge pixel art, roughly one-pixel dark outlines at the *chosen native resolution*, consistent sprite density/lighting/color language; 2D oblique side view, typically right-facing.
- Use an approved character sheet as the scale, pixel-unit, and wardrobe authority. Align feet to shared baseline. Respect relative height (e.g. larger bosses) without inadvertently enlarging heads, shoes, or texture resolution.
- Reference-era characters may feature navy shop shirts, Thai-school canvas shoes, detailed hair silhouettes, strong attack silhouettes; no unrequested school emblems, identifying logos, real-school symbolism.
- Keep gameplay area separate from scenic floor objects and hitboxes; sprites usually RGBA transparent. Magenta `#FF00FF` is only a *requested color-key alternative*, not a substitute for real alpha unless engine import is configured accordingly.
- Default animation naming: `idle`, `walk`, `run`, `jab`, `hook`, `kick`, `hurt`, `launched`, `down`, `getup`; directional suffix only if applicable.
- Do not impose a fixed 72x88 frame or 68-90 px visible height on all characters; negotiate from real approved sprites. Never claim visual pixel density is exactly 1 px from a generated raster without inspecting it.

## zbom-rpg
- Z Bom: muted, gritty, detailed 16-bit pixel art; top-down/three-quarter RPG/survival horror view; non-chibi human proportions; worn and restrained colors; crisp hard pixels. Canonical orientations: `front`, `back`, `left`, `right`.
- Preserve costume topology under rotation (straps, pockets, hair part, sleeves, carried gear); do not blindly mirror left and right when clothing is asymmetrical.
- Lighting and camera must agree across frames. 3/4 front, back, and side are deliberately drawn, not a 2D flip of a single pose.
- Ton's gameplay sprites already exist in the user's ongoing project context; a Ton reference for opening cinematic is not a request to create redundant game sprites. Avoid mixing cinematic proportions and in-game scale.
- Keep per-direction eye line, feet origin, silhouette sizes, and palette stable. Typical actions: idle, walk, run, interact, hurt, attack (only when required), die.

## Priority when evidence conflicts
1. User's latest explicit correction.
2. User-provided and approved image/source sprite.
3. Character-specific lock sheet / source-of-truth asset.
4. Profile guidelines.
5. Generic defaults.

Document all deviations and never silently override a supplied art-direction decision.
