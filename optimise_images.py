"""Create smaller copies of the site's photos and record their sizes.

Run after adding or replacing a photo in dist/assets (needs Pillow: pip install pillow):

    python3 optimise_images.py

It writes name-480.webp and name-800.webp beside each large WebP photo and
dist/assets/image-manifest.json, which build.py reads to emit width, height and
srcset attributes. build.py itself stays dependency-free.
"""
import json
from pathlib import Path
from PIL import Image

ASSETS = Path(__file__).parent / 'dist' / 'assets'
WIDTHS = (480, 800)
MAX_WIDTH = 1400
SKIP = {'motion-poster'}

manifest = {}
for path in sorted(ASSETS.glob('*.webp')):
    name = path.stem
    if name.rsplit('-', 1)[-1].isdigit() and (ASSETS / (name.rsplit('-', 1)[0] + '.webp')).exists():
        continue  # a generated variant
    with Image.open(path) as im:
        im.load()
        if im.width > MAX_WIDTH and name not in SKIP:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
            im.save(path, 'WEBP', quality=80, method=6)
        width, height = im.size
        variants = []
        if name not in SKIP:
            for w in WIDTHS:
                if width >= w * 1.25:
                    small = im.resize((w, round(height * w / width)), Image.LANCZOS)
                    small.save(ASSETS / f'{name}-{w}.webp', 'WEBP', quality=76, method=6)
                    variants.append(w)
        manifest[name] = {'width': width, 'height': height, 'variants': variants}

(ASSETS / 'image-manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
print(f'{len(manifest)} photos recorded; {sum(len(v["variants"]) for v in manifest.values())} smaller copies written.')
