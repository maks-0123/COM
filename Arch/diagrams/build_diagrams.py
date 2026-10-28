from __future__ import annotations

import html
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
FONT = "Arial, Helvetica, sans-serif"

INK = "#0F172A"
MUTED = "#475569"
LINE = "#CBD5E1"
BG = "#F8FAFC"
BLUE = "#1D4ED8"
BLUE_BG = "#DBEAFE"
TEAL = "#0F766E"
TEAL_BG = "#CCFBF1"
AMBER = "#B45309"
AMBER_BG = "#FEF3C7"
ROSE = "#BE123C"
ROSE_BG = "#FFE4E6"
VIOLET = "#6D28D9"
VIOLET_BG = "#EDE9FE"
SLATE = "#334155"
SLATE_BG = "#F1F5F9"
WHITE = "#FFFFFF"


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def text(x: int, y: int, value: str, size: int = 24, weight: str = "normal",
         fill: str = INK, anchor: str = "start", opacity: float = 1.0) -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'opacity="{opacity}">{esc(value)}</text>'
    )


def lines(x: int, y: int, values: list[str], size: int = 22, leading: int = 32,
          weight: str = "normal", fill: str = INK) -> str:
    return "".join(text(x, y + i * leading, v, size, weight, fill) for i, v in enumerate(values))


def rect(x: int, y: int, w: int, h: int, fill: str = WHITE, stroke: str = LINE,
         rx: int = 14, sw: int = 2, dash: str | None = None, opacity: float = 1.0) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"{dash_attr}/>'
    )


def arrow(x1: int, y1: int, x2: int, y2: int, color: str = MUTED, width: int = 3,
          dash: str | None = None, marker: str = "arrow") -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
        f'stroke-width="{width}" marker-end="url(#{marker})"{dash_attr}/>'
    )


def curve_arrow(x1: int, y1: int, x2: int, y2: int, color: str = MUTED,
                width: int = 3, dash: str | None = None) -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    mx = (x1 + x2) // 2
    return (
        f'<path d="M {x1} {y1} C {mx} {y1}, {mx} {y2}, {x2} {y2}" fill="none" '
        f'stroke="{color}" stroke-width="{width}" marker-end="url(#arrow)"{dash_attr}/>'
    )


def defs() -> str:
    return f'''
<defs>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6"
          orient="auto" markerUnits="strokeWidth">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="{MUTED}"/>
  </marker>
  <marker id="arrowBlue" markerWidth="12" markerHeight="12" refX="10" refY="6"
          orient="auto" markerUnits="strokeWidth">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="{BLUE}"/>
  </marker>
  <marker id="arrowAmber" markerWidth="12" markerHeight="12" refX="10" refY="6"
          orient="auto" markerUnits="strokeWidth">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="{AMBER}"/>
  </marker>
  <marker id="arrowTeal" markerWidth="12" markerHeight="12" refX="10" refY="6"
          orient="auto" markerUnits="strokeWidth">
    <path d="M 0 0 L 12 6 L 0 12 z" fill="{TEAL}"/>
  </marker>
  <marker id="dot" markerWidth="10" markerHeight="10" refX="5" refY="5">
    <circle cx="5" cy="5" r="4" fill="{MUTED}"/>
  </marker>
</defs>'''


def svg(width: int, height: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n{defs()}\n'
        f'<rect width="{width}" height="{height}" fill="{WHITE}"/>\n{body}\n</svg>\n'
    )


def save(name: str, width: int, height: int, body: str) -> None:
    svg_path = OUT / f"{name}.svg"
    png_path = OUT / f"{name}.png"
    svg_path.write_text(svg(width, height, body), encoding="utf-8")
    subprocess.run(
        ["rsvg-convert", "-w", str(width * 2), "-h", str(height * 2),
         "-o", str(png_path), str(svg_path)],
        check=True,
    )
    print(f"created {svg_path.name} and {png_path.name}")


def header(title: str, subtitle: str) -> str:
    return (
        text(60, 58, title, 38, "bold")
        + text(60, 98, subtitle, 22, "normal", MUTED)
        + f'<line x1="60" y1="118" x2="1540" y2="118" stroke="{LINE}" stroke-width="2"/>'
    )


# ---------------------------------------------------------------------------
# Figure 1 - MVP context
# ---------------------------------------------------------------------------
def figure_context() -> None:
    b: list[str] = []
    b.append(header(
        "Figure 1. MVP context: one file, one screen, no backend",
        "The browser polls an atomic JSON snapshot; the positioning engine and Magma stay outside this increment.",
    ))
    b.append(rect(60, 140, 330, 270, BLUE_BG, BLUE))
    b.append(text(84, 180, "Coordinate producer", 25, "bold", BLUE))
    b.append(lines(84, 220, [
        "Positioning engine / script",
        "RSSI → distances → position",
        "Writes one JSON snapshot",
        "1 Hz in the demo",
    ], 20, 31))
    b.append(text(84, 382, "Outside this MVP", 18, "bold", BLUE, opacity=0.9))

    # Document shape
    b.append('<path d="M 470 225 h 190 l 40 40 v 145 h -230 z" fill="#FEF3C7" stroke="#B45309" stroke-width="2"/>')
    b.append('<path d="M 660 225 v 40 h 40" fill="none" stroke="#B45309" stroke-width="2"/>')
    b.append(text(488, 268, "fleet.snapshot.json", 18, "bold", AMBER))
    b.append(lines(492, 306, ["schemaVersion: 1.0", "site + stations", "+ trucks", "tmp → rename"], 18, 27))

    b.append(rect(760, 140, 280, 270, TEAL_BG, TEAL))
    b.append(text(784, 180, "Static server", 25, "bold", TEAL))
    b.append(lines(784, 220, [
        "Nginx (prod) / Vite (dev)",
        "GET / → React build",
        "GET /data/…json",
        "Cache-Control: no-store",
        "Same origin → no CORS",
    ], 18, 29))

    b.append(rect(1080, 140, 460, 590, BG, "#94A3B8"))
    b.append(text(1104, 180, "Browser: React SPA", 25, "bold"))
    chips = [
        ("useFleetSnapshot()", "TanStack Query · 1 s polling"),
        ("JsonFileFleetRepository", "fetch + cache: no-store"),
        ("Zod validation", "envelope + each record"),
        ("FleetMapPage / Leaflet", "markers · details · status"),
    ]
    for i, (title, sub) in enumerate(chips):
        y = 205 + i * 95
        b.append(rect(1104, y, 412, 72, WHITE, "#94A3B8", rx=12, sw=1.5))
        b.append(text(1124, y + 29, title, 20, "bold"))
        b.append(text(1124, y + 54, sub, 17, "normal", MUTED))
        if i < len(chips) - 1:
            b.append(arrow(1310, y + 72, 1310, y + 95, MUTED, 2))
    b.append(rect(1104, 595, 412, 62, "#F0FDF4", "#15803D", rx=12, sw=1.5))
    b.append(text(1124, 620, "Status: live / stale / error", 18, "bold", "#166534"))
    b.append(text(1124, 643, "last good snapshot is never discarded", 16, "normal", "#166534"))

    b.append(rect(1080, 770, 330, 80, WHITE, LINE, rx=12, sw=1.5, dash="8 6"))
    b.append(text(1100, 802, "OpenStreetMap tiles", 20, "bold"))
    b.append(text(1100, 828, "dev: public OSM · prod: self-hosted", 16, "normal", MUTED))
    b.append(arrow(1210, 770, 1210, 730, MUTED, 2, dash="6 5"))

    b.append(arrow(390, 300, 470, 300, BLUE, 3))
    b.append(arrow(675, 300, 760, 300, AMBER, 3))
    b.append(arrow(1040, 300, 1080, 300, TEAL, 3))

    b.append(rect(60, 770, 930, 80, SLATE_BG, LINE, rx=12, sw=1.5))
    b.append(text(84, 803, "No backend · no database · no Magma calls from the browser", 20, "bold", SLATE))
    b.append(text(84, 830, "The snapshot file is the only integration point in MVP.", 17, "normal", MUTED))
    save("fig1-context", 1600, 900, "".join(b))


# ---------------------------------------------------------------------------
# Figure 2 - Layers
# ---------------------------------------------------------------------------
def figure_layers() -> None:
    b: list[str] = []
    b.append(header(
        "Figure 2. Frontend layers and the dependency rule",
        "Outer layers know about inner layers. Domain knows nothing about React, Leaflet, fetch, or files.",
    ))
    x, w = 190, 1080
    bands = [
        (160, 130, "Presentation", "#E2E8F0", SLATE,
         ["FleetMapPage", "FleetMap", "TruckDetails", "StatusBanner"]),
        (320, 150, "Application", TEAL_BG, TEAL,
         ["useFleetSnapshot", "selectors", "staleness rules", "diagnostics"]),
        (500, 150, "Domain", BLUE_BG, BLUE,
         ["FleetSnapshot", "Truck / Station", "Zod schemas", "pure rules"]),
        (680, 130, "Infrastructure", AMBER_BG, AMBER,
         ["JsonFileFleetRepository", "HTTP / WebSocket (future)", "Leaflet adapter"]),
    ]
    for y, h, title, fill, stroke, chips in bands:
        b.append(rect(x, y, w, h, fill, stroke, rx=14, sw=2))
        b.append(text(x + 24, y + 36, title, 24, "bold", stroke))
        chip_y = y + 58
        chip_w = (w - 60 - (len(chips) - 1) * 16) // len(chips)
        for i, chip in enumerate(chips):
            cx = x + 24 + i * (chip_w + 16)
            b.append(rect(cx, chip_y, chip_w, 48, WHITE, stroke, rx=9, sw=1.2, opacity=0.95))
            b.append(text(cx + 12, chip_y + 30, chip, 17, "normal", INK))

    b.append(arrow(430, 290, 430, 320, SLATE, 3))
    b.append(arrow(430, 470, 430, 500, TEAL, 3))
    b.append(arrow(1000, 680, 1000, 650, AMBER, 3))

    b.append(rect(1310, 405, 230, 190, WHITE, BLUE, rx=14, sw=2, dash="10 7"))
    b.append(text(1330, 438, "Port", 18, "bold", BLUE))
    b.append(text(1330, 468, "FleetRepository", 20, "bold", INK))
    b.append(lines(1330, 500, ["loadSnapshot()", "→ FleetLoadResult"], 17, 25, fill=MUTED))
    b.append(arrow(1270, 440, 1310, 440, BLUE, 2, dash="7 5", marker="arrowBlue"))
    b.append(arrow(1270, 700, 1330, 595, BLUE, 2, dash="7 5", marker="arrowBlue"))

    b.append(rect(190, 840, 1350, 0, WHITE, WHITE, rx=0, sw=0))
    b.append(text(190, 855, "Composition root (App.tsx) is the only place that chooses JsonFileFleetRepository.", 18, "bold", MUTED))
    save("fig2-layers", 1600, 900, "".join(b))


# ---------------------------------------------------------------------------
# Figure 3 - Sequence
# ---------------------------------------------------------------------------
def figure_sequence() -> None:
    b: list[str] = []
    b.append(header(
        "Figure 3. One polling cycle, including validation and failure behaviour",
        "The UI never parses raw JSON directly; the repository returns a validated snapshot plus diagnostics.",
    ))
    actors = [
        (220, "Producer", BLUE),
        (560, "Static server", TEAL),
        (900, "Browser / React", SLATE),
        (1180, "Zod", VIOLET),
        (1450, "Leaflet map", AMBER),
    ]
    for x, name, color in actors:
        b.append(rect(x - 110, 145, 220, 54, WHITE, color, rx=10, sw=2))
        b.append(text(x, 179, name, 19, "bold", color, "middle"))
        b.append(f'<line x1="{x}" y1="199" x2="{x}" y2="780" stroke="{LINE}" stroke-width="2" stroke-dasharray="8 8"/>')

    # loop frame
    b.append(rect(345, 250, 1025, 330, "none", "#94A3B8", rx=14, sw=1.5, dash="8 6"))
    b.append(text(355, 242, "every 1 s", 17, "bold", MUTED))

    b.append(arrow(220, 285, 560, 285, BLUE, 3, marker="arrowBlue"))
    b.append(text(240, 272, "1. atomic write (tmp → rename)", 17, "normal", BLUE))

    b.append(arrow(560, 345, 900, 345, TEAL, 3, marker="arrowTeal"))
    b.append(text(580, 330, "2. GET /data/fleet.snapshot.json?t=…", 16, "normal", TEAL))

    b.append(arrow(900, 405, 1180, 405, VIOLET, 3, marker="arrow"))
    b.append(text(918, 390, "3. JSON.parse + envelope", 16, "normal", VIOLET))

    b.append(arrow(1180, 465, 900, 465, VIOLET, 3, marker="arrow"))
    b.append(text(918, 450, "4. snapshot + diagnostics", 16, "normal", VIOLET))

    b.append(arrow(900, 525, 1450, 525, AMBER, 3, marker="arrowAmber"))
    b.append(text(918, 510, "5. render / move markers", 16, "normal", AMBER))

    b.append(arrow(900, 600, 900, 650, ROSE, 3))
    b.append(text(918, 635, "6. on error: keep last good snapshot, show banner", 16, "normal", ROSE))

    b.append(rect(380, 690, 850, 66, "#FFF1F2", ROSE, rx=12, sw=1.5))
    b.append(text(400, 718, "Fail soft: a bad file never blanks the map.", 19, "bold", ROSE))
    b.append(text(400, 742, "Invalid single records are skipped and counted; an invalid envelope is a fatal, explicit error.", 16, "normal", MUTED))

    b.append(text(60, 850, "Cache-Control: no-store prevents a proxy or browser from serving yesterday's positions as if they were current.", 17, "normal", MUTED))
    save("fig3-sequence", 1600, 900, "".join(b))


# ---------------------------------------------------------------------------
# Figure 4 - Roadmap
# ---------------------------------------------------------------------------
def figure_roadmap() -> None:
    b: list[str] = []
    b.append(header(
        "Figure 4. Evolution without a rewrite: file → API → Magma → production",
        "The UI and the snapshot contract stay stable; only the source adapter and the server side grow.",
    ))
    cards = [
        (60, "PHASE 0 · NOW", "File MVP", "1–2 weeks", BLUE, BLUE_BG, [
            "JSON snapshot → React",
            "Leaflet map + dots",
            "1 s polling, no backend",
            "One versioned contract",
            "Demo + architecture seam",
        ], "No UI rework"),
        (430, "PHASE 1", "Snapshot API", "1–2 weeks", TEAL, TEAL_BG, [
            "Backend serves the same JSON",
            "File or DB behind it",
            "Auth / CORS ready",
            "Same UI contract",
            "Adapter swap only",
        ], "Repository + backend"),
        (800, "PHASE 2", "Magma + MQTT", "4–6 weeks", AMBER, AMBER_BG, [
            "Truck agent → MQTT",
            "Magma AGW events",
            "Positioning engine",
            "WebSocket stream",
            "Server-side credentials",
        ], "Backend + radio"),
        (1170, "PHASE 3", "Production", "ongoing", VIOLET, VIOLET_BG, [
            "PostGIS / Timescale history",
            "SSO + roles",
            "Geofences + alerts",
            "HA + monitoring",
            "Site calibration",
        ], "Operations"),
    ]
    for x, phase, title, duration, color, fill, bullets, changes in cards:
        b.append(rect(x, 170, 340, 590, fill, color, rx=16, sw=2))
        b.append(text(x + 24, 212, phase, 16, "bold", color))
        b.append(text(x + 24, 254, title, 30, "bold", INK))
        b.append(text(x + 24, 286, duration, 18, "bold", color))
        b.append(f'<line x1="{x+24}" y1="306" x2="{x+316}" y2="306" stroke="{color}" stroke-width="1.5" opacity="0.5"/>')
        for i, bullet in enumerate(bullets):
            b.append(f'<circle cx="{x+34}" cy="{346+i*52}" r="4" fill="{color}"/>')
            b.append(text(x + 50, 353 + i * 52, bullet, 17, "normal", INK))
        b.append(rect(x + 20, 640, 300, 92, WHITE, color, rx=10, sw=1.2, opacity=0.9))
        b.append(text(x + 34, 670, "What changes", 14, "bold", MUTED))
        b.append(text(x + 34, 698, changes, 17, "bold", color))
        b.append(text(x + 34, 720, "What stays: UI + contract", 14, "normal", MUTED))
    for x in (400, 770, 1140):
        b.append(arrow(x, 465, x + 30, 465, MUTED, 3))

    b.append(rect(60, 800, 1450, 58, SLATE_BG, LINE, rx=12, sw=1.5))
    b.append(text(84, 836, "Flexibility test: replace the file with an API without touching FleetMapPage, the domain types, or the markers.", 19, "bold", SLATE))
    save("fig4-roadmap", 1600, 900, "".join(b))


if __name__ == "__main__":
    figure_context()
    figure_layers()
    figure_sequence()
    figure_roadmap()


# ---------------------------------------------------------------------------
# Figure 5 - Target architecture with Magma
# ---------------------------------------------------------------------------
def poly_arrow(points: list[tuple[int, int]], color: str = MUTED, width: int = 3,
               dash: str | None = None, marker: str = "arrow") -> str:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    d = " ".join(f"{'M' if i == 0 else 'L'} {x} {y}" for i, (x, y) in enumerate(points))
    return (
        f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
        f'marker-end="url(#{marker})"{dash_attr}/>'
    )


def figure_target() -> None:
    b: list[str] = []
    b.append(header(
        "Figure 5. Target architecture: Magma and MQTT sit behind a server-side boundary",
        "The browser still consumes only FleetSnapshot; it never holds Magma credentials or calls the core directly.",
    ))

    b.append(rect(60, 180, 300, 150, BLUE_BG, BLUE))
    b.append(text(84, 218, "Truck + on-board agent", 21, "bold", BLUE))
    b.append(lines(84, 252, ["LTE modem", "RSRP / RSRQ / TA", "publishes measurements"], 17, 27))

    b.append(rect(60, 390, 300, 150, TEAL_BG, TEAL))
    b.append(text(84, 428, "Magma core", 21, "bold", TEAL))
    b.append(lines(84, 462, ["AGW + Orchestrator", "SIM / session events", "attach, detach, handover"], 17, 27))

    b.append(rect(60, 610, 300, 110, AMBER_BG, AMBER))
    b.append(text(84, 648, "MQTT broker", 21, "bold", AMBER))
    b.append(text(84, 680, "telemetry/<truck-id>", 17, "normal", MUTED))
    b.append(text(84, 704, "QoS 1 · TLS", 16, "normal", MUTED))

    b.append(rect(450, 150, 720, 650, BG, "#94A3B8"))
    b.append(text(474, 188, "Backend — private network", 23, "bold", SLATE))
    b.append(text(474, 214, "No browser credentials, no direct core access", 16, "normal", MUTED))

    b.append(rect(490, 235, 640, 120, WHITE, VIOLET))
    b.append(text(514, 272, "Ingest service", 21, "bold", VIOLET))
    b.append(text(514, 302, "normalizes events and measurements", 17, "normal", MUTED))
    b.append(text(514, 328, "validates schema, deduplicates", 17, "normal", MUTED))

    b.append(rect(490, 395, 640, 100, WHITE, BLUE))
    b.append(text(514, 432, "Positioning engine", 21, "bold", BLUE))
    b.append(text(514, 464, "RSSI → distances → multilateration → Kalman", 17, "normal", MUTED))

    b.append(rect(490, 535, 640, 100, WHITE, TEAL))
    b.append(text(514, 572, "Snapshot publisher", 21, "bold", TEAL))
    b.append(text(514, 604, "one versioned FleetSnapshot per cycle", 17, "normal", MUTED))

    b.append(rect(490, 665, 300, 100, WHITE, AMBER))
    b.append(text(514, 700, "PostGIS / Timescale", 19, "bold", AMBER))
    b.append(text(514, 730, "history + retention", 16, "normal", MUTED))

    b.append(rect(830, 665, 300, 100, WHITE, ROSE))
    b.append(text(854, 700, "REST + WebSocket", 19, "bold", ROSE))
    b.append(text(854, 730, "auth, rate limits", 16, "normal", MUTED))

    b.append(rect(1240, 260, 300, 340, BG, "#94A3B8"))
    b.append(text(1264, 298, "Browser: React SPA", 21, "bold"))
    b.append(rect(1264, 320, 252, 60, WHITE, "#94A3B8", rx=9, sw=1.2))
    b.append(text(1280, 345, "FleetRepository", 18, "bold"))
    b.append(text(1280, 368, "HTTP / WebSocket adapter", 14, "normal", MUTED))
    b.append(rect(1264, 395, 252, 60, WHITE, "#94A3B8", rx=9, sw=1.2))
    b.append(text(1280, 420, "FleetMapPage", 18, "bold"))
    b.append(text(1280, 443, "domain + status rules", 14, "normal", MUTED))
    b.append(rect(1264, 470, 252, 60, WHITE, "#94A3B8", rx=9, sw=1.2))
    b.append(text(1280, 495, "Leaflet map", 18, "bold"))
    b.append(text(1280, 518, "dots, details, accuracy", 14, "normal", MUTED))
    b.append(text(1264, 566, "HTTPS / WSS · same contract", 15, "bold", BLUE))

    # Data flows
    b.append(poly_arrow([(360, 465), (405, 465), (405, 270), (490, 270)], TEAL, 3, marker="arrowTeal"))
    b.append(text(372, 450, "events", 15, "bold", TEAL))
    b.append(poly_arrow([(360, 665), (430, 665), (430, 315), (490, 315)], AMBER, 3, marker="arrowAmber"))
    b.append(text(382, 650, "measurements", 15, "bold", AMBER))

    b.append(arrow(810, 355, 810, 395, VIOLET, 3))
    b.append(arrow(810, 495, 810, 535, BLUE, 3))
    b.append(poly_arrow([(640, 635), (640, 665)], TEAL, 3, marker="arrowTeal"))
    b.append(poly_arrow([(980, 635), (980, 665)], TEAL, 3, marker="arrowTeal"))
    b.append(poly_arrow([(1130, 715), (1215, 715), (1215, 450), (1240, 450)], ROSE, 3))

    b.append(rect(60, 820, 1460, 58, SLATE_BG, LINE, rx=12, sw=1.5))
    b.append(text(84, 856, "Open5GS can replace Magma behind the same event/measurement adapters. The browser does not change.", 18, "bold", SLATE))
    save("fig5-magma-target", 1600, 900, "".join(b))


if __name__ == "__main__":
    figure_target()
