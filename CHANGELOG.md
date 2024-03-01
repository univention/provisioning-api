# Changelog

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
