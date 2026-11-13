#!/usr/bin/env python3
"""Build a week's batch: render Coverage Check graphics, merge entries into
calendar.json, and write a readable markdown summary.

Usage (from repo root):  python3 tools/build_week.py weeks/YYYY-MM-DD.json out.md
"""
import json, os, subprocess, sys

RAW = "https://raw.githubusercontent.com/lamensinsurance/social-images/main/"

def main():
    week_path, md_out = sys.argv[1], sys.argv[2]
    week = json.load(open(week_path))
    cal_path = "calendar.json"
    cal = json.load(open(cal_path)) if os.path.exists(cal_path) else {"entries": []}
    def key(e):
        if e["kind"] == "coverage_check":
            return (e["date"], e["kind"], e.get("title") or e["spec"]["headline"])
        return (e["date"], e["kind"], e.get("video_number"))
    new_keys = {key(n) for n in week["entries"]}
    keep = [e for e in cal["entries"] if key(e) not in new_keys]
    md = [f"# Steve — week of {week['week']}", ""]
    for e in sorted(week["entries"], key=lambda x: (x["date"], x["kind"])):
        if e["kind"] == "coverage_check":
            img = f"images/{e['date']}-{e['slug']}.jpg"
            json.dump(e["spec"], open("/tmp/spec.json", "w"))
            subprocess.run(["python3", "tools/render_post.py", "/tmp/spec.json", img,
                            "--logo", "tools/logo-white.png"], check=True)
            entry = {"date": e["date"], "kind": "coverage_check", "line": e["line"],
                     "title": e["spec"]["headline"], "image_url": RAW + img,
                     "caption": e["caption"]}
            md += [f"## {e['date']} — {e['spec']['eyebrow']}: {e['spec']['headline']}",
                   f"Image: {RAW + img}", "", e["caption"], ""]
        else:
            entry = {k: e[k] for k in ("date", "kind", "video_number", "theme", "title",
                                       "runtime", "script", "caption")}
            md += [f"## {e['date']} — HeyGen video #{e['video_number']}: {e['title']} ({e['runtime']})",
                   "", "**Script**", "", e["script"], "", "**Caption**", "", e["caption"], ""]
        keep.append(entry)
    cal["entries"] = sorted(keep, key=lambda x: (x["date"], x["kind"]))
    json.dump(cal, open(cal_path, "w"), indent=2, ensure_ascii=False)
    open(md_out, "w").write("\n".join(md))
    print("entries:", len(cal["entries"]))

if __name__ == "__main__":
    main()
