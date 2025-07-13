# Quick Start Guide

Get up and running with the Reddit Persona Generator in 5 minutes!

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
python setup.py
```

### 2. Set Up API Credentials
1. Copy the environment template:
   ```bash
   cp env_example.txt .env
   ```

2. Edit `.env` file with your credentials:
   ```bash
   # Reddit API (get from https://www.reddit.com/prefs/apps)
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USERNAME=your_reddit_username
   REDDIT_PASSWORD=your_reddit_password
   
   # Google Gemini API (get from https://makersuite.google.com/app/apikey)
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### 3. Run the Generator
```bash
python reddit_persona_generator.py
```

When prompted, enter a Reddit profile URL like:
- `https://www.reddit.com/user/kojied/`
- `https://www.reddit.com/user/Hungry-Move-6603/`

## 🎯 Example Usage

### Basic Usage
```python
from reddit_persona_generator import RedditPersonaGenerator

# Initialize
generator = RedditPersonaGenerator()

# Generate persona
filename = generator.generate_persona("https://www.reddit.com/user/kojied/")
print(f"Persona saved to: {filename}")
```

### Custom Analysis
```python
# Analyze more posts/comments
filename = generator.generate_persona(
    reddit_url="https://www.reddit.com/user/kojied/",
    max_posts=100,      # Analyze up to 100 posts
    max_comments=200    # Analyze up to 200 comments
)
```

## 📊 What You'll Get

The tool generates a comprehensive text file containing:

1. **User Information**: Profile stats and account details
2. **Generated Persona**: Detailed personality analysis including:
   - Demographics & Background
   - Personality Traits
   - Interests & Hobbies
   - Communication Style
   - Online Behavior Patterns
   - Values & Beliefs
   - Professional Background
3. **Analysis Data**: Statistical breakdown of activity
4. **Citations**: Specific posts/comments supporting each characteristic

## 🔧 Troubleshooting

### Common Issues

**"Reddit API Error"**
- Verify your Reddit API credentials
- Check if your Reddit account has 2FA enabled
- Ensure your user agent string is unique

**"Google Gemini API Error"**
- Verify your Google Gemini API key
- Check your API usage and credits
- Ensure you have access to Gemini Pro

**"No .env file found"**
```bash
cp env_example.txt .env
# Then edit .env with your actual credentials
```

### Test Your Setup
```bash
python test_example.py
```

### See Demo Output
```bash
python demo_output.py
```

## 📝 API Setup Details

### Reddit API Setup
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Fill in:
   - Name: `RedditPersonaGenerator`
   - Description: `A tool for generating user personas`
   - Redirect URI: `http://localhost:8080`
5. Note the client ID (under app name) and client secret

### Google Gemini API Setup
1. Go to https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy to your `.env` file

## ⚡ Performance Tips

- Start with smaller numbers (10-20 posts/comments) for faster results
- Use lower `temperature` values for more consistent personas
- Monitor API usage to avoid rate limits

## 🎉 You're Ready!

Once set up, you can:
- Generate personas for any Reddit user
- Customize analysis parameters
- Integrate into your own applications
- Use the citation system for research

Happy persona generating! 🚀 