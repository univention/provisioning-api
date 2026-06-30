# Provisioning API usage examples

## Create a subscription:
```json
{
	"name": "demo-consumer",
	"realms_topics": [
		{"realm": "udm", "topic": "users/user"}
	],
	"request_prefill": true,
	"password": "super_secret_password"
}
```
POST: http://nubus-provisioning-api/v1/subscriptions
```sh
curl -u "${ADMIN_USERNAME}:${ADMIN_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d @subscription-config.json
  http://nubus-provisioning-api/v1/subscriptions
```

## Get an event
GET: http://nubus-provisioning-api/v1/subscriptions/demo-consumer/messages/next
```sh
curl -X POST -u "demo-consumer:super-secret-password" \
  http://nubus-provisioning-api/v1/subscriptions/demo-consumer/messages/next
```

This endpoint **long-polls**: it waits up to `timeout` seconds (query parameter,
default `5`) for a message before responding. An empty response means no message
arrived within that window; the consumer should simply request again.

> **Client timeout margin:** the client's HTTP request/read timeout must be set
> **longer than** the `timeout` query parameter. If the client timeout is shorter,
> the client aborts the connection before the long-poll returns; the server cannot
> detect this and the in-flight message stays stuck until the consumer-queue
> `ack_wait` expires and it is redelivered.

> Rule of thumb: client timeout >= long-poll `timeout` + a few seconds.
> The bundled `ProvisioningConsumerClient` already satisfies this (aiohttp default of 300s versus the 5s long-poll).

## Acknowledge an event
```sh
curl -X POST -u "demo-consumer:super-secret-password" \
  -d '{"status": "ok"}'
  http://nubus-provisioning-api/v1/subscriptions/demo-consumer/messages/1234/status
```

## Example event json:
```json
{
  "publisher_name": "udm-listener",
  "ts": "2025-01-07T15:18:23.515236",
  "realm": "udm",
  "topic": "groups/group",
  "body": {
    "old": {},
    "new": {
      "dn": "cn=Summit-Demo,cn=groups,dc=univention-organization,dc=intranet",
      "objectType": "groups/group",
      "id": "Summit-Demo",
      "position": "cn=groups,dc=univention-organization,dc=intranet",
      "properties": {
        "name": "Summit-Demo",
        "gidNumber": 5013,
        "sambaRID": 11027,
        "sambaGroupType": "2",
        "sambaPrivileges": [],
        "adGroupType": "-2147483646",
        "description": "Gruppe für eine summit demonstration der Nubus Provisioning API",
        "users": [
          "uid=Administrator,cn=users,dc=univention-organization,dc=intranet"
        ],
        "hosts": [],
        "mailAddress": null,
        "memberOf": [],
        "nestedGroup": [],
        "allowedEmailUsers": [],
        "allowedEmailGroups": [],
        "univentionObjectIdentifier": null,
        "univentionSourceIAM": null,
        "guardianMemberRoles": [],
        "objectFlag": []
      },
      "options": {
        "posix": true,
        "samba": true
      },
      "policies": {
        "policies/umc": []
      },
      "uuid": "613492ea-6156-103f-9c22-b957091217b2"
    }
  },
  "sequence_number": 41,
  "num_delivered": 1
}
```
