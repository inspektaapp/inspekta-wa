# Inspector WhatsApp Bot

WhatsApp integration for the Inspector real estate platform using PyWa framework and FastAPI.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 3.8+
* Docker
* Docker Compose

### Installing

1. Clone the repository:

```bash
git clone https://github.com/Bitsaac/Inspakta-wa.git
cd Inspakta-wa
```

2. Create a virtual environment and install the dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Set up the environment variables:

```bash
cp .env.example .env
```

4. Run the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

## Running the project with Docker

1. Build and run the containers:

```bash
docker-compose -f docker-compose.dev.yml up -d
```

2. The application will be available at [http://localhost:8000](http://localhost:8000).

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
