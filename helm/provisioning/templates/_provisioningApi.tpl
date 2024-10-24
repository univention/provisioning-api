{{/*
Provisioning API admin credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.admin.name" -}}

{{- if .Values.provisioningApi.auth.admin.name -}}
  {{- .Values.provisioningApi.auth.admin.name -}}
{{- else if .Values.global.provisioningApi.auth.admin.name -}}
  {{- .Values.global.provisioningApi.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
provisioningApi.auth.admin key
*/}}
{{- define "provisioning.provisioningApi.auth.admin.key" -}}

{{- if .Values.provisioningApi.auth.admin.key -}}
  {{- .Values.provisioningApi.auth.admin.key -}}
{{- else if .Values.global.provisioningApi.auth.admin.key -}}
  {{- .Values.global.provisioningApi.auth.admin.key -}}
{{- else -}}
ADMIN_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning API events UDM credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.eventsUdm.name" -}}

{{- if .Values.provisioningApi.auth.eventsUdm.name -}}
  {{- .Values.provisioningApi.auth.eventsUdm.name -}}
{{- else if .Values.global.provisioningApi.auth.eventsUdm.name -}}
  {{- .Values.global.provisioningApi.auth.eventsUdm.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
provisioningApi.auth.eventsUdm key
*/}}
{{- define "provisioning.provisioningApi.auth.eventsUdm.key" -}}

{{- if .Values.provisioningApi.auth.eventsUdm.key -}}
  {{- .Values.provisioningApi.auth.eventsUdm.key -}}
{{- else if .Values.global.provisioningApi.auth.eventsUdm.key -}}
  {{- .Values.global.provisioningApi.auth.eventsUdm.key -}}
{{- else -}}
EVENTS_PASSWORD_UDM
{{- end -}}
{{- end -}}{{/*
Provisioning API prefill credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.prefill.name" -}}

{{- if .Values.provisioningApi.auth.prefill.name -}}
  {{- .Values.provisioningApi.auth.prefill.name -}}
{{- else if .Values.global.provisioningApi.auth.prefill.name -}}
  {{- .Values.global.provisioningApi.auth.prefill.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
provisioningApi.auth.prefill key
*/}}
{{- define "provisioning.provisioningApi.auth.prefill.key" -}}

{{- if .Values.provisioningApi.auth.prefill.key -}}
  {{- .Values.provisioningApi.auth.prefill.key -}}
{{- else if .Values.global.provisioningApi.auth.prefill.key -}}
  {{- .Values.global.provisioningApi.auth.prefill.key -}}
{{- else -}}
PREFILL_PASSWORD
{{- end -}}
{{- end -}}