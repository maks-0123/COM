#!/bin/sh
# Первый запуск: том пустой, продюсеру нужен демо-файл рядом с живым снимком.
set -e
if [ ! -f /app/public/data/demo-scenario.json ]; then
	cp /seed/demo-scenario.json /app/public/data/demo-scenario.json
fi
exec node scripts/live-producer.mjs
