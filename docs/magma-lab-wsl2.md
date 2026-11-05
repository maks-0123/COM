# Лаборатория Magma на ноутбуке (Windows 10 → WSL2 → Docker)

План действий для поднятия Orc8r + NMS (Magma v1.8.0) на ноутбуке
12 ГБ ОЗУ / 50 ГБ диска. Без Kubernetes. Составлен 2026-11-05.

Цель этапа — научиться пользоваться Magma: NMS, абоненты (SIM/IMSI),
северный REST API, и подготовить почву для собственных сервисов.
Координаты тележек в этот этап не входят: они приходят готовыми
и подключаются к карте отдельно (см. `docs/docker-cart-tracker.md`).

## Фаза 0. Подготовка Windows 10 (30–60 минут)

1. **Виртуализация.** Диспетчер задач → Производительность → ЦП →
   «Виртуализация: Включено». Если выключено — VT-x/AMD-V в BIOS.
2. **WSL2.** PowerShell от администратора:
   ```powershell
   wsl --install
   wsl --set-default-version 2
   ```
   На старых сборках Win10 может потребоваться ручной апдейт ядра WSL2
   (wsl_update_x64.msi с сайта Microsoft) — следовать подсказкам `wsl --install`.
3. **Память WSL2.** Файл `C:\Users\<имя>\.wslconfig`:
   ```ini
   [wsl2]
   memory=9GB          # не больше: хосту оставить 3 ГБ
   processors=4
   swap=4GB            # страховка на время сборки Magma
   ```
4. **Диск WSL2.** По умолчанию vhdx живёт на системном диске. Если там тесно —
   перенести заранее (экспорт/импорт дистрибутива), пока он маленький:
   ```powershell
   wsl --shutdown
   wsl --export Ubuntu D:\backup\ubuntu.tar
   wsl --unregister Ubuntu
   wsl --import Ubuntu D:\wsl\Ubuntu D:\backup\ubuntu.tar
   ```
5. **Ubuntu 22.04** — из Microsoft Store, внутри неё:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
6. **Docker Desktop** — установить, в настройках включить **WSL2 backend**
   и интеграцию с дистрибутивом Ubuntu. Проверка из Ubuntu:
   ```bash
   docker run --rm hello-world
   ```

Контрольная точка: `docker version` без ошибок из консоли Ubuntu.

## Фаза 1. Magma v1.8.0 (вечер, в основном ждём сборку)

Все команды — внутри Ubuntu. Источник шагов: официальные скрипты репозитория
magma + проверенные внешние гайды (ссылки в конце).

1. **Исходники:**
   ```bash
   git clone https://github.com/magma/magma.git
   cd magma && git checkout v1.8.0
   export MAGMA_ROOT=$PWD
   ```
2. **Сертификаты** (домен `magma.test` — локальное имя, самоподписанные):
   ```bash
   mkdir -p ~/secrets/certs && cd ~/secrets/certs
   bash $MAGMA_ROOT/orc8r/cloud/deploy/scripts/self_sign_certs.sh magma.test
   bash $MAGMA_ROOT/orc8r/cloud/deploy/scripts/create_application_certs.sh magma.test
   mkdir -p $MAGMA_ROOT/.cache/test_certs/
   cp -r * $MAGMA_ROOT/.cache/test_certs/ && chmod -R +r $MAGMA_ROOT/.cache/test_certs/
   ```
3. **Сборка контейнеров Orc8r** — самый долгий шаг, ~30 минут, пик по памяти:
   ```bash
   cd $MAGMA_ROOT/orc8r/cloud/docker
   ./build.py --all
   ```
4. **Правки compose перед запуском** (`docker-compose.yml` в той же папке):
   - если сертификаты делали не на `magma.test` — заменить домен;
   - ограничить логи (инаже MariaDB/Prometheus заполнят диск):
     каждому сервису добавить
     ```yaml
     logging:
       driver: json-file
       options: { max-size: "100m", max-file: "5" }
     ```
   - `restart: always` — по желанию.
   - **Метрики не поднимать**: пропустить флаги Elasticsearch/Kibana/
     Prometheus (`run.py` без `--metrics` или отключить сервисы в compose) —
     на 12 ГБ ОЗУ они лишние.
5. **Запуск backend:**
   ```bash
   ./run.py
   docker ps   # почти все контейнеры Up (orc8r-test может быть остановлен — ок)
   ```
6. **NMS** (веб-админка) — отдельный compose:
   ```bash
   cd $MAGMA_ROOT/nms
   # известная правка для нового nginx: в docker/docker_ssl_proxy/proxy_ssl.conf
   # заменить "listen 443;" + "ssl on;" на одну строку "listen 443 ssl;"
   docker-compose up -d
   bash scripts/dev_setup.sh     # организация по умолчанию и админ
   ```
7. **Имена хостов.** Windows: `C:\Windows\System32\drivers\etc\hosts`
   (wildcard не поддерживается — добавлять имена по мере запросов):
   ```
   127.0.0.1 magma.test
   127.0.0.1 api.magma.test
   127.0.0.1 nms.magma.test
   ```

Контрольная точка: из Windows-браузера открыть NMS по адресу гайда
(обычно `https://localhost` или `https://magma.test:443`), принять
самоподписанный сертификат, войти под admin из `dev_setup.sh`.
Контроллер API проверяется: `curl -k https://api.magma.test/v1/networks`.

## Фаза 2. Учимся (цель этапа)

По нарастающей, каждый пункт — отдельное мини-занятие:

1. **NMS:** создать сеть (LTE), посмотреть дашборды. NMS не модифицируем —
   это чужой интерфейс (принцип из handoff-context).
2. **Абоненты:** добавить тестовых подписчиков (SIM/IMSI). IMSI совпадают
   с `carts[].imsi` из контракта карты — заложить реальные диапазоны сразу.
3. **Северный API:** тот же NMS — тонкая оболочка над REST. Погонять
   `curl -k --cert admin_operator.pem --key admin_operator.key.pem`
   против `/v1/...` — именно через этот API в будущем подключаются
   собственные сервисы.
4. **Встраивание карты:** в репозитории уже есть embed-режим
   (`?embed=1&data=<url>`, коммит 2fee35c) — зашить карту в NMS как
   iframe-виджет, когда появится живой источник координат.
5. **Первый собственный сервис Magma:** набросок микросервиса, читающего
   northbound API (состояние шлюзов/абонентов) — паттерн «добавлять свои
   сервисы», ради которого всё и затевается.

## Фаза 3. AGW и радио (позже, не на этом ноутбуке)

AGW требует Linux с **двумя сетевыми портами** (S1 к вышке и SGi в сеть) —
ноутбук с Windows+WSL не подходит. Когда дойдёт: отдельная машина
с Ubuntu, пакетная или контейнерная установка AGW 1.8, регистрация
в Orc8r по hardware ID, затем eNodeB/модемы. До этого момента Orc8r+NMS —
полноценная учебная площадка и без AGW.

## Риски и как их гасить

| Симптом | Причина | Лечение |
|---|---|---|
| Сборка умирает по памяти | build.py параллелит тяжело | swap из `.wslconfig`, повторить `./build.py --all` |
| Диск тает | логи контейнеров, образы | лимиты логов (шаг 4), `docker system prune` |
| Контейнер в restart loop | обычно сертификаты/домен | `docker logs <имя>`; сверить домен в compose с сертификатами |
| NMS не открывается из браузера | hosts/порты/proxy_ssl.conf | проверить hosts, правку nginx из шага 6 |
| WSL «съел» память хоста | лимит не задан | `.wslconfig` из фазы 0, `wsl --shutdown` |

## Источники шагов

- Официальный репозиторий: https://github.com/magma/magma (ветка v1.8.0),
  каталоги `orc8r/cloud/docker` и `nms`.
- Пошаговый стенд на чистом Docker (сертификаты, build.py, NMS):
  Lan Tian @ Blog, «Legal LTE Network at Home for $100» (окт. 2026),
  lantian.pub/en/article/modify-computer/legal-lte-network-at-home-for-100-bucks.lantian/
- Ограничение логов и dev-compose: caprivm/virtualization wiki,
  «Deploy Magma Orchestrator using Docker».
- Контекст проекта и словарь (Orc8r/AGW/NMS): `docs/handoff-context.md`.

## Приложение: Mac на Apple Silicon (arm64) — опыт 2026-11-05

Mac (16 ГБ ОЗУ, 113 ГБ свободно) пригоден как лаборатория, но образы
собираются под linux/amd64 через Rosetta — сеть внутри эмуляции работает
в ~15 раз медленнее, сборка `build.py --all` занимает часы, а не минуты.
Клон со всеми правками ниже уже лежит в `~/magma` (не переключайте ветку —
файлы не закоммичены).

### Что пришлось пропатчить (уже сделано в ~/magma)

Пакетные базы образов 2021–2022 годов ссылаются на пакеты, вычеркнутые
из зеркал; свежий `apt-get update` не спасает:

| Файл | Правка |
|---|---|
| `orc8r/cloud/docker/nginx/Dockerfile` | `security.debian.org` → `archive.debian.org`, чистка `apt/lists`, `Check-Valid-Until=false` |
| `orc8r/cloud/docker/controller/Dockerfile` | `archive/security.ubuntu.com` → `old-releases.ubuntu.com` (xenial EOL), то же про Valid-Until — в двух ступенях |
| `orc8r/cloud/docker/fluentd_daemon/Dockerfile` | как nginx (debian) |

Шаблон правки: перед `apt-get update` вставить
`sed -i 's|<старое зеркало>|<архивное>|g' /etc/apt/sources.list`,
`rm -rf /var/lib/apt/lists/*` и `apt-get -o Acquire::Check-Valid-Until=false update`.

### Порядок работы на Mac

```bash
# все команды из каталога
cd ~/magma/orc8r/cloud/docker

# собрать с ограничением параллелизма (иначе apt в эмуляции отваливается по таймауту)
COMPOSE_PARALLEL_LIMIT=2 ./build.py --all
# падает на каком-то образе? читаем ошибку, патчим его Dockerfile, повторяем
# (кеш сохраняет прогресс, повторная сборка продолжается с того же места)

# контроль готовых образов
docker images | grep orc8r
```

Дальше как в Фазах 1–2 основного ранбука: `./run.py` (метрики не нужны),
NMS из `~/magma/nms` (правка `proxy_ssl.conf`: `listen 443 ssl;` вместо
`listen 443;` + `ssl on;`), `bash scripts/dev_setup.sh`. Для имён
`magma.test` вместо hosts-файла удобнее `sudo sh -c 'echo "127.0.0.1
magma.test api.magma.test nms.magma.test" >> /etc/hosts'`.

### Проверенные факты

- `docker run --rm --platform linux/amd64 alpine uname -m` → `x86_64`:
  эмуляция работает.
- Сборка `build.py --all` (после патчей зеркал и gem'ов) завершается успехом;
  образы: orc8r-nginx, orc8r-controller, orc8r-fluentd, orc8r-test (~4 ГБ суммарно).
- NMS собирается из `~/magma/nms` (`docker-compose build` — долго, вести
  по частям; правка `proxy_ssl.conf`: одна строка `listen 443 ssl;`).
- **Состояние на 2026-11-06: стенд поднят и проверен end-to-end**
  (backend + NMS + северный API, создана сеть `test`).

### Подводные камни запуска (все пройдены)

1. **postgres.** В compose образ не закреплён (`image: postgres`) → тянется
   latest, несовместимый с существующим томом `pgdata`. Лечение: пин
   `image: postgres:13` (строка 53 docker-compose.yml), `run.py --down`,
   `docker volume rm orc8r_pgdata`, `run.py` заново.
2. **Регистрация сертификатов.** Контейнер controller в TEST_MODE сам генерирует
   свою пару `admin_operator` в `/var/opt/magma/certs` и регистрирует её в БД.
   Хостовый `~/secrets/certs/admin_operator.pem` — ДРУГОЙ сертификат, его SN
   в БД нет → 401 «unknown client certificate SN». Брать нужно контейнерную пару:
   `docker cp orc8r-controller-1:/var/opt/magma/certs/admin_operator.pem .`
   (и `.key.pem`). Если БД пересоздавалась, внутри контейнера перезапустить
   `create_test_controller_certs`.
3. **Префикс API.** Северный REST — `https://api.magma.test:9443/magma/v1/...`
   (не `/v1/...`). Порты: 9443 — REST с клиентским сертификатом; 8443/8444 —
   gRPC для шлюзов (браузеру не нужны).
4. **NMS.** Вход: `https://nms.magma.test`, пользователь `admin@magma.test`,
   пароль `password1234` (создаёт `nms/scripts/dev_setup.sh`). 403
   `USER_NOT_LOGGED_IN` — это страница логина, не ошибка.
5. **Имена хостов** (`magma.test`, `api.magma.test`, `nms.magma.test`) →
   `/etc/hosts` на 127.0.0.1; sudo нужен.

### Проверка работоспособности

```bash
# API: список сетей (должен вернуть ["test"])
curl -sk --cert container_admin_operator.pem --key container_admin_operator.key.pem \
  https://api.magma.test:9443/magma/v1/networks

# NMS: страница логина (должна открыться в браузере)
open https://nms.magma.test
```

- AGW на Mac не поднимается принципиально (нужен Linux с двумя NIC) —
  Mac годится только для Orc8r + NMS.
