#!/usr/bin/env bash
# Собирает собственную подложку карты для площадки: один файл
# public/basemap/site.pmtiles с векторными данными OpenStreetMap.
#
# Интернет нужен только здесь, один раз. Сайт потом берёт карту из этого
# файла и ни к каким внешним сервисам не обращается.
#
# Нужен pmtiles CLI:  brew install pmtiles
#
# Запуск из папки cart-tracker-web:
#   ./scripts/build-basemap.sh
#   BBOX=37.10,55.90,37.25,56.00 ./scripts/build-basemap.sh   # другая площадка
set -euo pipefail

# Прямоугольник площадки: запад,юг,восток,север (долгота,широта).
# По умолчанию — около 2 км вокруг origin из demo-scenario.json.
BBOX="${BBOX:-37.15,55.93,37.22,55.97}"

# Больше 15 не нужно: на более крупных масштабах векторная карта
# дорисовывается из данных 15-го уровня без потери качества.
MAXZOOM="${MAXZOOM:-15}"

OUT="public/basemap/site.pmtiles"

# Ежедневные сборки всей планеты от Protomaps. Целиком (~140 ГБ) не качаем:
# pmtiles extract забирает по HTTP только кусочки внутри BBOX.
PROTOMAPS_BUILD="${PROTOMAPS_BUILD:-$(curl -fsS https://build-metadata.protomaps.dev/builds.json \
	| python3 -c 'import json,sys; print(json.load(sys.stdin)[-1]["key"])')}"

mkdir -p "$(dirname "$OUT")"
echo "Сборка: $PROTOMAPS_BUILD  область: $BBOX  zoom 0–$MAXZOOM"
pmtiles extract "https://build.protomaps.com/$PROTOMAPS_BUILD" "$OUT" \
	--bbox="$BBOX" --maxzoom="$MAXZOOM"
ls -lh "$OUT"
