package e2etest

import (
	"bytes"
	"context"
	"fmt"
	"log/slog"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
	"github.com/univention/provisioning-api/go/client"
)

type E2ETestSuite struct {
	suite.Suite
	logBuf bytes.Buffer

	adminClient  *client.Client
	eventsClient *client.Client
}

func (s *E2ETestSuite) SetupSuite() {
	s.adminClient, s.eventsClient = NewTestClients()
}

func (s *E2ETestSuite) SetupTest() {
	s.logBuf.Reset()

	handler := slog.NewTextHandler(&s.logBuf, &slog.HandlerOptions{
		AddSource: false,
		Level:     slog.LevelDebug,
	})
	logger := slog.New(handler)
	slog.SetDefault(logger)
}

func (s *E2ETestSuite) TearDownTest() {
	if !s.T().Failed() || !testing.Verbose() {
		return
	}
	s.T().Log("=== Captured Production Logs ===\n")
	s.T().Log(s.logBuf.String())
}

func TestE2ESuite(t *testing.T) {
	suite.Run(t, new(E2ETestSuite))
}

func (s *E2ETestSuite) TestCreateAndDeleteSubscription() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	subscriptionName, client, _ := CreateTestSubscription(ctx, s.adminClient, DummyRealmTopics, false)

	subscription, err := client.GetSubscription(ctx, subscriptionName)
	s.Require().NoError(err)
	s.Require().Equal(subscriptionName, subscription.Name)

	s.Require().NoError(s.adminClient.DeleteSubscription(ctx, subscriptionName))
}

func (s *E2ETestSuite) TestPublishAndReceiveOneMessage() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, client, cleanup := CreateTestSubscription(ctx, s.adminClient, DummyRealmTopics, false)
	defer cleanup()
	// Give the dispatcher time to update its subscriptions mapping
	time.Sleep(time.Second)

	s.Require().NoError(PublishN(ctx, s.eventsClient, 1))

	msgs, err := GetMessages(ctx, client, 1)
	s.Require().NoError(err)
	fmt.Printf("%#v\n", msgs)

	msg, _, err := client.Next(ctx, 100*time.Millisecond)
	s.Require().NoError(err)

	s.Require().Len(msgs, 1)
	s.Require().Contains(msgs[0].Body.New, "count")
	s.Require().EqualValues(0, msgs[0].Body.New["count"])
	// Assert that the queue is empty.
	s.Require().Nil(msg)
}

func (s *E2ETestSuite) TestPublishAndReceiveFiveMessages() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	_, client, cleanup := CreateTestSubscription(ctx, s.adminClient, DummyRealmTopics, false)
	defer cleanup()
	// Give the dispatcher time to update its subscriptions mapping
	time.Sleep(time.Second)

	s.Require().NoError(PublishN(ctx, s.eventsClient, 5))

	msgs, err := GetMessages(ctx, client, 5)
	s.Require().NoError(err)
	fmt.Printf("%#v\n", msgs)

	for i, m := range msgs {
		s.Require().Contains(m.Body.New, "count")
		s.Require().EqualValues(i, m.Body.New["count"])
	}
}
