package client

import "time"

// MessageStatus represents the processing status for a message.
type MessageStatus string

const (
	Ok MessageStatus = "ok"
)

// PrefillStatus represents the prefill queue status for a subscription.
type PrefillStatus string

const (
	Pending PrefillStatus = "pending"
	Running PrefillStatus = "running"
	Failed  PrefillStatus = "failed"
	Done    PrefillStatus = "done"
)

// RealmTopic pairs a realm with a topic (e.g. realm "udm", topic "users/user").
type RealmTopic struct {
	Realm string `json:"realm"`
	Topic string `json:"topic"`
}

// NewSubscription is sent to create a subscription.
type NewSubscription struct {
	Name           string       `json:"name"`
	RealmsTopics   []RealmTopic `json:"realms_topics"`
	RequestPrefill bool         `json:"request_prefill"`
	Password       string       `json:"password"`
}

// Subscription represents a registered subscription.
type Subscription struct {
	Name               string        `json:"name"`
	RealmsTopics       []RealmTopic  `json:"realms_topics"`
	RequestPrefill     bool          `json:"request_prefill"`
	PrefillQueueStatus PrefillStatus `json:"prefill_queue_status"`
}

// Body is the message payload content.
type Body struct {
	Old map[string]any `json:"old"`
	New map[string]any `json:"new"`
}

// Message is the event posted via the events endpoint.
type Message struct {
	PublisherName string    `json:"publisher_name"`
	Ts            time.Time `json:"ts"`
	Realm         string    `json:"realm"`
	Topic         string    `json:"topic"`
	Body          Body      `json:"body"`
}

// ProvisioningMessage is the message returned to subscribers with metadata.
type ProvisioningMessage struct {
	PublisherName string    `json:"publisher_name"`
	Ts            time.Time `json:"ts"`
	Realm         string    `json:"realm"`
	Topic         string    `json:"topic"`
	Body          Body      `json:"body"`

	SequenceNumber int64 `json:"sequence_number"`
	NumDelivered   int   `json:"num_delivered"`
}

// MessageStatusReport is used to ack a message.
type MessageStatusReport struct {
	Status MessageStatus `json:"status"`
}
