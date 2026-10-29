"""Cut a sharp, enlarged band out of a scanned page, for reading Arabic and Persian lines.

Usage:
    python3 -I tools/zoom.py <volume.pdf> <pdf page> <top> <bottom> <out.png> [scale]

top/bottom are fractions of the page height (0..1). The page image is taken at the PDF's full
resolution (pdfimages -png), not the reduced page images used for ordinary reading, and enlarged
`scale` times (default 3) so that dots and harakat can be told apart.
"""
import sys, os, subprocess, tempfile
from PIL import Image

pdf, page, top, bottom, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
scale = float(sys.argv[6]) if len(sys.argv) > 6 else 3
with tempfile.TemporaryDirectory() as d:
    subprocess.run(['pdfimages', '-png', '-f', str(page), '-l', str(page), pdf, os.path.join(d, 'p')], check=True)
    im = Image.open(os.path.join(d, sorted(os.listdir(d))[0]))
    w, h = im.size
    band = im.crop((0, int(h * top), w, int(h * bottom)))
    band.resize((int(w * scale), int(band.size[1] * scale)), Image.LANCZOS).save(out)
