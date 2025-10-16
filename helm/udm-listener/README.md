# udm-listener

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A Helm chart for the Univention Portal Provisioning API

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus-dev/charts | nubus-common | 0.28.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| config | object | `{"caCert":"","caCertFile":"","debugLevel":"2","ldapHost":"","ldapPort":"389","natsMaxRetryCount":"3","natsRetryDelay":"10","nats_max_reconnect_attempts":"5","notifierServer":"ldap-notifier","provisioningApiHost":"provisioning-api","provisioningApiPort":"80","secretMountPath":"/var/secrets","tlsMode":"off"}` | Configuration of the UDM Listener that is notified on LDAP changes |
| config.caCert | string | `""` | CA root certificate, base64-encoded. Optional; will be written to "caCertFile" if set. |
| config.caCertFile | string | `""` | Where to search for the CA Certificate file. caCertFile: "/var/secrets/ca_cert" |
| config.ldapHost | string | `""` | The LDAP Server host, should point to the service name of the ldap-server-primary that the ldap-notifier is sharing a volume with. Example: "ldap-server-notifier" |
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
| global.imagePullPolicy | string | `nil` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| global.nubusDeployment | bool | `false` | Indicates wether this chart is part of a Nubus deployment. |
| image.imagePullPolicy | string | `nil` |  |
| image.registry | string | `""` |  |
| image.repository | string | `"nubus-dev/images/provisioning-udm-listener"` |  |
| image.tag | string | `"0.60.13-pre-jlohmer-nats-secrets@sha256:4d9894d4ae020450777d51c9a271b1707b25206ccece1dd90b97a9fafb5787be"` |  |
| imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| ldap | object | `{"auth":{"bindDn":"cn=admin,{{ include \"udm-listener.ldapBaseDn\" . }}","existingSecret":{"keyMapping":{"password":null},"name":null},"password":null},"tlsSecret":{"caCertKey":"ca.crt","name":""}}` | LDAP client access configuration. This value is in a transition towards the unified configuration structure for clients and secrets. |
| livenessProbe.enabled | bool | `true` | Enable liveness probe. |
| livenessProbe.exec.command[0] | string | `"sh"` |  |
| livenessProbe.exec.command[1] | string | `"-c"` |  |
| livenessProbe.exec.command[2] | string | `"exit 0\n"` |  |
| livenessProbe.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| livenessProbe.initialDelaySeconds | int | `15` | Delay after container start until LivenessProbe is executed. |
| livenessProbe.periodSeconds | int | `20` | Time between probe executions. |
| livenessProbe.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| livenessProbe.timeoutSeconds | int | `5` | Timeout for command return. |
| mountSecrets | bool | `true` |  |
| nameOverride | string | `""` |  |
| nats | object | `{"auth":{"existingSecret":{"keyMapping":{"password":null},"name":null},"password":null,"user":"udmlistener"},"connection":{"host":null,"port":"4222"}}` | NATS client access configuration. This value is in a transition towards the unified configuration structure for clients and secrets. |
| nodeSelector | object | `{}` |  |
| persistence.size | string | `"1Gi"` | Specify PVCs size |
| persistence.storageClass | string | `""` | Specify storageClassName - Leave empty to use the default storage class |
| podAnnotations | object | `{}` |  |
| podSecurityContext.enabled | bool | `true` | Enable security context. |
| podSecurityContext.fsGroup | int | `65534` | If specified, all processes of the container are also part of the supplementary group. |
| podSecurityContext.fsGroupChangePolicy | string | `"Always"` | Change ownership and permission of the volume before being exposed inside a Pod. |
| podSecurityContext.sysctls | list | `[]` | Allow binding to ports below 1024 without root access. |
| readinessProbe.enabled | bool | `true` | Enable readiness probe. |
| readinessProbe.exec.command[0] | string | `"sh"` |  |
| readinessProbe.exec.command[1] | string | `"-c"` |  |
| readinessProbe.exec.command[2] | string | `"exit 0\n"` |  |
| readinessProbe.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| readinessProbe.initialDelaySeconds | int | `15` | Delay after container start until ReadinessProbe is executed. |
| readinessProbe.periodSeconds | int | `20` | Time between probe executions. |
| readinessProbe.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| readinessProbe.timeoutSeconds | int | `5` | Timeout for command return. |
| replicaCount | int | `1` |  |
| resources.limits.cpu | string | `"2"` |  |
| resources.limits.memory | string | `"4Gi"` |  |
| resources.requests.cpu | string | `"1"` |  |
| resources.requests.memory | string | `"512Mi"` |  |
| securityContext | object | `{}` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automountServiceAccountToken | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` |  |
| startupProbe.enabled | bool | `true` | Enable startup probe. |
| startupProbe.exec.command[0] | string | `"sh"` |  |
| startupProbe.exec.command[1] | string | `"-c"` |  |
| startupProbe.exec.command[2] | string | `"exit 0\n"` |  |
| startupProbe.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| startupProbe.initialDelaySeconds | int | `15` | Delay after container start until StartupProbe is executed. |
| startupProbe.periodSeconds | int | `20` | Time between probe executions. |
| startupProbe.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| startupProbe.timeoutSeconds | int | `5` | Timeout for command return. |
| terminationGracePeriodSeconds | string | `""` | In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods |
| tolerations | list | `[]` |  |
| topologySpreadConstraints | list | `[]` | Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule |
| waitForDependency.image.pullPolicy | string | `nil` |  |
| waitForDependency.image.registry | string | `nil` |  |
| waitForDependency.image.repository | string | `"nubus/images/wait-for-dependency"` |  |
| waitForDependency.image.tag | string | `"0.35.0@sha256:61dfaea28a2b150459138dfd6a554ce53850cee05ef2a72ab47bbe23f2a92d0d"` |  |
| waitForDependency.resources.limits.cpu | string | `"500m"` |  |
| waitForDependency.resources.limits.memory | string | `"512Mi"` |  |
| waitForDependency.resources.requests.cpu | string | `"100m"` |  |
| waitForDependency.resources.requests.memory | string | `"256Mi"` |  |
