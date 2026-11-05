---
name: 6g-magama-mvp
description: "Работа в репозитории 6g-magama-mvp — MVP мониторинга производственных тележек (React/TS/Vite, карта Leaflet) с перспективой Magma LTE-ядра. Использовать при любых задачах в этом репозитории: правка кода cart-tracker-web, изменение контракта данных ScenarioFile, работа с документами Arch/, исследование Magma (Orc8r/AGW/eNodeB), подготовка ingest-сервиса, коммиты и релизы проекта."
---

# 6g-magama-mvp

MVP мониторинга тележек: приложение `cart-tracker-web` (React + TS + Vite) рисует тележки на карте Leaflet из JSON-снимка `ScenarioFile`. Magma — будущий источник данных, не интерфейс; NMS Magma не модифицируем.

Корень репозитория: `/Users/maksimromanuta/Documents/work_on_etalon/6g-magama-mvp` (каноничное имя папки — с опечаткой «magama», так и использовать).

## Перед работой прочитать (по порядку)

1. `<repo>/AGENTS.md` — команды, стиль, границы, definition of done. Авторитетный источник правил.
2. `<repo>/docs/handoff-context.md` — что сделано, принятые решения, контракт данных, роадмап, открытые вопросы.
3. `<repo>/docs/data-contract.md` — НЕ считать актуальным: документ устарел (описывает старый `FleetSnapshot`). Актуальный контракт — `cart-tracker-web/src/domain/types.ts` и `schemas.ts`.

## Команды (из корня репозитория)

```bash
cd cart-tracker-web
npm test          # vitest, 63 теста — обязательно перед сдачей
npm run build     # tsc -b && vite build — обязательно перед сдачей
npm run lint      # oxlint
npm run dev       # dev-сервер
npm run live      # демо-продюсер живого снимка (второй терминал)
```

pnpm в системе нет — только npm.

## Жёсткие правила (нарушение = порча артефактов)

- `keys/`, `.env*` — не читать, не коммитить, не выводить содержимое в ответ.
- `Arch/*.docx`, `Arch/*.xlsx` — бинарные артефакты: править только через `Arch/build_*.py`, не вручную и не через офисные скиллы.
- `cart-tracker-web/src/calculate_metrik.rs` — случайный пустой файл, не трогать и не тиражировать.
- Разрыв 6 с у `cart-02` в демо-данных — намеренная демонстрация состояния «нет данных», не баг; не «чинить».
- `public/data/demo-scenario.json` менять только вместе со схемой и фикстурой `src/domain/__fixtures__/scenario.example.json`.
- Коммиты — по-русски, коротко, одна мысль на коммит.

## Стиль кода

Табы, без точек с запятой, одинарные кавычки, комментарии по-русски. `strict` в tsconfig выключен — не оставлять неявных `any`. `domain/` не импортирует React и Leaflet. Новая логика — с тестом рядом (`*.test.ts`); тесты не переписывать под код, если расхождение означает ошибку в коде.

## Definition of done

1. `npm test` и `npm run build` зелёные.
2. Изменение домена или парсера покрыто тестом.
3. Публичные типы не расширены без необходимости.
4. Контракт изменился → привести `docs/data-contract.md` к фактическому `ScenarioFile`.

## Роадмап (handoff-context.md, раздел 8)

Этап 1 (карта, живой режим, устаревание) — готово. Далее: этап 2 — ingest (приём координат → `ScenarioFile`); этап 3 — лаборатория Orc8r (k3s/minikube, Ubuntu 22.04, Postgres, Helm-чарт); этап 4 — AGW + eNodeB + мультилатерация. Charmed Magma не использовать (архив с 2023) — путь: оригинальная Magma 1.8 через Helm.

## Сопутствующие навыки

- `webapp-building` — заметные правки UI/карты: сборка, самопроверка, мобильная адаптация.
- `kimi-pdf` — точечное извлечение из PDF по Magma: `../Books/WP_Implications_of_Magma_Architecture_092822.pdf`, `../Books/arXiv-2022 Building Flexible, Low-Cost Wireless Access Networks With Magma csNI-2209.10001v1.pdf`.
- `scholar` — поиск работ по RSSI/TA-мультилатерации и LTE-позиционированию.
- `deep-research` — этапы 3–4: развёртывание Orc8r, сравнение вариантов.
- `kimi-word` / `kimi-excel` — только новые документы вне `Arch/`; `kimi-slides` — презентации по проекту.
