package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/univention/provisioning-api/go/e2etest"
)

func main() {
	cfg := NewConfig()
	if err := run(cfg); err != nil {
		slog.Error("Performance test failed", "error", err)
		os.Exit(1)
	}
}

func run(cfg Config) error {
	slog.Info("Starting performance test", "config", cfg)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	adminClient, eventsClient := e2etest.NewTestClients()
	subName, subClient, cleanup := e2etest.CreateTestSubscription(ctx, adminClient, e2etest.DummyRealmTopics, false)
	defer cleanup()
	slog.Info("Created subscription", "name", subName)

	// Give the dispatcher time to update the subscriptions mapping
	time.Sleep(time.Second)

	slog.Info("Publishing messages", "count", cfg.NumMessages + 1)
	if err := e2etest.PublishN(ctx, eventsClient, cfg.NumMessages + 1); err != nil {
		return fmt.Errorf("failed to publish: %w", err)
	}

	// Warm up the API server to get better throughput
	_ = pullMessages(ctx, subClient, cfg)

	stats:= pullMessages(ctx, subClient, cfg)
	slog.Info("Completed", "messages", len(stats.GetLatencies), "get_errors", stats.getErrors, "ack_errors", stats.ackErrors)

	return stats.Eval(cfg.NumMessages)
}
