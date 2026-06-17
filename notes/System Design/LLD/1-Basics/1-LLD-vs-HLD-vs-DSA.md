# LLD vs HLD vs DSA

## One-Line Summary

| | What it answers |
|---|---|
| **DSA** | How do I process/store data efficiently? |
| **HLD** | What systems/services do I need? |
| **LLD** | How do I write the actual code/classes? |

---

## DSA — Data Structures & Algorithms

> How to solve a computational problem efficiently.

**Role:** Picks the right tool to process data fast.

**Example — URL Shortener:**
- Use **HashMap** to store `shortCode → longURL`
- Use **Base62 encoding** algorithm to generate short code
- Use **LRU Cache** for fast repeated lookups

DSA lives inside a single function or module. It's about **time & space complexity**.

---

## HLD — High Level Design

> What are the building blocks of the system?

**Role:** Defines services, databases, APIs, and how they talk to each other.

**Example — URL Shortener:**
```
Client → API Gateway → App Server → PostgreSQL (store URLs)
                              ↓
                         Redis Cache (hot URLs)
                              ↓
                         CDN (static assets)
```

- Which DB? (SQL vs NoSQL)
- Need a cache? (Redis)
- Need a queue? (Kafka for analytics)
- How to scale? (Load balancer, horizontal scaling)

HLD is a **blueprint**. No code. Boxes and arrows.

---

## LLD — Low Level Design

> How do you actually code this system?

**Role:** Defines classes, interfaces, relationships, and patterns.

**Example — URL Shortener:**
```python
class URLShortener:
    def shorten(self, long_url: str) -> str: ...
    def resolve(self, short_code: str) -> str: ...

class URLRepository:
    def save(self, url: URL) -> None: ...
    def find_by_code(self, code: str) -> URL: ...

class CacheService:
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...
```

- Which design patterns? (Repository, Factory, Strategy)
- Class relationships (has-a, is-a)
- API contracts (method signatures, DTOs)

LLD is **class diagrams + code structure**. Before writing actual implementation.

---

## How They Fit Together

```
Problem
  ↓
HLD → "I need App Server + Redis + PostgreSQL"
  ↓
LLD → "App Server has URLShortener, CacheService, URLRepository classes"
  ↓
DSA → "URLShortener.shorten() uses Base62 + HashMap internally"
  ↓
Code
```

**Real analogy — Building a house:**
- **HLD** = Architect's blueprint (rooms, floors, layout)
- **LLD** = Engineer's drawing (exact dimensions, materials, wiring)
- **DSA** = Tools & techniques (which drill bit, load-bearing calculations)

---

## Interview Context

| Round | Focus |
|---|---|
| DSA round | LeetCode-style problems, optimize complexity |
| HLD round | Design Twitter/YouTube/Uber at scale |
| LLD round | Design Parking Lot/Chess/BookMyShow in OOP |

All three matter. Senior engineers need all three.
