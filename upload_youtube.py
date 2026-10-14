import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video():
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    # Simple token.json file se credentials load karna
    if not os.path.exists('token.json'):
        raise FileNotFoundError("token.json file nahi mili!")

    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    youtube = build('youtube', 'v3', credentials=creds)

    body = {
        'snippet': {
            'title': 'Dark History Short #1',
            'description': 'Automated Dark History Short Video',
            'tags': ['Shorts', 'History', 'DarkHistory'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'private', # Pehle test ke liye private rakha hai
            'selfDeclaredMadeForKids': False
        }
    }

    # Video file upload
    media = MediaFileUpload('output.mp4', chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = request.execute()
    print(f"Video successfully upload ho gayi! Video ID: {response.get('id')}")

if __name__ == '__main__':
    upload_video()
