# File Upload Service

Production-grade file upload microservice with **MinIO**, **pre-signed URLs**, and **ClamAV virus scanning**.

## 🚀 Features

- **Secure File Upload** with validation and virus scanning
- **MinIO Integration** for S3-compatible object storage
- **Pre-signed URLs** for direct browser downloads
- **File Deduplication** via SHA256 hashing
- **Async/Await** with FastAPI
- **PostgreSQL** for metadata storage
- **Docker** deployment ready
- **Structured Logging** and error handling
- **Pagination** support for file listings

## 🛠 Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **MinIO** - Object storage
- **ClamAV** - Virus scanning
- **PostgreSQL** - Database
- **Alembic** - Migrations

## 📋 Project Structure

```
file_upload_service/
├── app/
│   ├── api/v1/endpoints/files.py      # Upload, download, delete endpoints
│   ├── core/
│   │   ├── config.py                   # Settings
│   │   ├── exceptions.py               # Custom exceptions
│   │   ├── minio_client.py             # MinIO integration
│   │   └── virus_scanner.py            # ClamAV integration
│   ├── db/
│   │   ├── session.py                  # Database session
│   ├── models/file.py                  # File metadata model
│   ├── repositories/file_repository.py # Database operations
│   ├── schemas/file.py                 # Pydantic schemas
│   ├── services/file_service.py        # Core business logic
│   └── utils/
│       ├── file_utils.py               # File utilities
│       └── logger.py                   # Structured logging
├── alembic/                            # Database migrations
├── tests/                              # Test suite
├── docker-compose.yml                  # Local development
└── Dockerfile                          # Production build
```

## 🔧 Setup

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- MinIO
- ClamAV

### Local Development (with Docker)

```bash
cd projects/file_upload_service

# Start all services
docker-compose up -d

# Logs
docker-compose logs -f file-upload-service

# API docs
http://localhost:8000/docs
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Start server
uvicorn app.main:app --reload
```

## 📚 API Endpoints

### Upload File

```bash
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer user123" \
  -F "file=@document.pdf" \
  -F "description=My important document"
```

Response:

```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 1024000,
  "file_hash": "abc123...",
  "content_type": "application/pdf",
  "created_at": "2024-01-15T10:30:00",
  "message": "File uploaded successfully"
}
```

### List Files

```bash
curl http://localhost:8000/api/v1/files/list \
  -H "Authorization: Bearer user123"
```

### Get File Metadata + Presigned URL

```bash
curl http://localhost:8000/api/v1/files/1 \
  -H "Authorization: Bearer user123"
```

### Generate Presigned Download URL

```bash
curl -X POST http://localhost:8000/api/v1/files/presigned-download/1 \
  -H "Authorization: Bearer user123"
```

### Delete File

```bash
curl -X DELETE http://localhost:8000/api/v1/files/1 \
  -H "Authorization: Bearer user123"
```

## 🔒 Security Features

- **File Extension Validation** - Whitelist allowed types
- **File Size Limits** - Configurable max upload size
- **Virus Scanning** - ClamAV integration (optional)
- **User Isolation** - Files belong to authenticated users
- **SHA256 Hashing** - File integrity verification
- **Pre-signed URLs** - Time-limited direct storage access

## ⚙️ Configuration

Edit `.env` file:

```env
# Storage
MAX_FILE_SIZE=104857600           # 100MB
ALLOWED_EXTENSIONS=pdf,jpg,png

# URLs
PRESIGNED_URL_EXPIRATION=3600     # 1 hour

# Virus Scanning
ENABLE_VIRUS_SCAN=true
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Watch mode
pytest-watch
```

## 📊 Database Schema

```sql
CREATE TABLE files (
  id SERIAL PRIMARY KEY,
  original_filename VARCHAR(255),
  stored_filename VARCHAR(255) UNIQUE,
  file_hash CHAR(64),
  file_size INTEGER,
  content_type VARCHAR(100),
  user_id VARCHAR(100),
  description TEXT,
  is_deleted INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_id ON files(user_id);
CREATE INDEX idx_file_hash ON files(file_hash);
CREATE INDEX idx_stored_filename ON files(stored_filename);
```

## 🚀 Production Deployment

### MinIO Setup

```bash
# Create bucket
aws s3api create-bucket \
  --bucket uploads \
  --endpoint-url http://minio:9000
```

### Database Backup

```bash
pg_dump file_upload_db > backup.sql
```

### Health Checks

- API: `GET /health`
- MinIO: `curl http://minio:9000/minio/health/live`
- ClamAV: `clamdscan --version`

## 📈 Performance

- **Async operations** for concurrent uploads
- **File deduplication** reduces storage
- **Presigned URLs** offload bandwidth
- **Indexed database queries** for fast lookups
- **Connection pooling** for efficiency

## 🐛 Troubleshooting

### ClamAV Connection Error

```bash
# Check ClamAV status
docker ps | grep clamav

# Check logs
docker logs clamav
```

### MinIO Connection Error

```bash
# Verify credentials
docker logs minio
```

### Permission Denied

- Ensure files have 755 permissions
- Check PostgreSQL user privileges

## 📖 References

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [MinIO SDK](https://min.io/docs/python/latest/)
- [ClamAV Docs](http://www.clamav.net/documents/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)

## 📝 License

MIT License
