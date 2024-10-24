{{/*
Provisioning portal consumer credentials user credentials name
*/}}
{{- define "provisioning.provisioning.auth.portalConsumer.name" -}}

{{- if .Values.provisioning.auth.portalConsumer.name -}}
  {{- .Values.provisioning.auth.portalConsumer.name -}}
{{- else if .Values.global.provisioning.auth.portalConsumer.name -}}
  {{- .Values.global.provisioning.auth.portalConsumer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-portal-consumer-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
provisioning.auth.portalConsumer key
*/}}
{{- define "provisioning.provisioning.auth.portalConsumer.key" -}}

{{- if .Values.provisioning.auth.portalConsumer.key -}}
  {{- .Values.provisioning.auth.portalConsumer.key -}}
{{- else if .Values.global.provisioning.auth.portalConsumer.key -}}
  {{- .Values.global.provisioning.auth.portalConsumer.key -}}
{{- else -}}
PROVISIONING_API_PASSWORD
{{- end -}}
{{- end -}}{{/*
Provisioning self-service listener credentials user credentials name
*/}}
{{- define "provisioning.provisioning.auth.selfserviceConsumer.name" -}}

{{- if .Values.provisioning.auth.selfserviceConsumer.name -}}
  {{- .Values.provisioning.auth.selfserviceConsumer.name -}}
{{- else if .Values.global.provisioning.auth.selfserviceConsumer.name -}}
  {{- .Values.global.provisioning.auth.selfserviceConsumer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-selfservice-listener-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
provisioning.auth.selfserviceConsumer key
*/}}
{{- define "provisioning.provisioning.auth.selfserviceConsumer.key" -}}

{{- if .Values.provisioning.auth.selfserviceConsumer.key -}}
  {{- .Values.provisioning.auth.selfserviceConsumer.key -}}
{{- else if .Values.global.provisioning.auth.selfserviceConsumer.key -}}
  {{- .Values.global.provisioning.auth.selfserviceConsumer.key -}}
{{- else -}}
PROVISIONING_API_PASSWORD
{{- end -}}
{{- end -}}