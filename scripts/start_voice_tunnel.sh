#!/usr/bin/env bash
# ==============================================================================
# Start Public Tunnel for AgencyOS Voice Agent (Port 8084)
# Exposes the local Voice Agent to Twilio PSTN Webhooks and WebSocket streams
# ==============================================================================

PORT=8084

echo "============================================================"
echo " Starting Public Webhook Tunnel for Voice Agent (Port $PORT)"
echo "============================================================"

# Check if ngrok is installed
if command -v ngrok &> /dev/null; then
    echo "Found ngrok. Starting ngrok http $PORT..."
    echo "Copy your Forwarding URL (https://xxxx.ngrok-free.app) and set:"
    echo "VOICE_PUBLIC_BASE_URL=https://xxxx.ngrok-free.app in your .env file"
    echo ""
    ngrok http $PORT
elif command -v lt &> /dev/null; then
    echo "Found localtunnel. Starting lt --port $PORT..."
    lt --port $PORT
else
    echo "Neither ngrok nor localtunnel (lt) found."
    echo "To install ngrok: https://ngrok.com/download"
    echo "Or run with npx: npx -y localtunnel --port $PORT"
    echo ""
    echo "Starting localtunnel via npx..."
    npx -y localtunnel --port $PORT
fi
