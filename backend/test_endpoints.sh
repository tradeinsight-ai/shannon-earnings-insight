#!/bin/bash
# Test script for earningsInsight API endpoints
# Usage: ./test_endpoints.sh

BASE_URL="http://localhost:8000"

echo "======================================"
echo "Testing earningsInsight API Endpoints"
echo "======================================"
echo ""

# Test 1: Health Check
echo "1. Testing Health Check..."
curl -s "$BASE_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 2: Search Companies
echo "2. Testing Search Companies (q=Apple)..."
curl -s "$BASE_URL/api/companies/search?q=Apple" | python3 -m json.tool | head -40
echo -e "\n"

# Test 3: Get Company Overview
echo "3. Testing Get Company (AAPL)..."
curl -s "$BASE_URL/api/companies/AAPL" | python3 -m json.tool | head -25
echo -e "\n"

# Test 4: Get Company Earnings
echo "4. Testing Get Company Earnings (AAPL)..."
curl -s "$BASE_URL/api/companies/AAPL/earnings" | python3 -m json.tool | head -30
echo -e "\n"

# Test 5: Get Company Financials
echo "5. Testing Get Company Financials (AAPL)..."
curl -s "$BASE_URL/api/companies/AAPL/financials" | python3 -m json.tool
echo -e "\n"

# Test 6: Get Earnings Calendar
echo "6. Testing Earnings Calendar (3month)..."
curl -s "$BASE_URL/api/companies/calendar/upcoming?horizon=3month" | python3 -m json.tool | head -40
echo -e "\n"

# Test 7: Get Transcript
echo "7. Testing Get Transcript (AAPL Q4 2024)..."
curl -s "$BASE_URL/api/transcript/AAPL/Q4/2024" | python3 -m json.tool | head -50
echo -e "\n"

# Test 8: API Documentation
echo "8. API Documentation available at:"
echo "   Swagger UI: $BASE_URL/docs"
echo "   ReDoc: $BASE_URL/redoc"
echo ""

echo "======================================"
echo "All tests completed!"
echo "======================================"
