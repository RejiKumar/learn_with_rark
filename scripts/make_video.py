#!/usr/bin/env python3
"""make_video.py <topic.json> <outdir>   -> <outdir>/final.mp4 and <outdir>/upload.json

Builds one 30-40 s, 1080x1920 tech Short from a topic file, using the free local pipeline
(Three.js scenes in headless Chrome, edge-tts voice, ffmpeg). No LLM is needed at run time.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
ENV = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
VOICE = os.environ.get("RARK_VOICE", "en-US-GuyNeural")


def run(args, **kw):
    print("+", " ".join(str(a) for a in args), flush=True)
    r = subprocess.run([str(a) for a in args], env=ENV, **kw)
    if r.returncode:
        sys.exit(f"command failed ({r.returncode}): {args[:3]}")
    return r


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def main(topic_path, out):
    t = json.load(open(topic_path, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    beats = [{"id": f"b{i+1}", "say": b["say"], "scene": b["visual"].get("type", "phone")} for i, b in enumerate(t["beats"])]
    script = {"title": t["title"], "language": "en", "label": t["label"], "lead": "template", "style": {"accent": "#7CF2C8"},
              "beats": beats, "sfx": t.get("sfx", []), "sources": t.get("sources", [])}
    json.dump(script, open(os.path.join(out, "script.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    specs = [b["visual"] for b in t["beats"]]
    tpl = open(os.path.join(ROOT, "scripts", "scenes_template.js"), encoding="utf-8").read()
    open(os.path.join(out, "scenes.js"), "w", encoding="utf-8").write("const SPECS = " + json.dumps(specs, ensure_ascii=False) + ";\n" + tpl)

    run([sys.executable, os.path.join(SK, "viral-animate", "timing.py"), out])
    rate, gap, n = -12, 0.12, len(beats)
    for attempt in range(5):
        run([sys.executable, os.path.join(SK, "viral-voice", "voice.py"), out, "--voice", VOICE, "--rate", f"{rate:+d}%", "--gap", f"{gap:.2f}"],
            stdin=subprocess.DEVNULL)
        d = duration(os.path.join(out, "voice.wav"))
        print(f"voice length {d:.1f}s at rate {rate:+d}%, gap {gap:.2f}s", flush=True)
        if 31 <= d <= 39:
            break
        if d > 39:   # too long: speak faster
            rate = min(25, rate + max(3, round((d - 35) / 35 * 100)))
        else:        # too short: add pauses between beats (speaking slower sounds unnatural)
            gap = min(1.4, gap + (34 - d) / max(1, n - 1))
    else:
        sys.exit(f"could not fit the voice into 31-39 s (last {d:.1f}s). Edit the script.")

    run([sys.executable, os.path.join(SK, "viral-voice", "finish.py"), out], stdin=subprocess.DEVNULL)
    final = os.path.join(out, "final.mp4")
    d = duration(final)
    if not 30 <= d <= 40:
        sys.exit(f"final video is {d:.1f}s, outside 30-40 s")
    chk = subprocess.run([sys.executable, os.path.join(SK, "viral-check", "check.py"), final], env=ENV, capture_output=True, text=True)
    print(chk.stdout[-1800:])
    if re.search(r"^FAIL", chk.stdout, re.M):
        sys.exit("viral-check reported a FAIL")
    yt = t["youtube"]
    json.dump({"title": yt["title"], "description": yt["description"], "tags": yt.get("tags", []), "video": final, "seconds": round(d, 1)},
              open(os.path.join(out, "upload.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("done", final, f"{d:.1f}s")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
