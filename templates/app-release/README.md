# app-release

This component sets up all jobs necessary to create app releases in the App center.

## Prerequisites

### Stages

This component runs jobs on the stages `build`, `release` and `cleanup` in this order by default.
Make sure that your pipeline defines those stages or configure the stages via the inputs.

## CI/CD Variables

This component requires the following CI/CD variables to be set:

- `APPCENTER_CONTROL_USERNAME`: The username to authenticate against the appcenter with.
- `APPCENTER_CONTROL_PASSWORD`: The password to authenticate against the appcenter with.
- `ROCKETCHAT_PASSWORD`: The password of the `flubberbot` user for rocket chat.

### App artifacts

If you build a docker app you need to provide the name of the job that builds the docker image as the input `app_build_job_name`.
This job is required to export the variable `IMAGE_TAG`, that contains the tag of the docker image for the release.

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
