#!/usr/bin/env python3
"""
Werkzeug-Memory v2 – echte Fotos vom Internet
Downloads real tool photos, overlays German name, generates A4 PDF.

Install:  pip install Pillow reportlab requests ddgs
Run:      python memory_game_v2.py
Output:   memory_game_v2.pdf   (print A4, cut out, play)

Image priority (highest first):
  1. ./images/{key}.jpg/png/…   ← place your own photo here to override
  2. ./tool_images/{key}.jpg     ← auto-downloaded cache (never re-fetched)
  3. Wikipedia REST API
  4. Openverse (CC-licensed)
  5. DuckDuckGo image search

Card design: playing-card size (63×88 mm)
  - real photo fills top ~79 % of card
  - German name in navy banner at bottom
  - identical pairs → standard memory game while learning names
"""

import argparse
import io
import math
import os
import sys
import time

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ─── Tool catalogue  (key, German name, English DDG search fallback) ──────────

TOOLS = [
    # (key, Deutsch, DDG search query, Русский)
    ("bohrmaschine",        "Bohrmaschine",          "cordless power drill tool",      "Дрель"),
    ("bohrer",              "Bohrer",                "spiral drill bit HSS metal",     "Сверло"),
    ("hammer",              "Hammer",                "claw hammer tool",               "Молоток"),
    ("meissel",             "Meißel",                "cold chisel steel tool",         "Зубило"),
    ("kreuzschrauber",      "Kreuzschraubenzieher",  "phillips screwdriver tool",      "Крестовая отвёртка"),
    ("schlitzschrauber",    "Schlitzschraubenzieher","flathead screwdriver tool",      "Плоская отвёртка"),
    ("nuss",                "Nuss",                  "socket set wrench tool",         "Торцевая головка"),
    ("ratsche",             "Ratsche",               "ratchet wrench socket tool",     "Трещотка"),
    ("inbusschluessel",     "Inbusschlüssel",        "hex allen key set",              "Шестигранный ключ"),
    ("handsaege",           "Handsäge",              "hand saw carpentry tool",        "Ручная пила"),
    ("wasserwaage",         "Wasserwaage",           "spirit level tool",              "Уровень"),
    ("massband",            "Maßband",               "tape measure retractable",       "Рулетка"),
    ("kombizange",          "Kombizange",            "combination lineman pliers",     "Плоскогубцы"),
    ("seitenschneider",     "Seitenschneider",       "diagonal cutting pliers",        "Бокорезы"),
    ("gabelschluessel",     "Gabelschlüssel",        "open end wrench spanner",        "Рожковый ключ"),
    ("rollgabelschluessel", "Rollgabelschlüssel",    "adjustable wrench spanner",      "Разводной ключ"),
    ("winkelschleifer",     "Winkelschleifer",       "angle grinder power tool",       "Болгарка"),
    ("stichsaege",          "Stichsäge",             "jigsaw power tool",              "Лобзик"),
    ("schraubklemme",       "Schraubklemme",         "C clamp G clamp workshop",       "Струбцина"),
    ("malerrolle",          "Malerrolle",            "paint roller brush",             "Малярный валик"),
    ("pinsel",              "Pinsel",                "paintbrush artist brush",        "Кисть"),
    ("kelle",               "Kelle",                 "masonry brick trowel",           "Мастерок"),
    ("spachtel",            "Spachtel",              "putty knife spatula",            "Шпатель"),
    ("feile",               "Feile",                 "metal hand file tool",           "Напильник"),
    ("zollstock",           "Zollstock",             "folding zigzag ruler carpenter", "Складной метр"),
    ("kreissaege",          "Kreissäge",             "circular saw power tool",        "Циркулярная пила"),
]


# ─── Card pixel dimensions (63 × 88 mm @ 300 dpi) ─────────────────────────────

CARD_W   = 744   # px
CARD_H   = 1040  # px
PHOTO_H  = 780   # px  (top 75 % for photo)
BANNER_H = CARD_H - PHOTO_H   # 260 px — room for DE + RU name
RADIUS   = 24    # corner radius

BANNER_BG    = (20, 45, 100)       # dark navy
BANNER_TEXT  = (255, 255, 255)
BACK_BG      = (18, 40, 92)
SHADOW_COLOR = (0, 0, 0, 60)

IMG_DIR        = "images"        # auto-downloaded cache (committed to repo)
CUSTOM_IMG_DIR = "my_images"     # user-supplied overrides (gitignored)

HEADERS = {
    # Wikipedia policy requires a descriptive User-Agent for API access
    "User-Agent": "WerkzeugMemory/1.0 (educational memory card game; python-requests)"
}

# Wikipedia REST API article names for each tool
WIKI_ARTICLES = {
    "bohrmaschine":        "Drill",
    "bohrer":              "Drill bit",
    "hammer":              "Hammer",
    "meissel":             "Chisel",
    "kreuzschrauber":      "Screwdriver",
    "schlitzschrauber":    "Screwdriver",
    "nuss":                "Socket wrench",
    "ratsche":             "Ratchet wrench",
    "inbusschluessel":     "Hex key",
    "handsaege":           "Hand saw",
    "wasserwaage":         "Spirit level",
    "massband":            "Tape measure",
    "kombizange":          "Lineman's pliers",
    "seitenschneider":     "Diagonal pliers",
    "gabelschluessel":     "Spanner",
    "rollgabelschluessel": "Adjustable spanner",
    "winkelschleifer":     "Angle grinder",
    "stichsaege":          "Jigsaw",
    "schraubklemme":       "C clamp",
    "malerrolle":          "Paint roller",
    "pinsel":              "Paintbrush",
    "kelle":               "Trowel",
    "spachtel":            "Putty knife",
    "feile":               "File (tool)",
    "zollstock":           "Folding rule",
    "kreissaege":          "Circular saw",
}

# ─── Font helpers ─────────────────────────────────────────────────────────────

_FONT_PATHS = [
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/noto/NotoSans-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
]
_font_path = next((p for p in _FONT_PATHS if os.path.exists(p)), None)


def fnt(size):
    if _font_path:
        return ImageFont.truetype(_font_path, size)
    return ImageFont.load_default()


# ─── Image download & cache ───────────────────────────────────────────────────

CUSTOM_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif")


def load_custom(key):
    """Return a PIL image from ./images/{key}.* if present, else None."""
    for ext in CUSTOM_EXTS:
        for name_variant in (key, key.lower(), key.upper()):
            path = os.path.join(CUSTOM_IMG_DIR, name_variant + ext)
            if os.path.exists(path):
                try:
                    return Image.open(path).convert("RGB"), path
                except Exception:
                    pass
    return None, None


def cached_path(key):
    return os.path.join(IMG_DIR, f"{key}.jpg")


def load_cached(key):
    path = cached_path(key)
    if os.path.exists(path):
        try:
            return Image.open(path).convert("RGB")
        except Exception:
            os.remove(path)
    return None


def download_url(url, key):
    """Download image URL → PIL Image, save to cache."""
    r = requests.get(url, timeout=15, headers=HEADERS)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content)).convert("RGB")
    path = cached_path(key)
    img.save(path, "JPEG", quality=90)
    return img


def _to_wiki_thumb(url, width=800):
    """
    Convert a full-resolution Wikimedia Commons URL to a pre-rendered thumbnail URL.
    Wikimedia explicitly requires using these pre-computed sizes for API access.
    E.g. …/commons/a/ae/file.jpg → …/commons/thumb/a/ae/file.jpg/800px-file.jpg
    """
    import re
    m = re.match(
        r"(https://upload\.wikimedia\.org/wikipedia/[^/]+/)([a-f0-9]/[a-f0-9]{2})/(.+)$",
        url,
    )
    if m:
        base, hash_path, filename = m.group(1), m.group(2), m.group(3)
        return f"{base}thumb/{hash_path}/{filename}/{width}px-{filename}"
    return url   # already a thumbnail or unrecognised format


def wikipedia_thumbnail_url(article_title):
    """
    Use Wikipedia's official REST summary API to get the article thumbnail URL.
    Always returns a pre-rendered thumbnail URL (avoids full-res 429 blocking).
    """
    import urllib.parse
    slug = urllib.parse.quote(article_title.replace(" ", "_"))
    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{slug}"
    r = requests.get(api_url, timeout=12, headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    # Prefer originalimage converted to thumbnail, else use REST thumbnail directly
    original = data.get("originalimage", {}).get("source")
    if original:
        return _to_wiki_thumb(original, width=800)
    return data.get("thumbnail", {}).get("source")


def openverse_url(query):
    """Search Openverse (CC-licensed images) and return the first thumbnail URL."""
    try:
        r = requests.get(
            "https://api.openverse.org/v1/images/",
            params={"q": query, "license_type": "modification", "page_size": 6},
            headers=HEADERS, timeout=12,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        for item in results:
            thumb = item.get("thumbnail")
            if thumb and thumb.startswith("http"):
                return thumb
    except Exception:
        pass
    return None


def ddg_search_url(query):
    """Return first image URL from DuckDuckGo (tries both package names), or None."""
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS
        results = list(DDGS().images(query, max_results=6))
        for r in results:
            url = r.get("image", "")
            if url and url.startswith("http"):
                return url
    except Exception:
        pass
    return None


def get_photo(key, ddg_query, force_download=False):
    """
    Return (PIL Image, source_str).
    Priority: ./images/ override → cache → Wikipedia → Openverse → DuckDuckGo → None.
    Custom images in ./images/ always win, even over the cache.
    """
    # 0. User-supplied override (./images/{key}.*)
    custom_img, custom_path = load_custom(key)
    if custom_img is not None:
        return custom_img, f"custom ({os.path.basename(custom_path)})"

    if not force_download:
        cached = load_cached(key)
        if cached:
            return cached, "cache"

    # 1. Wikipedia official REST API
    article = WIKI_ARTICLES.get(key)
    if article:
        try:
            time.sleep(0.5)
            thumb_url = wikipedia_thumbnail_url(article)
            if thumb_url:
                img = download_url(thumb_url, key)
                return img, "wikipedia"
        except Exception as e:
            print(f"\n    Wikipedia failed, trying Openverse …", end=" ")

    # 2. Openverse (CC-licensed, designed for API use)
    try:
        time.sleep(0.5)
        ov_url = openverse_url(ddg_query)
        if ov_url:
            img = download_url(ov_url, key)
            return img, "openverse"
    except Exception:
        print(f"\n    Openverse failed, trying DuckDuckGo …", end=" ")

    # 3. DuckDuckGo image search
    time.sleep(0.5)
    ddg_url = ddg_search_url(ddg_query)
    if ddg_url:
        try:
            img = download_url(ddg_url, key)
            return img, "duckduckgo"
        except Exception as e:
            print(f"\n    DuckDuckGo failed ({e})", end=" ")

    return None, "failed"


# ─── Image processing ─────────────────────────────────────────────────────────

def center_crop(img, target_w, target_h):
    """Scale + center-crop image to exact pixel dimensions."""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = max(target_w, int(src_w * scale))
    new_h = max(target_h, int(src_h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)
    x = (new_w - target_w) // 2
    y = (new_h - target_h) // 2
    return img.crop((x, y, x + target_w, y + target_h))


def add_bottom_gradient(img, height=120):
    """Add a dark-to-transparent gradient at the bottom of the photo."""
    grad = Image.new("RGBA", (img.width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(grad)
    for y in range(height):
        alpha = int(180 * (y / height) ** 1.5)
        draw.line([(0, y), (img.width, y)], fill=(0, 0, 0, alpha))
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay.paste(grad, (0, img.height - height))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")


def rounded_rectangle_mask(size, radius):
    """Return an L-mode mask with rounded corners."""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def build_card(photo, de_name, ru_name=None):
    """
    Compose one card: photo (top) + name banner (bottom) with rounded corners.
    `photo` is a PIL RGB image or None (draws a placeholder).
    Banner shows German name (large, white) and optional Russian name (smaller, steel-blue).
    """
    card = Image.new("RGB", (CARD_W, CARD_H), "white")

    # ── Photo area ──────────────────────────────────────────────────────────
    if photo is not None:
        tile = center_crop(photo, CARD_W, PHOTO_H)
        tile = add_bottom_gradient(tile, height=int(PHOTO_H * 0.22))
    else:
        tile = Image.new("RGB", (CARD_W, PHOTO_H), (230, 235, 245))
        d = ImageDraw.Draw(tile)
        d.text((CARD_W // 2 - 60, PHOTO_H // 2 - 20), "?", fill=(150, 160, 180), font=fnt(120))

    card.paste(tile, (0, 0))

    # ── Name banner ─────────────────────────────────────────────────────────
    banner = Image.new("RGB", (CARD_W, BANNER_H), BANNER_BG)
    bd = ImageDraw.Draw(banner)

    def wrap(text, f):
        words = text.split()
        lines, cur = [], ""
        for word in words:
            test = (cur + " " + word).strip()
            bb = bd.textbbox((0, 0), test, font=f)
            if bb[2] - bb[0] <= CARD_W - 40 or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    # German name — primary, white
    n = len(de_name)
    de_fs = 76 if n <= 8 else 64 if n <= 12 else 52 if n <= 16 else 44 if n <= 20 else 36
    de_f  = fnt(de_fs)
    de_lines = wrap(de_name, de_f)
    de_lh = de_fs + 6

    # Russian name — secondary, steel-blue, ~65 % the size of German
    ru_lines, ru_lh = [], 0
    if ru_name:
        ru_fs = max(32, int(de_fs * 0.65))
        ru_f  = fnt(ru_fs)
        ru_lines = wrap(ru_name, ru_f)
        ru_lh = ru_fs + 4

    gap = 14 if ru_lines else 0
    total_h = len(de_lines) * de_lh + gap + len(ru_lines) * ru_lh
    y = (BANNER_H - total_h) // 2

    for line in de_lines:
        bb = bd.textbbox((0, 0), line, font=de_f)
        bd.text(((CARD_W - bb[2] + bb[0]) // 2, y), line, fill=(255, 255, 255), font=de_f)
        y += de_lh

    if ru_lines:
        y += gap
        for line in ru_lines:
            bb = bd.textbbox((0, 0), line, font=ru_f)
            bd.text(((CARD_W - bb[2] + bb[0]) // 2, y), line, fill=(170, 200, 240), font=ru_f)
            y += ru_lh

    card.paste(banner, (0, PHOTO_H))

    # ── Divider line ────────────────────────────────────────────────────────
    cd = ImageDraw.Draw(card)
    cd.line([(0, PHOTO_H), (CARD_W, PHOTO_H)], fill=(100, 130, 180), width=3)

    # ── Rounded corner mask ─────────────────────────────────────────────────
    mask = rounded_rectangle_mask((CARD_W, CARD_H), RADIUS)
    bg = Image.new("RGB", (CARD_W, CARD_H), "white")
    bg.paste(card, mask=mask)

    # ── Thin border ─────────────────────────────────────────────────────────
    bd2 = ImageDraw.Draw(bg)
    bd2.rounded_rectangle([(2, 2), (CARD_W - 3, CARD_H - 3)],
                          radius=RADIUS, outline=(80, 100, 150), width=4)
    return bg


def build_back():
    """Card back design."""
    card = Image.new("RGB", (CARD_W, CARD_H), BACK_BG)
    d = ImageDraw.Draw(card)

    # Diagonal stripe pattern
    stripe_gap = 60
    for i in range(-(CARD_H + CARD_W) // stripe_gap, (CARD_H + CARD_W) // stripe_gap + 1):
        x0 = i * stripe_gap
        d.line([(x0, 0), (x0 + CARD_H, CARD_H)], fill=(25, 55, 115), width=24)

    # Centre label
    cx, cy = CARD_W // 2, CARD_H // 2
    pad = 60
    d.rounded_rectangle([(pad, cy - 140), (CARD_W - pad, cy + 140)],
                         radius=20, fill=(15, 35, 85), outline=(80, 120, 200), width=4)
    f1, f2 = fnt(80), fnt(44)
    for txt, f, yoff in [("Werkzeug", f1, -60), ("Memory", f2, 50)]:
        bb = d.textbbox((0, 0), txt, font=f)
        x = cx - (bb[2] - bb[0]) // 2
        d.text((x, cy + yoff - (bb[3] - bb[1]) // 2), txt, fill="white", font=f)

    # Rounded border
    mask = rounded_rectangle_mask((CARD_W, CARD_H), RADIUS)
    bg = Image.new("RGB", (CARD_W, CARD_H), "white")
    bg.paste(card, mask=mask)
    bd = ImageDraw.Draw(bg)
    bd.rounded_rectangle([(2, 2), (CARD_W - 3, CARD_H - 3)],
                         radius=RADIUS, outline=(80, 120, 200), width=4)
    return bg


# ─── PDF layout constants ─────────────────────────────────────────────────────

PAGE_W, PAGE_H = A4
CARD_PDF_W = 63 * mm
CARD_PDF_H = 88 * mm
MARGIN = 9 * mm
COLS = 3
ROWS = 3
PER_PAGE = COLS * ROWS   # 9
START_X = (PAGE_W - COLS * CARD_PDF_W) / 2
START_Y = (PAGE_H - ROWS * CARD_PDF_H) / 2
TICK = 4


def pil_reader(img):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=88)
    buf.seek(0)
    return ImageReader(buf)


def draw_cut_marks(c, x, y):
    c.setStrokeColorRGB(.65, .65, .65)
    c.setLineWidth(.5)
    for cx_, cy_ in [(x, y), (x + CARD_PDF_W, y),
                     (x, y + CARD_PDF_H), (x + CARD_PDF_W, y + CARD_PDF_H)]:
        c.line(cx_ - TICK, cy_, cx_ + TICK, cy_)
        c.line(cx_, cy_ - TICK, cx_, cy_ + TICK)


def render_page(c, card_images, label, page_num, total_pages):
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(START_X, PAGE_H - MARGIN * .55,
                 f"Werkzeug-Memory — {label}  •  Seite {page_num}/{total_pages}")
    c.drawRightString(PAGE_W - START_X, PAGE_H - MARGIN * .55,
                      "Ausschneiden entlang der Markierungen")

    for idx, img in enumerate(card_images):
        row, col = divmod(idx, COLS)
        x = START_X + col * CARD_PDF_W
        y = PAGE_H - START_Y - (row + 1) * CARD_PDF_H
        c.drawImage(pil_reader(img), x + 1, y + 1,
                    CARD_PDF_W - 2, CARD_PDF_H - 2)
        draw_cut_marks(c, x, y)
    c.showPage()


# ─── Main build ───────────────────────────────────────────────────────────────

def build_pdf(output, tools, force_download=False):
    os.makedirs(IMG_DIR, exist_ok=True)

    print(f"Lade Bilder herunter (Cache: ./{IMG_DIR}/) …\n")
    photos = {}
    for i, (key, name, ddg_query, *_) in enumerate(tools, 1):
        print(f"  [{i:2d}/{len(tools)}] {name:<26}", end=" ", flush=True)
        img, src = get_photo(key, ddg_query, force_download)
        photos[key] = img
        print(f"✓ {src}" if img else "✗ Zeichnung als Ersatz")

    print(f"\nErstelle Karten …")
    card_images = []
    for key, name, _, ru_name in tools:
        card = build_card(photos[key], name, ru_name)
        card_images.append(card)
        card_images.append(card)   # identical pair

    back_img = build_back()

    # Split into pages
    pages = [card_images[i:i + PER_PAGE] for i in range(0, len(card_images), PER_PAGE)]
    n_front = len(pages)
    total   = n_front + 1

    print(f"Schreibe PDF  ({len(card_images)} Karten, {total} Seiten) …")
    c = canvas.Canvas(output, pagesize=A4)

    for i, page in enumerate(pages):
        render_page(c, page, "Karten", i + 1, total)

    # Back page (full grid)
    backs = [back_img] * PER_PAGE
    render_page(c, backs, "Rückseite", total, total)
    c.save()

    print(f"\n✓  {output}")
    print(f"   {len(tools)} Werkzeuge × 2 Karten = {len(card_images)} Karten")
    print(f"   {n_front} Vorderseiten + 1 Rückseite = {total} Seiten")
    print()
    print("  Druckhinweis:")
    print(f"    1) Seiten 1–{n_front} einseitig drucken (Karten-Vorderseiten)")
    print(f"    2) Seite {total} auf die Rückseite jedes Blattes drucken")
    print("    3) Karten ausschneiden, mischen und spielen!")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Werkzeug-Memory v2 – echte Fotos vom Internet"
    )
    ap.add_argument("--output", default="memory_game_v2.pdf")
    ap.add_argument("--force-download", action="store_true",
                    help="Vorhandene Cache-Bilder ignorieren und neu herunterladen")
    ap.add_argument("--list-tools", action="store_true",
                    help="Alle Werkzeuge auflisten und beenden")
    args = ap.parse_args()

    if args.list_tools:
        print(f"{'Schlüssel':<24}  {'Deutsch':<26}  {'Русский':<22}  Status")
        print("-" * 90)
        for k, name, _, ru_name in TOOLS:
            custom_img, custom_path = load_custom(k)
            if custom_img:
                status = f"custom  ({os.path.basename(custom_path)})"
            elif os.path.exists(cached_path(k)):
                status = "cached  (images/)"
            else:
                status = "wird heruntergeladen"
            print(f"  {k:<22}  {name:<26}  {ru_name:<22}  {status}")
        return

    build_pdf(args.output, TOOLS, args.force_download)


if __name__ == "__main__":
    main()
