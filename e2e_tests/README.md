# Testing

### Local manual testing

update all lock files:
> uv lock --project backends/ && uv lock --project common/ && uv lock --project rest-api/ && uv lock --project listener/ && uv lock --project dispatcher/ && uv lock --project prefill/ && uv lock --project dispatcher/ && uv lock --project udm-transformer/ && uv lock --project consumer_example/ && uv lock

* Unit tests:
  ```
  uv sync
  source .venv/bin/activate
  pytest -v
  ```

* e2e tests:
  ```
  docker compose down -v && docker compose up --build provisioning-api nats1 nats2 nats3 dispatcher prefill udm-transformer udm-rest-api ldap-server udm-listener ldap-notifier ldif-producer
  cd e2e_tests
  cp e2e_settings.json.example e2e_settings.json
  uv sync
  source .venv/bin/activate
  pytest -v
  ```
* If you have a problem with `docker compose` caching, you can build the images manually like this:
  ```
  docker build -f docker/dispatcher/Dockerfile .
  ```
### Testing on a UCS

`ucs-test` contains automatic tests for the Provisioning Service.

##### Inspect NATS on UCS:

> docker run --rm -it  -e NATS_URL="nats://nats:4222" -e NATS_USER="api" -e NATS_PASSWORD="$(sudo cat /etc/provisioning-secrets.json | jq -r '.NATS_PASSWORD')" natsio/nats-box:latest

* lookup user in nats.conf (/var/lib/univention-appcenter/apps/provisioning-service/conf/nats.conf)
  ```
  nats stream view
  nats stream info
  nats stream ls
  ```

* erroneous message removal
  ```
  nats stream rmm
  ```