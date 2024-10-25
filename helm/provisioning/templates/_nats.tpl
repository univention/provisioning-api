{{/*
Provisioning NATS admin user credentials name
*/}}
{{- define "provisioning.nats.auth.admin.name" -}}

{{- if .Values.global.nats.auth.admin.name -}}
  {{- .Values.global.nats.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-nats-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning NATS API user credentials name
*/}}
{{- define "provisioning.nats.auth.provisioningApi.name" -}}

{{- if .Values.global.nats.auth.provisioningApi.name -}}
  {{- .Values.global.nats.auth.provisioningApi.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning NATS prefill user credentials name
*/}}
{{- define "provisioning.nats.auth.prefill.name" -}}

{{- if .Values.global.nats.auth.prefill.name -}}
  {{- .Values.global.nats.auth.prefill.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-prefill-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning NATS dispatcher user credentials name
*/}}
{{- define "provisioning.nats.auth.dispatcher.name" -}}

{{- if .Values.global.nats.auth.dispatcher.name -}}
  {{- .Values.global.nats.auth.dispatcher.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-dispatcher-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning NATS UDM transformer user credentials name
*/}}
{{- define "provisioning.nats.auth.udmTransformer.name" -}}

{{- if .Values.global.nats.auth.udmTransformer.name -}}
  {{- .Values.global.nats.auth.udmTransformer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-udm-transformer-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
Provisioning NATS UDM listener user credentials name
*/}}
{{- define "provisioning.nats.auth.udmListener.name" -}}

{{- if .Values.global.nats.auth.udmListener.name -}}
  {{- .Values.global.nats.auth.udmListener.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-udm-listener-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}
