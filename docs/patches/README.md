# Патчи лаборатории Magma

`magma-1.8.0-docker-lab.patch` — все правки Dockerfile'ов и конфигов в клоне
`~/magma` (ветка v1.8.0, shallow clone), без которых стенд не собирается
и не запускается на современных машинах. Применяется так:

```bash
cd ~/magma
git checkout v1.8.0            # или на чистый клон
git apply /путь/к/magma-1.8.0-docker-lab.patch
```

Покрывает: зеркала archive.debian.org для nginx/fluentd, пины apt-репозиториев
xenial, установку совместимых версий gem'ов (multi_json, excon), скачивание Go
с go.dev, пин `postgres:13`, правку `proxy_ssl.conf`.

`sertifikat-proxy-nms` отдельно: `cert.pem`/`key.pem` в
`~/magma/nms/docker/docker_ssl_proxy/` в гит не выгружены (там приватный ключ).
Генерируются заново от лабораторного rootCA:

```bash
cd ~/magma/nms/docker/docker_ssl_proxy
openssl req -new -newkey rsa:2048 -nodes -keyout key.pem -out proxy.csr \
  -subj "/CN=magma-test.nms.magma.test"
printf 'subjectAltName=DNS:magma-test.nms.magma.test,DNS:nms.magma.test,DNS:magma.test,DNS:localhost,IP:127.0.0.1\nextendedKeyUsage=serverAuth\nkeyUsage=digitalSignature,keyEncipherment\n' > san.ext
openssl x509 -req -in proxy.csr -CA ~/secrets/certs/rootCA.pem \
  -CAkey ~/secrets/certs/rootCA.key -CAcreateserial -days 825 \
  -extfile san.ext -out cert.pem
rm proxy.csr san.ext
docker exec nms-nginx-proxy-1 nginx -s reload
```

`nms-nginx-http.conf` — server-блок на порту 80; копируется рядом с
`proxy_ssl.conf` в `~/magma/nms/docker/docker_ssl_proxy/http.conf`, в
`~/magma/nms/docker-compose.yml` у nginx-proxy добавляется `"80:80"` в ports.
