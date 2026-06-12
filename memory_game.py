#!/usr/bin/env python3
"""
German Tool Memory Game Generator
Generates a printable A4 PDF with paired image/name cards.

Install:  pip install Pillow reportlab
Run:      python memory_game.py
          python memory_game.py --image-dir ./my_photos/   # use your own images
Output:   memory_game.pdf  (print on A4, cut cards apart)

Card layout:
  - Pages 1–N : image cards  (tool drawing)
  - Pages N+1–: text cards   (German name, blue background)
  - Last page : card backs   (print double-sided or glue)
"""

import argparse
import io
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ─── Tool catalogue ────────────────────────────────────────────────────────────

TOOLS = [
    ("bohrmaschine",        "Bohrmaschine"),
    ("bohrer",              "Bohrer"),
    ("hammer",              "Hammer"),
    ("meissel",             "Meißel"),
    ("kreuzschrauber",      "Kreuzschraubenzieher"),
    ("schlitzschrauber",    "Schlitzschraubenzieher"),
    ("nuss",                "Nuss"),
    ("ratsche",             "Ratsche"),
    ("inbusschluessel",     "Inbusschlüssel"),
    ("handsaege",           "Handsäge"),
    ("wasserwaage",         "Wasserwaage"),
    ("massband",            "Maßband"),
    ("kombizange",          "Kombizange"),
    ("seitenschneider",     "Seitenschneider"),
    ("gabelschluessel",     "Gabelschlüssel"),
    ("rollgabelschluessel", "Rollgabelschlüssel"),
    ("winkelschleifer",     "Winkelschleifer"),
    ("stichsaege",          "Stichsäge"),
    ("schraubklemme",       "Schraubklemme"),
    ("malerrolle",          "Malerrolle"),
    ("pinsel",              "Pinsel"),
    ("kelle",               "Kelle"),
    ("spachtel",            "Spachtel"),
    ("feile",               "Feile"),
    ("zollstock",           "Zollstock"),
    ("kreissaege",          "Kreissäge"),
]

# ─── Canvas / card constants ──────────────────────────────────────────────────

SZ = 300    # image canvas in pixels
LW = 5      # default line width


def p(frac):
    return int(frac * SZ)


def new_card(bg="white"):
    img = Image.new("RGB", (SZ, SZ), bg)
    d = ImageDraw.Draw(img)
    return img, d


def border(d, color="black", pad=4):
    d.rectangle([pad, pad, SZ - pad - 1, SZ - pad - 1], outline=color, width=3)


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

_font_path = None
for _fp in _FONT_PATHS:
    if os.path.exists(_fp):
        _font_path = _fp
        break


def font(size):
    if _font_path:
        return ImageFont.truetype(_font_path, size)
    return ImageFont.load_default()


# ─── Drawing functions (26 tools) ─────────────────────────────────────────────

def draw_bohrmaschine():
    img, d = new_card()
    # Body
    d.rectangle([p(.20), p(.10), p(.72), p(.54)], outline="black", width=LW)
    for yf in [.22, .30, .38, .46]:
        d.line([p(.26), p(yf), p(.54), p(yf)], fill="black", width=1)
    # Handle
    d.rectangle([p(.30), p(.54), p(.48), p(.86)], outline="black", width=LW)
    # Trigger guard
    d.arc([p(.30), p(.50), p(.54), p(.70)], 0, 180, fill="black", width=LW)
    # Chuck
    d.rectangle([p(.60), p(.24), p(.80), p(.40)], outline="black", width=LW)
    d.line([p(.66), p(.24), p(.66), p(.40)], fill="black", width=2)
    d.line([p(.73), p(.24), p(.73), p(.40)], fill="black", width=2)
    # Drill bit
    d.line([p(.80), p(.30), p(.97), p(.30)], fill="black", width=LW)
    d.line([p(.80), p(.34), p(.97), p(.34)], fill="black", width=2)
    border(d)
    return img


def draw_bohrer():
    img, d = new_card()
    cx = p(.50)
    # Shank
    d.rectangle([cx - p(.06), p(.04), cx + p(.06), p(.24)], outline="black", width=LW)
    # Outline of fluted section
    d.line([cx - p(.10), p(.24), cx - p(.13), p(.84)], fill="black", width=2)
    d.line([cx + p(.10), p(.24), cx + p(.13), p(.84)], fill="black", width=2)
    # Flute arcs
    for i in range(5):
        top = p(.24 + i * .12)
        bot = p(.24 + (i + 1) * .12)
        mid = (top + bot) // 2
        shift = p(.06) if i % 2 else -p(.06)
        d.arc([cx - p(.12) + shift, top, cx + p(.12) + shift, bot],
              0, 180, fill="black", width=2)
    # Tip
    d.polygon([(cx - p(.13), p(.84)), (cx + p(.13), p(.84)), (cx, p(.97))],
              outline="black", width=LW)
    border(d)
    return img


def draw_hammer():
    img, d = new_card()
    cx = p(.50)
    # Handle
    d.rectangle([cx - p(.06), p(.30), cx + p(.06), p(.94)], outline="black", width=LW)
    for yf in [.55, .64, .73, .82]:
        d.line([cx - p(.04), p(yf), cx + p(.04), p(yf)], fill="black", width=1)
    # Head
    d.rectangle([p(.10), p(.06), p(.90), p(.30)], outline="black", width=LW)
    # Eye hole in head
    d.ellipse([cx - p(.07), p(.13), cx + p(.07), p(.23)], outline="black", width=2)
    border(d)
    return img


def draw_meissel():
    img, d = new_card()
    cx = p(.50)
    # Body (trapezoid)
    d.polygon([(cx - p(.14), p(.06)), (cx + p(.14), p(.06)),
               (cx + p(.08), p(.80)), (cx - p(.08), p(.80))],
              outline="black", width=LW)
    # Cutting bevel
    d.polygon([(cx - p(.16), p(.80)), (cx + p(.16), p(.80)),
               (cx + p(.02), p(.94)), (cx - p(.02), p(.94))],
              fill="black", outline="black")
    # Strike cap
    d.rectangle([cx - p(.14), p(.04), cx + p(.14), p(.10)],
                outline="black", width=2)
    border(d)
    return img


def draw_kreuzschrauber():
    img, d = new_card()
    cx = p(.50)
    # Handle (rounded octagon approximated with ellipse)
    d.ellipse([cx - p(.22), p(.04), cx + p(.22), p(.30)], outline="black", width=LW)
    d.ellipse([cx - p(.16), p(.08), cx + p(.16), p(.26)], outline="black", width=1)
    # Shaft
    d.rectangle([cx - p(.04), p(.30), cx + p(.04), p(.82)], outline="black", width=LW)
    # Phillips cross
    ty, arm = p(.84), p(.09)
    d.line([cx, ty, cx, ty + p(.14)], fill="black", width=LW)
    d.line([cx - arm, ty + p(.07), cx + arm, ty + p(.07)], fill="black", width=LW)
    border(d)
    return img


def draw_schlitzschrauber():
    img, d = new_card()
    cx = p(.50)
    # Handle
    d.ellipse([cx - p(.22), p(.04), cx + p(.22), p(.30)], outline="black", width=LW)
    d.ellipse([cx - p(.16), p(.08), cx + p(.16), p(.26)], outline="black", width=1)
    # Shaft
    d.rectangle([cx - p(.04), p(.30), cx + p(.04), p(.84)], outline="black", width=LW)
    # Flat tip
    d.rectangle([cx - p(.13), p(.84), cx + p(.13), p(.91)], fill="black", outline="black")
    border(d)
    return img


def draw_nuss():
    img, d = new_card()
    cx, cy, r = p(.50), p(.50), p(.35)
    pts = [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3),
            cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    d.polygon(pts, outline="black", width=LW)
    # Inner hex
    r2 = p(.18)
    pts2 = [(cx + r2 * math.cos(math.pi / 6 + i * math.pi / 3),
             cy + r2 * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    d.polygon(pts2, outline="black", width=2)
    # Square drive (rotated square)
    sq = p(.10)
    d.polygon([(cx, cy - sq), (cx + sq, cy), (cx, cy + sq), (cx - sq, cy)],
              outline="black", width=2)
    border(d)
    return img


def draw_ratsche():
    img, d = new_card()
    hx, hy, r = p(.32), p(.32), p(.22)
    # Head circle
    d.ellipse([hx - r, hy - r, hx + r, hy + r], outline="black", width=LW)
    # Teeth
    for i in range(12):
        a = i * math.pi / 6
        x0 = hx + (r - p(.03)) * math.cos(a)
        y0 = hy + (r - p(.03)) * math.sin(a)
        x1 = hx + (r + p(.04)) * math.cos(a)
        y1 = hy + (r + p(.04)) * math.sin(a)
        d.line([x0, y0, x1, y1], fill="black", width=2)
    # Square drive
    sq = p(.08)
    d.rectangle([hx - sq, hy - sq, hx + sq, hy + sq], outline="black", width=2)
    # Handle
    d.rectangle([p(.44), p(.26), p(.94), p(.38)], outline="black", width=LW)
    border(d)
    return img


def draw_inbusschluessel():
    img, d = new_card()
    # Short arm (vertical, top-left quadrant)
    d.rectangle([p(.38), p(.10), p(.52), p(.50)], outline="black", width=LW)
    # Long arm (horizontal)
    d.rectangle([p(.38), p(.50), p(.88), p(.62)], outline="black", width=LW)
    # Fill corner junction
    d.rectangle([p(.38), p(.46), p(.54), p(.64)], fill="black")
    # Hex facet marks on short arm
    for yf in [.18, .26, .34, .42]:
        d.line([p(.38), p(yf), p(.41), p(yf)], fill="black", width=1)
        d.line([p(.49), p(yf), p(.52), p(yf)], fill="black", width=1)
    # Hex facet marks on long arm
    for xf in [.54, .62, .70, .78]:
        d.line([p(xf), p(.50), p(xf), p(.53)], fill="black", width=1)
        d.line([p(xf), p(.59), p(xf), p(.62)], fill="black", width=1)
    border(d)
    return img


def draw_handsaege():
    img, d = new_card()
    # Blade
    d.rectangle([p(.05), p(.30), p(.78), p(.42)], outline="black", width=LW)
    # Teeth
    n = 15
    bw = p(.73) / n
    for i in range(n):
        x = p(.05) + int(i * bw)
        nx = p(.05) + int((i + 1) * bw)
        mid = (x + nx) // 2
        d.line([x, p(.42), mid, p(.54), nx, p(.42)], fill="black", width=2)
    # D-handle
    d.arc([p(.56), p(.10), p(.92), p(.42)], 270, 90, fill="black", width=LW)
    d.line([p(.74), p(.10), p(.74), p(.42)], fill="black", width=LW)
    d.line([p(.56), p(.26), p(.74), p(.26)], fill="black", width=LW)
    border(d)
    return img


def draw_wasserwaage():
    img, d = new_card()
    # Body
    d.rectangle([p(.04), p(.38), p(.96), p(.62)], outline="black", width=LW)
    # Center bubble vial
    d.ellipse([p(.32), p(.41), p(.68), p(.59)], outline="black", width=2)
    # Bubble
    d.ellipse([p(.44), p(.44), p(.56), p(.56)], outline="black", width=2)
    # End vials
    d.ellipse([p(.08), p(.41), p(.20), p(.59)], outline="black", width=2)
    d.ellipse([p(.80), p(.41), p(.92), p(.59)], outline="black", width=2)
    # Scale marks
    for xf in [.10, .14, .16, .82, .86, .88]:
        d.line([p(xf), p(.38), p(xf), p(.43)], fill="black", width=1)
    border(d)
    return img


def draw_massband():
    img, d = new_card()
    cx, cy, r = p(.46), p(.44), p(.30)
    # Case (rounded rectangle)
    d.rounded_rectangle([cx - r, cy - r, cx + r, cy + r],
                        radius=p(.07), outline="black", width=LW)
    # Belt clip
    d.rectangle([p(.60), p(.16), p(.72), p(.30)], outline="black", width=2)
    # Tape emerging right
    d.arc([p(.60), p(.60), p(.88), p(.88)], 180, 360, fill="black", width=LW)
    for i in range(4):
        x = p(.63 + i * .05)
        d.line([x, p(.80), x, p(.85)], fill="black", width=1)
    # Thumb button
    d.rectangle([p(.32), p(.34), p(.44), p(.44)], outline="black", width=2)
    # Spring return arrow hint
    d.text((cx - p(.10), cy - p(.06)), "m", fill="black", font=font(36))
    border(d)
    return img


def draw_kombizange():
    img, d = new_card()
    # Pivot
    px, py = p(.50), p(.50)
    d.ellipse([px - p(.07), py - p(.07), px + p(.07), py + p(.07)], fill="black")
    # Left jaw
    d.polygon([(p(.08), py), (p(.34), py), (p(.30), p(.08)), (p(.18), p(.08))],
              outline="black", width=LW)
    # Right jaw (serrated side)
    d.polygon([(p(.66), py), (p(.92), py), (p(.82), p(.08)), (p(.70), p(.08))],
              outline="black", width=LW)
    # Left handle
    d.rectangle([p(.08), py, p(.34), p(.94)], outline="black", width=LW)
    # Right handle
    d.rectangle([p(.66), py, p(.92), p(.94)], outline="black", width=LW)
    # Serration marks on right jaw
    for yf in [.20, .28, .36, .44]:
        d.line([p(.70), p(yf), p(.80), p(yf)], fill="black", width=1)
    border(d)
    return img


def draw_seitenschneider():
    img, d = new_card()
    px, py = p(.50), p(.48)
    d.ellipse([px - p(.07), py - p(.07), px + p(.07), py + p(.07)], fill="black")
    # Left cutting blade (comes to a point at top-left)
    d.polygon([(p(.08), py), (p(.36), py), (p(.26), p(.08)), (p(.10), p(.08))],
              outline="black", width=LW)
    # Right cutting blade
    d.polygon([(p(.64), py), (p(.92), py), (p(.90), p(.08)), (p(.74), p(.08))],
              outline="black", width=LW)
    # Cutting point
    d.polygon([(p(.26), p(.08)), (p(.74), p(.08)), (p(.50), p(.16))],
              fill="black", outline="black", width=2)
    # Handles
    d.rectangle([p(.08), py, p(.36), p(.94)], outline="black", width=LW)
    d.rectangle([p(.64), py, p(.92), p(.94)], outline="black", width=LW)
    border(d)
    return img


def draw_gabelschluessel():
    img, d = new_card()
    cx = p(.50)
    # Handle
    d.rectangle([cx - p(.08), p(.35), cx + p(.08), p(.94)], outline="black", width=LW)
    # Open-end wrench head
    # Outer arc
    d.arc([p(.12), p(.06), p(.68), p(.50)], 180, 360, fill="black", width=LW)
    # Inner arc (gap)
    d.arc([p(.20), p(.13), p(.60), p(.43)], 180, 360, fill="black", width=3)
    # Left jaw
    d.line([p(.12), p(.28), p(.20), p(.28)], fill="black", width=LW)
    d.line([p(.12), p(.28), p(.12), p(.35)], fill="black", width=LW)
    d.line([p(.20), p(.28), p(.20), p(.35)], fill="black", width=3)
    # Right jaw
    d.line([p(.60), p(.28), p(.68), p(.28)], fill="black", width=LW)
    d.line([p(.68), p(.28), p(.68), p(.35)], fill="black", width=LW)
    d.line([p(.60), p(.28), p(.60), p(.35)], fill="black", width=3)
    border(d)
    return img


def draw_rollgabelschluessel():
    img, d = new_card()
    # Handle
    d.rectangle([p(.40), p(.44), p(.56), p(.94)], outline="black", width=LW)
    # Fixed upper jaw
    d.rectangle([p(.40), p(.10), p(.56), p(.44)], outline="black", width=LW)
    d.rectangle([p(.40), p(.10), p(.72), p(.24)], outline="black", width=LW)
    # Movable lower jaw (offset)
    d.rectangle([p(.18), p(.44), p(.40), p(.56)], outline="black", width=LW)
    d.rectangle([p(.18), p(.30), p(.40), p(.44)], outline="black", width=LW)
    # Jaw gap
    d.rectangle([p(.40), p(.24), p(.72), p(.30)], fill="white", outline="white")
    d.line([p(.40), p(.24), p(.72), p(.24)], fill="black", width=2)
    d.line([p(.40), p(.30), p(.72), p(.30)], fill="black", width=2)
    # Adjustment wheel
    d.ellipse([p(.22), p(.38), p(.38), p(.54)], outline="black", width=LW)
    for i in range(6):
        a = i * math.pi / 3
        d.line([p(.30) + p(.08) * math.cos(a), p(.46) + p(.08) * math.sin(a),
                p(.30) + p(.06) * math.cos(a), p(.46) + p(.06) * math.sin(a)],
               fill="black", width=2)
    border(d)
    return img


def draw_winkelschleifer():
    img, d = new_card()
    # Motor body (horizontal)
    d.rounded_rectangle([p(.08), p(.20), p(.78), p(.48)],
                        radius=p(.06), outline="black", width=LW)
    # Rear handle
    d.rectangle([p(.78), p(.28), p(.96), p(.40)], outline="black", width=LW)
    # Side handle (top)
    d.rectangle([p(.26), p(.10), p(.38), p(.22)], outline="black", width=LW)
    # Guard (half circle)
    d.arc([p(.04), p(.40), p(.46), p(.90)], 0, 180, fill="black", width=LW)
    # Disc
    d.ellipse([p(.06), p(.42), p(.44), p(.88)], outline="black", width=2)
    # Disc center hole
    d.ellipse([p(.22), p(.60), p(.28), p(.70)], fill="black")
    # Ventilation slots
    for xf in [.44, .52, .60]:
        d.line([p(xf), p(.26), p(xf), p(.42)], fill="black", width=1)
    border(d)
    return img


def draw_stichsaege():
    img, d = new_card()
    # Body
    d.rounded_rectangle([p(.18), p(.08), p(.82), p(.52)],
                        radius=p(.08), outline="black", width=LW)
    # Top handle
    d.arc([p(.30), p(.04), p(.70), p(.30)], 180, 360, fill="black", width=LW)
    # Base plate
    d.rectangle([p(.10), p(.52), p(.90), p(.60)], outline="black", width=LW)
    # Blade
    d.rectangle([p(.46), p(.60), p(.54), p(.94)], outline="black", width=LW)
    # Blade teeth (right side)
    for i in range(6):
        y = p(.62 + i * .05)
        d.line([p(.54), y, p(.62), y + p(.025)], fill="black", width=2)
    # Ventilation slots
    for xf in [.32, .40, .60, .68]:
        d.line([p(xf), p(.18), p(xf), p(.42)], fill="black", width=1)
    border(d)
    return img


def draw_schraubklemme():
    img, d = new_card()
    cx = p(.50)
    # C-frame (arc)
    d.arc([p(.14), p(.08), p(.86), p(.88)], 55, 305, fill="black", width=LW)
    # Top cross bar
    d.rectangle([p(.14), p(.08), p(.86), p(.24)], outline="black", width=LW)
    # T-bar handle
    d.line([p(.34), p(.12), p(.66), p(.12)], fill="black", width=LW)
    d.line([cx, p(.12), cx, p(.24)], fill="black", width=LW)
    # Screw rod
    d.line([cx, p(.24), cx, p(.62)], fill="black", width=LW)
    # Thread marks
    for yf in [.30, .36, .42, .48, .54]:
        d.line([cx - p(.04), p(yf), cx + p(.04), p(yf)], fill="black", width=1)
    # Pressure pad
    d.ellipse([cx - p(.12), p(.62), cx + p(.12), p(.74)], outline="black", width=LW)
    border(d)
    return img


def draw_malerrolle():
    img, d = new_card()
    # Roller cylinder
    d.ellipse([p(.06), p(.16), p(.30), p(.52)], outline="black", width=LW)
    d.rectangle([p(.18), p(.16), p(.74), p(.52)], outline="black", width=LW)
    d.ellipse([p(.62), p(.16), p(.86), p(.52)], outline="black", width=LW)
    # Roller texture (stripes)
    for xf in [.28, .38, .48, .58, .68]:
        d.line([p(xf), p(.16), p(xf), p(.52)], fill="black", width=1)
    # Frame arm
    d.line([p(.74), p(.34), p(.90), p(.34)], fill="black", width=LW)
    d.line([p(.90), p(.34), p(.90), p(.88)], fill="black", width=LW)
    # Handle grip
    d.rounded_rectangle([p(.82), p(.80), p(.96), p(.96)],
                        radius=p(.04), outline="black", width=LW)
    border(d)
    return img


def draw_pinsel():
    img, d = new_card()
    cx = p(.50)
    # Handle
    d.rounded_rectangle([cx - p(.08), p(.06), cx + p(.08), p(.58)],
                        radius=p(.04), outline="black", width=LW)
    # Ferrule
    d.rectangle([cx - p(.10), p(.58), cx + p(.10), p(.66)],
                fill="black", outline="black")
    # Bristle block
    d.polygon([(cx - p(.18), p(.66)), (cx + p(.18), p(.66)),
               (cx + p(.12), p(.90)), (cx - p(.12), p(.90))],
              outline="black", width=LW)
    # Bristle lines
    for xf in [-.12, -.06, .00, .06, .12]:
        x = cx + p(xf)
        d.line([x, p(.66), x + p(.02), p(.90)], fill="black", width=1)
    border(d)
    return img


def draw_kelle():
    img, d = new_card()
    cx = p(.50)
    # Tang / rod connecting handle to blade
    d.line([cx, p(.06), cx, p(.28)], fill="black", width=LW)
    # Handle
    d.rounded_rectangle([cx - p(.12), p(.04), cx + p(.12), p(.16)],
                        radius=p(.04), outline="black", width=LW)
    # Trowel blade (pointed diamond)
    d.polygon([(cx - p(.30), p(.36)),
               (cx + p(.30), p(.36)),
               (cx + p(.28), p(.58)),
               (cx, p(.94)),
               (cx - p(.28), p(.58))],
              outline="black", width=LW)
    # Centre line on blade
    d.line([cx, p(.36), cx, p(.94)], fill="black", width=1)
    border(d)
    return img


def draw_spachtel():
    img, d = new_card()
    cx = p(.50)
    # Handle
    d.rounded_rectangle([cx - p(.08), p(.04), cx + p(.08), p(.48)],
                        radius=p(.04), outline="black", width=LW)
    # Ferrule
    d.rectangle([cx - p(.10), p(.48), cx + p(.10), p(.56)],
                fill="black", outline="black")
    # Wide flat blade
    d.rectangle([cx - p(.28), p(.56), cx + p(.28), p(.90)],
                outline="black", width=LW)
    # Flex centre line
    d.line([cx, p(.56), cx, p(.90)], fill="black", width=1)
    # Width marks
    d.line([cx - p(.28), p(.72), cx + p(.28), p(.72)], fill="black", width=1)
    border(d)
    return img


def draw_feile():
    img, d = new_card()
    cx = p(.50)
    # Handle (oval)
    d.ellipse([cx - p(.18), p(.04), cx + p(.18), p(.28)], outline="black", width=LW)
    # Tang
    d.line([cx, p(.28), cx, p(.36)], fill="black", width=LW)
    # File body
    d.rectangle([cx - p(.10), p(.36), cx + p(.10), p(.92)],
                outline="black", width=LW)
    # Cross-cut hatching
    step = p(.05)
    for y in range(p(.40), p(.90), step):
        d.line([cx - p(.08), y, cx + p(.08), y + step // 2], fill="black", width=1)
    for y in range(p(.43), p(.90), step):
        d.line([cx + p(.08), y, cx - p(.08), y + step // 2], fill="black", width=1)
    border(d)
    return img


def draw_zollstock():
    img, d = new_card()
    # Segment dimensions
    sw, sh = p(.28), p(.10)
    # Segment 1 (horizontal, bottom)
    x1, y1 = p(.06), p(.70)
    d.rectangle([x1, y1, x1 + sw, y1 + sh], outline="black", width=LW)
    for xf in [.12, .18, .24]:
        d.line([p(xf), y1, p(xf), y1 + sh], fill="black", width=1)
    # Pivot 1
    d.ellipse([x1 + sw - p(.03), y1, x1 + sw + p(.03), y1 + sh], fill="black")
    # Segment 2 (angled 45° up-right)
    x2a, y2a = x1 + sw, y1 + sh // 2
    x2b, y2b = x2a + p(.22), y1 + sh // 2 - p(.22)
    pts2 = [(x2a, y2a - sh // 2), (x2a, y2a + sh // 2),
            (x2b, y2b + sh // 2), (x2b, y2b - sh // 2)]
    d.polygon(pts2, outline="black", width=LW)
    # Pivot 2
    d.ellipse([x2b - p(.03), y2b - p(.03), x2b + p(.03), y2b + p(.03)], fill="black")
    # Segment 3 (horizontal, top)
    x3, y3 = x2b, y2b - sh // 2
    d.rectangle([x3, y3, x3 + sw, y3 + sh], outline="black", width=LW)
    for xf_off in [p(.06), p(.12), p(.18)]:
        d.line([x3 + xf_off, y3, x3 + xf_off, y3 + sh], fill="black", width=1)
    border(d)
    return img


def draw_kreissaege():
    img, d = new_card()
    cx, cy, r = p(.40), p(.54), p(.30)
    # Circular blade
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline="black", width=LW)
    # Teeth
    for i in range(18):
        a = i * 2 * math.pi / 18
        x0 = cx + (r - p(.03)) * math.cos(a)
        y0 = cy + (r - p(.03)) * math.sin(a)
        x1 = cx + (r + p(.05)) * math.cos(a)
        y1 = cy + (r + p(.05)) * math.sin(a)
        d.line([x0, y0, x1, y1], fill="black", width=2)
    # Arbor hole
    d.ellipse([cx - p(.04), cy - p(.04), cx + p(.04), cy + p(.04)], fill="black")
    # Guard (partial arc)
    d.arc([cx - r - p(.04), cy - r - p(.04), cx + r + p(.04), cy + r + p(.04)],
          195, 340, fill="black", width=LW)
    # Motor / body
    d.rounded_rectangle([p(.56), p(.18), p(.92), p(.50)],
                        radius=p(.05), outline="black", width=LW)
    # Handle
    d.rectangle([p(.68), p(.06), p(.86), p(.20)], outline="black", width=LW)
    # Saw base plate
    d.rectangle([p(.10), p(.80), p(.70), p(.88)], outline="black", width=2)
    border(d)
    return img


# ─── Dispatch table ───────────────────────────────────────────────────────────

DRAW = {
    "bohrmaschine":        draw_bohrmaschine,
    "bohrer":              draw_bohrer,
    "hammer":              draw_hammer,
    "meissel":             draw_meissel,
    "kreuzschrauber":      draw_kreuzschrauber,
    "schlitzschrauber":    draw_schlitzschrauber,
    "nuss":                draw_nuss,
    "ratsche":             draw_ratsche,
    "inbusschluessel":     draw_inbusschluessel,
    "handsaege":           draw_handsaege,
    "wasserwaage":         draw_wasserwaage,
    "massband":            draw_massband,
    "kombizange":          draw_kombizange,
    "seitenschneider":     draw_seitenschneider,
    "gabelschluessel":     draw_gabelschluessel,
    "rollgabelschluessel": draw_rollgabelschluessel,
    "winkelschleifer":     draw_winkelschleifer,
    "stichsaege":          draw_stichsaege,
    "schraubklemme":       draw_schraubklemme,
    "malerrolle":          draw_malerrolle,
    "pinsel":              draw_pinsel,
    "kelle":               draw_kelle,
    "spachtel":            draw_spachtel,
    "feile":               draw_feile,
    "zollstock":           draw_zollstock,
    "kreissaege":          draw_kreissaege,
}

# ─── Card makers ─────────────────────────────────────────────────────────────

def make_image_card(key, image_dir=None):
    """Return a PIL image for the image card (tool drawing or photo)."""
    if image_dir:
        for ext in (".png", ".PNG", ".jpg", ".JPG", ".jpeg", ".JPEG"):
            path = os.path.join(image_dir, key + ext)
            if os.path.exists(path):
                img = Image.open(path).convert("RGB").resize((SZ, SZ), Image.LANCZOS)
                d = ImageDraw.Draw(img)
                border(d)
                return img
    if key in DRAW:
        return DRAW[key]()
    # Fallback: grey placeholder
    img, d = new_card("#eee")
    d.text((SZ // 2 - 20, SZ // 2 - 10), key[:12], fill="black", font=font(20))
    border(d)
    return img


def make_text_card(name):
    """Return a PIL image for the name/text card."""
    img, d = new_card("#ddeeff")
    border(d, color="#334466")

    # Determine font size based on word length
    max_word = max((len(w) for w in name.split()), default=1)
    total_len = len(name)
    if total_len <= 8:
        fsize = 52
    elif total_len <= 12:
        fsize = 42
    elif total_len <= 16:
        fsize = 34
    else:
        fsize = 26

    f = font(fsize)

    # Word-wrap
    words = name.split()
    lines, cur = [], ""
    max_w = SZ - p(.14)
    for word in words:
        test = (cur + " " + word).strip()
        bb = d.textbbox((0, 0), test, font=f)
        if bb[2] - bb[0] <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)

    line_h = fsize + 6
    total_h = len(lines) * line_h
    y = (SZ - total_h) / 2 - 10

    for line in lines:
        bb = d.textbbox((0, 0), line, font=f)
        x = (SZ - (bb[2] - bb[0])) / 2
        d.text((x, y), line, fill="#1a2a4a", font=f)
        y += line_h

    # Small label at bottom
    sf = font(16)
    hint = "Was ist das?"
    bb = d.textbbox((0, 0), hint, font=sf)
    x = (SZ - (bb[2] - bb[0])) / 2
    d.text((x, SZ - p(.12)), hint, fill="#667799", font=sf)
    return img


def make_back_card():
    """Card back design."""
    img, d = new_card("#1a3a6a")
    border(d, color="#ffffff")
    # Decorative diagonal lines
    for i in range(0, SZ + SZ, p(.12)):
        d.line([i, 0, 0, i], fill="#2a4a8a", width=2)
    # Centre text
    f1 = font(32)
    f2 = font(18)
    for txt, f, yf, col in [
        ("Werkzeug", f1, .40, "white"),
        ("Memory",   f1, .54, "#aaccff"),
        ("🔨",       f2, .68, "#aaccff"),
    ]:
        bb = d.textbbox((0, 0), txt, font=f)
        x = (SZ - (bb[2] - bb[0])) / 2
        d.text((x, p(yf)), txt, fill=col, font=f)
    border(d, color="white")
    return img


# ─── PIL image → ReportLab reader ─────────────────────────────────────────────

def pil_reader(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return ImageReader(buf)


# ─── Layout constants ─────────────────────────────────────────────────────────

CARD_W = 58 * mm
CARD_H = 58 * mm
PAGE_W, PAGE_H = A4
MARGIN = 10 * mm
COLS = int((PAGE_W - 2 * MARGIN) / CARD_W)   # 3
ROWS = int((PAGE_H - 2 * MARGIN) / CARD_H)   # 4
PER_PAGE = COLS * ROWS                        # 12
START_X = (PAGE_W - COLS * CARD_W) / 2
START_Y = (PAGE_H - ROWS * CARD_H) / 2
TICK = 4   # cut-mark tick length in points


def draw_cut_marks(c, x, y):
    c.setStrokeColorRGB(.6, .6, .6)
    c.setLineWidth(.4)
    for cx_, cy_ in [(x, y), (x + CARD_W, y), (x, y + CARD_H), (x + CARD_W, y + CARD_H)]:
        c.line(cx_ - TICK, cy_, cx_ + TICK, cy_)
        c.line(cx_, cy_ - TICK, cx_, cy_ + TICK)


def draw_cards_page(c, cards, label, page_num, total_pages, image_dir=None):
    c.setFont("Helvetica-Bold", 8)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(START_X, PAGE_H - MARGIN * .55,
                 f"Werkzeug-Memory — {label}  •  Seite {page_num}/{total_pages}")
    c.drawRightString(PAGE_W - START_X, PAGE_H - MARGIN * .55,
                      "Ausschneiden entlang der Markierungen")

    for idx, (kind, key, name) in enumerate(cards):
        row, col = divmod(idx, COLS)
        x = START_X + col * CARD_W
        y = PAGE_H - START_Y - (row + 1) * CARD_H

        if kind == "image":
            img = make_image_card(key, image_dir)
        elif kind == "text":
            img = make_text_card(name)
        else:
            img = make_back_card()

        c.drawImage(pil_reader(img), x + 1, y + 1, CARD_W - 2, CARD_H - 2)
        draw_cut_marks(c, x, y)

    c.showPage()


# ─── PDF builder ─────────────────────────────────────────────────────────────

def create_pdf(output, tools, image_dir=None):
    n = len(tools)
    # Build card lists
    img_cards  = [("image", k, nm) for k, nm in tools]
    text_cards = [("text",  k, nm) for k, nm in tools]
    back_cells = [("back",  "",  "") for _ in range(PER_PAGE)]

    def pages(cards):
        return [cards[i:i + PER_PAGE] for i in range(0, len(cards), PER_PAGE)]

    img_pages  = pages(img_cards)
    text_pages = pages(text_cards)
    n_img   = len(img_pages)
    n_text  = len(text_pages)
    total   = n_img + n_text + 1  # +1 for back page

    c = canvas.Canvas(output, pagesize=A4)

    # Image card pages
    for i, page in enumerate(img_pages):
        draw_cards_page(c, page, "Bildkarten", i + 1, total, image_dir)

    # Text card pages
    for i, page in enumerate(text_pages):
        draw_cards_page(c, page, "Wortkarten", n_img + i + 1, total, image_dir)

    # Card back page
    draw_cards_page(c, back_cells, "Rückseite (beidseitig drucken)", total, total)

    c.save()

    print(f"✓  {output}")
    print(f"   {n} Werkzeuge × 2 = {n * 2} Karten  ({total} Seiten)")
    print(f"   Druckhinweis:")
    print(f"     Seiten 1–{n_img}        : Bildkarten   (Vorderseite)")
    print(f"     Seiten {n_img+1}–{n_img+n_text}  : Wortkarten   (Vorderseite)")
    print(f"     Seite  {total}           : Rückseite    (auf Vorderseiten drucken)")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Werkzeug-Memory: A4 PDF mit Bild- und Wortkarten"
    )
    ap.add_argument("--image-dir", metavar="DIR",
                    help="Ordner mit eigenen Werkzeugbildern (PNG/JPG)."
                         " Dateinamen ohne Erweiterung = Schlüssel aus TOOLS-Liste.")
    ap.add_argument("--output", default="memory_game.pdf",
                    help="Ausgabedatei (Standard: memory_game.pdf)")
    ap.add_argument("--list-tools", action="store_true",
                    help="Alle Werkzeuge mit Schlüsseln ausgeben und beenden")
    args = ap.parse_args()

    if args.list_tools:
        print(f"{'Schlüssel':<24}  Deutsch")
        print("-" * 44)
        for k, name in TOOLS:
            print(f"  {k:<22}  {name}")
        return

    print(f"Generiere Memory-Spiel mit {len(TOOLS)} Werkzeugen …")
    if args.image_dir and not os.path.isdir(args.image_dir):
        print(f"Fehler: --image-dir '{args.image_dir}' nicht gefunden.", file=sys.stderr)
        sys.exit(1)

    create_pdf(args.output, TOOLS, args.image_dir)


if __name__ == "__main__":
    main()
