
import sys
from youtube_transcript_api import YouTubeTranscriptApi

try:
    transcript = YouTubeTranscriptApi.get_transcript('Y5pzLHmMobc', languages=['ko', 'en'])
    text = " ".join([t['text'] for t in transcript])
    print(text[:2000]) # First 2000 characters
    print("\n...\n")
    print(text[-2000:]) # Last 2000 characters
except Exception as e:
    print(e)
