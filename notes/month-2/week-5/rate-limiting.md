# Rate Limiting (Backend Notes)

Rate limiting controls how many requests a client can make in a time window.

Goal:

- protect APIs from abuse,
- keep latency stable under spikes,
- provide fair usage across users/tenants.

## 1. What To Limit By

Common limit keys:

- IP address
- user id
- API key
- route + user id (fine-grained)

In authenticated APIs, user-based keys are usually more reliable than IP-based keys.

## 2. Common Algorithms

### Fixed Window

- Example: 100 requests per minute.
- Fast and simple.
- Weakness: burst at boundary (end of one minute + start of next minute).

### Sliding Window Log

- Track timestamps and count requests in moving interval.
- More accurate fairness.
- Higher memory and compute cost.

### Token Bucket

- Bucket fills at constant rate.
- Each request spends one token.
- Allows short bursts while enforcing average rate.

Most production APIs prefer token bucket or sliding window counters.

## 3. Response Behavior

When limit exceeded:

- return HTTP `429 Too Many Requests`
- include `Retry-After` header when possible
- include rate limit metadata headers if your clients need backoff control

Typical headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

## 4. Redis Pattern For Distributed Apps

When multiple API instances run behind a load balancer, in-memory counters per instance are wrong.

Use shared Redis:

1. Build key like `rl:{route}:{user_id}`
2. Increment counter atomically
3. Set/refresh TTL for window
4. Block when counter crosses threshold

Atomic operations or Lua scripts avoid race conditions.

## 5. Design For URL Shortener

Practical split:

- Redirect endpoint: high threshold, because it is read-heavy and public.
- Auth endpoints (`/login`, `/refresh`): strict limits to stop brute force/token abuse.
- URL creation endpoint: moderate per-user limit to control spam.

Combine this with queue-backed analytics so overloaded clients do not block critical flows.

## 6. Security Use Cases

- Login brute-force mitigation.
- OTP and password reset abuse control.
- API scraping/bot slowdown.
- Cost control for expensive AI endpoints.

Rate limiting is not a firewall replacement. Use it together with auth, validation, and monitoring.

## 7. Operational Tips

- Expose metrics: blocked requests, top limited routes, limit key cardinality.
- Add alerts on sudden `429` spikes.
- Tune per route, not globally.
- Whitelist internal health checks and trusted system traffic.
- Keep fallback policy if Redis is unavailable (fail-open vs fail-closed, chosen per endpoint risk).

## 8. Common Mistakes

- One global limit for all endpoints.
- Limiting only by IP in mobile/NAT-heavy networks.
- No `429` observability.
- Not returning retry guidance.
- No distinction between anonymous and authenticated traffic.

## 9. Interview-Ready Summary

Rate limiting protects availability and fairness by controlling request volume per identity and time window. In distributed backends, Redis-backed atomic counters plus endpoint-specific policies and clear `429` responses give a practical production setup.
