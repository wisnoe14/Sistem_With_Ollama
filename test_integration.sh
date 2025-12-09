#!/bin/bash

# Test frontend and backend integration
echo "=== Testing Frontend-Backend Integration ==="

# Start servers if not running
echo "1. Checking if servers are running..."
curl -s http://localhost:8000/api/v1/endpoints/conversation/generate-simulation-questions > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend not running on port 8000"
fi

curl -s http://localhost:5174 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend is running on port 5174"
else
    echo "❌ Frontend not running on port 5174"
fi

# Test the endpoint directly
echo -e "\n2. Testing generate-simulation-questions endpoint..."
curl -X POST http://localhost:8000/api/v1/endpoints/conversation/generate-simulation-questions \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "ICON12345",
    "topic": "telecollection",
    "conversation": [],
    "user": "test@iconnet.co.id"
  }' | python -m json.tool

echo -e "\n3. Check CORS headers..."
curl -i -X OPTIONS http://localhost:8000/api/v1/endpoints/conversation/generate-simulation-questions \
  -H "Origin: http://localhost:5174" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"

echo -e "\n=== Integration Test Complete ==="