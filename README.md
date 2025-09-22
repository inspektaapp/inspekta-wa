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

### ✅ Milestone 1.2 Complete
- [x] WhatsApp webhook setup
- [x] PyWa integration
- [x] Message handling foundation
- [x] ngrok tunneling setup

### ✅ Milestone 1.3 Complete (Database Integration)
- [x] Database connectivity (Neon PostgreSQL)
- [x] Property search functionality
- [x] Natural language processing
- [x] Session management with multi-user support

### 🎯 Current Features
- ✅ WhatsApp bot with menu-driven interface
- ✅ Property search (quick & detailed search options)
- ✅ Natural language property queries
- ✅ Session isolation for multiple users
- ✅ Error handling with user guidance
- ✅ Back navigation and menu commands
- ✅ Automated startup/management scripts
- ✅ Stable ngrok URL management

### 🚧 Next Phase: Property Enhancements
- ⏳ Add property links to inspector.app
- ⏳ Implement meta tags/thumbnails for property sharing
- ⏳ Add agent name + profile links
- ⏳ Add Schedule Inspection buttons
- ⏳ **Then**: Milestone 2.1 - OTP-Based Account Linking

## Testing

```bash
# Run health checks
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/detailed
curl http://localhost:8000/api/v1/health/ready
```

## Management Commands

### 🚀 **Quick Start** (Recommended)
```bash
# Start both server and ngrok with stable URL management
./start_bot.sh

# The script will:
# - Stop any existing processes
# - Start FastAPI server with auto-reload
# - Start ngrok tunnel
# - Display webhook URL for WhatsApp configuration
# - Keep processes running until Ctrl+C
```

### 🔄 **Manual Server Management**
```bash
# Start server only (keeps existing ngrok URL)
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Restart server only (preserves ngrok tunnel and URL)
pkill -f "uvicorn app.main:app"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Check running processes
ps aux | grep uvicorn

# View logs
tail -f logs/app.log
```

### 🌐 **Ngrok Management**
```bash
# Start ngrok tunnel
ngrok http 8000

# Check ngrok status and get webhook URL
curl -s http://localhost:4040/api/tunnels | python3 -m json.tool

# View ngrok web interface (shows all webhook requests)
open http://localhost:4040

# Stop ngrok
pkill ngrok
```

### 🧪 **Testing Commands**
```bash
# Health checks
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/health/detailed
curl http://localhost:8000/api/v1/health/ready

# WhatsApp functionality
curl http://localhost:8000/api/v1/whatsapp/webhook/status

# Session management
curl http://localhost:8000/api/v1/whatsapp/webhook/sessions

# Test message send
curl -X POST "http://localhost:8000/api/v1/whatsapp/send-message?recipient=YOUR_NUMBER&message=Test"

# Run comprehensive tests
python3 test_enhanced_functionality.py
```

### 🚨 **Emergency Reset**
```bash
# Kill everything and restart fresh
pkill uvicorn && pkill ngrok
ngrok http 8000 &
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

Key environment variables:

- `DEBUG`: Enable debug mode
- `SECRET_KEY`: JWT secret key (minimum 32 characters)
- `DATABASE_URL`: Database connection string (Neon PostgreSQL)
- `WHATSAPP_TOKEN`: WhatsApp Business API token
- `WHATSAPP_PHONE_ID`: WhatsApp Business phone number ID
- `WHATSAPP_WEBHOOK_VERIFY_TOKEN`: Webhook verification token
- `INSPECTOR_API_KEY`: Inspector platform API key

See `.env.example` for all configuration options.

## 🤖 Bot Commands

Users can interact with the bot using:

**Menu Navigation:**
- `1-8` - Menu options for property search
- `menu` - Return to main menu
- `back` - Go back one step

**Greetings:**
- `hi`, `hello`, `hey` - Friendly greeting with menu

**Natural Language:**
- `"3 bedroom apartments in Lagos"`
- `"Houses under 50 million naira"`
- `"Office spaces in Abuja"`
