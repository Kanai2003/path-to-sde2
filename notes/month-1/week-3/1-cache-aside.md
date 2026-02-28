# Cache-aside

The **ache-aside** pattern (also known as "Lazy Loading") is the most common caching strategy in backend development. It puts the application in the driver's seat: the app is responsible for checking the cache and updating it.

Think of it like checking your fridge for milk before driving to the store. If the milk is there **(Cache Hit)**, you’re done. If it’s not **(Cache Miss)**, you go to the store, buy it, and put some in the fridge for next time.

## How it Works (The Workflow)

1. **Request**: The application receives a request for data (e.g., getUser(id: 123)).

2. **Check Cache**: The app checks the cache (like Redis).

3. Hit or Miss:
   - **Cache Hit**: The data is found! Return it immediately.

   - **Cache Miss**: The data isn't there. The app queries the Database.

4. **Update Cache**: The app takes the data from the database and writes it into the cache with a **Time-to-Live (TTL)**.

5. **Return**: The data is sent back to the user.

## Why use it?

- **Resiliency**: If the cache goes down, the application still works—it just goes straight to the database (though it will be slower).

- **Efficiency**: You only cache what is actually requested. You aren't wasting memory on "cold" data that nobody asks for.

- **Flexible Data Models**: Since the application handles the logic, you can transform the database data before storing it in the cache (e.g., converting a complex SQL join into a simple JSON string).

## The Challenge: Stale Data

The biggest risk with Cache-aside is Data Inconsistency. If you update a user's name in the database but forget to delete the old version from the cache, the user will see their old name until the TTL expires.

To handle this, developers usually use a **Cache Eviction strategy**: whenever you **UPDATE** or **DELETE** a record in the database, you must also Invalidate (delete) that specific key in the cache.

- **Pro Tip**: In a Node.js or Python backend, you’ll often see this implemented as a "Decorator" or "Middleware" to keep the caching logic separate from your business logic.
