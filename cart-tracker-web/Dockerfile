# Многоступенчатая сборка: фронтенд (nginx) и продюсер живого снимка.
# Только npm (pnpm в системе нет), arm64/x86_64 без разницы — чистый JS.

# ---------- сборка фронтенда ----------
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# ---------- веб: статика за nginx ----------
FROM nginx:1.27-alpine AS web
COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

# ---------- продюсер: пишет live-scenario.json в общий том ----------
FROM node:22-alpine AS producer
WORKDIR /app
# Семя демо-данных: при первом старте пустого тома entrypoint скопирует
# demo-scenario.json рядом с живым снимком (продюсер читает его оттуда).
COPY public/data/demo-scenario.json /seed/demo-scenario.json
COPY scripts/live-producer.mjs scripts/live-producer.mjs
COPY docker/producer-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
