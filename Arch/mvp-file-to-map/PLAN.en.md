# MVP Plan — Cart Tracker Web, Stage 0 ("file → map")

**Start here.** This is the step-by-step plan for building the first version of the
web panel. Read [ARCHITECTURE.md](ARCHITECTURE.md) for the *why* and the exact data
contracts; this file covers *what to do, in what order, and how to know each
step is done*.

---

## 0. Goal and scope

**Goal:** a React website that reads production-cart coordinates from a file and
shows them on a map as moving dots, like buses on Yandex Maps. The coordinates are
already computed elsewhere (by the positioning engine / simulator / a Python script,
from signal attenuation to 2+ base stations). The website only displays them.

**In scope (Stage 0)**

- Load a scenario file: site, base stations, carts, time-ordered position fixes.
- Validate it and show clear errors if it's wrong.
- Map with base stations (fixed icons) and carts (dots).
- Replay over time: play / pause / speed / scrub; dots glide smoothly with heading.
- Per cart: accuracy circle, short trail, online/stale/offline status, method badge.
- Sidebar: cart list with search, details of the selected cart.
- Two ways to load: a built-in demo file, or drag-and-drop your own.
- Works on OSM street map **or** a floor-plan image **or** a blank grid.

**Out of scope (later stages):** computing positions from RSSI, backend, database,
Magma integration, history queries, auth, station editing, mobile layout polish.

**Built so that later:** swapping the file for a live WebSocket feed (backend / Magma)
is one new class, with no changes to the map or sidebar. See ARCHITECTURE §2, §7, §9.

**Definition of done for Stage 0:** see §4 (demo checklist).

---

## 1. Before you start (≈ 1–2 days if new to the stack)

Install:
- **Node.js 20+** (you have v24 — fine) and npm.
- **Git**, **VS Code** with extensions: ESLint, Prettier, Error Lens (optional).

Learn just enough of (in this order, ~1 hour each, by doing the tutorial):
1. **TypeScript basics:** types, unions, `type` vs `interface`, generics at a glance.
   → typescriptlang.org "TS for JS programmers".
2. **React:** components, props, `useState`, `useEffect` (and its cleanup!), `useRef`.
   → react.dev "Learn" section, first 3 chapters.
3. **Leaflet:** map, tile layer, marker, circle, polyline; then react-leaflet's
   `MapContainer`. → leafletjs.com "Quick Start", react-leaflet.js.org "Getting started".
4. **zustand** README (10 minutes) and **zod** README "Basic usage" (15 minutes).

You don't need to know: Redux, Next.js, CSS frameworks, backend, Docker (until §3 step 11).

---

## 2. Milestones at a glance

| # | Milestone | Result you can show | Effort* |
|---|---|---|---|
| M1 | Skeleton | App runs, empty map visible, lint + tests run | 0.5–1 d |
| M2 | Contract | Types + zod schemas + example file validated by a test | 1 d |
| M3 | Static map | Stations and first position of every cart drawn | 1–2 d |
| M4 | Replay | Dots move over time; playback bar works | 2 d |
| M5 | "Yandex feel" | Smooth gliding, heading, trails, accuracy, status | 2 d |
| M6 | Panel UX | Cart list, details, selection, layer toggles | 1–2 d |
| M7 | Any file | Drag-and-drop, validation errors, floor-plan basemap, CSV (opt.) | 1–2 d |
| M8 | Hand-off | Generator script, tests green, README, build/Docker, WS stub | 1–2 d |

\*For one developer doing this for the first time. Total ≈ **2–3 weeks**. M1–M4 alone
already give a demo.

---

## 3. Step-by-step

Each step has: **Do** (tasks) → **Done when** (check) → **Watch out** (common
beginner traps).

### Step 1 — Create the project (M1)

**Do**
```bash
npm create vite@latest cart-tracker-web -- --template react-ts
```
```bash
cd cart-tracker-web && npm install
```
```bash
npm install leaflet react-leaflet zustand zod
```
```bash
npm install -D @types/leaflet vitest @testing-library/react @testing-library/jest-dom jsdom prettier
```
- `git init`, first commit.
- Create the folder structure from ARCHITECTURE §4 (empty files with a `// TODO` are fine).
- Add scripts to `package.json`: `"test": "vitest"`, `"lint": "eslint ."`,
  `"format": "prettier --write ."`.
- Add the ESLint `no-restricted-imports` rules from ARCHITECTURE §3 (e.g. forbid
  `leaflet` and `react-leaflet` everywhere except `src/features/map/**`, forbid
  `react` inside `src/domain/**` and `src/sources/**`).
- Copy `.env.example`:
  ```
  VITE_SOURCE=file
  VITE_FILE_URL=/data/demo-scenario.json
  VITE_WS_URL=ws://localhost:8080/ws
  ```

**Done when:** `npm run dev` opens the page; `npm test` runs (even with 0 tests);
`npm run lint` passes.

**Watch out:** env vars must start with `VITE_` to reach the browser. Restart
`npm run dev` after editing `.env`.

---

### Step 2 — Write the data contract first (M2)

This is the most important step. Everything else depends on it.

**Do**
- `src/domain/schemas.ts`: zod schemas for `LocalPoint`, `GeoPoint`, `SiteConfig`,
  `Station`, `Cart`, `PositionFix`, `ScenarioFile` exactly as in ARCHITECTURE §6.
  Add the cross-field checks from §6.3 with `superRefine` (coordinate system match,
  unique ids, unknown `cartId`, `origin` required for local+osm…).
- `src/domain/types.ts`: `export type PositionFix = z.infer<typeof PositionFixSchema>` etc.
- Copy `examples/scenario.example.json` (next to this plan) into the project as
  `public/data/demo-scenario.json` and `src/domain/__fixtures__/scenario.example.json`.
- `src/sources/file/parsers/parseJsonScenario.ts`:
  `parse(text: string): { ok: true; scenario } | { ok: false; errors: string[] }`.
  It does `JSON.parse` (catching syntax errors), zod `safeParse`, turns zod issues into
  `"fixes[3].position: expected {x,y} because site.coordinateSystem = local"`, and
  sorts `fixes` by `ts`.
- Tests: example file parses; a file with a `{lat,lon}` fix in a `local` site fails
  with a readable message; broken JSON fails gracefully.

**Done when:** `npm test` shows ~5 green tests for parsing.

**Watch out:** don't skip `schemaVersion`. Always store `ts` as ISO-8601 **UTC**
(`...Z`). Convert to epoch ms once, at parse time.

---

### Step 3 — Geometry helpers (M2/M3)

**Do**
- `src/domain/geo.ts`:
  - `localToWgs84({x,y}, origin, rotationDeg)`: rotate, then
    `lat = origin.lat + y / 111_320`, `lon = origin.lon + x / (111_320 · cos(origin.lat))`.
    (Flat approximation, error is negligible for a factory-sized site.)
  - `wgs84ToLocal` (inverse), `distanceM(a, b)`, `bearingDeg(a, b)`.
- `src/domain/interpolate.ts`: `lerpPoint(a, b, t)`, `lerpAngle(a, b, t)` (shortest way
  round: 350° → 10° goes through 0°, not 180°).
- Tests: round-trip local→wgs84→local within 1 cm; bearing (0,0)→(0,10) = 0°,
  →(10,0) = 90°; `lerpAngle(350, 10, 0.5) = 0`.

**Done when:** tests green.

---

### Step 4 — Show a map and the stations (M3)

**Do**
- `src/features/map/projection.ts`: `makeProjection(site)` returns
  `{ toLatLng(p: Point): [number, number]; crs: 'EPSG3857' | 'Simple' }` per the table
  in ARCHITECTURE §6.1.
- `src/features/map/basemaps.tsx`: `osm` → `<TileLayer url=...>` (default
  `https://tile.openstreetmap.org/{z}/{x}/{y}.png` with attribution);
  `image` → `<ImageOverlay>` with `CRS.Simple`; `none` → light grid background.
- `MapView.tsx`: `MapContainer` filling the area, `preferCanvas`, fits bounds to all
  stations on load.
- `StationLayer.tsx`: one marker per station with a simple SVG/triangle icon + tooltip.
- For now load the demo file directly in `App.tsx` (temporary) and pass stations in.

**Done when:** three station icons appear in the right relative positions
(BS-1 bottom-left, BS-2 200 m east, BS-3 top-middle).

**Watch out (the classic Leaflet traps):**
- Import `leaflet/dist/leaflet.css` once in `main.tsx`, otherwise tiles are scrambled.
- The map container needs an explicit **height** (e.g. `height: 100%` all the way up,
  or `100vh`), otherwise it renders as 0 px and you see nothing.
- Default marker icons are broken under Vite; use `CircleMarker` or your own `divIcon`.
- Leaflet uses `[lat, lng]`; GeoJSON uses `[lng, lat]`. Never mix them.
- With `CRS.Simple`, `LatLng = [y, x]`.

---

### Step 5 — The store and the source interface (M3)

**Do**
- `src/sources/PositionSource.ts`: copy the interface from ARCHITECTURE §7.
- `src/store/trackingStore.ts`: zustand store with the shape from ARCHITECTURE §8.1 and
  actions `setSite`, `applyFixes(fixes[])` (shifts `curr` → `prev`, appends trail),
  `reset`, `setStatus`, `select`, `toggleLayer`.
- `src/app/useSourceConnection.ts`: a hook that creates the source from config
  (`registry.ts`), calls `connect()` with handlers that write to the store, and calls
  `disconnect()` in the effect cleanup.
- First version of `FileReplaySource`: fetch + parse, `onSite(...)`, then emit **the
  first fix of each cart** (no time yet).
- `CartLayer.tsx`: one `CircleMarker` per cart at `latest[cartId].curr`.
- Remove the temporary loading code from `App.tsx`.

**Done when:** stations + 2 cart dots visible; data flows file → source → store → map.

**Watch out:** React 18 StrictMode runs effects **twice** in dev (mount → unmount →
mount). If you see data loaded twice or two timers, your `disconnect()` isn't cleaning
up. Make it idempotent and cancel `fetch` with an `AbortController`.

---

### Step 6 — Replay over time (M4)

**Do**
- `src/sources/file/ReplayClock.ts` (pure, injectable `now()`): `play`, `pause`,
  `seek`, `setSpeed`, `time()`. Unit-test it with a fake clock.
- `FileReplaySource` implements `Replayable` (ARCHITECTURE §7.1): a tick every ~100 ms
  (`setInterval` is fine) emits all fixes with `lastT < ts ≤ clock.time()` using a
  moving index; batch them into one `applyFixes` call per tick; at the end set status
  `ended` (or loop).
- Seek backwards → `onReset()` → emit the last 2 fixes per cart before the new time.
- `PlaybackBar.tsx`: shown only if `isReplayable(source)`. Play/pause, speed buttons
  (1×, 2×, 10×, 60×), time slider over `getTimeRange()`, current time as `HH:mm:ss`.
  Keep playback state in the store so the bar and the map agree.

**Done when:** pressing play makes the dots move in sync with the time label; the
slider jumps instantly forwards and backwards; 60× plays a 30-min file in 30 s.

**Watch out:** don't put the replay timer inside a React component. It belongs to the
source. Components only read the store.

---

### Step 7 — The "buses on Yandex Maps" feel (M5)

**Do** (details in ARCHITECTURE §8.2–8.3)
- Smooth movement: in `CartLayer`, keep a `useRef` map of Leaflet marker instances.
  On a new fix, start a `requestAnimationFrame` animation from the currently drawn
  position to the new one over `clamp(Δt_between_fixes / speed, 0.2 s, 2 s)` and call
  `marker.setLatLng()` each frame. No `setState` per frame.
- Heading arrow: a small rotated triangle `divIcon` (CSS `transform: rotate(...)`),
  from `headingDeg` or computed bearing; frozen when the cart moves < 0.5 m.
- `TrailLayer`: polyline of the last ~60 points from `trails[cartId]`.
- `AccuracyLayer`: `Circle` with radius `accuracyM` (metres — Leaflet `Circle` takes
  metres on OSM; on `CRS.Simple`, 1 unit = 1 m, which matches our projection).
- `domain/status.ts`: `online / stale / offline` by age of last fix vs **replay time**.
  Style dots by status.
- Labels: cart name next to the dot, hidden below a zoom level.
- Colors: from `cart.color` or a stable palette by index.

**Done when:** at 1× motion looks continuous (no once-per-second jumps), arrows
point along the route, cart-02 in the example shows a big circle when it falls back to
`ecid-ta`, and a huge one for `cell-id`.

---

### Step 8 — Sidebar and interaction (M6)

**Do**
- `CartList.tsx`: rows with colour dot, name, status, method; search by name/id;
  sort by name or status.
- Selection: click a row or a dot → `select(id)`, the dot gets a ring, the map pans
  to it, `CartDetails.tsx` shows: id, type, last update time, position (x/y and
  lat/lon), accuracy, method, stations used, speed, heading.
- Click a station → tooltip/popup with id, name, height, serial.
- Layer toggles: accuracy, trails, labels, truth (truth only if the file has it).
- Header: site name, source kind and file name, status indicator.

**Done when:** you can find any cart in 2 clicks and the map and list always agree.

---

### Step 9 — Load any file, fail nicely (M7)

**Do**
- `FileDropZone.tsx`: drag-over overlay; on drop read with `FileReader`, create
  `new FileReplaySource({ file })`, switch the app's active source (disconnect the old
  one first). Also a "Open file…" button with `<input type="file">`.
- `ValidationErrors.tsx`: list the `path: message` errors from the parser, max ~20,
  with "show all".
- Floor-plan basemap: test with `"basemap": { "type": "image", "url": "/data/plan.png",
  "widthM": 250, "heightM": 180 }`.
- URL params: `?file=/data/other.json&speed=10&autoplay=1` (handy for demos).
- Optional: `parseCsvFixes.ts` with papaparse + separate `site.json`
  (format in ARCHITECTURE §6.3).

**Done when:** dropping a broken file shows exact errors and keeps the old data;
dropping a good file replaces the scene; the floor-plan scenario shows correctly.

---

### Step 10 — Demo data generator (M8)

You need longer, realistic data than the hand-written example.

**Do**
- `scripts/generate-scenario.ts` (run with `npx tsx scripts/generate-scenario.ts
  --carts 20 --minutes 30 --out public/data/demo-scenario.json`):
  - define 3–5 stations and a few routes (polylines between "workshop", "warehouse",
    "dock");
  - each cart drives a route at 1–3 m/s with stops, 1 fix per second;
  - store the true point as `truth`; add noise to get `position` (e.g. Gaussian, σ
    that grows with distance from the nearest station); set `accuracyM` ≈ 2σ;
  - occasionally drop to `ecid-ta` / `cell-id` with bigger noise; occasionally leave a
    gap of 40 s (to see `offline`).
- Reuse `domain/geo.ts` and validate the output with your own schema before writing.

Optional upgrade (bridges to Stage 0.5): instead of adding noise to the position,
compute RSSI per station with the log-distance model
`RSSI(d) = A − 10·n·lg(d) + noise` (system doc §2.2) and save *measurements*; later a
browser-side `Locator` turns them into fixes. Then you visualise the real algorithm.

**Done when:** a 20-cart × 30-min file loads in < 1 s and plays smoothly at 60×.

---

### Step 11 — Hand-off quality (M8)

**Do**
- Tests green: domain (schemas, geo, interpolate, status), ReplayClock,
  FileReplaySource, 2–3 components.
- `README.md` in the project: how to run, file format (link to ARCHITECTURE §6), how to
  add a source.
- `npm run build` → static `dist/`. Optional Dockerfile: `nginx:alpine` serving `dist/`
  (that's all Stage 0 needs to run on a plant server, no Node in production).
- `WebSocketSource.ts` **stub**: implements `PositionSource`, parses `ServerMessage`
  with zod, reconnects with backoff. Test it against a 20-line mock server
  (`ws` package) that reads the demo file and sends `position` messages. This proves
  the architecture works for live data before the real backend exists.
- Self-hosted tiles: make `basemap.tileUrl` configurable (a closed plant network has no
  internet; see system doc §5.6).

**Done when:** the checklist in §4 passes on a clean clone.

---

## 4. Demo checklist (Stage 0 acceptance)

- [ ] `git clone` → `npm install` → `npm run dev` works with no manual steps.
- [ ] Demo file loads automatically; stations and carts visible on OSM.
- [ ] Play / pause / 1× / 10× / 60× / scrub all work; time label is correct.
- [ ] Dots glide smoothly, arrows show direction, trails follow.
- [ ] Accuracy circles grow when the method degrades (RSSI → E-CID → Cell-ID).
- [ ] A cart with a data gap turns stale, then offline, then comes back.
- [ ] Clicking a cart shows its details; list and map stay in sync.
- [ ] Dropping an invalid file shows readable errors; old scene stays.
- [ ] Same data shows on a floor-plan image (`local` + `image`).
- [ ] `?source=ws` with the mock server moves the dots with **no playback bar** and no
      other code changes.
- [ ] `npm test` and `npm run lint` pass; `npm run build` produces `dist/`.

---

## 5. Risks and how the plan handles them

| Risk | Mitigation |
|---|---|
| File format keeps changing (radio team is still experimenting) | `schemaVersion` + zod + optional fields; CSV adapter; parser is the only place that changes |
| Real positions are noisy, dots jitter | Accuracy circle shows honest uncertainty; smoothing (Kalman) belongs in the engine, not the UI; UI animation already hides 1 Hz steps |
| Site has no GPS reference / indoor | `local` coordinates + floor-plan basemap, no lat/lon needed |
| Closed network, no OSM tiles | Configurable `tileUrl`, `image` and `none` basemaps |
| Too many carts slow the map | Imperative updates, canvas renderer, batching; MapLibre swap isolated to `features/map` |
| Magma integration differs from expectations | Browser never talks to Magma; backend adapter absorbs it (ARCHITECTURE §9) |
| First-timer gets lost in scope | Milestones are independent demos; stop after M4 if needed and you still have a working product |

---

## 6. Questions to settle with the team before Step 2

1. **Who produces the file and in what format?** Agree on the JSON contract
   (ARCHITECTURE §6) — or CSV columns — with whoever computes positions.
2. **Coordinates:** will the engine output local metres (likely) or lat/lon? Where is
   the site origin, and what's the rotation of the site grid vs north?
3. **Basemap:** street map (OSM) or a floor plan of the plant? Do we have the plan as
   PNG/SVG with known dimensions in metres?
4. **Scale:** how many carts and how often (1 Hz?) in the pilot?
5. **Accuracy display:** do we show the circle to dispatchers or only in a dev mode?
6. **Confirm "magama" = Magma** (the LF open-source mobile core). If it's something
   else, only ARCHITECTURE §9 changes.

---

## 7. After Stage 0

Next steps map 1:1 onto the system doc roadmap (Таблица 5):
- **Stage 0.5:** measurement files + browser `Locator` to visualise the algorithm.
- **Stage 1 (Каркас и симулятор):** Node/TS backend with simulator, `WebSocketSource`
  goes live, history tracks via REST, PostgreSQL/PostGIS/TimescaleDB.
- **Stages 2–3:** real radio, MQTT agents, Magma/Open5GS events → event log.
- **Stage 4:** station management, UX polish. **Stage 5:** pilot and accuracy report.

Because of the source abstraction, none of these stages requires rewriting the map,
list, details or playback components built here.
