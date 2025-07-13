#!/usr/bin/env python3
"""
Simple test for Gemini API
"""
import google.generativeai as genai

# Your API key
API_KEY = "GEMINI_API_KEY"  # Replace with your actual API key

try:
    print("Testing Gemini API...")
    genai.configure(api_key=API_KEY)
    
    # Try to list models first
    print("Available models:")
    models = list(genai.list_models())
    for model in models:
        print(f"  - {model.name}")
    
    # Test generation
    print("\nTesting generation...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Say hello")
    
    print(f"Response: {response.text}")
    print("✅ Success!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if your API key has billing enabled")
    print("2. Try creating a new API key at https://aistudio.google.com/")
    print("3. Make sure you're in a supported region")