# Nubus Provisioning Service client

`nubus-provisioning-service-client` provides the shared subscription lifecycle
used by UCS apps and Python integrations. Its command-line program is
`univention-provisioning-service-client`.

The client deliberately separates two credentials:

- The Provisioning administrator password is needed while creating or
  replacing a subscription. It is also fetched after an ambiguous unsubscribe
  retry only to confirm that the exact subscription is already absent. On UCS
  it is read from the Provisioning host and kept in process memory; it is not
  intentionally written to the consuming host, logged, exported, or passed on
  a command line.
- The generated subscriber password has access only to its own subscription.
  It is stored because the consumer needs it while running and because
  Provisioning stores only its one-way hash.

Python cannot guarantee cryptographic memory zeroization or prevent the
operating system from swapping or dumping process memory. "Memory-only" here
means that the client does not intentionally persist or log the administrator
password.

## Create or validate a subscription

```console
univention-provisioning-service-client subscribe "$@" \
  --provisioning-server "$(ucr get ldap/master)" \
  --subscription-file /var/lib/univention-appcenter/apps/example/runtime-secrets/provisioning-subscription.json \
  --generate-password \
  --request-prefill \
  --json '{
    "name": "example-consumer",
    "realms_topics": [
      {"realm": "udm", "topic": "users/user"}
    ],
    "request_prefill": false
  }'
```

The App Center or join-script arguments `--binddn` and `--bindpwdfile` may be
forwarded in `"$@"`. If the Provisioning host is remote, the client converts
the user DN and uses `univention-ssh` to run its fixed credential-read command
there. The SSH stdout is captured directly; the Primary's secret file is never
copied.

`password` and `password_file` are accepted in imported JSON for compatibility
but ignored. `--generate-password` is the only supported source for a new
subscriber password.

## Retry and collision behavior

The credential file is written as a protected `candidate` before the API call
and promoted to `active` only after subscriber authentication succeeds. A
retry therefore reuses the same limited password if a response is lost after
the subscription was created.

With no local credential file, an existing exact subscription name is left
untouched by default. `--force` deletes and recreates only that exact name. This
also deletes its pending event queue. A requested prefill restores current
objects, not lost historic updates or deletion events. Accepted replacement
intent is stored only while the record is a `candidate`, so a retry after a
failed delete or create remains authorized for that exact name. Promotion to
`active` clears the intent; an active record never authorizes later destructive
replacement on its own.

An active subscription with valid credentials is reused and never rotated. If
it disappeared remotely, the retained password is reused and recovery requests
a prefill. If the password is rejected while the name still exists, the client
stops rather than silently deleting a potentially active queue.

## Remove a subscription

```console
univention-provisioning-service-client unsubscribe \
  --provisioning-server "$(ucr get ldap/master)" \
  --subscription-file /var/lib/univention-appcenter/apps/example/runtime-secrets/provisioning-subscription.json
```

Removal authenticates with the limited subscriber password. The local file is
deleted only after the API confirms deletion or reports that the subscription
is already absent. Because the API authenticates before checking existence, a
retry after a lost successful DELETE response can return HTTP 401. Only in that
case, the client lazily reads the Provisioning administrator password and lists
subscriptions. It deletes the local file only when the exact name is confirmed
absent. If the name still exists or confirmation fails, the file is retained.
The administrator password remains process-memory-only as described above.

## Stored file

The parent directory must be owned by the current user with mode `0700`; the
credential file is written atomically with mode `0600`. Version 1 stores:

```json
{
  "schema_version": 1,
  "state": "active",
  "provisioning_api_base_url": "https://primary.example.test/univention/provisioning",
  "subscription": {
    "name": "example-consumer",
    "realms_topics": [{"realm": "udm", "topic": "users/user"}],
    "request_prefill": true
  },
  "password": "limited-subscriber-password"
}
```

Links, special files, hard links, unexpected owners or modes, oversized data,
unknown fields, and malformed JSON are rejected.

While a forced replacement is unfinished, a version 1 `candidate` may also
contain `"replacement_authorized": true`. Existing version 1 files without
that field remain valid. The field is removed before an `active` record is
written.
