import sys, os
from PIL import Image, ImageOps, ImageDraw, ImageFont
src, out, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
def crop(p):
    im = Image.open(p).convert('L')
    # dark pixels only (ignore light watermark)
    bw = im.point(lambda v: 255 if v < 110 else 0)
    w, h = im.size
    box = bw.getbbox() or (0,0,w,h)
    l,t,r,b = box
    # drop footer url line: cut bottom 5%
    b = min(b, int(h*0.95))
    return im.crop((max(0,l-8), max(0,t-8), min(w,r+8), b))
font = ImageFont.load_default(size=28)
for i in range(0, n, 2):
    ims = [(j, crop(next(f"{src}/p-{j:03d}.{e}" for e in ('png', 'jpg') if os.path.exists(f"{src}/p-{j:03d}.{e}"))))
           for j in (i, i+1) if j < n]
    H = max(im.size[1] for _, im in ims) + 40
    W = sum(im.size[0] for _, im in ims) + 30*(len(ims)-1)
    canvas = Image.new('L', (W, H), 255)
    d = ImageDraw.Draw(canvas); x = 0
    for j, im in ims:
        d.text((x+10, 4), f"PDF {j+1}", fill=0, font=font)
        canvas.paste(im, (x, 40)); x += im.size[0] + 30
        if x < W: d.line([(x-15,0),(x-15,H)], fill=0, width=3)
    canvas.save(f"{out}/pair-{i+1:03d}.jpg", quality=85)
