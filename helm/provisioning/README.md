# provisioning

A Helm chart for the Univention Management Stack Provisioning Service

- **Version**: 0.1.0
- **Type**: application
- **Homepage:** <https://www.univention.de/>

## TL;DR

```console
helm repo add provisioning-api oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/provisioning-api/helm/provisioning-api
helm upgrade --install provisioning-api provisioning-api
```

## Introduction

This chart installs the Provisioning API of the Univention Management Stack.

## Installing

To install the chart with the release name `provisioning-api`:

```console
helm repo add univention-portal oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/provisioning-api/helm/provisioning-api
helm upgrade --install provisioning-api provisioning-api
```

By default the chart will install PostgreSQL as well. See the section [Values](#values)
regarding all available configuration options.

## Uninstalling

To uninstall the chart with the release name `provisioning-api`:

```console
helm uninstall provisioning-api
```

Note that persistent volume claims are not automatically deleted. This is
relevant if you did use the bundled PostgreSQL as a database.

```console
kubectl delete pvc -l release=provisioning-api
```

## Requirements

| Repository | Name | Version |
|------------|------|---------|
|  | dispatcher | * |
|  | events-and-consumer-api | * |
|  | udm-listener | * |
| https://nats-io.github.io/k8s/helm/charts/ | nats | ^1.1.5 |
| oci://gitregistry.knut.univention.de/univention/customers/dataport/upx/common-helm/helm | common | 0.* |

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
			<td>affinity</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>dispatcher</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>environment</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>events-and-consumer-api</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>fullnameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nameOverride</td>
			<td>string</td>
			<td><pre lang="json">
""
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>nats</td>
			<td>object</td>
			<td><pre lang="json">
{
  "bundled": true,
  "config": {
    "jetstream": {
      "enabled": true,
      "fileStorage": {
        "pvc": {
          "size": "1Gi"
        }
      }
    }
  },
  "container": {
    "image": {
      "registry": "docker.io",
      "repository": "nats",
      "tag": "2.10.5-alpine"
    }
  },
  "natsBox": {
    "container": {
      "image": {
        "registry": "docker.io",
        "repository": "natsio/nats-box",
        "tag": "0.14.1"
      }
    }
  },
  "reloader": {
    "image": {
      "registry": "docker.io",
      "repository": "natsio/nats-server-config-reloader",
      "tag": "0.14.0"
    }
  },
  "statefulSet": {
    "spec": {
      "template": {
        "spec": {
          "serviceAccountName": "nats"
        }
      }
    }
  }
}
</pre>
</td>
			<td>NATS server settings.</td>
		</tr>
		<tr>
			<td>nats.bundled</td>
			<td>bool</td>
			<td><pre lang="json">
true
</pre>
</td>
			<td>Set to `true` if you want NATS to be installed as well.</td>
		</tr>
		<tr>
			<td>nodeSelector</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podAnnotations</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>podSecurityContext</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>replicaCount</td>
			<td>int</td>
			<td><pre lang="json">
1
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>securityContext</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>tolerations</td>
			<td>list</td>
			<td><pre lang="json">
[]
</pre>
</td>
			<td></td>
		</tr>
		<tr>
			<td>udm-listener</td>
			<td>object</td>
			<td><pre lang="json">
{}
</pre>
</td>
			<td></td>
		</tr>
	</tbody>
</table>

