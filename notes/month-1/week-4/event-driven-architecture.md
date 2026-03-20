# Event-Driven Architecture (EDA)

Event-Driven Architecture is a design style where services communicate by publishing and reacting to **events** instead of calling each other directly for every step.

Think of it like this:

- A direct API call is a phone call: one service talks to exactly one other service right now.
- An event is a radio broadcast: one service announces that something happened, and any interested service can react.

## 1. Core Idea

An **event** is a fact that already happened in the past.

Examples:

- `url.created`
- `url.redirected`
- `user.registered`
- `payment.completed`

The producer does not need to know who will consume the event. This reduces tight coupling between services.

## 2. Main Building Blocks

1. **Producer**
   - Creates events (for example, URL service emits `url.created`).

2. **Broker / Event Bus**
   - Transports events (Kafka, RabbitMQ, Redis Streams, NATS, SQS).

3. **Consumer**
   - Listens and performs work (analytics, notifications, fraud checks).

4. **Schema / Contract**
   - Defines event shape so all services agree on payload format.

5. **Dead Letter Queue (DLQ)**
   - Stores events that failed repeatedly.

## 3. Why Use EDA

- **Scalability**: Heavy background tasks can be processed asynchronously.
- **Resilience**: If one consumer is down, producer can continue publishing.
- **Extensibility**: Add new consumers later without changing producer code.
- **Faster user response**: API can return quickly and move non-critical work to background.

## 4. Trade-offs

- **Eventual consistency**: Data may not update everywhere immediately.
- **Debugging complexity**: A request path can span multiple services and queues.
- **Duplicate events**: Consumers must be idempotent.
- **Ordering challenges**: Global ordering is expensive and often unnecessary.

## 5. Connect to Week 2 (DB Concepts)

### Transactions

If you save data in DB and publish event separately, you can get inconsistency:

- DB write succeeds, event publish fails.
- Event publish succeeds, DB write fails.

Use **Transactional Outbox Pattern**:

1. Save business data and outbox row in the same DB transaction.
2. Background worker reads outbox and publishes event.
3. Mark outbox row as sent.

This gives strong reliability without distributed transactions.

### Isolation Levels

Consumers should read only committed data. This aligns with `READ COMMITTED` behavior and avoids reacting to uncommitted changes.

### Indexing + Query Planner

Consumers often query by:

- `event_id`
- `status`
- `created_at`
- `aggregate_id` (like `short_code` or `user_id`)

Index these columns, then verify with `EXPLAIN ANALYZE` so workers do not cause table scans under load.

## 6. Connect to Week 3 (Cache + Redis)

- Use events to invalidate cache keys in **cache-aside** (`DELETE cache:user:123` after user update).
- Use events to pre-warm cache for hot reads.
- Redis Streams can be used as a lightweight event log in small systems.

## 7. URL Shortener Example

### Synchronous path (user-facing)

1. User hits short URL.
2. Service resolves `short_code -> original_url` quickly.
3. Redirect response is returned immediately.

### Async path (event-driven)

1. Service publishes `url.redirected` event with timestamp, country, user-agent.
2. Analytics consumer increments counters.
3. Reporting consumer updates hourly aggregates.
4. Fraud consumer detects suspicious traffic spikes.

User gets fast redirect while analytics happens in background.

## 8. Delivery Semantics You Should Know

- **At-most-once**: may lose events, no duplicates.
- **At-least-once**: no loss preferred, duplicates possible (most common).
- **Exactly-once**: expensive and difficult across full systems.

Real-world rule: design consumers to be **idempotent** and tolerate retries.

## 9. Practical Checklist

- Define clear event names (`domain.action`, e.g., `url.redirected`).
- Version event schema (`v1`, `v2`) for safe evolution.
- Add `event_id`, `occurred_at`, `source`, and correlation ID.
- Keep payload small; include identifiers, not huge objects.
- Implement retries with backoff and DLQ.
- Build observability: logs + metrics + trace IDs.

## 10. One-Line Summary

EDA helps you build scalable and decoupled systems by reacting to events, but you must manage consistency, retries, idempotency, and monitoring carefully.
