#!/usr/bin/env python3
"""upload.py <upload.json>  -> uploads the video with the YouTube Data API v3.

Secrets (environment): YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN.
YT_PRIVACY: private (default), unlisted or public.
Note: Google keeps uploads from an unaudited API project private whatever this says.
"""
import json, os, sys
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def main(path):
    meta = json.load(open(path, encoding="utf-8"))
    for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"):
        if not os.environ.get(k):
            sys.exit(f"{k} is not set. Add it as a GitHub Actions secret.")
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    creds.refresh(Request())
    yt = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"], "tags": meta.get("tags", []), "categoryId": "28"},
            "status": {"privacyStatus": os.environ.get("YT_PRIVACY", "private"), "selfDeclaredMadeForKids": False}}
    media = MediaFileUpload(meta["video"], mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {int(status.progress() * 100)}%", flush=True)
    print("VIDEO_ID", resp["id"], "privacy", resp["status"]["privacyStatus"])
    open(os.path.join(os.path.dirname(path), "youtube_id.txt"), "w").write(resp["id"])

if __name__ == "__main__":
    main(sys.argv[1])
