# Configuring a custom Consumer

To create a new subscription for your Consumer in the Nubus Provisioning Stack,
you need to configure the following things.

## Nubus umbrella chart values.yaml

Add a consumer section in the `createUsers` list.
You need to point to an existing secret name and key, which holds the configuration JSON.
This secret can be created e.G. via the `extraSecrets` mechanism.
But also by the Consumer helm chart or an external secrets manager like Hashicorp Vault.

```yaml
nubusProvisioning:
  registerConsumers:
    createUsers:
      exampleClient:
        existingSecret:
          name: example-client-json-secret
          keyMapping:
            password: "example-consumer.json"
      otherClient: foobar

  extraSecrets:
    - name: example-client-json-secret
      stringData:
        example-consumer.json: |
          {
            "name": "example-client",
            "realms_topics": [
              {"realm": "udm", "topic": "groups/group"},
              {"realm": "udm", "topic": "users/user"}
            ],
            "request_prefill": true,
            "password": "example-client-password"
          }
```

## Consumer configuration

Example of a values.yaml of a consumer helm chart.

The relevant part is that the `name` and `password`, defined in the `example-consumer.json`
is provided to the Provisioning Consumer as it's credentials for interacting with the Provisioning API.

```yaml
provisioning:
  connection:
    url: "http://nubus-provisioning-api"
  auth:
    username: example-client
    password: example-client-password
    existingSecret:
      name: null
      keyMapping:
        password: null
```
