{{/*
UMC server Memcached credentials user credentials name
*/}}
{{- define "provisioning.memcached.auth.umcServer.name" -}}

{{- if .Values.memcached.auth.umcServer.name -}}
  {{- .Values.memcached.auth.umcServer.name -}}
{{- else if .Values.global.memcached.auth.umcServer.name -}}
  {{- .Values.global.memcached.auth.umcServer.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-umc-server-memcached-credentials" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
memcached.auth.umcServer key
*/}}
{{- define "provisioning.memcached.auth.umcServer.key" -}}

{{- if .Values.memcached.auth.umcServer.key -}}
  {{- .Values.memcached.auth.umcServer.key -}}
{{- else if .Values.global.memcached.auth.umcServer.key -}}
  {{- .Values.global.memcached.auth.umcServer.key -}}
{{- else -}}
memcached-password
{{- end -}}
{{- end -}}