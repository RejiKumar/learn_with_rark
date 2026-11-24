#!/usr/bin/env python3
"""upload_instagram.py <upload.json>  -> publishes the video as an Instagram Reel.

Secrets (environment): IG_USER_ID (the Instagram professional account's id) and IG_ACCESS_TOKEN.
Optional: IG_GRAPH_VERSION (default v23.0), IG_HOST (default graph.facebook.com; use graph.instagram.com
for a token made with "Instagram API with Instagram Login").
Uses the resumable upload, so the video does not need a public URL.
If the secrets are missing it prints a note and exits 0, so it never blocks the YouTube upload.
"""
import json, os, sys, time
import requests

def main(path):
    uid, token = os.environ.get("IG_USER_ID"), os.environ.get("IG_ACCESS_TOKEN")
    if not uid or not token:
        print("Instagram skipped: IG_USER_ID / IG_ACCESS_TOKEN are not set."); return
    meta = json.load(open(path, encoding="utf-8"))
    host = os.environ.get("IG_HOST", "graph.facebook.com")
    base = f"https://{host}/{os.environ.get('IG_GRAPH_VERSION', 'v23.0')}"
    caption = (meta["title"] + "\n\n" + meta["description"])[:2200]
    video = meta["video"]; size = os.path.getsize(video)

    r = requests.post(f"{base}/{uid}/media", data={"media_type": "REELS", "upload_type": "resumable", "caption": caption,
                                                   "share_to_feed": "true", "access_token": token}, timeout=60)
    if r.status_code >= 400: sys.exit(f"Instagram: could not create the container: {r.text}")
    c = r.json(); cid, uri = c["id"], c["uri"]

    with open(video, "rb") as f:
        up = requests.post(uri, headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(size)}, data=f, timeout=600)
    if up.status_code >= 400: sys.exit(f"Instagram: upload failed: {up.text}")

    for _ in range(60):  # wait up to ~10 minutes for processing
        s = requests.get(f"{base}/{cid}", params={"fields": "status_code,status", "access_token": token}, timeout=60).json()
        code = s.get("status_code")
        print("instagram status:", code, flush=True)
        if code == "FINISHED": break
        if code in ("ERROR", "EXPIRED"): sys.exit(f"Instagram processing failed: {s}")
        time.sleep(10)
    else:
        sys.exit("Instagram: processing timed out")

    pub = requests.post(f"{base}/{uid}/media_publish", data={"creation_id": cid, "access_token": token}, timeout=60)
    if pub.status_code >= 400: sys.exit(f"Instagram: publish failed: {pub.text}")
    print("INSTAGRAM_MEDIA_ID", pub.json().get("id"))

if __name__ == "__main__":
    main(sys.argv[1])
