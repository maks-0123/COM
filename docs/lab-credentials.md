# Доступы лаборатории (шпаргалка)

Все секреты — самоподписанные, сгенерированы скриптами Magma для локальной
лабы. Файл хранит только **пароли и пути**; приватные ключи лежат в
`~/secrets/certs/` и в репозиторий не копируются.

## NMS (веб-админка)

| Параметр | Значение |
|---|---|
| Адрес | `http://magma-test.nms.magma.test` (важен хост — организация из поддомена, камень №7) |
| Организация | `magma-test` |
| Логин | `admin@magma.test` |
| Пароль | `password1234` (задаёт `nms/scripts/dev_setup.sh`) |

Сброс пароля: `cd ~/magma/nms && docker-compose exec magmalte yarn setAdminPassword magma-test admin@magma.test <новый>`.

## Северный API оркестратора

| Параметр | Значение |
|---|---|
| Endpoint | `https://api.magma.test:9443/magma/v1/…` (камень №3) |
| Аутентификация | клиентский сертификат (mTLS) |
| Сертификат | `~/secrets/certs/container_admin_operator.pem` |
| Ключ | `~/secrets/certs/container_admin_operator.key.pem` |

Важно: рабочая пара — **контейнерная** (выгружена из `orc8r-controller-1`,
камень №2). Хостовая пара `admin_operator.*` из `~/secrets/certs/` НЕ
подходит — 401 «unknown client certificate SN».

Шаблон запроса:

```bash
curl -sk --resolve api.magma.test:9443:127.0.0.1 \
  --cert ~/secrets/certs/container_admin_operator.pem \
  --key ~/secrets/certs/container_admin_operator.key.pem \
  https://api.magma.test:9443/magma/v1/networks
```

## Базы данных (psql из контейнеров)

| Что | Команда |
|---|---|
| Оркестратор (сети, абоненты, SN сертификатов) | `docker exec orc8r-postgres-1 psql -U magma_dev -d magma_dev` |
| NMS (организации, пользователи) | `docker exec nms-postgres-1 psql -U nms -d nms` |
| NMS (контейнерная БД) | пользователь `nms`, пароль `password` (compose) |

Полезные запросы — в `docs/magma-lab.md`, раздел «как работает БД».

## Управление стендом

| Что | Команда |
|---|---|
| Статус ~25 микросервисов контроллера | `docker exec orc8r-controller-1 supervisorctl status` |
| Белый список сертификатов (accessc) | `docker exec orc8r-controller-1 accessc list` |
| Логи NMS | `docker logs -f nms-magmalte-1` |
| Перегенерация прокси-сертификата NMS | `docs/patches/README.md` |

## Ключи и сертификаты (файлы)

| Файл | Роль |
|---|---|
| `~/secrets/certs/rootCA.pem` + `.key` | корень доверия TLS (10 лет) |
| `~/secrets/certs/controller.crt` + `.key` | серверный сертификат оркестратора |
| `~/magma/nms/docker/docker_ssl_proxy/cert.pem` + `key.pem` | сертификат NMS-прокси (наш, до 2029) |
| `~/secrets/certs/certifier.pem` + `.key` | внутренняя PKI Magma (перевыпущена контроллером, см. камень №2) |

Доверие rootCA для HTTPS: `sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ~/secrets/certs/rootCA.pem` (камень №9). Для повседневной работы достаточно HTTP-адреса NMS.
