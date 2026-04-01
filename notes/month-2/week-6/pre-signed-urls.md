# Pre-Signed URLs

Pre-signed URLs are temporary, cryptographically signed URLs that allow a client to perform a specific action on an object in blob storage without exposing long-lived credentials.

They are commonly used for:

- Direct file uploads from the browser or mobile app to storage
- Temporary downloads of private files
- Reducing load on application servers by bypassing file proxying

## What Problem They Solve

Without pre-signed URLs, a backend often has to receive the file, validate it, and then forward it to storage. That works, but it is expensive:

- The backend uses bandwidth for large files.
- The backend becomes a bottleneck under heavy upload traffic.
- The server must stay online for the full upload duration.

With a pre-signed URL, the backend only authorizes the request. The client uploads or downloads directly from storage.

## Core Idea

A pre-signed URL usually encodes:

- the operation, such as `PUT` or `GET`
- the object key, such as `users/42/avatar.jpg`
- an expiration time
- optional constraints such as content type or headers

The storage service verifies the signature and expiry before allowing the request.

## Typical Upload Flow

1. Client asks backend for an upload URL.
2. Backend validates the request and generates a short-lived pre-signed `PUT` URL.
3. Backend returns the URL and object key.
4. Client uploads the file directly to storage.
5. Client notifies backend that upload is complete.
6. Backend stores metadata in the database.

This pattern keeps the backend out of the file transfer path.

## Typical Download Flow

1. Client requests access to a private file.
2. Backend checks authorization.
3. Backend generates a short-lived pre-signed `GET` URL.
4. Client downloads directly from storage.

## Example: Generating An Upload URL In Python

Using `boto3` with S3:

```python
import boto3

s3 = boto3.client("s3")

def create_upload_url(bucket_name: str, object_key: str, content_type: str) -> str:
    return s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": bucket_name,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=600,  # 10 minutes
    )

url = create_upload_url("my-private-bucket", "users/42/avatar.jpg", "image/jpeg")
print(url)
```

## Example: FastAPI Endpoint For Upload Intent

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/files/upload-intent")
def create_upload_intent(filename: str, content_type: str):
    object_key = f"uploads/{filename}"
    upload_url = create_upload_url(
        bucket_name="my-private-bucket",
        object_key=object_key,
        content_type=content_type,
    )

    return {
        "object_key": object_key,
        "upload_url": upload_url,
        "expires_in_seconds": 600,
    }
```

In a real app, do not trust the raw filename directly. Generate a safe object key yourself, usually with a user ID, UUID, or timestamp prefix.

## Example: Browser Upload With Fetch

```javascript
async function uploadFile(uploadUrl, file) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": file.type,
    },
    body: file,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }
}
```

## Security Rules

- Keep the bucket private by default.
- Issue URLs only after authorization.
- Make URLs short-lived.
- Restrict the object key to exactly one file.
- Validate file type and size before issuing the URL.
- Prefer server-generated object keys over client-provided ones.
- Use separate URLs for upload and download.

## What To Store In The Database

The database should store metadata, not the file bytes:

- `id`
- `owner_id`
- `object_key`
- `bucket`
- `content_type`
- `size_bytes`
- `status` such as `pending`, `ready`, or `deleted`
- `created_at`

The storage bucket is the source of truth for the file itself.

## Common Failure Cases

- Upload succeeds but database write fails: run a reconciliation job.
- URL expires before upload completes: request a new one.
- Client uploads the wrong content type: reject during validation or completion.
- Object exists but metadata was never saved: mark it for cleanup.

## Best Practices

- Use pre-signed uploads for large or frequent files.
- Pair them with object lifecycle rules for temporary files.
- Use a CDN for public or frequently downloaded content.
- Log upload intent and completion separately for observability.

## Interview Summary

Pre-signed URLs let a backend grant temporary access to a single storage operation without exposing credentials. They are the standard way to support scalable direct-to-storage uploads and private downloads while keeping the application server lightweight.
