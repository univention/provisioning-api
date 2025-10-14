# Changelog

## [0.62.1](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.62.0...v0.62.1) (2025-10-14)


### Bug Fixes

* adjust keyMapping in values for api.nats.auth.existingSecret ([e2f1be1](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/e2f1be11e7733abd45f6cd6f6f9ae1fd00573584)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)

## [0.62.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.61.0...v0.62.0) (2025-10-13)


### Features

* **nats:** Integrate improved nats user configuration ([8203ef9](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/8203ef9e4db505c56ad37addfcfea942f4d16572)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)


### Bug Fixes

* adjust kyverno-values ([93bfeee](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/93bfeee56ce90f469650f384dcca25833cc1ae6f)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* **helm-unittests:** Ensure that existing secrets can be templated and usernames are required ([4315381](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/43153812b2a5d53d1313cb494f2e084b88175b36)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* **helm-unittests:** Update nats secrets tests and migrate helm unittests to flavor-based helm test harness ([21a1f4b](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/21a1f4b68d6e02a1dcdcb2f904eb0efeb9590960)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* **helm:** Fix secret name mismatches between this chart and the nats subchart ([0b19bf0](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/0b19bf00a50a71123dfd22c38d4760a9d4231bcc)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* **nats:** Integrate improved nats user configuration and migrate helm unittests to flavor-based helm test harness ([37b4001](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/37b40018b606fe488092d0ceb9bfa31dc3aee0b1)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* **nats:** Update nats chart version ([99499ea](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/99499eae4f4ee2e6b86fc2054faf6071c0e501db)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)
* prefix generated NATS password with 'nbs_' ([b0f0da1](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b0f0da19b4398bd32946a87bc912c27f8c1abeeb)), closes [univention/dev/internal/team-nubus#1399](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1399)

## [0.61.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.12...v0.61.0) (2025-09-24)


### Features

* support disabling probes and omit 'enabled' field ([6f836db](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/6f836db24506654bcc22491061ffd8aa79c498e2)), closes [univention/dev/internal/team-nubus#1426](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1426)

## [0.60.12](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.11...v0.60.12) (2025-09-03)


### Bug Fixes

* **dispatcher,prefill:** don't crash on subscription handling errors ([543ec48](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/543ec485b198ade071fd242cc20ff9a38f80ea8c)), closes [univention/dev/internal/team-nubus#1383](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1383)
* **dispatcher,transformer,prefill:** reconnect to NATS on connection loss ([715dac9](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/715dac944fae6087fdd9ad9d7267e69998ee10c2)), closes [univention/dev/internal/team-nubus#1383](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1383)
* **natsmq:** prevent crashing on purge of non-existent streams ([010179a](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/010179a5eecbf77ed89ebb7af5c5577a519b6a1e)), closes [univention/dev/internal/team-nubus#1383](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1383)
* **prefill:** prevent crash when updating status of deleted subscription ([8899dbc](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/8899dbc4c424ae89b3e2fe7428bb2efe1f5f90fd)), closes [univention/dev/internal/team-nubus#1383](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1383)

## [0.60.11](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.10...v0.60.11) (2025-09-03)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/nubus-for-k8s/listener-base/listener-base Docker tag to v0.13.6 ([a96e373](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/a96e373b1205cd50b027949f0671bc68db3c1667)), closes [#0](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/0)

## [0.60.10](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.9...v0.60.10) (2025-09-02)


### Bug Fixes

* **deps:** Update gitregistry.knut.univention.de/univention/dev/projects/ucs-base-image/ucs-base-python Docker tag to v5.2.2-build.20250828 ([4aa0b0d](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/4aa0b0da510eeb7eb444645ee6ad1a027e525bb2)), closes [#0](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/0)

## [0.60.9](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.8...v0.60.9) (2025-09-01)


### Bug Fixes

* Update base image to version 5.2.2-build.20250821 ([27ea14e](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/27ea14e0ed6542cbb21026efbe4b25333a024350)), closes [univention/dev/internal/team-nubus#1385](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1385)

## [0.60.8](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.7...v0.60.8) (2025-08-22)


### Bug Fixes

* update listener-base ([b492370](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b49237020fdd87690095f038a59abbf4f0772283)), closes [univention/dev/internal/team-nubus#1372](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1372)

## [0.60.7](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.6...v0.60.7) (2025-08-18)


### Bug Fixes

* **udm-listener:** remove unused events_username_udm secret from helm chart to simplify secrets documentation ([87d6293](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/87d629368cafa8e2a0d30170b9c23d720382b33b)), closes [univention/dev/internal/team-nubus#989](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/989)

## [0.60.6](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.5...v0.60.6) (2025-08-14)


### Bug Fixes

* bump NATS chart ([a0ffb83](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/a0ffb838ad4fac0dd2b6aedb382d9a01bad70ccb)), closes [univention/dev/internal/team-nubus#1382](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1382)

## [0.60.5](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.4...v0.60.5) (2025-08-12)


### Bug Fixes

* **dispatcher:** catch and handle failing send or acknowledgement requests ([97fc48a](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/97fc48a4299f17abcb0ca97529b6b7ea40d628e1)), closes [univention/dev/internal/team-nubus#1349](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1349)
* **dispatcher:** ensure docker rebuild respects changes in dispatcher files w/o need to use --no-cache ([d807856](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/d807856bc45af6cd34ee5e404cb22d4842ce6c7d)), closes [univention/dev/internal/team-nubus#1349](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1349)
* **dispatcher:** ignore subscriptions w/o matching stream, create fatal log on send failure ([2d2eaf0](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/2d2eaf069b9665b8864e97eefc08dc5cbaffb90a)), closes [univention/dev/internal/team-nubus#1349](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1349)
* **rest-api:** rollback any NATS related changes if creating a subscription fails ([5204ae0](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/5204ae0413966688da745ad12ea779bb5efddfe5)), closes [univention/dev/internal/team-nubus#1349](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1349)
* **rest-api:** unit test rollback of any NATS related changes if creating a subscription fails ([37825bb](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/37825bb89501ba775e53077a929478b3dd2d75a7)), closes [univention/dev/internal/team-nubus#1349](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1349)

## [0.60.4](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.3...v0.60.4) (2025-08-11)


### Bug Fixes

* code cleanup and error message improvement ([5889488](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/588948821d7b8d77bc6500195962e8b9aaa224a4)), closes [univention/dev/projects/provisioning#78](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/78)
* code cleanup and error message improvement ([604db64](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/604db647774bcee29dbed7ff1d243b38f413ad13)), closes [univention/dev/projects/provisioning#78](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/78)
* improve error handling for 'consumer not found' ([4becbe7](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/4becbe7e75bad188afdbcc1726d5eb6cb68056c4)), closes [univention/dev/projects/provisioning#78](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/78)
* raise exception from backend -> nats-adapter -> restapi ([664f64a](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/664f64accf0a6f97078cf0eecc0eabcc864de10b)), closes [univention/dev/projects/provisioning#78](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/78)

## [0.60.3](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.2...v0.60.3) (2025-08-08)


### Bug Fixes

* **prefill:** Adapt the network retry timeout for the integration tests so it doesn't hang for ages in case of an error ([03107ff](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/03107ff56fca4e93eda3a047a457c6df0a085e9c)), closes [univention/dev/internal/team-nubus#1357](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1357)

## [0.60.2](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.1...v0.60.2) (2025-07-31)


### Bug Fixes

* **prefill:** Retry NATS and UDM request if they fail ([55fc1a1](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/55fc1a1ad250a74c2a5ff95eba9ab4df9ae49bbd)), closes [univention/dev/internal/team-nubus#1357](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1357)

## [0.60.1](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.60.0...v0.60.1) (2025-07-28)


### Bug Fixes

* **nats:** bump nats image version to 2.11.6 ([9516034](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/9516034246f00b434896347e691ed744c7000113)), closes [univention/dev/internal/team-nubus#1350](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1350)

## [0.60.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.59.0...v0.60.0) (2025-07-17)


### Features

* update UDM listener image to 0.13.0 ([558b233](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/558b2330a6a61710e91e23212a66a7c1b0f23894)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)
* update wait-for-dependency to 0.35.0 ([3df0628](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/3df06283d2cdf373564e63059193eeb932258f38)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.59.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.58.3...v0.59.0) (2025-07-17)


### Features

* update listener base image ([b861313](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b861313a4c08cfdd2883afe8b2124a67cf3cc337)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)
* update ucs-base to 5.2.2-build.20250714 ([22eedfe](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/22eedfe5d7df6c25877130c9fe3a24174a19ef4b)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)


### Bug Fixes

* use ucs-base-python image for docker images ([ca4141c](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/ca4141c8037a83e6f77040bfb6ef8ddc28f1b5df)), closes [univention/dev/internal/team-nubus#1320](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1320)

## [0.58.3](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.58.2...v0.58.3) (2025-07-14)


### Bug Fixes

* **listener:** Make the listener container easier to use in docker-compose test setups ([c44814c](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/c44814c53204976017382308f7c4784453ea0c4a)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)

## [0.58.2](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.58.1...v0.58.2) (2025-07-14)


### Bug Fixes

* add waitForDependency.image to image value mapping ([b7f434a](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b7f434a96c512bbcfe8bdcdb44597ea5fb1d84e7)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)

## [0.58.1](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.58.0...v0.58.1) (2025-07-11)


### Bug Fixes

* **listener:** allow disabling listener termination on NATS failures ([bac45c5](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/bac45c541a84af984583f7db5ada82ec02396291)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)

## [0.58.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.57.0...v0.58.0) (2025-07-10)


### Features

* **listener:** Retry nats interactions in the udm-listener to avoid loosing messages ([45d2b86](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/45d2b8675f0179c30b21a0efad30dfb94f8cbdde)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)


### Bug Fixes

* **listener:** ensure that the listener process is not PID1 and can be terminated by the listener module ([cb189ab](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/cb189ab220612ce1a1c78faef1af10546b08be7b)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)

## [0.57.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.56.0...v0.57.0) (2025-07-09)


### Features

* add wait-for-nats initContainer to udm-listener ([c2ab464](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/c2ab464e2076939a8189e29356da3674cf1855e1)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)


### Bug Fixes

* **listener:** Terminate the listener process when the listener-module encounters an exception ([0ea7e2d](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/0ea7e2d034f36fc92cda9945dcc95b39e553a999)), closes [univention/dev/internal/dev-issues/dev-incidents#149](https://git.knut.univention.de/univention/dev/internal/dev-issues/dev-incidents/issues/149)

## [0.56.0](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.55.3...v0.56.0) (2025-06-27)


### Features

* Common secret handling for api.auth.admin ([b4072d5](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b4072d5782620bcb232440bbb179b92446c278ea)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for dispatcher.nats.auth ([9f1aa85](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/9f1aa858ee3c4ae62c000719622ab0da0f918838)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for prefill.udm.auth ([6cbec3d](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/6cbec3df0293bae766071be77a8f2a5bd28b1baa)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for registerConsumers.createUsers ([db9c7b7](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/db9c7b7d5571f4015587a123b68964f193ffb1dc)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for registerConsumers.udm.auth ([20de2e1](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/20de2e1dea455a291ebef54969dd2fab167e8b50)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for udmTransformer.ldap.auth ([1f293a8](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/1f293a8ac82c280f586d992204921ea954b2b274)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secret handling for udmTransformer.nats.auth ([08fd701](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/08fd701495216143ac7bd3ad5be53476a3a1ef6e)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Common secrets handling for prefill.nats.auth ([dd158d8](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/dd158d800df4acc3a73e6a96ab3595f33b1d141f)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Ensure stable secret value generation ([dae8e87](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/dae8e87fc8e31c9009f630fd28bce6510e444866)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Follow common image pull policy configuration structure ([0dac2ec](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/0dac2ec900d43cb8fddcfec05df1d3479b103634)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **provisioning:** Common secret handling for "api.nats.auth" ([2e7c9b5](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/2e7c9b5bd5319db7bf9504561ccef101f6ec7dc4)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Remove top level "ldap" configuration options from chart ([155af7e](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/155af7ec63070f030aba9167e6011ecfbec2a056)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Support owner role for "api.auth.admin" ([b9684b7](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/b9684b7e7a8e69a0bbb0c0d10f7568ac8725fe6a)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Support owner role for remaining users in "api.auth" ([901bd1f](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/901bd1f5f49529e67431b54498a9058dbcd4c1c3)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Follow common behavior around image configuration ([abed7e9](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/abed7e90cdba2e187e42b1077d7fb510300e3d28)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Follow common secret behavior around nats.auth ([e8cfd8b](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/e8cfd8b1518b25cd5560fc39b397a95009bbccd4)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Follow common secret behavior around provisioningApi.auth ([ef9eee4](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/ef9eee4f22b778f47c38717267224f92d63a4311)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Update nubus-common version to 0.21.1 ([a4fb320](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/a4fb320af3e5686d10b4b9f2c0115a2752a92386)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Use common secret behavior around ldap.auth ([fb11e1d](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/fb11e1d53a140126c9ffcb8b4f9d77a39bd2e654)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Update dependency nubus-common to version 0.21.1 ([8aef09b](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/8aef09bc3c9868ffab37e2beffbbdedc0052550e)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* Update generated files ([e9d48de](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/e9d48de2d17593a6577bfbad1e37d7ab291277c6)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)


### Bug Fixes

* Correct condition for the bundled nats to "nats.bundled" ([f550a05](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/f550a05bb4b9750ada9a0b1e894dbe878f44f3d2)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **provisioning:** Use ldap base dn in default value of "udmTransformer.ldap.bindDn" ([e4b4fae](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/e4b4fae0f3767bc0a2452ad7a25836074ace351f)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Correct path to ldap password file ([ab7e2d9](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/ab7e2d9d4144f31a0882dcb2636530397943badf)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Remove LDAP_PASSWORD from config maps ([612657a](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/612657adcfa08138d15d8e3068d538371c1f7232)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)
* **udm-listener:** Use global ldap base dn in default of "ldap.bindDn" ([84c944e](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/84c944e7671a2a2f0f9a2b69d1179eb365c150e9)), closes [univention/dev/internal/team-nubus#892](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/892)

## [0.55.3](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.55.2...v0.55.3) (2025-06-23)


### Bug Fixes

* use default cluster ingress class if not defined ([ecf657e](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/ecf657ec019e3cab2e1c58764bb422e4bf62b025)), closes [univention/dev/internal/team-nubus#1134](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1134)

## [0.55.2](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.55.1...v0.55.2) (2025-06-23)


### Bug Fixes

* listener image bump ([bc63028](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/bc63028ee2dfa0796cb7b71e8c8d5509339b99f5)), closes [univention/dev/internal/team-nubus#1263](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1263)

## [0.55.1](https://git.knut.univention.de/univention/dev/projects/provisioning/compare/v0.55.0...v0.55.1) (2025-06-18)


### Bug Fixes

* update ucs image ([24cedc5](https://git.knut.univention.de/univention/dev/projects/provisioning/commit/24cedc568541b863bb0c6afcd8f5faed74136963)), closes [#0](https://git.knut.univention.de/univention/dev/projects/provisioning/issues/0)

## [0.55.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.54.0...v0.55.0) (2025-06-11)


### Features

* **dispatcher:** ports and adapters ([303cf20](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/303cf20558183f5672729291479886e65fcf4378))
* Migrate backends and common from poetry to uv ([331b657](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/331b657149d84375e19b877b743ffae795acf49c))
* ports and adapters, split KV and MQ ([6223c7e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6223c7e87175c763367f8fa653b69e4f88e1a662))
* **prefill:** ports and adapters ([32628f4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/32628f4cb5c8e0f6e48b06e3c090140bf4501a2c))
* **rest-api:** ports and adapters ([e12ca4c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e12ca4cd157e0e7780986c30cc44c7fa031dd14d))
* restructure project ([a381da9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a381da9a83c46b39eac6fb9aad3ba48853215917))
* **udm-transformer:** ports and adapters ([5819ea2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5819ea2a44bffce997862e83a8609dfd17a58126))


### Bug Fixes

* **common:** Don't crash the udm-transformer on unknown messages like the cn=admin creation event (has no udm module) ([f708350](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f708350e0c58bc4e5d1bce8ef491d72064b8f778))
* **common:** fix comparison ([bfae914](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bfae9149dffa55118287b35fa935608cfb323082))
* **consumer_example:** container build ([9ebee9c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9ebee9cc8e5a175018fdf7c2aa1b1da96b05d7a1))
* **consumer-client:** Migrate the consumer package from poetry to uv ([baab0eb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/baab0eb50bda3b54691c76d2e093b0cf5063c6b6))
* **consumer-example:** Migrate the consumer example package from poetry to uv and update container build ([0cc9c17](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0cc9c177db383226c81390c44b02997206cf64b4))
* **dispatcher:** Cancel the task group if the nats message polling fails ([7b4b5e9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7b4b5e942f470842767f23c02307824d9f5abb6d)), closes [univention/dev/internal/team-nubus#930](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/930)
* **dispatcher:** container build ([d3de9f0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d3de9f082c8ac2c508beb126ea8ecf56d0fa7f6c))
* **dispatcher:** Migrate dispatcher from poetry to uv ([9676157](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9676157a9ca83f934727a3775ae2084f9b827e82))
* **dispatcher:** multi-stage dispatcher build ([8184789](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/81847893ae88091a1a2ca327d19d9494bb6a8c2e))
* **dispatcher:** remove old MessageAckManager ([1cba115](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1cba1158aee302f58ae4e3fac8692c6eade0c650))
* **dispatcher:** uv based single stage dispatcher container build ([6df5d8d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6df5d8da833fb591bb223f91b06e6eee9cec6288))
* **e2e-tests:** actually execute the fixture cleanup and delete the subscriptions ([7c4cce9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7c4cce9e6e466d203f846519429abf0b8f276693))
* **e2e-tests:** add dedicated testrunner for the e2e tests ([d759086](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d7590863d05f12c9561c26992865da2bcc39e8de))
* **e2e-tests:** Last e2e fixes to get a clean e2e test run after the project restructuring ([874ad1c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/874ad1c45b40ba0906e583b59d77f4b61d9d0974))
* **e2e-tests:** Migrate the e2e tests from poetry to uv and update the container build and docker compose setup ([85a65bf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/85a65bf255da067c726ffad9fb26dd8a6af7eb83))
* fix e2e tests ([b61a057](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b61a057e411521f2ea7bc48418226cc76ac5e642)), closes [univention/dev/internal/team-nubus#930](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/930)
* functioning dispatcher dockerfile ([3245838](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3245838f587e8a7e2d9862a4aa93a47ad71c83d6))
* **listener:** container build ([3772374](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3772374a90df36dd2182d0d4bd91fbe0fed95030))
* **listener:** Filter out non-udm messages like temporary locking objects ([82cd54d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/82cd54d2ca0d794eac2f6994d76bbe79fdef7100))
* **listener:** Fix udm listener container build after refactoring ([1927c89](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1927c89e35cdfa020122ae07b95f905fb5fc0afa))
* **listener:** Migrate the udm-listener from poetry to uv and update container build ([a776747](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a776747876cea8f91578e6a1925072c9eace108b))
* **listener:** ports and adapters; fix imports; improve names ([3ebb7f2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3ebb7f21e33c075425ec6f3e5595ebd590ed9ba5))
* **listener:** remove nats client code copy ([a4e95bb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a4e95bbc7d85be7599f0e813cdddddaf728c680f))
* Migrate metapackage from poetry to uv ([3a3d699](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3a3d6993f3c6226275eea19e65ee80e877c5a766))
* move things where they belong, fix imports ([c1390d6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c1390d6372053ca82d090c00511055724b855e9f))
* **prefill:** Add udm rest client library to prefill ([e1f2dec](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e1f2dec5becf8afb6f4300ba53d1ba44a6faa992))
* **prefill:** container build ([7c92006](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7c920068b5d2ad6209d5677d85e65de733f6ed4d))
* **prefill:** Migrate prefill from poetry to uv and update container build ([bd0703a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bd0703a9c609f9854be47f6b3736f9b6a23d9ed2))
* Remove poetry from init container run command ([243543e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/243543e5722fce8ae2865f12d465c55b17ce6c7e))
* **rest-api:** container build ([12faddc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/12faddcd6b519001342495c1b6707c16ca535b4f))
* **rest-api:** Migrate the rest-api from poetry to uv and update container build ([46c4739](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/46c4739557f0050346c137c07234690aaa7fe216))
* **rest-api:** Workaround for a passlib bug that prints a confusing traceback into the logs ([f91d8f3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f91d8f3b7f87a04558159e54a0ec5fd351a5718f))
* **server:** build consolidated server container and adapt the docker-compose setup ([69238ad](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/69238ad98b294d50ba581927d7d485348928b5e3))
* **server:** make server services executable and remove name conflict ([26b5e95](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/26b5e9518f5d34f0acda609afb7a215ac804ba1c))
* **server:** Remove problematic version logging and make the rest-api more easily executable ([aedda45](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/aedda457b118b97fcd2a1660e480b83b7c47ed1f))
* **test:** container build ([3258528](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/32585280a4273872e684bf2f4911de6b7d42d47e))
* **tests:** e2e tests ([329c281](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/329c281923cb4519190b30a1afd8be4c41eb162a))
* **tests:** fix unittests and integration-tests ([6aefc9f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6aefc9f486cea28a7acbef9c0a7edc703a361935))
* **tests:** integration tests ([5f5298c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5f5298c1ec242bf27ff0a592667c1853f17ef07e))
* **tests:** Make all unit and integration tests easily executable locally ([a7c4ae1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a7c4ae159cff3f3b4e31dc377ddbe01ccfff5c3d))
* **tests:** make integration tests compatible with httpx 1.28.* ([14595a1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/14595a185e57c29137653fe54a8da2a48dd9c1f6))
* **tests:** remove test stage from dockerfiles because they are now centralized in the metapackage ([bb0fee0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bb0fee0149e96f9b230f5e43c47efb09a4aa33bf))
* **tests:** rename test file to avoid pytest error because of conflicting files ([d5c9c92](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d5c9c92e29aa7052a02503131595576685ba932a))
* **udm-transformer:** container build ([b4d2bf4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b4d2bf4f04036cac5cfe2f9ae2fe4b60eab0a23a))
* **udm-transformer:** Don't retry LDAP messages that don't have the necessary UDM information ([66aef20](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/66aef2011b588a3d85959894af4d7c3b5838a6c9))
* **udm-transformer:** explicitly nack a message if any exception is raised, to get faster redelivery by nats ([dd720fd](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/dd720fdff0bc738b4186476611c88784fef323a2)), closes [univention/dev/internal/team-nubus#930](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/930)
* **udm-transformer:** Migrate the udm-transformer from poetry to uv and update container build ([4869689](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4869689ab36b4091f0b2d31751daa89aac83825c))

## [0.54.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.53.3...v0.54.0) (2025-06-02)


### Features

* add ability to configure external NATS for udm-listener ([4e3ea36](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4e3ea368d919cfcdc38c841b8142448657005ca9)), closes [univention/dev/internal/team-nubus#950](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/950)

## [0.53.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.53.2...v0.53.3) (2025-05-29)


### Bug Fixes

* **udm-listener:** Typo in provisioningApi secret value mapping ([04e5046](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/04e50469989b62768add7b53c14a8dda9fee8657)), closes [univention/dev/internal/team-nubus#1208](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1208)

## [0.53.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.53.1...v0.53.2) (2025-05-19)


### Bug Fixes

* **udm-listener:** add configurable storageClass and size to PVC ([80f985a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/80f985acd041b988cac4d8ad4824e588c4c1d7f0)), closes [univention/dev/internal/team-nubus#1181](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1181)

## [0.53.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.53.0...v0.53.1) (2025-05-16)


### Bug Fixes

* **udm-transformer:** Update base image to include univentionObjectIdentifier changes from upstream ([cf47179](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/cf471797651a182f9fb4411128419d60300e8fa4)), closes [univention/dev/internal/team-nubus#1143](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1143)

## [0.53.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.52.0...v0.53.0) (2025-05-16)


### Features

* **udm-listener:** Refactor secret configuration to use "{client}.auth.existingSecret" ([97a66b4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/97a66b4e14d5fa15cf7c0eba332723770e387525))


### Bug Fixes

* **udm-listener:** Remove default comment from values file ([d5cd6e1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d5cd6e151fb51ef006c948bb9b205c3bd171d8a6))

## [0.52.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.51.1...v0.52.0) (2025-05-11)


### Features

* move and upgrade ucs-base-image to 0.17.3-build-2025-05-11 ([a7753ca](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a7753ca06c351780128073fc5b526a9b67e80332))

## [0.51.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.51.0...v0.51.1) (2025-05-10)


### Bug Fixes

* add missing env for ldap-server in docker-compose.yaml ([d8e0cd4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d8e0cd41816fd531413cd0b76b02fbc0e3f5a5d7))
* move addlicense pre-commit hook ([46f1aaf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/46f1aaf965b8980b5e6cf24fb5603a57fb36f794))
* move docker-services ([194d197](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/194d1972cb91c26c69024ec6b5985543ced65125))
* update common-ci to main ([73ff4de](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/73ff4de40b8d3d06f275b673ae5ee0aa1788893b))

## [0.51.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.50.0...v0.51.0) (2025-04-29)


### Features

* Bump ucs-base-image version ([b567617](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b56761753954f14f69d8bb5f1e5b508b31b7696e)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)


### Bug Fixes

* final version of wait-for-dependency ([0479143](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0479143a5dbdb2d9db81c8a12a34f247ebbeeedb)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)

## [0.50.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.49.4...v0.50.0) (2025-04-29)


### Features

* Remove docker.io dependencies ([e63b436](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e63b4365b740e9cb0efae6265b5bde2725111b41)), closes [univention/dev/internal/team-nubus#1131](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1131)


### Bug Fixes

* Bump base image versions ([21e7738](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/21e773830f08f1235d0a2017cebd1b6379eb5e45)), closes [univention/dev/internal/team-nubus#1155](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1155)

## [0.49.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.49.3...v0.49.4) (2025-04-10)


### Bug Fixes

* make copy calls in container init more robust ([dd26ec3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/dd26ec33cac85d3f77edeca9907b200bbc06fa48)), closes [univention/dev/internal/team-nubus#1079](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1079)
* update common helm dependency to remove deprecated dependency and avoid dockerhub rate limits ([41d6166](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/41d6166ce33298928718848f19ad4259a7d2015f)), closes [univention/dev/internal/team-nubus#1079](https://git.knut.univention.de/univention/dev/internal/team-nubus/issues/1079)

## [0.49.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.49.2...v0.49.3) (2025-03-17)


### Bug Fixes

* unblock pipeline by getting the bitnami common chart as a transitive dependency of the nubus-common chart ([4eff19b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4eff19bf2ce29e30380c55f10d1a8cabd927ec6c)), closes [univention/dev-issues/dev-incidents#131](https://git.knut.univention.de/univention/dev-issues/dev-incidents/issues/131)

## [0.49.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.49.1...v0.49.2) (2025-03-17)


### Bug Fixes

* **nats:** bump nats image version ([385c424](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/385c4241c5b3e67ad736088cd290a49b84561f30)), closes [univention/dev-issues/dev-incidents#131](https://git.knut.univention.de/univention/dev-issues/dev-incidents/issues/131)

## [0.49.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.49.0...v0.49.1) (2025-02-27)


### Bug Fixes

* Avoid prefix "nubus-common" in named templates ([646100d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/646100de287cbf9a49e7ba5a8f280994518fd2c5))

## [0.49.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.48.4...v0.49.0) (2025-02-26)


### Features

* Bump ucs-base-image to use released apt sources ([df44c76](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/df44c76a8d746ce9d11d7645efdb0229443b6791))

## [0.48.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.48.3...v0.48.4) (2025-02-20)


### Bug Fixes

* added more callbacks ([569fa99](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/569fa9977e8bdb5d49a32203d2d3c882cfe269c1))
* dispatcher integration test ([f1301b1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f1301b1547fa9b867c904527d136060fb88537a2))
* dispatcher should crash if it can't connect to nats ([9237c88](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9237c880c822a17273202d110e5cd2bec089526a))
* dispatcher unit test ([bbaf9d4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bbaf9d40fab8bbd3f9f13e79bcc569060d050ff6))
* Migrate dispatcher from websocket to long polling to ensure the container exits if it looses connection to nats ([22f44d2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/22f44d2d5422797c0736c79ee46e4510931784d4))

## [0.48.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.48.2...v0.48.3) (2025-02-10)


### Bug Fixes

* set plugin mounts to read-only ([2c0f91f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2c0f91fdee5cdf182ee691d032f88fd523744221))

## [0.48.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.48.1...v0.48.2) (2025-02-10)


### Bug Fixes

* add .kyverno to helmignore ([897d653](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/897d65360459be8e9d1ed2f06c9146c51747ed63))

## [0.48.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.48.0...v0.48.1) (2025-01-26)


### Bug Fixes

* **udm-listener:** Fix duplicate resources key ([0a26c24](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0a26c246c159c900e4af29a1aef59d00f51452d8))

## [0.48.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.47.0...v0.48.0) (2025-01-13)


### Features

* upgrade NATS chart ([2685c9f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2685c9f5f934f61f3bdeb4e0331030973e966a92))

## [0.47.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.46.0...v0.47.0) (2024-12-20)


### Features

* upgrade listener base ([d4f43ec](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d4f43ec05e675cc6fb6c2d8bf498b014ab046e43))
* upgrade UCS base image to 2024-12-12 ([2e94db9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2e94db9e7c007388cdcb1f010b831fbe76f42fd4))

## [0.46.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.45.1...v0.46.0) (2024-12-04)


### Features

* **udm-listener:** use ldap-server-primary coupled to ldap-notifier ([457be7c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/457be7c65b4e06cd6a290bc0a7d5582bc7762c16))

## [0.45.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.45.0...v0.45.1) (2024-11-27)


### Bug Fixes

* extension template ([228d22c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/228d22c4efed81e70e0f683abd4b8ce985f9409f))
* kyverno lint for provisioning chart ([f757c68](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f757c687eb30c61b28febf6a0d317b06c221d581))
* Kyverno lint udm-listener ([3e6d5a1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3e6d5a1f5b58b6b652243dddf983df89867aaac5))
* make resources optional ([a566578](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a566578450903271dba071f92b94c35479a95036))

## [0.45.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.44.1...v0.45.0) (2024-11-05)


### Features

* **secrets-refactoring:** generated nubus-common artifacts ([74d8859](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/74d8859e4c69fa42891d8a61ff24e64bf8d59212))
* **secrets-refactoring:** refactored values structure to existingSecret mechanism ([ec4d565](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ec4d5654457255d1b980799c1744850bc4859507))


### Bug Fixes

* fix chart version and track todo ([c78e0a7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c78e0a7502c5f0b3789bb2ad7e29470826f1da62))
* **nats:** adjust values structure to new standard ([2651b5b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2651b5bb7194448b2febf4f7b468e9cb7036b579))
* **nats:** bump nats subchart to version 0.2.0 ([9dc57c2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9dc57c2476f04e4a54bd74f4b3317be7a2440b05))
* refactor secrets structure to use bitnami style existingSecrets ([84eaa34](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/84eaa341c40f3a14111571798ce7c02e4b13625a))
* **secrets-refactoring:** add provisioning consumers configurability ([4a0850e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4a0850e5cba88b9248ff67dcdb571c3f8620f304))
* **secrets-refactoring:** all secrets migrated to new structure ([6a167c3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6a167c3ed2affae83a95bbcf0bca242b8e1462fd))
* **secrets-refactoring:** customized the generated values to get helm template working ([ba3a792](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ba3a792dcea0fea87fd56133f9bcfb951b6c6a03))
* **secrets-refactoring:** fixes while integrating into the umbrella chart ([5a2a7d5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5a2a7d55b5478f63bf02bed7faae0ca104656e52))

## [0.44.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.44.0...v0.44.1) (2024-10-04)


### Bug Fixes

* **udm-transformer:** fix typo ([973581d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/973581d9e489a64f4952aa4e9a74f05cc2d208a2))

## [0.44.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.43.1...v0.44.0) (2024-10-02)


### Features

* remove duplicate data from KV DB, Dispatcher generates reverse-mapping dynamically ([680c326](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/680c32613c476133472fdeaa22a2b602e1c6155c))
* support safely updating values in KV DB ([95c707f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/95c707f1dc3c02ea140e775c3509737ca227c5e9))

## [0.43.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.43.0...v0.43.1) (2024-09-26)


### Bug Fixes

* add missing imagePullSecret and imagePullPolicy to the helmfile templates ([8c6fb2f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8c6fb2f4bf190f30264586e459fd925ecb21e5b5))

## [0.43.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.42.0...v0.43.0) (2024-09-26)


### Features

* **ci:** enable malware scanning, disable sbom generation ([c47f943](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c47f943285b8d23333f5898b2904eca13714fc17))

## [0.42.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.41.0...v0.42.0) (2024-09-25)


### Features

* make subscriptions format consistent in REST API and persistence ([7314aac](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7314aac61a50772f08824ffb3d0aa33c390f5a1e))


### Bug Fixes

* increase wait for api timeout ([7ce1d5b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7ce1d5bfbeb420e09ed4002e8172b1caa102d7da))

## [0.41.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.40.4...v0.41.0) (2024-09-24)


### Features

* change subscription and messages API, simplify project structure. rename settings ([5297c4a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5297c4a338b307d8beb3afc9233148a9b77f5240))
* convert realm_topic parameter from list to object ([8e58585](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8e58585f4665573c922e080dd9fcf58baf29d9ff))
* remove message_seq_num from PATCH payload, as it's already in the path ([d79911f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d79911f1d0719b8afc80a51f4eb5b8574700386c))


### Bug Fixes

* remove config defaults from code, config name consistency ([62f8e7a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/62f8e7ac123b2fd400d3fbfe78aded3c134f2a9c))

## [0.40.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.40.3...v0.40.4) (2024-09-23)


### Bug Fixes

* OpenAPI schema paths ([211eb4f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/211eb4f4d60859882f8586562cd8c0946d94c1fc))

## [0.40.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.40.2...v0.40.3) (2024-09-23)


### Bug Fixes

* Don't leak secrets in bash scripts ([7178582](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/71785823232a914019a8460c35a44d4dcda333cd))

## [0.40.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.40.1...v0.40.2) (2024-09-23)


### Bug Fixes

* **provisioning-nats:** Increase the maximum nats messages size to 16MB ([7396f0a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7396f0afdcfcb88e0312000e760e744e968887c8))

## [0.40.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.40.0...v0.40.1) (2024-09-19)


### Bug Fixes

* **provisioning-consumer:** Modules executing from __main__ debug logging ([3db85ee](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3db85eea3165577bfbf83e24a174fd4a93e600fc))

## [0.40.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.39.0...v0.40.0) (2024-09-16)


### Features

* update UCS base image to 2024-09-09 ([241149f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/241149f241be1f99ec29066550c8ba8f6a427361))
* upgrade listener-base image ([714ea80](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/714ea802462c3cb09a2a7f83e4fa6212afc97f7c))

## [0.39.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.38.1...v0.39.0) (2024-09-12)


### Features

* changes relating to BSI compliance (udm-listener) ([49b6128](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/49b612867f258429b76c338ed57cb9bebbede14c))

## [0.38.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.38.0...v0.38.1) (2024-09-12)


### Bug Fixes

* new default port because of moving udm to a headless service ([383084b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/383084b9a6779b6e7198d3737f7d30349b5679c5))

## [0.38.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.37.1...v0.38.0) (2024-08-28)


### Features

* unify UCR configuration ([02038e1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/02038e1c9d9b2884311992f7d3d440f79f079282))

## [0.37.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.37.0...v0.37.1) (2024-08-28)


### Bug Fixes

* **nubus-provisioning-consumer:** return ProvisioningMessage with sequence_number and num_delivered to the consumer ([4704c6f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4704c6f867cb58197f88354b3ffc6ece089fb354))
* update log messages, add maxsize to [@lru](https://git.knut.univention.de/lru)_cache ([9845df0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9845df0e348b18b3e15ccff76a00f5ed80ade147))
* update logs to display message content only at the DEBUG level ([2735d4a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2735d4a9153d6c8b7b3be3b890884cf3cb5c7e9b))

## [0.37.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.36.0...v0.37.0) (2024-08-21)


### Features

* **register-consumer:** add data loader check to the consumer registration job ([749b63d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/749b63dd2a0a4b8972598d51ea4fd5185901a36f))


### Bug Fixes

* improve method to reload UDM lib, fix duplicate logs ([689adb8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/689adb86cc926d0f03343cbb66af4376c46d78bc))
* reload the UDM library to react to the changes in the data schema ([1b2a9ca](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1b2a9ca3f64efa10e4c8bdcf65aa921153aa20e0))

## [0.36.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.35.0...v0.36.0) (2024-08-19)


### Features

* add message model for LDIF Producer ([41024f0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/41024f03b5b91197c4734fb975a643b724c2e189))


### Bug Fixes

* h11._util.LocalProtocolError caused by timing_middleware ([8b2e4e4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8b2e4e4af663c7a73b20ee61077b047192daa527))
* UDM listener logs at INFO level ([66df353](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/66df3536efa00787d507653b14b5bb9e9c2ebdca))
* use of Python logging library ([68a3cda](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/68a3cda25ea873b82990b5c8ce3a5fb68cb2d0ba))

## [0.35.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.34.0...v0.35.0) (2024-08-10)


### Features

* cache consumer prefill state, cache credentials verification ([d110689](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d1106893b7b4cdb09bea1731b296ac4fa9c34096))


### Bug Fixes

* **udm-transformer:** point the udm transformer to the ldap primary instead of the proxy, eliminating out-of-sync conditions. ([a8cae7c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a8cae7cd16805f11529e68e9f9b3c6b48165b323))

## [0.34.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.33.2...v0.34.0) (2024-08-09)


### Features

* **nats-adapter:** set replicas to 3 and stream to type work queue to auto-delete messages ([d90c5bc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d90c5bcf48da04c2c681a8b0582352e01378759b))


### Bug Fixes

* **consumer-client:** acknowledge message only after all callbacks have been executed ([61992c5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/61992c51d90cb34c98f5a448865f50989e8fc205))
* fix small rebase error ([758d885](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/758d885005e7f6eef027aaf4e820d27f4f4144a9))
* make the nats stream type configurable ([30fd72d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/30fd72da1190344706418cb9389efe4dca0a7b76))
* **nats-adapret:** fix nats stream update scenario and add nats adapter tests ([c825f4a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c825f4a9711dcee2ddd27b0261f6d0b1a6cf7347))
* **nats-adapter:** set replicas back to 1 until nats clustering is reliable ([8e64bd4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8e64bd47fa3a5744f89378b173dc62c421d48e4c))
* **udm-listener:** fix container build and reactivate the udm-listener build in ci ([f7d5956](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f7d5956d38bf7fe14e5e250ee3bce4072d15e250))
* **udm-listener:** keep compatibility with python 3.7 for the udm-listener 5.0-7 container ([3b7f551](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3b7f5516c287441ea65d72781476c01b94b8510e))
* **udm-listeren:** extract the listener into it's own pyproject.toml to upgrade the rest to python 3.11 ([3081120](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3081120faac6ba5d6f344cbd7f1568cfaafeb3e1))
* use updated version of nats chart to fix disabling the anti affinity configuration ([8472e36](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8472e36111f3173fae64becf10f826be63539517))
* wrap concurrent task executions in TaskGroup to propagate errors from any task ([b49f5a1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b49f5a13019b8f9aadbc7e03edd8e90e8fb9bfcd))


### Reverts

* "fix(udm-listener): keep compatibility with python 3.7 for the udm-listener 5.0-7 container" ([49e60bf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/49e60bf71073f45934d4d6fd62bd45e595df0850))

## [0.33.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.33.1...v0.33.2) (2024-08-09)


### Bug Fixes

* improve the wait-for-provisioning api init container script ([57bc532](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/57bc53213df25bf48ec7fcffd4a7032684997ab2))

## [0.33.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.33.0...v0.33.1) (2024-08-08)


### Bug Fixes

* clean up nats credentials ([449ca00](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/449ca00ce69b292594861083606706cce35af63a))

## [0.33.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.32.0...v0.33.0) (2024-08-08)


### Features

* allow direct access to the Body model and MessageHandlerSettings from the module ([ccccaf4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ccccaf418bc152cfdd898a6ddb2455f81af0cbed))


### Bug Fixes

* **example-client:** fix example-client ([d7d121f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d7d121fc3c2f58dd4cc0b71d001113ca643ac4a9))
* replace dict with Pydantic model for the body field ([762b4cc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/762b4cc243139dd9ec4fb78b0718a6e457faf900))

## [0.32.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.31.1...v0.32.0) (2024-08-07)


### Features

* add request ID to logs, add request timing, fix log level config being ignored ([235768d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/235768d7cd6d7db9df3db0ccccf9eef0a5daa1e1))

## [0.31.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.31.0...v0.31.1) (2024-08-06)


### Bug Fixes

* add wait-for-api initContainer to the Prefill deployment ([9d575f4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9d575f4cb493584a39d52606063ec7275bc74ca0))
* **prefill:** make prefill retries configurable ([297845d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/297845d4683ea06d9fc86aa73b0ff702c5b52db9))

## [0.31.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.30.2...v0.31.0) (2024-07-31)


### Features

* implement retry mechanism for message acknowledgment ([2cd3f5e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2cd3f5ee8142b53e99481c7a2d9df38b0f4686bb))


### Bug Fixes

* **consumer-client:** small consumer client fixes and renaming ([5e0fa8a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5e0fa8a3154190740269734ac612b992e2a4b899))

## [0.30.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.30.1...v0.30.2) (2024-07-31)


### Bug Fixes

* **provisioning-api:** add startup task to create the 'provisioning' nats stream ([1447b4f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1447b4f33ae1410467439ed23dcff58061f10093))

## [0.30.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.30.0...v0.30.1) (2024-07-25)


### Bug Fixes

* trigger for semantic-release ([d7260da](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d7260da9396a750fac4159378660b2c3fe38e9b2))

## [0.30.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.29.1...v0.30.0) (2024-07-19)


### Features

* **consumer-client:** change producer names from LDAP-* to LDIF-* ([ce75fdf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ce75fdfb5f271771a4307cf9430ff8fbe76ef2fc))


### Bug Fixes

* add ldif-producer to docker-compose ([8b11493](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8b114939280349bf4ee77709ea8903f976c8e46a))
* migrate docker-compose to artifacts.software-univention.de ([1811d20](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1811d201dd13a746021f5e38b2b8eda56ede521e))
* **models:** change publisher name from udm_listener to ldif_producer ([258b0a4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/258b0a4a3ce3c3ab401ad714e1df33e721ce0aad))
* remove unnecessary env values ([b72ebc1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b72ebc107deae9a71df7e3f91ba45190de3793f4))
* replace the UDM-listener with the new LDIF-Producer and activate it in the UDM REST API ([4c802f6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4c802f66ce01cc8646bb94b23be65a8cb71c93f6))
* **udm-transformer:** make the ldap queue name configurable ([26e1778](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/26e1778674e2120c9a38ae374baccf9a93db7f3e))
* **udm-transformer:** only crash when an transformation error occurred for a supported object type ([4aaff67](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4aaff672ae77e94fed0fd0e9842f9c86d9d7668e))
* wip fixes for the e2e tests ([69d3d28](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/69d3d282d8f76ef35e5bcd85767e5a9a32eceed3))

## [0.29.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.29.0...v0.29.1) (2024-07-18)


### Bug Fixes

* fix consumer creation, add tests ([0893d91](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0893d912da6d55a1d42fde8108d20979f41b412c))

## [0.29.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.7...v0.29.0) (2024-07-10)


### Features

* UDM producer container loads UDM extensions at deployment time ([498e016](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/498e0163296bce7b0e14253fc1fcd8e936576300))

## [0.28.7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.6...v0.28.7) (2024-07-04)


### Bug Fixes

* remove LDAP index for App Center attribute ([b0357ae](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b0357ae861d1cf28db7a3985877e707ccaf58c3f))

## [0.28.6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.5...v0.28.6) (2024-07-03)


### Bug Fixes

* **udm-transformer:** mount ucr into udm-transformer pod ([d6e5424](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d6e542495c24fd7f99b055dcb8d7b009fe9b76d3))

## [0.28.5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.4...v0.28.5) (2024-06-27)


### Bug Fixes

* fix provisioning helm chart and pin udm-listener container to 0.28.3 ([ef2912c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ef2912c3f4d320fc02fd6a6f84d801eb5570b9d2))

## [0.28.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.3...v0.28.4) (2024-06-27)


### Bug Fixes

* add ldap position to udm transformer code ([5c4ad70](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5c4ad70e7c4f07c39678611f7181a0132eafd940))
* add wait-for-nats and respect global.imageRegistry ([48e338c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/48e338c8bcfa07488852e24f3551367eff6f2598))
* **udm-transformer:** add udm extensions to udm-transformer container image ([945e62a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/945e62ae1a236a596c11c9ea9687d2fd754341b9))

## [0.28.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.2...v0.28.3) (2024-06-25)


### Bug Fixes

* adjust support for individual annotations for each deployment and job ([1073859](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/107385941771f5aebeb34b78ddb403319efce872))
* rename register_consumers to registerConsumers ([539ff93](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/539ff9339610eae7f8cb2df97b5b73b8fa35cfec))
* typo ... ([7249e74](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7249e74233b544d0a8e2332bbcbd603e64d95ec2))

## [0.28.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.1...v0.28.2) (2024-06-25)


### Bug Fixes

* remove WebSocket API ([9c5e944](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9c5e9441479dea405824fc51cc75aa673df61ac1))
* stop the infinite request loop due to failure to prefill ([52d64c1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/52d64c1e9e1cca3a2f1dfa6c831e87b0a0726323))

## [0.28.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.28.0...v0.28.1) (2024-06-06)


### Bug Fixes

* add python3-univention-directory-manager-rest-client to the prefill ([7c021ed](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7c021ed45a1957f26a5ed0efb9cfe2a4b9bd8301))

## [0.28.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.27.2...v0.28.0) (2024-05-31)


### Features

* add logic to wait for the udm and nats ([d1ca562](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d1ca562fff57893f197d2e1405512ea6e1c4f2cb))

## [0.27.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.27.1...v0.27.2) (2024-05-29)


### Bug Fixes

* **register-consumer:** do not fail if subscription already exists ([de47892](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/de47892b91550b2bb0d832833ba3952e1548ee40))

## [0.27.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.27.0...v0.27.1) (2024-05-24)


### Bug Fixes

* **ci:** use fixed common-ci/helm package to not update dependency waiter tags ([ec98ab2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ec98ab2ceb13c80d654b803d160548c62a8c031f))

## [0.27.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.26.3...v0.27.0) (2024-05-23)


### Features

* push to harbor ([57b622e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/57b622e35d8b6d948d8d3564c2db2821bd11f8ad))

## [0.26.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.26.2...v0.26.3) (2024-05-23)


### Bug Fixes

* **provisioning-client:** trigger pipeline force-build ([3108efe](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3108efeebef8ee22182dd81f7835e766c93ed0da))

## [0.26.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.26.1...v0.26.2) (2024-05-22)


### Bug Fixes

* **helm:** add configuration for selfservice-listener ([5ad5a18](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5ad5a188ad157aab20b0ccecd6334c739472f70b))
* **helm:** adjust label definitions for all services, provisioningApiBaseUrl templating ([4fec3f2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4fec3f2fe0bd4c65e397d895e450c9a303edf732))
* **helm:** consumer-registration exit on error ([51cfbf4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/51cfbf42466bcbc4b330eeb79309bf0250bb1cc9))

## [0.26.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.26.0...v0.26.1) (2024-05-20)


### Bug Fixes

* **helm:** add additional templating support ([b3728e7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b3728e735d7b40636ab401ac5e5b24c3bd98764d))

## [0.26.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.25.1...v0.26.0) (2024-05-16)


### Features

* **ldap-producer:** push ldap objects into nats queue ([10dd83e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/10dd83e3a5bf21477aab61e2e218e156101dd93e))
* **udm-transformer:** add the udm-transformer to the provisioning helm chart ([b82b83f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b82b83f32fccdab51ad5b70e677e6eed5f73aa8b))


### Bug Fixes

* fix e2e testing pipeline ([fea82f3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fea82f3a13bfcf297b4d4eab5a4ab57262a6b6d6))
* improve e2e test docs and config ([bd5e5f1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bd5e5f1089a74755d2a821306e7f12032de6cba2))
* **udm-transformer:** add in progress acknowledgements to message transforming ([8ea4922](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8ea492265404efca62fb682cd7c8529cdbdb7a58))
* **udm-transformer:** clean up Stream vs Subject vs Deliver Subject ([d84270c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d84270c2a34a4feef64e3bd0221569be044eb1b8))
* **udm-transformer:** fix docker-compose setup ([38e55ee](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/38e55eed15caca1d63789368b30001f5a41e81fd))
* **udm-transformer:** fixed unittests ([f8cceff](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f8cceff5270c33552270dacad300331f3c8a7286))
* **udm-transformer:** working udm transformer service ([82375b9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/82375b9b94d33f42c3998f57e91138da147b8a05))

## [0.25.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.25.0...v0.25.1) (2024-05-14)


### Bug Fixes

* override global registry for all NATS components to docker.io ([123c617](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/123c617420ad2396310fd3b62477894ed78a0d58))
* override NATS global registry ([25a0139](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/25a01397b0c8e91b0bac3a16f301f57f5e5312dd))

## [0.25.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.24.0...v0.25.0) (2024-05-07)


### Features

* Update base image to version 0.12.0 ([f46e1c1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f46e1c1a4faf6bbcb87d63c32fa63b8811a62b98))
* Update listener base image to version 0.6.0 ([8bad417](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8bad417a07492439a0e7f6b3f47493321aa0de7a))

## [0.24.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.23.3...v0.24.0) (2024-04-29)


### Features

* changes to support the refactored umbrella values in a nubus deployment ([b81076f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b81076fc948f328ba79772fca2523135cb44f954))


### Bug Fixes

* adding package python3-univention-directory-manager-rest-client ([9530d02](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9530d02a1980ee89c6cc33ba7fd5f016fa103b9c))
* removing unneeded certifcate/private key mounts ([b4d2241](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b4d224194cd9820afca296baa04e0160e1cbb0dd))
* set no default for ldapHost, use variable if set, even in Nubus umbrella deployments ([b369030](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b3690306432d005b4795dc9409b6d8aaaa554476))

## [0.23.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.23.2...v0.23.3) (2024-04-26)


### Bug Fixes

* delete one message at a time ([0916476](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/091647678ac903b58b5b2e4003c3ecf21bc4db4b))
* fix deleting messages, fix unit tests ([ce45040](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ce45040171a7aba2f4e021a8d9d108836c173786))
* remove the logic of receiving multiple messages at once since it does not work with max_ack_pending parameter ([119b793](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/119b7934df96534af53e8f41454d50586bf41d39))
* use a consumer to get messages, and combine prefill and main streams into one, split by different subjects ([e5aaeba](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e5aaeba9fae3116355642cf70a71eec6d2769aa5))

## [0.23.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.23.1...v0.23.2) (2024-04-25)


### Bug Fixes

* add missing resource limits ([a9c71a9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a9c71a9aea02d3d80bd693267dcb2b850ca1b887))

## [0.23.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.23.0...v0.23.1) (2024-04-17)


### Bug Fixes

* **helm:** Update chart "nats" to version 0.2.0 ([7739fd8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7739fd89332d796d5a3543f47107ff63e3ab5ada))

## [0.23.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.22.1...v0.23.0) (2024-04-15)


### Features

* add configmap for registration, move admin credentials to the Secret, and wait for api to start before running the registration jobs ([1849d7c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1849d7c66bb276f131e8f1ec8cb0b6618545e409))
* register consumers via k8s ([e01ca5b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e01ca5b212ad055e268dbace6f2c1abb06ceaa8d))


### Bug Fixes

* add resource limits and requests to the initContainers ([30a5b8e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/30a5b8e078fa0bf0e38a8ba9b5c74c7e397385f5))
* create Job for each consumer, change provisioning-api image tag to latest ([b8d0d5f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b8d0d5ff512744424f45fbc7657da386afa21ecc))
* define resource requests and limits for the job ([12d0120](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/12d0120c67de689857db2f9aa638f37dede39dae))
* improve logging and error handling during consumer registration ([c4104db](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c4104db4de1bc2354066e9984e4f2e81048adb73))
* pass already rendered JSON via secrets for consumer registration ([1c8d1ba](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1c8d1ba7ca50f35f60b73d39a841c6a6388d4985))
* use wait-for-dependency image instead of busybox, use static name for initContainer, do not hard-code port value, add curlys and quotes to the bash script ([ca6bce1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ca6bce1ecc3d4033527d72a9e7ee15495619a650))
* use waitForDependency  image with already installed curl ([3ee1481](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3ee148156a412d77565d7face4a1e00cc0fb98c4))

## [0.22.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.22.0...v0.22.1) (2024-04-12)


### Bug Fixes

* use repository versioning on pypi released package [force-build] ([28c22f2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/28c22f252e2e57ddb707224cf41faddd071270d0))

## [0.22.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.21.4...v0.22.0) (2024-04-10)


### Features

* add a CI job for publishing provisioning-client lib ([ffc947e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ffc947e5396d984978d4e62b14b3f4259dc65a39))
* add CI job for testing provisioning lib ([1743c51](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1743c51ad7f09d7d98411a3196d45814ad1add9f))
* add pyproject.toml for client lib ([7d80563](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7d8056343b85b667f7be6570681ff2064b758bf5))


### Bug Fixes

* add 'build_python' stage ([165aced](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/165acedc7ec3602b0f4a515dea23058f474a4bce))
* add missing import ([d8c2f8e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d8c2f8eb01be892afa681e520c94ef47babee3a9))
* add POETRY_VERSION to the gitlab-ci, increase python version ([2b6ebc1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2b6ebc129366e96cc28112e66cb29b3a228518c0))
* add pytest to the pyproject.toml ([6f58731](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6f5873151e1fc7727f83e3c6fc544bc5876f3b47))
* change command to run the tests and path to the coverage.xml ([4d845c0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4d845c05b8c5b43115307d31ffba590a84c380b2))
* do not use folder 'src' as the top level package ([681b1ff](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/681b1ff1c850bb052d86e2025b6dead3b2596134))
* fix code after refactoring ([596e029](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/596e02927d0d9ea51db09a828ba83ae201a11b3d))
* fix copying the source code for the example-client ([388b3fb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/388b3fb8deab76036f77de34cae1c8ac28002303))
* fix installing the dependencies for the test container ([1f5ddc4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1f5ddc497257d4aeafd4698c2f420fd8cf0fda24))
* fix typo ([b6d4c70](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b6d4c709e703eb0a7f717fa4f3bda2e24fed965d))
* install poetry before COPY src ([4064ce6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4064ce6e89db001a4b053c61f7645e0c5f702020))
* move test_provisioning_lib to the publish_provisioning_lib needs ([729db4b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/729db4b001fa9cd27c5b54b91184646622abac62))
* rename 'example-client' to 'example_client' ([fcbcb9e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fcbcb9e6d1309b6c1dcadb429cb73d5ba7bed349))
* rename 'provisioning-lib' to 'provisioning-consumer-lib' ([baf8464](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/baf8464c3f2fa3b3a4ada173b4e06276c5fb0d4b))
* return back the SHELL option -o pipefail before RUN ([358f7ba](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/358f7bad08149e27781ae3f2f24bd181b3a9e4a2))
* use 'build' stage instead of 'build_python', use lower python version ([4798ec9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4798ec91d397f36e09aeac44553f6c99aae60998))
* use pipx for installing Poetry instead of curl, and deliver docs for all parts of the project ([635242e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/635242ef7bf0f0343839be9fe7e434847414fb8e))

## [0.21.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.21.3...v0.21.4) (2024-04-08)


### Bug Fixes

* preserve the order of the message delivery, add tests ([f73f353](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f73f35342cbcfde8c309e8443a8f8e45666b7772))

## [0.21.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.21.2...v0.21.3) (2024-04-03)


### Bug Fixes

* add maxsplit param ([c1d74cc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c1d74cc16472ca355935c2fc216ffbb50c9445e6))
* implement direct nats access for dispatcher and prefill, use the watch feature to reduce nats calls ([389a000](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/389a00056837b7603fc318a5163cb2af993109cd))
* refactor and fix the logic for watching for the changes ([cf92d9c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/cf92d9c103cb7c6616531ea58d988d289a5e85f8))
* remove credentials for dispatcher ([0c5c51d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0c5c51d7f1a3deebea5b08eb049cad44b5206c4b))

## [0.21.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.21.1...v0.21.2) (2024-04-03)


### Bug Fixes

* **dispatcher:** handle failed events in the dispatcher ([a901c4e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a901c4ea2bd2c766a40f4ce5093297f13fb34bf9))
* **dispatcher:** raise an exception in the dispatcher on failure ([c0290d3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c0290d3df91bde0f10a47cad6500b768fcec4269))
* forward the entire deployment instead of the pod-hash, use upper case for constants ([7a79b73](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7a79b73f6dde9411c885afcf618d047b501af97a))
* **prefill:** do not return the message to the queue on error ([6361315](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6361315316b6937fc3f8edac855087a859394428))
* prevent redelivery of messages by extending AckWait for prefill service ([e84c7b7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e84c7b79a2461c26f21659dab4408c2149e7c7f5))
* prevent redelivery of messages for the dispatcher service ([ac5738c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ac5738c04aa24d47763b359a869b42a07b4435a3))
* remove unused values from PrefillService, add annotations ([fc01cfb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fc01cfb27ae50bdfe6dee74e2405840f0ddec807))

## [0.21.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.21.0...v0.21.1) (2024-03-22)


### Bug Fixes

* **ci:** update common-ci from v1.20.0 to v1.24.5 ([783ecab](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/783ecabd2dc0a6bfbe0466a4ce8f0097f1b049a7))
* **helm/provisioning:** add missing registry keys ([3860adb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3860adb670a6dc2864bb1e1fab70e3f86343df28))

## [0.21.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.20.3...v0.21.0) (2024-03-22)


### Features

* Set "global.imageRegistry" in the provisioning Helm chart ([684ca89](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/684ca89e0f3cad2679bebac2a8a3e10bd0e0f557))


### Bug Fixes

* Add helm-docs templates for "example-client" and "provisioning" ([38e2a66](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/38e2a669b8ec6b4aea3f309ef43539c822b532a4))

## [0.20.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.20.2...v0.20.3) (2024-03-20)


### Bug Fixes

* add missing values to tests/base.conf ([76453bb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/76453bbe919cf80612caa6d10f561889dfd4b013))

## [0.20.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.20.1...v0.20.2) (2024-03-15)


### Bug Fixes

* change credentials for authentication for Events endpoint ([06ae777](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/06ae777e4f6aa140d09d5f8ad17cd271e41ead16))

## [0.20.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.20.0...v0.20.1) (2024-03-14)


### Bug Fixes

* delete force parameter from the client api ([a51356e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a51356e3b777587c73c629698b42cbdb577995f2))
* merge main ([0f9588b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0f9588b461c2b6863c23dd11c5465ba02f00ad27))
* merge main ([62cfb84](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/62cfb84fca3d9ecf5d60b412a1a5758efad9f165))
* remove skip prefill parameter ([4ba7d0a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4ba7d0af9014f457a1d89b2576c4dc71ba4b398b))

## [0.20.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.6...v0.20.0) (2024-03-14)


### Features

* allow admin to delete subscriptions ([2655165](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2655165cda75b48b01ef2b889a97fc426f7f24d4))


### Bug Fixes

* fix rehashing password ([2a2c139](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2a2c1394e58c71e5cbfcb07159b3e7be48e1625c))
* rehash the consumer's password if needed ([99f3390](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/99f339098e75895c92aab24f5641b41c4e5748c3))
* remove DELETE route from the  internal app and rename 'sink' tag ([269ba10](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/269ba10c07348dde7ed524c966f7ed0164494773))
* save subscription list as a list, not string ([1fa7793](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1fa77930d5a8bffb189fc6072d86a447f7260feb))

## [0.19.6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.5...v0.19.6) (2024-03-14)


### Bug Fixes

* **helm:** udm-rest-api service port is 80, not 9979 ([d89cbc9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d89cbc9eebe89fec4b4cfb5f0e2e823578bead7b))

## [0.19.5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.4...v0.19.5) (2024-03-13)


### Bug Fixes

* **helm:** fix Chart.yaml version match for nats-helm dep ([d6e2410](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d6e24106ac159f46a65983c3373729588994d267))

## [0.19.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.3...v0.19.4) (2024-03-13)


### Bug Fixes

* get rid of unclosed client connections after e2e tests ([0d38af8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0d38af8c2e7aafabf7b5e0a661c532c906bd362d))

## [0.19.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.2...v0.19.3) (2024-03-13)


### Bug Fixes

* **udm-listener:** fix regressions from migrating to internal api ([dc8aebf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/dc8aebf3904181734d6403ccc923bfdd1e1f981b))

## [0.19.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.1...v0.19.2) (2024-03-12)


### Bug Fixes

* **dispatcher:** add missing env value to configmap ([34afe1f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/34afe1fcf322679bde9145a7a136821ed018abda))

## [0.19.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.19.0...v0.19.1) (2024-03-12)


### Bug Fixes

* remove error word from uvicorn logger ([2c75a32](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2c75a328edee686aa59b5e994c04cf7372e58af6))

## [0.19.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.18.0...v0.19.0) (2024-03-11)


### Features

* add authentication for AsyncClient and fix tests ([7fdfc01](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7fdfc01b5989aa747a937e62c6c16ae269e475c7))
* add nats user ([e936fbb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e936fbb19acbd042474869dfd11c0a862b384db3))
* implement consumer authentication ([3a57774](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3a57774bb90213b6e4b209cae0895def0882a657))
* move internal endpoints to the sub app ([8f64bb1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8f64bb1f479586a8414fb1830610ab4c440e2deb))


### Bug Fixes

* configure settings ([4d384b0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4d384b0c2aa73e9bda4e6fc0b0ccf59709eb6f40))
* do not expose the auth attribute to users of the AsyncClient class ([fa39d55](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fa39d559e9b71955aac14938674ac81112626d39))
* **example-client:** fix env vars for example-client and url for creating subscriptions ([03429c7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/03429c77ecead9e2eccb21193f0da21360720c2d))
* fix method import ([bf184cb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bf184cbada1d36b12eb2e7af16908624806b0162))
* merge main ([8090a3c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8090a3cd4978d481e69f00836b892a903f7545e8))
* merge main ([d22bef7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d22bef7b13e4342ad983008ac5f2008e59cd259e))
* merge release commit from the main ([187e0ec](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/187e0ec8b3c66038d03ddf5c9c1b4855177d5d05))
* move internal api to the separate route and hide from consumer OpenApi ([6f36ed8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6f36ed86eeeb6535f086342809c7e062d352b430))
* update class constructor to initialize _auth with user credentials, extract _admin_auth ([d63e14a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d63e14a9b9b2103c1592d2e04162e4f3d2f94f55))

## [0.18.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.17.3...v0.18.0) (2024-03-08)


### Features

* add helm chart for provisioning example client ([ae2f301](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ae2f301771e97fd9dbecabebaf5d6d49a5c5bf22))


### Bug Fixes

* fix async context manager, use it and make subscription optional ([7513a45](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7513a45f41765d2130d4c35391a97a4a39f18dea))

## [0.17.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.17.2...v0.17.3) (2024-03-07)


### Bug Fixes

* **dispatcher:** terminate if nats connection error ([d52a1e1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d52a1e133969acc528182e5b011e052040f7b7e7))
* **prefill:** terminate if nats connection error ([1cbab33](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1cbab33c346532d48d028b32dd117b3ad6062acf))

## [0.17.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.17.1...v0.17.2) (2024-03-06)


### Bug Fixes

* **helm:** rollback to deployment ([c64434f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c64434f7719a627b3a5d2147878ab12210890222))

## [0.17.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.17.0...v0.17.1) (2024-03-05)


### Bug Fixes

* **helm:** revert workaround for missing nats credentials from kubernetes secrets ([c752e8a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c752e8a31af3d3f7893c1783630f2d906a627de1))

## [0.17.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.16.1...v0.17.0) (2024-03-04)


### Features

* **example-client:** fix example-client and migrate it to the callback api ([c3045cb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c3045cb1bd9a58a3f546eacf36ce4bc639d9d4e2))


### Bug Fixes

* **consumer-client:** Fail early if required settings are missing and make Settings composable ([582c0a3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/582c0a3dc503b4bf43fe41cddfde0df471191ba0))
* **consumer-client:** migrate to a shared aiohttp session on the class-level to simplify authentication ([25ddffc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/25ddffc6cf3c1cbef4401b9f92a9a56289c1cfba))
* **e2e-tests:** don't override existing env values during test runs ([3c06327](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3c063272d5d591d8902ec74fb4f5ee786067ab9c))
* **e2e:** missing arguments on settings instance ([8848c3c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8848c3cade8e7be8a4b9dc8fb980628c8e785d4f))
* **example-client:** acknowledge messages by migrating the example client to the MessageHandler ([7f3046d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7f3046d73f77438bf4066bb7c7760a4e342a6496))
* **helm:** workaround for missing nats credentials from kubernetes secrets ([705f81f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/705f81fe15d74f57e9db7794e6dd77aca082dcf9))
* **listener:** Disregard temporary LDAP objects ([9c6f1be](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9c6f1be7530f395cce07e49638d54b01bbeddfe4))
* **listener:** missing ldap configuration ([acc5467](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/acc5467cfe3ad2a38998ec8029c915d4bf10b1a4))
* **provisioning:** udm-listener needs access to the consumer events api ([c5178ca](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c5178ca473da770342cb941980c1cb70dd308d40))
* **shared:** logging formatting error ([43d151c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/43d151c564e5083cbd408062c573035af426d6ac))

## [0.16.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.16.0...v0.16.1) (2024-03-04)


### Bug Fixes

* **admin-api:** add env values for admin-api and prefill to helm chart ([1d13ce1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1d13ce1630ea8f635a5e6fd81508e5ae5a48b4f5))
* **helm:** make sure old pods terminate before new pods start to avoid bug ([c013bf3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c013bf3603496567d98b2d0a458fc2ef8326d019))
* **helm:** workaround for missing nats credentials from kubernetes secrets ([5761725](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/57617257b9ffe4825e87934fb689ccf835f496a8))

## [0.16.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.15.0...v0.16.0) (2024-03-01)


### Features

* add admin api ([deeb276](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/deeb2766ef561c8d00e496a91245f6b4a1549f99))
* add Basic Auth for admin endpoints, add config file to nats ([8de5cac](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8de5cac13a44e675d6ab53087c774638352ba57d))
* add bcrypt and passlib ([6d244e3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6d244e362064776ae240d9452742883149da61c9))
* implement registering subsciptions, fix getting all subscriptions and deleting subscriptions ([d08649a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d08649a01302b93bd6bf9a98aeef7549fac74972))


### Bug Fixes

* add authentication for creating subscriptions in the AsyncClient ([36f30c0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/36f30c0f1425b9e85ca8bb40dba9e45cbc729046))
* add needed env vars for connecting to the nats ([2d16809](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2d168099614fd40e435fc83a3a1b6ce670987e66))
* authorize admin through FastApi not NATS, fix tests ([d7cdee9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d7cdee98f7df865147e3aa26990e69d5c8c95483))
* catch more specific exception during connecting to the nats ([9e7fa54](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9e7fa548013bc9b734aeeb301024676cb8cb27c6))
* disable running end to end tests in pipeline ([604e1a3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/604e1a3090ce0e26b430de1af1d9623dcd45d994))
* enable e2e tests in the pipeline ([f01694f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f01694f4537767892cfb86a18b00be108afca383))
* merge main ([8f4f6bd](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8f4f6bdc0fc90e29a44f6fbdd561d0e5552bb114))
* merge main ([905089a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/905089a3ed406b6cf4f5f54117f1686c49dd9ee5))
* remove methods to create and get subscriptions from AsyncClient, extract admin creds to the settings ([ac39bbe](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ac39bbea602ac66b6a826191d5e07faed390ea89))
* remove resolved comment ([e733e78](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e733e78f00ae42c12e59043e8d1c59219abc8fba))
* return back creating subscriptions to the AsyncClient, create AdminSettings, fix tests ([2489ed4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2489ed4b690d22c0c6a970c994abe222c37582ad))
* split NATS Key/Value Bucket into Multiple Buckets ([3972e23](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3972e236762e36a554c1e200542ee9d646961f44))
* split settings and remove default values for credentials ([02a8269](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/02a82693b983a2f3c8f391a49abffdfd524b27c8))
* update dependencies ([ee856f3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ee856f32f4b5497098ad2f9849e6b7bb17677c13))

## [0.15.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.14.1...v0.15.0) (2024-03-01)


### Features

* Add nats credentials ([c5b7769](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c5b77692c3bf2f376e313244e403a0614fa6fce7))


### Bug Fixes

* add nats credentials to configmap in udmlistener ([18e85e7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/18e85e7fef0fbb81c22439e6d4e3357b44d47f23))
* Fix tests, except a few ([6999891](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6999891cc9ac5cba86e1c54fabbcaeb45b6ec7be))

## [0.14.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.14.0...v0.14.1) (2024-02-29)


### Bug Fixes

* change publisher_name description, rename methods ([7439ab4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7439ab4e07af5dd7681626f457db6869f842a216))
* delete the messages by sequence number ([d0068d0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d0068d0cfe93446408be3197e632adff1ed401a3))
* fix example-client and tests ([fefd70c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fefd70ca6a53afbbe00f7456e9325db1467922ac))
* fix PROVISIONING_API_HOST and tests ([4d28b3c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4d28b3c1d7c07be5da8ba58a4e117965f4d6020c))
* introduce ProvisioningMessage for client-facing API responses ([88a0c22](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/88a0c2254f24404ac7c946fd8b28a471233549a7))
* merge main ([20e35ae](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/20e35ae625ff2d5229b2de9226dd205982208cc1))
* merge main ([d12f531](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d12f5313f5b164f14f291f2fda6374eb1a887e69))
* merge main ([e8f844a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e8f844a7320751b67ee61176ed4a23e58a7feda6))
* parallelize deleting messages, add num_delivered field to the ProvisioingMessage and use this class in the exmple-client, rename methods ([cd2470b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/cd2470bd4f167c0c32c521da467761de434b4415))
* pass queue type to delete message, fix tests ([278fef3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/278fef32ab970a049a17d1e54a6af120d00b956a))
* remove python3-venv from udm-listener Dockerfile ([50238cf](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/50238cf7bc5be45bbbb4c73475ecaca84b0c69d2))
* use MessageProcessingStatusReport for a single message, fix no module error with udm-listener ([990ca94](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/990ca94b1b8f0c9acb0efeb5a29fe6b04c5056f9))

## [0.14.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.13.1...v0.14.0) (2024-02-28)


### Features

* **docker:** prepend provisioning to images ([bd3e2c3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bd3e2c3c496c40242bf4418165bb4a91b2a4e7fd))

## [0.13.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.13.0...v0.13.1) (2024-02-28)


### Bug Fixes

* **helm:** unset imageRegistry, drop unused non-global imagePullPolicy ([88e71d6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/88e71d6f90fdfc21eee07b1b2b3c9cb679e424c8))

## [0.13.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.12.0...v0.13.0) (2024-02-23)


### Features

* new BSI compliant helm chart for use with umbrella chart ([cfad306](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/cfad306467212a93e5b365877cd723ea5349ee96))
* new BSI compliant helm chart for use with umbrella chart ([6edd096](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6edd0962002444cc6f73f65de8b244aaec417b94))

## [0.12.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.11.2...v0.12.0) (2024-02-22)


### Features

* Add CI build for example client ([f11ad4b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f11ad4b21c87de5a056cad31d699768c793962a2))
* **consumer-client:** abstract polling into syncronous callback wrapper ([7f92ad5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7f92ad5fcfbfa5d521c91b133f4be99f4e3926d4))


### Bug Fixes

* **consumer-client:** add final MR comments ([5f70adb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5f70adbc531b3f456d69608879bb67a9584bc8c7))
* **consumer-client:** allign with api changes ([2baa680](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2baa680e0550d7874349f3acf8c3da3b6237bd3a))
* **consumer-client:** improve callback wrapper and extract it into a separate class ([d4d02ec](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d4d02ecab5776612743803b47eb4a5d9f4394472))

## [0.11.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.11.1...v0.11.2) (2024-02-22)


### Bug Fixes

* change consumer endpoints to use subscription istead of sibscriber, fix creating prefill queue ([d7a1dee](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d7a1deeffcfa7283685ac540f4afd277c236769a))
* create subscriptions once, delete the whole subscriber instead of a subscription, fix endpoints, use consumer's API endpoints, request prefill for all topics altogether ([7d1581b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7d1581bf9e6a606492c5b2b1ee6932f9228481f2))
* merge main ([d9949c8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d9949c8e01cca125e17d3d3ea6c4c0ab9acb8f0b))
* merge main ([c6e74dc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c6e74dcc625810b1eeb02c582a738202c00734f2))
* Update packages ([7074d56](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7074d56547d0e00b89c2ee0acac2962831b56601))
* use tuple for realm_topic instead of list ([a346c6d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a346c6dd0ea7670700180e7e69fdf3689e5b7dfa))

## [0.11.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.11.0...v0.11.1) (2024-02-21)


### Bug Fixes

* Start uvicorn app so that no reloader runs ([0d56424](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0d5642423046c82ed04ad33756f14dea31a57f96))

## [0.11.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.10.1...v0.11.0) (2024-02-12)


### Features

* **client:** Containerize example client ([c9f8f86](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c9f8f86acd663741e9807485fe45390aa253d503))

## [0.10.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.10.0...v0.10.1) (2024-02-07)


### Bug Fixes

* **consumer-client:** add client E2E test including event generation via UDM ([4142f9f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4142f9f6ea17a58ce19130200c0f1a2e8eef50b0))
* **consumer-client:** add UDM REST API Client as new dev dependency ([51b9fb2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/51b9fb200fec356ea9026d19144f67dccbae1964))
* **consumer-client:** adjust async client after rebase ([bd19198](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bd191982660bccffd6926df79c9a8f57cdd09fbd))
* **consumer-client:** fix outdated code and add tests ([98df94d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/98df94d91c93cf3dbb8ebf2d948756ef8701a98e))
* **consumer-client:** fix outdated code and add tests ([f98558b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f98558b5e8087c63214650816e2f42c35cfbedf2))

## [0.10.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.5...v0.10.0) (2024-02-06)


### Features

* add endpoint for creating prefill stream to the Consumer Messages API ([5bad721](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5bad72157216e7eec280dc6448c8b5ed170cabcb))
* add endpoints for updating queue status, for sending message to the sub's prefill queue, create adapter for Consumer Messages ([c72d1a4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c72d1a4d74a8464d28b1882714ebec719a897090))
* add sending the request to the prefill, add prefill container, get messages from prefill queue first ([79f4cb3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/79f4cb381e7189c42f9bb679209381df316d2dfa))
* create prefill deamon, fix Dispatcher, fix subscribing to the queue ([2e6292b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2e6292bca659d72c1ab918727cddfdaa129f855f))
* handle failed prefill request, delete consumer prefill queue before creation ([8319498](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/831949882e05a819056c6f5564289212d10107e2))


### Bug Fixes

* add licenses ([a914113](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a914113bb3b8315c389dd2e3cda96cf0e1db390f))
* create durable consumer before subscribing to the stream ([e3c6600](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e3c66005205c6183da23aa8e35dbe1e260122e5f))
* delete unused print ([b4a9688](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b4a96882dfb47c85b917af15cc623397bdc20e2b))
* do not delete prefill queue if pop is False, fix tests ([5abfb27](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5abfb27b6a803f168aa5e294c97507b09cc5b6ac))
* fix creating consumer, create stream and consumer during creating new subscriber ([db60a2d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/db60a2dac917dd50fbd1426a2fdf56b3e2b39fd2))
* fix handling failed prefill requests, add tests for prefill logic ([e1b9c7a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e1b9c7abe79a0f60b9b4ad935c31957bcf7e77c8))
* fix the method of getting messages ([d22ba30](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d22ba303265dc8f9d2a104f2839edb30cd24ffe1))
* merge main ([b6c9ef3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b6c9ef3bfbf2c8d89e0486b2c673b0b47587e461))
* merge main ([324fee8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/324fee8b489f5af8b2b65d170437cd4fb4aaada2))
* remove dispatcher logic for sending events to the incoming queue ([5dc3ae3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5dc3ae38d13a9c2bcef11b0c49efd1786391d70e))
* remove nats logic from dispatcher and prefill ([a542f79](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a542f798b7ff213d4e1f3b30864911fbea0b2347))
* use correct durable name for subscribing to queue ([1362bba](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1362bba9a03731796ae8935b5e39f84252e1ac52))

## [0.9.5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.4...v0.9.5) (2024-02-02)


### Bug Fixes

* **helm:** remove liveness and readyness probes from dispatcher ([6070490](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/60704902a08d639884012ea3dfcf4d27a9b8a7fe))

## [0.9.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.3...v0.9.4) (2024-02-02)


### Bug Fixes

* **helm:** Unify and fix nats server config ([fa2abb7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/fa2abb766cd3febc6ea9faf8ae0ed26035db3d17))

## [0.9.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.2...v0.9.3) (2024-01-30)


### Bug Fixes

* **udm-listener:** Missing serviceName and replicaCount ([3aae8b9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/3aae8b99dc4586dc526f156c1075e7d397fe1bad))

## [0.9.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.1...v0.9.2) (2024-01-30)


### Bug Fixes

* create stream and consumer during creating new subscriber ([5e14f6f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5e14f6f9907141d9d19def2cf76bfea4d431479e))
* make ldap_server_uri a propetry, not attribute ([227c321](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/227c321fbec75bf488f934c02d503bd9a538c809))
* merge main ([f34062c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f34062c9d9251ecf80aaac0100ddf88f07c99920))
* merge main ([2eaf1ca](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/2eaf1ca35f629b9e7f153a7a97e22886e075875c))
* reuse connection to ldap, use ldap_host property ([b15c47e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b15c47e2b0ce253e5445411ef19686e163262a7f))

## [0.9.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.9.0...v0.9.1) (2024-01-29)


### Bug Fixes

* **helm:** Allow to configure the NATS hostname for listener chart ([8a58663](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8a586637c1e79baa2354cef456ef081bb80deec9))
* **helm:** Avoid to render an undefined AppVersion into the README ([6ee5cde](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6ee5cdefe0fb14c3ee65c781dae9185543fc0f61))
* **helm:** Remove unused key "environment" from linter_values of listener chart ([1dc6ec3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1dc6ec3715c0428803b53dd29e714b166eb62e69))

## [0.9.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.8.0...v0.9.0) (2024-01-26)


### Features

* add abstract adapters for MQ and KV Store ([d9e3beb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d9e3beb5fee3c1ff251adfb5b46d544b0d7e5015))
* update readme ([af6cd13](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/af6cd136e2d6745d298bd99038609607cff0d058))


### Bug Fixes

* add licenses ([452c192](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/452c1920de4b3fb9202d936c17e7f68600cbf6f0))
* pass image tag as an argument during build ([9e07a2f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/9e07a2f71d1eec6c2b7e9724ced1e1508863b8fe))
* split the nats adapter into MQ and KV store ([06b84ad](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/06b84ad1517f98ea805d0fd258d59be49162e540))
* use lazy logging instead of f-string ([8e356e0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8e356e03fb25798d4adf389be26b77168e6e6ed8))
* use lower() method for checking tls mode, use longer name for the variable ([971f7ca](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/971f7cad5db0c094745f7e326efb45fe52723c37))
* use TLS_MODE instead of ldap_start_tls ([f25fdd8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f25fdd8cbe37e6e2ee981628e446aacdd3abd966))

## [0.8.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.7.1...v0.8.0) (2024-01-23)


### Features

* **helm:** Lower the initial delay for the propers in udm-listener ([b137844](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b1378444ad144f566ecf56426abb1bd4abd4c9df))
* **helm:** Reduce initial delay of probes in dispatcher chart ([ef605f7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/ef605f73ba0d72ee898735adb9e1b6547d5fe856))
* **helm:** Remove "config.environment" from udm-listener ([4967e19](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/4967e19c0e7f364e9f7de71e85b918f8d5951a6b))
* **helm:** Remove repositories of embedded charts ([7b1bd67](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7b1bd67aaf007fd05b4869586d3bdf0ed1e05b26))
* **helm:** Update common-helm to 0.6.0 ([7b1f465](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/7b1f465f149c3671a25e6367ba780eebc2e660df))


### Bug Fixes

* **helm:** Avoid setting resources as default in dispatcher ([995e384](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/995e384e7b8755948a6e1b67b37715ba3fe20dd5))
* **helm:** Avoid setting resources in the default values of udm-listener ([e76c2d7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e76c2d7f0fcc5d25629f0226f77d09f9f7620acc))
* **helm:** Drop appVersion ([0e967e0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0e967e0b0297e4c0545e4a982f3e15a60061819b))
* **helm:** Remove appVersion in the dispatcher chart ([f0a3aa8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f0a3aa8f6421e93f48a2a4d461ba647df0e5e8fa))
* **helm:** Remove invalid default value of "config.caCert" ([c6bae19](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c6bae1931aa73c857ce9f106ab44f95bf8f7bd23))

## [0.7.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.7.0...v0.7.1) (2024-01-19)


### Bug Fixes

* remove fullnameOverrides to get provisioning- prefix ([5d665df](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/5d665dfd567485e87fdf12f8321c61144773dbe6))

## [0.7.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.6.0...v0.7.0) (2024-01-18)


### Features

* **ci:** add debian update check jobs for scheduled pipeline ([1fd8495](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1fd84955d00f8817090dafadb1c6f875c4148d0a))
* **ci:** add debian update check jobs for scheduled pipeline ([1d87650](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/1d87650e9fbde98c3927a43493a6f0296dc8e731))

## [0.6.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/compare/v0.5.2...v0.6.0) (2024-01-17)


### Features

* add adapter for Consumer Registration API, send event to incoming queue due to blocked consumer queue ([a84f17f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/a84f17f13a87d4a3156bc2703b72144798b57e99))
* add field 'receivers' to the Message, use Field for description ([82a78cb](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/82a78cb46309c3a3a160ab1aac1db825c0c65963))
* wait for pre-fill to finish during getting messages ([18a094a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/18a094a655b1fdc04639d6105f9c28d80a6bd12c))


### Bug Fixes

* add licenses ([8df66a3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/8df66a391e48f0624456b133d0f60b5c98d7fcff))
* fix typo in the settings variables ([0e4a993](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0e4a99366312c7afd10e374511cf4dfcbec26ace))
* get realm_topic subs using Consumer REST API, remove trailing forward-slash from endpoints ([6362ee7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/6362ee70fbcf9f62f5f2d0f522bbbfe8f01a6451))
* pin versions in apt get install, set the SHELL option -o pipefail ([29a139c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/29a139cc6d2ddae355a44b50f23e8d772079bc15))
* remove context manager from EventAdapter ([c850699](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c8506998993a489f6a6aa0352762be5697350b08))
* rename connection settings after their purpose ([c9857ce](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/c9857ce131a1bf2ca6db89442bb158c15660f138))
* rename docker stages, remove unused workdir argument ([d1758aa](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/d1758aa375b1b6d116828802fedbcec9c51cafb4))
* replace flatten and inflate methods ([bd4b990](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/bd4b990b76a40f829cd1473d9fba0ac9f79c3d20))
* return back WORKDIR argument ([6984407](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/69844070d1960e17e5d4e21547aad12effc1be9a))
* return calling prefill, fix connection to the UDM REST, refactor settings ([539bd81](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/539bd81d50f098c552a46c18fe6b700116f4a46f))
* update project name ([f3b8848](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/f3b8848ad508ea66372155ef6843806fb76aacf6))
* use listener-base image to install dependencies ([0c9fad3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/0c9fad3b95b54ee9a3a8d7019bae854fc7abfb73))
* use pluralization for endpoints ([e92f9c5](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/e92f9c51e803b94980cf983d3b515699d51c6d22))
* use univention module from udm-rest-image ([b143271](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning/commit/b1432713b11fd58f7a1706111c605e43227f3d94))

## [0.5.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.5.1...v0.5.2) (2024-01-04)


### Bug Fixes

* **ci:** add license header checking with common-ci v1.14.x and pre-commit-hook ([f7602e7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/f7602e7e0f16d38a821da1cf08b57bcec288c7bc))
* **licensing:** add spdx license headers to all files ([5fc8106](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/5fc810654f20e48386ca68dadf9c4be8526bb1c2))

## [0.5.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.5.0...v0.5.1) (2024-01-04)


### Bug Fixes

* **deps:** add renovate.json ([ac93093](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/ac93093cb3af578942d63cfc50ad3f9173c9ec7a))
* disable publish-helm-charts-souvap ([fbc2701](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/fbc27011b48b6a6249daae3b8b3a8e424f0dfb3c))

## [0.5.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.4.0...v0.5.0) (2023-12-29)


### Features

* add E2E test ([cc2d0a7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/cc2d0a7706d2c407d9dd272de9b691e5bf0a7745))
* add ldap notifier image ([22d7403](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/22d740360c630e77943ada927720a3018a81642a))
* add openldap container ([d7de0a2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d7de0a2159348592874a8b911fbfa800417e1e86))
* add udm-listener, ldap-server and ldap-admin to the docker-compose ([12c7bc4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/12c7bc46dfa03e5fe80d5dd46cf85e9c03105c83))
* add udm-rest-api container and fix converting ldap to udm ([dd542b2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/dd542b2b07ede30c21989fb43507a1efef2be6e7))
* convert LDAP obj to UDM obj and resolve references ([438bb5f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/438bb5fe3a1b8df02efb99912041dfe0ab8d1f08))
* make ldap methods initial realization ([d4f667d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d4f667de6d77d38e178fefb08a105bc609b6fc9a))


### Bug Fixes

* add annotation and make Python version an argument ([047a1e1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/047a1e1aca5462e9989512d8ad6ee89647cf7999))
* add logger into classes, clear commented lines ([16befc6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/16befc6a82256a7473d36aaa7e884b4bb20ad4ae))
* add missed rest and management modules to the listener container ([6eea289](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/6eea2895380d68cd29ac7ce20fb27ff048806d8a))
* connection to EventAdapter, validation model for send_event ([a55ee2e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/a55ee2e27343334bbd135d8d6862dbb962d20d41))
* do not pass class as the first argument ([a5c1bea](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/a5c1bea29fad182dcec598cfc5f0b02805d163a8))
* fix connecting to the nats and displaying the logs int the dispatcher ([03e963d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/03e963d0864ba0d7cbf2a1904e34a6a07578783a))
* fix inflate method and e2e test ([30c99b8](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/30c99b84f7c7e9422ae0e021508b7402d07b6f73))
* fix modify and delete methods, retrieving data from cache and refactor handling changes ([c1edcd1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/c1edcd1ff2c8ad9be862832a0526ca5d589c1485))
* move ldap connection settings to the config file ([3395470](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/3395470414b46d39ef21f9e2fcbe784c5e1f4c0c))
* provisioning-dispatcher-dev container ([8a9250d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/8a9250db778302a792a74841ad4a78ea546c2839))
* remove commented code and WORKDIR argument, rename python image version argument ([422d0b0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/422d0b0fa2ba925b3fd7674a097b2051850f0b69))
* remove the _event_adapter variable from the UDMMessagingPort class ([bb6cb15](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/bb6cb15f6d2a07c29c3852345d5ade4c0c7c6856))
* rollback fixing dockerfile path ([114a70f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/114a70fdce778776dfeb47b9c0df70526cc370b9))
* set WORKDIR, tag the version of an image explicitly, fix line too log error ([36bbd87](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/36bbd879e4f9e23aee5ce6ef567df5f01b3f074c))
* specify poetry version to install ([f410876](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/f410876e6089234e65e33d22fd26863cec1c8135))
* use existing image for notifier and fix installing libs for listener ([2a316f9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/2a316f95a412a4d36b1a82f56bbe8db264f3aa19))

## [0.4.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.3.1...v0.4.0) (2023-12-22)


### Features

* **helm:** Add dispatcher and udm-listener ([56de228](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/56de228149326512dee3eb5f457d41b343381952))


### Bug Fixes

* **helm:** remove autoscaling ([e7c4f2c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e7c4f2c2f777c579ea4932b204c43912908c7b0b))

## [0.3.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.3.0...v0.3.1) (2023-12-20)


### Bug Fixes

* **docker:** update ucs-base 5.2-0 from v0.7.2 ro v0.10.0 ([79ca4b9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/79ca4b922f63aa09a388df37ac50d2fe4b19345e))

## [0.3.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.2.1...v0.3.0) (2023-12-19)


### Features

* **docker:** update dispatcher to UCS base and build it in CI ([147cf9c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/147cf9c666c688000efd950d88bc6df8b707760d))

## [0.2.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.2.0...v0.2.1) (2023-12-18)


### Bug Fixes

* **ci:** add Helm chart signing and publishing to souvap via OCI, common-ci 1.12.x ([e7fcd74](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e7fcd7499327367d7057647525066235fa05fb92))

## [0.2.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.1.4...v0.2.0) (2023-12-14)


### Features

* create Dockerfile for dispatcher ([92ba35f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/92ba35fc3ce17bed55ec864721b17bf4c0117540))
* implement dispatcher ([3c6b22c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/3c6b22ceb92bce0d424a3aa7efb14b62d1afaf36))


### Bug Fixes

* call dispatcher service as daemon ([3dd4125](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/3dd41250fc32d7486a803c4bd14252e33da2fae1))
* use asyncio.Queue instead of Future and add integration test for dispatcher ([976e81b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/976e81b86c216407de54111cd12470c1b7969f90))

## [0.1.4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.1.3...v0.1.4) (2023-12-13)


### Bug Fixes

* **helm:** use full image registry spec ([a8fafb1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/a8fafb1859fc3e1b033322f17726123a7e6572e8))

## [0.1.3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.1.2...v0.1.3) (2023-12-11)


### Bug Fixes

* fix deleting subscriber, getting subscribers and adding value to nats ([ce55584](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/ce555840770861b1376909a9da3f94eea3bb1f7a))
* remove unused print ([e0e27d7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e0e27d7307a1fc0e1d5ac7497413161598b24ee5))

## [0.1.2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.1.1...v0.1.2) (2023-12-09)


### Bug Fixes

* **ci:** reference common-ci v1.11.x to push sbom and signature to souvap ([86e1bbc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/86e1bbc35af459e46548cee84be33cb55631bd20))

## [0.1.1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.1.0...v0.1.1) (2023-12-08)


### Bug Fixes

* **ci:** add nats helm repo ([d1eb805](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d1eb80574a5bb8f020bb00c474f7de96fee8bdf3))
* **helm:** replace redis with nats ([fc2bc4e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/fc2bc4e426dbb0b4674f7cd76ef86247058e9825))
* **helm:** switch to helm chart from nats instead of bitnami ([c55579e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/c55579e1ee5efb134980a28b652a285fbae9d3c2))

## [0.1.0](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/compare/v0.0.1...v0.1.0) (2023-12-04)


### Features

* **docker-compose:** provide udm-listener service ([17c24a2](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/17c24a2f62fdb9bb64a51541d5dfedc214c1a2d8))
* **docker:** add udm-listener image build to CI ([9e6253c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/9e6253c6b70704a3e9559e0f77cb716ea19b4fa9))
* **docker:** provide Dockerfile for udm-listener ([403dee9](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/403dee985242b59749aa83935d96a5ae86b3894e))
* **listener:** add listener implementation ([d799a9b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d799a9b9d8e328335c0b6a7f35aaff04555ce174))
* **listener:** add listener implementation ([e88971f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e88971f16158f38d9c8a74541de50c3faee9c208))

## 0.0.1 (2023-11-29)


### Features

* add consumer rest api stub ([fe4c039](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/fe4c039061b3330f61e0dcb781b0a73d8a873225))
* add helm ([8a6950f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/8a6950f8c36318261d81b0dc3a986ee741ba3748))
* add LDAP listener ([eb7afce](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/eb7afce12409342584e1119883379dadbc8402df))
* add MessageRepository logic to port and adapter ([382224d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/382224dca7d40146029841daacc29f4eb172fa74))
* add nats adapter ([0316a6b](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/0316a6ba3158f54500646323715089a1fb0cf7b6))
* Add nats adapter. Add methods to delete message and get next message from nats. Fix tests for consumer and dispatcher api, fix methods to delete messages and stream. Add api for deleting message, add dataclass for messages from Nats ([19ecb8d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/19ecb8d16ac0d673a80d65e08b73f24606fc6156))
* add queue pre-filling ([e85dc38](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e85dc3818ef01d5b028322db8b6bfa9bdcdd0473))
* add settings for Notification REST API ([bb38f2a](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/bb38f2a7249b83716901ba2c81509b9df194516f))
* add tests for get_subscribers (not finished) ([03b948d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/03b948d910ba9b331aadb7b8fb2bba66bbaece97))
* create a subscription to 1 topic at a time ([c22963c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/c22963c8ea8210cc2825331a3541c848f640d55c))
* fix redis_adapter to make tests run ([ba21c58](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/ba21c581248cb2cb8f126ad237da7fd67c26ee27))
* fix tests, add a separate test clients for dispatcher_app and consumer_app ([e69ee0d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e69ee0d8b2efc13502d007e9b122ce136580e6d2))
* **helm:** adjust default Redis configuration; disabling replicas ([43cbb3d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/43cbb3dfb8d43977b213e920fd7278b710fb3d56))
* implement udm messaging, port and adapters for this service ([08136ce](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/08136ce8ff7cbf475efc69335fb519a3648ce8d9))
* improve output clarity in example client ([d97f4ae](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d97f4ae8280d50c4a1c0b17d176ee4903e9d6327))
* initialize classes for Port and Redis Adapter ([75b611e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/75b611eb208a837658121bc5b4117b9823c9a911))
* move adapters to the shared folder ([94ebee4](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/94ebee4e6746c00de6a574f76fa906f5b6d01dfa))
* replace redis with nats for the rest methods ([007b836](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/007b83623bc09122d54ef9d56080726f1ce11b3a))
* spin off events api ([b966d22](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/b966d2279c7a0a198a5fdf67233e17753f39e2e7))
* use methods to delete message and get next message from nats ([e108133](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e1081330adb4c3826a50b2d32e4377d7e5e9b552))
* use Nats key/value store for old objs and refactor nats adapter ([87f5151](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/87f5151a26f0a625bf005e5f87c79e145d035ca7))
* use nats key/value store to create and get subscriptions ([3250d27](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/3250d27d9094c72e97ea178aa189cce746ac1a4c))
* use port for SubscriptionRepository ([21eeac6](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/21eeac64f36d44e1e53ad14d68f9f9fe8a27ed61))


### Bug Fixes

* add api for deleting message, add dataclass for messages from Nats, fix tests ([2297c1d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/2297c1df074d18d343085c664607cd011e97e3e2))
* add checking for an existing subscription ([9984dee](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/9984dee31fc7d520acd6fd40880f2664c0f434cc))
* add dependency override for EventsPort ([bf38e64](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/bf38e6404d57cc0745c1947dd5d40a50014e71ee))
* add nats dependency ([4e514bc](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/4e514bcf4ddce17ba099c5b08de4d07111cce65c))
* add prefix per router ([f157737](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/f157737cfd9a3fe41b66edefe96ad7885a2cb701))
* add settings to config map ([da98c6f](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/da98c6fa1a432dd368274c1f0956f9846b166939))
* change dosctrings ([c228f7e](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/c228f7e2991942de7e1327f68237cc7964d5e97d))
* change package path in poetry ([447aa5d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/447aa5d328eef464ff78f88edba4ddfffed64a4b))
* change port context and dependency ([66dcc6d](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/66dcc6de1df17cc6391c7508fcb654a18c1e906e))
* **ci:** fix package-helmchart (use common-ci v1.9.8) ([d92d8a7](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d92d8a7cba3c612364dec847d163bd6782873847))
* **dispatcher:** pre-fill does not fail when no subscribed objects are found in LDAP ([563ab27](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/563ab27327d0054f10833123c6386a89d6e0aa84))
* **docker:** fix Docker image build ([6965627](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/69656270ee212ee881fb94b0c195ce3797648be3))
* **docker:** make image run ([ad1efac](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/ad1eface025a7f45c1801c750c2761b06ed70db7))
* fix delete method and tests ([07e9246](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/07e9246423759588d917792decac3f52463af345))
* fix method to cancel subscription ([93324de](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/93324de46613bc763ab4d637a3fa89633109099b))
* fix methods to delete messages and stream ([bb0a149](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/bb0a149af22f3dd0c4ff1a0d259b8ad4823cf8a9))
* fix mocks in tests and add trio dependency ([befb7dd](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/befb7dda71d9f52ed365d7aa4bea9670769f418d))
* fix pytest warnings ([6ddaaee](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/6ddaaee966045d1fdb49040b447ba3c429360496))
* helm chart publishing - add version pinning ([11f4d56](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/11f4d56d8ea0b1ee2663635fcc9da0e661be1834))
* **helm:** make UDM connection parameters mandatory ([63e4b45](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/63e4b453464b85b8ba02dbd7cc821a5ef622b2a9))
* import after refactoring ([f0bdac3](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/f0bdac3487ab37aafdc072c3806365fed14f9ee2))
* install required `websockets` dependency ([b3db112](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/b3db1125c609a9c4fcdf8b8e6fa4ef0f101bfaf1))
* make linter happy ([d20f534](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/d20f534ca9cab611f33f259e04e8ae045448f981))
* Remove unused import. **Tests are not working in this branch, WIP** ([cafa176](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/cafa17698234bc8d8d96950187e234ce77e74ea7))
* uncomment docker-compose profile flag ([5308bc1](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/5308bc13c5bb2a6b65146d309d4bb4ae8094c517))
* use port as private attribute ([54bf38c](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/54bf38cc3aa183fc09e23a490cfe958849267016))
* use PortDependency instead of Message and Subscription and fix tests ([e5e9906](https://git.knut.univention.de/univention/customers/dataport/upx/provisioning-api/commit/e5e9906307d2df39b0fad70ddc2e959d6a693d84))
