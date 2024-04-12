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
