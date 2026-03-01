# Redis Data Structure

Redis isn't just a "key-value" store; it’s a **data structures server**. Choosing the right structure can drastically change the performance and memory usage of your backend.

## The primary structures you'll use in Python:

1.  **Strings (The Basic)**

    The most common structure. It can store text, serialized JSON, or even binary data (images).
    - **Use Case**: Session tokens, HTML fragments, or simple Write-Through caching.

    - **Python**:

      ```python
      # Best practice: Set data + TTL in one atomic command
      cache.setex("user:101:token", 3600, "secret_session_id")

      # Fetch with a check
      token = cache.get("user:101:token")
      if token:
          print(f"Token active: {token}")
      ```

2.  **Hashes (The "Object")**

    Think of this as a Python dict. It maps string fields to string values, which is much more memory-efficient than storing a big JSON string if you only need to update one field.
    - **Use Case**: User profiles or object properties.

    - **Python**:

      ```python

      # Set multiple fields at once

      cache.hset("profile:101", mapping={"name": "Kanai", "role": "dev"})

      # Get just one field

      role = cache.hget("profile:101", "role")
      ```

3.  **Lists (The Queue)**

    A collection of strings sorted by insertion order. You can push/pop from both ends ($O(1)$ operations).
    - **Use Case**: Task queues (like Celery), recent activity feeds, or notification stacks.
    - **Python**:

      ```Python
      cache.lpush("tasks", "send_email") # Add to front
      task = cache.rpop("tasks")        # Remove from back
      ```

4.  **Sets (The Unique Collection)**

    An unordered collection of unique strings. Redis handles the logic to ensure no duplicates exist.
    - **Use Case**: Tracking unique visitors, "Who's Online," or tags on a blog post.

    - **Python** :

      ```Python
      cache.sadd("online_users", "user_1", "user_2", "user_1") # "user_1" only added once

      is_online = cache.sismember("online_users", "user_1")
      ```

5.  **Sorted Sets (The Leaderboard)**

    Similar to Sets, but every member is associated with a score (a float). The set is always kept sorted by that score.
    - **Use Case**: Gaming leaderboards, priority queues, or "Most Popular" lists.

    - **Python**

      ```python
      cache.zadd("leaderboard", {"player_1": 500, "player_2": 750})
      # Get top players
      top_players = cache.zrevrange("leaderboard", 0, 10, withscores=True)
      ```

## Summary

| Structure       | Best For                      | Time Complexity      | Example                                                               |
| --------------- | ----------------------------- | -------------------- | --------------------------------------------------------------------- |
| **Strings**     | Simple caching, counters      | O(1)                 | `cache.set("user:1", "Kanai")`                                        |
| **Hashes**      | Objects with multiple fields  | O(1) per field       | `cache.hset("profile:101", mapping={"name": "Kanai", "role": "dev"})` |
| **Lists**       | Queues and chronological data | O(1) for push/pop    | `cache.lpush("tasks", "send_email")`                                  |
| **Sets**        | Uniqueness and intersections  | O(1) for adds/checks | `cache.sadd("online_users", "user_1", "user_2")`                      |
| **Sorted Sets** | Ranking and range queries     | O(log N)             | `cache.zadd("leaderboard", {"player_1": 500})`                        |
