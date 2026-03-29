# Blob Storage (Backend Notes)

Blob storage is object storage for files (images, videos, PDFs, backups, logs).

Each stored item is an object:

- `key`: unique path-like name (`users/42/avatar.jpg`)
- `data`: raw bytes
- `metadata`: content type, size, custom tags

It is optimized for storing large binary content cheaply and at scale.

## 1. Why Not Store Files In DB

Storing large files in relational DB rows increases DB size, backup time, and query pressure.

Better pattern:

1. Store file bytes in blob storage.
2. Store only file metadata + object key/URL in DB.

This keeps DB focused on transactional data.

## 2. Core Terms

- `bucket/container`: top-level namespace for objects.
- `object key`: full identifier inside bucket.
- `metadata`: file attributes.
- `ACL/policy`: access rules.
- `lifecycle policy`: auto move/delete objects after age threshold.

## 3. Upload/Download Patterns

### A) Server Proxy Upload

1. Client sends file to backend.
2. Backend validates and uploads to storage.
3. Backend returns stored object URL/key.

Pros: easy control.  
Cons: backend bandwidth and CPU cost are high.

### B) Direct Upload With Pre-Signed URL (Preferred)

1. Client asks backend for upload permission.
2. Backend generates short-lived signed URL for one object key.
3. Client uploads directly to blob storage.
4. Client notifies backend; backend stores metadata in DB.

Pros: scalable and cheaper for backend.  
Cons: requires careful validation and expiry control.

## 4. Pre-Signed URL: What It Is

A pre-signed URL is a temporary, signed link that grants limited access to one object operation.

Common constraints:

- method: `PUT` or `GET`
- object key: fixed
- expiry: short (for example 5 to 15 minutes)
- optional max size and content type checks

Use case:

- upload profile photo without routing file through API servers.

## 5. Data Model Pattern

Example table for app metadata:

- `id`
- `owner_id`
- `object_key`
- `bucket`
- `content_type`
- `size_bytes`
- `checksum` (optional)
- `status` (`pending`, `ready`, `deleted`)
- `created_at`

Important: source of truth for bytes is blob storage; DB tracks references and business state.

## 6. Security Checklist

1. Keep bucket private by default.
2. Use pre-signed URLs instead of public write access.
3. Validate file type and max size before issuing upload URL.
4. Enforce key naming rules to prevent collisions.
5. Scan uploads if your domain requires malware checks.
6. Use encryption at rest and TLS in transit.
7. Rotate credentials and use least-privilege IAM policies.

## 7. Performance And Cost Tips

1. Use CDN in front of blob storage for hot downloads.
2. Use lifecycle policies:
   - move old objects to cheaper tier
   - delete temporary uploads automatically
3. Compress where useful (images/text artifacts).
4. Avoid very large numbers of objects in one flat prefix; use structured prefixes.

## 8. Failure Cases To Handle

1. Uploaded to storage but DB write failed: run reconciliation job.
2. DB row exists but object missing: mark as broken and alert.
3. Expired pre-signed URL: client retries by requesting a new URL.
4. Duplicate upload intent: use idempotency key in backend endpoint.

## 9. Concrete Flow (Profile Image Upload)

1. Client calls `POST /files/upload-intent` with filename and content type.
2. Backend validates request and creates object key.
3. Backend returns pre-signed `PUT` URL (10 min expiry).
4. Client uploads bytes directly to storage.
5. Client calls `POST /files/complete` with object key.
6. Backend verifies object exists, then persists metadata in DB.

## 10. Interview-Ready Summary

Blob storage stores files as objects (`key + bytes + metadata`) and scales better than relational DB for binary data. In production, keep buckets private, upload via short-lived pre-signed URLs, store metadata in DB, and use lifecycle + CDN for cost and performance.
