{{/*
LDAP admin credentials user credentials name
*/}}
{{- define "provisioning.ldap.auth.cnAdmin.name" -}}

{{- if .Values.ldap.auth.cnAdmin.name -}}
  {{- .Values.ldap.auth.cnAdmin.name -}}
{{- else if .Values.global.ldap.auth.cnAdmin.name -}}
  {{- .Values.global.ldap.auth.cnAdmin.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-ldap-server-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
ldap.auth.cnAdmin key
*/}}
{{- define "provisioning.ldap.auth.cnAdmin.key" -}}

{{- if .Values.ldap.auth.cnAdmin.key -}}
  {{- .Values.ldap.auth.cnAdmin.key -}}
{{- else if .Values.global.ldap.auth.cnAdmin.key -}}
  {{- .Values.global.ldap.auth.cnAdmin.key -}}
{{- else -}}
adminPassword
{{- end -}}
{{- end -}}{{/*
LDAP administrator credentials user credentials name
*/}}
{{- define "provisioning.ldap.auth.administrator.name" -}}

{{- if .Values.ldap.auth.administrator.name -}}
  {{- .Values.ldap.auth.administrator.name -}}
{{- else if .Values.global.ldap.auth.administrator.name -}}
  {{- .Values.global.ldap.auth.administrator.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-nubus-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
ldap.auth.administrator key
*/}}
{{- define "provisioning.ldap.auth.administrator.key" -}}

{{- if .Values.ldap.auth.administrator.key -}}
  {{- .Values.ldap.auth.administrator.key -}}
{{- else if .Values.global.ldap.auth.administrator.key -}}
  {{- .Values.global.ldap.auth.administrator.key -}}
{{- else -}}
administrator_password
{{- end -}}
{{- end -}}{{/*
Keycloak bootstrap LDAP credentials user credentials name
*/}}
{{- define "provisioning.ldap.auth.keycloak.name" -}}

{{- if .Values.ldap.auth.keycloak.name -}}
  {{- .Values.ldap.auth.keycloak.name -}}
{{- else if .Values.global.ldap.auth.keycloak.name -}}
  {{- .Values.global.ldap.auth.keycloak.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-keycloak-bootstrap-ldap-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
ldap.auth.keycloak key
*/}}
{{- define "provisioning.ldap.auth.keycloak.key" -}}

{{- if .Values.ldap.auth.keycloak.key -}}
  {{- .Values.ldap.auth.keycloak.key -}}
{{- else if .Values.global.ldap.auth.keycloak.key -}}
  {{- .Values.global.ldap.auth.keycloak.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}