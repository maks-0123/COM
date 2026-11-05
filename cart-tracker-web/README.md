# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.

## Запуск в Docker

Контур без Node на хосте: `web` (собранный SPA за nginx) + `producer`
(раз в секунду пишет живой снимок в общий том).

```bash
docker compose up --build -d   # http://localhost:8080
```

Режимы: `/` — демо-запись, `/?source=live` — живые данные продюсера.
Файлы: `Dockerfile` (ступени `web` и `producer`), `docker/nginx.conf`
(живой снимок отдаётся с `Cache-Control: no-store` через общий том),
`docker/producer-entrypoint.sh` (первый старт: копирует демо в пустой том).
