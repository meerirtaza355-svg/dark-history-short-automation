import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video():
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    if not os.path.exists('token.json'):
        raise FileNotFoundError("token.json file nahi mili!")

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    youtube = build('youtube', 'v3', credentials=creds)

    # Read title and description from story.json
    title = "Dark History Short"
    description = "Automated Dark History Short Video"
    tags = ["Shorts", "History", "DarkHistory"]

    if os.path.exists('story.json'):
        with open('story.json', 'r', encoding='utf-8') as f:
            story = json.load(f)
            title = story.get('title', title)
            description = story.get('description', description)
            tags = story.get('tags', tags)

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private',
            'selfDeclaredMadeForKids': False
        }
    }

    media = MediaFileUpload('output/dark_history_short.mp4', chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = request.execute()
    print(f"Video successfully upload ho gayi! Video ID: {response.get('id')}")

if __name__ == '__main__':
    upload_video()
