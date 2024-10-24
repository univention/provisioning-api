{{/*
Portal server central navigation shared secret user credentials name
*/}}
{{- define "provisioning.portal.auth.centralNavigation.name" -}}

{{- if .Values.portal.auth.centralNavigation.name -}}
  {{- .Values.portal.auth.centralNavigation.name -}}
{{- else if .Values.global.portal.auth.centralNavigation.name -}}
  {{- .Values.global.portal.auth.centralNavigation.name -}}
{{- else -}}
{{- $namePrefix := default .Release.Name .Values.global.releaseNameOverride | trunc 63 | trimSuffix "-" -}}
{{- printf "%s-portal-server-central-navigation-shared-secret" $namePrefix -}}
{{- end -}}
{{- end -}}

{{/*
portal.auth.centralNavigation key
*/}}
{{- define "provisioning.portal.auth.centralNavigation.key" -}}

{{- if .Values.portal.auth.centralNavigation.key -}}
  {{- .Values.portal.auth.centralNavigation.key -}}
{{- else if .Values.global.portal.auth.centralNavigation.key -}}
  {{- .Values.global.portal.auth.centralNavigation.key -}}
{{- else -}}
authenticator.secret
{{- end -}}
{{- end -}}