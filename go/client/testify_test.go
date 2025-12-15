package client

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/hex"
	"log/slog"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
)

type Integrationtest struct {
	suite.Suite
	logBuf    bytes.Buffer

	adminClient  *Client
	eventsClient *Client
}

func (s *Integrationtest) SetupSuite() {
	// Configure base URL and credentials from env vars.
	baseURL := getenv("PROVISIONING_API_BASE_URL", "http://localhost:7777")
	adminUsername := getenv("PROVISIONING_ADMIN_USERNAME", "admin")
	adminPassword := getenv("PROVISIONING_ADMIN_PASSWORD", "provisioning")
	eventsUsername := getenv("PROVISIONING_EVENTS_USERNAME", "udm")
	eventsPassword := getenv("PROVISIONING_EVENTS_PASSWORD", "udmpass")

	// Initialize admin client and fork an events client to share transport.
	s.adminClient = New(baseURL, adminUsername, adminPassword, nil)
	s.eventsClient = s.adminClient.Fork(eventsUsername, eventsPassword)
}

func (s *Integrationtest) SetupTest() {
	s.logBuf.Reset()

	handler := slog.NewTextHandler(&s.logBuf, &slog.HandlerOptions{
		AddSource: false,
		Level:     slog.LevelDebug,
	})
	logger := slog.New(handler)
	slog.SetDefault(logger)
}

func (s *Integrationtest) TearDownTest() {
	if !s.T().Failed() || !testing.Verbose() {
		return
	}
	s.T().Log("=== Captured Production Logs ===\n")
	s.T().Log(s.logBuf.String())
}

func TestIntegrationSuite(t *testing.T) {
	suite.Run(t, new(Integrationtest))
}

// createTestSubscription creates a unique subscription and returns a client bound
// to this subscription's credentials, plus a deferrable cleanup callback that
// deletes the subscription.
// createTestSubscription returns a subscription-scoped client and a deferrable
// cleanup callback to remove the subscription.
func createTestSubscription(ctx context.Context, adminClient *Client, realmsTopics []RealmTopic, requestPrefill bool) (*Client, func()) {
    name := "it-" + randHex(8)
    password := randHex(16)

    if err := adminClient.CreateSubscription(ctx, NewSubscription{
        Name:           name,
        Password:       password,
        RealmsTopics:   realmsTopics,
        RequestPrefill: requestPrefill,
    }); err != nil {
        // The caller uses testify; we keep helpers generic and return errors via cleanup when possible.
        // Here we choose to panic to fail fast during setup, which matches test expectations.
        panic(err)
    }

    cleanup := func() {
        ctx2, cancel := context.WithTimeout(context.Background(), 10*time.Second)
        defer cancel()
        _ = adminClient.DeleteSubscription(ctx2, name)
    }
    return adminClient.Fork(name, password), cleanup
}

func randHex(n int) string {
	b := make([]byte, n)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}

func getenv(key, defaultValue string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return defaultValue
}
