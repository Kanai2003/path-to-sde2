# Write Through

The **Write-through** strategy takes a different approach by treating the cache and the database as a single, synchronized unit. Instead of the application manually updating the cache after a miss (like in Cache-aside), the application always writes data to the cache first.

The cache then immediately updates the database before confirming the write is "done" to the application.

## How it Works (The Workflow)

1. **Application Write**: Your backend sends a "Save" or "Update" request to the cache (e.g., updating a user's status).

2. **Synchronous Update**: The cache synchronously writes that data to the database.

3. **Confirmation**: Only after the database confirms the save does the cache tell the application, "Success!"

4. **Read Path**: When you need to read that data later, it is already sitting in the cache, ready for a guaranteed **Cache Hit**.

## Why use Write-through?

- **Data Consistency**: This is the biggest "pro." Since the cache and DB are updated in the same transaction, they are almost never out of sync. You don't have to worry about "stale" data.

- **Read Performance**: Every write pre-loads the cache. This is perfect for data that is written once but read many, many times (like a viral social media post or a product description).

- **Simplicity for Reads**: Your read logic doesn't need "if/else" checks for cache misses; it just trusts the cache.

## The Trade-offs

- **Write Latency**: Because you have to wait for both the cache and the database to finish saving, every "write" operation takes slightly longer than it would if you just hit the database.

- **Cache Churn**: You might end up filling your expensive RAM (Redis) with data that is never actually read. If you save 1,000 logs but only ever read 5 of them, you're wasting cache space.

## Write-through vs. Write-behind

Don't confuse this with Write-behind (or Write-back).

- In **Write-through**, the DB update happens immediately (Synchronous).

- In **Write-behind**, the cache saves the data and tells the app "Done!" immediately, then updates the DB a few seconds later in the background (Asynchronous). This is faster for the user but riskier if the cache crashes before the DB is updated.
