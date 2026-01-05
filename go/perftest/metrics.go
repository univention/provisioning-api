package main

import (
	"fmt"
	"sort"
	"time"
)

type Insights struct {
	Count      int
	Min        time.Duration
	Avg        time.Duration
	P50        time.Duration
	P95        time.Duration
	P99        time.Duration
	Max        time.Duration
}

func CalculateStats(durations []time.Duration) Insights {
	if len(durations) == 0 {
		return Insights{}
	}

	sorted := make([]time.Duration, len(durations))
	copy(sorted, durations)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i] < sorted[j]
	})

	var sum time.Duration
	for _, d := range sorted {
		sum += d
	}

	return Insights{
		Count: len(sorted),
		Min:   sorted[0],
		Avg:   sum / time.Duration(len(sorted)),
		P50:   percentile(sorted, 50),
		P95:   percentile(sorted, 95),
		P99:   percentile(sorted, 99),
		Max:   sorted[len(sorted)-1],
	}
}

func percentile(sorted []time.Duration, p int) time.Duration {
	if len(sorted) == 0 {
		return 0
	}
	idx := (len(sorted) * p / 100)
	if idx >= len(sorted) {
		idx = len(sorted) - 1
	}
	return sorted[idx]
}

func (s Insights) String() string {
	return fmt.Sprintf(
		"count=%d min=%v avg=%v p50=%v p95=%v p99=%v max=%v",
		s.Count,
		s.Min.Round(time.Microsecond),
		s.Avg.Round(time.Microsecond),
		s.P50.Round(time.Microsecond),
		s.P95.Round(time.Microsecond),
		s.P99.Round(time.Microsecond),
		s.Max.Round(time.Microsecond),
	)
}
