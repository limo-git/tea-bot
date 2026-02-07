#!/usr/bin/env python3
"""
Test v1 API for embeddings
"""

import httpx
from config import Config
import asyncio

async def test_v1_api():
    """Test v1 API for embeddings"""
    try:
        api_key = Config.GEMINI_API_KEY
        
        # Test v1 models endpoint
        print("🔍 Testing v1 API...")
        print("=" * 40)
        
        async with httpx.AsyncClient() as client:
            # List v1 models
            response = await client.get(
                "https://generativelanguage.googleapis.com/v1/models?key=" + api_key
            )
            
            if response.status_code == 200:
                models_data = response.json()
                print("✅ v1 API - Found models:")
                
                for model in models_data.get("models", []):
                    name = model.get("name", "")
                    methods = model.get("supportedMethods", [])
                    display_name = model.get("displayName", "")
                    
                    if any("embed" in method.lower() for method in methods):
                        print(f"   📝 EMBEDDING: {name} ({display_name})")
                        
                        # Test this embedding model
                        try:
                            embed_response = await client.post(
                                f"https://generativelanguage.googleapis.com/v1/models/{name}:embedContent?key=" + api_key,
                                json={
                                    "content": {
                                        "parts": [{"text": "test text"}]
                                    }
                                }
                            )
                            
                            if embed_response.status_code == 200:
                                print(f"      ✅ WORKS for embedding!")
                            else:
                                print(f"      ❌ Failed: {embed_response.status_code}")
                        except Exception as e:
                            print(f"      ❌ Error: {e}")
                    
                    elif any("generate" in method.lower() for method in methods):
                        print(f"   🤖 GENERATION: {name} ({display_name})")
            else:
                print(f"❌ v1 API failed: {response.status_code}")
                print(f"   {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_v1_api())
