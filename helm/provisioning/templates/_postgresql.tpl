{{/*
Postgresql provisioning account password user credentials name
*/}}
{{- define "provisioning.postgresql.auth.postgresqlProvisioning.name" -}}

{{- if .Values.postgresql.auth.postgresqlProvisioning.name -}}
  {{- .Values.postgresql.auth.postgresqlProvisioning.name -}}
{{- else if .Values.global.postgresql.auth.postgresqlProvisioning.name -}}
  {{- .Values.global.postgresql.auth.postgresqlProvisioning.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.postgresqlProvisioning key
*/}}
{{- define "provisioning.postgresql.auth.postgresqlProvisioning.key" -}}

{{- if .Values.postgresql.auth.postgresqlProvisioning.key -}}
  {{- .Values.postgresql.auth.postgresqlProvisioning.key -}}
{{- else if .Values.global.postgresql.auth.postgresqlProvisioning.key -}}
  {{- .Values.global.postgresql.auth.postgresqlProvisioning.key -}}
{{- else -}}
admin_password
{{- end -}}
{{- end -}}{{/*
Guardian management API Postgresql credentials user credentials name
*/}}
{{- define "provisioning.postgresql.auth.guardian.name" -}}

{{- if .Values.postgresql.auth.guardian.name -}}
  {{- .Values.postgresql.auth.guardian.name -}}
{{- else if .Values.global.postgresql.auth.guardian.name -}}
  {{- .Values.global.postgresql.auth.guardian.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-guardian-management-api-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.guardian key
*/}}
{{- define "provisioning.postgresql.auth.guardian.key" -}}

{{- if .Values.postgresql.auth.guardian.key -}}
  {{- .Values.postgresql.auth.guardian.key -}}
{{- else if .Values.global.postgresql.auth.guardian.key -}}
  {{- .Values.global.postgresql.auth.guardian.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}{{/*
Keycloak extensions Postgresql credentials user credentials name
*/}}
{{- define "provisioning.postgresql.auth.keycloakExtensions.name" -}}

{{- if .Values.postgresql.auth.keycloakExtensions.name -}}
  {{- .Values.postgresql.auth.keycloakExtensions.name -}}
{{- else if .Values.global.postgresql.auth.keycloakExtensions.name -}}
  {{- .Values.global.postgresql.auth.keycloakExtensions.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-keycloak-extensions-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.keycloakExtensions key
*/}}
{{- define "provisioning.postgresql.auth.keycloakExtensions.key" -}}

{{- if .Values.postgresql.auth.keycloakExtensions.key -}}
  {{- .Values.postgresql.auth.keycloakExtensions.key -}}
{{- else if .Values.global.postgresql.auth.keycloakExtensions.key -}}
  {{- .Values.global.postgresql.auth.keycloakExtensions.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}{{/*
Keycloak Postgresql credentials user credentials name
*/}}
{{- define "provisioning.postgresql.auth.keycloak.name" -}}

{{- if .Values.postgresql.auth.keycloak.name -}}
  {{- .Values.postgresql.auth.keycloak.name -}}
{{- else if .Values.global.postgresql.auth.keycloak.name -}}
  {{- .Values.global.postgresql.auth.keycloak.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-keycloak-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.keycloak key
*/}}
{{- define "provisioning.postgresql.auth.keycloak.key" -}}

{{- if .Values.postgresql.auth.keycloak.key -}}
  {{- .Values.postgresql.auth.keycloak.key -}}
{{- else if .Values.global.postgresql.auth.keycloak.key -}}
  {{- .Values.global.postgresql.auth.keycloak.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}{{/*
Notifications API Postgresql credentials user credentials name
*/}}
{{- define "provisioning.postgresql.auth.notificationsApi.name" -}}

{{- if .Values.postgresql.auth.notificationsApi.name -}}
  {{- .Values.postgresql.auth.notificationsApi.name -}}
{{- else if .Values.global.postgresql.auth.notificationsApi.name -}}
  {{- .Values.global.postgresql.auth.notificationsApi.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-notifications-api-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.notificationsApi key
*/}}
{{- define "provisioning.postgresql.auth.notificationsApi.key" -}}

{{- if .Values.postgresql.auth.notificationsApi.key -}}
  {{- .Values.postgresql.auth.notificationsApi.key -}}
{{- else if .Values.global.postgresql.auth.notificationsApi.key -}}
  {{- .Values.global.postgresql.auth.notificationsApi.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}{{/*
UMC server Postgresql credentials user credentials name
*/}}
{{- define "provisioning.postgresql.auth.umcServer.name" -}}

{{- if .Values.postgresql.auth.umcServer.name -}}
  {{- .Values.postgresql.auth.umcServer.name -}}
{{- else if .Values.global.postgresql.auth.umcServer.name -}}
  {{- .Values.global.postgresql.auth.umcServer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-umc-server-postgresql-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
postgresql.auth.umcServer key
*/}}
{{- define "provisioning.postgresql.auth.umcServer.key" -}}

{{- if .Values.postgresql.auth.umcServer.key -}}
  {{- .Values.postgresql.auth.umcServer.key -}}
{{- else if .Values.global.postgresql.auth.umcServer.key -}}
  {{- .Values.global.postgresql.auth.umcServer.key -}}
{{- else -}}
password
{{- end -}}
{{- end -}}