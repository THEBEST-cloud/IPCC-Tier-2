#!/bin/bash

# Test script for Reservoir GHG Emissions Tool API

echo "======================================"
echo "Testing Reservoir GHG Emissions Tool"
echo "======================================"
echo ""

# Check if application is running
echo "1. Checking if application is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Application is running"
else
    echo "❌ Application is not responding"
    echo "   Please start it with: docker-compose up -d"
    exit 1
fi

echo ""
echo "2. Testing health endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

echo ""
echo "3. Testing climate region detection..."
curl -s http://localhost:8000/api/climate-region/45.5 | python3 -m json.tool
echo ""

echo ""
echo "4. Running example analysis..."
curl -s -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @example_request.json | python3 -m json.tool | head -50
echo ""

echo ""
echo "5. Getting list of analyses..."
curl -s http://localhost:8000/api/analyses | python3 -m json.tool | head -20
echo ""

echo ""
echo "======================================"
echo "✅ API Tests Complete!"
echo "======================================"
echo ""
echo "View full API documentation at:"
echo "http://localhost:8000/docs"
echo ""
