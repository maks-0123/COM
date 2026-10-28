from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_diagrams import (  # noqa: E402
    BLUE, BLUE_BG, TEAL, TEAL_BG, AMBER, AMBER_BG, MUTED, LINE, BG, WHITE,
    INK, SLATE, SLATE_BG, text, lines, rect, arrow, header, save, FONT,
)


def context_ru() -> None:
    b: list[str] = []
    b.append(header(
        "Рисунок 1. Контекст MVP: один файл, один экран, без бэкенда",
        "Браузер раз в секунду читает атомарный JSON-снимок; движок позиционирования и Magma остаются вне этого инкремента.",
    ))
    b.append(rect(60, 140, 330, 270, BLUE_BG, BLUE))
    b.append(text(84, 180, "Источник координат", 23, "bold", BLUE))
    b.append(lines(84, 220, [
        "Движок позиционирования / скрипт",
        "RSSI → расстояния → позиция",
        "Пишет один JSON-снимок",
        "1 Гц в демо",
    ], 18, 31))
    b.append(text(84, 382, "Вне границ MVP", 17, "bold", BLUE, opacity=0.9))

    b.append('<path d="M 470 225 h 190 l 40 40 v 145 h -230 z" fill="#FEF3C7" stroke="#B45309" stroke-width="2"/>')
    b.append('<path d="M 660 225 v 40 h 40" fill="none" stroke="#B45309" stroke-width="2"/>')
    b.append(text(488, 268, "fleet.snapshot.json", 18, "bold", AMBER))
    b.append(lines(488, 306, ["schemaVersion: 1.0", "площадка + станции", "+ тележки", "tmp → rename"], 17, 27))

    b.append(rect(760, 140, 280, 270, TEAL_BG, TEAL))
    b.append(text(784, 180, "Статический сервер", 22, "bold", TEAL))
    b.append(lines(784, 220, [
        "Nginx (прод) / Vite (дев)",
        "GET / → сборка React",
        "GET /data/…json",
        "Cache-Control: no-store",
        "Тот же origin → без CORS",
    ], 16, 29))

    b.append(rect(1080, 140, 460, 590, BG, "#94A3B8"))
    b.append(text(1104, 180, "Браузер: React SPA", 23, "bold"))
    chips = [
        ("useFleetSnapshot()", "TanStack Query · опрос 1 Гц"),
        ("JsonFileFleetRepository", "fetch + cache: no-store"),
        ("Валидация Zod", "конверт + каждая запись"),
        ("FleetMapPage / Leaflet", "маркеры · карточка · статус"),
    ]
    for i, (title, sub) in enumerate(chips):
        y = 205 + i * 95
        b.append(rect(1104, y, 412, 72, WHITE, "#94A3B8", rx=12, sw=1.5))
        b.append(text(1124, y + 29, title, 18, "bold"))
        b.append(text(1124, y + 54, sub, 15, "normal", MUTED))
        if i < len(chips) - 1:
            b.append(arrow(1310, y + 72, 1310, y + 95, MUTED, 2))
    b.append(rect(1104, 595, 412, 62, "#F0FDF4", "#15803D", rx=12, sw=1.5))
    b.append(text(1124, 620, "Статус: live / stale / error", 16, "bold", "#166534"))
    b.append(text(1124, 643, "последний хороший снимок не теряется", 14, "normal", "#166534"))

    b.append(rect(1080, 770, 330, 80, WHITE, LINE, rx=12, sw=1.5, dash="8 6"))
    b.append(text(1100, 802, "Тайлы OpenStreetMap", 18, "bold"))
    b.append(text(1100, 828, "демо: публичный OSM · прод: свой сервер", 14, "normal", MUTED))
    b.append(arrow(1210, 770, 1210, 730, MUTED, 2, dash="6 5"))

    b.append(arrow(390, 300, 470, 300, BLUE, 3))
    b.append(arrow(700, 300, 760, 300, AMBER, 3))
    b.append(arrow(1040, 300, 1080, 300, TEAL, 3))

    b.append(rect(60, 770, 930, 80, SLATE_BG, LINE, rx=12, sw=1.5))
    b.append(text(84, 803, "Без бэкенда · без БД · браузер не вызывает Magma", 18, "bold", SLATE))
    b.append(text(84, 830, "Файл-снимок — единственная точка интеграции в MVP.", 15, "normal", MUTED))
    save("fig1-context-ru", 1600, 900, "".join(b))


if __name__ == "__main__":
    context_ru()
