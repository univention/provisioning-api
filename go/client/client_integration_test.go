package client

// These are integration / e2e tests. They expect provisioning-api running via docker-compose.

import (
	"context"
	"time"
)

func dummyRealmTopics() []RealmTopic {
	return []RealmTopic{{Realm: "udm", Topic: "tests/topic"}}
}

func (s *Integrationtest) TestCreateAndDeleteSubscription() {
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	client, cleanup := s.createTestSubscription(ctx, dummyRealmTopics(), false)
	// Ensure cleanup if the test fails before explicit delete.
	defer cleanup()

	// Verify the subscription is retrievable using subscriber credentials.
	subscription, err := client.GetSubscription(ctx, client.username)
	s.Require().NoError(err)
	s.Require().Equal(client.username, subscription.Name)

	// Explicitly delete to validate delete path.
	s.Require().NoError(s.adminClient.DeleteSubscription(ctx, client.username))
}
