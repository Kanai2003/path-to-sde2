# 🚀 Deploy to Render (Production)

This guide shows how to deploy the file upload service to **Render** without managing databases and storage.

## Architecture

```
┌─────────────────────────────────────────┐
│         Render Web Service              │
│  (File Upload API - FastAPI Container)  │
└────────┬─────────────────┬──────────────┘
         │                 │
    ┌────▼────┐      ┌─────▼──────┐
    │ Render  │      │ AWS S3 or  │
    │PostgreSQL      │ DO Spaces  │
    └─────────┘      └────────────┘
```

## Step-by-Step Deployment

### 1. Create Render PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `file-upload-db`
   - **Database**: `file_upload_db`
   - **User**: `file_upload_user`
   - **Region**: Pick closest to you
4. Create database
5. Copy the **Connection String** (looks like: `postgresql://user:password@dpg-xxx.render.internal:5432/file_upload_db`)

### 2. Set Up Object Storage

Choose **ONE** option:

#### Option A: AWS S3 (Recommended)

```bash
# Create S3 bucket
aws s3 mb s3://your-app-uploads --region us-east-1

# Create IAM user for programmatic access
# Permissions: s3:GetObject, s3:PutObject, s3:DeleteObject
# Get: Access Key ID, Secret Access Key
```

#### Option B: Digital Ocean Spaces (Cheaper)

1. [Create Spaces account](https://cloud.digitalocean.com/spaces)
2. Create new Space: `your-app-uploads`
3. Generate Access Keys
4. Region: NYC3 (or closest to you)

### 3. Generate Secret Key

```bash
# Generate a secure random key
openssl rand -hex 32
# Copy output and save to PRODUCTION SECRET_KEY
```

### 4. Create Render Web Service

1. Go to Render Dashboard
2. Click **New +** → **Web Service**
3. Connect your **GitHub repository**
4. Configure:
   - **Name**: `file-upload-service`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt && alembic upgrade head`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 5. Set Environment Variables

In Render dashboard, go to **Environment**:

```env
# Database
DATABASE_URL=postgresql://user:password@dpg-xxx.render.internal:5432/file_upload_db

# If using AWS S3
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_S3_BUCKET=your-app-uploads
AWS_S3_REGION=us-east-1
AWS_S3_ENDPOINT=https://s3.amazonaws.com

# If using Digital Ocean Spaces
# STORAGE_TYPE=s3
# AWS_ACCESS_KEY_ID=YOUR_SPACES_KEY
# AWS_SECRET_ACCESS_KEY=YOUR_SPACES_SECRET
# AWS_S3_BUCKET=your-app-uploads
# AWS_S3_REGION=nyc3
# AWS_S3_ENDPOINT=https://nyc3.digitaloceanspaces.com

# Security
SECRET_KEY=your-generated-secret-key
ENABLE_VIRUS_SCAN=false

# Disable debug
DEBUG=false
```

### 6. Update Storage Integration

Modify `app/core/storage.py` to support S3-compatible services:

```python
import boto3
from botocore.exceptions import ClientError

class S3Storage:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT,
            region_name=settings.AWS_S3_REGION,
        )
        self.bucket = settings.AWS_S3_BUCKET

    async def upload_file(self, file_name: str, file_data, file_size: int, **kwargs):
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=file_name,
                Body=file_data.getvalue(),
                ContentType=kwargs.get('content_type', 'application/octet-stream'),
            )
            return file_name
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            raise

    async def download_file(self, file_name: str):
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=file_name)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 download error: {e}")
            raise

    async def get_presigned_download_url(self, file_name: str, expiration: int):
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_name},
                ExpiresIn=expiration,
            )
            return url
        except ClientError as e:
            logger.error(f"Presigned URL error: {e}")
            raise
```

### 7. Deploy

1. Push code to GitHub
2. Render automatically builds and deploys
3. Monitor in **Logs** tab
4. Check API at: `https://your-service.render.com/docs`

## Cost Comparison (Monthly)

| Service                | Free Tier         | Paid             |
| ---------------------- | ----------------- | ---------------- |
| **Render Web Service** | 10 free hrs/month | $10-48/month     |
| **Render PostgreSQL**  | 90 days free      | $9/month (1GB)   |
| **AWS S3**             | 5GB free          | ~$0.023/GB       |
| **DO Spaces**          | None              | $5/month (250GB) |

**Total**: ~$24-62/month for full production setup

## Environment-Specific Configs

### Development

```bash
docker-compose up -d
# Uses local PostgreSQL + MinIO + ClamAV
```

### Production (Render)

```bash
docker-compose -f docker-compose.prod.yml up
# Uses Render PostgreSQL + AWS S3 + VirusTotal API (optional)
```

## Health Checks

Render automatically checks `/health` endpoint:

```
✅ GET /health → {"status": "healthy", "service": "file-upload-service"}
```

## SSL/TLS

Render provides **automatic HTTPS** - no configuration needed!

## Logs & Monitoring

1. View in Render Dashboard → **Logs**
2. Or via CLI:

   ```bash
   # Install Render CLI
   npm install -g @render-oss/cli

   # View logs
   render logs file-upload-service
   ```

## Troubleshooting

### Database Connection Error

- Verify **Internal Database URL** (not external)
- Check firewall: Render services are on same network
- Test: `psql -c "SELECT version()" $DATABASE_URL`

### S3 Upload Fails

- Verify IAM permissions include: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`
- Check bucket region matches `AWS_S3_REGION`
- Verify credentials in Render env vars

### Migration Fails on Deploy

- Check build logs in Render dashboard
- Manually run: `alembic current` to see current migration
- Roll back if needed: `alembic downgrade -1`

## Auto-Scaling

To auto-deploy on Git push:

1. Render Dashboard → Web Service → **Auto-Deploy**: ON ✅
2. Deploys on every main branch push

## Disaster Recovery

### Database Backup

```bash
# Render PostgreSQL has automatic backups (7 days retention)
# Manual backup:
pg_dump $DATABASE_URL > backup.sql
```

### S3 Versioning

```bash
# Enable S3 versioning for recovery
aws s3api put-bucket-versioning \
  --bucket your-app-uploads \
  --versioning-configuration Status=Enabled
```

---

**Next Steps:**

1. ✅ Create Render PostgreSQL
2. ✅ Create S3 bucket
3. ✅ Generate secret key
4. ✅ Create Render web service
5. ✅ Set environment variables
6. ✅ Deploy and test

You're done! 🎉
