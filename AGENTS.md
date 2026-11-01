# 6g-magama-mvp — инструкции для агента

MVP мониторинга производственных тележек: React-приложение читает JSON-сценарий
с координатами и рисует станции и тележки на карте Leaflet. Координаты приходят
готовыми; RSSI, мультилатерация, Magma и MQTT в этот инкремент не входят.

## Команды

Работать из каталога `cart-tracker-web/`. Пакетный менеджер — npm (pnpm в системе нет).

| Задача | Команда |
|---|---|
| тесты | `npm test` (vitest, 63 теста) |
| сборка | `npm run build` (`tsc -b && vite build`) |
| линт | `npm run lint` (oxlint) |
| dev-сервер | `npm run dev` (vite) |
| один тест | `npx vitest run src/domain/geo.test.ts` |

Перед сдачей задачи обязательны `npm test` и `npm run build`.

## Структура

```
cart-tracker-web/src/
  app/        App.tsx — загрузка сценария и композиция экрана
  domain/     types.ts, schemas.ts (zod), geo.ts, статусы, интерполяция
  features/   map/ (MapView + слои), carts/, loader/, playback/
  sources/    PositionSource, file/ (парсеры), websocket/
  store/      zustand-состояние
public/data/demo-scenario.json   рабочий сценарий
```

`sources/file/` умеет проигрывать запись: `FileReplaySource` + `ReplayClock`,
зациклено, в тестах — ручные часы. `PollingFileSource` раз в секунду опрашивает
снимок (`/?source=live`), режим выбирает `registry`. `WebSocketSource`, `store`
и панели `carts/`, `playback/` — пока заглушки. Демо-продюсер для живого режима:
`npm run live` (пишет `public/data/live-scenario.json`).

## Контракт данных

- `src/domain/types.ts` — типы; `src/domain/schemas.ts` — zod-схема `ScenarioFile`
  (`schemaVersion: 1`, поля `site`, `stations`, `carts`, `fixes`).
- `generatedAt` — необязательное время сборки снимка (ISO-8601); его пишет
  продюсер, поле зарезервировано под проверку свежести снимка.
- Парсер `parseJsonScenario` не бросает исключений: возвращает `{ ok, errors }`,
  отметки сортируются по времени.
- `docs/data-contract.md` устарел (описывает `FleetSnapshot` 1.0 с `baseStations`).
  При изменении схемы — привести документ к фактическому `ScenarioFile`.
- `public/data/demo-scenario.json` менять только вместе со схемой и фикстурой
  `src/domain/__fixtures__/scenario.example.json`.
- Устаревание: порог `STALE_AFTER_MS` в `src/domain/status.ts` (2.5 с). В демо
  у `cart-02` разрыв 6 с — так видно состояние «нет данных»; не «чинить» его.

## Стиль

- табы, без точек с запятой, одинарные кавычки; комментарии по-русски;
- `strict` в tsconfig не включён — не оставлять неявных `any`;
- `domain/` не импортирует React и Leaflet;
- новая логика — с тестом рядом (`*.test.ts`); тесты не переписывать под код,
  если расхождение означает ошибку в коде.

## Границы

- `Arch/*.docx`, `Arch/*.xlsx` — бинарные артефакты: править только через
  `Arch/build_*.py` и `Arch/diagrams/build_diagrams.py`, не руками.
- `keys/`, `.env*` — не читать, не коммитить, не выводить в ответ.
- Не добавлять файлы вне структуры: в `src/` уже лежит случайный пустой
  `calculate_metrik.rs`, его не трогать и не тиражировать.
- Сообщения коммитов — по-русски, коротко, одна мысль на коммит.

## Definition of done

1. `npm test` и `npm run build` зелёные.
2. Изменение домена или парсера покрыто тестом.
3. Публичные типы не расширены без необходимости.
4. Документация обновлена, если изменился контракт данных.
