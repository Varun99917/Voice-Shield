#!/bin/bash
# Voice Shield Auto-Setup Script
# Run this ONCE after every Mac restart
# It auto-detects IP and starts everything

echo "🛡️ Voice Shield Auto-Setup Starting..."

# Get current Mac IP
MAC_IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
echo "📡 Detected IP: $MAC_IP"

# Update config.ts with current IP
CONFIG_FILE="/Users/opium_17/Desktop/SIH/voice-shield/frontend/src/config.ts"
sed -i.bak "s|const API_BASE_URL = 'http://[^:]*:8000'|const API_BASE_URL = 'http://$MAC_IP:8000'|" "$CONFIG_FILE"
echo "✅ Updated config.ts with IP: $MAC_IP"

# Kill existing backend
echo "🛑 Stopping old backend..."
lsof -ti :8000 | xargs kill -9 2>/dev/null
sleep 1

# Start backend
echo "🚀 Starting backend..."
cd /Users/opium_17/Desktop/SIH/voice-shield/backend
../../venv/bin/python main.py > /tmp/backend.log 2>&1 &
sleep 3

# Check backend
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend running on port 8000"
else
    echo "❌ Backend failed to start!"
    cat /tmp/backend.log
    exit 1
fi

# Kill existing web server
echo "🛑 Stopping old web server..."
lsof -ti :8080 | xargs kill -9 2>/dev/null
sleep 1

# Rebuild web
echo "📦 Rebuilding web app..."
cd /Users/opium_17/Desktop/SIH/voice-shield/frontend
rm -rf dist .expo
npx expo export --platform web > /tmp/build.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Web build successful"
else
    echo "❌ Web build failed!"
    tail -20 /tmp/build.log
    exit 1
fi

# Start web server
echo "🌐 Starting web server..."
cd dist
python3 -m http.server 8080 --bind 0.0.0.0 > /dev/null 2>&1 &
sleep 2

# Check web server
if curl -s http://localhost:8080/ > /dev/null 2>&1; then
    echo "✅ Web server running on port 8080"
else
    echo "❌ Web server failed!"
    exit 1
fi

echo ""
echo "============================================"
echo "🎉 VOICE SHIELD READY!"
echo "============================================"
echo "📱 Phone URL: http://$MAC_IP:8080"
echo "💻 Mac URL:  http://localhost:8080"
echo "📚 Backend:  http://localhost:8000/docs"
echo "============================================"
echo "Login: admin@voiceshield.com / admin123"
echo "============================================"
