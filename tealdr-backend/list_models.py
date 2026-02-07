#!/usr/bin/env python3
"""
Script to list all available Gemini models and their supported methods
"""

import google.genai as genai
from config import Config
import asyncio

async def list_models():
    """List all available models and their capabilities"""
    try:
        client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        print("🔍 Fetching available Gemini models...")
        print("=" * 60)
        
        # Get all models
        models = client.models.list()
        
        embedding_models = []
        generation_models = []
        
        for model in models:
            model_name = model.name
            supported_methods = getattr(model, 'supported_methods', [])
            
            # Check if it supports embedding
            if any(method in ['embedContent', 'batchEmbedContents'] for method in supported_methods):
                embedding_models.append({
                    'name': model_name,
                    'methods': supported_methods,
                    'display_name': getattr(model, 'display_name', 'Unknown')
                })
            
            # Check if it supports generation
            if any(method in ['generateContent', 'streamGenerateContent'] for method in supported_methods):
                generation_models.append({
                    'name': model_name,
                    'methods': supported_methods,
                    'display_name': getattr(model, 'display_name', 'Unknown')
                })
        
        print("\n📝 EMBEDDING MODELS:")
        print("-" * 40)
        for i, model in enumerate(embedding_models, 1):
            print(f"{i}. {model['display_name']}")
            print(f"   Model: {model['name']}")
            print(f"   Methods: {', '.join(model['methods'])}")
            print()
        
        print("\n🤖 GENERATION MODELS:")
        print("-" * 40)
        for i, model in enumerate(generation_models, 1):
            print(f"{i}. {model['display_name']}")
            print(f"   Model: {model['name']}")
            print(f"   Methods: {', '.join(model['methods'])}")
            print()
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        if embedding_models:
            print("✅ For Embeddings:")
            for model in embedding_models[:3]:  # Show top 3
                print(f"   • {model['name']} (supports: {', '.join(model['methods'])})")
        
        if generation_models:
            print("\n✅ For Generation:")
            for model in generation_models[:3]:  # Show top 3
                print(f"   • {model['name']} (supports: {', '.join(model['methods'])})")
        
        # Best choices
        print("\n🎯 BEST CHOICES:")
        print("-" * 40)
        
        # Find best embedding model
        best_embedding = None
        for model in embedding_models:
            if 'text-embedding' in model['name'].lower():
                best_embedding = model
                break
        
        if best_embedding:
            print(f"📊 Best Embedding: {best_embedding['name']}")
        
        # Find best generation model
        best_generation = None
        for model in generation_models:
            if 'gemini-3' in model['name'].lower() or 'gemini-2' in model['name'].lower():
                best_generation = model
                break
        
        if best_generation:
            print(f"🤖 Best Generation: {best_generation['name']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your GEMINI_API_KEY is valid")

if __name__ == "__main__":
    asyncio.run(list_models())
