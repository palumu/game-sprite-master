# Character contract and visual QA

## Contract template
```yaml
character_id: example
profile: beat-em-up-16bit
version: v0.1
reference_images: [reference.png]
native_frame_px: [96, 112] # example only; validate against approved artwork
visible_height_px: null
facing: right
pivot_px: [48, 104]
floor_baseline_y: 104
outline_px: 1
palette: ['#26335D', '#FFFFFF', '#171717']
locked_details:
  - hair outline and direction
  - shirt color, pattern, sleeve length
  - shoes, accessories, left/right placement
avoid:
  - antialiasing and blurry resampling
  - different eye/head ratio per frame
  - floating feet and sliding anchor
```

## Frame-by-frame review
1. Compare silhouette over canonical pose; allow justified changes for crouching, action stretch, or damage.
2. Check distinguishing hair/accessories and garment seams, including hidden/visible sides and which arm is foreground.
3. Compare same material colors; assess palette drift from existing reference, not merely internally.
4. Compare pixel block scale, line thickness, anti-aliasing, unwanted JPEG edge artifacts.
5. Register frame origin to ground/feet or hip pivot. Confirm player does not bounce unintentionally when animation loops.
6. Verify transparency by sampling corner and testing PNG alpha; a visible checkerboard rendered into pixels is not transparency.
7. Preserve approved identity between versions; change only explicitly requested features.

## Generation prompt scaffold
"Use the supplied approved [character/version] as strict identity/style reference, NOT as inspiration. Native [W]x[H] hard-edge pixel art, [camera], [direction], [action], frame [i/N]. Retain [locked clothing/colors/accessories], [head scale], [outline/pixel density]. Draw [near arm/leg action], [far limb visibility], [contact foot], [face rotation]; keep baseline [y] and consistent anchor [x,y]. Genuine transparent background, no labels, no soft shadow, no gradients/antialiasing, no cropped limbs."

A prompt alone cannot guarantee consistency; visually assess each result and perform surgical revisions. Do not claim a generated image is exact pixel art when edges prove otherwise.
