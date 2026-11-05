# Docker-контур карты: что и как устроено

Подробное описание упаковки `cart-tracker-web` в Docker (сделано 2026-11-04).
Краткая шпаргалка — в `cart-tracker-web/README.md`, раздел «Запуск в Docker».

## Исходные условия

Приложение — статический SPA (React + Vite), данные — два JSON-файла:

- `data/demo-scenario.json` — демо-запись, лежит в `public/`, vite копирует в `dist/`;
- `data/live-scenario.json` — живой снимок, **пишется внешним процессом** раз в
  секунду атомарно (tmp + rename), в git не входит.

Из этого следуют три требования к упаковке:

1. Фронтенд не знает, откуда снимок: URL относительные (`data/...`), значит
   nginx должен отдавать оба файла по одним и тем же путям, что и dev-сервер.
2. Живой снимок — двухсторонняя связь: продюсер пишет, браузер читает. В
   контейнерах это общий том.
3. Снимок меняется раз в секунду — кеширование его браузером недопустимо.

## Архитектура: два сервиса и том

```
┌────────────┐   GET data/live-scenario.json    ┌─────────────┐
│  браузер   │ ◄──────────────────────────────► │  web (nginx)│──► /live (том, ro)
└────────────┘                                   └─────────────┘
                                                      ▲
                                                 live-data (именованный том)
                                                      ▲
┌────────────┐   раз в 1 с атомарно                   │
│ producer   │ ───────────────────────────────────────┘
│ (node)     │──► /app/public/data (том, rw)
└────────────┘
```

- `web` — собранный SPA за nginx. Том смонтирован **только на чтение**:
  контейнер, доступный извне, не может испортить данные.
- `producer` — тот же `scripts/live-producer.mjs`, что и в dev-режиме
  (`npm run live`), без изменений кода. Том смонтирован на запись.
- Именованный том `live-data` переживает пересоздание контейнеров:
  `docker compose down && up` не сбрасывает данные (в отличие от
  bind-mount в `public/data`, который на macOS ещё и медленный).

## Dockerfile: почему так

```dockerfile
FROM node:22-alpine AS build        # 1. сборка
FROM nginx:1.27-alpine AS web       # 2. веб-образ (target: web)
FROM node:22-alpine AS producer     # 3. продюсер (target: producer)
```

1. **Ступень `build`**: `npm ci` строго по `package-lock.json` (воспроизводимо,
   без «у меня работает»), затем `npm run build`. Node 22 — потому что Vite 8
   требует Node ≥ 20.19 / 22.12. Alpine — маленький образ, ничего нативного
   в проекте не собирается.
2. **Цель `web`**: nginx + готовый `dist/` + свой `docker/nginx.conf`.
   Никакого node в боевом контейнере — поверхность атаки и размер меньше.
3. **Цель `producer`**: node + скрипт + `demo-scenario.json`, спрятанный в
   `/seed/`. Никаких `node_modules` — скрипт использует только встроенные
   модули (`node:fs/promises`).

Одному Dockerfile две цели — compose собирает каждый сервис своей ступенью
(`target: web` / `target: producer`), дублировать Dockerfile не нужно.

## Два ключа к общему тому

**Ключ 1 — демо-файл при первом запуске.** Продюсер читает демо из той же
директории, куда пишет снимок (`public/data/` от корня проекта). Том при
первом старте пуст → продюсер упадёт на чтении. Решение — семя в образе:
`docker/producer-entrypoint.sh` копирует `/seed/demo-scenario.json` в том,
если его там нет, и только потом запускает node. Копирование однократное,
дальше том самодостаточен.

**Ключ 2 — чтение без затенения.** Если смонтировать том прямо поверх
`.../html/data`, он скроет встроенный в образ `demo-scenario.json` (режим
replay перестанет работать). Поэтому в `web` том смонтирован на `/live`, а
nginx связывает точный путь с файлом в томе:

```nginx
location = /data/live-scenario.json {
    alias /live/live-scenario.json;
    add_header Cache-Control 'no-store' always;   # шаг 3 требований
}
```

`location =` — точное совпадение: только живой снимок идёт из тома,
всё остальное (включая demo) — из образа. `no-store` гарантирует, что
опрос 1 Гц видит свежие данные, а не 304 от прошлой секунды.
`try_files ... /index.html` — страховка для SPA-маршрутов.

## Ошибка, которую поймал при проверке

Первый `docker compose up` упал: `exec: "/entrypoint.sh": permission denied`.
Скрипт в git без бита исполнения. Исправлено в Dockerfile
(`RUN chmod +x /entrypoint.sh`) — так работает на любой свежей checkout,
независимо от того, как git/fs восстановили права.

## Протокол проверки (и что каждый шаг доказывает)

```bash
docker compose up --build -d
curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/        # 200: SPA жив
curl -s http://localhost:8080/data/demo-scenario.json | head -c 100  # demo на месте
curl -s http://localhost:8080/data/live-scenario.json                # generatedAt растёт
curl -sI http://localhost:8080/data/live-scenario.json | grep -i cache-control  # no-store
docker compose down                                                  # стоп, образы остаются
```

Проверено: 200 на `/`, валидный demo-JSON, снимок обновляется раз в секунду
(число отметок растёт), `Cache-Control: no-store` стоит.

## Эксплуатация

```bash
docker compose up -d            # поднять
docker compose logs -f producer # смотреть продюсер
docker compose down             # остановить (том данных сохранится)
docker compose down -v          # остановить И стереть данные
docker compose up --build -d    # после правок кода — пересборка
docker system prune             # если 50 ГБ диска ноутбука начнут таять
```

## Куда дальше встраивается ingest

Когда появится сервис-приёмник готовых координат, он встаёт третьим сервисом
compose, пишет `live-scenario.json` в тот же том `live-data` вместо (или рядом
с) продюсера — `web` менять не придётся: он и не узнает, кто пишет в `/live`.
Продюсер останется как демо-режим для разработки без железа.
