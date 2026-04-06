from youtube_transcript_api import YouTubeTranscriptApi
import sys
try:
    transcript = YouTubeTranscriptApi.get_transcript('nldkPgp3aIA', languages=['ko', 'en'])
    for x in transcript:
         print(x['text'])
except Exception as e:
    print(e)
