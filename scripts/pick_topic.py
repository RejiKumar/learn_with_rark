#!/usr/bin/env python3
"""Print the path of the next unpublished topic. Exits non-zero when the bank is empty."""
import glob, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
state = os.path.join(ROOT, "state", "published.json")
done = set(json.load(open(state))) if os.path.exists(state) else set()
for p in sorted(glob.glob(os.path.join(ROOT, "topics", "*.json"))):
    if os.path.basename(p)[:-5] not in done:
        print(p); sys.exit(0)
sys.exit("No unpublished topics left. Add more files to topics/.")
