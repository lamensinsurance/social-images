#!/usr/bin/env python3
"""Lamens Insurance social graphic renderer.

Usage:  python3 render_post.py spec.json out.jpg [--logo logo.png]

spec.json fields:
  template : "tip" (daily education post) or "blog" (new blog promo)
  eyebrow  : short label, e.g. "HOME INSURANCE TIP" / "NEW ON THE BLOG"
  headline : main text, ideally <= 60 characters
  points   : (tip) 0-3 short lines, each <= 45 characters
  excerpt  : (blog) 1-2 sentence teaser, <= 140 characters
  footer_cta : optional, e.g. "Questions? (425) 419-0099"
Output: 1080x1350 JPEG (4:5, works for Instagram + Facebook feed).
"""
import json, sys, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY = (0, 35, 57)          # #002339
BLUE = (74, 153, 204)       # #4a99cc
WHITE = (255, 255, 255)
SOFT = (220, 233, 243)
MARGIN = 96
EMAIL = "cody@lamensinsurance.com"

FONT_DIRS = ["/usr/share/fonts/opentype/inter", "/usr/share/fonts/truetype/dejavu"]
def font(weight, size):
    names = {"bold": ["Inter-Bold.otf", "DejaVuSans-Bold.ttf"],
             "semi": ["Inter-SemiBold.otf", "DejaVuSans-Bold.ttf"],
             "reg":  ["Inter-Regular.otf", "DejaVuSans.ttf"],
             "med":  ["Inter-Medium.otf", "DejaVuSans.ttf"]}[weight]
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(draw, text, f, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def fit_headline(draw, text, max_w, max_h, start=104, minimum=56):
    size = start
    while size >= minimum:
        f = font("bold", size)
        lines = wrap(draw, text, f, max_w)
        lh = int(size * 1.12)
        if lh * len(lines) <= max_h:
            return f, lines, lh
        size -= 4
    f = font("bold", minimum)
    return f, wrap(draw, text, f, max_w), int(minimum * 1.12)

def paste_logo(img, logo_path, box_h, x, y_center):
    if not logo_path or not os.path.exists(logo_path):
        return False
    lg = Image.open(logo_path).convert("RGBA")
    r = box_h / lg.height
    lg = lg.resize((int(lg.width * r), box_h))
    img.paste(lg, (x, int(y_center - box_h / 2)), lg)
    return True

def footer(img, d, dark_bg, logo_path, cta):
    # bottom band
    band_top = H - 170
    d.rectangle([0, band_top, W, H], fill=NAVY if not dark_bg else (0, 26, 43))
    d.rectangle([0, band_top, W, band_top + 6], fill=BLUE)
    yc = band_top + 85
    if not paste_logo(img, logo_path, 112, MARGIN - 8, yc):
        d.text((MARGIN, yc - 30), "Lamens Insurance Agency", font=font("bold", 34), fill=WHITE)
        d.text((MARGIN, yc + 12), "Insurance in Lamens Terms", font=font("med", 24), fill=BLUE)
    cta = cta or "(425) 419-0099"
    f = font("semi", 28)
    d.text((W - MARGIN - d.textlength(cta, font=f), yc - 52), cta, font=f, fill=WHITE)
    ef = font("med", 25)
    em = EMAIL
    d.text((W - MARGIN - d.textlength(em, font=ef), yc - 12), em, font=ef, fill=WHITE)
    sf = font("med", 22)
    sv = "Serving WA, OR & ID"
    d.text((W - MARGIN - d.textlength(sv, font=sf), yc + 24), sv, font=sf, fill=BLUE)

def render_tip(spec, logo):
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)
    # subtle accent shapes
    d.ellipse([W - 360, -220, W + 220, 360], fill=(8, 52, 82))
    d.rectangle([MARGIN, 150, MARGIN + 90, 160], fill=BLUE)
    d.text((MARGIN, 186), spec.get("eyebrow", "INSURANCE TIP").upper(), font=font("semi", 34), fill=BLUE)
    f, lines, lh = fit_headline(d, spec["headline"], W - 2 * MARGIN, 470)
    y = 260
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=WHITE); y += lh
    y += 50
    pf = font("med", 38)
    for p in spec.get("points", [])[:3]:
        pl = wrap(d, p, pf, W - 2 * MARGIN - 70)
        d.ellipse([MARGIN, y + 14, MARGIN + 22, y + 36], fill=BLUE)
        for i, ln in enumerate(pl):
            d.text((MARGIN + 52, y), ln, font=pf, fill=SOFT); y += 50
        y += 26
    footer(img, d, True, logo, spec.get("footer_cta"))
    return img

def render_blog(spec, logo):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 22], fill=BLUE)
    d.ellipse([-260, H - 640, 300, H - 80], fill=(237, 245, 251))
    tag = spec.get("eyebrow", "NEW ON THE BLOG").upper()
    tf = font("semi", 30)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([MARGIN, 150, MARGIN + tw + 56, 210], radius=30, fill=NAVY)
    d.text((MARGIN + 28, 163), tag, font=tf, fill=WHITE)
    f, lines, lh = fit_headline(d, spec["headline"], W - 2 * MARGIN, 520, start=96)
    y = 270
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=NAVY); y += lh
    y += 40
    d.rectangle([MARGIN, y, MARGIN + 90, y + 8], fill=BLUE); y += 50
    ef = font("reg", 38)
    for ln in wrap(d, spec.get("excerpt", ""), ef, W - 2 * MARGIN)[:4]:
        d.text((MARGIN, y), ln, font=ef, fill=(45, 70, 90)); y += 52
    btn = "Read it at lamensinsurance.com/blog"
    bf = font("semi", 34)
    by = H - 170 - 150
    bw = d.textlength(btn, font=bf)
    d.rounded_rectangle([MARGIN, by, MARGIN + bw + 70, by + 84], radius=42, fill=BLUE)
    d.text((MARGIN + 35, by + 22), btn, font=bf, fill=WHITE)
    footer(img, d, False, logo, spec.get("footer_cta"))
    return img

PALE = (232, 242, 250)     # light blue-gray background

def render_light(spec, logo):
    """Style 'light': pale background, navy text, numbered white cards."""
    img = Image.new("RGB", (W, H), PALE)
    d = ImageDraw.Draw(img)
    d.ellipse([-300, -300, 340, 340], fill=(214, 232, 245))
    tag = spec.get("eyebrow", "INSURANCE TIP").upper()
    tf = font("semi", 30)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([MARGIN, 140, MARGIN + tw + 56, 200], radius=30, fill=NAVY)
    d.text((MARGIN + 28, 153), tag, font=tf, fill=WHITE)
    f, lines, lh = fit_headline(d, spec["headline"], W - 2 * MARGIN, 400, start=96)
    y = 250
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=NAVY); y += lh
    y += 50
    pf = font("semi", 36)
    nf = font("bold", 34)
    for n, p in enumerate(spec.get("points", [])[:3], 1):
        pl = wrap(d, p, pf, W - 2 * MARGIN - 150)
        ch = 50 * len(pl) + 56
        d.rounded_rectangle([MARGIN, y, W - MARGIN, y + ch], radius=24, fill=WHITE)
        cy = y + ch // 2
        d.ellipse([MARGIN + 30, cy - 30, MARGIN + 90, cy + 30], fill=BLUE)
        s = str(n)
        d.text((MARGIN + 60 - d.textlength(s, font=nf) / 2, cy - 22), s, font=nf, fill=WHITE)
        ty = y + 28
        for ln in pl:
            d.text((MARGIN + 120, ty), ln, font=pf, fill=NAVY); ty += 50
        y += ch + 22
    footer(img, d, False, logo, spec.get("footer_cta"))
    return img

def render_bold(spec, logo):
    """Style 'bold': brand-blue background, big white headline, navy panel of points."""
    img = Image.new("RGB", (W, H), BLUE)
    d = ImageDraw.Draw(img)
    d.ellipse([W - 230, -330, W + 330, 130], outline=(120, 182, 222), width=26)
    d.ellipse([W - 300, H - 560, W + 160, H - 100], outline=(120, 182, 222), width=20)
    d.text((MARGIN, 150), spec.get("eyebrow", "INSURANCE TIP").upper(), font=font("bold", 32), fill=NAVY)
    d.rectangle([MARGIN, 198, MARGIN + 90, 206], fill=WHITE)
    pts = spec.get("points", [])[:3]
    f, lines, lh = fit_headline(d, spec["headline"], W - 2 * MARGIN, 440 if pts else 640, start=108)
    y = 250
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=WHITE); y += lh
    if pts:
        y += 50
        pf = font("med", 36)
        wrapped = [wrap(d, p, pf, W - 2 * MARGIN - 130) for p in pts]
        ph = sum(46 * len(w) + 24 for w in wrapped) + 60
        d.rounded_rectangle([MARGIN, y, W - MARGIN, y + ph], radius=28, fill=NAVY)
        ty = y + 34
        for w in wrapped:
            d.text((MARGIN + 44, ty - 2), "✓", font=font("bold", 36), fill=BLUE)
            for ln in w:
                d.text((MARGIN + 96, ty), ln, font=pf, fill=WHITE); ty += 46
            ty += 24
    footer(img, d, False, logo, spec.get("footer_cta"))
    return img

STYLES = {"tip": render_tip, "navy": render_tip, "light": render_light, "bold": render_bold}

def main():
    args = sys.argv[1:]
    logo = None
    if "--logo" in args:
        i = args.index("--logo"); logo = args[i + 1]; del args[i:i + 2]
    spec = json.load(open(args[0]))
    out = args[1]
    if spec.get("template") == "blog":
        img = render_blog(spec, logo)
    else:
        img = STYLES[spec.get("style", "navy")](spec, logo)
    img.save(out, "JPEG", quality=90, optimize=True)
    print(out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    main()
