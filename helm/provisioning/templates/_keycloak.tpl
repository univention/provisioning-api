{{/*
Keycloak admin credentials user credentials name
*/}}
{{- define "provisioning.keycloak.auth.admin.name" -}}

{{- if .Values.keycloak.auth.admin.name -}}
  {{- .Values.keycloak.auth.admin.name -}}
{{- else if .Values.global.keycloak.auth.admin.name -}}
  {{- .Values.global.keycloak.auth.admin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-keycloak-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
keycloak.auth.admin key
*/}}
{{- define "provisioning.keycloak.auth.admin.key" -}}

{{- if .Values.keycloak.auth.admin.key -}}
  {{- .Values.keycloak.auth.admin.key -}}
{{- else if .Values.global.keycloak.auth.admin.key -}}
  {{- .Values.global.keycloak.auth.admin.key -}}
{{- else -}}
admin_password
{{- end -}}
{{- end -}}{{/*
Keycloak guardian client secret user credentials name
*/}}
{{- define "provisioning.keycloak.auth.guardianClient.name" -}}

{{- if .Values.keycloak.auth.guardianClient.name -}}
  {{- .Values.keycloak.auth.guardianClient.name -}}
{{- else if .Values.global.keycloak.auth.guardianClient.name -}}
  {{- .Values.global.keycloak.auth.guardianClient.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-guardian-keycloak-client-secret" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
keycloak.auth.guardianClient key
*/}}
{{- define "provisioning.keycloak.auth.guardianClient.key" -}}

{{- if .Values.keycloak.auth.guardianClient.key -}}
  {{- .Values.keycloak.auth.guardianClient.key -}}
{{- else if .Values.global.keycloak.auth.guardianClient.key -}}
  {{- .Values.global.keycloak.auth.guardianClient.key -}}
{{- else -}}
oauthAdapterM2mSecret
{{- end -}}
{{- end -}}