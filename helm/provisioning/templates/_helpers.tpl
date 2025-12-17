{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
They are defined so other sub-charts can read information that otherwise would be solely known to this Helm chart.
If compatible Helm charts set .Values.global.nubusDeployment to true, the templates defined here will be imported.
*/}}

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
{{- required ".Values.prefill.config.UDM_HOST must be defined." .Values.prefill.config.UDM_HOST -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmRestApi.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.udmRestApi.port" . -}}
{{- else -}}
{{- required ".Values.prefill.config.UDM_PORT must be defined." .Values.prefill.config.UDM_PORT -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmTransformer.ldap.baseDn" -}}
{{- default "dc=univention-organization,dc=intranet"
      ( coalesce .Values.udmTransformer.ldap.baseDn (.Values.global.ldap).baseDn ) }}
{{- end -}}

{{- define "provisioning-register-consumers.provisioningApiBaseUrl" -}}
{{- if .Values.global.nubusDeployment -}}
{{ printf "http://%s-provisioning-api" .Release.Name }}
{{- else -}}
{{- required ".Values.registerConsumers.provisioningApiBaseUrl must be defined." .Values.registerConsumers.provisioningApiBaseUrl -}}
{{- end -}}
{{- end -}}
