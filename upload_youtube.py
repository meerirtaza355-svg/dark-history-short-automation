import base64, json, os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = Path(__file__).resolve().parent
secret = os.environ.get("YOUTUBE_TOKEN_B64", "")
if not secret:
    raise SystemExit("Missing YOUTUBE_TOKEN_B64 GitHub secret")
info = json.loads(base64.b64decode(secret).decode("utf-8"))
creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/youtube.upload"])
if creds.expired and creds.refresh_token:
    creds.refresh(Request())
if not creds.valid:
    raise SystemExit("YouTube credentials are not valid. Re-run authorize_youtube.py and update the GitHub secret.")
metadata = json.loads((ROOT / "output" / "metadata.json").read_text(encoding="utf-8"))
youtube = build("youtube", "v3", credentials=creds)
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {"title": metadata["title"], "description": metadata["description"], "categoryId": "27", "defaultLanguage": "en"},
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}
    },
    media_body=MediaFileUpload(str(ROOT / "output" / "dark_history_short.mp4"), mimetype="video/mp4", resumable=True)
)
response = request.execute()
print("Uploaded video ID:", response.get("id"), "Privacy: private")
