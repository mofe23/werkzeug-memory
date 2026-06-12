# Werkzeug-Memory

Printable A4 memory card game for learning German tool names. Downloads real photos from the web, overlays the German name, and outputs a PDF ready to print and cut.

```
┌──────────────────┐
│                  │
│   [tool photo]   │
│                  │
├──────────────────┤
│  Bohrmaschine    │
└──────────────────┘
```

26 tools · 52 cards · playing-card size (63 × 88 mm) · 7 pages

---

## Install

**macOS** — requires Python 3 from [python.org](https://www.python.org/downloads/) or Homebrew (`brew install python`):

```bash
pip3 install Pillow reportlab requests ddgs
```

**Linux:**

```bash
pip3 install Pillow reportlab requests ddgs
```

If `pip3` is not found on Linux, install it first:

```bash
# Debian / Ubuntu
sudo apt install python3-pip

# Arch
sudo pacman -S python-pip
```

---

## Run

```bash
git clone https://github.com/YOUR_USERNAME/werkzeug-memory.git
cd werkzeug-memory
python3 memory_game_v2.py
```

First run downloads ~26 images and takes 1–2 minutes. Open `memory_game_v2.pdf` when done.

---

## Print

1. Print **pages 1–6** single-sided (card fronts)
2. Print **page 7** on the reverse of each sheet (card backs)
3. Cut along the grey corner marks · shuffle · play

---

## When the AI got it wrong

Check what was downloaded:

```bash
python3 memory_game_v2.py --list-tools
```

Take or find a better photo, then drop it into `./my_images/` named after the tool key:

```
my_images/
├── hammer.jpg           # any of: .jpg .jpeg .png .webp .bmp .tiff
└── kreissaege.png
```

Files in `./my_images/` always override the downloaded cache. Rerun to rebuild the PDF.

To force a full re-download of everything:

```bash
python3 memory_game_v2.py --force-download
```

---

## Tool keys

| Key | Deutsch | Русский |
|-----|---------|---------|
| `bohrmaschine` | Bohrmaschine | Дрель |
| `bohrer` | Bohrer | Сверло |
| `hammer` | Hammer | Молоток |
| `meissel` | Meißel | Зубило |
| `kreuzschrauber` | Kreuzschraubenzieher | Крестовая отвёртка |
| `schlitzschrauber` | Schlitzschraubenzieher | Плоская отвёртка |
| `nuss` | Nuss | Торцевая головка |
| `ratsche` | Ratsche | Трещотка |
| `inbusschluessel` | Inbusschlüssel | Шестигранный ключ |
| `handsaege` | Handsäge | Ручная пила |
| `wasserwaage` | Wasserwaage | Уровень |
| `massband` | Maßband | Рулетка |
| `kombizange` | Kombizange | Плоскогубцы |
| `seitenschneider` | Seitenschneider | Бокорезы |
| `gabelschluessel` | Gabelschlüssel | Рожковый ключ |
| `rollgabelschluessel` | Rollgabelschlüssel | Разводной ключ |
| `winkelschleifer` | Winkelschleifer | Болгарка |
| `stichsaege` | Stichsäge | Лобзик |
| `schraubklemme` | Schraubklemme | Струбцина |
| `malerrolle` | Malerrolle | Малярный валик |
| `pinsel` | Pinsel | Кисть |
| `kelle` | Kelle | Мастерок |
| `spachtel` | Spachtel | Шпатель |
| `feile` | Feile | Напильник |
| `zollstock` | Zollstock | Складной метр |
| `kreissaege` | Kreissäge | Циркулярная пила |

---

> The AI's idea of a "Meißel" looks like it was forged in the Stone Age — because it was.
> Grab your phone, take a photo of the actual tool in your drawer, and drop it in `./images/`.
> Your game, your garage, your photos. The AI will stay out of the workshop.
