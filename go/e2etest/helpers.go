package e2etest

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"os"
	"time"

	"github.com/univention/provisioning-api/go/client"
)

// DummyRealmTopics is a test realm/topic pair.
var DummyRealmTopics = []client.RealmTopic{{Realm: "udm", Topic: "tests/topic"}}

// DummyMessage creates a test message with a predictable count marker.
func DummyMessage(count int) client.Message {
	return client.Message{
		PublisherName: "consumer_client_test",
		Ts:            time.Now(),
		Realm:         "udm",
		Topic:         "tests/topic",
		Body: client.Body{
			Old: map[string]any{},
			New: map[string]any{"count": count, "objectType": "foo/bar"},
		},
	}
}

// PublishN publishes n dummy messages with counts 0..n-1 via the given events client.
func PublishN(ctx context.Context, events *client.Client, n int) error {
	for i := 0; i < n; i++ {
		if err := events.PublishMessage(ctx, DummyMessage(i)); err != nil {
			return err
		}
	}
	return nil
}

// GetMessages pulls up to count messages using server long-polling and acks them.
// It stops when it has collected count messages or observed 10 consecutive empty responses.
func GetMessages(ctx context.Context, c *client.Client, count int) ([]client.ProvisioningMessage, error) {
	msgs := make([]client.ProvisioningMessage, 0, count)
	empty := 0
	for len(msgs) < count && empty < 10 {
		msg, ack, err := c.Next(ctx, 100*time.Millisecond)
		if err != nil {
			return nil, err
		}
		if msg == nil {
			empty++
			continue
		}
		empty = 0
		msgs = append(msgs, *msg)

		// Ack the message
		if err := ack(); err != nil {
			return nil, err
		}
	}
	return msgs, nil
}

// CreateTestSubscription creates a unique subscription and returns a client bound
// to this subscription's credentials, plus a deferrable cleanup callback that
// deletes the subscription.
func CreateTestSubscription(ctx context.Context,
	adminClient *client.Client,
	realmsTopics []client.RealmTopic,
	requestPrefill bool,
) (string, *client.Client, func()) {

	name := "e2e-" + RandHex(8)
	password := RandHex(16)

	if err := adminClient.CreateSubscription(ctx, client.NewSubscription{
		Name:           name,
		Password:       password,
		RealmsTopics:   realmsTopics,
		RequestPrefill: requestPrefill,
	}); err != nil {
		panic(err)
	}

	cleanup := func() {
		ctx2, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = adminClient.DeleteSubscription(ctx2, name)
	}
	return name, adminClient.Fork(name, password), cleanup
}

// RandHex generates a random hex string of n bytes.
func RandHex(n int) string {
	b := make([]byte, n)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

// Getenv returns the value of an environment variable or a default value.
func Getenv(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}

// NewTestClients creates admin and events clients from environment variables.
func NewTestClients() (*client.Client, *client.Client) {
	baseURL := Getenv("PROVISIONING_API_BASE_URL", "http://localhost:7777")
	adminUsername := Getenv("PROVISIONING_ADMIN_USERNAME", "admin")
	adminPassword := Getenv("PROVISIONING_ADMIN_PASSWORD", "provisioning")
	eventsUsername := Getenv("PROVISIONING_EVENTS_USERNAME", "udm")
	eventsPassword := Getenv("PROVISIONING_EVENTS_PASSWORD", "udmpass")

	adminClient := client.New(baseURL, adminUsername, adminPassword, nil)
	eventsClient := adminClient.Fork(eventsUsername, eventsPassword)

	return adminClient, eventsClient
}
