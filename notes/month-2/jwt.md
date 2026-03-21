# JWT in URL Shortener (Implementation-Synced Notes)

This note is synced with the current auth implementation in the URL shortener app.

## 1. Why JWT Here

The app has 3 main responsibilities:

1. URL shortening
2. URL redirection
3. Link analytics

JWT auth is added so user-specific actions can be protected without storing server-side sessions.

In this design:

- Access token: short-lived, sent as Bearer token to protected APIs.
- Refresh token: long-lived, rotated, stored as hash in DB.

## 2. Auth Architecture (Current Project)

Request flow follows your project pattern:

Client -> API -> Service/Dependency -> Repository -> DB

For auth-protected routes:

1. Client sends `Authorization: Bearer <access_token>`.
2. Dependency validates JWT signature and claims.
3. Dependency fetches active user from DB.
4. Endpoint executes business logic.

## 3. JWT Structure Used

Tokens are signed with HS256 and include:

- `sub`: user id
- `type`: `access` or `refresh`
- `iat`: issued-at timestamp
- `exp`: expiry timestamp
- `jti`: unique token id

Important: refresh token raw value is never stored in DB. Only SHA-256 hash is stored.

## 4. Endpoints Implemented

Base prefix: `/api/v1/auth`

1. `POST /register`
   - Creates user with PBKDF2 password hash.

2. `POST /login`
   - Verifies credentials.
   - Issues access + refresh tokens.
   - Stores refresh token hash in `refresh_tokens` table.

3. `POST /refresh`
   - Verifies refresh JWT.
   - Confirms refresh token is active in DB (not revoked, not expired).
   - Revokes old refresh token.
   - Issues new access + refresh pair (rotation).

4. `POST /logout`
   - Requires valid access token.
   - Revokes the provided refresh token for current user.

5. `POST /logout-all`
   - Requires valid access token.
   - Revokes all non-revoked refresh tokens for current user.

6. `GET /me`
   - Requires valid access token.
   - Returns current user profile.

## 5. Data Model for Auth

### users

- `id` (UUID as string)
- `email` (unique, indexed)
- `password_hash`
- `is_active`, `is_verified`
- timestamps

### refresh_tokens

- `id`
- `user_id` (FK users.id)
- `token_hash` (unique, indexed)
- `expires_at` (indexed)
- `revoked` (indexed)
- timestamps
- composite index: `(user_id, revoked, expires_at)`

This indexing supports fast checks during refresh/logout at high request volume.

## 6. Security Decisions in Code

1. Password hashing
   - PBKDF2-SHA256 with random per-password salt and high iterations.

2. Constant-time comparison
   - `hmac.compare_digest` for password/hash verification path.

3. Refresh token protection
   - Store hash, not raw token.

4. Token type enforcement
   - Access token cannot be used on refresh endpoint.
   - Refresh token cannot be used as bearer access token.

5. Rotation on refresh
   - Old refresh token is revoked before new pair is returned.

## 7. Config Values Added

From environment/config:

- `JWT_SECRET_KEY`
- `JWT_ALGORITHM` (default `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 15)
- `REFRESH_TOKEN_EXPIRE_DAYS` (default 7)

Use a strong random secret in production.

## 8. Sequence Diagrams (Mental Model)

### Login

1. User sends email + password.
2. API verifies credentials.
3. API returns access + refresh token.
4. DB stores refresh token hash + expiry.

### Access protected endpoint (`/me`)

1. Client sends bearer access token.
2. API validates JWT and `type=access`.
3. API fetches user by `sub`.
4. API returns profile.

### Refresh

1. Client sends refresh token.
2. API validates JWT and `type=refresh`.
3. API checks active token hash in DB.
4. API revokes old refresh token.
5. API issues new token pair and stores new refresh hash.

## 9. How This Fits Your High-Level Design

Your redirection path remains performance-focused:

- Redirect flow still optimized with cache-first lookup.
- Analytics still decoupled through queue/background processing.

JWT auth is isolated in `/api/v1/auth` and dependency layer, so it does not slow down the core hot redirect path unnecessarily.

## 10. Practical Testing Checklist

1. Register user with unique email.
2. Login and capture tokens.
3. Call `/api/v1/auth/me` with access token.
4. Refresh using refresh token and ensure old refresh token fails later.
5. Logout using new refresh token; verify refresh fails.
6. Login again, call `/logout-all`, verify all sessions revoked.

## 11. Interview-Ready Summary

This app uses stateless JWT access tokens plus DB-backed refresh token rotation. Access stays fast, refresh is revocable, stolen refresh tokens are limited by hashing + rotation + revocation checks.
