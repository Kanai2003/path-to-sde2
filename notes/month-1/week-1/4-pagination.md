# Pagination

Pagination is the process of splitting a large dataset into smaller, manageable chunks (pages). Without it, if your GitCash app tries to load 10,000 GitHub commits at once, the browser will freeze, the database will sweat, and the user will wait forever.

There are two main ways to do this in backend development.

## 1. Offset Pagination (The "Classic" Way)

This is the most common method. It uses two parameters:

- **Limit (or Page Size)**: How many items you want (e.g., 10).

- **Offset**: How many items to skip (e.g., if you are on page 3, skip 20).

The SQL behind it:

```SQL
SELECT \* FROM commits ORDER BY created_at DESC LIMIT 10 OFFSET 20;
```

### Pros:

- Easy to implement.
- Allows users to jump to a specific page (e.g., "Go to page 5").

### Cons:

- **Performance**: As the offset gets huge (e.g., OFFSET 1000000), the database gets very slow because it still has to "read" all those skipped rows.

- **The "Drift" Problem**: If a new commit is added while a user is on page 1, when they click page 2, they might see the last item from page 1 again because everything shifted down.

## 2. Cursor Pagination (The "Infinite Scroll" Way)

**Used by Facebook, Instagram, and the GitHub API**. Instead of "skipping" rows, you ask for items after the last ID you saw.

- Limit: 10.

- After (Cursor): The ID or timestamp of the last item on the current page.

The SQL behind it:

```SQL
SELECT \* FROM commits WHERE id < last_seen_id ORDER BY id DESC LIMIT 10;
```

### Pros:

- **Performance**: Extremely fast even with billions of rows (it uses an index).

- **Consistency**: No "duplicate" items if new rows are added.

### Cons:

- You can't jump to a specific page; you can only go "Next" or "Previous."

## Professional Response Structure

A mature API doesn't just return a list. It returns metadata so the frontend knows if there is a "Next" page.The Level 3 (HATEOAS) version of pagination looks like this:\

```JSON
{
    "items": [...],
    "metadata": {
        "total_count": 100,
        "has_next": true,
        "next_page_url": "/api/v1/commits?limit=10&offset=20"
    }
}
```

## Summary Table

| Feature      | Offset Pagination            | Cursor Pagination      |
| ------------ | ---------------------------- | ---------------------- |
| Best For     | Admin panels, Search results | Feeds, Infinite scroll |
| Speed        | Slows down at high offsets   | Consistent speed       |
| Ease of Use  | Very Easy                    | Moderate               |
| Jump to Page | Yes                          | No                     |
