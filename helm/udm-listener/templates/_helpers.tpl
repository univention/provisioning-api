{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
Templates defined in other Helm sub-charts are imported to be used to configure this chart.
If the value .Values.global.nubusDeployment equates to true, the defined templates are imported.
*/}}
{{- define "udm-listener.ldapBaseDn" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.baseDn" . -}}
{{- else if .Values.config.ldapBaseDn -}}
{{- .Values.config.ldapBaseDn -}}
{{- else -}}
dc=univention-organization,dc=intranet
{{- end -}}
{{- end -}}


{{- define "udm-listener.ldapAdminDn" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.adminDn" . -}}
{{- else if .Values.config.ldapHostDn -}}
{{- .Values.config.ldapHostDn -}}
{{- else -}}
cn=admin,dc=univention-organization,dc=intranet
{{- end -}}
{{- end -}}

{{- define "udm-listener.ldap.connection.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.connection.host" . -}}
{{- else if .Values.config.ldapHost -}}
{{- .Values.config.ldapHost -}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.ldap.connection.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.connection.port" . -}}
{{- else if .Values.config.ldapPort -}}
{{- .Values.config.ldapPort -}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.nats.connection.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.nats.connection.host" . -}}
{{- else -}}
{{ required ".Values.config.natsHost must be defined." .Values.config.natsHost}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.nats.connection.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.nats.connection.port" . -}}
{{- else -}}
{{ required ".Values.config.natsPort must be defined." .Values.config.natsPort}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.ldapNotifier.connection.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapNotifier.connection.host" . -}}
{{- else -}}
{{ required ".Values.config.notifierServer must be defined." .Values.config.notifierServer}}
{{- end -}}
{{- end -}}


{{- define "udm-listener.provisioningApi.connection.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.provisioningApi.connection.host" . -}}
{{- else -}}
{{ required ".Values.config.internalApiHost must be defined." .Values.config.internalApiHost}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.provisioningApi.connection.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.provisioningApi.connection.port" . -}}
{{- else -}}
{{ required ".Values.config.internalApiPort must be defined." .Values.config.internalApiPort}}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "udm-listener.tlsSecretTemplate" -}}
{{- if (index . 2).Release.Name -}}
{{- $secretName := printf "%s-%s-tls" (index . 2).Release.Name (index . 0) -}}
{{- if (index . 1).name -}}
{{- (index . 1).name -}}
{{- else if (index . 2).Values.global.nubusDeployment -}}
{{- $secretName -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.secretTemplate" -}}
{{- if (index . 2).Release.Name -}}
{{- $secretName := printf "%s-%s-credentials" (index . 2).Release.Name (index . 0) -}}
{{- if (index . 1).name -}}
{{- (index . 1).name -}}
{{- else if (index . 2).Values.global.nubusDeployment -}}
{{- $secretName -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "udm-listener.ldap.credentialSecret.name" -}}
{{- include "udm-listener.secretTemplate" (list "provisioning-udm-listener-ldap" .Values.ldap.credentialSecret .) -}}
{{- end -}}

{{- define "udm-listener.ldap.tlsSecret.name" -}}
{{- include "udm-listener.tlsSecretTemplate" (list "provisioning-udm-listener-ldap" .Values.ldap.tlsSecret .) -}}
{{- end -}}

{{- define "udm-listener.nats.auth.credentialSecret.name" -}}
{{- include "udm-listener.secretTemplate" (list "provisioning-udm-listener" .Values.nats.auth.credentialSecret .) -}}
{{- end -}}

{{- define "udm-listener.provisioningApi.auth.credentialSecret.name" -}}
{{- include "udm-listener.secretTemplate" (list "provisioning-udm-listener" .Values.config.provisioningApi.auth.credentialSecret .) -}}
{{- end -}}

{{- define "udm-listener.notifierServer" -}}
{{- if .Values.config.notifierServer -}}
{{- .Values.config.notifierServer -}}
{{- else -}}
{{- printf "%s-ldap-notifier" .Release.Name -}}
{{- end -}}
{{- end -}}
