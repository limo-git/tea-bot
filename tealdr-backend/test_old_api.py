#!/usr/bin/env python3
"""
Test older embedding API endpoints
"""

import httpx
from config import Config
import asyncio

async def test_old_endpoints():
    """Test various embedding endpoints"""
    try:
        api_key = Config.GEMINI_API_KEY
        
        endpoints_to_test = [
            # v1beta endpoints
            "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent",
            "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents",
            
            # v1 endpoints  
            "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:embedContent",
            "https://generativelanguage.googleapis.com/v1/models/text-embedding-004:batchEmbedContents",
            
            # Alternative format
            "https://generativelanguage.googleapis.com/v1beta/embeddings",
            "https://generativelanguage.googleapis.com/v1/embeddings"
        ]
        
        print("🔍 Testing different embedding endpoints...")
        print("=" * 60)
        
        for endpoint in endpoints_to_test:
            print(f"\nTesting: {endpoint}")
            
            async with httpx.AsyncClient() as client:
                try:
                    if "embeddings" in endpoint:
                        # Different format for embeddings endpoint
                        response = await client.post(
                            endpoint + "?key=" + api_key,
                            json={
                                "model": "text-embedding-004",
                                "content": "test text"
                            }
                        )
                    else:
                        # Standard embedContent format
                        response = await client.post(
                            endpoint + "?key=" + api_key,
                            json={
                                "content": {
                                    "parts": [{"text": "test text"}]
                                },
                                "taskType": "retrieval_document"
                            }
                        )
                    
                    if response.status_code == 200:
                        print(f"✅ SUCCESS - {response.status_code}")
                        result = response.json()
                        if "embedding" in result:
                            embedding = result["embedding"].get("values", [])
                            print(f"   Embedding length: {len(embedding)}")
                        elif "embeddings" in result:
                            embeddings = result["embeddings"]
                            print(f"   Found {len(embeddings)} embeddings")
                    else:
                        print(f"❌ FAILED - {response.status_code}")
                        print(f"   {response.text[:100]}...")
                        
                except Exception as e:
                    print(f"❌ ERROR - {e}")
                    
    except Exception as e:
        print(f"❌ Setup Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_old_endpoints())
