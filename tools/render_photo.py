#!/usr/bin/env python3
"""Photo Coverage Check post: a text-free photo (generated in HeyGen) on top, with the
Lamens navy band underneath: eyebrow label, 1-2 line headline, the real logo file and
the contact footer. Output is 1080x1350, the same size as the graphic posts.

Usage (from repo root):
  python3 tools/render_photo.py spec.json out.jpg [--logo tools/logo-white.png]

spec keys:
  template  "photo"
  photo     path to the source photo in the repo, e.g. photos/2026-11-18-home-business.png
  eyebrow   e.g. "Small Business Coverage Check"
  headline  full headline (used for the calendar title)
  lines     optional [line1, line2] to control the line break; defaults to headline
"""
import json, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
NAVY, BLUE, WHITE = (0, 35, 57), (74, 153, 204), (255, 255, 255)
M = 64
PHOTO_H = 1040
FD = "/usr/share/fonts/opentype/inter/"

def f(name, size):
    try:
        return ImageFont.truetype(FD + name, size)
    except OSError:
        fallback = "DejaVuSans-Bold.ttf" if "Bold" in name or "Semi" in name else "DejaVuSans.ttf"
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/" + fallback, size)

def render(spec, out, logo_path):
    img = Image.new("RGB", (W, H), NAVY)
    photo = Image.open(spec["photo"]).convert("RGB")
    s = max(W / photo.width, PHOTO_H / photo.height)
    photo = photo.resize((round(photo.width * s), round(photo.height * s)), Image.LANCZOS)
    left, top = (photo.width - W) // 2, (photo.height - PHOTO_H) // 2
    img.paste(photo.crop((left, top, left + W, top + PHOTO_H)), (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, PHOTO_H, W, PHOTO_H + 8], fill=BLUE)
    band_top = PHOTO_H + 8

    logo = Image.open(logo_path).convert("RGBA")
    lh = 120
    logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
    lx = W - M - logo.width
    band_mid = band_top + (H - band_top) // 2
    img.paste(logo, (lx, band_mid - lh // 2 - 18), logo)

    d.text((M, band_top + 30), spec["eyebrow"].upper(), font=f("Inter-SemiBold.otf", 26), fill=BLUE)
    lines = spec.get("lines") or [spec["headline"]]
    max_w = lx - M - 40
    size = 58
    while size > 34:
        hf = f("Inter-Bold.otf", size)
        if max(d.textlength(l.upper(), font=hf) for l in lines) <= max_w:
            break
        size -= 2
    y = band_top + 74
    for l in lines:
        d.text((M, y), l.upper(), font=hf, fill=WHITE)
        y += size + 12

    contact = "Questions? (425) 419-0099  ·  cody@lamensinsurance.com  ·  Serving WA, OR & ID"
    cs = 28
    cf = f("Inter-Medium.otf", cs)
    while d.textlength(contact, font=cf) > W - 2 * M:
        cs -= 1
        cf = f("Inter-Medium.otf", cs)
    d.text((M, H - 44 - cs), contact, font=cf, fill=BLUE)
    img.save(out, quality=92)

def main():
    args = sys.argv[1:]
    logo = "tools/logo-white.png"
    if "--logo" in args:
        i = args.index("--logo"); logo = args[i + 1]; del args[i:i + 2]
    render(json.load(open(args[0])), args[1], logo)

if __name__ == "__main__":
    main()
