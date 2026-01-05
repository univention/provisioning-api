package main

import (
	"context"
	"fmt"
	"log/slog"
	"time"

	"github.com/univention/provisioning-api/go/client"
)

// Track consecutive nil messages for idle timeout
type idleTracker struct {
	maxConsecutiveNils int
	consecutiveNils    int
	idleStart          time.Time
}

func newIdleTracker(idleTimeout, pollInterval time.Duration) *idleTracker {
	return &idleTracker{
		maxConsecutiveNils: int((idleTimeout + pollInterval - 1) / pollInterval),
	}
}

func (t *idleTracker) recordNil(received, expected int) error {
	if t.consecutiveNils == 0 {
		t.idleStart = time.Now()
	}
	t.consecutiveNils++

	if t.consecutiveNils >= t.maxConsecutiveNils {
		idleDuration := time.Since(t.idleStart)
		slog.Warn("Stopping after consecutive nil responses",
			"consecutive_nils", t.consecutiveNils,
			"idle_duration", idleDuration,
			"received", received,
			"expected", expected)
		return fmt.Errorf("idle timeout reached after %d consecutive nils", t.consecutiveNils)
	}
	return nil
}

func (t *idleTracker) recordMessage(messageIndex int) {
	if t.consecutiveNils <= 0 {
		return
	}
	idleDuration := time.Since(t.idleStart)
	slog.Info("Received message after idle period",
		"index", messageIndex,
		"consecutive_nils", t.consecutiveNils,
		"idle_duration", idleDuration)
	t.consecutiveNils = 0
}

// getMessage retrieves the next message and records timing
func getMessage(ctx context.Context, subClient *client.Client, cfg Config, stats *PerfStats) (*client.ProvisioningMessage, func() error, error) {
	getStart := time.Now()
	msg, ack, err := subClient.Next(ctx, cfg.PollInterval)
	getDuration := time.Since(getStart)

	if err != nil {
		stats.getErrors++
		slog.Error("Failed to get message", "received", len(stats.GetLatencies), "expected", cfg.NumMessages, "error", err)
		if cfg.FailFast {
			slog.Error("Failing fast on get error")
			return nil, nil, fmt.Errorf("get message failed: %w", err)
		}
		return nil, nil, nil // continue on error if not fail-fast
	}

	if msg != nil {
		stats.GetLatencies = append(stats.GetLatencies, getDuration)
	}

	return msg, ack, nil
}

// ackMessage acknowledges a message and records timing
func ackMessage(ack func() error, cfg Config, stats *PerfStats) error {
	ackStart := time.Now()
	if err := ack(); err != nil {
		stats.ackErrors++
		slog.Error("Failed to ack message", "received", len(stats.AckLatencies), "error", err)
		if cfg.FailFast {
			slog.Error("Failing fast on ack error")
			return fmt.Errorf("ack message failed: %w", err)
		}
		return nil // continue on error if not fail-fast
	}

	ackDuration := time.Since(ackStart)
	stats.AckLatencies = append(stats.AckLatencies, ackDuration)
	return nil
}

func pullMessages(ctx context.Context, subClient *client.Client, cfg Config) PerfStats {
	slog.Info("Pulling messages", "count", cfg.NumMessages)
	stats := PerfStats{
		GetLatencies: make([]time.Duration, 0, cfg.NumMessages),
		AckLatencies: make([]time.Duration, 0, cfg.NumMessages),
	}

	idleTracker := newIdleTracker(cfg.IdleTimeout, cfg.PollInterval)

	for len(stats.GetLatencies) < cfg.NumMessages {
		msg, ack, err := getMessage(ctx, subClient, cfg, &stats)
		if err != nil {
			return stats
		}
		if msg == nil {
			if err := idleTracker.recordNil(len(stats.GetLatencies), cfg.NumMessages); err != nil {
				return stats
			}
			continue
		}

		idleTracker.recordMessage(len(stats.GetLatencies))

		if err := ackMessage(ack, cfg, &stats); err != nil {
			return stats
		}
	}

	return stats
}

