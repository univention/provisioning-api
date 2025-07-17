# provisioning

![Version: 0.45.0](https://img.shields.io/badge/Version-0.45.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square)

A Helm Chart that deploys the provisioning services

## Source Code

* <https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/-/tree/main/helm/provisioning?ref_type=heads>

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nats | 0.3.2 |
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | 0.21.1 |

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| additionalAnnotations | object | `{}` | Additional custom annotations to add to all deployed objects. |
| additionalLabels | object | `{}` | Additional custom labels to add to all deployed objects. |
| affinity | object | `{}` | Affinity for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity Note: podAffinityPreset, podAntiAffinityPreset, and nodeAffinityPreset will be ignored when it's set. |
| api.additionalAnnotations | object | `{}` |  |
| api.additionalLabels | object | `{}` |  |
| api.auth.admin.existingSecret.keyMapping.password | string | `nil` |  |
| api.auth.admin.existingSecret.name | string | `nil` |  |
| api.auth.admin.password | string | `nil` |  |
| api.auth.eventsUdm.existingSecret.keyMapping.password | string | `nil` |  |
| api.auth.eventsUdm.existingSecret.name | string | `nil` |  |
| api.auth.eventsUdm.password | string | `nil` |  |
| api.auth.prefill.existingSecret.keyMapping.password | string | `nil` |  |
| api.auth.prefill.existingSecret.name | string | `nil` |  |
| api.auth.prefill.password | string | `nil` |  |
| api.config.CORS_ALL | string | `"false"` |  |
| api.config.DEBUG | string | `"false"` |  |
| api.config.LOG_LEVEL | string | `"INFO"` |  |
| api.config.ROOT_PATH | string | `"/"` |  |
| api.image.pullPolicy | string | `nil` |  |
| api.image.registry | string | `""` |  |
| api.image.repository | string | `"nubus-dev/images/provisioning-events-and-consumer-api"` |  |
| api.image.tag | string | `"0.44.1@sha256:c34020a9c402e204948df782e161329bc4644442d680397d2736024881b9d766"` |  |
| api.nats.auth.existingSecret.keyMapping.provisioningApiPassword | string | `nil` |  |
| api.nats.auth.existingSecret.name | string | `nil` |  |
| api.nats.auth.password | string | `nil` |  |
| api.podAnnotations | object | `{}` |  |
| containerSecurityContext.allowPrivilegeEscalation | bool | `false` | Enable container privileged escalation. |
| containerSecurityContext.capabilities | object | `{"drop":["ALL"]}` | Security capabilities for container. |
| containerSecurityContext.enabled | bool | `true` | Enable security context. |
| containerSecurityContext.privileged | bool | `false` |  |
| containerSecurityContext.readOnlyRootFilesystem | bool | `true` | Mounts the container's root filesystem as read-only. |
| containerSecurityContext.runAsGroup | int | `1000` | Process group id. |
| containerSecurityContext.runAsNonRoot | bool | `true` | Run container as a user. |
| containerSecurityContext.runAsUser | int | `1000` | Process user id. |
| containerSecurityContext.seccompProfile.type | string | `"RuntimeDefault"` | Disallow custom Seccomp profile by setting it to RuntimeDefault. |
| dispatcher.additionalAnnotations | object | `{}` |  |
| dispatcher.additionalLabels | object | `{}` |  |
| dispatcher.config.LOG_LEVEL | string | `"INFO"` |  |
| dispatcher.config.natsMaxReconnectAttempts | int | `5` |  |
| dispatcher.image.pullPolicy | string | `nil` |  |
| dispatcher.image.registry | string | `""` |  |
| dispatcher.image.repository | string | `"nubus-dev/images/provisioning-dispatcher"` |  |
| dispatcher.image.tag | string | `"0.44.1@sha256:67289856a73701fae780f305cc86d627452812e86cd1e6abdb2893a5b74a6eb7"` |  |
| dispatcher.nats.auth.existingSecret.keyMapping.password | string | `nil` |  |
| dispatcher.nats.auth.existingSecret.name | string | `nil` |  |
| dispatcher.nats.auth.password | string | `nil` |  |
| dispatcher.podAnnotations | object | `{}` |  |
| extraEnvVars | list | `[]` | Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar" |
| extraSecrets | list | `[]` | Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates) |
| extraVolumeMounts | list | `[]` | Optionally specify an extra list of additional volumeMounts. |
| extraVolumes | list | `[]` | Optionally specify an extra list of additional volumes. |
| fullnameOverride | string | `""` | Provide a name to substitute for the full names of resources. |
| global.configMapUcr | string | `nil` |  |
| global.imagePullPolicy | string | `nil` | Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails. |
| global.imagePullSecrets | list | `[]` | Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry" |
| global.imageRegistry | string | `"artifacts.software-univention.de"` | Container registry address. |
| global.nats | object | `{"connection":{"host":"","port":""}}` | Define configuration regarding nats connectivity. |
| global.nubusDeployment | bool | `false` | Indicates wether this chart is part of a Nubus deployment. |
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
| livenessProbe.udmTransformer.exec.command[0] | string | `"sh"` |  |
| livenessProbe.udmTransformer.exec.command[1] | string | `"-c"` |  |
| livenessProbe.udmTransformer.exec.command[2] | string | `"exit 0\n"` |  |
| livenessProbe.udmTransformer.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| livenessProbe.udmTransformer.initialDelaySeconds | int | `15` | Delay after container start until LivenessProbe is executed. |
| livenessProbe.udmTransformer.periodSeconds | int | `20` | Time between probe executions. |
| livenessProbe.udmTransformer.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| livenessProbe.udmTransformer.timeoutSeconds | int | `5` | Timeout for command return. |
| nameOverride | string | `"provisioning"` | String to partially override release name. |
| nats | object | `{"affinity":{"enabled":true},"bundled":true,"config":{"authorization":{"enabled":true},"cluster":{"replicas":3},"createUsers":{"dispatcher":{"password":"$NATS_DISPATCHER_PASSWORD","permissions":{"publish":">","subscribe":">"},"user":"dispatcher"},"prefill":{"password":"$NATS_PREFILL_PASSWORD","permissions":{"publish":">","subscribe":">"},"user":"prefill"},"provisioningApi":{"password":"$NATS_PROVISIONING_API_PASSWORD","permissions":{"publish":">","subscribe":">"},"user":"api"},"udmTransformer":{"password":"$NATS_UDM_TRANSFORMER_PASSWORD","permissions":{"publish":">","subscribe":">"},"user":"udmtransformer"}},"extraConfig":{"max_payload":"16MB"},"jetstream":{"enabled":true}},"connection":{"host":"","port":"","tls":{"caFile":"/certificates/ca.crt","certFile":"/certificates/tls.crt","enabled":false,"keyFile":"/certificates/tls.key"}},"extraEnvVars":[{"name":"NATS_PASSWORD","valueFrom":{"secretKeyRef":{"key":null,"name":null}}},{"name":"NATS_PROVISIONING_API_PASSWORD","valueFrom":{"secretKeyRef":{"key":null,"name":null}}},{"name":"NATS_DISPATCHER_PASSWORD","valueFrom":{"secretKeyRef":{"key":null,"name":null}}},{"name":"NATS_UDM_TRANSFORMER_PASSWORD","valueFrom":{"secretKeyRef":{"key":null,"name":null}}},{"name":"NATS_PREFILL_PASSWORD","valueFrom":{"secretKeyRef":{"key":null,"name":null}}}],"nameOverride":"provisioning-nats","nats":{"image":{"registry":"docker.io"}},"natsBox":{"image":{"registry":"docker.io"}},"reloader":{"image":{"registry":"docker.io"}}}` | NATS server settings. |
| nats.bundled | bool | `true` | Set to `true` if you want NATS to be installed as well. |
| nats.config.cluster.replicas | int | `3` | Has to be set to at least 3, the minimum for nats clustering |
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
| prefill.additionalAnnotations | object | `{}` |  |
| prefill.additionalLabels | object | `{}` |  |
| prefill.config.LOG_LEVEL | string | `"INFO"` |  |
| prefill.config.UDM_HOST | string | `""` |  |
| prefill.config.UDM_PORT | int | `9979` |  |
| prefill.config.maxPrefillAttempts | int | `5` |  |
| prefill.config.natsMaxReconnectAttempts | int | `5` |  |
| prefill.image.pullPolicy | string | `nil` |  |
| prefill.image.registry | string | `""` |  |
| prefill.image.repository | string | `"nubus-dev/images/provisioning-prefill"` |  |
| prefill.image.tag | string | `"0.44.1@sha256:79a87775aa23fef2716203b2e38048ef75afe5d7ff3eb25c992bc6ec1041ea86"` |  |
| prefill.nats.auth.existingSecret.keyMapping.prefillPassword | string | `nil` |  |
| prefill.nats.auth.existingSecret.name | string | `nil` |  |
| prefill.nats.auth.password | string | `nil` |  |
| prefill.podAnnotations | object | `{}` |  |
| prefill.udm.auth.existingSecret.keyMapping.password | string | `nil` |  |
| prefill.udm.auth.existingSecret.name | string | `nil` |  |
| prefill.udm.auth.password | string | `nil` |  |
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
| readinessProbe.udmTransformer.exec.command[0] | string | `"sh"` |  |
| readinessProbe.udmTransformer.exec.command[1] | string | `"-c"` |  |
| readinessProbe.udmTransformer.exec.command[2] | string | `"exit 0\n"` |  |
| readinessProbe.udmTransformer.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| readinessProbe.udmTransformer.initialDelaySeconds | int | `15` | Delay after container start until ReadinessProbe is executed. |
| readinessProbe.udmTransformer.periodSeconds | int | `20` | Time between probe executions. |
| readinessProbe.udmTransformer.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| readinessProbe.udmTransformer.timeoutSeconds | int | `5` | Timeout for command return. |
| registerConsumers.additionalAnnotations | object | `{}` |  |
| registerConsumers.additionalLabels | object | `{}` |  |
| registerConsumers.config.UDM_HOST | string | `""` |  |
| registerConsumers.config.UDM_PORT | int | `9979` |  |
| registerConsumers.createUsers | object | `{}` | Allows to create users in the Provisioning API.  The entries have to be in the following structure:    consumerName:     existingSecret:       name: null       keyMapping:         registration: null  The entries can only be provided as existing secrets and the content of the key "registration" has to follow the correct JSON structure.  This parameter shall be used as an integration point between the consumer's chart and this chart. The consumer's chart owns the Secret and has to store the correct JSON data within the Secret. This chart only receives a reference this Secret so that it can register the consumer. |
| registerConsumers.image.pullPolicy | string | `nil` |  |
| registerConsumers.image.registry | string | `""` |  |
| registerConsumers.image.repository | string | `"nubus/images/wait-for-dependency"` |  |
| registerConsumers.image.tag | string | `"0.35.0@sha256:61dfaea28a2b150459138dfd6a554ce53850cee05ef2a72ab47bbe23f2a92d0d"` |  |
| registerConsumers.jsonSecretName | string | `""` |  |
| registerConsumers.podAnnotations | object | `{}` |  |
| registerConsumers.provisioningApiBaseUrl | string | `""` |  |
| registerConsumers.udm.auth.existingSecret.keyMapping.password | string | `nil` |  |
| registerConsumers.udm.auth.existingSecret.name | string | `nil` |  |
| registerConsumers.udm.auth.password | string | `nil` |  |
| replicaCount | object | `{"api":1,"dispatcher":1,"prefill":1,"udmTransformer":1}` | Set the amount of replicas of deployment. |
| resources.api.limits.cpu | int | `1` |  |
| resources.api.limits.memory | string | `"1Gi"` |  |
| resources.api.requests.cpu | float | `0.1` |  |
| resources.api.requests.memory | string | `"100Mi"` |  |
| resources.dispatcher.limits.cpu | int | `1` |  |
| resources.dispatcher.limits.memory | string | `"1Gi"` |  |
| resources.dispatcher.requests.cpu | float | `0.1` |  |
| resources.dispatcher.requests.memory | string | `"64Mi"` |  |
| resources.prefill.limits.cpu | int | `1` |  |
| resources.prefill.limits.memory | string | `"1Gi"` |  |
| resources.prefill.requests.cpu | float | `0.1` |  |
| resources.prefill.requests.memory | string | `"64Mi"` |  |
| resources.registerConsumers.limits.cpu | int | `1` |  |
| resources.registerConsumers.limits.memory | string | `"1Gi"` |  |
| resources.registerConsumers.requests.cpu | float | `0.1` |  |
| resources.registerConsumers.requests.memory | string | `"64Mi"` |  |
| resources.udmTransformer.limits.cpu | int | `1` |  |
| resources.udmTransformer.limits.memory | string | `"1Gi"` |  |
| resources.udmTransformer.requests.cpu | float | `0.1` |  |
| resources.udmTransformer.requests.memory | string | `"64Mi"` |  |
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
| startupProbe.udmTransformer.exec.command[0] | string | `"sh"` |  |
| startupProbe.udmTransformer.exec.command[1] | string | `"-c"` |  |
| startupProbe.udmTransformer.exec.command[2] | string | `"exit 0\n"` |  |
| startupProbe.udmTransformer.failureThreshold | int | `10` | Number of failed executions until container is terminated. |
| startupProbe.udmTransformer.initialDelaySeconds | int | `15` | Delay after container start until StartupProbe is executed. |
| startupProbe.udmTransformer.periodSeconds | int | `20` | Time between probe executions. |
| startupProbe.udmTransformer.successThreshold | int | `1` | Number of successful executions after failed ones until container is marked healthy. |
| startupProbe.udmTransformer.timeoutSeconds | int | `5` | Timeout for command return. |
| terminationGracePeriodSeconds | string | `""` | In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods |
| tolerations | list | `[]` | Tolerations for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/ |
| topologySpreadConstraints | list | `[]` | Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule |
| udmTransformer.additionalAnnotations | object | `{}` |  |
| udmTransformer.additionalLabels | object | `{}` |  |
| udmTransformer.config.LDAP_TLS_MODE | string | `"off"` | Whether to start ldap encryption and validate certificates. Chose from "off", "unvalidated" and "secure". |
| udmTransformer.config.LOG_LEVEL | string | `"INFO"` |  |
| udmTransformer.config.ldapPublisherName | string | `"udm-listener"` |  |
| udmTransformer.image.pullPolicy | string | `nil` |  |
| udmTransformer.image.registry | string | `""` |  |
| udmTransformer.image.repository | string | `"nubus-dev/images/provisioning-udm-transformer"` |  |
| udmTransformer.image.tag | string | `"0.44.1@sha256:2209558b3a544739b982637d57480951044247e3baae242d30e8e6437e9925c8"` |  |
| udmTransformer.ldap.auth.bindDn | string | `"cn=admin,{{ include \"provisioning.udmTransformer.ldap.baseDn\" . }}"` | LDAP username with global read access |
| udmTransformer.ldap.auth.existingSecret.keyMapping.password | string | `nil` |  |
| udmTransformer.ldap.auth.existingSecret.name | string | `nil` |  |
| udmTransformer.ldap.auth.password | string | `nil` |  |
| udmTransformer.ldap.baseDn | string | `""` |  |
| udmTransformer.ldap.connection.host | string | `""` |  |
| udmTransformer.ldap.connection.port | string | `""` |  |
| udmTransformer.nats.auth.existingSecret.keyMapping.password | string | `nil` |  |
| udmTransformer.nats.auth.existingSecret.name | string | `nil` |  |
| udmTransformer.nats.auth.password | string | `nil` |  |
| udmTransformer.podAnnotations | object | `{}` |  |
| updateStrategy.type | string | `"Recreate"` | Set to Recreate if you use persistent volume that cannot be mounted by more than one pods to make sure the pods are destroyed first. FIXME: Change to `RollingUpdate` after this bug is fixed https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/-/issues/70 |
