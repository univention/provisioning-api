# ucsschool ci utils

This repository contains docker images and gitlab CI fragments that are used by some of the repositories of the UCS@school team.

The images and fragments are documented in this README.

## Images

### ec2 tools (`gitregistry.knut.univention.de/univention/internal/ucsschool-ci-utils/ec2-tools')
This image is the same as the original `gitregistry.knut.univention.de/univention/dist/ucs-ec2-tools` image, except that some
packages are installed in addition. See `./images/ec2-tools.Containerfile` for details.

This image is build daily by a scheduled pipeline with the `latest` tag. No versioning is planned at this point.

### univention-appcenter-control (`gitregistry.knut.univention.de/univention/internal/ucsschool-ci-utils/univention-appcenter-control')
This image is the same as the original `docker-registry.knut.univention.de/knut/univention-appcenter-control` image, except that some
packages are installed in addition. See `./images/univention-appcenter-control.Containerfile` for details.

This image is build daily by a scheduled pipeline with the `latest` tag. No versioning is planned at this point.

## Gitlab CI fragments

### run_openstack_cfg

This fragment allows to run a `cfg` file in our openstack environment.
The following variables are available:

- `EC2_TOOLS_IMAGE`: The image to start the job with. It is set to the ec2 tools image from this repo.
- `OPENSTACK_CFG_FILE`: The cfg to start. It is set to `scenario.cfg` by default.
- `REPLACE_INSTANCE`: If set to any value other than the default `true`, the instance will not replace
   any other instance with the same name.
- `TERMINATE_INSTANCE`: If set to any other value than the default `true`, the instance will not be terminated
  after the `cfg` is finished.
- `OPENSTACK_RC_FILE`: This must be configured as a CI/CD variable of type file in Gitlab.
  It must contain the rc formatted credentials to access the Openstack environment.
- `SSH_PRIVATE_KEY`: This must be configured as a CI/CD variable of type file in Gitlab.
  It is optional and can be used to insert a ssh key into the job environment. It will be placed as `~/.ssh/id_rsa`

### create_app_version/delete_app_version

These two fragments allow to automatically create a test version in the appcenter for the branch. One creates the version and the other removes it once the branch is merged or closed.
The following variables are available:

- `APPCENTER_CONTROL_IMAGE`: The image to start the job with. It is set to the univention-appcenter-control image from this repo.
- `APP_ID`: The `id` of the app in question. This is the part without the version and without the UCS version. Needs to be set for the jobs to work.
- `APP_UCS_VERSION`: The UCS version part of the app in question. Needs to be set for the jobs to work.
- `APP_VERSION`: The version of the app in question. On the main branch it is set to `0.0.0-staging`, on branches it is set to `0.0.0-$CI_COMMIT_REF_SLUG

### update_appcenter

This fragment updates the appcenter files for the appcenter version of the branch.
The following variables are available:

- `APPCENTER_CONTROL_IMAGE`: The image to start the job with. It is set to the univention-appcenter-control image from this repo.
- `APP_ID`: The `id` of the app in question. This is the part without the version and without the UCS version. Needs to be set for the jobs to work.
- `APP_UCS_VERSION`: The UCS version part of the app in question. Needs to be set for the jobs to work.
- `APP_VERSION`: The version of the app in question. On the main branch it is set to `0.0.0-staging`, on branches it is set to `0.0.0-$CI_COMMIT_REF_SLUG
 `APPCENTER_DOCKER_IMAGE`: The docker image to use for the `DockerImage` value in the ini file. Only relevant if this is a docker based app. It is set to `$CI_REGISTRY_IMAGE:latest` on main
  and `$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG` on feature branches by default.
