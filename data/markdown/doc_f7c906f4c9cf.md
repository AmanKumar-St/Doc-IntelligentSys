DocIntelligent Cloud API Architecture Guide

1. Authentication Protocol

All requests to the DocIntelligent API must include a Bearer Token in the HTTP Authorization header:
Authorization: Bearer doc_sec_live_xxxxxx. Tokens can be generated in the developer portal and
rotate every 90 days for production security compliance.

2. Rate Limits and Quotas

The standard tier enforces a rate limit of 120 requests per minute per IP address and 5,000 total
document queries per day. When limits are exceeded, the API returns HTTP 429 (Too Many Requests)
with a Retry-After header in seconds.

3. Webhook Delivery & Event Signatures

Async ingestion completion events are dispatched via HTTPS POST webhooks. Each payload includes
an X-DocIntelligent-Signature HMAC-SHA256 signature calculated against the raw JSON payload
using your webhook secret key.

