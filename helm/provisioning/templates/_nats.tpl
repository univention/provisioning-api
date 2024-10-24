{{/*
Provisioning NATS admin credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.admin.name" -}}

{{- if .Values.nats.auth.admin.name -}}
  {{- .Values.nats.auth.admin.name -}}
{{- else if .Values.global.nats.auth.admin.name -}}
  {{- .Values.global.nats.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-nats-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.admin key
*/}}
{{- define "provisioning.nats.auth.admin.key" -}}

{{- if .Values.nats.auth.admin.key -}}
  {{- .Values.nats.auth.admin.key -}}
{{- else if .Values.global.nats.auth.admin.key -}}
  {{- .Values.global.nats.auth.admin.key -}}
{{- else -}}
admin_password
{{- end -}}
{{- end -}}{{/*
Provisioning NATS API credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.provisioningApi.name" -}}

{{- if .Values.nats.auth.provisioningApi.name -}}
  {{- .Values.nats.auth.provisioningApi.name -}}
{{- else if .Values.global.nats.auth.provisioningApi.name -}}
  {{- .Values.global.nats.auth.provisioningApi.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-api-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.provisioningApi key
*/}}
{{- define "provisioning.nats.auth.provisioningApi.key" -}}

{{- if .Values.nats.auth.provisioningApi.key -}}
  {{- .Values.nats.auth.provisioningApi.key -}}
{{- else if .Values.global.nats.auth.provisioningApi.key -}}
  {{- .Values.global.nats.auth.provisioningApi.key -}}
{{- else -}}
NATS_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning NATS prefill credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.prefill.name" -}}

{{- if .Values.nats.auth.prefill.name -}}
  {{- .Values.nats.auth.prefill.name -}}
{{- else if .Values.global.nats.auth.prefill.name -}}
  {{- .Values.global.nats.auth.prefill.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-prefill-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.prefill key
*/}}
{{- define "provisioning.nats.auth.prefill.key" -}}

{{- if .Values.nats.auth.prefill.key -}}
  {{- .Values.nats.auth.prefill.key -}}
{{- else if .Values.global.nats.auth.prefill.key -}}
  {{- .Values.global.nats.auth.prefill.key -}}
{{- else -}}
NATS_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning NATS dispatcher credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.dispatcher.name" -}}

{{- if .Values.nats.auth.dispatcher.name -}}
  {{- .Values.nats.auth.dispatcher.name -}}
{{- else if .Values.global.nats.auth.dispatcher.name -}}
  {{- .Values.global.nats.auth.dispatcher.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-dispatcher-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.dispatcher key
*/}}
{{- define "provisioning.nats.auth.dispatcher.key" -}}

{{- if .Values.nats.auth.dispatcher.key -}}
  {{- .Values.nats.auth.dispatcher.key -}}
{{- else if .Values.global.nats.auth.dispatcher.key -}}
  {{- .Values.global.nats.auth.dispatcher.key -}}
{{- else -}}
NATS_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning NATS UDM transformer credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.udmTransformer.name" -}}

{{- if .Values.nats.auth.udmTransformer.name -}}
  {{- .Values.nats.auth.udmTransformer.name -}}
{{- else if .Values.global.nats.auth.udmTransformer.name -}}
  {{- .Values.global.nats.auth.udmTransformer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-udm-transformer-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.udmTransformer key
*/}}
{{- define "provisioning.nats.auth.udmTransformer.key" -}}

{{- if .Values.nats.auth.udmTransformer.key -}}
  {{- .Values.nats.auth.udmTransformer.key -}}
{{- else if .Values.global.nats.auth.udmTransformer.key -}}
  {{- .Values.global.nats.auth.udmTransformer.key -}}
{{- else -}}
NATS_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning NATS UDM listener credentials user credentials name
*/}}
{{- define "provisioning.nats.auth.udmListener.name" -}}

{{- if .Values.nats.auth.udmListener.name -}}
  {{- .Values.nats.auth.udmListener.name -}}
{{- else if .Values.global.nats.auth.udmListener.name -}}
  {{- .Values.global.nats.auth.udmListener.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-provisioning-udm-listener-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
nats.auth.udmListener key
*/}}
{{- define "provisioning.nats.auth.udmListener.key" -}}

{{- if .Values.nats.auth.udmListener.key -}}
  {{- .Values.nats.auth.udmListener.key -}}
{{- else if .Values.global.nats.auth.udmListener.key -}}
  {{- .Values.global.nats.auth.udmListener.key -}}
{{- else -}}
NATS_PASSWORD
{{- end -}}
{{- end -}}