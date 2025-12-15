package client

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"
)

// Client is a minimal HTTP client for the Provisioning API.
type Client struct {
	baseURL    string
	username   string
	password   string
	httpClient *http.Client
}

// New creates a new client. If httpClient is nil, a tuned default is used.
func New(baseURL, username, password string, httpClient *http.Client) *Client {
	if httpClient == nil {
		tr := &http.Transport{
			Proxy: http.ProxyFromEnvironment,
			// Tune connection reuse for high-concurrency tests.
			MaxIdleConns:        100,
			MaxIdleConnsPerHost: 100,
			MaxConnsPerHost:     0, // unlimited
			IdleConnTimeout:     90 * time.Second,
		}
		httpClient = &http.Client{Transport: tr}
	}
	return &Client{baseURL: trimTrailingSlash(baseURL), username: username, password: password, httpClient: httpClient}
}

func trimTrailingSlash(s string) string {
	for len(s) > 0 && s[len(s)-1] == '/' {
		s = s[:len(s)-1]
	}
	return s
}

func (c *Client) url(path string) string { return c.baseURL + path }

func (c *Client) doJSON(ctx context.Context, req *http.Request, v any) error {
	req = req.WithContext(ctx)
	req.Header.Set("Accept", "application/json")
	if req.Method == http.MethodPost || req.Method == http.MethodPatch {
		req.Header.Set("Content-Type", "application/json")
	}
	// Apply BasicAuth for this client instance
	req.SetBasicAuth(c.username, c.password)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 400 {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 8<<10))
		return fmt.Errorf("http %s %s: %d: %s", req.Method, req.URL.Path, resp.StatusCode, string(b))
	}
	if v == nil {
		// caller doesn't want a body
		io.Copy(io.Discard, resp.Body)
		return nil
	}
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return err
	}
	// empty body or explicit null indicates no content
	trimmed := bytes.TrimSpace(data)
	if len(trimmed) == 0 || bytes.Equal(trimmed, []byte("null")) {
		return nil
	}
	return json.Unmarshal(trimmed, v)
}

// Fork creates a new Client that shares the same underlying HTTP transport
// but uses different BasicAuth credentials. Useful for creating per-role or
// per-subscription clients while preserving connection pooling.
func (c *Client) Fork(username, password string) *Client {
	return &Client{
		baseURL:    c.baseURL,
		httpClient: c.httpClient,
		username:   username,
		password:   password,
	}
}

// CreateSubscription registers a new subscription.
func (c *Client) CreateSubscription(ctx context.Context, sub NewSubscription) error {
	body, err := json.Marshal(sub)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.url("/v1/subscriptions"), bytes.NewReader(body))
	if err != nil {
		return err
	}
	// 201 created or 200 ok (already exists) are both fine
	err = c.doJSON(ctx, req, nil)
	var httpErr *url.Error
	if err != nil && !errors.As(err, &httpErr) {
		// For idempotency: accept HTTP 200 as non-error, but doJSON
		// already returns nil on non-4xx/5xx. Just return err.
		return err
	}
	return err
}

// DeleteSubscription deletes a subscription.
func (c *Client) DeleteSubscription(ctx context.Context, name string) error {
	req, err := http.NewRequest(http.MethodDelete, c.url("/v1/subscriptions/"+url.PathEscape(name)), nil)
	if err != nil {
		return err
	}
	return c.doJSON(ctx, req, nil)
}

// GetSubscription retrieves subscription information.
func (c *Client) GetSubscription(ctx context.Context, name string) (*Subscription, error) {
	req, err := http.NewRequest(http.MethodGet, c.url("/v1/subscriptions/"+url.PathEscape(name)), nil)
	if err != nil {
		return nil, err
	}
	var sub Subscription
	if err := c.doJSON(ctx, req, &sub); err != nil {
		return nil, err
	}
	return &sub, nil
}

// GetNextMessage returns the next message or nil if none available.
// timeout controls server long-polling (nil to omit). pop is optional (nil to omit).
func (c *Client) GetNextMessage(ctx context.Context, name string, timeout *time.Duration, pop *bool) (*ProvisioningMessage, error) {
	q := url.Values{}
	if timeout != nil {
		// API expects seconds (float). Use milliseconds precision.
		q.Set("timeout", fmt.Sprintf("%.3f", timeout.Seconds()))
	}
	if pop != nil {
		if *pop {
			q.Set("pop", "true")
		} else {
			q.Set("pop", "false")
		}
	}
	path := fmt.Sprintf("/v1/subscriptions/%s/messages/next", url.PathEscape(name))
	if len(q) > 0 {
		path += "?" + q.Encode()
	}
	req, err := http.NewRequest(http.MethodGet, c.url(path), nil)
	if err != nil {
		return nil, err
	}
	var msg ProvisioningMessage
	if err := c.doJSON(ctx, req, &msg); err != nil {
		return nil, err
	}
	// If no body was returned, doJSON leaves msg zero-value. Distinguish using Ts/Realm?
	// The server sends `null` for no message, handled above -> returns nil error and msg untouched.
	if msg.SequenceNumber == 0 && msg.Realm == "" && msg.Topic == "" && msg.NumDelivered == 0 && msg.Ts.IsZero() {
		return nil, nil
	}
	return &msg, nil
}

// AckMessage updates the message processing status (subscriber auth).
func (c *Client) AckMessage(ctx context.Context, name string, seq int64, status MessageStatus) error {
	report := MessageStatusReport{Status: status}
	body, err := json.Marshal(report)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPatch, c.url(fmt.Sprintf("/v1/subscriptions/%s/messages/%d/status", url.PathEscape(name), seq)), bytes.NewReader(body))
	if err != nil {
		return err
	}
	return c.doJSON(ctx, req, nil)
}

// PublishMessage posts a new message to the incoming queue (events auth).
func (c *Client) PublishMessage(ctx context.Context, msg Message) error {
	body, err := json.Marshal(msg)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.url("/v1/messages"), bytes.NewReader(body))
	if err != nil {
		return err
	}
	return c.doJSON(ctx, req, nil)
}
