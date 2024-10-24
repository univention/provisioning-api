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
{{- end -}}
