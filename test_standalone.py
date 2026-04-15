#!/usr/bin/env python3
"""
SavySoil Backend - Standalone Local Testing Script
===================================================

This script allows you to test the backend independently without running the frontend.
Useful for debugging LLM integration and verifying your API key works.

Usage:
    python test_backend_standalone.py
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BACKEND_URL = "http://localhost:8000/review-submission"
GEMMA_API_KEY = os.getenv("GEMMA_API_KEY", "")
GEMMA_ENDPOINT = os.getenv("GEMMA_ENDPOINT", "")

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

async def test_health_endpoint():
    """Test the health check endpoint."""
    print_section("Testing Health Endpoint")
    
    url = "http://localhost:8000/health"
    print(f"GET {url}\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            if response.status_code == 200:
                print("✅ Health check passed!")
                print(f"Response:\n{json.dumps(response.json(), indent=2)}")
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code}")
                print(f"Response: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Hint: Is the backend running? Run: uvicorn main:app --reload")
        return False

async def test_submission_endpoint():
    """Test the main submission endpoint."""
    print_section("Testing Review Submission Endpoint")
    
    # Sample student submission
    submission = {
        "crop": "wheat",
        "soil_type": "cropping_loam",
        "yield_score": 78,
        "cost_score": 82,
        "fertilizer_plan": [
            {
                "product_name": "Urea",
                "rate_kg_ha": 150,
                "timing": "Sowing"
            },
            {
                "product_name": "Triple Superphosphate",
                "rate_kg_ha": 100,
                "timing": "Sowing"
            },
            {
                "product_name": "Ammonium Sulfate",
                "rate_kg_ha": 120,
                "timing": "Vegetative"
            }
        ]
    }
    
    print(f"POST {BACKEND_URL}\n")
    print(f"Request body:\n{json.dumps(submission, indent=2)}\n")
    print("Waiting for Gemma to respond (this may take 10-30 seconds)...\n")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(BACKEND_URL, json=submission)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Submission processed successfully!")
                print(f"\nResponse:\n{json.dumps(data, indent=2)}")
                return True
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
                # Debug info
                if response.status_code == 500:
                    print("\n💡 Hint: API key might not be configured.")
                    print(f"   GEMMA_API_KEY = '{GEMMA_API_KEY[:10]}...' (shown truncated)")
                    print(f"   GEMMA_ENDPOINT = {GEMMA_ENDPOINT}")
                
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Hint: Is the backend running? Run: uvicorn main:app --reload")
        return False

async def test_invalid_input():
    """Test error handling with invalid input."""
    print_section("Testing Error Handling")
    
    invalid_submission = {
        "crop": "wheat",
        "soil_type": "cropping_loam",
        "yield_score": 150,  # Invalid: > 100
        "cost_score": 82,
        "fertilizer_plan": []
    }
    
    print(f"POST {BACKEND_URL}")
    print("Testing with invalid input (yield_score > 100)\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(BACKEND_URL, json=invalid_submission)
            
            if response.status_code != 200:
                print("✅ Backend correctly rejected invalid input!")
                print(f"Status: {response.status_code}")
                print(f"Error message: {response.json()}\n")
                return True
            else:
                print("❌ Backend accepted invalid input (this shouldn't happen)")
                return False
    except Exception as e:
        print(f"Error: {e}")
        return False

async def main():
    """Run all tests."""
    print("\n" + "🌱"*30)
    print("  SavySoil Backend - Standalone Test Suite")
    print("🌱"*30)
    
    # Check environment variables
    print_section("Environment Check")
    if GEMMA_API_KEY:
        print(f"✅ GEMMA_API_KEY is set ({GEMMA_API_KEY[:15]}...)")
    else:
        print("⚠️  GEMMA_API_KEY is not set. Advisor review will fail.")
        print("   Set it in .env or your hosting platform environment variables.")
    
    if GEMMA_ENDPOINT:
        print(f"✅ GEMMA_ENDPOINT = {GEMMA_ENDPOINT}")
    else:
        print("⚠️  GEMMA_ENDPOINT is not set.")
    
    print(f"\nBackend URL: {BACKEND_URL}\n")
    
    # Run tests
    results = []
    
    results.append(("Health Check", await test_health_endpoint()))
    
    if results[0][1]:  # Only run remaining tests if health check passes
        results.append(("Submission Test", await test_submission_endpoint()))
        results.append(("Error Handling", await test_invalid_input()))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}\n")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your backend is working correctly.")
        print("   You can now use the frontend and click 'Get Advisor Review'.")
    else:
        print("\n❌ Some tests failed. See above for details and hints.")
    
    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Tests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
