{{/*
common.names.fullnameWithRevision will render a full name like "common.names.fullname"
and append the revision number.

The intended usage is for "Job" objects which do not allow that the template
section is updated. The consequence is that the "Job" object will need a new name
on every call to "helm upgrade", so that a new object will be created instead of
the existing one being patched.

Usage:
{{ include "nubus-common.names.fullnameWithRevision" (dict "localName" "myLocalName" "context" $) }}

The function will return a string with the following structure:
<helm chart fullname>-[<localName>-]<revision number>

Params:
  - localName String - Optional. It is used to customize the manifest name beyond the release and chart names.
  - context - Dict - Required. The context for the template evaluation.
*/}}
{{- define "nubus-common.names.fullnameWithRevision" }}
  {{- if not .localName }}
    {{- $name := include "common.names.fullname" .context | trunc 55 | trimSuffix "-" }}
    {{- printf "%s-%d" $name .context.Release.Revision | trunc 63 | trimSuffix "-" -}}
  {{- else -}}
    {{- $name := printf "%s-%s" ( include "common.names.fullname" .context ) .localName | trunc 55 | trimSuffix "-" }}
  {{- printf "%s-%d" $name .context.Release.Revision | trunc 63 | trimSuffix "-" -}}
  {{- end -}}
{{- end -}}
