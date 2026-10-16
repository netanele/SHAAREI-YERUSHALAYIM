# Shaarei Yerushalayim — donor catalog

Digital donor catalog for **Shaarei Yerushalayim (שערי ירושלים)**, a planned synagogue and Torah center in Jerusalem. The project is initiated by Marc Elbaz, is before construction, and is raising donations to build the whole complex. The catalog presents the vision to donors.

- Live site: GitHub Pages from `/docs` on `main` → https://netanele.github.io/SHAAREI-YERUSHALAYIM/
- Deep links skip the language screen: add `#he`, `#en`, `#fr` or `#es` (or a page, e.g. `#en-dome`).

## Layout

| Path | What it is |
|---|---|
| `docs/index.html` | The whole site: one self-contained page (HTML, CSS, vanilla JS, no build step). Source of truth. |
| `docs/img/` | Catalog images; `docs/img/t/` contents-screen thumbnails; `docs/img/og-cover.jpg` the 1200×630 link preview. |
| `docs/audio/` | Background music `jerusalem-night.mp3` (see Music below). |
| `docs/video/` | Hebrew promo videos: `…_WhatsApp.mp4` (720×1280, for sending in chats with HD on) and `…_HD.mp4` (1080×1920, send as a Document or upload to YouTube). |
| `tools/video/` | Scripts that build the videos and the link-preview image. |
| `data/` | Source material, **git-ignored** (`.gitignore` lists only `/data/` and `.DS_Store`): original Word texts, printer brief, original images, build output. Never commit it. |

## Content rules

- Four languages: Hebrew (RTL), English, French, Spanish (LTR). The first screen asks for a language; page direction follows it. Choosing a language from the top menu always returns to the cover.
- Body texts are **verbatim** from the Word files in `data/` (`Shaarei_Yerushalayim_Texts_HE_EN_FR_ES.docx`, the computer-room texts in `Printiv_Handoff_and_Computer_Texts.docx`, `12_Underground_Parking_Text_HE_EN_FR_ES.docx`). Do not rewrite them. Section titles in EN/FR/ES are our own translations, pending Marc's approval.
- The "guest rooms" text is intentionally left out: the computer room replaced it.
- Images are conceptual renderings of a planned building. No tag on the images; keep the single line on the back cover and on the video's closing card ("כל התמונות הן הדמיות רעיוניות של פרויקט מתוכנן").
- Contact: Marc Elbaz, WhatsApp +1 786 909 0999 (`https://wa.me/17869090999`). The QR code is an inline SVG in `index.html`.
- No logo yet: the name is set in gold type. Replace when a logo file arrives.

## Music

- Track: "EG. – Sounds of the Eternal Land – The Silence of Jerusalem at Night" by jakob_welik, from Pixabay (https://pixabay.com/music/world-eg-sounds-of-the-eternal-land-the-silence-of-jerusalem-at-night-411194/). Pixabay Content License: free, commercial use allowed, no attribution required. It is Content ID registered, so a YouTube upload of the video may get a claim that can be cleared.
- Only use music we have the right to use. Do not rip songs from YouTube or other commercial recordings.
- `docs/audio/jerusalem-night.mp3` is trimmed of the opening silence and normalized to about -20 LUFS (soft background).
- Catalog: the music starts with the language choice (browsers need a tap first; after a deep link it starts on the first tap) and loops. The speaker button in the top bar mutes and unmutes it; the choice is saved in `localStorage` (`sy-muted`). Music pauses when the tab is hidden.
- Videos: `compose.py` mixes the same file under the scenes (start offset, +3 dB, fade in and out) when it exists.

## Design

- Wide screens (≥900px and landscape) show two-page book spreads that follow the 24-page print plan; phones and portrait tablets show one page at a time with swipe (CSS scroll-snap).
- Navy velvet background, gold, Jerusalem-stone text pages; gate/arch motif.
- Fonts (Google Fonts): Frank Ruhl Libre (Hebrew), EB Garamond (Latin text), Cinzel (Latin caps), Assistant (UI).
- After any change, check phone (~390px), tablet and desktop widths in all four languages.

## Video and link preview

From the repo root start a server: `python3 -m http.server 8766`. Then in `tools/video/`:

```bash
python3 render.py 1      # text layers 720x1280
python3 render.py 1.5    # text layers 1080x1920
python3 render.py og     # rebuilds docs/img/og-cover.jpg
python3 compose.py 720  ../../docs/video/Shaarei_Yerushalayim_Video_WhatsApp.mp4
python3 compose.py 1080 ../../docs/video/Shaarei_Yerushalayim_Video_HD.mp4
python3 compose.py 720 preview   # still frames to check first
```

Needs Python with Pillow, numpy and Playwright (Chromium), plus ffmpeg. Scene list and timings are at the top of `compose.py`; texts are in `overlay.html`. WhatsApp re-compresses videos, so keep text large and bold, lines thick, and motion gentle.

## Workflow

Edit `docs/index.html`, test, commit, push. Pages updates about a minute later. The catalog is also published as a claude.ai artifact with the same page body (everything inside `<body>`); update it too when the content changes.
