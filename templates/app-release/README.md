# app-release

This component sets up all jobs necessary to create app releases in the App center.

[[_TOC_]]

## Prerequisites

### Stages

This component runs jobs on the stages `build`, `release` and `cleanup` in this order by default.
Make sure that your pipeline defines those stages or configure the stages via the inputs.

## CI/CD Variables

This component requires the following CI/CD variables to be set:

- `APPCENTER_CONTROL_USERNAME`: The username to authenticate against the appcenter with.
- `APPCENTER_CONTROL_PASSWORD`: The password to authenticate against the appcenter with.
- `ROCKETCHAT_PASSWORD`: The password of the `flubberbot` user for rocket chat.

### Templating

The `app-release` component allows for templating of the appcenter files via jinja templates.
This feature is completely optional, except in one instance:
The `ini` file must be templated and contain the following fragment for the version:

```ini
Version = {{ APP_VERSION }}
```

If you build a docker app you need to provide the name of the job that builds the docker image as the input `app_build_job_name`.
This job is required to export the variable `IMAGE_TAG`, that contains the tag of the docker image for the release.

To make use of this feature, simply append `.jinja` to any appcenter file within the `appcenter_file_dir`.
Within the template you have access to the full feature set of jinja.
Its context is composed of all environment variables the `update_appcenter` job has access to.

If you have jobs that provide important variables for your templates, make sure they are included in the `update_appcenter` jobs
need section.
For that you can use the input `additional_update_appcenter_needs`.

Per default the following environment variables are available next to Gitlab Pipeline predefined variables:

- APP_ID
- APP_VERSION
- APP_COMPONENT_ID
- APP_UCS_VERSION
- APP_NAME

You can include raw files by using a filter suplied by this componet:

```jinja
{{ '<path_to_your_file>' | source }}
```

## Behavior

### Merge Request

This CI/CD component creates a temporary version in the appcenter with the format `0.0.0-$CI_COMMIT_REF_SLUG`.
This version in the appcenter is kept up to date with the merge request
and gets removed once the MR is closed or merged.

### Main branch

The CI/CD component keeps the app in the version specified in the input `app_staging_version` up to date with the main branch.

### Tag

If a tag is created the pipeline acts like a merge request pipeline.
If the tag follows the regex defined by combining the inputs `release_tag_prefix` and `release_tag_constraint`,
an app version following `release_tag_constraint` is created in the appcenter.
After triggering the manual `do_release` job in the tag pipeline, the app is published and announced.
