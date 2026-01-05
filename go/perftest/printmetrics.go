package main

import (
	"fmt"
	"time"
)

type PerfStats struct {
	GetLatencies []time.Duration
	AckLatencies []time.Duration
	getErrors    int
	ackErrors    int
}

func (s *PerfStats) Eval(numMessages int) error {
	// Calculate stats
	getInsights := CalculateStats(s.GetLatencies)
	ackInsights := CalculateStats(s.AckLatencies)

	// Display results
	fmt.Println("\n=== Performance Results ===")
	fmt.Printf("Get: %s\n", getInsights)
	fmt.Printf("Ack: %s\n", ackInsights)
	fmt.Printf("Errors: get=%d ack=%d\n", s.getErrors, s.ackErrors)

	if s.getErrors > 0 || s.ackErrors > 0 || len(s.GetLatencies) < numMessages {
		return fmt.Errorf("test incomplete: received %d/%d messages, errors: get=%d ack=%d", len(s.GetLatencies), numMessages, s.getErrors, s.ackErrors)
	}
	return nil
}
