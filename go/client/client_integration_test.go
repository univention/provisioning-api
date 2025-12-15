package client

// These are integration / e2e tests. They expect provisioning-api running via docker-compose.

import (
	"context"
	"fmt"
	"time"
)

func dummyRealmTopics() []RealmTopic {
	return []RealmTopic{{Realm: "udm", Topic: "tests/topic"}}
}

func dummyMessage(count int) Message {
	return Message{
		PublisherName: "consumer_client_test",
		Ts:            time.Now(),
		Realm:         "udm",
		Topic:         "tests/topic",
		Body: Body{
			Old: map[string]any{},
			New: map[string]any{"count": count, "objectType": "foo/bar"},
		},
	}
}

// publishN publishes n dummy messages with counts 0..n-1 via the given events client.
// Using predictable counters keeps assertions and perf attribution straightforward.
func publishN(ctx context.Context, events *Client, n int) error {
	for i := 0; i < n; i++ {
		if err := events.PublishMessage(ctx, dummyMessage(i)); err != nil {
			return err
		}
	}
	return nil
}

// getMessages pulls up to count messages using server long-polling.
// It stops when it has collected count messages or observed 10 consecutive empty responses.
func getMessages(ctx context.Context, client *Client, count int) ([]ProvisioningMessage, error) {
	msgs := make([]ProvisioningMessage, 0, count)
	empty := 0
	for len(msgs) < count && empty < 10 {
		msg, err := client.GetNextMessage(ctx, 100*time.Millisecond, nil)
		if err != nil {
			return nil, err
		}
		if msg == nil {
			empty++
			continue
		}
		empty = 0
		msgs = append(msgs, *msg)
	}
	return msgs, nil
}

func (s *Integrationtest) TestCreateAndDeleteSubscription() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, _ := createTestSubscription(ctx, s.adminClient, dummyRealmTopics(), false)

	subscription, err := client.GetSubscription(ctx, client.username)
	s.Require().NoError(err)
	s.Require().Equal(client.username, subscription.Name)

	s.Require().NoError(s.adminClient.DeleteSubscription(ctx, client.username))
}

func (s *Integrationtest) TestPublishAndReceiveOneMessage() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, cleanup := createTestSubscription(ctx, s.adminClient, dummyRealmTopics(), false)
	defer cleanup()
	// Give the dispatcher time to update it's subscriptions mapping
	time.Sleep(time.Second)

    s.Require().NoError(publishN(ctx, s.eventsClient, 1))

	msgs, err := getMessages(ctx, client, 1)
	s.Require().NoError(err)
	fmt.Printf("%#v\n", msgs)

	msg, err := client.GetNextMessage(ctx, 100*time.Millisecond, nil)
	s.Require().NoError(err)

	s.Require().Len(msgs, 1)
	s.Require().Contains(msgs[0].Body.New, "count")
	s.Require().EqualValues(0, msgs[0].Body.New["count"])
	// Assert that the queue is empty.
	s.Require().Nil(msg)

}

func (s *Integrationtest) TestPublishAndReceiveFiveMessages() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, cleanup := createTestSubscription(ctx, s.adminClient, dummyRealmTopics(), false)
	defer cleanup()
	// Give the dispatcher time to update it's subscriptions mapping
	time.Sleep(time.Second)

    s.Require().NoError(publishN(ctx, s.eventsClient, 5))

	msgs, err := getMessages(ctx, client, 5)
	s.Require().NoError(err)
	fmt.Printf("%#v\n", msgs)

	for i, m := range msgs {
		s.Require().Contains(m.Body.New, "count")
		s.Require().EqualValues(i, m.Body.New["count"])
	}
}
