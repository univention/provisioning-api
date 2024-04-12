{{- /*
SPDX-FileCopyrightText: 2024 Univention GmbH
SPDX-License-Identifier: AGPL-3.0-only
*/}}
{{- /*
{{- /*
These template definitions are only used in this chart and do not relate to templates defined elsewhere.
*/}}

{{- define "provisioning-dispatcher.credentialSecretName" -}}
{{- coalesce .Values.dispatcher.credentialSecretName (printf "%s-provisioning-dispatcher-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-api.credentialSecretName" -}}
{{- coalesce .Values.api.credentialSecretName (printf "%s-provisioning-api-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-prefill.credentialSecretName" -}}
{{- coalesce .Values.prefill.credentialSecretName (printf "%s-provisioning-prefill-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.credentialSecretName" -}}
{{- coalesce .Values.register_consumers.credentialSecretName (printf "%s-provisioning-register-consumers-credentials" .Release.Name) -}}
{{- end -}}

{{- define "provisioning-register-consumers.jsonSecretName" -}}
{{- coalesce .Values.register_consumers.jsonSecretName (printf "%s-provisioning-register-consumers-json-secrets" .Release.Name) -}}
{{- end -}}