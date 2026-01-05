- [x] WTF is transport and why do I need to tune it?
- [x] Why is HTTPClient exported in the Client struct? Why is BaseURL exported?

- [x] Change the method names in the client.go
  Names sholud be CreateSubscription, GetSubscription, DeleteSubscription, GetNextMessage, get next message should return a callback to ack the message.
  CreateMessage instead of PublishMessage.

- [x] Why does the client lib not implement any authentication support?

- [x] def -> default pass -> password
read the existing performance tests in e2e_tests/test_zzz... I want to implement new, similar performance
▌tests in golang that importantly pull messages in parallel from multiple subscriptions.

- [x] Exclude the go directory from addlicense in the root.

- [x] Change how timeout and stuff is passed in.

- [ ] Swap Message and ProvisioningMessage
  the outgoing message should be the main one.
- [x] what is v in doJson?

- [ ] Use the builtin fuzzing support to fuzz the subscription name and password.
- [x] explain doJson to me.

- [x] Move the env var parsing and settings into helpers for the perf tests aswell.


perf tests

- [x] For timings, is it better to have a timing struct for each message or have a timing slice for each getLatency and AckLatency?
- [x] use foreach loops whenever possible.
- [x] Cancel the context?

- [x] Collect errors, log them and continue with the perf test. Instead of exiting. Or even better, have a switch that exits or logs and tracks them.

- [x] Make ack a callback returned from Next
- [ ]

- [ ] extract the get messages into separate function. And maybe others aswell. This is getting way to long.
- [ ] Set idleStart back to it's zero value / nil and check that instead of consequtiveNils?
- [ ] the consecutiveNils calculation. does it round up or down? It should round up.
- [ ] Also get the median duration, not just the average.

