# debian-package

This component sets up all jobs necessary to build debian packages.

[[_TOC_]]

## Prerequisites

### Stages

This component runs jobs in the `build` stage.
Make sure that your pipeline defines this stage or configures the stage via the inputs.

### Variables

The jobs of this component expect the variable `DEBIAN_SOURCE_DIRECTORIES` to be set.
This variable needs to contain all directories of debian source packages to be build.
The format is a space separated list of paths.

## Behavior

### Merge Request

The component builds the debian packages within the pipeline and uploads them to the app in the appcenter.
This is not done in the official build system for ucs and does not result in signed packages!

### Main branch

The component imports and builds the debian packages on the ucs build system.
You need to make sure that packages that are already built are not passed in the `DEBIAN_SOURCE_DIRECTORIES` variable.

### Tag

This component is not doing anything in a tag pipeline.
