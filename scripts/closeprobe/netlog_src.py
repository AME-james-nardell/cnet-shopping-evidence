"""Dump every event for requests whose URL matches a pattern (default: et.php) in a Chrome net-export log, plus a timeline of all requests."""
import json, sys, re
p = sys.argv[1]
pat = re.compile(sys.argv[2] if len(sys.argv) > 2 else r"et\.php")
d = json.load(open(p, encoding="utf-8"))
c = d["constants"]
et = {v: k for k, v in c["logEventTypes"].items()}
ph = {v: k for k, v in c["logEventPhase"].items()}
ev = d["events"]
ids = set()
for e in ev:
    if et.get(e["type"]) == "URL_REQUEST_START_JOB":
        u = (e.get("params") or {}).get("url") or ""
        if pat.search(u):
            ids.add(e["source"]["id"])
print("matching sources:", ids)
t0 = min(int(e["time"]) for e in ev)
for e in ev:
    if e["source"]["id"] in ids:
        prm = e.get("params")
        s = json.dumps(prm, ensure_ascii=False)[:900] if prm else ""
        print((int(e["time"]) - t0) / 1000.0, "s", et.get(e["type"]), ph.get(e["phase"]), s)
