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

{{- define "nats.authorization" -}}
{{- if .Values.config.authorization.enabled -}}
authorization {
  {{- if .Values.config.authorization.token }}
  token: {{ .Values.config.authorization.token }}
  {{- end }}
  {{- if .Values.config.authorization.users }}
  users: [
    {{- range .Values.config.authorization.users }}
    {
      user: {{ .user }}
      password: {{ .password }}
      {{- if .permissions }}
      permissions: {
      {{- .permissions | toYaml | nindent 8 }}
      {{- end }}
      }
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
