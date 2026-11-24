#!/usr/bin/env python3
"""generate_topics.py [--min 6] [--count 6]

Keeps the topic bank stocked so the bot never runs dry. If fewer than --min unpublished topics are
left, asks Claude for --count new tech tips and writes them to topics/<id>.json after validating them.
Needs ANTHROPIC_API_KEY (a GitHub Actions secret). Exits 0 without doing anything when the bank is full
or no key is set, so the daily run is never blocked by this step.
"""
import argparse, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("RARK_TOPIC_MODEL", "claude-opus-5-5")
VISUALS = {"door", "padlock", "bulb", "sign", "phone"}

SYSTEM = """You write scripts for the YouTube Shorts channel RARK: short, useful tech tips for curious people worldwide, in plain simple English.
Return ONLY a JSON array of topic objects, no prose and no code fences. Each object:
{
 "id": "kebab-case-slug",
 "title": "2-4 word working name",
 "label": "on-screen hook, max 6 words, ALL CAPS",
 "beats": [ {"say": "...", "visual": {...}} ],   // exactly 6 beats
 "youtube": {"title": "under 60 characters, one emoji at the end", "description": "1-2 plain sentences", "tags": ["3 to 5 tags"]}
}
Rules for the script:
- The 6 "say" lines total 80 to 95 words. Beat 1 is the hook: 14 words or fewer, a claim or question a stranger understands.
- Practical advice only: security habits, phone settings, safe AI use, how common tech works. No hype words, no 'hack', no 'secret'.
- NO numbers, statistics, prices or named studies, and no claims about a specific company's product features that could be wrong or change. Say what is generally true.
- No medical, legal, financial or political claims. Nothing frightening. Suitable for all ages.
- The last beat tells the viewer to do one small thing today and to send the video to someone.
- Each "visual" is an object drawn in 3D, never a person or animal. Allowed forms:
  {"type":"door"}  {"type":"padlock"}  {"type":"bulb"}
  {"type":"sign","text":"2-4 words","color":"#7CF2C8"}
  {"type":"phone","title":"short title","lines":["short text"],"badge":"WORD","badgeAt":2.4}   (lines and badge are optional)
  {"type":"phone","title":"Security","mode":"toggle","subtitle":"short setting name","at":3.4}   (toggle slides to ON at 'at' seconds)
  {"type":"phone","title":"Your code","mode":"code"}
- Vary the visuals across the 6 beats; open beat 1 with a door, bulb, sign or phone.
"""

def load_ids():
    ids, titles = [], []
    for p in glob.glob(os.path.join(ROOT, "topics", "*.json")):
        ids.append(os.path.basename(p)[:-5])
        try: titles.append(json.load(open(p, encoding="utf-8")).get("title", ""))
        except Exception: pass
    return ids, titles

def unpublished():
    st = os.path.join(ROOT, "state", "published.json")
    done = set(json.load(open(st))) if os.path.exists(st) else set()
    return [i for i in load_ids()[0] if i not in done]

def validate(t, existing):
    errs = []
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", str(t.get("id", ""))): errs.append("bad id")
    if t.get("id") in existing: errs.append("duplicate id")
    beats = t.get("beats", [])
    if len(beats) != 6: errs.append("need exactly 6 beats")
    words = sum(len(str(b.get("say", "")).split()) for b in beats)
    if not 76 <= words <= 98: errs.append(f"{words} words")
    if beats and len(str(beats[0].get("say", "")).split()) > 15: errs.append("hook too long")
    for b in beats:
        v = b.get("visual", {})
        if v.get("type") not in VISUALS: errs.append(f"bad visual {v.get('type')}")
        if v.get("type") == "sign" and not v.get("text"): errs.append("sign without text")
    if re.search(r"\d", " ".join(str(b.get("say", "")) for b in beats)): errs.append("digits in script")
    yt = t.get("youtube", {})
    if not yt.get("title") or len(yt["title"]) > 70 or not yt.get("description"): errs.append("bad youtube fields")
    if not t.get("label") or len(t["label"].split()) > 7: errs.append("bad label")
    return errs

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--min", type=int, default=6); ap.add_argument("--count", type=int, default=6)
    a = ap.parse_args()
    left = len(unpublished())
    if left >= a.min:
        print(f"{left} unpublished topics left; nothing to generate."); return
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{left} topics left and ANTHROPIC_API_KEY is not set; adding topics from the bank instead.")
        from bank_topics import fill_from_bank
        fill_from_bank(a.count); return
    import anthropic
    ids, titles = load_ids()
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL, max_tokens=16000, system=SYSTEM,
        messages=[{"role": "user", "content": f"Write {a.count} NEW topics. Do not repeat or closely overlap any of these existing ones: " + "; ".join(titles) + "."}])
    if msg.stop_reason == "refusal":
        sys.exit("The model declined this request; no topics were written.")
    text = "".join(b.text for b in msg.content if b.type == "text").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        items = json.loads(text)
    except json.JSONDecodeError as e:
        sys.exit(f"Could not parse the topics: {e}")
    written, existing = 0, set(ids)
    for t in items:
        errs = validate(t, existing)
        if errs:
            print("rejected", t.get("id"), errs); continue
        json.dump(t, open(os.path.join(ROOT, "topics", t["id"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        existing.add(t["id"]); written += 1; print("wrote", t["id"])
    print(f"{written} new topics written, {len(unpublished())} unpublished in total.")
    if left + written == 0:
        sys.exit("No valid topics were produced.")

if __name__ == "__main__":
    main()
