# ucsschool ci utils

This repository contains docker images and gitlab CI fragments that are used by some of the repositories of the UCS@school team.

The images and fragments are documented in this README.

## Images

### ec2 tools (`gitregistry.knut.univention.de/univention/internal/ucsschool-ci-utils/ec2-tools')
This image is the same as the original `gitregistry.knut.univention.de/univention/dist/ucs-ec2-tools` image, except that some
packages are installed in addition. See `./images/ec2-tools.Containerfile` for details.

This image is build daily by a scheduled pipeline with the `latest` tag. No versioning is planned at this point.
