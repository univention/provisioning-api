# provisioning

![Version: 0.13.0](https://img.shields.io/badge/Version-0.13.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A Helm Chart that deploys the provisioning services

## Source Code

* <https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/-/tree/main/helm/provisioning?ref_type=heads>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://registry.souvap-univention.de/souvap/tooling/charts/bitnami-charts | common | ^2.x.x |
| oci://registry.souvap-univention.de/souvap/tooling/charts/univention | nats | 0.0.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| additionalAnnotations | object | `{}` | Additional custom annotations to add to all deployed objects. |
| additionalLabels | object | `{}` | Additional custom labels to add to all deployed objects. |
| affinity | object | `{}` | Affinity for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity Note: podAffinityPreset, podAntiAffinityPreset, and nodeAffinityPreset will be ignored when it's set. |
| api.config.CORS_ALL | string | `"false"` |  |
| api.config.DEBUG | string | `"true"` |  |
| api.config.LOG_LEVEL | string | `"INFO"` |  |
| api.config.ROOT_PATH | string | `"/univention/provisioning-api"` |  |
| api.credentialSecretName | string | `""` |  |
| api.image.imagePullPolicy | string | `"IfNotPresent"` |  |
| api.image.registry | string | `""` |  |
| api.image.repository | string | `"univention/customers/dataport/upx/provisioning/provisioning-events-and-consumer-api"` |  |
| api.image.tag | string | `"0.14.0"` |  |
| containerSecurityContext.allowPrivilegeEscalation | bool | `false` | Enable container privileged escalation. |
| containerSecurityContext.capabilities | object | `{"drop":["ALL"]}` | Security capabilities for container. |
| containerSecurityContext.enabled | bool | `true` | Enable security context. |
| containerSecurityContext.readOnlyRootFilesystem | bool | `true` | Mounts the container's root filesystem as read-only. |
| containerSecurityContext.runAsGroup | int | `1000` | Process group id. |
| containerSecurityContext.runAsNonRoot | bool | `true` | Run container as a user. |
| containerSecurityContext.runAsUser | int | `1000` | Process user id. |
| containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` | Disallow custom Seccomp profile by setting it to RuntimeDefault. |
| dispatcher.config.LOG_LEVEL | string | `"INFO"` |  |
| dispatcher.config.UDM_HOST | string | `""` |  |
| dispatcher.config.UDM_PASSWORD | string | `nil` |  |
| dispatcher.config.UDM_PORT | int | `9979` |  |
| dispatcher.config.UDM_USERNAME | string | `"cn=admin"` |  |
| dispatcher.credentialSecretName | string | `""` |  |
| dispatcher.image.imagePullPolicy | string | `"IfNotPresent"` |  |
| dispatcher.image.registry | string | `""` |  |
| dispatcher.image.repository | string | `"univention/customers/dataport/upx/provisioning/provisioning-dispatcher"` |  |
| dispatcher.image.tag | string | `"0.14.0"` |  |
| extraEnvVars | list | `[]` | Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar" |
| extraSecrets | list | `[]` | Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates) |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` | Provide a name to substitute for the full names of resources. |
| global.configMapUcr | string | `"stack-data-swp-ucr"` |  |
| global.configMapUcrDefaults | string | `"stack-data-ums-ucr"` |  |
| global.configMapUcrForced | string | `nil` |  |
| global.imagePullPolicy | string | `"IfNotPresent"` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `""` | Container registry address. |
| imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| ingress.annotations | object | `{}` | Define custom ingress annotations. annotations:   nginx.ingress.kubernetes.io/rewrite-target: / |
| ingress.enabled | bool | `false` | Enable creation of Ingress. |
| ingress.host | string | `""` | Define the Fully Qualified Domain Name (FQDN) where application should be reachable. |
| ingress.ingressClassName | string | `"nginx"` | The Ingress controller class name. |
| ingress.pathType | string | `"Prefix"` | Each path in an Ingress is required to have a corresponding path type. Paths that do not include an explicit pathType will fail validation. There are three supported path types:  "ImplementationSpecific" => With this path type, matching is up to the IngressClass. Implementations can treat this                             as a separate pathType or treat it identically to Prefix or Exact path types. "Exact" => Matches the URL path exactly and with case sensitivity. "Prefix" => Matches based on a URL path prefix split by /.  Ref.: https://kubernetes.io/docs/concepts/services-networking/ingress/#path-types |
| ingress.paths | list | `[]` | Define the Ingress path. |
| ingress.tls | object | `{"enabled":true,"secretName":""}` | Secure an Ingress by specifying a Secret that contains a TLS private key and certificate.  Ref.: https://kubernetes.io/docs/concepts/services-networking/ingress/#tls |
| ingress.tls.enabled | bool | `true` | Enable TLS/SSL/HTTPS for Ingress. |
| ingress.tls.secretName | string | `""` | The name of the kubernetes secret which contains a TLS private key and certificate. Hint: This secret is not created by this chart and must be provided. |
| istio.enabled | bool | `false` | Set this to `true` in order to enable the installation on Istio related objects. |
| istio.gateway.annotations | string | `nil` |  |
| istio.gateway.enabled | bool | `false` |  |
| istio.gateway.externalGatewayName | string | `"swp-istio-gateway"` |  |
| istio.gateway.selectorIstio | string | `"ingressgateway"` |  |
| istio.gateway.tls.enabled | bool | `true` |  |
| istio.gateway.tls.httpsRedirect | bool | `true` |  |
| istio.gateway.tls.secretName | string | `""` |  |
| istio.virtualService | object | `{"annotations":{},"enabled":true,"pathOverrides":[],"paths":[]}` | The hostname. This parameter has to be supplied. Example `portal.example`. host: provisioning.local |
| istio.virtualService.pathOverrides | list | `[]` | Allows to inject deployment specific path configuration which is configured before the elements from `paths` below. This allows to redirect some paths to other services, e.g. in order to supply a file `custom.css`. |
| istio.virtualService.paths | list | `[]` | The paths configuration. The default only grabs what is known to be part of the frontend.  `pathOverrides` is provided as a workaround so that specific sub-paths can be redirected to other services. |
| lifecycleHooks | object | `{}` | Lifecycle to automate configuration before or after startup. |
| livenessProbe.api.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| livenessProbe.api.initialDelaySeconds | int | `15` | Delay after container start until LivenessProbe is executed. |
| livenessProbe.api.periodSeconds | int | `20` | Time between probe executions. |
| livenessProbe.api.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| livenessProbe.api.tcpSocket.port | int | `7777` | The port to connect to the container. |
| livenessProbe.api.timeoutSeconds | int | `5` | Timeout for command return. |
| livenessProbe.dispatcher.exec.command[0] | string | `"sh"` |  |
| livenessProbe.dispatcher.exec.command[1] | string | `"-c"` |  |
| livenessProbe.dispatcher.exec.command[2] | string | `"exit 0\n"` |  |
| livenessProbe.dispatcher.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| livenessProbe.dispatcher.initialDelaySeconds | int | `15` | Delay after container start until LivenessProbe is executed. |
| livenessProbe.dispatcher.periodSeconds | int | `20` | Time between probe executions. |
| livenessProbe.dispatcher.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| livenessProbe.dispatcher.timeoutSeconds | int | `5` | Timeout for command return. |
| livenessProbe.prefill.exec.command[0] | string | `"sh"` |  |
| livenessProbe.prefill.exec.command[1] | string | `"-c"` |  |
| livenessProbe.prefill.exec.command[2] | string | `"exit 0\n"` |  |
| livenessProbe.prefill.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| livenessProbe.prefill.initialDelaySeconds | int | `15` | Delay after container start until LivenessProbe is executed. |
| livenessProbe.prefill.periodSeconds | int | `20` | Time between probe executions. |
| livenessProbe.prefill.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| livenessProbe.prefill.timeoutSeconds | int | `5` | Timeout for command return. |
| nameOverride | string | `"provisioning"` | String to partially override release name. |
| nats | object | `{"bundled":true,"config":{"cluster":{"replicas":1},"jetstream":{"enabled":true,"fileStorage":{"pvc":{"size":"1Gi"}}}},"connection":{"host":"","port":"","tls":{"caFile":"/certificates/ca.crt","certFile":"/certificates/tls.crt","enabled":false,"keyFile":"/certificates/tls.key"}},"nameOverride":"provisioning-nats"}` | NATS server settings. |
| nats.bundled | bool | `true` | Set to `true` if you want NATS to be installed as well. |
| nats.connection.host | string | `""` | The NATS service to connect to. |
| nats.connection.port | string | `""` | The port to connect to the NATS service. |
| nats.connection.tls | object | `{"caFile":"/certificates/ca.crt","certFile":"/certificates/tls.crt","enabled":false,"keyFile":"/certificates/tls.key"}` | The token to use when connecting to the NATS service. token: |
| nats.connection.tls.caFile | string | `"/certificates/ca.crt"` | The CA to verify the servers identity when initialising the connection. |
| nats.connection.tls.certFile | string | `"/certificates/tls.crt"` | The certificate to present when initialising the connection. |
| nats.connection.tls.keyFile | string | `"/certificates/tls.key"` | The private key to use for the connection. |
| nodeSelector | object | `{}` | Node labels for pod assignment. Ref: https://kubernetes.io/docs/user-guide/node-selection/ |
| podAnnotations | object | `{}` | Pod Annotations. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/ |
| podLabels | object | `{}` | Pod Labels. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ |
| podSecurityContext.enabled | bool | `true` | Enable security context. |
| podSecurityContext.fsGroup | int | `1000` | If specified, all processes of the container are also part of the supplementary group. |
| podSecurityContext.fsGroupChangePolicy | string | `"Always"` | Change ownership and permission of the volume before being exposed inside a Pod. |
| podSecurityContext.sysctls | list | `[{"name":"net.ipv4.ip_unprivileged_port_start","value":"1"}]` | Allow binding to ports below 1024 without root access. |
| prefill.config.LOG_LEVEL | string | `"INFO"` |  |
| prefill.config.UDM_HOST | string | `""` |  |
| prefill.config.UDM_PASSWORD | string | `nil` |  |
| prefill.config.UDM_PORT | int | `9979` |  |
| prefill.config.UDM_USERNAME | string | `"cn=admin"` |  |
| prefill.credentialSecretName | string | `""` |  |
| prefill.image.imagePullPolicy | string | `"IfNotPresent"` |  |
| prefill.image.registry | string | `""` |  |
| prefill.image.repository | string | `"univention/customers/dataport/upx/provisioning/provisioning-prefill"` |  |
| prefill.image.tag | string | `"0.14.0"` |  |
| readinessProbe.api.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| readinessProbe.api.initialDelaySeconds | int | `15` | Delay after container start until ReadinessProbe is executed. |
| readinessProbe.api.periodSeconds | int | `20` | Time between probe executions. |
| readinessProbe.api.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| readinessProbe.api.tcpSocket.port | int | `7777` | The port to connect to the container. |
| readinessProbe.api.timeoutSeconds | int | `5` | Timeout for command return. |
| readinessProbe.dispatcher.exec.command[0] | string | `"sh"` |  |
| readinessProbe.dispatcher.exec.command[1] | string | `"-c"` |  |
| readinessProbe.dispatcher.exec.command[2] | string | `"exit 0\n"` |  |
| readinessProbe.dispatcher.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| readinessProbe.dispatcher.initialDelaySeconds | int | `15` | Delay after container start until ReadinessProbe is executed. |
| readinessProbe.dispatcher.periodSeconds | int | `20` | Time between probe executions. |
| readinessProbe.dispatcher.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| readinessProbe.dispatcher.timeoutSeconds | int | `5` | Timeout for command return. |
| readinessProbe.prefill.exec.command[0] | string | `"sh"` |  |
| readinessProbe.prefill.exec.command[1] | string | `"-c"` |  |
| readinessProbe.prefill.exec.command[2] | string | `"exit 0\n"` |  |
| readinessProbe.prefill.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| readinessProbe.prefill.initialDelaySeconds | int | `15` | Delay after container start until ReadinessProbe is executed. |
| readinessProbe.prefill.periodSeconds | int | `20` | Time between probe executions. |
| readinessProbe.prefill.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| readinessProbe.prefill.timeoutSeconds | int | `5` | Timeout for command return. |
| replicaCount | object | `{"api":1,"dispatcher":1,"prefill":1}` | Set the amount of replicas of deployment. |
| resources.api | object | `{}` |  |
| resources.dispatcher | object | `{}` |  |
| resources.prefill | object | `{}` |  |
| service.annotations | object | `{}` | Additional custom annotations. |
| service.enabled | bool | `true` | Enable kubernetes service creation. |
| service.ports.http.containerPort | int | `7777` | Internal port. |
| service.ports.http.port | int | `80` | Accessible port. |
| service.ports.http.protocol | string | `"TCP"` | service protocol. |
| service.type | string | `"ClusterIP"` | Choose the kind of Service, one of "ClusterIP", "NodePort" or "LoadBalancer". |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automountServiceAccountToken | bool | `false` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.labels | object | `{}` | Additional custom labels for the ServiceAccount. |
| serviceAccount.name | string | `""` |  |
| startupProbe.api.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| startupProbe.api.initialDelaySeconds | int | `15` | Delay after container start until StartupProbe is executed. |
| startupProbe.api.periodSeconds | int | `20` | Time between probe executions. |
| startupProbe.api.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| startupProbe.api.tcpSocket | object | `{"port":7777}` | Timeout for command return. |
| startupProbe.api.tcpSocket.port | int | `7777` | The port to connect to the container. |
| startupProbe.dispatcher.exec.command[0] | string | `"sh"` |  |
| startupProbe.dispatcher.exec.command[1] | string | `"-c"` |  |
| startupProbe.dispatcher.exec.command[2] | string | `"exit 0\n"` |  |
| startupProbe.dispatcher.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| startupProbe.dispatcher.initialDelaySeconds | int | `15` | Delay after container start until StartupProbe is executed. |
| startupProbe.dispatcher.periodSeconds | int | `20` | Time between probe executions. |
| startupProbe.dispatcher.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| startupProbe.dispatcher.timeoutSeconds | int | `5` | Timeout for command return. |
| startupProbe.prefill.exec.command[0] | string | `"sh"` |  |
| startupProbe.prefill.exec.command[1] | string | `"-c"` |  |
| startupProbe.prefill.exec.command[2] | string | `"exit 0\n"` |  |
| startupProbe.prefill.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| startupProbe.prefill.initialDelaySeconds | int | `15` | Delay after container start until StartupProbe is executed. |
| startupProbe.prefill.periodSeconds | int | `20` | Time between probe executions. |
| startupProbe.prefill.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| startupProbe.prefill.timeoutSeconds | int | `5` | Timeout for command return. |
| terminationGracePeriodSeconds | string | `""` | In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods |
| tolerations | list | `[]` | Tolerations for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/ |
| topologySpreadConstraints | list | `[]` | Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule |
| updateStrategy.type | string | `"RollingUpdate"` | Set to Recreate if you use persistent volume that cannot be mounted by more than one pods to make sure the pods are destroyed first. |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.11.3](https://github.com/norwoodj/helm-docs/releases/v1.11.3)
