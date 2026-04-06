import os
import argparse
from googleapiclient.discovery import build

# API Key loaded from environment variable
API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Basic list of malicious keywords for filtering
# This can be expanded or replaced with an LLM sentiment analysis
MALICIOUS_KEYWORDS = [
    "최악", "쓰레기", "병신", "돌팔이", "돈만", "불친절", "가지마", "망해라", 
    "사기", "바가지", "오진", "의료사고", "불만", "짜증"
]

def get_channel_id(youtube, channel_name):
    """Search for a channel by name and return its ID."""
    request = youtube.search().list(
        q=channel_name,
        type="channel",
        part="id,snippet",
        maxResults=1
    )
    response = request.execute()
    
    if not response.get("items"):
        print(f"Channel '{channel_name}' not found.")
        return None
        
    channel_id = response['items'][0]['id']['channelId']
    channel_title = response['items'][0]['snippet']['title']
    print(f"Found Channel: {channel_title} (ID: {channel_id})")
    return channel_id

def get_channel_videos(youtube, channel_id, max_results=10):
    """Get the latest videos from a channel."""
    # First get the uploads playlist ID
    request = youtube.channels().list(
        id=channel_id,
        part="contentDetails"
    )
    response = request.execute()
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get videos from the uploads playlist
    videos = []
    request = youtube.playlistItems().list(
        playlistId=uploads_playlist_id,
        part="snippet",
        maxResults=max_results
    )
    response = request.execute()
    
    for item in response.get("items", []):
        video_id = item["snippet"]["resourceId"]["videoId"]
        video_title = item["snippet"]["title"]
        videos.append({"id": video_id, "title": video_title})
        
    return videos

def fetch_and_analyze_comments(youtube, video_id, video_title):
    """Fetch comments for a video and identify malicious ones."""
    malicious_comments_found = []
    
    try:
        request = youtube.commentThreads().list(
            videoId=video_id,
            part="snippet",
            maxResults=100,
            textFormat="plainText"
        )
        response = request.execute()
        
        while request is not None:
            for item in response.get("items", []):
                comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                author = item["snippet"]["topLevelComment"]["snippet"]["authorDisplayName"]
                published_at = item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
                
                # Simple keyword-based analysis
                found_keywords = [kw for kw in MALICIOUS_KEYWORDS if kw in comment]
                
                if found_keywords:
                    malicious_comments_found.append({
                        "video_title": video_title,
                        "author": author,
                        "date": published_at,
                        "comment": comment,
                        "keywords_flagged": found_keywords
                    })
            
            # Pagination
            if "nextPageToken" in response:
                request = youtube.commentThreads().list_next(request, response)
                if request:
                    response = request.execute()
            else:
                break
                
    except Exception as e:
         print(f"Error fetching comments for video {video_title}: {e}")
         
    return malicious_comments_found

def generate_report(malicious_comments, channel_name):
    """Format and print the analysis report."""
    print("\n" + "="*50)
    print(f"📊 YouTube Comment Analysis Report: {channel_name}")
    print("="*50)
    
    if not malicious_comments:
        print("✅ No malicious comments detected in the analyzed videos.")
        print("="*50 + "\n")
        return
        
    print(f"⚠️ Warning: Found {len(malicious_comments)} potentially malicious comments!\n")
    
    for i, item in enumerate(malicious_comments, 1):
        print(f"[{i}] Video: {item['video_title']}")
        print(f"    Author: {item['author']} ({item['date']})")
        print(f"    Flagged Keywords: {', '.join(item['keywords_flagged'])}")
        print(f"    Comment: \"{item['comment']}\"")
        print("-" * 50)
        
    print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Analyze YouTube comments for a specific channel.")
    parser.add_argument("--channel", type=str, default="백병원", help="The name of the YouTube channel to analyze")
    parser.add_argument("--videos", type=int, default=5, help="Number of latest videos to analyze")
    args = parser.parse_args()
    
    print(f"🚀 Initializing YouTube Monitor for channel: '{args.channel}'...")
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    
    channel_id = get_channel_id(youtube, args.channel)
    if not channel_id:
        return
        
    print(f"📥 Fetching latest {args.videos} videos...")
    videos = get_channel_videos(youtube, channel_id, max_results=args.videos)
    
    all_malicious_comments = []
    
    print("🔍 Analyzing comments (this might take a moment)...")
    for video in videos:
        # print(f"  - Analyzing: {video['title']}")
        flagged = fetch_and_analyze_comments(youtube, video["id"], video["title"])
        all_malicious_comments.extend(flagged)
        
    generate_report(all_malicious_comments, args.channel)

if __name__ == "__main__":
    main()
