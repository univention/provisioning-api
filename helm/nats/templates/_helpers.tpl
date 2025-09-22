{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}

{{- /*
These template definitions are only used in this chart.
*/}}
{{/*
 Create the name of the service account to use
 */}}
{{- define "nats.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
    {{ default (include "common.names.fullname" .) .Values.serviceAccount.name }}
{{- else -}}
    {{ default "default" .Values.serviceAccount.name }}
{{- end -}}
{{- end -}}

{{- define "nats.podNamePrefix" -}}
    {{ include "common.names.fullname" . }}
{{- end -}}
{{- define "nats.headlessServiceName" -}}
    {{ printf "%s-headless" (include "common.names.fullname" .) }}
{{- end -}}

{{- define "nats.env-passwords" -}}
- name: "ADMINUSER"
  valueFrom:
    secretKeyRef:
      name: {{ include "nubus-common.secrets.name" (dict "existingSecret" $.Values.config.createUsers.adminUser.existingSecret "defaultNameSuffix" "admin" "context" .) | quote }}
      key: {{ include "nubus-common.secrets.key" (dict "existingSecret" $.Values.config.createUsers.adminUser.existingSecret "key" "password") | quote }}
{{- range $passwordEnvVar, $config := omit .Values.config.createUsers "adminUser" }}
- name: {{ $passwordEnvVar | upper }}
  valueFrom:
    secretKeyRef:
      name: {{ include "nubus-common.secrets.name" (dict "existingSecret" $config.existingSecret "defaultNameSuffix" "admin" "context" $) | quote }}
      key: {{ include "nubus-common.secrets.key" (dict "existingSecret" $config.existingSecret "key" "password") | quote }}
{{- end -}}
{{- end -}}

{{- define "nats.authorization" -}}
{{- if or .Values.config.authorization.token .Values.config.createUsers -}}
authorization {
  {{- if .Values.config.authorization.token }}
  token: {{ .Values.config.authorization.token }}
  {{- end }}
  {{- if .Values.config.createUsers }}
  users: [
    {{- range $passwordEnvVar, $config := .Values.config.createUsers }}
    {
      user: {{ tpl $config.auth.username $ }}
      password: ${{ $passwordEnvVar | upper }}
      {{- if $config.permissions }}
      permissions: {
        {{- if $config.permissions.publish }}
        publish: {{ $config.permissions.publish | quote }}
        {{- end }}
        {{- if $config.permissions.subscribe }}
        subscribe: {{ $config.permissions.subscribe | quote }}
        {{- end }}
      }
      {{- end }}
    }
    {{- end }}
  ]
  {{- end }}
}
{{- end -}}
{{- end -}}

{{- define "nats.cluster.authorization" -}}
{{- if and .Values.config.cluster.authorization.enabled -}}
authorization {
  {{- if .Values.config.cluster.authorization.user }}
  user: {{ .Values.config.cluster.authorization.user }}
  password: ${{ .Values.config.cluster.authorization.passwordVariable }}
  {{- end }}
}
{{- end -}}
{{- end -}}
