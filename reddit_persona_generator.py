#!/usr/bin/env python3
"""
Reddit User Persona Generator
A tool to analyze Reddit user profiles and generate detailed personas based on their posts and comments.
"""
import google.generativeai as genai
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import praw
from dotenv import load_dotenv
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditPersonaGenerator:
    def __init__(self):
        """Initialize the Reddit Persona Generator with API credentials."""
        self.reddit = self._initialize_reddit()
        self.gemini_client = self._initialize_gemini()
        self.user_data = {}
        self.citations = {}
        
    def _initialize_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client."""
        try:
            reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'RedditPersonaGenerator/1.0'),
                username=os.getenv('REDDIT_USERNAME'),
                password=os.getenv('REDDIT_PASSWORD')
            )
            logger.info("Reddit API initialized successfully")
            return reddit
        except Exception as e:
            logger.error(f"Failed to initialize Reddit API: {e}")
            raise
    
    def _initialize_gemini(self):
        """Initialize Gemini (Google Generative AI) client."""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            logger.info(f"Initializing Gemini API with key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
            genai.configure(api_key=api_key)
            
            # Use the correct model name for Gemini 1.5 Flash
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            # Test the model with a simple prompt
            logger.info("Testing Gemini API connection...")
            test_response = model.generate_content("Test connection")
            if test_response and test_response.text:
                logger.info("Gemini API initialized successfully")
                return model
            else:
                raise ValueError("Gemini API responded but with empty content")
                
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            logger.error(f"Available models: {[m.name for m in genai.list_models()]}")
            raise
    
    def extract_username_from_url(self, url: str) -> str:
        """Extract username from Reddit profile URL."""
        try:
            # Handle different URL formats
            url = url.strip()
            if url.startswith('u/') or url.startswith('/u/'):
                return url.split('/')[-1]
            elif url.startswith('reddit.com/u/') or url.startswith('reddit.com/user/'):
                return url.split('/')[-1]
            elif 'reddit.com' in url:
                parsed = urlparse(url)
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) >= 2 and path_parts[0] in ['user', 'u']:
                    return path_parts[1]
                else:
                    raise ValueError("Invalid Reddit profile URL format")
            else:
                # Assume it's just a username
                return url.replace('u/', '').replace('/u/', '')
        except Exception as e:
            logger.error(f"Error extracting username from URL: {e}")
            raise
    
    def collect_user_data(self, username: str, max_posts: int = 50, max_comments: int = 100) -> Dict:
        """Collect user data including posts and comments."""
        logger.info(f"Collecting data for user: {username}")
        
        try:
            redditor = self.reddit.redditor(username)
            
            # Check if user exists
            try:
                redditor.id
            except Exception as e:
                logger.error(f"User {username} not found or is suspended")
                raise ValueError(f"User {username} not found or is suspended")
            
            # Collect basic user info
            user_info = {
                'username': username,
                'created_utc': redditor.created_utc,
                'comment_karma': getattr(redditor, 'comment_karma', 0),
                'link_karma': getattr(redditor, 'link_karma', 0),
                'is_gold': getattr(redditor, 'is_gold', False),
                'is_mod': getattr(redditor, 'is_mod', False),
                'has_verified_email': getattr(redditor, 'has_verified_email', False)
            }
            
            # Collect posts
            posts = []
            post_count = 0
            logger.info(f"Collecting posts for {username}...")
            for submission in redditor.submissions.new(limit=max_posts):
                try:
                    post_data = {
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'upvote_ratio': getattr(submission, 'upvote_ratio', 0),
                        'num_comments': submission.num_comments,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'permalink': submission.permalink,
                        'is_self': submission.is_self,
                        'type': 'post'
                    }
                    posts.append(post_data)
                    post_count += 1
                    if post_count >= max_posts:
                        break
                except Exception as e:
                    logger.warning(f"Error collecting post {submission.id}: {e}")
                    continue
            
            # Collect comments
            comments = []
            comment_count = 0
            logger.info(f"Collecting comments for {username}...")
            for comment in redditor.comments.new(limit=max_comments):
                try:
                    comment_data = {
                        'id': comment.id,
                        'body': comment.body,
                        'subreddit': comment.subreddit.display_name,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'permalink': comment.permalink,
                        'parent_id': comment.parent_id,
                        'type': 'comment'
                    }
                    comments.append(comment_data)
                    comment_count += 1
                    if comment_count >= max_comments:
                        break
                except Exception as e:
                    logger.warning(f"Error collecting comment {comment.id}: {e}")
                    continue
            
            self.user_data = {
                'user_info': user_info,
                'posts': posts,
                'comments': comments
            }
            
            logger.info(f"Collected {len(posts)} posts and {len(comments)} comments for {username}")
            return self.user_data
            
        except Exception as e:
            logger.error(f"Error collecting user data: {e}")
            raise
    
    def analyze_text_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text using TextBlob."""
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {e}")
            return {'polarity': 0, 'subjectivity': 0}
    
    def extract_topics_and_interests(self, texts: List[str]) -> Dict:
        """Extract topics and interests from text data."""
        try:
            # Combine all texts
            combined_text = ' '.join(texts)
            
            # Remove stopwords and tokenize
            stop_words = set(stopwords.words('english'))
            words = word_tokenize(combined_text.lower())
            words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 3]
            
            # Count word frequencies
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top words
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            
            return {
                'top_words': top_words,
                'total_words': len(words),
                'unique_words': len(word_freq)
            }
        except Exception as e:
            logger.warning(f"Error extracting topics: {e}")
            return {'top_words': [], 'total_words': 0, 'unique_words': 0}
    
    def analyze_user_activity_patterns(self) -> Dict:
        """Analyze user activity patterns."""
        try:
            posts = self.user_data.get('posts', [])
            comments = self.user_data.get('comments', [])
            
            # Analyze posting frequency
            if posts:
                post_times = [post['created_utc'] for post in posts]
                post_times.sort()
                time_diffs = [post_times[i+1] - post_times[i] for i in range(len(post_times)-1)]
                avg_time_between_posts = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            else:
                avg_time_between_posts = 0
            
            # Analyze subreddit preferences
            subreddit_counts = {}
            for post in posts:
                subreddit = post['subreddit']
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            for comment in comments:
                subreddit = comment['subreddit']
                subreddit_counts[subreddit] = subreddit_counts.get(subreddit, 0) + 1
            
            top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'avg_time_between_posts': avg_time_between_posts,
                'top_subreddits': top_subreddits,
                'total_subreddits': len(subreddit_counts),
                'post_count': len(posts),
                'comment_count': len(comments)
            }
        except Exception as e:
            logger.warning(f"Error analyzing activity patterns: {e}")
            return {}
    
    def generate_persona_with_llm(self, analysis_data: Dict) -> Tuple[str, Dict]:
        """Generate user persona using Gemini 1.5 Flash."""
        try:
            # Prepare context for LLM
            posts_text = '\n'.join([f"Post: {post['title']} - {post['selftext'][:200]}..." 
                                   for post in self.user_data.get('posts', [])[:10]])
            comments_text = '\n'.join([f"Comment: {comment['body'][:200]}..." 
                                     for comment in self.user_data.get('comments', [])[:20]])
            
            prompt = f"""
            Based on the following Reddit user data, create a detailed user persona in the following format:

================================================================================
USERNAME: <Reddit username>
================================================================================
AGE: <inferred or blank>
OCCUPATION: <inferred or blank>
STATUS: <inferred or blank>
LOCATION: <inferred or blank>
TIER: <inferred or blank>
ARCHETYPE: <inferred or blank>

[Practical] [Adaptable] [Spontaneous] [Active]  # Use traits inferred from posts/comments

------------------------------------------------------------------------------
"<A short, first-person quote that summarizes the user’s main motivation or pain point.>"
------------------------------------------------------------------------------

MOTIVATIONS (rate each 1-5, cite a post/comment for each)
Convenience:     <1-5>   (Cited from: "<excerpt>" - <link>)
Wellness:        <1-5>   (Cited from: "<excerpt>" - <link>)
Speed:           <1-5>   (Cited from: "<excerpt>" - <link>)
Preferences:     <1-5>   (Cited from: "<excerpt>" - <link>)
Comfort:         <1-5>   (Cited from: "<excerpt>" - <link>)
Dietary Needs:   <1-5>   (Cited from: "<excerpt>" - <link>)

PERSONALITY (rate each 1-5, cite a post/comment for each)
Introvert(1) - Extrovert(5): <1-5>   (Cited from: "<excerpt>" - <link>)
Intuition(1) - Sensing(5): <1-5>     (Cited from: "<excerpt>" - <link>)
Feeling(1) - Thinking(5): <1-5>      (Cited from: "<excerpt>" - <link>)
Perceiving(1) - Judging(5): <1-5>    (Cited from: "<excerpt>" - <link>)

------------------------------------------------------------------------------
BEHAVIOUR & HABITS
- <Bullet point 1> (Cited from: "<excerpt>" - <link>)
- <Bullet point 2> (Cited from: "<excerpt>" - <link>)
...

------------------------------------------------------------------------------
FRUSTRATIONS
- <Bullet point 1> (Cited from: "<excerpt>" - <link>)
- <Bullet point 2> (Cited from: "<excerpt>" - <link>)
...

------------------------------------------------------------------------------
GOALS & NEEDS
- <Bullet point 1> (Cited from: "<excerpt>" - <link>)
- <Bullet point 2> (Cited from: "<excerpt>" - <link>)
...

For each field, infer from Reddit data if possible, otherwise leave blank. For every motivation, personality trait, habit, frustration, and goal, cite the specific Reddit post or comment (with a short excerpt and a direct link). Use the provided Reddit data below:

User Info:
- Username: {self.user_data['user_info']['username']}
- Account Age: {datetime.fromtimestamp(self.user_data['user_info']['created_utc']).strftime('%Y-%m-%d')}
- Karma: {self.user_data['user_info']['comment_karma']} comment, {self.user_data['user_info']['link_karma']} post

Activity Analysis:
- Posts: {analysis_data.get('post_count', 0)}
- Comments: {analysis_data.get('comment_count', 0)}
- Top Subreddits: {', '.join([sub[0] for sub in analysis_data.get('top_subreddits', [])[:5]])}
- Top Interests: {', '.join([word[0] for word in analysis_data.get('top_words', [])[:10]])}

Sample Posts:
{posts_text}

Sample Comments:
{comments_text}

Format the response exactly as above, with clear section headers, 1-5 scales, and citations for each characteristic."""
            
            # Generate content with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Generating persona with Gemini 1.5 Flash (attempt {attempt + 1})")
                    
                    # Configure generation parameters
                    generation_config = genai.types.GenerationConfig(
                        temperature=0.7,
                        top_p=0.8,
                        top_k=40,
                        max_output_tokens=4096,
                    )
                    
                    response = self.gemini_client.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    
                    if response and response.text:
                        persona_text = response.text
                        logger.info("Persona generated successfully")
                        break
                    else:
                        logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                        if attempt == max_retries - 1:
                            raise ValueError("Gemini returned empty response after all retries")
                        time.sleep(2)  # Wait before retry
                        
                except Exception as e:
                    logger.warning(f"Gemini generation attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)  # Wait before retry
            
            # Generate citations
            citations = self._generate_citations()
            
            return persona_text, citations
            
        except Exception as e:
            logger.error(f"Error generating persona with LLM: {e}")
            raise
    
    def _generate_citations(self) -> Dict:
        """Generate citations for persona characteristics."""
        citations = {
            'personality_traits': [],
            'interests': [],
            'communication_style': [],
            'behavior_patterns': [],
            'values_beliefs': []
        }
        
        # Add citations based on posts and comments
        for post in self.user_data.get('posts', []):
            if post['score'] > 10:  # High-scoring posts
                citations['interests'].append({
                    'type': 'post',
                    'content': post['title'][:100] + "...",
                    'url': f"https://reddit.com{post['permalink']}",
                    'score': post['score']
                })
        
        for comment in self.user_data.get('comments', []):
            if comment['score'] > 5:  # High-scoring comments
                citations['communication_style'].append({
                    'type': 'comment',
                    'content': comment['body'][:100] + "...",
                    'url': f"https://reddit.com{comment['permalink']}",
                    'score': comment['score']
                })
        
        return citations
    
    def save_persona_to_file(self, username: str, persona_text: str, citations: Dict, analysis_data: Dict):
        """Save the generated persona to a text file."""
        try:
            filename = f"persona_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"REDDIT USER PERSONA ANALYSIS\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Username: {username}\n")
                f.write(f"Account Created: {datetime.fromtimestamp(self.user_data['user_info']['created_utc']).strftime('%Y-%m-%d')}\n")
                f.write(f"Total Karma: {self.user_data['user_info']['comment_karma'] + self.user_data['user_info']['link_karma']}\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("USER PERSONA\n")
                f.write("=" * 80 + "\n\n")
                f.write(persona_text)
                f.write("\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("ANALYSIS DATA\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("Activity Summary:\n")
                f.write(f"- Total Posts Analyzed: {analysis_data.get('post_count', 0)}\n")
                f.write(f"- Total Comments Analyzed: {analysis_data.get('comment_count', 0)}\n")
                f.write(f"- Subreddits Active In: {analysis_data.get('total_subreddits', 0)}\n\n")
                
                f.write("Top Subreddits:\n")
                for subreddit, count in analysis_data.get('top_subreddits', [])[:10]:
                    f.write(f"- r/{subreddit}: {count} interactions\n")
                f.write("\n")
                
                f.write("Top Interests (Keywords):\n")
                for word, count in analysis_data.get('top_words', [])[:15]:
                    f.write(f"- {word}: {count} mentions\n")
                f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("CITATIONS\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("High-Scoring Posts (Interest Indicators):\n")
                for citation in citations.get('interests', [])[:5]:
                    f.write(f"- {citation['content']}\n")
                    f.write(f"  URL: {citation['url']} (Score: {citation['score']})\n\n")
                
                f.write("High-Scoring Comments (Communication Style):\n")
                for citation in citations.get('communication_style', [])[:5]:
                    f.write(f"- {citation['content']}\n")
                    f.write(f"  URL: {citation['url']} (Score: {citation['score']})\n\n")
            
            logger.info(f"Persona saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving persona to file: {e}")
            raise
    
    def generate_persona(self, reddit_url: str, max_posts: int = 50, max_comments: int = 100) -> str:
        """Main method to generate persona from Reddit URL."""
        try:
            # Extract username from URL
            username = self.extract_username_from_url(reddit_url)
            logger.info(f"Processing user: {username}")
            
            # Collect user data
            self.collect_user_data(username, max_posts, max_comments)
            
            # Analyze data
            all_texts = []
            for post in self.user_data.get('posts', []):
                all_texts.append(post['title'])
                if post['selftext']:
                    all_texts.append(post['selftext'])
            
            for comment in self.user_data.get('comments', []):
                all_texts.append(comment['body'])
            
            # Perform analysis
            topics_analysis = self.extract_topics_and_interests(all_texts)
            activity_analysis = self.analyze_user_activity_patterns()
            
            analysis_data = {**topics_analysis, **activity_analysis}
            
            # Generate persona with LLM
            persona_text, citations = self.generate_persona_with_llm(analysis_data)
            
            # Save to file
            filename = self.save_persona_to_file(username, persona_text, citations, analysis_data)
            
            logger.info(f"Persona generation completed successfully. Saved to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error in persona generation: {e}")
            raise

def main():
    """Main function to run the persona generator."""
    print("Reddit User Persona Generator")
    print("=" * 50)
    
    # Check for required environment variables
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'GEMINI_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file with the following variables:")
        print("REDDIT_CLIENT_ID=your_reddit_client_id")
        print("REDDIT_CLIENT_SECRET=your_reddit_client_secret")
        print("REDDIT_USERNAME=your_reddit_username")
        print("REDDIT_PASSWORD=your_reddit_password")
        print("REDDIT_USER_AGENT=RedditPersonaGenerator/1.0")
        print("GEMINI_API_KEY=your_gemini_api_key")
        return
    
    try:
        # Initialize generator
        generator = RedditPersonaGenerator()
        
        # Get user input
        reddit_url = input("Enter Reddit profile URL or username: ").strip()
        
        if not reddit_url:
            print("Error: Please provide a Reddit profile URL or username")
            return
        
        # Generate persona
        print("\nGenerating persona... This may take a few minutes.")
        filename = generator.generate_persona(reddit_url)
        
        print(f"\n✅ Persona generated successfully!")
        print(f"📄 Output saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"Application error: {e}")

if __name__ == "__main__":
    main()