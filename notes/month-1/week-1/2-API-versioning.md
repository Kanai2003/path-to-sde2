# API Versioning

API versioning is the "insurance policy" for your backend. It allows you to upgrade your code, change data structures, or fix mistakes without breaking the apps (mobile, web, or third-party) that are already using your API.

Think of it like a phone update. Apple can release iOS 18, but they don't force everyone's iPhone 13 to explode the moment they do; they let the old and new exist together for a while.

## The 3 Common Ways to Version

### 1. URL Path Versioning (Most Popular)

The version is literally in the address. It is clear, cache-friendly, and easy to see in logs.

Example: `https://api.example.com/v1/users`

### 2. Header Versioning

The URL stays the same, but the client sends a custom header (like `X-API-Version: 2`). This keeps URLs "clean" but makes testing in a browser harder.

### 3. Query Parameter Versioning

The version is a variable in the URL.

Example: `https://api.example.com/users?version=2`

## Implementation

- Step 1: Create your `v1` logic in a file called `api/v1/endpoints.py`

- Step 2: Create your `v2` logic in a file called `api/v2/endpoints.py`

- Step 3: Mount them in `main.py`

This is where the magic happens. You "prefix" the routers so they don't collide.

## Why go through this trouble?

- **Breaking Changes**: If you decide to rename a field from user_name to username, any app currently using user_name will crash. By putting the change in v2, you let the old app keep working on v1 until they have time to update.

- **A/B Testing**: You can roll out a new feature to only a few users by pointing them to a new version.

- **Deprecation**: You can track how many people are still using v1. Once that hits zero, you can safely delete the old code.

## The "Sunset" Strategy

Never keep versions forever. A common industry standard is to support:

- v(Current): Active development.

- v(Current - 1): Maintenance mode (bug fixes only).

- Everything older: Officially "Sunset" (turned off).

## Senior level tips

Instead of just "mounting" routers, we create sub-applications. This is the cleanest way to keep v1 and v2 docs strictly separated.

- **Scalability**: If you reach v10 in three years, your main file stays tiny—you just keep mounting new sub-apps.
- **No Pollution**: If you deprecate an endpoint in v2, it simply doesn't exist in the /v2/docs, but stays safely in /v1/docs for older clients.
- **Cleaner Logic**: Each version can have its own custom middleware, exception handlers, and security dependencies without affecting the other.
