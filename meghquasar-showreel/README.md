# MeghQuasar showreel

A 94-second brand film for **MeghQuasar**, the broker-only air charter desk for the
Gulf–India–Africa–Europe corridor, built as a motion-design showreel piece.

*Megh* (मेघ) is Sanskrit for cloud; a quasar is among the most luminous objects in the
universe. The film follows the name: light cutting through cloud, then the desk's work
made visible.

- `index.html`: the film. It runs in real time in the browser (three.js + custom GLSL +
  Web Audio), with a transport bar, shot list and fullscreen.
- `dist/meghquasar-showreel.mp4`: 1920×1080, 30 fps H.264 render with the synthesized
  score (AAC). It is rendered from the same file, frame by frame.

## Shots

| # | Time | Shot | What's on screen |
|---|------|------|------------------|
| 01 | 0:00 | Signal | Starfield push-in to a quasar: GLSL accretion disk with Doppler colour shift, particle jets |
| 02 | 0:08 | Megh + Quasar | Backlit procedural cloud bank, god rays, kinetic wordmark and the two definitions |
| 03 | 0:18 | The fog | 110 noise-tangled flight paths, 3D-anchored data tags, glitch hits: the opaque charter market |
| 04 | 0:30 | The cut | A light sweep morphs every path, per vertex, into clean lanes: "Broker-only" |
| 05 | 0:38 | The corridor | 72k-point Fibonacci globe on a Natural Earth land mask, 18 great-circle routes across 15 hubs |
| 06 | 0:52 | Sourcing | 700 instanced jets scanned down to a 5-operator shortlist |
| 07 | 0:57 | Feasibility | VOHS → FAOR exceeds an illustrative 5,500 km range; tech stop at FSIA; GO |
| 08 | 1:02 | Compliance | Document stack and scanning ring; OFAC SDN, UN, EU, UK OFSI, India UAPA/MHA |
| 09 | 1:07 | Quotes | Stacked 3D bars re-rank from headline price to all-in (illustrative values) |
| 10 | 1:12 | Mission | Comet along the VOHS → OMDB great circle with live telemetry |
| 11 | 1:20 | Why it matters | Dawn over a cloud sea |
| 12 | 1:26 | Resolve | Quasar mark and end card |

## Accuracy

- Every distance on screen is computed at runtime from airport coordinates using the
  haversine great-circle formula (for example VOHS → OMDB is 2,546 km and VOHS → FAOR is 7,257 km).
- Range rings use the true destination-point formula, so their shape is correct on the map.
- The aircraft range, the quote values, the operator shortlist and the mission panel are
  illustrative, and each is marked as such on screen.
- 3C 273 is the first quasar identified (1963); its coordinates are shown in the opening.

## Preview

```sh
npm install
npm run preview          # http://localhost:8080
```

three.js loads from jsDelivr and fonts from Google Fonts, so the page needs network
access. Press play for sound; keys: space, ← →, M, C, F.

## Render the MP4

```sh
pip install imageio-ffmpeg     # or set FFMPEG to an ffmpeg with libx264
npm run render                 # → dist/meghquasar-showreel.mp4
node tools/render.mjs --stills 15.3,48,70.9   # PNG stills → dist/stills/
node tools/render.mjs --fps 60 --workers 4    # smoother, slower
```

The renderer serves the page to headless Chromium, calls `MQ.renderFrame(t)` for each
frame (every frame is a pure function of time), pipes the frames to ffmpeg, renders the
score offline with `OfflineAudioContext`, and muxes both.

## Editing

- Copy and timing: `buildCues()` and `SHOTS` in `index.html`.
- Hubs, routes and the illustrative range: `HUBS`, `ROUTES`, `ILLUSTRATIVE_RANGE_KM`.
- Score: `renderScore()` (120 BPM, D minor; cuts land on bar lines).
- Land mask: `npm run landmask` regenerates the embedded bitmask from `world-atlas`.
- `npm run artifact` writes the claude.ai Artifact variant (the host adds its own
  document wrapper).

Credits: three.js, Natural Earth via `world-atlas`, Unbounded, Instrument Sans,
IBM Plex Mono, Tiro Devanagari Hindi.
