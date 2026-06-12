# Werkzeug-Memory — Capacitor Web App Plan

> Status: draft · branch `plan/capacitor-webapp`

---

## What we're building

A mobile-first Capacitor app (iOS + Android) that turns any word list into a printable
memory card game. The user installs the app, gets a ready-to-play Werkzeuge project
out of the box, can scroll through the cards, mark bad AI images, replace them with
phone photos, and export print-ready PDFs whenever enough replacements have accumulated
to fill a page.

The Python script stays as a standalone tool; the app is a full replacement for the
generate → browse → print → replace loop, fully on-device.

---

## Core user flow

```
Install
  └─ Werkzeuge project pre-loaded (26 cards, Wikipedia images auto-downloaded)
       │
       ├─ Scroll through cards          (swipeable gallery)
       │
       ├─ First print                   (all 52 cards → share PDF)
       │
       ├─ Mark AI fuckup                (long-press or flag button on a card)
       │
       ├─ Replace with camera           (tap flag → open camera → crop → save)
       │
       └─ Print replacements            (once a full A4 page of fixes is ready → share PDF)
```

---

## Feature breakdown

### 1 · Project management

A **project** is a named word list + its images. Multiple projects can coexist.

| Feature | Detail |
|---------|--------|
| Pre-installed project | "Werkzeuge" with the 26 tools from the Python script |
| Create project | Enter a name, paste or type a word list (one word pair per line: `DE;RU`) |
| Import word list | Plain text / CSV from Files app or clipboard |
| Project list | Home screen shows all projects with card count + unflagged-fuckup badge |
| Delete project | With confirmation; deletes cached images from device storage |

**Open question Q1** — Should users be able to add more target languages beyond RU, or is DE↔RU fixed for now?

---

### 2 · Card gallery (scroll view)

Swipeable card browser, one card at a time or grid view toggle.

Each card shows:
- Photo (full-bleed)
- German name (large banner)
- Russian translation (smaller, steel-blue)
- 🚩 flag button (top-right corner) to mark as AI fuckup
- Replacement photo indicator if already replaced

**Open question Q2** — Should the gallery show both card faces (image card + text card),
or just the image card since the text card is always generated from the name?

---

### 3 · Initial print (full deck)

Taps "Print all" → generates a PDF in the same A4 layout as the Python script
(playing-card size 63 × 88 mm, 3 × 3 per page, cut marks, card backs) →
hands it to the native OS share sheet for AirPrint / Files / email.

PDF is generated entirely on-device using a canvas-based renderer (no server).

**Open question Q3** — Same paper format (A4) only, or also Letter for US users?

---

### 4 · AI fuckup marking + camera replacement

Flag a card → options sheet:
- **"Foto aufnehmen"** → opens Capacitor Camera plugin → user photographs the real tool →
  image is cropped/resized on-device → saved to project storage → card re-renders
- **"Bild aus Fotos"** → opens photo picker (same plugin, `Camera.getPhoto` with `source: Photos`)
- **"Bild neu herunterladen"** → retries Wikipedia/DDG/Openverse pipeline for this card

Replaced images are stored in the app's private filesystem
(`@capacitor/filesystem`, `Directory.Data`), keyed by `{projectId}/{cardKey}.jpg`.
They shadow the auto-downloaded Wikipedia cache exactly like `./my_images/` does
in the Python script.

---

### 5 · Replacement print (optimised pages)

The app tracks which cards have been replaced since the last print.
When the replacement queue fills one full A4 page (9 cards), a badge appears:
**"9 Ersatzkarten druckbereit"**.

User taps → generates a PDF containing only the replacement cards (+ their pair)
→ share sheet. They print, cut out the new cards, swap them into the physical deck.

The queue is cleared after export. Partial pages can also be exported manually at any time.

**Open question Q4** — Should replacement cards be printed as singles (just the one
corrected card) or always as pairs (to keep the memory game symmetric)?
Pairs make sense but doubles the page usage for a single fix.

---

### 6 · PDF export via share sheet

Both "print all" and "print replacements" produce a PDF blob, handed to
`@capacitor/share` (`Share.share({ files: [pdfUri] })`).

On iOS this surfaces AirPrint, Files, email, etc.
On Android it opens the system share sheet with any PDF-capable app.

PDF generation: **jsPDF** + canvas rendering of each card. No server required.
Card layout mirrors the Python script exactly so physical decks printed from
both tools are interchangeable.

---

## Architecture

```
app/
├── src/
│   ├── pages/
│   │   ├── Home.tsx          # project list
│   │   ├── Project.tsx       # card gallery + print buttons
│   │   └── CardDetail.tsx    # single card + flag/replace actions
│   ├── components/
│   │   ├── CardView.tsx      # renders one card (photo + DE + RU banner)
│   │   ├── FlagSheet.tsx     # action sheet: camera / photos / re-download
│   │   └── PrintPreview.tsx  # PDF preview before share
│   ├── lib/
│   │   ├── imageSearch.ts    # Wikipedia REST → Openverse → DDG pipeline
│   │   ├── pdfRenderer.ts    # jsPDF card layout (matches Python script)
│   │   ├── storage.ts        # Capacitor Filesystem wrapper
│   │   └── db.ts             # SQLite project/card state (via @capacitor-community/sqlite)
│   └── data/
│       └── werkzeuge.ts      # bundled initial word list (26 tools, DE + RU)
├── capacitor.config.ts
└── package.json
```

**Open question Q5** — What JS framework? The transcription doesn't specify.
Options: React (Ionic React), Vue (Ionic Vue), or plain web components.
Recommendation: **Ionic React** — widest Capacitor ecosystem, easiest camera/share integration.

---

## Capacitor plugins needed

| Plugin | Use |
|--------|-----|
| `@capacitor/camera` | Take photo or pick from library |
| `@capacitor/filesystem` | Store images + export PDF to temp file |
| `@capacitor/share` | Hand PDF to OS share sheet / AirPrint |
| `@capacitor/preferences` | Store lightweight settings (last-opened project, etc.) |
| `@capacitor-community/sqlite` | Project + card state, replacement queue |
| `@capacitor/network` | Detect offline before attempting image downloads |

---

## Data model (SQLite)

```sql
-- one row per project
CREATE TABLE projects (
  id        TEXT PRIMARY KEY,   -- uuid
  name      TEXT NOT NULL,
  created   INTEGER NOT NULL    -- unix ms
);

-- one row per card in a project
CREATE TABLE cards (
  id           TEXT PRIMARY KEY,  -- uuid
  project_id   TEXT NOT NULL REFERENCES projects(id),
  key          TEXT NOT NULL,     -- e.g. "hammer"
  de_name      TEXT NOT NULL,
  ru_name      TEXT,
  img_source   TEXT,              -- 'wikipedia'|'openverse'|'ddg'|'camera'|'photos'
  img_path     TEXT,              -- filesystem path to cached image
  flagged      INTEGER DEFAULT 0, -- 1 = AI fuckup
  replaced     INTEGER DEFAULT 0, -- 1 = has custom image
  printed      INTEGER DEFAULT 0  -- 1 = included in last full print
);

-- tracks which replaced cards haven't been printed yet
CREATE TABLE replacement_queue (
  card_id    TEXT NOT NULL REFERENCES cards(id),
  queued_at  INTEGER NOT NULL
);
```

---

## Image download pipeline (on-device)

Same three-source fallback as the Python script, now running in the browser:

1. **Wikipedia REST API** — `https://en.wikipedia.org/api/rest_v1/page/summary/{slug}`
   → thumbnail URL → fetch image blob → store via Filesystem
2. **Openverse** — `https://api.openverse.org/v1/images/?q={query}`
3. **DuckDuckGo** — via `ddgs` (needs CORS proxy or native HTTP plugin)

**Open question Q6** — Wikipedia and Openverse work fine from a browser (CORS-friendly).
DuckDuckGo image search does not (no CORS headers). Do we drop DDG as a fallback
and rely on Wikipedia + Openverse only, or add a tiny proxy?

---

## Phased implementation

### Phase 1 — Scaffold + bundled data (no downloads yet)
- Ionic React + Capacitor project
- Home screen (project list)
- Werkzeuge project hard-coded with placeholder images
- Card gallery (swipe, grid toggle)
- Card renderer matching Python script layout

### Phase 2 — Image pipeline
- Wikipedia + Openverse fetching on-device
- Progress screen during initial image download
- Filesystem caching

### Phase 3 — Flag + replace
- Flag button UI
- Capacitor Camera integration (take photo + photo picker)
- Image crop / resize on-device
- Card re-render with custom image

### Phase 4 — PDF + print
- jsPDF card renderer (A4, 3×3, cut marks, backs — same as Python output)
- "Print all" → share sheet
- Replacement queue tracker
- "Print replacements" → share sheet

### Phase 5 — Project management
- Create / import / delete projects
- CSV / plain-text word list import
- Multiple concurrent projects

---

## Open questions summary

| # | Question | Why it matters |
|---|----------|----------------|
| Q1 | Fixed DE↔RU, or configurable language pairs? | Affects data model and card renderer |
| Q2 | Gallery shows image cards only, or image + text cards? | UX and print symmetry |
| Q3 | A4 only, or also Letter? | PDF renderer complexity |
| Q4 | Replacement prints single corrected card, or always a pair? | Page-fill logic |
| Q5 | React, Vue, or other? | Scaffolding decision — needed before Phase 1 |
| Q6 | Drop DDG (CORS), or add a proxy for it? | Image pipeline reliability |
