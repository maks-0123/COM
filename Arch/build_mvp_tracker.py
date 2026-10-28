from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "MVP_Plan_Tracker.xlsx"

# Palette
NAVY = "0F172A"
BLUE = "1D4ED8"
BLUE_SOFT = "DBEAFE"
TEAL = "0F766E"
TEAL_SOFT = "CCFBF1"
AMBER = "B45309"
AMBER_SOFT = "FEF3C7"
ROSE = "BE123C"
ROSE_SOFT = "FFE4E6"
GREEN = "15803D"
GREEN_SOFT = "DCFCE7"
SLATE = "334155"
SLATE_SOFT = "F1F5F9"
LINE = "CBD5E1"
SOFT = "F8FAFC"
WHITE = "FFFFFF"

THIN = Side(style="thin", color=LINE)
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

STATUS_LIST = '"Not started,In progress,Blocked,Done"'
PRIORITY_LIST = '"L,M,H"'

PHASES = [
    ("M0", "Contract and decisions", 7, "2–3 days", "Schema v1 + CRS agreed"),
    ("M1", "Skeleton and shell", 6, "1 day", "App shell + map"),
    ("M2", "Data layer", 10, "2 days", "Domain + file adapter"),
    ("M3", "Map and interaction", 14, "2–3 days", "Dots + selection"),
    ("M4", "States and polish", 10, "2 days", "States + a11y"),
    ("M5", "Tests and handover", 11, "2 days", "Tests + deploy"),
]

TASKS = [
    ("M0-1", "M0", "Contract review with producer and customer", 4, "—", "Frontend + domain", "Not started", "Schema v1 and sample signed off"),
    ("M0-2", "M0", "Coordinate and map-provider decisions", 3, "—", "Frontend + domain", "Not started", "WGS84 confirmed; tiles/site plan chosen"),
    ("M1-1", "M1", "Scaffold Vite + React + TS + lint/test", 3, "—", "Frontend", "Not started", "pnpm dev, lint, test, build work"),
    ("M1-2", "M1", "App shell, providers, error boundary", 3, "M1-1", "Frontend", "Not started", "Blank page with header/footer and no errors"),
    ("M2-1", "M2", "Domain types + Zod schemas + tests", 4, "M0-1", "Frontend", "Not started", "Valid/invalid fixtures behave as specified"),
    ("M2-2", "M2", "JsonFileFleetRepository + typed errors", 4, "M2-1", "Frontend", "Not started", "Fetch, parse, partial failure, 404 covered"),
    ("M2-3", "M2", "useFleetSnapshot + QueryClient", 2, "M2-2", "Frontend", "Not started", "Debug view updates every second"),
    ("M3-1", "M3", "Map shell + station markers", 5, "M1-2", "Frontend", "Not started", "Map centred; stations and labels visible"),
    ("M3-2", "M3", "Truck markers + status + accuracy", 5, "M3-1", "Frontend", "Not started", "Dots move; selected dot has a ring"),
    ("M3-3", "M3", "Truck list + details panel + selection", 4, "M3-2", "Frontend", "Not started", "Map and list select the same object"),
    ("M4-1", "M4", "Loading/empty/stale/error/partial states", 4, "M3-3", "Frontend", "Not started", "Every state can be triggered manually"),
    ("M4-2", "M4", "Responsive layout + accessibility pass", 3, "M4-1", "Frontend + design", "Not started", "1024 px and mobile; keyboard path works"),
    ("M4-3", "M4", "Data health panel + diagnostics", 3, "M4-1", "Frontend", "Not started", "Source, age, counts, skipped records visible"),
    ("M5-1", "M5", "Unit/component/integration tests", 5, "M2-2, M3-3", "Frontend", "Not started", "Test plan from section 9.2 is covered"),
    ("M5-2", "M5", "Production build, Nginx, README, runbook", 4, "M4-2", "Frontend", "Not started", "Deployed URL; docs reviewed"),
    ("M5-3", "M5", "Demo data, rehearsal, handover", 2, "M5-2", "Frontend + product", "Not started", "Demo runs twice without intervention"),
]

ACCEPTANCE = [
    ("AC-01", "Map", "Valid snapshot with 3 stations and 5 trucks renders within 2 s", "Manual + E2E", "Not started", ""),
    ("AC-02", "Freshness", "Replacing the file moves dots without a page reload", "Manual + integration", "Not started", ""),
    ("AC-03", "Selection", "Clicking a dot opens the correct details card", "Component", "Not started", ""),
    ("AC-04", "Resilience", "One invalid record is skipped; the rest render; the count is visible", "Unit + component", "Not started", ""),
    ("AC-05", "Errors", "Missing file shows a fatal error with Retry on first load", "Component", "Not started", ""),
    ("AC-06", "Errors", "Failed refresh keeps last good dots and shows a banner", "Integration", "Not started", ""),
    ("AC-07", "Freshness", "Old generatedAt shows a stale banner even with HTTP 200", "Unit + component", "Not started", ""),
    ("AC-08", "Performance", "100 trucks at 1 Hz remains responsive", "Performance check", "Not started", ""),
    ("AC-09", "Offline", "Tiles blocked: dots, stations, legend, details still work", "Manual", "Not started", ""),
    ("AC-10", "Accessibility", "Keyboard-only selection works through the truck list", "Manual + a11y", "Not started", ""),
    ("CHK-01", "Build", "Lint, typecheck, test, and production build are green", "CI", "Not started", ""),
    ("CHK-02", "Deploy", "Base-path deployment loads assets and data", "Manual", "Not started", ""),
    ("CHK-03", "Cache", "Cache-Control: no-store is present on the snapshot response", "DevTools", "Not started", ""),
    ("CHK-04", "Docs", "README covers run, build, deploy, and data replacement", "Review", "Not started", ""),
    ("CHK-05", "Security", "No secrets in the bundle; app is behind the agreed perimeter", "Review", "Not started", ""),
    ("CHK-06", "Demo", "Demo script rehearsed twice, including the failure drill", "Rehearsal", "Not started", ""),
    ("CHK-07", "Release", "Release tagged v0.1.0 with a visible build stamp", "Release", "Not started", ""),
    ("CHK-08", "Contract", "Example snapshot matches the v1 schema", "Review", "Not started", ""),
    ("CHK-09", "Ops", "Previous good snapshot and rollback path documented", "Review", "Not started", ""),
    ("CHK-10", "Sign-off", "Customer accepts the MVP scope and demo", "Review", "Not started", ""),
]

RISKS = [
    ("Coordinate system mismatch (local metres vs WGS84)", "H", "H", "Freeze CRS; convert in producer; validate ranges; one known-point check", "Dots offset by a constant distance", "Frontend + domain", "Open"),
    ("Stale file served as live", "H", "H", "Check generatedAt, not HTTP status; stale banner; external age check", "HTTP 200 but positions frozen", "Frontend", "Open"),
    ("Scope creep into RSSI/Magma/DB", "H", "H", "Out-of-scope list; change rule; Phase 1/2 backlog", "New must-have in standup", "Product", "Open"),
    ("Map tiles blocked in a closed network", "H", "M", "Site-plan overlay or local tiles; blank map still works", "Grey tiles in the demo", "IT + frontend", "Open"),
    ("Yandex Maps required late", "M", "H", "Isolate Leaflet behind FleetMap; clarify provider on day 1", "API key mentioned after build", "Product", "Open"),
    ("Non-atomic file write", "M", "H", "Temp file + rename; previous snapshot; parse error banner", "Intermittent JSON parse errors", "Integrator", "Open"),
    ("Schema drift between producer and UI", "M", "M", "Version field; Zod; contract review; example file in repo", "Unknown/missing fields", "Frontend + domain", "Open"),
    ("Performance at 1,000+ trucks", "M", "M", "Canvas markers, API/WS, clustering; budget at 100 trucks", "Frame drops / long tasks", "Frontend", "Open"),
    ("Positions exposed on an open URL", "M", "H", "Perimeter auth; no secrets; HTTPS; privacy review", "App reachable from guest network", "Security", "Open"),
    ("Magma integration surprises", "H", "M", "Server-side adapter; Open5GS fallback; spike in Phase 2", "Events missing or API unstable", "Backend", "Open"),
    ("Clock skew / timezone errors", "M", "M", "UTC ISO strings; NTP; future-timestamp warning", "“-3 s ago” or “in 2 hours”", "Frontend + ops", "Open"),
    ("First-timer overengineering", "M", "M", "One port, no Redux, no generic data source; review checklist", "More abstraction than features", "Tech lead", "Open"),
]

ADRS = [
    ("ADR-001", "File-backed static SPA for MVP 0.1", "Accepted", "2026-10-28", "No backend; fastest demo; file is a temporary transport"),
    ("ADR-002", "FleetRepository port with a file adapter", "Accepted", "2026-10-28", "Source can change without touching the UI"),
    ("ADR-003", "Leaflet + OpenStreetMap for the map", "Accepted", "2026-10-28", "No API key; open licence; easy markers and circles"),
    ("ADR-004", "WGS84 lat/lon is the canonical UI contract", "Accepted", "2026-10-28", "No geodesy in components; local metres converted upstream"),
    ("ADR-005", "JSON Schema v1 + Zod at the boundary", "Accepted", "2026-10-28", "Runtime safety; versioned evolution"),
    ("ADR-006", "1 Hz polling, not WebSocket, in MVP", "Accepted", "2026-10-28", "Simple, debuggable, proxy-friendly; upgrade later"),
    ("ADR-007", "No database or history in MVP", "Accepted", "2026-10-28", "Smaller scope; live dots only"),
    ("ADR-008", "Magma only server-side in Phase 2", "Accepted", "2026-10-28", "No credentials or core APIs in the browser"),
]

CONTRACT = [
    ("Top level", "schemaVersion", "string", "yes", "1.x; major mismatch is fatal"),
    ("Top level", "generatedAt", "ISO 8601", "yes", "UTC with Z or offset; when the snapshot was made"),
    ("Top level", "site", "object", "yes", "Site identity and map centre"),
    ("Top level", "baseStations", "array", "yes", "0+ station objects"),
    ("Top level", "trucks", "array", "yes", "0+ truck objects; empty is valid"),
    ("Site", "id", "string", "yes", "Stable site ID"),
    ("Site", "name", "string", "yes", "Header label"),
    ("Site", "center.lat", "number", "yes", "WGS84, -90..90"),
    ("Site", "center.lon", "number", "yes", "WGS84, -180..180"),
    ("Site", "defaultZoom", "integer", "yes", "2..22; 16–18 typical"),
    ("Site", "timeZone", "IANA string", "no", "Default: browser zone"),
    ("Site", "map", "object", "no", "mode osm | image | blank"),
    ("Station", "id", "string", "yes", "Stable, unique"),
    ("Station", "name", "string", "yes", "Map label"),
    ("Station", "lat, lon", "number", "yes", "WGS84"),
    ("Station", "status", "enum", "yes", "online | offline | maintenance"),
    ("Station", "heightM", "number", "no", "Antenna height; not used for 2D"),
    ("Truck", "id", "string", "yes", "Stable, unique; never an array index"),
    ("Truck", "name", "string", "no", "Fallback to id"),
    ("Truck", "lat, lon", "number", "yes", "WGS84"),
    ("Truck", "updatedAt", "ISO 8601", "yes", "When this truck was measured"),
    ("Truck", "status", "enum", "yes", "moving | idle | offline | unknown"),
    ("Truck", "accuracyM", "number", "no", "Radius in metres, >= 0; absent = unknown"),
    ("Truck", "method", "string", "no", "Known values labelled; unknown raw"),
    ("Truck", "speedMps", "number", "no", "Metres per second, >= 0"),
    ("Truck", "headingDeg", "number", "no", "0..<360; 0 = north"),
    ("Truck", "zone", "string", "no", "Future grouping"),
    ("Truck", "batteryPct", "number", "no", "0..100"),
]


def title(ws, cell_range, text, size=18, fill=NAVY, color=WHITE):
    first = cell_range.split(":")[0]
    ws.merge_cells(cell_range)
    c = ws[first]
    c.value = text
    c.font = Font(name="Arial", size=size, bold=True, color=color)
    c.fill = PatternFill("solid", fgColor=fill)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[c.row].height = 34
    for row in ws[cell_range]:
        for cell in row:
            cell.fill = PatternFill("solid", fgColor=fill)


def subtitle(ws, cell_range, text):
    first = cell_range.split(":")[0]
    ws.merge_cells(cell_range)
    c = ws[first]
    c.value = text
    c.font = Font(name="Arial", size=10, color="475569")
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[c.row].height = 28


def section(ws, row, text, last_col=8):
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name="Arial", size=12, bold=True, color=NAVY)
    c.fill = PatternFill("solid", fgColor=BLUE_SOFT)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 24
    for col in range(1, last_col + 1):
        ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=BLUE_SOFT)
    return row + 1


def header_row(ws, row, values):
    for col, value in enumerate(values, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9.5, bold=True, color=WHITE)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        c.border = BORDER
    ws.row_dimensions[row].height = 30
    return row + 1


def body_rows(ws, start_row, rows, widths=None, heights=None, bold_first=False, zebra=True):
    r = start_row
    for i, row in enumerate(rows):
        for col, value in enumerate(row, start=1):
            c = ws.cell(row=r, column=col, value=value)
            c.font = Font(name="Arial", size=9, bold=(bold_first and col == 1), color="1F2937")
            c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
            c.border = BORDER
            if zebra and i % 2 == 1:
                c.fill = PatternFill("solid", fgColor=SOFT)
        if heights:
            ws.row_dimensions[r].height = heights
        r += 1
    if widths:
        for i, width in enumerate(widths, start=1):
            ws.column_dimensions[chr(64 + i)].width = width
    return r


def finish_sheet(ws, last_row, last_col, freeze="A2", landscape=True):
    ws.freeze_panes = freeze
    ws.auto_filter.ref = f"A1:{chr(64 + last_col)}{last_row - 1}"
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.print_title_rows = "1:1"


wb = Workbook()

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
ws = wb.active
ws.title = "Overview"
ws.sheet_properties.tabColor = BLUE
ws.sheet_view.showGridLines = False
for col, width in zip("ABCDEFGH", [26, 22, 18, 18, 26, 8, 12, 26]):
    ws.column_dimensions[col].width = width

title(ws, "A1:H1", "Production truck monitoring — MVP 0.1 plan tracker", 20)
subtitle(ws, "A2:H2", "A one-page dashboard for the two-week, file-backed MVP. The detailed plan and architecture are in Arch/MVP_Plan_and_Architecture.docx.")

r = section(ws, 4, "At a glance", 8)
metrics = [
    ("Duration", "10 working days / 2 calendar weeks"),
    ("Effort", "58 ideal hours + 15% buffer"),
    ("Team", "1 frontend + part-time domain/design"),
    ("MVP scope", "JSON file → React → Leaflet map"),
    ("Out of scope", "RSSI, Magma, MQTT, DB, auth"),
    ("Definition of done", "20 acceptance checks signed"),
]
for label, value in metrics:
    c1 = ws.cell(row=r, column=1, value=label)
    c1.font = Font(name="Arial", size=9.5, bold=True, color=NAVY)
    c1.fill = PatternFill("solid", fgColor=SLATE_SOFT)
    c1.border = BORDER
    c1.alignment = Alignment(vertical="center", indent=1)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    c2 = ws.cell(row=r, column=2, value=value)
    c2.font = Font(name="Arial", size=9.5, color="1F2937")
    c2.border = BORDER
    c2.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    for col in range(2, 5):
        ws.cell(row=r, column=col).border = BORDER
    ws.row_dimensions[r].height = 24
    r += 1

# Phase table on the right
phase_start = 5
for col, value in enumerate(["Phase", "Hours", "Calendar", "Outcome"], start=5):
    c = ws.cell(row=phase_start, column=col, value=value)
    c.font = Font(name="Arial", size=9.5, bold=True, color=WHITE)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.border = BORDER
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
ws.row_dimensions[phase_start].height = 26
for i, (phase, name, hours, calendar, outcome) in enumerate(PHASES, start=phase_start + 1):
    values = [f"{phase} · {name}", hours, calendar, outcome]
    for col, value in enumerate(values, start=5):
        c = ws.cell(row=i, column=col, value=value)
        c.font = Font(name="Arial", size=8.5, color="1F2937", bold=(col == 5))
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 0:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.row_dimensions[i].height = 28

# Hours by phase data for chart
chart_row = 18
ws.cell(row=chart_row, column=1, value="Hours by phase").font = Font(name="Arial", size=12, bold=True, color=NAVY)
for col, value in enumerate(["Phase", "Ideal hours"], start=1):
    c = ws.cell(row=chart_row + 1, column=col, value=value)
    c.font = Font(name="Arial", size=9, bold=True, color=WHITE)
    c.fill = PatternFill("solid", fgColor=NAVY)
    c.border = BORDER
for i, (phase, name, hours, calendar, outcome) in enumerate(PHASES, start=chart_row + 2):
    c1 = ws.cell(row=i, column=1, value=f"{phase} · {name}")
    c2 = ws.cell(row=i, column=2, value=hours)
    for c in (c1, c2):
        c.font = Font(name="Arial", size=9, color="1F2937")
        c.border = BORDER
        c.alignment = Alignment(vertical="center", indent=1)
    c1.fill = PatternFill("solid", fgColor=SOFT if i % 2 == 0 else WHITE)
    c2.fill = PatternFill("solid", fgColor=SOFT if i % 2 == 0 else WHITE)

chart = BarChart()
chart.type = "bar"
chart.style = 10
chart.title = "Ideal hours by phase"
chart.y_axis.title = "Hours"
chart.x_axis.title = None
data = Reference(ws, min_col=2, min_row=chart_row + 1, max_row=chart_row + 1 + len(PHASES))
cats = Reference(ws, min_col=1, min_row=chart_row + 2, max_row=chart_row + 1 + len(PHASES))
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.legend = None
chart.height = 7.5
chart.width = 15
ws.add_chart(chart, "A29")

# Instructions
ins_row = 45
r = section(ws, ins_row, "How to use this tracker", 8)
instructions = [
    "1. Start with the Backlog sheet. Move each task from Not started to In progress to Done. The 58 hours are ideal hours, not calendar hours.",
    "2. Use the Calendar sheet for the two-week sequence. A gate is a demo, not a status meeting.",
    "3. Record evidence in Acceptance as you demonstrate each check. A checked box means demonstrated, not implemented.",
    "4. Review the Risks sheet at every gate. Update probability, impact, and trigger; do not leave a risk owner blank.",
    "5. Keep ADRs current when a decision changes. The code and the document are the source of truth, not the spreadsheet.",
]
for text in instructions:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    c = ws.cell(row=r, column=1, value=text)
    c.font = Font(name="Arial", size=9, color="334155")
    c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
    ws.row_dimensions[r].height = 30
    r += 1

# Status legend
r += 1
ws.cell(row=r, column=1, value="Status legend").font = Font(name="Arial", size=10, bold=True, color=NAVY)
legend = [("Not started", "E2E8F0"), ("In progress", BLUE_SOFT), ("Blocked", ROSE_SOFT), ("Done", GREEN_SOFT)]
for i, (label, fill) in enumerate(legend, start=1):
    c = ws.cell(row=r + 1, column=i, value=label)
    c.fill = PatternFill("solid", fgColor=fill)
    c.font = Font(name="Arial", size=8.5, bold=True, color="334155")
    c.border = BORDER
    c.alignment = Alignment(horizontal="center", vertical="center")

ws.freeze_panes = "A4"

# ---------------------------------------------------------------------------
# Backlog
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Backlog")
ws.sheet_properties.tabColor = TEAL
title(ws, "A1:H1", "Backlog and estimates", 18)
subtitle(ws, "A2:H2", "16 tasks, 58 ideal hours. Status values are validated; keep the Done when column testable.")
header_row(ws, 4, ["ID", "Phase", "Task", "Hours", "Depends on", "Owner", "Status", "Done when"])
row = 5
for task in TASKS:
    for col, value in enumerate(task, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 1))
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        c.border = BORDER
        if row % 2 == 0:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.row_dimensions[row].height = 34
    row += 1
last_data_row = row - 1
# Total
c = ws.cell(row=row, column=1, value="Total")
c.font = Font(name="Arial", size=9, bold=True, color=WHITE)
c.fill = PatternFill("solid", fgColor=NAVY)
c.border = BORDER
ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
for col in range(2, 4):
    ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(row=row, column=col).border = BORDER
c = ws.cell(row=row, column=4, value=f"=SUM(D5:D{last_data_row})")
c.font = Font(name="Arial", size=10, bold=True, color=WHITE)
c.fill = PatternFill("solid", fgColor=NAVY)
c.border = BORDER
c.alignment = Alignment(horizontal="center", vertical="center")
for col in range(5, 9):
    ws.cell(row=row, column=col).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(row=row, column=col).border = BORDER

for col, width in zip("ABCDEFGH", [8, 8, 46, 8, 14, 18, 13, 46]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:H{last_data_row}"

# Validation + formatting
dv = DataValidation(type="list", formula1=STATUS_LIST, allow_blank=False)
ws.add_data_validation(dv)
dv.add(f"G5:G{last_data_row}")
ws.conditional_formatting.add(f"G5:G{last_data_row}", FormulaRule(formula=['$G5="Done"'], fill=PatternFill("solid", fgColor=GREEN_SOFT)))
ws.conditional_formatting.add(f"G5:G{last_data_row}", FormulaRule(formula=['$G5="In progress"'], fill=PatternFill("solid", fgColor=BLUE_SOFT)))
ws.conditional_formatting.add(f"G5:G{last_data_row}", FormulaRule(formula=['$G5="Blocked"'], fill=PatternFill("solid", fgColor=ROSE_SOFT)))

# Phase summary + chart
ws.cell(row=4, column=10, value="Phase").font = Font(name="Arial", size=9, bold=True, color=WHITE)
ws.cell(row=4, column=11, value="Hours").font = Font(name="Arial", size=9, bold=True, color=WHITE)
for col in (10, 11):
    ws.cell(row=4, column=col).fill = PatternFill("solid", fgColor=NAVY)
    ws.cell(row=4, column=col).border = BORDER
for i, (phase, name, hours, calendar, outcome) in enumerate(PHASES, start=5):
    ws.cell(row=i, column=10, value=f"{phase} · {name}").font = Font(name="Arial", size=8.5)
    ws.cell(row=i, column=11, value=f"=SUMIF($B$5:$B${last_data_row},$A${i-1+0},$D$5:$D${last_data_row})")
    for col in (10, 11):
        ws.cell(row=i, column=col).border = BORDER
        ws.cell(row=i, column=col).alignment = Alignment(vertical="center", indent=1)
# Fix phase codes in summary to actual M0..M5
for i, (phase, name, hours, calendar, outcome) in enumerate(PHASES, start=5):
    ws.cell(row=i, column=10, value=phase)
    ws.cell(row=i, column=11, value=f"=SUMIF($B$5:$B${last_data_row},J{i},$D$5:$D${last_data_row})")

for col, width in zip("JK", [18, 10]):
    ws.column_dimensions[col].width = width

# ---------------------------------------------------------------------------
# Calendar
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Calendar")
ws.sheet_properties.tabColor = AMBER
title(ws, "A1:D1", "Two-week calendar", 18)
subtitle(ws, "A2:D2", "Every day ends with something that can be shown. Gates are demos, not status meetings.")
header_row(ws, 4, ["Day", "Focus", "Output", "Gate"])
calendar = [
    ("1", "Contract review; scaffold; map shell", "Schema v1 agreed; Vite app; Leaflet map with site centre", "G0: contract frozen"),
    ("2", "Domain types, Zod, sample file, repository", "Validated snapshot in tests; raw debug view", "—"),
    ("3", "Polling, station markers, truck dots", "Moving dots from the file; last update time", "G1: first dots"),
    ("4", "Selection, details, status colours", "Click a dot or list row; card and accuracy circle", "—"),
    ("5", "Error, empty, stale states; review", "Demo 1; issue list; scope check", "G2: usable screen"),
    ("6", "Responsive layout, accessibility, diagnostics", "Mobile/desktop; keyboard list; data health", "—"),
    ("7", "Unit, component, integration tests", "Test suite green; failure cases covered", "—"),
    ("8", "Build, Nginx, README, runbook", "Release candidate deployed at a real URL", "G3: RC"),
    ("9", "Bugfix, performance, demo data, rehearsal", "Polished demo; 100-truck check", "—"),
    ("10", "Customer demo, handover, tag", "Accepted MVP; v0.1.0; backlog for Phase 1", "G4: done"),
]
row = 5
for i, item in enumerate(calendar):
    for col, value in enumerate(item, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 1 or col == 4))
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 1:
            c.fill = PatternFill("solid", fgColor=SOFT)
    gate = item[3]
    if gate != "—":
        ws.cell(row=row, column=4).fill = PatternFill("solid", fgColor=AMBER_SOFT)
    ws.row_dimensions[row].height = 36
    row += 1
for col, width in zip("ABCD", [8, 40, 52, 22]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"

# ---------------------------------------------------------------------------
# Acceptance
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Acceptance")
ws.sheet_properties.tabColor = GREEN
title(ws, "A1:F1", "Acceptance and release checklist", 18)
subtitle(ws, "A2:F2", "A checked box means demonstrated, not implemented. Record evidence or a link in the last column.")
header_row(ws, 4, ["ID", "Area", "Criterion", "How verified", "Status", "Evidence / notes"])
row = 5
for i, item in enumerate(ACCEPTANCE):
    for col, value in enumerate(item, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 1))
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 1:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.row_dimensions[row].height = 30
    row += 1
for col, width in zip("ABCDEF", [9, 14, 58, 20, 13, 40]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:F{row-1}"
dv = DataValidation(type="list", formula1=STATUS_LIST, allow_blank=False)
ws.add_data_validation(dv)
dv.add(f"E5:E{row-1}")
ws.conditional_formatting.add(f"E5:E{row-1}", FormulaRule(formula=['$E5="Done"'], fill=PatternFill("solid", fgColor=GREEN_SOFT)))
ws.conditional_formatting.add(f"E5:E{row-1}", FormulaRule(formula=['$E5="In progress"'], fill=PatternFill("solid", fgColor=BLUE_SOFT)))
ws.conditional_formatting.add(f"E5:E{row-1}", FormulaRule(formula=['$E5="Blocked"'], fill=PatternFill("solid", fgColor=ROSE_SOFT)))

# ---------------------------------------------------------------------------
# Risks
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Risks")
ws.sheet_properties.tabColor = ROSE
title(ws, "A1:H1", "Risk register", 18)
subtitle(ws, "A2:H2", "P = probability, I = impact, Score = 1–9. Review at every gate; every risk needs an owner.")
header_row(ws, 4, ["Risk", "P", "I", "Score", "Mitigation", "Trigger", "Owner", "Status"])
row = 5
for i, item in enumerate(RISKS):
    risk, p, imp, mitigation, trigger, owner, status = item
    values = [risk, p, imp, None, mitigation, trigger, owner, status]
    for col, value in enumerate(values, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 1))
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 1:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.cell(row=row, column=4, value=f'=IF(B{row}="H",3,IF(B{row}="M",2,1))*IF(C{row}="H",3,IF(C{row}="M",2,1))')
    ws.cell(row=row, column=4).font = Font(name="Arial", size=10, bold=True, color=NAVY)
    ws.cell(row=row, column=4).alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 40
    row += 1
last_risk = row - 1
for col, width in zip("ABCDEFGH", [46, 6, 6, 8, 50, 30, 18, 12]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:H{last_risk}"
dv_pi = DataValidation(type="list", formula1=PRIORITY_LIST, allow_blank=False)
ws.add_data_validation(dv_pi)
dv_pi.add(f"B5:C{last_risk}")
ws.conditional_formatting.add(f"D5:D{last_risk}", CellIsRule(operator="greaterThanOrEqual", formula=["9"], fill=PatternFill("solid", fgColor=ROSE_SOFT), font=Font(color=ROSE, bold=True)))
ws.conditional_formatting.add(f"D5:D{last_risk}", CellIsRule(operator="between", formula=["6", "8"], fill=PatternFill("solid", fgColor=AMBER_SOFT), font=Font(color=AMBER, bold=True)))
ws.conditional_formatting.add(f"D5:D{last_risk}", CellIsRule(operator="lessThanOrEqual", formula=["4"], fill=PatternFill("solid", fgColor=GREEN_SOFT), font=Font(color=GREEN, bold=True)))

# ---------------------------------------------------------------------------
# ADRs
# ---------------------------------------------------------------------------
ws = wb.create_sheet("ADRs")
ws.sheet_properties.tabColor = "6D28D9"
title(ws, "A1:E1", "Architecture decision records", 18)
subtitle(ws, "A2:E2", "Short, dated decisions. Update the log when a decision changes; do not leave it to memory.")
header_row(ws, 4, ["ADR", "Decision", "Status", "Date", "Consequence"])
row = 5
for i, item in enumerate(ADRS):
    for col, value in enumerate(item, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 1))
        c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 1:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.row_dimensions[row].height = 34
    row += 1
for col, width in zip("ABCDE", [11, 46, 12, 13, 58]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"

# ---------------------------------------------------------------------------
# Contract
# ---------------------------------------------------------------------------
ws = wb.create_sheet("Contract")
ws.sheet_properties.tabColor = "0891B2"
title(ws, "A1:E1", "Snapshot contract v1.0 — field reference", 18)
subtitle(ws, "A2:E2", "The complete contract is docs/data-contract.md. This sheet is a quick field lookup for the producer.")
header_row(ws, 4, ["Section", "Field", "Type", "Required", "Rules"])
row = 5
for i, item in enumerate(CONTRACT):
    for col, value in enumerate(item, start=1):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Arial", size=9, color="1F2937", bold=(col == 2))
        c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
        c.border = BORDER
        if i % 2 == 1:
            c.fill = PatternFill("solid", fgColor=SOFT)
    ws.row_dimensions[row].height = 26
    row += 1
for col, width in zip("ABCDE", [14, 20, 14, 10, 70]):
    ws.column_dimensions[col].width = width
ws.freeze_panes = "A5"
ws.auto_filter.ref = f"A4:E{row-1}"

# Page setup for all sheets
for ws in wb.worksheets:
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_options.horizontalCentered = True
    ws.page_margins.left = 0.3
    ws.page_margins.right = 0.3
    ws.page_margins.top = 0.4
    ws.page_margins.bottom = 0.4

wb.save(OUT)
print(f"Saved {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")
