# Changelog

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
