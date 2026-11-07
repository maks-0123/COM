# Лаборатория Magma на Mac (Apple Silicon, docker-compose)

Как поднят Orc8r + NMS (Magma v1.8.0) на MacBook Pro с Apple Silicon,
16 ГБ ОЗУ, без Kubernetes. Составлен 2026-11-05, переписан 2026-11-07
по факту: вся работа велась на Mac, Windows-план (см. приложение) не использовался.

Цель — научиться пользоваться Magma: NMS, абоненты (SIM/IMSI), северный
REST API и подготовить почву для собственных сервисов. Координаты тележек
в этот этап не входят: они приходят готовыми и подключаются к карте
отдельно (см. `docs/docker-cart-tracker.md`).

**Состояние на 2026-11-06: стенд поднят и проверен end-to-end**
(backend + NMS с рабочим дашбордом + северный API; сеть `test` типа `lte`).

## Особенности платформы

- Все контейнеры — `linux/amd64` через Rosetta: сеть внутри эмуляции
  работает в ~15 раз медленнее, сборка `build.py --all` занимает **часы,
  не минуты**. Терпение и кеш — главные инструменты.
- Docker Desktop: лимит памяти оставить ~11–12 ГБ (стенд ест 4–5 ГБ).
- Клон с патчами лежит в `~/magma` (shallow, ветка v1.8.0). Патчи
  продублированы в `docs/patches/magma-1.8.0-docker-lab.patch` —
  восстановление на чистом клоне: `git apply`.
- Сертификаты — в `~/secrets/certs/` (самоподписанные, домен `magma.test`).

## Порядок работы (восстановление с нуля)

```bash
# 1. Исходники + патчи
git clone --depth 1 --branch v1.8.0 https://github.com/magma/magma.git ~/magma
cd ~/magma && git apply /путь/к/docs/patches/magma-1.8.0-docker-lab.patch
# плюс docs/patches/nms-nginx-http.conf → ~/magma/nms/docker/docker_ssl_proxy/http.conf

# 2. Сертификаты
mkdir -p ~/secrets/certs && cd ~/secrets/certs
bash ~/magma/orc8r/cloud/deploy/scripts/self_sign_certs.sh magma.test
bash ~/magma/orc8r/cloud/deploy/scripts/create_application_certs.sh magma.test
mkdir -p ~/magma/.cache/test_certs/
cp -r * ~/magma/.cache/test_certs/ && chmod -R +r ~/magma/.cache/test_certs/

# 3. Сборка (самый долгий шаг; кеш сохраняет прогресс между попытками)
cd ~/magma/orc8r/cloud/docker
COMPOSE_PARALLEL_LIMIT=2 ./build.py --all
# падает на образе? читаем ошибку, патчим его Dockerfile, повторяем
docker images | grep orc8r   # контроль готовых образов
```

Дальше — разделы «Запуск и остановка» и «Подводные камни» ниже.

## Запуск и остановка

Два независимых compose-проекта: сначала backend, потом NMS
(NMS ходит в API оркестратора). Порядок важен.

```bash
# ЗАПУСК
cd ~/magma/orc8r/cloud/docker && ./run.py
# ждём 30–60 с: контроллер поднимает ~25 микросервисов под supervisor'ом
docker exec orc8r-controller-1 supervisorctl status | grep -cv RUNNING   # ждём 0
cd ~/magma/nms && docker-compose up -d

# ОСТАНОВКА
cd ~/magma/nms && docker-compose down
cd ~/magma/orc8r/cloud/docker && ./run.py --down
```

`down` останавливает контейнеры, но **не удаляет данные**: БД в
именованных томах (сеть `test`, тип `lte`, логин admin переживают
перезапуск). Полное удаление данных — только `down -v`, оно не нужно.

### Проверка работоспособности

```bash
# API: список сетей (должен вернуть ["test"])
curl -sk --resolve api.magma.test:9443:127.0.0.1 \
  --cert ~/secrets/certs/container_admin_operator.pem \
  --key ~/secrets/certs/container_admin_operator.key.pem \
  https://api.magma.test:9443/magma/v1/networks

# тип сети зарегистрирован (должен вернуть "lte")
curl -sk --resolve api.magma.test:9443:127.0.0.1 \
  --cert ~/secrets/certs/container_admin_operator.pem \
  --key ~/secrets/certs/container_admin_operator.key.pem \
  https://api.magma.test:9443/magma/v1/networks/test/type

# NMS: вход admin@magma.test / password1234
open http://magma-test.nms.magma.test
```

## Что пропатчено и почему (все правки — в docs/patches/)

Пакетные базы образов 2021–2022 годов ссылаются на пакеты, вычеркнутые
из зеркал; свежий `apt-get update` не спасает.

| Файл | Правка |
| --- | --- |
| `orc8r/cloud/docker/nginx/Dockerfile` | `security.debian.org` → `archive.debian.org`, чистка `apt/lists`, `Check-Valid-Until=false` |
| `orc8r/cloud/docker/controller/Dockerfile` | `rm -rf /var/lib/apt/lists/*` + `apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Retries=5 -o Acquire::http::Timeout=120 update` в обеих ступенях. **Важно:** xenial (16.04) живёт на `archive.ubuntu.com`, а НЕ на `old-releases.ubuntu.com`; туда переезжают только версии ≤ 14.04. URL Go: `artifactory.magmacore.org` → `go.dev/dl` |
| `orc8r/cloud/docker/fluentd/Dockerfile`, `fluentd_forward/Dockerfile` | сначала `gem install multi_json -v 1.15.0` и `gem install excon -v 1.2.5`, основная установка с `--minimal-deps` (старый RubyGems иначе тянет свежие несовместимые версии) |
| `orc8r/cloud/docker/fluentd_daemon/Dockerfile` | как nginx (debian) |
| `orc8r/cloud/docker/docker-compose.yml` | `image: postgres` → `postgres:13` (иначе latest несовместим с существующим томом `pgdata`) |
| `nms/docker/docker_ssl_proxy/proxy_ssl.conf` | одна строка `listen 443 ssl;` вместо `listen 443;` + `ssl on;` |
| `nms/docker-compose.yml` + `docker_ssl_proxy/http.conf` | проброс порта 80 + server-блок на 80 (обход сертификатов, см. камень №6) |

Шаблон правки зеркал: перед `apt-get update` вставить
`sed -i 's|<старое зеркало>|<архивное>|g' /etc/apt/sources.list`,
`rm -rf /var/lib/apt/lists/*` и `apt-get -o Acquire::Check-Valid-Until=false update`.

## Подводные камни (все пройдены)

1. **postgres.** В compose образ не закреплён (`image: postgres`) → тянется
   latest, несовместимый с существующим томом `pgdata`. Лечение: пин
   `image: postgres:13`, `run.py --down`, `docker volume rm orc8r_pgdata`,
   `run.py` заново.
2. **Регистрация сертификатов.** Контейнер controller в TEST_MODE сам
   генерирует свою пару `admin_operator` в `/var/opt/magma/certs` и
   регистрирует её в БД. Хостовый `~/secrets/certs/admin_operator.pem` —
   ДРУГОЙ сертификат, его SN в БД нет → 401 «unknown client certificate
   SN». Брать нужно контейнерную пару:
   `docker cp orc8r-controller-1:/var/opt/magma/certs/admin_operator.pem .`
   (и `.key.pem`). Если БД пересоздавалась, внутри контейнера перезапустить
   `create_test_controller_certs`.
3. **Префикс API.** Северный REST — `https://api.magma.test:9443/magma/v1/...`
   (не `/v1/...`). Порты: 9443 — REST с клиентским сертификатом; 8443/8444 —
   gRPC для шлюзов (браузеру не нужны).
4. **NMS.** Пользователь `admin@magma.test`, пароль `password1234`
   (создаёт `nms/scripts/dev_setup.sh`). 403 `USER_NOT_LOGGED_IN` — это
   страница логина, не ошибка.
5. **Имена хостов** (`magma.test`, `api.magma.test`, `nms.magma.test`,
   `magma-test.nms.magma.test`) → `/etc/hosts` на 127.0.0.1; sudo нужен.
6. **Просроченный сертификат nginx-proxy NMS.** В репозитории зашит
   демо-серт `CN=localhost` с валидностью 2018–2019 → браузер блокирует
   страницу (`ERR_CERT_AUTHORITY_INVALID`, белый экран со спиннером).
   Лечение: свой серт от лабораторного rootCA с SAN
   `magma-test.nms.magma.test` в `nms/docker/docker_ssl_proxy/cert.pem` +
   `key.pem` (команды генерации — в `docs/patches/README.md`) и HTTP-порт
   80 как обход. Итог: NMS открывается по
   `http://magma-test.nms.magma.test` без предупреждений.
7. **Организация NMS определяется поддоменом.** middleware берёт первую
   метку хоста как имя организации: только `magma-test.nms.magma.test` →
   организация `magma-test` (там admin). Заход по `localhost` попадает в
   организацию `localhost` → «Invalid organization» или чужой пароль.
8. **Сеть без типа = вечный спиннер дашборда NMS.** Если сеть создана
   «голой» (`POST /networks` без конфигов), NMS после логина дёргает
   `GET /networks/{id}/type`, получает `""` и висит на спиннере, не делая
   ни одного запроса дальше; в логах magmalte тишина. Лечение:
   `PUT /magma/v1/networks/test/type` с телом `"lte"` → 204, после этого
   дашборд отрисовывается. Проверка: `GET /magma/v1/lte/test` должен
   вернуть 200 (в теле `cellular:null`, конфиги EPC/RAN — следующим шагом).
9. **Доверие rootCA.** Для чистого HTTPS:
   `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/secrets/certs/rootCA.pem`
   (без sudo сертификат добавляется в login keychain, но Chromium может не
   увидеть доверие). Для лабы достаточно HTTP-варианта из камня №6.
10. **Создание абонента: POST, а не PUT.** `PUT /lte/{id}/subscribers/{imsi}`
    обновляет ТОЛЬКО существующего (иначе 404 `Not Found`), создание —
    пакетное: `POST /lte/{id}/subscribers` с телом-массивом mutable_subscriber.
    Ответ 201. Абонент появляется в `cfg_entities` (type `subscriber`).
11. **Секреты LTE строго 16 байт в base64.** `auth_key`/`auth_opc` —
    16 байт, в JSON это base64 (**24 символа**). 32 hex-символа — это уже
    24 байта: валидация obsidian отвечает `400` с пустым телом `{}`
    (сообщение об ошибке теряется — баг Magma). Ключи генерировать:
    `openssl rand 16 | base64`. До абонентов сеть должна иметь cellular-конфиг
    (камень ниже), иначе тот же пустой 400.
12. **Cellular-конфиг создаётся только целиком.** `PUT /lte/{id}/cellular`
    (не /epc и не /ran по отдельности — они 400 «No cellular network config
    found», если конфига ещё нет). Обязательные поля: `ran.fdd_config.earfcndl`
    + `earfcnul` (вложенный объект! плоские `earfcndl` молча не проходят),
    `epc.mcc/mnc/tac/lte_auth_amf/lte_auth_op/hss_relay_enabled/
    gx_gy_relay_enabled`. Образец — `NewDefaultFDDNetworkConfig()` в
    `lte/cloud/go/services/lte/obsidian/models/defaults.go`. Ошибки obsidian
    бывают двух видов: развёрнутые `validation failure list` (swagger-слой)
    и пустые `{}` (ValidateModel в handler'е — копать код модели).
13. **id абонента с префиксом `IMSI`.** Паттерн `^(IMSI\d{10,15})$` —
    буквально буквы IMSI + 10–15 цифр, например `IMSI001010000000001`
    (тестовый PLMN 001/01 из камня №12).

## Фаза 2. Учимся (текущая цель)

По нарастающей, каждый пункт — отдельное мини-занятие:

1. **NMS:** дашборды сети `test` (готово). NMS не модифицируем — это
   чужой интерфейс (принцип из handoff-context).
2. **Абоненты:** созданы через `POST /magma/v1/lte/test/subscribers`
   (камни №10–13), видны в `cfg_entities` и в NMS → Subscribers. IMSI —
   тестовый диапазон `00101…`; при связывании с картой `carts[].imsi`
   схемы — поменять MCC/MNC в EPC-конфиге под реальный план.
3. **Северный API:** NMS — тонкая оболочка над REST. Погонять curl
   против `/magma/v1/...` (примеры выше) — именно через этот API в
   будущем подключаются собственные сервисы; затем переписать на Python.
4. **Встраивание карты:** в репозитории уже есть embed-режим
   (`?embed=1`, коммит 2fee35c) — зашить карту в NMS как iframe-виджет,
   когда появится живой источник координат.
5. **Первый собственный сервис Magma:** микросервис, читающий northbound
   API (состояние шлюзов/абонентов), — паттерн «добавлять свои сервисы»,
   ради которого всё и затевается.

## Фаза 3. AGW и радио (позже, не на этой машине)

AGW требует Linux с **двумя сетевыми портами** (S1 к вышке и SGi в сеть) —
Mac и Windows-ноутбук не подходят. Когда дойдёт: отдельная машина
с Ubuntu, пакетная или контейнерная установка AGW 1.8, регистрация
в Orc8r по hardware ID, затем eNodeB/модемы. До этого момента Orc8r+NMS —
полноценная учебная площадка и без AGW.

## Риски и как их гасить

| Симптом | Причина | Лечение |
| --- | --- | --- |
| Сборка падает по таймауту сети | apt/gem в эмуляции медленные | `COMPOSE_PARALLEL_LIMIT=2`, повторять (кеш хранит прогресс) |
| Сборка падает с 404 на пакетах | пакет вычеркнут из зеркала | патч Dockerfile зеркалом archive.* (см. таблицу выше) |
| Сборка падает на gem'ах | свежие версии несовместимы со старым Ruby | пины `multi_json -v 1.15.0`, `excon -v 1.2.5`, `--minimal-deps` |
| Диск тает | логи контейнеров, образы | `docker system prune`; лимиты логов в compose |
| 401 «unknown client certificate SN» | не тот сертификат | брать пару из контейнера controller (камень №2) |
| Спиннер дашборда NMS | у сети нет типа | `PUT /networks/{id}/type` = `"lte"` (камень №8) |
| Страница NMS не открывается | сертификат/hosts/организация | камни №5–№7 |

## Источники шагов

- Официальный репозиторий: https://github.com/magma/magma (ветка v1.8.0),
  каталоги `orc8r/cloud/docker` и `nms`.
- Пошаговый стенд на чистом Docker (сертификаты, build.py, NMS):
  Lan Tian @ Blog, «Legal LTE Network at Home for $100» (окт. 2026),
  lantian.pub/en/article/modify-computer/legal-lte-network-at-home-for-100-bucks.lantian/
- Ограничение логов и dev-compose: caprivm/virtualization wiki,
  «Deploy Magma Orchestrator using Docker».
- Контекст проекта и словарь (Orc8r/AGW/NMS): `docs/handoff-context.md`.

## Приложение: изначальный план Windows 10 + WSL2 (не реализован)

Изначально лаба планировалась на втором ноутбуке (Windows 10, 12 ГБ ОЗУ,
~25 ГБ свободно) через WSL2 + Docker Desktop: включить виртуализацию,
`wsl --install`, в `.wslconfig` лимит `memory=9GB`, Docker Desktop
с WSL2-backend, дальше те же Фазы 1–2. План не понадобился — всё поднялось
на Mac; отличия только в подготовке платформы (Фаза 0) и скорости сборки
(в WSL2 без Rosetta сборка была бы быстрее). Если вернётесь к Windows:
заменить «Особенности платформы» на шаги WSL2 из истории коммитов
(файл `docs/magma-lab-wsl2.md` до 2026-11-07).

- AGW на Mac/Windows принципиально не поднимается (нужен Linux с двумя NIC) —
  обе машины годятся только для Orc8r + NMS.
