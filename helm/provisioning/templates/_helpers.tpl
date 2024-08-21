{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
They are defined so other sub-charts can read information that otherwise would be solely known to this Helm chart.
If compatible Helm charts set .Values.global.nubusDeployment to true, the templates defined here will be imported.
*/}}

{{- define "udm-transformer.configMapUcrDefaults" -}}
{{- $nubusDefaultConfigMapUcrDefaults := printf "%s-stack-data-ums-ucr" .Release.Name -}}
{{- tpl (coalesce .Values.configMapUcrDefaults .Values.global.configMapUcrDefaults $nubusDefaultConfigMapUcrDefaults (.Values.global.configMapUcrDefaults | required ".Values.global.configMapUcrDefaults must be defined.")) . -}}
{{- end -}}

{{- define "udm-transformer.configMapUcr" -}}
{{- $nubusDefaultConfigMapUcr := printf "%s-stack-data-ums-ucr" .Release.Name -}}
{{- tpl (coalesce .Values.configMapUcr .Values.global.configMapUcr $nubusDefaultConfigMapUcr) . -}}
{{- end -}}

{{- define "udm-transformer.configMapUcrForced" -}}
{{- tpl (coalesce .Values.configMapUcrForced .Values.global.configMapUcrForced | default "" ) . -}}
{{- end -}}

{{- define "nubusTemplates.nats.connection.host" -}}
{{- printf "%s-provisioning-nats" .Release.Name -}}
{{- end -}}

{{- define "nubusTemplates.nats.connection.port" -}}
4222
{{- end -}}

{{- define "nubusTemplates.provisioningApi.connection.host" -}}
{{ printf "%s-provisioning-api" .Release.Name }}
{{- end -}}

{{- define "nubusTemplates.provisioningApi.connection.port" -}}
80
{{- end -}}

{{- define "provisioning.udmRestApi.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.udmRestApi.host" . -}}
{{- else -}}
{{- required "Either .Values.registerConsumers.config.UDM_HOST or .Values.prefill.config.UDM_HOST must be defined." (coalesce .Values.registerConsumers.config.UDM_HOST .Values.prefill.config.UDM_HOST) -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmRestApi.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.udmRestApi.port" . -}}
{{- else -}}
{{- required "Either .Values.dispatcher.config.UDM_PORT or .Values.prefill.config.UDM_PORT must be defined." (coalesce .Values.dispatcher.config.UDM_PORT .Values.prefill.config.UDM_PORT) -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmTransformer.ldap.baseDn" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.baseDn" . -}}
{{- else -}}
{{- required ".Values.udmTransformer.ldap.baseDn must be defined." .Values.udmTransformer.ldap.baseDn -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmTransformer.ldap.auth.bindDn" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.adminDn" . -}}
{{- else -}}
{{- required ".Values.udmTransformer.ldap.auth.bindDn must be defined." .Values.udmTransformer.ldap.auth.bindDn -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmTransformer.ldap.connection.host" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.connections.ldap.primary.host" . -}}
{{- else -}}
{{- required ".Values.udmTransformer.ldap.connection.host must be defined." .Values.udmTransformer.ldap.connection.host -}}
{{- end -}}
{{- end -}}


{{- define "provisioning.udmTransformer.ldap.connection.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.ldapServer.ldap.connection.port" . -}}
{{- else -}}
{{- required ".Values.udmTransformer.ldap.connection.port must be defined." .Values.udmTransformer.ldap.connection.port -}}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "provisioning-dispatcher.credentialSecretName" -}}
{{- coalesce .Values.dispatcher.credentialSecretName (printf "%s-provisioning-dispatcher-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-udm-transformer.api.auth.credentialSecretName" -}}
{{- coalesce .Values.udmTransformer.api.auth.credentialSecretName (printf "%s-provisioning-udm-transformer-api-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-udm-transformer.nats.auth.credentialSecretName" -}}
{{- coalesce .Values.udmTransformer.nats.auth.credentialSecretName (printf "%s-provisioning-udm-transformer-nats-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-udm-transformer.ldap.auth.credentialSecretName" -}}
{{- coalesce .Values.udmTransformer.ldap.auth.credentialSecretName (printf "%s-provisioning-udm-transformer-ldap-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-api.credentialSecretName" -}}
{{- coalesce .Values.api.credentialSecretName (printf "%s-provisioning-api-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-prefill.credentialSecretName" -}}
{{- coalesce .Values.prefill.credentialSecretName (printf "%s-provisioning-prefill-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.credentialSecretName" -}}
{{- coalesce .Values.registerConsumers.credentialSecretName (printf "%s-provisioning-register-consumers-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.jsonSecretName" -}}
{{- coalesce .Values.registerConsumers.jsonSecretName (printf "%s-provisioning-register-consumers-json-secrets" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.provisioningApiBaseUrl" -}}
{{- if .Values.global.nubusDeployment -}}
{{ printf "http://%s-provisioning-api" .Release.Name }}
{{- else -}}
{{- required ".Values.registerConsumers.provisioningApiBaseUrl must be defined." .Values.registerConsumers.provisioningApiBaseUrl -}}
{{- end -}}
{{- end -}}
