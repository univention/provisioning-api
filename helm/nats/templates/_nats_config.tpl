{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}

{{- /*
These template definitions are only used in this chart.
*/}}


{{- define "nats.env-passwords" -}}
- name: "ADMINUSER"
  valueFrom:
    secretKeyRef:
      name: {{ include "nubus-common.secrets.name" (dict "existingSecret" $.Values.config.createUsers.adminUser.auth.existingSecret "defaultNameSuffix" "admin" "context" .) }}
      key: {{ include "nubus-common.secrets.key" (dict "existingSecret" $.Values.config.createUsers.adminUser.auth.existingSecret "key" "password" "context" .) }}
{{- range $passwordEnvVar, $config := omit .Values.config.createUsers "adminUser" }}
- name: {{ $passwordEnvVar | upper }}
  valueFrom:
    secretKeyRef:
      name: {{ tpl (required (printf "config.createUsers.%s.auth.existingSecret.name is required" $passwordEnvVar ) ($config.auth.existingSecret).name ) $ }}
      key: {{ include "nubus-common.secrets.key" (dict "existingSecret" $config.auth.existingSecret "key" "password" "context" .) }}
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
      user: {{ tpl (required (printf "config.createUsers.%s.auth.username is required" $passwordEnvVar ) ($config.auth).username) $ }}
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
