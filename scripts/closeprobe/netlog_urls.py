import json, sys, re, collections
p = sys.argv[1]
txt = open(p, encoding="utf-8").read()
try:
    d = json.loads(txt)
except Exception:
    marker = '"events":['
    i = txt.index(marker) + len(marker)
    head = json.loads(txt[:txt.index(marker)].rstrip().rstrip(",") + "}")
    dec = json.JSONDecoder()
    evs = []
    pos = i
    ws = " \r\n\t,"
    while True:
        while pos < len(txt) and txt[pos] in ws:
            pos += 1
        if pos >= len(txt) or txt[pos] == "]":
            break
        try:
            o, pos = dec.raw_decode(txt, pos)
        except Exception:
            break
        evs.append(o)
    print("repaired truncated log; events parsed:", len(evs), "| file ended at char", pos, "of", len(txt))
    d = {"constants": head["constants"], "events": evs}
c = d["constants"]
et = {v: k for k, v in c["logEventTypes"].items()}
ev = d["events"]
print("events", len(ev))
rows = []
for e in ev:
    t = et.get(e["type"])
    if t == "URL_REQUEST_START_JOB":
        prm = e.get("params") or {}
        rows.append((int(e["time"]), e["source"]["id"], prm.get("method"), prm.get("url"), prm.get("initiator")))
rows.sort(key=lambda r: (r[0], r[1]))
t0 = rows[0][0] if rows else 0
print("requests", len(rows), "span s", ((rows[-1][0] - t0) // 1000) if rows else 0)
hosts = collections.Counter(re.sub(r"^https?://([^/]+).*", r"\1", r[3] or "") for r in rows)
print(hosts.most_common(40))
print("---- interesting")
pat = re.compile(r"cnet|rdr\.php|et\.php|unctew|digidip|viglink|ebay|final-prices|catalog-products|/install", re.I)
skip = re.compile(r"\.(png|jpg|gif|svg|woff2?|css|webp)(\?|$)", re.I)
for r in rows:
    if r[3] and pat.search(r[3]) and not skip.search(r[3]):
        print((r[0] - t0) // 1000, "s", r[2], r[3][:230], "| init:", (r[4] or "")[:60])
