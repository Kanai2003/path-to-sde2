# OAuth Basics (Backend Notes)

OAuth 2.0 is an authorization framework. It is used to let one application access user resources from another service without sharing the user's password.

JWT answers "who are you?" for your API calls.
OAuth answers "what can this app access, and with whose permission?"

## 1. Core Roles

- Resource Owner: the user.
- Client: your app (web, mobile, backend).
- Authorization Server: issues tokens after user consent.
- Resource Server: API that validates tokens and serves protected data.

## 2. Common Grant Type For Modern Apps

For web and mobile apps, use Authorization Code Flow with PKCE.

High-level flow:

1. User clicks "Continue with Google/GitHub".
2. Client redirects user to provider auth page.
3. User logs in and grants consent.
4. Provider returns an authorization code.
5. Backend exchanges code for access token (and sometimes refresh token).
6. Backend fetches profile data and maps it to local user account.

PKCE protects the code exchange from interception, especially for public clients.

## 3. Access Token vs Refresh Token

- Access token: short-lived, used to call APIs.
- Refresh token: longer-lived, used to get new access tokens.

Best practice:

- Keep access token lifetime small.
- Rotate refresh tokens.
- Revoke refresh tokens on logout/suspicious activity.

## 4. OAuth Scopes

Scopes define permissions, for example:

- `profile`
- `email`
- `repo:read`

Request the minimum scopes required. This is least privilege in practice.

## 5. OAuth In FastAPI Project Architecture

For your URL shortener style architecture:

1. API route receives callback code.
2. Auth service exchanges code with provider.
3. Auth service fetches provider user info.
4. User repository performs upsert in local `users` table.
5. Local app issues its own access/refresh JWT pair.

Important: even when login starts with OAuth provider, your backend should still issue first-party tokens for internal APIs.

## 6. Security Checklist

- Validate `state` parameter to prevent CSRF.
- Validate redirect URI exactly.
- Do not store provider access token in plaintext if long-lived.
- Use HTTPS everywhere.
- Do not trust email verification claim blindly across all providers.
- Log auth events (login success/failure, provider errors, token refresh).

## 7. OAuth vs OIDC

- OAuth 2.0: authorization framework.
- OpenID Connect (OIDC): identity layer on top of OAuth.

If you need reliable user identity claims like `sub`, `email`, `name`, use OIDC.

## 8. Failure Cases To Design For

- User denies consent.
- Code already used or expired.
- Provider downtime/timeouts.
- Scope mismatch.
- Callback replay attempt.

Return clear 4xx errors for client mistakes and 5xx for provider/system failures.

## 9. Interview-Ready Summary

OAuth lets users delegate limited access without sharing passwords. In production backends, use Authorization Code + PKCE, minimal scopes, strict callback validation, and convert provider identity into local first-party tokens for your own APIs.
