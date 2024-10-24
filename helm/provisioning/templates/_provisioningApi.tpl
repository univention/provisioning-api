{{/*
Provisioning API admin credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.admin.name" -}}

{{- if .Values.provisioningApi.auth.admin.name -}}
  {{- .Values.provisioningApi.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning API events UDM credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.eventsUdm.name" -}}

{{- if .Values.provisioningApi.auth.eventsUdm.name -}}
  {{- .Values.provisioningApi.auth.eventsUdm.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning API prefill credentials user credentials name
*/}}
{{- define "provisioning.provisioningApi.auth.prefill.name" -}}

{{- if .Values.provisioningApi.auth.prefill.name -}}
  {{- .Values.provisioningApi.auth.prefill.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}
