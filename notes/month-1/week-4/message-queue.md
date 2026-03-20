# Message Queue

A Message Queue is a buffer between producer and consumer services.

Instead of doing all work in one API request, a service can push a message to a queue and return quickly. Workers process messages asynchronously.

## 1. Mental Model

Think of a restaurant:

- API server = waiter taking orders.
- Queue = order slip rail in kitchen.
- Worker = chef processing slips.

If many customers come at once, the queue absorbs the spike so the system does not collapse.

## 2. Queue vs Pub/Sub

### Queue (Work Queue)

- One message is processed by one worker.
- Good for background jobs: email, image resize, analytics write.

### Pub/Sub (Fan-out)

- One message can go to multiple consumers.
- Good when many systems react to same event.

You can combine both: publish an event, then each consumer group uses its own queue.

## 3. Core Terms

- **Producer**: sends message.
- **Consumer/Worker**: processes message.
- **Ack**: confirms successful processing.
- **Retry**: message is re-delivered after failure.
- **DLQ**: messages that failed too many times.
- **Visibility timeout / in-flight timeout**: lock period while worker is processing.

## 4. Message Lifecycle

1. Producer sends message.
2. Broker stores message durably.
3. Worker receives message.
4. Worker processes business logic.
5. On success, worker sends ack.
6. On failure, broker retries or routes to DLQ.

## 5. Delivery Guarantees

- **At-most-once**: no retry, may lose message.
- **At-least-once**: retries enabled, duplicates possible.
- **Exactly-once**: costly and limited in scope.

Most production systems use at-least-once + idempotent workers.

## 6. Connect to Week 2

### Transactions

When creating DB data and queue message together, use reliable pattern (Outbox):

- Write DB row + outbox row in one transaction.
- Separate publisher sends queued message from outbox.

This avoids lost events during partial failures.

### Isolation Levels

Workers should process committed data only. Reading uncommitted state can cause invalid side effects.

### Indexing + Query Planner

Queue-backed workers usually update and query by:

- `job_id`
- `status`
- `next_retry_at`
- `created_at`

Index these fields and validate with `EXPLAIN ANALYZE` to avoid throughput drops.

## 7. Connect to Week 3

- Queue consumers can refresh or invalidate Redis cache entries.
- Redis Lists/Streams can implement simple queue patterns.
- Cache-aside plus queue works well for expensive recalculation tasks.

## 8. URL Shortener Example

### Problem

On every redirect, writing analytics synchronously increases latency.

### Queue-based flow

1. User requests short link.
2. Service resolves URL and returns redirect immediately.
3. Service pushes `click_recorded` message with metadata.
4. Analytics worker batches writes to DB.
5. Failed messages retry; poison messages move to DLQ.

Result: fast redirects + reliable analytics.

## 9. Best Practices

- Keep messages small and schema-versioned.
- Add idempotency key (`event_id`) to deduplicate.
- Use exponential backoff for retries.
- Set max retry count, then DLQ.
- Track queue lag, retry rate, and DLQ volume.
- Use correlation IDs for tracing across services.

## 10. Common Mistakes

- Doing long processing before ack without timeout tuning.
- No idempotency handling (duplicates corrupt data).
- Infinite retries without DLQ.
- Treating queue as database (no archival strategy).

## 11. One-Line Summary

A message queue improves reliability and scalability by decoupling producers from consumers, but correct retries, idempotency, and observability are essential.
