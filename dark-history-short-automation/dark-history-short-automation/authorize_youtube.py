"""Run locally once to create token.json. Requires client_secret.json from Google Cloud OAuth Desktop app."""
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
with open("token.json", "w", encoding="utf-8") as f:
    f.write(creds.to_json())
print("Created token.json. Keep it private; never commit it to GitHub.")
