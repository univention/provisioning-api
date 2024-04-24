# udm-listener

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
| config | object | `{"caCert":"","caCertFile":"","debugLevel":"4","eventsPasswordUdm":"udmpass","eventsUsernameUdm":"udm","internalApiHost":"provisioning-api","internalApiPort":"80","ldapBaseDn":null,"ldapHost":"","ldapHostDn":null,"ldapHostIp":null,"ldapPassword":"","ldapPasswordFile":"/var/secrets/ldap_secret","ldapPort":"389","natsHost":null,"natsPassword":"password","natsPort":"4222","natsUser":"udmlistener","notifierServer":"ldap-notifier","provisioningApi":{"auth":{"credentialSecret":{"name":"","passwordKey":"EVENTS_PASSWORD_UDM","userNameKey":"EVENTS_USERNAME_UDM"}}},"secretMountPath":"/var/secrets","tlsMode":"off"}` | Configuration of the UDM Listener that is notified on LDAP changes |
| config.caCert | string | `""` | CA root certificate, base64-encoded. Optional; will be written to "caCertFile" if set. |
| config.caCertFile | string | `""` | Where to search for the CA Certificate file. caCertFile: "/var/secrets/ca_cert" |
| config.eventsUsernameUdm | string | `"udm"` | Messages-API Port |
| config.internalApiHost | string | `"provisioning-api"` | Messages-API Hostname |
| config.ldapHostIp | string | `nil` | Will add a mapping from "ldapHost" to "ldapHostIp" into "/etc/hosts" if set |
| config.ldapPassword | string | `""` | LDAP password for `cn=admin`. Will be written to "ldapPasswordFile" if set. |
| config.ldapPasswordFile | string | `"/var/secrets/ldap_secret"` | The path to the "ldapPasswordFile" docker secret or a plain file |
| config.natsHost | string | `nil` | NATS: host (required if nats.bundled == false) |
| config.natsPassword | string | `"password"` | NATS: password |
| config.natsPort | string | `"4222"` | NATS: port (required if nats.bundled == false) |
| config.natsUser | string | `"udmlistener"` | NATS: user name |
| config.notifierServer | string | `"ldap-notifier"` | Defaults to "ldapHost" if not set. |
| config.secretMountPath | string | `"/var/secrets"` | Path to mount the secrets to. |
| config.tlsMode | string | `"off"` | Whether to start encryption and validate certificates. Chose from "off", "unvalidated" and "secure". |
| environment | object | `{}` |  |
| fullnameOverride | string | `""` |  |
| global.nubusDeployment | bool | `false` | Indicates wether this chart is part of a Nubus deployment. |
| image.imagePullPolicy | string | `"Always"` |  |
| image.registry | string | `"gitregistry.knut.univention.de"` |  |
| image.repository | string | `"univention/customers/dataport/upx/provisioning/provisioning-udm-listener"` |  |
| image.tag | string | `"latest"` |  |
| ldap.credentialSecret.ldapPasswordKey | string | `"ldap.secret"` |  |
| ldap.credentialSecret.machinePasswordKey | string | `"machine.secret"` |  |
| ldap.credentialSecret.name | string | `""` |  |
| ldap.tlsSecret.caCertKey | string | `"ca.crt"` |  |
| ldap.tlsSecret.certificateKey | string | `"tls.crt"` |  |
| ldap.tlsSecret.name | string | `""` |  |
| ldap.tlsSecret.privateKeyKey | string | `"tls.key"` |  |
| mountSecrets | bool | `true` |  |
| nameOverride | string | `""` |  |
| nats.auth.credentialSecret.key | string | `"NATS_PASSWORD"` |  |
| nats.auth.credentialSecret.name | string | `""` |  |
| nats.bundled | bool | `true` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podSecurityContext | object | `{}` |  |
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
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| tolerations | list | `[]` |  |
