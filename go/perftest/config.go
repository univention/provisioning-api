package main

import (
	"strconv"
	"time"

	"github.com/univention/provisioning-api/go/e2etest"
)

type Config struct {
	NumMessages  int
	FailFast     bool
	PollInterval time.Duration
	IdleTimeout  time.Duration
}

func NewConfig() Config {
	numMessages, _ := strconv.Atoi(e2etest.Getenv("PERF_MESSAGES", "100"))
	failFast, _ := strconv.ParseBool(e2etest.Getenv("PERF_FAIL_FAST", "false"))
	pollIntervalMs, _ := strconv.Atoi(e2etest.Getenv("PERF_POLL_INTERVAL_MS", "1000"))
	idleTimeoutMs, _ := strconv.Atoi(e2etest.Getenv("PERF_IDLE_MS", "10000"))
	return Config{
		NumMessages:  numMessages,
		FailFast:     failFast,
		PollInterval: time.Duration(pollIntervalMs) * time.Millisecond,
		IdleTimeout:  time.Duration(idleTimeoutMs) * time.Millisecond,
	}
}
