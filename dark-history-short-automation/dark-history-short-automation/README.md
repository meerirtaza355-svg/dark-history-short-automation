# Dark History Shorts — zero-budget starter

This starter creates a vertical 30–60 second video using locally generated title cards and offline English text-to-speech, then uploads it to YouTube as **private** via the YouTube Data API. It does not use paid stock footage or paid AI video generation.

## Important limitations
- This first version uses the hand-written `story.json` story, not AI-generated scripts. Add Gemini API later only if its current free tier suits you; quotas and availability can change.
- Visuals are text cards, not cinematic footage. Replace them only with assets you own or have permission to use.
- Unverified YouTube API projects may be forced to upload private videos until the project passes Google's required audit.
- OAuth consent screen in Testing mode may cause refresh tokens to expire after 7 days. If uploads stop, reauthorize and update the GitHub secret. Google consent configuration/verification may be needed for longer-term automation.
- GitHub Actions is scheduled job hosting, not an always-on 24/7 server. Scheduled jobs can be delayed; public repository standard runners are generally free, subject to GitHub policies.
- Check historical claims before publishing. This starter's example is educational and should be fact-checked.

## A. Make a YouTube API OAuth token on your laptop
1. Create a Google Cloud project at https://console.cloud.google.com/ .
2. Enable **YouTube Data API v3**.
3. Configure OAuth consent screen. If asked for audience, choose External for a personal Gmail account, and add your Google account as a test user if using Testing mode.
4. Create OAuth client credentials of type **Desktop app** and download the JSON file. Rename it `client_secret.json` and put it in this project folder.
5. Install Python 3.11+ and FFmpeg on your laptop; then open Terminal/Command Prompt in this folder.
6. Run:
   ```
   pip install -r requirements.txt
   python authorize_youtube.py
   ```
   A browser opens; sign into the channel-owning Google account and approve YouTube upload access. This creates `token.json`.
7. Convert token.json to one line of Base64. On Windows PowerShell:
   ```powershell
   [Convert]::ToBase64String([IO.File]::ReadAllBytes("token.json")) | Set-Clipboard
   ```
   On macOS/Linux:
   ```bash
   base64 -w 0 token.json
   ```
   Copy the output securely. Do not share it or commit it to the repository.

## B. Create the GitHub repository
1. Create a **public** repository at https://github.com/new (public standard Actions runners are the easiest free route; remember the code will be visible).
2. Upload the project files/folders to the repository. Do not upload `client_secret.json`, `token.json`, or `output/`.
3. Open repository **Settings → Secrets and variables → Actions → New repository secret**.
4. Secret name: `YOUTUBE_TOKEN_B64`. Value: the Base64 string copied above. Save.
5. Open **Actions** tab and enable workflows if prompted.
6. Select **Build and upload Dark History Short → Run workflow** to test it. Check the run logs and then YouTube Studio → Content; the upload should be private.
7. If the test succeeds, the workflow is scheduled for 19:00 Pakistan time daily (14:00 UTC). GitHub schedule may not start at the exact minute.

## C. Change the story
Edit `story.json` with your own researched title, description, six short scene captions, and narration. Keep narration under 59 seconds. Commit the change. The workflow will use the updated story on its next run.

## D. Security
Never commit OAuth JSON/token files or paste them into chat. If a token leaks, revoke it in your Google Account security settings and create a new one.
