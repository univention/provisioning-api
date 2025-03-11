# How to debug the provisioning stack

## Inspect the NATS database

```sh
kubectl -n ${NAMESPACE?} get secrets nubus-provisioning-nats-credentials
kubectl -n ${NAMESPACE?} exec -it nubus-provisioning-nats-0 -c nats-box -- sh
kubectl -n ${NAMESPACE?} get secrets nubus-provisioning-nats-credentials -o json
nats --user admin --password <super-secret-password> stream ls
```

## Recreate a provisioning subscription

Provisioning subscriptions are immutable, except for changing the password.

If e.g. a prefill failed permanently for a subscription,
you have to delete and recreate the subscription to recover from this state.

For the moment a few manual steps are required to achieve this.
We can add automated support in form of a helm chart flag to automate this process if it's a common occurrence.

First we need to get the json secret from the Kubernetes API and save it to a file:

`kubectl -n ${NAMESPACE?} get secrets nubus-provisioning-register-consumers-json-secrets -o json | jq '.data | map_values(@base64d)' | jq -r '."selfservice.json"' > selfservice.json
`
Then we need to obtain the Provisioning API credentials from the API:
`PASSWORD=$(kubectl -n ${NAMESPACE?} get secrets nubus-provisioning-register-consumers-credentials -o json | jq '.data.ADMIN_PASSWORD | @base64d' | sed -re 's/^"([^"]+)"$/\1/')`

The Provisioning API is not exposed outside the cluster.
The easiest way to access it from your laptop is a kubectl port-forward.
To start the port-forward, execute the following command in a separate terminal window:

`kubectl -n ${NAMESPACE?} port-forward nubus-provisioning-api-* 7777`

Now we can delete the old subscription:
`curl -o - -u "admin:${PASSWORD?}" -X DELETE http://localhost:7777/v1/subscriptions/selfservice`

After deleting the subscription, we can recreate it with the following command:
`curl -u "admin:${PASSWORD?}" -H 'Content-Type: application/json' -d @selfservice.json http://localhost:7777/v1/subscriptions`
