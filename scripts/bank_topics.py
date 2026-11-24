#!/usr/bin/env python3
"""Fallback topic source used when ANTHROPIC_API_KEY is not set.

Reads topics/bank.txt (a plain-text list of ready-written topics) and writes the next ones that
do not exist yet as topics/<id>.json, so the daily run keeps going without an API key.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANK = os.path.join(ROOT, "topics", "bank.txt")
SUFFIX = "\n\nMade with AI tools. New tech Shorts every day on RARK.\n#Shorts #TechTips #RARK"


def parse_visual(spec):
    kind, _, rest = spec.strip().partition(" ")
    rest = rest.strip()
    if kind in ("bulb", "door", "padlock"):
        return {"type": kind}
    if kind == "sign":
        return {"type": "sign", "text": rest, "color": "#7CF2C8"}
    if kind == "phone":
        parts = [p.strip() for p in rest.split(";")]
        return {"type": "phone", "title": parts[0], "lines": parts[1:]}
    if kind == "toggle":
        title, _, sub = rest.partition(";")
        return {"type": "phone", "title": title.strip(), "lines": [], "mode": "toggle",
                "subtitle": sub.strip(), "at": 3.4}
    raise ValueError("unknown visual: " + spec)


def parse_bank(text):
    topics, cur = [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("@ "):
            cur = {"id": line[2:].strip(), "beats": [], "youtube": {}}
            topics.append(cur)
            continue
        key, sep, val = line.partition(": ")
        if sep and key in ("title", "label", "yt", "desc", "tags") and " | " not in line:
            if key == "yt":
                cur["youtube"]["title"] = val
            elif key == "desc":
                cur["youtube"]["description"] = val + SUFFIX
            elif key == "tags":
                cur["youtube"]["tags"] = [t.strip() for t in val.split(",")]
            else:
                cur[key] = val
            continue
        spec, _, say = line.partition(" | ")
        cur["beats"].append({"say": say.strip(), "visual": parse_visual(spec)})
    return topics


def fill_from_bank(count):
    if not os.path.exists(BANK):
        print("No topics/bank.txt found; nothing to add.")
        return 0
    written = 0
    for t in parse_bank(open(BANK, encoding="utf-8").read()):
        path = os.path.join(ROOT, "topics", t["id"] + ".json")
        if os.path.exists(path) or len(t["beats"]) != 6:
            continue
        json.dump(t, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        written += 1
        print("added from bank", t["id"])
        if written >= count:
            break
    print(f"{written} topics added from the bank.")
    return written
