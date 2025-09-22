#!/bin/bash

# Script to start Inspector WhatsApp Bot with ngrok tunnel
# This will keep the same ngrok URL until manually restarted

echo "🤖 Starting Inspector WhatsApp Bot..."

# Kill any existing processes
echo "🔄 Stopping existing processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill ngrok 2>/dev/null || true

# Wait for processes to stop
sleep 2

# Start the FastAPI server in background
echo "🚀 Starting FastAPI server..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Start ngrok
echo "🌐 Starting ngrok tunnel..."
ngrok http 8000 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 5

# Get and display ngrok URL
echo ""
echo "📡 Getting ngrok webhook URL..."
WEBHOOK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] + '/api/v1/whatsapp/webhook') if data.get('tunnels') else print('ERROR: ngrok not ready')" 2>/dev/null)

echo ""
echo "✅ Inspector WhatsApp Bot is ready!"
echo "================================================"
echo "📞 Webhook URL: $WEBHOOK_URL"
echo "🌐 ngrok Web Interface: http://localhost:4040"
echo "🔧 Server Health: http://localhost:8000/api/v1/health/"
echo "================================================"
echo ""
echo "📋 Next Steps:"
echo "1. Update WhatsApp webhook URL in Meta Developer Console:"
echo "   $WEBHOOK_URL"
echo "2. Add your phone number to recipient allowlist"
echo "3. Send 'hi' to your WhatsApp Business number to test"
echo ""
echo "⚠️  Keep this terminal open to maintain the tunnel!"
echo "💡 Press Ctrl+C to stop both server and ngrok"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $SERVER_PID 2>/dev/null || true
    kill $NGROK_PID 2>/dev/null || true
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill ngrok 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running
echo "🎯 Bot is running... Press Ctrl+C to stop"
wait