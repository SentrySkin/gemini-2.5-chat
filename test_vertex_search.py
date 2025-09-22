#!/usr/bin/env python3
"""
Simple test script to validate Vertex Search Engine integration
"""

import os
import sys
from main import smart_retrieve_from_search, VERTEX_SEARCH_ENGINE

def test_vertex_search():
    """Test the Vertex Search Engine integration"""
    print("Testing Vertex Search Engine integration...")
    print(f"Search Engine: {VERTEX_SEARCH_ENGINE}")
    
    # Test query
    test_query = "esthetic program courses schedule"
    conversation_stage = "active"
    
    try:
        print(f"\nTesting with query: '{test_query}'")
        snippets, sources = smart_retrieve_from_search(test_query, conversation_stage)
        
        print(f"\nResults:")
        print(f"Number of snippets: {len(snippets)}")
        print(f"Number of sources: {len(sources)}")
        
        for i, snippet in enumerate(snippets):
            print(f"\nSnippet {i+1}: {snippet[:100]}...")
            
        for i, source in enumerate(sources):
            print(f"\nSource {i+1}: {source}")
            
        print("\n✅ Vertex Search Engine integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    # Set up environment if needed
    if not os.getenv("GCP_PROJECT"):
        os.environ["GCP_PROJECT"] = "christinevalmy"
    
    success = test_vertex_search()
    sys.exit(0 if success else 1)
