# dispatcher

![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.16.0](https://img.shields.io/badge/AppVersion-1.16.0-informational?style=flat-square)

A Helm chart for the Univention Portal Provisioning API

**Homepage:** <https://www.univention.de/>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | ums-common(common) | ^0.2.0 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| config | object | `{"natsHost":"localhost","natsPort":4222}` | Configuration of the dispatcher component |
| config.natsHost | string | `"localhost"` | NATS: host (required if nats.bundled == false) |
| config.natsPort | int | `4222` | NATS: port (required if nats.bundled == false) |
| environment | object | `{}` |  |
| fullnameOverride | string | `"provisioning-dispatcher"` |  |
| image.imagePullPolicy | string | `"Always"` |  |
| image.registry | string | `"gitregistry.knut.univention.de"` |  |
| image.repository | string | `"univention/customers/dataport/upx/provisioning-api/provisioning-dispatcher"` |  |
| image.tag | string | `"latest"` |  |
| nameOverride | string | `""` |  |
| nats.bundled | bool | `true` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
| probes.liveness.enabled | bool | `true` |  |
| probes.liveness.failureThreshold | int | `3` |  |
| probes.liveness.initialDelaySeconds | int | `120` |  |
| probes.liveness.periodSeconds | int | `30` |  |
| probes.liveness.successThreshold | int | `1` |  |
| probes.liveness.timeoutSeconds | int | `3` |  |
| probes.readiness.enabled | bool | `true` |  |
| probes.readiness.failureThreshold | int | `30` |  |
| probes.readiness.initialDelaySeconds | int | `30` |  |
| probes.readiness.periodSeconds | int | `15` |  |
| probes.readiness.successThreshold | int | `1` |  |
| probes.readiness.timeoutSeconds | int | `3` |  |
| replicaCount | int | `1` |  |
| resources.limits.memory | string | `"4Gi"` |  |
| resources.requests.memory | string | `"512Mi"` |  |
| securityContext | object | `{}` |  |
| service.enabled | bool | `true` |  |
| service.ports.http.containerPort | int | `8080` |  |
| service.ports.http.port | int | `80` |  |
| service.ports.http.protocol | string | `"TCP"` |  |
| service.sessionAffinity.enabled | bool | `false` |  |
| service.sessionAffinity.timeoutSeconds | int | `10800` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.11.3](https://github.com/norwoodj/helm-docs/releases/v1.11.3)