{{/*
Keycloak extensions SMTP credentials user credentials name
*/}}
{{- define "provisioning.smtp.auth.keycloakExtensions.name" -}}

{{- if .Values.smtp.auth.keycloakExtensions.name -}}
  {{- .Values.smtp.auth.keycloakExtensions.name -}}
{{- else if .Values.global.smtp.auth.keycloakExtensions.name -}}
  {{- .Values.global.smtp.auth.keycloakExtensions.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-keycloak-extensions-smtp-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
smtp.auth.keycloakExtensions key
*/}}
{{- define "provisioning.smtp.auth.keycloakExtensions.key" -}}

{{- if .Values.smtp.auth.keycloakExtensions.key -}}
  {{- .Values.smtp.auth.keycloakExtensions.key -}}
{{- else if .Values.global.smtp.auth.keycloakExtensions.key -}}
  {{- .Values.global.smtp.auth.keycloakExtensions.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}{{/*
UMC server SMTP credentials user credentials name
*/}}
{{- define "provisioning.smtp.auth.umcServer.name" -}}

{{- if .Values.smtp.auth.umcServer.name -}}
  {{- .Values.smtp.auth.umcServer.name -}}
{{- else if .Values.global.smtp.auth.umcServer.name -}}
  {{- .Values.global.smtp.auth.umcServer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-umc-server-smtp-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
smtp.auth.umcServer key
*/}}
{{- define "provisioning.smtp.auth.umcServer.key" -}}

{{- if .Values.smtp.auth.umcServer.key -}}
  {{- .Values.smtp.auth.umcServer.key -}}
{{- else if .Values.global.smtp.auth.umcServer.key -}}
  {{- .Values.global.smtp.auth.umcServer.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}