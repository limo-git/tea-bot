#!/usr/bin/env python3
"""
Debug script to test context assembler behavior
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from retrieval.context_assembler import assemble_context

def debug_context_assembly():
    """Debug the context assembly with temporal metadata."""
    
    graph_results = [
        {
            "content": "Primary message",
            "timestamp": "2026-03-01T14:00:00Z",
            "author": "limo.ew",
            "channel": "dev-ops",
            "related_discussions": [
                {
                    "content": "Related message from yesterday",
                    "timestamp": "2026-02-28T14:00:00Z",
                    "author": "sidtheitguy",
                    "channel": "dev-ops",
                    "time_gap": 1
                }
            ]
        }
    ]
    
    vector_results = [
        {
            "content": "Vector result",
            "author_name": "quantadude",
            "channel_id": "123456",
            "created_at": "2026-03-01T15:00:00Z",
            "similarity": 0.8
        }
    ]
    
    print("🔍 Debugging Context Assembly")
    print("=" * 40)
    
    print(f"Input graph_results: {len(graph_results)} items")
    for i, item in enumerate(graph_results):
        print(f"  {i+1}. {item}")
    
    print(f"\nInput vector_results: {len(vector_results)} items")
    for i, item in enumerate(vector_results):
        print(f"  {i+1}. {item}")
    
    print("\n🔍 Processing graph results...")
    for i, item in enumerate(graph_results):
        print(f"  Item {i+1}:")
        print(f"    Has 'messages' key: {'messages' in item}")
        print(f"    Has 'content' key: {'content' in item}")
        print(f"    Content value: '{item.get('content', 'NO CONTENT')}'")
        print(f"    Has 'related_discussions': {'related_discussions' in item}")
    
    context = assemble_context(graph_results, vector_results, "temporal_context")
    
    print(f"\nOutput context: {len(context)} items")
    for i, item in enumerate(context):
        print(f"  {i+1}. {item}")
    
    # Check temporal metadata
    temporal_items = [item for item in context if item.get("temporal_context")]
    print(f"\nTemporal items found: {len(temporal_items)}")
    for i, item in enumerate(temporal_items):
        print(f"  {i+1}. {item}")
    
    # Check for related discussions
    related_items = [item for item in context 
                    if item.get("temporal_context", {}).get("context_type") == "related_discussion"]
    print(f"\nRelated discussion items: {len(related_items)}")
    for i, item in enumerate(related_items):
        print(f"  {i+1}. {item}")

if __name__ == "__main__":
    debug_context_assembly()
