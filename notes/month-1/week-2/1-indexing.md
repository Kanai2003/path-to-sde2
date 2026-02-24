# Indexing DB column

In database management, indexing is a data structure technique used to quickly locate and access the data in a database table without having to search every row.

Think of it like the index at the back of a textbook. If you want to find "FastAPI" in a 500-page book, you don't read page by page (a Full Table Scan). Instead, you go to the index, find "FastAPI," see that it's on page 42, and flip directly there.

## 1. How Indexing Works

When you create an index on a column (e.g., email), the database creates a separate, sorted structure that contains the column values and **pointers** to the physical location of the full row in the main table.
Most modern databases (PostgreSQL, MySQL, etc.) use a **B-Tree (Balanced Tree)** structure for indexing.

- **B-Tree Efficiency**: A B-Tree keeps data sorted and allows for searches, sequential access, insertions, and deletions in logarithmic time **(O(log n))**.
- **The Search Process**: Instead of checking 1 million rows, a B-Tree might only require 4 or 5 "hops" to find the exact record you need.

## 2. Types of Indexes

| Type            | Description                                                                                |
| --------------- | ------------------------------------------------------------------------------------------ |
| Primary Index   | Automatically created for your PRIMARY KEY. It's usually the fastest way to find a record. |
| Secondary Index | Created on non-primary columns (like username) to speed up specific searches.              |
| Unique Index    | Ensures that no two rows have the same value in that column (great for emails).            |
| Composite Index | An index on multiple columns at once (e.g., first_name + last_name). Order matters here!   |

## 3. The "Cost" of Indexing

Indexing is not "free." There is always a trade-off.

- **Storage Space**: Indexes are separate files. If you index every column, your database size will balloon.

- **Write Performance**: Every time you INSERT, UPDATE, or DELETE a row, the database must also update the index. This makes writes slightly slower.

- **Maintenance**: Over time, indexes can become fragmented and may need to be rebuilt for peak performance.

## Best practices

- **Index Foreign Keys**: Always index columns used in JOIN operations.

- **Analyze Your Queries**: Don't index everything. Use `EXPLAIN ANALYZE` in DBeaver to see if a query is actually using an index or doing a slow "Full Table Scan".

- **Low Cardinality Rule**: Avoid indexing columns with very few unique values (like gender or is_active). The database often finds it faster to just scan the whole table in those cases.

On the `URL_SHORTENER` project I've indexed the `short_code` column of `urls` table, as this this is the `primary key` so by default this will be indexed. As we know that the redirect action needs to be done with less time so this will be efficient.
