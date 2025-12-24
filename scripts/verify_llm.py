#!/usr/bin/env python3
"""
LLM Verification Script
Tests the LLM connection and configuration.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from backend.llm_client import LLMClient

def test_llm_connection():
    """Test basic LLM connectivity."""
    print("=" * 60)
    print("LLM Configuration Verification")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   Base URL: {config.LLM_BASE_URL}")
    print(f"   Model: {config.LLM_MODEL}")
    print(f"   API Key: {'*' * len(config.LLM_API_KEY)}")
    
    print(f"\n🔌 Testing connection to LLM...")
    
    try:
        client = LLMClient()
        
        # Test 1: Simple completion
        print(f"\n✓ LLM client initialized")
        
        # Test 2: Generate a response
        print(f"\n🧪 Test: Generating sample response...")
        test_messages = [
            {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
        ]
        
        response = client.get_waiter_response(test_messages, "")
        
        if response:
            print(f"✓ Response received: {response[:100]}...")
            print(f"\n✅ LLM is working correctly!")
            return True
        else:
            print(f"❌ No response received")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   1. Check if Ollama is running: curl http://localhost:11434/api/tags")
        print(f"   2. Verify model is installed: ollama list")
        print(f"   3. Pull model if needed: ollama pull {config.LLM_MODEL}")
        return False

if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)
