"""Reading images for transcription: each page cropped to its text, contrast stretched, cut into an upper and a
lower half (with a small overlap) and enlarged 1.7x. Much easier to read than the two-page images of pairs.py.

Usage:
    pdfimages -png <volume.pdf> <imgdir>/p
    python3 -I tools/halves.py <imgdir> <outdir> <first pdf page> <last pdf page>
Writes <outdir>/NNNa.png and NNNb.png (NNN = PDF page).
"""
import sys, os
from PIL import Image, ImageOps
src, out, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(out, exist_ok=True)
for pdf in range(a, b + 1):
    f = f'{src}/p-{pdf-1:03d}.png'
    im = Image.open(f).convert('L')
    bw = im.point(lambda v: 255 if v < 140 else 0)
    w, h = im.size
    l, t, r, bt = bw.getbbox() or (0, 0, w, h)
    im = im.crop((max(0, l-6), max(0, t-6), min(w, r+6), min(h, bt+6)))
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.point(lambda v: 0 if v < 150 else min(255, int(v*1.1)))
    W, H = im.size
    for k, (y0, y1) in enumerate(((0, H//2 + 20), (H//2 - 20, H))):
        c = im.crop((0, y0, W, y1))
        c.resize((int(W*1.7), int((y1-y0)*1.7)), Image.LANCZOS).save(f'{out}/{pdf:03d}{"ab"[k]}.png')
