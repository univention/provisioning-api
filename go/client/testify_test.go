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
	oldLogger *slog.Logger

	adminClient   *Client
	baseURL       string
	adminUsername string
	adminPassword string
}

func (s *Integrationtest) SetupSuite() {
	// Configure base URL and admin credentials from env vars.
	s.baseURL = getenv("PROVISIONING_API_BASE_URL", "http://localhost:7777")
	s.adminUsername = getenv("PROVISIONING_ADMIN_USERNAME", "admin")
	s.adminPassword = getenv("PROVISIONING_ADMIN_PASSWORD", "provisioning")

	// Initialize API client.
	s.adminClient = New(s.baseURL, s.adminUsername, s.adminPassword, nil)
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
func (s *Integrationtest) createTestSubscription(ctx context.Context, realmsTopics []RealmTopic, requestPrefill bool) (*Client, func()) {
	name := "it-" + randHex(8)
	password := randHex(16)

	s.Require().NoError(s.adminClient.CreateSubscription(ctx, NewSubscription{
		Name:           name,
		Password:       password,
		RealmsTopics:   realmsTopics,
		RequestPrefill: requestPrefill,
	}))

	cleanup := func() {
		ctx2, cancel := context.WithTimeout(context.Background(), 10*time.Second)
		defer cancel()
		_ = s.adminClient.DeleteSubscription(ctx2, name)
	}
	return s.adminClient.Fork(name, password), cleanup
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
