{{/*
Provisioning API admin credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.admin.name" -}}

{{- if .Values.api.auth.admin.name -}}
  {{- .Values.api.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning API events UDM credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.eventsUdm.name" -}}

{{- if .Values.api.auth.eventsUdm.name -}}
  {{- .Values.api.auth.eventsUdm.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning API prefill credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.prefill.name" -}}

{{- if .Values.api.auth.prefill.name -}}
  {{- .Values.api.auth.prefill.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}
