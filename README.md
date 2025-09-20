# Inspector WhatsApp Bot

WhatsApp integration for the Inspector real estate platform using PyWa framework and FastAPI.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Or using Python module
python -m app.main
```

### 4. Test the Setup

Visit these endpoints to verify everything is working:

- **Health Check**: http://localhost:8000/api/v1/health/
- **Detailed Health**: http://localhost:8000/api/v1/health/detailed
- **API Documentation**: http://localhost:8000/docs
- **Readiness Check**: http://localhost:8000/api/v1/health/ready

## Project Structure

```
inspakta-wa/
├── app/
│   ├── api/v1/endpoints/        # API endpoints
│   ├── core/                    # Core configurations
│   ├── models/                  # Database models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── workers/                 # Celery tasks
│   └── utils/                   # Utility functions
├── tests/                       # Test files
├── logs/                        # Log files
├── requirements.txt             # Dependencies
└── .env                         # Environment variables
```

## Development Status

### ✅ Milestone 1.1 Complete
- [x] Project structure setup
- [x] FastAPI application foundation
- [x] Health check endpoints
- [x] Logging configuration
- [x] Environment management

### 🚧 Next: Milestone 1.2
- [ ] WhatsApp webhook setup
- [ ] PyWa integration
- [ ] Message handling foundation

## Testing

```bash
# Run health checks
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/detailed
curl http://localhost:8000/api/v1/health/ready
```

## Configuration

Key environment variables:

- `DEBUG`: Enable debug mode
- `SECRET_KEY`: JWT secret key (minimum 32 characters)
- `DATABASE_URL`: Database connection string
- `WHATSAPP_TOKEN`: WhatsApp Business API token
- `INSPECTOR_API_KEY`: Inspector platform API key

See `.env.example` for all configuration options.