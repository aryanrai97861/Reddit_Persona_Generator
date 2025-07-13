#!/usr/bin/env python3
"""
Test script for Reddit Persona Generator
This script demonstrates how to use the persona generator with example data.
"""

import os
import json
from datetime import datetime
from reddit_persona_generator import RedditPersonaGenerator

def create_mock_data():
    """Create mock Reddit data for testing when API is not available."""
    return {
        'user_info': {
            'username': 'test_user',
            'created_utc': 1600000000,  # 2020-09-13
            'comment_karma': 5000,
            'link_karma': 2000,
            'is_gold': False,
            'is_mod': False,
            'has_verified_email': True
        },
        'posts': [
            {
                'id': 'post1',
                'title': 'My experience with Python async programming',
                'selftext': 'I recently started learning async programming in Python and wanted to share my journey. The asyncio library has been a game-changer for my web scraping projects.',
                'subreddit': 'programming',
                'score': 127,
                'upvote_ratio': 0.95,
                'num_comments': 45,
                'created_utc': 1700000000,
                'url': 'https://example.com',
                'permalink': '/r/programming/comments/post1',
                'is_self': True,
                'type': 'post'
            },
            {
                'id': 'post2',
                'title': 'Best practices for machine learning projects',
                'selftext': 'After working on several ML projects, here are the key lessons I learned about data preprocessing, model selection, and deployment.',
                'subreddit': 'MachineLearning',
                'score': 89,
                'upvote_ratio': 0.92,
                'num_comments': 32,
                'created_utc': 1699000000,
                'url': 'https://example.com',
                'permalink': '/r/MachineLearning/comments/post2',
                'is_self': True,
                'type': 'post'
            }
        ],
        'comments': [
            {
                'id': 'comment1',
                'body': 'Great question! I think the key is to start with simple models and gradually increase complexity. Also, make sure to validate your assumptions.',
                'subreddit': 'datascience',
                'score': 15,
                'created_utc': 1698000000,
                'permalink': '/r/datascience/comments/comment1',
                'parent_id': 'parent1',
                'type': 'comment'
            },
            {
                'id': 'comment2',
                'body': 'I completely agree with your analysis. The documentation could definitely be improved. Have you tried looking at the GitHub issues?',
                'subreddit': 'programming',
                'score': 8,
                'created_utc': 1697000000,
                'permalink': '/r/programming/comments/comment2',
                'parent_id': 'parent2',
                'type': 'comment'
            }
        ]
    }

def test_persona_generation():
    """Test the persona generation functionality."""
    print("🧪 Testing Reddit Persona Generator")
    print("=" * 50)
    
    try:
        # Initialize generator
        generator = RedditPersonaGenerator()
        print("✅ Generator initialized successfully")
        
        # Test with a real Reddit URL
        test_url = "https://www.reddit.com/user/kojied/"
        print(f"\n🔍 Testing with URL: {test_url}")
        
        # Generate persona
        filename = generator.generate_persona(test_url, max_posts=10, max_comments=20)
        print(f"✅ Persona generated successfully: {filename}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        print("\n📝 This might be due to missing API credentials.")
        print("Please ensure you have set up your .env file with valid API keys.")
        
        # Show mock data example
        print("\n" + "=" * 50)
        print("📋 Example Mock Data Structure:")
        print("=" * 50)
        
        mock_data = create_mock_data()
        print(json.dumps(mock_data, indent=2, default=str))

def test_analysis_functions():
    """Test individual analysis functions."""
    print("\n🔬 Testing Analysis Functions")
    print("=" * 50)
    
    try:
        generator = RedditPersonaGenerator()
        
        # Test text analysis
        test_texts = [
            "I love programming in Python and machine learning",
            "The async programming features are amazing",
            "Data science projects require careful planning"
        ]
        
        topics = generator.extract_topics_and_interests(test_texts)
        print(f"✅ Topic extraction: {topics['top_words'][:5]}")
        
        # Test sentiment analysis
        sentiment = generator.analyze_text_sentiment("I'm really excited about this new technology!")
        print(f"✅ Sentiment analysis: {sentiment}")
        
    except Exception as e:
        print(f"❌ Error in analysis functions: {e}")

def main():
    """Main test function."""
    print("🚀 Reddit Persona Generator - Test Suite")
    print("=" * 60)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found!")
        print("Please create a .env file with your API credentials:")
        print("   cp env_example.txt .env")
        print("   # Then edit .env with your actual API keys")
        print()
    
    # Run tests
    test_analysis_functions()
    test_persona_generation()
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("\nNext steps:")
    print("1. Set up your API credentials in .env file")
    print("2. Run: python reddit_persona_generator.py")
    print("3. Enter a Reddit profile URL when prompted")

if __name__ == "__main__":
    main() 