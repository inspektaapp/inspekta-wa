# Getting Started - Inspector WhatsApp Bot

Quick guide to run and test the WhatsApp bot application.

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)

## Option 1: Local Development (Recommended for beginners)

### 1. Install Dependencies
```bash
pip install -r requirements-core.txt
```

### 2. Run the Application
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test the Application
Open your browser or use curl:

```bash
# Basic health check
curl http://localhost:8000/api/v1/health/

# Detailed health check
curl http://localhost:8000/api/v1/health/detailed

# Interactive API documentation
open http://localhost:8000/docs
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-20T17:55:00.000000Z",
  "version": "1.0.0"
}
```

## Option 2: Docker (Production-ready)

### 1. Run with Docker Compose
```bash
# Development mode (with hot reload)
docker-compose -f docker-compose.dev.yml up

# Production mode
docker-compose up
```

### 2. Test the Application
```bash
curl http://localhost:8000/api/v1/health/
```

## What's Currently Working

✅ **FastAPI Application**: REST API server with health endpoints
✅ **Health Monitoring**: `/api/v1/health/` endpoints with detailed checks
✅ **Configuration Management**: Environment-based settings
✅ **Logging**: Structured logging with file rotation
✅ **Docker Support**: Containerized deployment ready
✅ **Auto Documentation**: Swagger UI at `/docs`

## Next Steps

The current foundation provides:
- A running FastAPI server
- Health check endpoints
- Basic project structure
- Docker containerization

**Coming Next**: WhatsApp webhook integration (Milestone 1.2)

## Project Structure
```
inspakta-wa/
├── app/                    # Main application code
│   ├── main.py            # FastAPI app entry point
│   ├── core/              # Core utilities (config, logging)
│   └── api/v1/            # API endpoints
├── docs/                  # Documentation
├── tests/                 # Test files
├── logs/                  # Application logs
├── requirements-*.txt     # Dependencies
└── docker-compose.yml     # Container orchestration
```

## Troubleshooting

**Port already in use?**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

**Dependencies issues?**
```bash
# Try minimal requirements first
pip install -r requirements-minimal.txt
```