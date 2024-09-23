# udm-listener

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for the Univention Portal Provisioning API

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://registry-1.docker.io/bitnamicharts | common | ^2.x.x |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| config | object | `{"caCert":"","caCertFile":"","debugLevel":"2","eventsPasswordUdm":"udmpass","eventsUsernameUdm":"udm","ldapBaseDn":null,"ldapHost":"","ldapHostDn":null,"ldapPassword":"","ldapPasswordFile":"/var/secrets/ldap_secret","ldapPort":"389","natsHost":null,"natsPassword":"udmlistenerpass","natsPort":"4222","natsUser":"udmlistener","nats_max_reconnect_attempts":"5","notifierServer":"ldap-notifier","provisioningApi":{"auth":{"credentialSecret":{"name":"","passwordKey":"EVENTS_PASSWORD_UDM","userNameKey":"EVENTS_USERNAME_UDM"}}},"provisioningApiHost":"provisioning-api","provisioningApiPort":"80","secretMountPath":"/var/secrets","tlsMode":"off"}` | Configuration of the UDM Listener that is notified on LDAP changes |
| config.caCert | string | `""` | CA root certificate, base64-encoded. Optional; will be written to "caCertFile" if set. |
| config.caCertFile | string | `""` | Where to search for the CA Certificate file. caCertFile: "/var/secrets/ca_cert" |
| config.ldapPassword | string | `""` | LDAP password for `cn=admin`. Will be written to "ldapPasswordFile" if set. |
| config.ldapPasswordFile | string | `"/var/secrets/ldap_secret"` | The path to the "ldapPasswordFile" docker secret or a plain file |
| config.natsHost | string | `nil` | NATS: host (required if nats.bundled == false) |
| config.natsPassword | string | `"udmlistenerpass"` | NATS: password |
| config.natsPort | string | `"4222"` | NATS: port (required if nats.bundled == false) |
| config.natsUser | string | `"udmlistener"` | NATS: user name |
| config.nats_max_reconnect_attempts | string | `"5"` | NATS: maximum number of reconnect attempts to the NATS server |
| config.notifierServer | string | `"ldap-notifier"` | Defaults to "ldapHost" if not set. |
| config.provisioningApiHost | string | `"provisioning-api"` | Provisioning-API Hostname |
| config.provisioningApiPort | string | `"80"` | Provisioning-API Port |
| config.secretMountPath | string | `"/var/secrets"` | Path to mount the secrets to. |
| config.tlsMode | string | `"off"` | Whether to start encryption and validate certificates. Chose from "off", "unvalidated" and "secure". |
| containerSecurityContext.allowPrivilegeEscalation | bool | `false` | Enable container privileged escalation. |
| containerSecurityContext.capabilities | object | `{"drop":["ALL"]}` | Security capabilities for container. |
| containerSecurityContext.enabled | bool | `true` | Enable security context. |
| containerSecurityContext.readOnlyRootFilesystem | bool | `true` | Mounts the container's root filesystem as read-only. |
| containerSecurityContext.runAsGroup | int | `65534` | Process group id. |
| containerSecurityContext.runAsNonRoot | bool | `true` | Run container as a user. |
| containerSecurityContext.runAsUser | int | `102` | Process user id. |
| containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` | Disallow custom Seccomp profile by setting it to RuntimeDefault. |
| environment | object | `{}` |  |
| extraInitContainers | list | `[]` |  |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` |  |
| global.imagePullPolicy | string | `"IfNotPresent"` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| global.nubusDeployment | bool | `false` | Indicates wether this chart is part of a Nubus deployment. |
| image.imagePullPolicy | string | `"Always"` |  |
| image.registry | string | `""` |  |
| image.repository | string | `"nubus-dev/images/provisioning-udm-listener"` |  |
| image.tag | string | `"0.28.3@sha256:b9c452e55e6716f93309bef0af7d401e218cd1e6ea9ad3d2819fb10dd631aecd"` |  |
| imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| ldap.credentialSecret.ldapPasswordKey | string | `"ldap.secret"` |  |
| ldap.credentialSecret.machinePasswordKey | string | `"machine.secret"` |  |
| ldap.credentialSecret.name | string | `""` |  |
| ldap.tlsSecret.caCertKey | string | `"ca.crt"` |  |
| ldap.tlsSecret.name | string | `""` |  |
| mountSecrets | bool | `true` |  |
| nameOverride | string | `""` |  |
| nats.auth.credentialSecret.key | string | `"NATS_PASSWORD"` |  |
| nats.auth.credentialSecret.name | string | `""` |  |
| nats.bundled | bool | `true` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext.enabled | bool | `true` | Enable security context. |
| podSecurityContext.fsGroup | int | `65534` | If specified, all processes of the container are also part of the supplementary group. |
| podSecurityContext.fsGroupChangePolicy | string | `"Always"` | Change ownership and permission of the volume before being exposed inside a Pod. |
| podSecurityContext.sysctls | list | `[]` | Allow binding to ports below 1024 without root access. |
| probes.liveness.enabled | bool | `true` |  |
| probes.liveness.failureThreshold | int | `30` |  |
| probes.liveness.initialDelaySeconds | int | `10` |  |
| probes.liveness.periodSeconds | int | `10` |  |
| probes.liveness.successThreshold | int | `1` |  |
| probes.liveness.timeoutSeconds | int | `3` |  |
| probes.readiness.enabled | bool | `true` |  |
| probes.readiness.failureThreshold | int | `3` |  |
| probes.readiness.initialDelaySeconds | int | `10` |  |
| probes.readiness.periodSeconds | int | `10` |  |
| probes.readiness.successThreshold | int | `1` |  |
| probes.readiness.timeoutSeconds | int | `3` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automountServiceAccountToken | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` |  |
| terminationGracePeriodSeconds | string | `""` | In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods |
| tolerations | list | `[]` |  |
| topologySpreadConstraints | list | `[]` | Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule |
