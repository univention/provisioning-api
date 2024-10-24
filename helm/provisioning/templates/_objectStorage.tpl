{{/*
Minio provisioning account password user credentials name
*/}}
{{- define "provisioning.objectStorage.auth.minioProvisioning.name" -}}

{{- if .Values.objectStorage.auth.minioProvisioning.name -}}
  {{- .Values.objectStorage.auth.minioProvisioning.name -}}
{{- else if .Values.global.objectStorage.auth.minioProvisioning.name -}}
  {{- .Values.global.objectStorage.auth.minioProvisioning.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-minio-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
objectStorage.auth.minioProvisioning key
*/}}
{{- define "provisioning.objectStorage.auth.minioProvisioning.key" -}}

{{- if .Values.objectStorage.auth.minioProvisioning.key -}}
  {{- .Values.objectStorage.auth.minioProvisioning.key -}}
{{- else if .Values.global.objectStorage.auth.minioProvisioning.key -}}
  {{- .Values.global.objectStorage.auth.minioProvisioning.key -}}
{{- else -}}
root-password
{{- end -}}
{{- end -}}{{/*
Portal server Minio credentials user credentials name
*/}}
{{- define "provisioning.objectStorage.auth.portalServer.name" -}}

{{- if .Values.objectStorage.auth.portalServer.name -}}
  {{- .Values.objectStorage.auth.portalServer.name -}}
{{- else if .Values.global.objectStorage.auth.portalServer.name -}}
  {{- .Values.global.objectStorage.auth.portalServer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-portal-server-minio-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
objectStorage.auth.portalServer key
*/}}
{{- define "provisioning.objectStorage.auth.portalServer.key" -}}

{{- if .Values.objectStorage.auth.portalServer.key -}}
  {{- .Values.objectStorage.auth.portalServer.key -}}
{{- else if .Values.global.objectStorage.auth.portalServer.key -}}
  {{- .Values.global.objectStorage.auth.portalServer.key -}}
{{- else -}}
secretKey
{{- end -}}
{{- end -}}{{/*
Portal consumer Minio credentials user credentials name
*/}}
{{- define "provisioning.objectStorage.auth.portalConsumer.name" -}}

{{- if .Values.objectStorage.auth.portalConsumer.name -}}
  {{- .Values.objectStorage.auth.portalConsumer.name -}}
{{- else if .Values.global.objectStorage.auth.portalConsumer.name -}}
  {{- .Values.global.objectStorage.auth.portalConsumer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-portal-consumer-minio-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
objectStorage.auth.portalConsumer key
*/}}
{{- define "provisioning.objectStorage.auth.portalConsumer.key" -}}

{{- if .Values.objectStorage.auth.portalConsumer.key -}}
  {{- .Values.objectStorage.auth.portalConsumer.key -}}
{{- else if .Values.global.objectStorage.auth.portalConsumer.key -}}
  {{- .Values.global.objectStorage.auth.portalConsumer.key -}}
{{- else -}}
secretKey
{{- end -}}
{{- end -}}