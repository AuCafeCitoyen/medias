"""Rend des slides story Au Café Citoyen (2160x3840) sur le template du projet.
Usage : python3 render_story.py template.png spec.json dossier_sortie
spec.json : [{"file": "post1-1", "label": "...", "head": "...", "hsize": 170,
  "sub": "...", "body": "para1\npara2", "cols": [...], "after": "...", "src": "..."}]
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

TEMPLATE, SPEC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FMT = sys.argv[4] if len(sys.argv) > 4 else "9x16"
OSWALD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Oswald.ttf")  # github.com/google/fonts ofl/oswald
INTER = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
INTER_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
BLACK, ORANGE, GREY = (21, 21, 21), (255, 74, 35), (90, 90, 90)
# 9x16 (2160x3840) : stories IG/TikTok + carrousel photo TikTok. Marge droite 360 px (icônes),
#   rien sous y=2880 (légende TikTok, barre de réponse).
# 4x5 (2160x2700) : feed Instagram. Pas d'icônes ; la grille du profil recadre en 3:4 (≈70 px par côté).
FORMATS = {
    "9x16": dict(X0=190, X1=1800, Y0=780, Y_MAX=2880, K=1.0, NCOL=2),
    "4x5": dict(X0=170, X1=1990, Y0=470, Y_MAX=2330, K=1.0, NCOL=3),
}
F = FORMATS[FMT]
X0, X1, Y_MAX, K = F["X0"], F["X1"], F["Y_MAX"], F["K"]
W = X1 - X0


def oswald(size, weight=700):
    f = ImageFont.truetype(OSWALD, size)
    f.set_variation_by_axes([weight])
    return f


def wrap(d, text, font):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= W:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def block(d, y, text, font, fill, lh):
    for line in wrap(d, text, font):
        d.text((X0, y), line, font=font, fill=fill); y += lh
    return y


for s in json.load(open(SPEC)):
    img = Image.open(TEMPLATE).convert("RGB")
    d = ImageDraw.Draw(img)
    y = F["Y0"]
    r = int(44*K); d.ellipse((X0, y + int(22*K), X0 + r, y + int(22*K) + r), fill=ORANGE)
    d.text((X0 + int(75*K), y), s["label"], font=oswald(int(70*K), 600), fill=ORANGE)
    y += int(160*K)
    hs = int(s.get("hsize", 170) * K)
    y = block(d, y, s["head"], oswald(hs), BLACK, int(hs * 1.12))
    if s.get("sub"):
        y = block(d, y + int(60*K), s["sub"], oswald(hs), ORANGE, int(hs * 1.12))
    if s.get("body"):
        y += int(60*K)
        d.line((X0, y, X0 + 180, y), fill=ORANGE, width=10)
        y += int(60*K)
        bf = ImageFont.truetype(INTER, int(76*K))
        for para in s["body"].split("\n"):
            y = block(d, y, para, bf, BLACK, int(108*K)) + int(36*K)
    if s.get("cols"):
        y += 10
        cf = ImageFont.truetype(INTER, int(50*K)); lh = int(68*K); n = F["NCOL"]
        items = s["cols"]; half = -(-len(items) // n)
        for k, it in enumerate(items):
            cx, cy = X0 + (k // half) * (W // n), y + (k % half) * lh
            b = int(16*K); d.ellipse((cx, cy + int(22*K), cx + b, cy + int(22*K) + b), fill=ORANGE)
            d.text((cx + int(38*K), cy), it, font=cf, fill=BLACK)
        y += half * lh
    if s.get("after"):
        y = block(d, y + int(50*K), s["after"], oswald(int(96*K)), ORANGE, int(110*K))
    if s.get("src"):
        sf = ImageFont.truetype(INTER_SB, int(48*K))
        y += int(50*K)
        for line in wrap(d, s["src"], sf):
            d.text((X0, y), line, font=sf, fill=GREY); y += int(62*K)
    if y > Y_MAX:
        print(f"ATTENTION {s['file']} : le texte dépasse la zone sûre ({y} > {Y_MAX}), raccourcir")
    img.save(f"{OUT}/{s['file']}-{FMT}.png", optimize=True)
    print("ok", s["file"], y)

# Export 1080 px en JPEG (TikTok refuse le PNG pour les carrousels photo)
for s in json.load(open(SPEC)):
    p = f"{OUT}/{s['file']}-{FMT}.png"
    im = Image.open(p).convert("RGB")
    im.resize((im.width // 2, im.height // 2), Image.LANCZOS).save(p[:-4] + ".jpg", quality=92, optimize=True)
    os.remove(p)
