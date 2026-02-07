#!/usr/bin/env python3
"""
Test the gemini-embedding-001 model directly
"""

import httpx
from config import Config
import asyncio

async def test_embedding():
    """Test gemini-embedding-001 model"""
    try:
        api_key = Config.GEMINI_API_KEY
        
        print("🔍 Testing gemini-embedding-001...")
        print("=" * 50)
        
        async with httpx.AsyncClient() as client:
            # Test embedding with gemini-embedding-001
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key=" + api_key,
                json={
                    "content": {
                        "parts": [{"text": "test text for embedding"}]
                    },
                    "taskType": "retrieval_document"
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                embedding = result.get("embedding", {}).get("values", [])
                print(f"✅ SUCCESS! Embedding length: {len(embedding)}")
                print(f"First 5 values: {embedding[:5]}")
            else:
                print(f"❌ FAILED: {response.status_code}")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_embedding())
