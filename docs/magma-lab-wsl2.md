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
