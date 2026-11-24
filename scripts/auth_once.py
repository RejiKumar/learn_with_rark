#!/usr/bin/env python3
"""Run ONCE on your own computer to get a YouTube refresh token.

1. In Google Cloud Console: create a project, enable "YouTube Data API v3",
   configure the OAuth consent screen, and create an OAuth client of type "Desktop app".
   Download its JSON as client_secret.json next to this file.
2. pip install google-auth-oauthlib
3. python auth_once.py
4. Sign in with the Google account that owns the RARK channel and approve.
5. Copy the three printed values into GitHub: Settings > Secrets and variables > Actions.
   Never paste them into chat or commit them.
"""
import json
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", scopes=["https://www.googleapis.com/auth/youtube.upload"])
creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
cfg = json.load(open("client_secret.json"))["installed"]
print("\nYT_CLIENT_ID     =", cfg["client_id"])
print("YT_CLIENT_SECRET =", cfg["client_secret"])
print("YT_REFRESH_TOKEN =", creds.refresh_token)
