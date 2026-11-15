#!/usr/bin/env python3
"""Deterministic sprite slicing, raster QA, and uniform-grid atlas export."""
import argparse
import json
import math
import re
import sys
import zipfile
from pathlib import Path
from PIL import Image


def pngs(folder):
    paths = list(Path(folder).glob('*.png'))
    return sorted(paths, key=lambda p: [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', p.name)])


def image_rgba(path):
    with Image.open(path) as im:
        return im.convert('RGBA')


def run_slice(args):
    src = image_rgba(args.sheet)
    if src.width % args.cols or src.height % args.rows:
        raise ValueError('Sheet dimensions must be exactly divisible by grid dimensions')
    n = args.count or args.cols * args.rows
    if n > args.cols * args.rows:
        raise ValueError('Count exceeds number of cells')
    w, h = src.width // args.cols, src.height // args.rows
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for i in range(n):
        x, y = (i % args.cols) * w, (i // args.cols) * h
        im = src.crop((x, y, x + w, y + h))
        if args.trim == 'yes':
            bbox = im.getchannel('A').getbbox()
            if bbox:
                im = im.crop(bbox)
        im.save(out / f'{args.prefix}_{i:03d}.png')
    print(json.dumps({'frames': n, 'cell': [w, h], 'output': str(out)}))


def rgb_tuple(v):
    h = v.lstrip('#')
    if len(h) != 6:
        raise ValueError(f'Invalid 6-digit hex palette color {v}')
    return tuple(bytes.fromhex(h))


def inspect_frame(path, cfg):
    issues = []
    with Image.open(path) as original:
        had_alpha = ('A' in original.getbands()) or ('transparency' in original.info)
        im = original.convert('RGBA')
    if cfg.get('require_alpha', True) and not had_alpha:
        issues.append('missing_alpha_channel')
    if cfg.get('canvas') and list(im.size) != list(cfg['canvas']):
        issues.append('canvas_mismatch')
    alpha = im.getchannel('A')
    bbox = alpha.getbbox()
    if bbox is None:
        issues.append('empty_frame')
    pix = list(im.get_flattened_data() if hasattr(im, 'get_flattened_data') else im.getdata())
    partial = sum(1 for p in pix if 0 < p[3] < 255)
    if partial and cfg.get('alpha_mode', 'binary') == 'binary':
        issues.append('partial_alpha_pixels')
    edge = []
    if im.width and im.height:
        edge += [im.getpixel((x, 0))[3] for x in range(im.width)]
        edge += [im.getpixel((x, im.height-1))[3] for x in range(im.width)]
        edge += [im.getpixel((0, y))[3] for y in range(im.height)]
        edge += [im.getpixel((im.width-1, y))[3] for y in range(im.height)]
    if any(a for a in edge) and cfg.get('require_transparent_border', True):
        issues.append('occupied_border')
    if cfg.get('baseline_y') is not None and bbox:
        baseline = int(cfg['baseline_y'])
        if not (0 <= baseline < im.height):
            issues.append('invalid_baseline')
        elif not any(im.getpixel((x, baseline))[3] for x in range(im.width)):
            issues.append('no_opaque_pixel_on_baseline')
    off_palette = 0
    if cfg.get('palette'):
        allowed = [rgb_tuple(c) for c in cfg['palette']]
        tol = int(cfg.get('palette_tolerance', 0))
        for r,g,b,a in pix:
            if a and not any(max(abs(r-r0), abs(g-g0), abs(b-b0)) <= tol for r0,g0,b0 in allowed):
                off_palette += 1
        if off_palette:
            issues.append('palette_outliers')
    return {'file': path.name, 'size': list(im.size), 'alpha_channel': had_alpha,
            'occupied_bbox': list(bbox) if bbox else None, 'partial_alpha_pixels': partial,
            'palette_outlier_pixels': off_palette, 'issues': issues, 'pass': not issues}


def run_qa(args):
    cfg = json.loads(Path(args.config).read_text()) if args.config else {}
    frames = pngs(args.input)
    if not frames:
        raise ValueError('No PNG frames found in input directory')
    rows = [inspect_frame(p, cfg) for p in frames]
    sizes = {tuple(row['size']) for row in rows}
    overall = []
    if len(sizes) > 1:
        overall.append('inconsistent_canvas_sizes')
    if cfg.get('frame_count') is not None and len(rows) != int(cfg['frame_count']):
        overall.append('frame_count_mismatch')
    result = {'pass': not overall and all(r['pass'] for r in rows), 'frame_count': len(rows),
              'global_issues': overall, 'frames': rows,
              'notes': 'Raster QA only. Artistic consistency, frame timing, facing and anatomy require visual review.'}
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(result, indent=2))
    print(json.dumps({'pass': result['pass'], 'frame_count': len(rows), 'global_issues': overall,
                      'frame_issues': {r['file']: r['issues'] for r in rows if r['issues']}}, indent=2))
    if not result['pass']:
        sys.exit(2)


def run_pack(args):
    files = pngs(args.input)
    if not files:
        raise ValueError('No PNG frames found')
    frames = [image_rgba(p) for p in files]
    sizes = {im.size for im in frames}
    if len(sizes) != 1:
        raise ValueError('Frame canvas dimensions are inconsistent; fix before packing')
    w,h = frames[0].size
    cols = args.columns
    rows = math.ceil(len(frames) / cols)
    out = Path(args.out)
    if out.resolve() == Path(args.input).resolve():
        raise ValueError('Output directory must differ from input directory')
    out.mkdir(parents=True, exist_ok=True)
    frame_dir = out / 'frames'; frame_dir.mkdir(exist_ok=True)
    atlas = Image.new('RGBA', (w * cols, h * rows), (0,0,0,0))
    index = {}
    for i,(p,im) in enumerate(zip(files,frames)):
        name = f'frame_{i:03d}'
        im.save(frame_dir / (name + '.png'))
        x, y = i % cols * w, i // cols * h
        atlas.paste(im, (x, y))
        index[name] = {'frame': {'x': x, 'y': y, 'w': w, 'h': h}, 'source': p.name, 'pivot': [0.5, 1.0]}
    atlas.save(out / 'atlas.png')
    checks = [inspect_frame(p, {}) for p in files]
    qa = {'pass': len(sizes) == 1 and all(c['pass'] for c in checks), 'frames': checks,
          'notes': 'Basic raster QA only; verify artistic consistency and animation manually.'}
    (out / 'qa.json').write_text(json.dumps(qa, indent=2))
    contact_scale = max(1, min(6, 384 // max(w,h)))
    preview = atlas.resize((atlas.width * contact_scale, atlas.height * contact_scale), Image.Resampling.NEAREST)
    preview.save(out / 'contact_sheet.png')
    meta = {'format': 'game-sprite-master/v1', 'image': 'atlas.png',
            'size': [atlas.width, atlas.height], 'frame_size': [w,h],
            'origin': 'top-left coordinates; pivot is normalized at bottom-center by default',
            'character': args.character, 'frames': index,
            'animations': {f'{args.action}_{args.direction}': {'frames': list(index.keys()),
                     'fps': args.fps, 'loop': not args.once, 'direction': args.direction,
                     'action': args.action}}}
    (out / 'atlas.json').write_text(json.dumps(meta, indent=2))
    (out / 'README.txt').write_text('Game Sprite Master export\n'
        f'Character: {args.character}\nAnimation: {args.action}_{args.direction}\n'
        f'Canvas: {w}x{h}; frames: {len(frames)}; fps: {args.fps}\n'
        'PNG frames maintain original canvas; atlas is row-major.\n'
        'JSON is a generic schema, not directly a Phaser/Godot/Unity native import file.\n'
        f'Basic QA passed: {qa["pass"]}. Inspect qa.json for failures.\n'
        'Review artistic consistency and animation manually before declaring game-ready.\n')
    archive = None
    if args.zip:
        archive = out / 'sprite_pack.zip'
        with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in out.rglob('*'):
                if p.is_file() and p != archive:
                    z.write(p, p.relative_to(out))
    print(json.dumps({'output': str(out), 'frame_count': len(files), 'atlas': [atlas.width,atlas.height],
                      'zip': str(archive) if archive else None}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    s = sub.add_parser('slice', help='Slice a uniform rectangular sprite sheet')
    s.add_argument('--sheet', required=True); s.add_argument('--cols', type=int, required=True)
    s.add_argument('--rows', type=int, required=True); s.add_argument('--count', type=int)
    s.add_argument('--out', required=True); s.add_argument('--prefix', default='frame')
    s.add_argument('--trim', choices=['yes','no'], default='no')
    s.set_defaults(func=run_slice)
    q = sub.add_parser('qa', help='Perform deterministic raster checks on PNG frames')
    q.add_argument('--input', required=True); q.add_argument('--config'); q.add_argument('--report')
    q.set_defaults(func=run_qa)
    p = sub.add_parser('pack', help='Build a uniform-frame sprite atlas and JSON')
    p.add_argument('--input', required=True); p.add_argument('--out', required=True)
    p.add_argument('--character', required=True); p.add_argument('--action', required=True)
    p.add_argument('--direction', required=True); p.add_argument('--fps', type=float, default=8)
    p.add_argument('--columns', type=int, default=4); p.add_argument('--once', action='store_true')
    p.add_argument('--zip', action='store_true'); p.set_defaults(func=run_pack)
    args = parser.parse_args()
    if hasattr(args, 'cols') and (args.cols <= 0 or args.rows <= 0 or (args.count is not None and args.count <= 0)):
        parser.error('Grid sizes and count must be positive')
    if hasattr(args, 'columns') and (args.columns <= 0 or args.fps <= 0):
        parser.error('Columns and fps must be positive')
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(1, f'Error: {exc}\n')

if __name__ == '__main__':
    main()
