# nats

A Helm Chart that deploys NATS

- **Version**: 0.1.2
- **Type**: application
- **AppVersion**:
- **Homepage:** <https://git.knut.univention.de/univention/customers/dataport/upx/nats-helm>

## TL;DR

```console
helm upgrade --install nats oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/nats-helm/charts/nats
```

## Introduction

This chart deploys a NATS server/cluster.

## Installing

To install the chart with the release name `nats`:

```console
helm upgrade --install nats oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/nats-helm/charts/nats
```

## Uninstalling

To uninstall the chart with the release name `nats`:

```console
helm uninstall nats
```

## Testing

### create stream

```
nats stream add teststream --subjects='testsubject.>' --storage=file --replicas=1 --ack --retention=limits --discard=old  --max-msg-size=-1 --max-msgs=-1 --max-msgs-per-subject=-1 --max-bytes=-1 --max-age=-1  --dupe-window="2m0s" --no-allow-rollup --no-deny-delete --no-deny-purge
```

### add consumer
```
nats consumer add teststream testconsumer --pull --deliver=all --ack=explicit --replay=instant --filter="" --max-deliver=-1 --max-pending=0 --no-headers-only --backoff=none
```

### publish message
```
echo $(date) | nats publish testsubject.test1
```
### consume message

```
nats consumer next teststream testconsumer
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
| oci://artifacts.software-univention.de/nubus/charts | nubus-common | ^0.25.x |

## Values

<table>
	<thead>
		<th>Key</th>
		<th>Type</th>
		<th>Default</th>
		<th>Description</th>
	</thead>
	<tbody>
		<tr>
			<td>additionalAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>additionalLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels to add to all deployed objects.</td>
		</tr>
		<tr>
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{
  "content": {
    "podAntiAffinity": {
      "requiredDuringSchedulingIgnoredDuringExecution": [
        {
          "labelSelector": {
            "matchExpressions": [
              {
                "key": "app.kubernetes.io/name",
                "operator": "In",
                "values": [
                  "nats"
                ]
              }
            ]
          },
          "topologyKey": "kubernetes.io/hostname"
        }
      ]
    }
  },
  "enabled": true
}
</pre>
</td>
			<td>Affinity for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/assign-pod-node/#affinity-and-anti-affinity Note: podAffinityPreset, podAntiAffinityPreset, and nodeAffinityPreset will be ignored when it's set.</td>
		</tr>
		<tr>
			<td>config.authorization.token</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.authorization.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.authorization.password</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.authorization.timeout</td>
			<td>float</td>
			<td><pre lang="json">
0.5
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.authorization.user</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.connect_retries</td>
			<td>int</td>
			<td><pre lang="json">
600
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.cluster.replicas</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.createUsers</td>
			<td>object</td>
			<td><pre lang="json">
{
  "adminUser": {
    "auth": {
      "existingSecret": {
        "keyMapping": {
          "password": null
        },
        "name": null
      },
      "password": null,
      "username": "admin"
    },
    "permissions": {
      "publish": "\u003e",
      "subscribe": "\u003e"
    }
  }
}
</pre>
</td>
			<td>Create additional nats users Ref: https://docs.nats.io/running-a-nats-service/configuration/securing_nats/auth_intro/username_password#multiple-users permissions, auth.username and auth.existingSecret.name are required. Example: createUsers:   normalUser:     permissions:       publish: ">"       subscribe: ">"     auth:       username: "admin"       existingSecret:         name: null         keyMapping:           password: null</td>
		</tr>
		<tr>
			<td>config.createUsers.adminUser.auth.existingSecret.name</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The name of an existing Secret to use for retrieving the password for the nats admin account.  "config.createUsers.adminUser.auth.password" will be ignored if this value is set.</td>
		</tr>
		<tr>
			<td>config.createUsers.adminUser.auth.password</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>The password used to authenticate with nats database. Either this value or an existing Secret has to be specified.</td>
		</tr>
		<tr>
			<td>config.createUsers.adminUser.auth.username</td>
			<td>string</td>
			<td><pre lang="json">
"admin"
</pre>
</td>
			<td>The nats admin username</td>
		</tr>
		<tr>
			<td>config.extraConfig</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.jetstream</td>
			<td>object</td>
			<td><pre lang="json">
{
  "enabled": true,
  "fileStore": {
    "dir": "/data"
  },
  "memoryStore": {
    "size": "256Mi"
  }
}
</pre>
</td>
			<td>JetStream configuration Ref: https://docs.nats.io/running-a-nats-service/configuration/resource_management</td>
		</tr>
		<tr>
			<td>config.lame_duck_duration</td>
			<td>string</td>
			<td><pre lang="json">
"30s"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.lame_duck_grace_period</td>
			<td>string</td>
			<td><pre lang="json">
"10s"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.tls.ca_file</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/ca.crt"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.tls.cert_file</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/tls.crt"
</pre>
</td>
			<td>Name of the certificate to mount, must be set if tls is enabled certificateSecret: ""</td>
		</tr>
		<tr>
			<td>config.tls.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.tls.key_file</td>
			<td>string</td>
			<td><pre lang="json">
"/certificates/tls.key"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.tls.verify</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>config.tls.verify_and_map</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>containerSecurityContext.allowPrivilegeEscalation</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Enable container privileged escalation.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.capabilities</td>
			<td>object</td>
			<td><pre lang="json">
{
  "drop": [
    "ALL"
  ]
}
</pre>
</td>
			<td>Security capabilities for container.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.readOnlyRootFilesystem</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Mounts the container's root filesystem as read-only.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process group id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsNonRoot</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Run container as a user.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.runAsUser</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>Process user id.</td>
		</tr>
		<tr>
			<td>containerSecurityContext.seccompProfile.type</td>
			<td>string</td>
			<td><pre lang="json">
"RuntimeDefault"
</pre>
</td>
			<td>Disallow custom Seccomp profile by setting it to RuntimeDefault.</td>
		</tr>
		<tr>
			<td>extraEnvVars</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Array with extra environment variables to add to containers.  extraEnvVars:   - name: FOO     value: "bar"</td>
		</tr>
		<tr>
			<td>extraSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify a secret to create (primarily intended to be used in development environments to provide custom certificates)</td>
		</tr>
		<tr>
			<td>extraVolumeMounts</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumeMounts.</td>
		</tr>
		<tr>
			<td>extraVolumes</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Optionally specify an extra list of additional volumes.</td>
		</tr>
		<tr>
			<td>global.imagePullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Define an ImagePullPolicy.  Ref.: https://kubernetes.io/docs/concepts/containers/images/#image-pull-policy  "IfNotPresent" => The image is pulled only if it is not already present locally. "Always" => Every time the kubelet launches a container, the kubelet queries the container image registry to             resolve the name to an image digest. If the kubelet has a container image with that exact digest cached             locally, the kubelet uses its cached image; otherwise, the kubelet pulls the image with the resolved             digest, and uses that image to launch the container. "Never" => The kubelet does not try fetching the image. If the image is somehow already present locally, the            kubelet attempts to start the container; otherwise, startup fails.</td>
		</tr>
		<tr>
			<td>global.imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>global.imageRegistry</td>
			<td>string</td>
			<td><pre lang="json">
"docker.io"
</pre>
</td>
			<td>Container registry address.</td>
		</tr>
		<tr>
			<td>global.nubusDeployment</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td>Indicates wether this chart is part of a Nubus deployment.</td>
		</tr>
		<tr>
			<td>imagePullSecrets</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Credentials to fetch images from private registry. Ref: https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/  imagePullSecrets:   - "docker-registry"</td>
		</tr>
		<tr>
			<td>lifecycleHooks</td>
			<td>object</td>
			<td><pre lang="json">
{
  "preStop": {
    "exec": {
      "command": [
        "nats-server",
        "-sl=ldm=/var/run/nats.pid"
      ]
    }
  }
}
</pre>
</td>
			<td>Lifecycle to automate configuration before or after startup.</td>
		</tr>
		<tr>
			<td>livenessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/healthz?js-enabled-only=true"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"monitor"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>livenessProbe.httpGet.scheme</td>
			<td>string</td>
			<td><pre lang="json">
"HTTP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>livenessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Delay after container start until LivenessProbe is executed.</td>
		</tr>
		<tr>
			<td>livenessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
30
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>livenessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>livenessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>String to partially override release name.</td>
		</tr>
		<tr>
			<td>nats.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>nats.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>nats.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"library/nats"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nats.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"2.11.6@sha256:ba50652d7781b9707997e5c0cb7ffacb88919e689594c65be580037e1f2468d7"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>natsBox.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>natsBox.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"natsio/nats-box"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.18.0-nonroot@sha256:eea818c6e5248aabbcabd41fa1496a618aab0377352c3b66a43f5ed3fa49e30b"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"256Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"10m"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>natsBox.resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"32Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Node labels for pod assignment. Ref: https://kubernetes.io/docs/user-guide/node-selection/</td>
		</tr>
		<tr>
			<td>persistence.accessModes</td>
			<td>list</td>
			<td><pre lang="json">
[
  "ReadWriteOnce"
]
</pre>
</td>
			<td>The volume access modes, some of "ReadWriteOnce", "ReadOnlyMany", "ReadWriteMany", "ReadWriteOncePod".  "ReadWriteOnce" => The volume can be mounted as read-write by a single node. ReadWriteOnce access mode still can                    allow multiple pods to access the volume when the pods are running on the same node. "ReadOnlyMany" => The volume can be mounted as read-only by many nodes. "ReadWriteMany" => The volume can be mounted as read-write by many nodes. "ReadWriteOncePod" => The volume can be mounted as read-write by a single Pod. Use ReadWriteOncePod access mode if                       you want to ensure that only one pod across whole cluster can read that PVC or write to it. </td>
		</tr>
		<tr>
			<td>persistence.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Annotations for the PVC.</td>
		</tr>
		<tr>
			<td>persistence.dataSource</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Custom PVC data source.</td>
		</tr>
		<tr>
			<td>persistence.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable data persistence (true) or use temporary storage (false).</td>
		</tr>
		<tr>
			<td>persistence.existingClaim</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>Use an already existing claim.</td>
		</tr>
		<tr>
			<td>persistence.labels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Labels for the PVC.</td>
		</tr>
		<tr>
			<td>persistence.selector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Selector to match an existing Persistent Volume (this value is evaluated as a template).  selector:   matchLabels:     app: my-app </td>
		</tr>
		<tr>
			<td>persistence.size</td>
			<td>string</td>
			<td><pre lang="json">
"10Gi"
</pre>
</td>
			<td>The volume size with unit.</td>
		</tr>
		<tr>
			<td>persistence.storageClassName</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>The (storage) class of PV.</td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Pod Annotations. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/</td>
		</tr>
		<tr>
			<td>podLabels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Pod Labels. Ref: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/</td>
		</tr>
		<tr>
			<td>podManagementPolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Parallel"
</pre>
</td>
			<td>Pod management policy. Parallel means that the pods are created in parallel and not in sequence. Ref: https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/</td>
		</tr>
		<tr>
			<td>podSecurityContext.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable security context.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroup</td>
			<td>int</td>
			<td><pre lang="json">
1000
</pre>
</td>
			<td>If specified, all processes of the container are also part of the supplementary group.</td>
		</tr>
		<tr>
			<td>podSecurityContext.fsGroupChangePolicy</td>
			<td>string</td>
			<td><pre lang="json">
"Always"
</pre>
</td>
			<td>Change ownership and permission of the volume before being exposed inside a Pod.</td>
		</tr>
		<tr>
			<td>podSecurityContext.sysctls</td>
			<td>list</td>
			<td><pre lang="json">
[
  {
    "name": "net.ipv4.ip_unprivileged_port_start",
    "value": "1"
  }
]
</pre>
</td>
			<td>Allow binding to ports below 1024 without root access.</td>
		</tr>
		<tr>
			<td>readinessProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
3
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/healthz?js-enabled-only=true"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"monitor"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>readinessProbe.httpGet.scheme</td>
			<td>string</td>
			<td><pre lang="json">
"HTTP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>readinessProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Delay after container start until ReadinessProbe is executed.</td>
		</tr>
		<tr>
			<td>readinessProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>readinessProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>readinessProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>reloader.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable the config reloader</td>
		</tr>
		<tr>
			<td>reloader.image.pullPolicy</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Image pull policy. This setting has higher precedence than global.imagePullPolicy.</td>
		</tr>
		<tr>
			<td>reloader.image.registry</td>
			<td>string</td>
			<td><pre lang="json">
null
</pre>
</td>
			<td>Container registry address. This setting has higher precedence than global.registry.</td>
		</tr>
		<tr>
			<td>reloader.image.repository</td>
			<td>string</td>
			<td><pre lang="json">
"natsio/nats-server-config-reloader"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>reloader.image.tag</td>
			<td>string</td>
			<td><pre lang="json">
"0.18.3@sha256:41271dc1b9e1027867ee0e63aa2866c89ca8272a4f88991f6ebec34eb12dee3b"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>reloader.resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"256Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>reloader.resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"10m"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>reloader.resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"32Mi"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>resources.limits.memory</td>
			<td>string</td>
			<td><pre lang="json">
"1Gi"
</pre>
</td>
			<td>The max number of RAM to consume.</td>
		</tr>
		<tr>
			<td>resources.requests.cpu</td>
			<td>string</td>
			<td><pre lang="json">
"100m"
</pre>
</td>
			<td>The number of CPUs which has to be available on the scheduled node.</td>
		</tr>
		<tr>
			<td>resources.requests.memory</td>
			<td>string</td>
			<td><pre lang="json">
"64Mi"
</pre>
</td>
			<td>The number of RAM which has to be available on the scheduled node.</td>
		</tr>
		<tr>
			<td>service.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom annotations.</td>
		</tr>
		<tr>
			<td>service.enabled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Enable kubernetes service creation.</td>
		</tr>
		<tr>
			<td>service.ports.client.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
4222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.client.port</td>
			<td>int</td>
			<td><pre lang="json">
4222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.client.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.cluster.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
6222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.cluster.port</td>
			<td>int</td>
			<td><pre lang="json">
6222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.cluster.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.monitor.containerPort</td>
			<td>int</td>
			<td><pre lang="json">
8222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.monitor.port</td>
			<td>int</td>
			<td><pre lang="json">
8222
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.ports.monitor.protocol</td>
			<td>string</td>
			<td><pre lang="json">
"TCP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>service.type</td>
			<td>string</td>
			<td><pre lang="json">
"ClusterIP"
</pre>
</td>
			<td>Choose the kind of Service, one of "ClusterIP", "NodePort" or "LoadBalancer".</td>
		</tr>
		<tr>
			<td>serviceAccount.annotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.automountServiceAccountToken</td>
			<td>bool</td>
			<td><pre lang="json">
false
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.create</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>serviceAccount.labels</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td>Additional custom labels for the ServiceAccount.</td>
		</tr>
		<tr>
			<td>serviceAccount.name</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>startupProbe.failureThreshold</td>
			<td>int</td>
			<td><pre lang="json">
90
</pre>
</td>
			<td>Number of failed executions until container is terminated.</td>
		</tr>
		<tr>
			<td>startupProbe.httpGet.path</td>
			<td>string</td>
			<td><pre lang="json">
"/healthz?js-enabled-only=true"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>startupProbe.httpGet.port</td>
			<td>string</td>
			<td><pre lang="json">
"monitor"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>startupProbe.httpGet.scheme</td>
			<td>string</td>
			<td><pre lang="json">
"HTTP"
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>startupProbe.initialDelaySeconds</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Delay after container start until StartupProbe is executed.</td>
		</tr>
		<tr>
			<td>startupProbe.periodSeconds</td>
			<td>int</td>
			<td><pre lang="json">
10
</pre>
</td>
			<td>Time between probe executions.</td>
		</tr>
		<tr>
			<td>startupProbe.successThreshold</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td>Number of successful executions after failed ones until container is marked healthy.</td>
		</tr>
		<tr>
			<td>startupProbe.timeoutSeconds</td>
			<td>int</td>
			<td><pre lang="json">
5
</pre>
</td>
			<td>Timeout for command return.</td>
		</tr>
		<tr>
			<td>terminationGracePeriodSeconds</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td>In seconds, time the given to the pod needs to terminate gracefully. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods</td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Tolerations for pod assignment. Ref: https://kubernetes.io/docs/concepts/configuration/taint-and-toleration/</td>
		</tr>
		<tr>
			<td>topologySpreadConstraints</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td>Topology spread constraints rely on node labels to identify the topology domain(s) that each Node is in. Ref: https://kubernetes.io/docs/concepts/workloads/pods/pod-topology-spread-constraints/  topologySpreadConstraints:   - maxSkew: 1     topologyKey: failure-domain.beta.kubernetes.io/zone     whenUnsatisfiable: DoNotSchedule</td>
		</tr>
		<tr>
			<td>updateStrategy.type</td>
			<td>string</td>
			<td><pre lang="json">
"RollingUpdate"
</pre>
</td>
			<td>Set to Recreate if you use persistent volume that cannot be mounted by more than one pods to make sure the pods are destroyed first.</td>
		</tr>
	</tbody>
</table>

