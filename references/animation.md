# Animation direction

## Action planning table
For each action record: `action`, `direction`, `frame_names`, `fps`, `loop`, `pose_description`, `near_arm`, `near_leg`, `planted_foot`, `pivot`, `transition`.

## Beat-em-up pose reference (starting points, not fixed counts)
- `idle`: 2-4 frames, breathing/guard, no unintended feet translation.
- `walk`: 4-8 frames, left-contact -> passing -> right-contact -> passing; alternating shoulders/arms. Resolve front/rear legs based on camera and facing.
- `run`: 4-8 frames, pronounced weight transfer, avoid identical walk frames with speed alone.
- `jab` / `hook`: 3-6 frames; windup -> contact -> follow through -> guard/recovery, far arm visible where anatomically relevant.
- `kick`: 4-7 frames; plant -> raise -> extension -> retract -> recover.
- `hurt`, `launched`, `down`, `getup`: distinct keys with clear transitions; never repurpose a grounded pose for midair without correction.

## Z Bom four-direction reference
- Create separate front/back/left/right key poses before animation. Validate differences in face visibility, upper torso perspective, and shoe overlap.
- `walk`: 4-6 frames per direction; front/back arm and leg overlap must not accidentally reverse; left/right gear placement follows contract.
- `interact`: differentiate facing object from generic idle where needed.
- Preserve shoulder width and head silhouette across directions without forcing identical outline (a rotated form legitimately changes projection).

## Animation review
- Flip through frames at intended fps and inspect onion-skin overlay and a contact sheet.
- Confirm continuity across loop seam (`last -> first`) and foot-plant timing.
- When the user says a direction is wrong (e.g. walk frames 3-4), inspect and redraw those specific frames; do not silently edit correct frames 1-2.
- Physical correctness, timing, and consistency are semantic visual checks and cannot be certified by Pillow-only automated QA.
