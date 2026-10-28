# Fleet snapshot contract — v1.0

**Status:** draft for review · **Applies to:** MVP 0.1 · **Canonical file:** `web/public/data/fleet.snapshot.example.json`

This document is the producer-facing contract for the file that the React map reads. The full plan and
architecture are in [`Arch/MVP_Plan_and_Architecture.docx`](../Arch/MVP_Plan_and_Architecture.docx);
this page is the short, code-adjacent version for the team that writes the file.

## 1. What the file is

One JSON object, called a **snapshot**, containing the site, the base stations, and the trucks at one moment.
The snapshot is complete, not incremental: one valid file is enough to draw the whole screen.

```
producer (script / backend / simulator)
        │  writes atomically
        ▼
web/public/data/fleet.snapshot.json
        │  GET, same origin, Cache-Control: no-store
        ▼
React SPA → Zod → FleetSnapshot → Leaflet
```

The browser never reads an arbitrary path on disk. The file must be served by the same web server as the app.

## 2. Minimal valid example

```json
{
  "schemaVersion": "1.0",
  "generatedAt": "2026-10-28T13:38:30.000Z",
  "site": {
    "id": "plant-1",
    "name": "Plant 1 — Assembly and logistics",
    "center": { "lat": 55.7558, "lon": 37.6173 },
    "defaultZoom": 17,
    "timeZone": "Europe/Moscow",
    "map": { "mode": "osm" }
  },
  "baseStations": [
    { "id": "bs-01", "name": "BS-01 / North gate", "lat": 55.7562, "lon": 37.6168, "status": "online" }
  ],
  "trucks": [
    {
      "id": "truck-01",
      "name": "Truck 01",
      "lat": 55.7559,
      "lon": 37.6171,
      "updatedAt": "2026-10-28T13:38:28.000Z",
      "status": "moving",
      "accuracyM": 18.5,
      "method": "rssi-multilateration"
    }
  ]
}
```

A complete four-truck example is committed at
[`web/public/data/fleet.snapshot.example.json`](../web/public/data/fleet.snapshot.example.json).

## 3. Top-level fields

| Field | Type | Required | Rules |
|---|---|---|---|
| `schemaVersion` | string | yes | `1.x` for this contract. A major mismatch is a fatal, explicit error. |
| `generatedAt` | ISO 8601 string | yes | When the producer created this snapshot. UTC with `Z` or an explicit offset. |
| `site` | object | yes | Site identity, map centre, zoom, optional time zone and map mode. |
| `baseStations` | array | yes | 0 or more station objects. |
| `trucks` | array | yes | 0 or more truck objects. Empty is valid. |

## 4. Site

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | Stable site ID, e.g. `plant-1`. |
| `name` | string | yes | Shown in the header. |
| `center.lat` | number | yes | WGS84 latitude, −90…90. |
| `center.lon` | number | yes | WGS84 longitude, −180…180. |
| `defaultZoom` | integer | yes | Leaflet zoom, 2…22; 16–18 for a factory. |
| `timeZone` | IANA string | no | e.g. `Europe/Moscow`; default is the browser zone. |
| `map` | object | no | `{ "mode": "osm" }`, `"image"`, or `"blank"`; image mode needs `imageBounds`. |

## 5. Base station

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | Stable, unique within the snapshot, e.g. `bs-01`. |
| `name` | string | yes | Label on the map, e.g. `BS-01 / North gate`. |
| `lat`, `lon` | number | yes | WGS84, same CRS as trucks. |
| `status` | enum | yes | `online`, `offline`, or `maintenance`. |
| `heightM` | number | no | Antenna height in metres; not used for the 2D dot. |

## 6. Truck

| Field | Type | Required | Rules |
|---|---|---|---|
| `id` | string | yes | Stable asset ID, unique in the snapshot. Never use an array index. |
| `name` | string | no | Display name; fall back to `id`. |
| `lat`, `lon` | number | yes | WGS84 position, finite and in range. |
| `updatedAt` | ISO 8601 string | yes | When this truck was measured, not when the file was written. |
| `status` | enum | yes | `moving`, `idle`, `offline`, or `unknown`. |
| `accuracyM` | number | no | Estimated radius in metres, ≥ 0. Absent means unknown, not zero. |
| `method` | string | no | `rssi-multilateration`, `timing-advance`, `cell-id`, etc. Unknown values display raw. |
| `speedMps` | number | no | Metres per second, ≥ 0. |
| `headingDeg` | number | no | 0 ≤ value < 360; 0 = north, clockwise. |
| `zone` | string | no | Optional zone label for future grouping. |
| `batteryPct` | number | no | 0…100; optional and not required for the map. |

## 7. Validation and failure policy

The app validates in two stages:

1. **Envelope** — `schemaVersion`, `generatedAt`, `site`, and the two arrays. An envelope failure rejects the
   whole poll and keeps the previous good snapshot.
2. **Records** — each station and truck is validated individually. An invalid record is skipped and counted;
   the rest of the snapshot still renders.

| Condition | Behaviour | What the dispatcher sees |
|---|---|---|
| File missing / 404 | Fatal on first load; keep previous data later | Error card with URL + Retry, or a banner |
| Invalid JSON | Reject the poll; keep previous data | “Snapshot is not valid JSON” |
| Envelope schema invalid | Reject the poll; keep previous data | “Contract mismatch” + first issue |
| One invalid truck | Skip only that record | “1 record skipped” in data health |
| Duplicate truck ID | Keep first, skip duplicate | “1 duplicate ID” |
| `generatedAt` old | Keep data, mark stale | Amber stale banner with age |
| Clock skew > 5 min | Keep data, warn | Warning in data health |
| Empty `trucks` | Valid empty snapshot | “No trucks in the snapshot” |

## 8. Coordinates, units, time

The canonical UI contract is **WGS84 latitude/longitude in decimal degrees**. Local site metres are fine
for the positioning engine, but convert them upstream; a React component must not know the site origin.

| Quantity | Unit | Convention |
|---|---|---|
| Latitude, longitude | decimal degrees | WGS84; 6 decimals ≈ 0.11 m |
| Accuracy | metres | Radius, not diameter; absent = unknown |
| Speed | metres per second | UI may convert to km/h |
| Heading | degrees | 0 = north, clockwise, `[0, 360)` |
| Timestamps | ISO 8601 | UTC with `Z` or an explicit offset |
| Map circle radius | metres | Leaflet `Circle` radius |

If only local ENU metres exist, convert them before writing the file:

```ts
const R = 6_378_137; // metres
const lat = lat0 + (y / R) * (180 / Math.PI);
const lon = lon0 + (x / (R * Math.cos((lat0 * Math.PI) / 180))) * (180 / Math.PI);
```

Document the origin and the axis convention (`x` = east, `y` = north).

## 9. Atomic writes

A browser polling every second will eventually read a half-written file. Write to a temporary file in the
same directory and rename over the target:

```js
import { writeFile, rename } from 'node:fs/promises';

const target = '/srv/fleet/data/fleet.snapshot.json';
const temp = `${target}.tmp`;

await writeFile(temp, JSON.stringify(snapshot, null, 2), 'utf8');
await rename(temp, target); // atomic on POSIX, same filesystem
```

Keep `fleet.snapshot.previous.json` for diagnostics if the producer crashes.

## 10. Serving and caching

- Serve the file from the **same origin** as the app: `/data/fleet.snapshot.json`.
- Send `Cache-Control: no-store` for `/data/`.
- Do not rely on a query parameter alone; use both `cache: 'no-store'` and a cache-busting `?t=...`.
- Use gzip for JSON; a 100-truck snapshot is ~20–30 KB.
- Do not put secrets, IMSIs, driver names, or credentials in the file. It is readable by anyone who can
  reach the app.

## 11. Versioning

- **Minor** (`1.0` → `1.1`): add an optional field, add an enum value the UI can display raw, relax a rule.
  Old consumers keep working.
- **Major** (`1.x` → `2.0`): rename/remove a required field, change a unit, or change a field's meaning.
  The app refuses the file with a clear message.
- **Additive by default.** Unknown fields are ignored; unknown `method` values are displayed raw.
- Never reuse a field name with a new meaning. Add `zoneName` instead of changing `zone` from a string to an object.

## 12. Producer acceptance checklist

- [ ] The file parses as JSON and matches `schemaVersion: "1.0"`.
- [ ] `generatedAt` and every `updatedAt` are ISO 8601 with `Z` or an offset.
- [ ] Every truck and station has a unique, stable `id`.
- [ ] All coordinates are WGS84 and validated against the site bounds.
- [ ] The file is written with a temporary file + atomic rename.
- [ ] `Cache-Control: no-store` is present in the response.
- [ ] A 100-truck snapshot is under ~50 KB and is produced at the agreed cadence.
- [ ] Stopping the producer makes the UI stale, not silently live.
- [ ] Corrupting one record skips it without blanking the map.
- [ ] The previous good snapshot is kept for diagnostics.

## 13. Why JSON

JSON supports the nested site/stations/trucks object, is native to JavaScript, and can be written by any
producer. CSV is fine as an import format in the producer, but it should be converted to this contract before
the browser sees it. JSON Lines is better for append-only streams, not for a full snapshot that is polled.
