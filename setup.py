#!/usr/bin/env python3
"""
Setup script for Reddit Persona Generator
Helps users install dependencies and configure the project.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    if env_example.exists():
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual API credentials")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ env_example.txt not found")
        return False

def download_nltk_data():
    """Download required NLTK data."""
    print("\n📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    print("\n🔍 Testing imports...")
    required_modules = [
        'praw',
        'google.generativeai',
        'dotenv',
        'textblob',
        'nltk'
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n⚠️  Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def main():
    """Main setup function."""
    print("🚀 Reddit Persona Generator - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Download NLTK data
    if not download_nltk_data():
        return
    
    # Create .env file
    if not create_env_file():
        return
    
    # Test imports
    if not test_imports():
        return
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API credentials:")
    print("   - REDDIT_CLIENT_ID")
    print("   - REDDIT_CLIENT_SECRET")
    print("   - REDDIT_USERNAME")
    print("   - REDDIT_PASSWORD")
    print("   - GEMINI_API_KEY")
    print("\n2. Run the generator:")
    print("   python reddit_persona_generator.py")
    print("\n3. Or run tests:")
    print("   python test_example.py")

if __name__ == "__main__":
    main() 