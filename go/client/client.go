package client

import (
	"bytes"
	"context"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

func basicAuth(username, password string) string {
	return "Basic " + base64.StdEncoding.EncodeToString([]byte(username+":"+password))
}

// Client is a minimal HTTP client for the Provisioning API.
type Client struct {
	url        *url.URL
	name       string
	authHeader string
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
	u, err := url.Parse(strings.TrimRight(baseURL, "/"))
	if err != nil {
		panic(err)
	}
	return &Client{
		url:        u,
		name:       username,
		authHeader: basicAuth(username, password),
		httpClient: httpClient,
	}
}

func (c *Client) doBody(ctx context.Context, req *http.Request) (*http.Response, error) {
	req = req.WithContext(ctx)
	req.Header.Set("Accept", "application/json")
	if req.Method == http.MethodPost || req.Method == http.MethodPatch {
		req.Header.Set("Content-Type", "application/json")
	}
	req.Header.Set("Authorization", c.authHeader)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	if resp.StatusCode >= 400 {
		defer resp.Body.Close()
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 8<<10))
		return nil, fmt.Errorf("http %s %s: %d: %s", req.Method, req.URL.Path, resp.StatusCode, string(b))
	}
	return resp, nil
}

func (c *Client) do(ctx context.Context, req *http.Request) error {
	resp, err := c.doBody(ctx, req)
	if err != nil {
		return err
	}
	resp.Body.Close()
	return nil
}

func decodeJSON[T any](resp *http.Response) (*T, error) {
	defer resp.Body.Close()
	var result *T
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		if err == io.EOF {
			return nil, nil
		}
		return nil, err
	}
	return result, nil
}

// Fork creates a new Client that shares the same underlying HTTP transport
// but uses different BasicAuth credentials. Useful for creating per-role or
// per-subscription clients while preserving connection pooling.
func (c *Client) Fork(username, password string) *Client {
	return &Client{
		url:        c.url,
		name:       username,
		authHeader: basicAuth(username, password),
		httpClient: c.httpClient,
	}
}

// CreateSubscription registers a new subscription.
func (c *Client) CreateSubscription(ctx context.Context, sub NewSubscription) error {
	body, err := json.Marshal(sub)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.url.JoinPath("/v1/subscriptions").String(), bytes.NewReader(body))
	if err != nil {
		return err
	}
	return c.do(ctx, req)
}

// DeleteSubscription deletes a subscription.
func (c *Client) DeleteSubscription(ctx context.Context, name string) error {
	req, err := http.NewRequest(http.MethodDelete, c.url.JoinPath("/v1/subscriptions", name).String(), nil)
	if err != nil {
		return err
	}
	return c.do(ctx, req)
}

// GetSubscription retrieves subscription information.
func (c *Client) GetSubscription(ctx context.Context, name string) (*Subscription, error) {
	req, err := http.NewRequest(http.MethodGet, c.url.JoinPath("/v1/subscriptions", name).String(), nil)
	if err != nil {
		return nil, err
	}
	resp, err := c.doBody(ctx, req)
	if err != nil {
		return nil, err
	}
	return decodeJSON[Subscription](resp)
}

func (c *Client) nextUrl(timeout time.Duration, pop bool) string {
	u := c.url.JoinPath("/v1/subscriptions", c.name, "messages", "next")
	u.RawQuery = url.Values{
		"timeout": []string{strconv.Itoa(int(timeout.Seconds()))},
		"pop":     []string{strconv.FormatBool(pop)},
	}.Encode()
	return u.String()
}

func (c *Client) Next(ctx context.Context, timeout time.Duration) (*ProvisioningMessage, func() error, error) {
	req, err := http.NewRequest(http.MethodGet, c.nextUrl(timeout, false), nil)
	if err != nil {
		return nil, nil, err
	}
	resp, err := c.doBody(ctx, req)
	if err != nil {
		return nil, nil, err
	}
	msg, err := decodeJSON[ProvisioningMessage](resp)
	if err != nil {
		return nil, nil, err
	}
	if msg == nil {
		return nil, nil, nil
	}

	ack := func() error {
		return c.MessageStatus(ctx, c.name, msg.SequenceNumber, Ok)
	}

	return msg, ack, nil
}

// MessageStatus updates the message processing status (subscriber auth).
func (c *Client) MessageStatus(ctx context.Context, name string, seq int64, status MessageStatus) error {
	report := MessageStatusReport{Status: status}
	body, err := json.Marshal(report)
	if err != nil {
		return err
	}
	url := c.url.JoinPath("/v1/subscriptions", name, "messages", strconv.FormatInt(seq, 10), "status").String()
	req, err := http.NewRequest(http.MethodPatch, url, bytes.NewReader(body))
	if err != nil {
		return err
	}
	return c.do(ctx, req)
}

// PublishMessage posts a new message to the incoming queue (events auth).
func (c *Client) PublishMessage(ctx context.Context, msg Message) error {
	body, err := json.Marshal(msg)
	if err != nil {
		return err
	}
	req, err := http.NewRequest(http.MethodPost, c.url.JoinPath("/v1/messages").String(), bytes.NewReader(body))
	if err != nil {
		return err
	}
	return c.do(ctx, req)
}
