{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
These template definitions relate to the use of this Helm chart as a sub-chart of the Nubus Umbrella Chart.
They are defined so other sub-charts can read information that otherwise would be solely known to this Helm chart.
If compatible Helm charts set .Values.global.nubusDeployment to true, the templates defined here will be imported.
*/}}
{{- define "nubusTemplates.nats.connection.host" -}}
{{- printf "%s-provsioning-nats" .Release.Name -}}
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
{{- required "Either .Values.dispatcher.config.UDM_HOST or .Values.prefill.config.UDM_HOST must be defined." (coalesce .Values.dispatcher.config.UDM_HOST .Values.prefill.config.UDM_HOST) -}}
{{- end -}}
{{- end -}}

{{- define "provisioning.udmRestApi.port" -}}
{{- if .Values.global.nubusDeployment -}}
{{- include "nubusTemplates.udmRestApi.port" . -}}
{{- else -}}
{{- required "Either .Values.dispatcher.config.UDM_PORT or .Values.prefill.config.UDM_PORT must be defined." (coalesce .Values.dispatcher.config.UDM_PORT .Values.prefill.config.UDM_PORT) -}}
{{- end -}}
{{- end -}}

{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "provisioning-dispatcher.credentialSecretName" -}}
{{- coalesce .Values.dispatcher.credentialSecretName (printf "%s-provisioning-dispatcher-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-api.credentialSecretName" -}}
{{- coalesce .Values.api.credentialSecretName (printf "%s-provisioning-api-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-prefill.credentialSecretName" -}}
{{- coalesce .Values.prefill.credentialSecretName (printf "%s-provisioning-prefill-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.credentialSecretName" -}}
{{- coalesce .Values.register_consumers.credentialSecretName (printf "%s-provisioning-register-consumers-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.jsonSecretName" -}}
{{- coalesce .Values.register_consumers.jsonSecretName (printf "%s-provisioning-register-consumers-json-secrets" .Release.Name) -}}
{{- end -}}
