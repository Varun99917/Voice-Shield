#!/bin/bash
# Quick IP Fix - Run when Mac IP changes
# Just updates config and restarts web server

MAC_IP=$(ifconfig en0 | grep "inet " | awk '{print $2}')
echo "📡 New IP: $MAC_IP"

# Update config
sed -i.bak "s|const API_BASE_URL = 'http://[^:]*:8000'|const API_BASE_URL = 'http://$MAC_IP:8000'|" \
  /Users/opium_17/Desktop/SIH/voice-shield/frontend/src/config.ts

# Rebuild web
cd /Users/opium_17/Desktop/SIH/voice-shield/frontend
rm -rf dist .expo
npx expo export --platform web > /tmp/build.log 2>&1

# Restart web server
lsof -ti :8080 | xargs kill -9 2>/dev/null
cd dist && python3 -m http.server 8080 --bind 0.0.0.0 > /dev/null 2>&1 &

echo "✅ Fixed! New URL: http://$MAC_IP:8080"