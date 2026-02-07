#!/usr/bin/env python3
"""
Simple test to check Gemini API and find working models
"""

import google.genai as genai
from config import Config
import asyncio

async def test_models():
    """Test different model names to see what works"""
    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        print("🔍 Testing different model names...")
        print("=" * 50)
        
        # Test embedding models
        embedding_models_to_test = [
            "text-embedding-004",
            "models/text-embedding-004", 
            "embedding-001",
            "models/embedding-001",
            "text-embedding-005",
            "models/text-embedding-005"
        ]
        
        print("\n📝 TESTING EMBEDDING MODELS:")
        print("-" * 40)
        
        for model_name in embedding_models_to_test:
            try:
                result = client.models.embed_content(
                    model=model_name,
                    contents="test text",
                    config={"task_type": "retrieval_document"}
                )
                print(f"✅ {model_name} - WORKS")
                print(f"   Embedding length: {len(result.embeddings[0].values)}")
                break
            except Exception as e:
                print(f"❌ {model_name} - {str(e)[:80]}...")
        
        # Test generation models
        generation_models_to_test = [
            "gemini-3-flash-preview",
            "models/gemini-3-flash-preview",
            "gemini-2.0-flash-exp", 
            "models/gemini-2.0-flash-exp",
            "gemini-1.5-flash",
            "models/gemini-1.5-flash",
            "gemini-1.5-pro",
            "models/gemini-1.5-pro"
        ]
        
        print("\n🤖 TESTING GENERATION MODELS:")
        print("-" * 40)
        
        for model_name in generation_models_to_test:
            try:
                result = client.models.generate_content(
                    model=model_name,
                    contents="Hello, test message"
                )
                print(f"✅ {model_name} - WORKS")
                print(f"   Response: {result.text[:50]}...")
                break
            except Exception as e:
                print(f"❌ {model_name} - {str(e)[:80]}...")
        
        # Try to list models using REST API directly
        print("\n🌐 TRYING REST API DIRECTLY:")
        print("-" * 40)
        
        try:
            import httpx
            
            api_key = Config.GEMINI_API_KEY
            url = "https://generativelanguage.googleapis.com/v1beta/models"
            
            async with httpx.AsyncClient() as client_http:
                response = await client_http.get(
                    f"{url}?key={api_key}"
                )
                
                if response.status_code == 200:
                    models_data = response.json()
                    print("✅ REST API - Found models:")
                    
                    for model in models_data.get("models", []):
                        name = model.get("name", "")
                        methods = model.get("supportedMethods", [])
                        display_name = model.get("displayName", "")
                        
                        # Print all models for debugging
                        print(f"   📋 ALL: {name} ({display_name}) - {methods}")
                        
                        if any("embed" in method.lower() for method in methods):
                            print(f"   📝 EMBEDDING: {name} ({display_name})")
                        elif any("generate" in method.lower() for method in methods):
                            print(f"   🤖 GENERATION: {name} ({display_name})")
                else:
                    print(f"❌ REST API failed: {response.status_code}")
                    print(f"   {response.text}")
                    
        except Exception as e:
            print(f"❌ REST API error: {e}")
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        print("Check your GEMINI_API_KEY in .env file")

if __name__ == "__main__":
    asyncio.run(test_models())
