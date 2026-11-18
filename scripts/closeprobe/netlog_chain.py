"""Follow the redirect chain of requests whose URL matches a pattern in a Chrome net-export log.
Prints, per request source: start URL, initiator, each redirect target, response status/location, and cookie names set."""
import json, sys, re
p = sys.argv[1]
pat = re.compile(sys.argv[2])
d = json.load(open(p, encoding="utf-8"))
c = d["constants"]
et = {v: k for k, v in c["logEventTypes"].items()}
ev = d["events"]
t0 = min(int(e["time"]) for e in ev)
bysrc = {}
for e in ev:
    bysrc.setdefault(e["source"]["id"], []).append(e)
hit = []
for sid, es in bysrc.items():
    for e in es:
        if et.get(e["type"]) == "URL_REQUEST_START_JOB":
            u = (e.get("params") or {}).get("url") or ""
            if pat.search(u):
                hit.append((int(e["time"]), sid))
                break
hit.sort()
def short(u, n=200):
    return (u or "")[:n]
for t, sid in hit:
    print("=" * 10, "source", sid, "start +%.2fs" % ((t - t0) / 1000.0))
    for e in sorted(bysrc[sid], key=lambda x: int(x["time"])):
        ty = et.get(e["type"]); prm = e.get("params") or {}
        rel = (int(e["time"]) - t0) / 1000.0
        if ty == "URL_REQUEST_START_JOB" and e["phase"] == 1:
            print("  +%.2f START %s %s | initiator=%s | type=%s | first_party=%s" % (rel, prm.get("method"), short(prm.get("url")), prm.get("initiator"), prm.get("request_type"), short(str(prm.get("site_for_cookies")), 80)))
        elif ty == "URL_REQUEST_REDIRECTED":
            print("  +%.2f REDIRECT -> %s" % (rel, short(prm.get("location"))))
        elif ty == "HTTP_TRANSACTION_READ_RESPONSE_HEADERS" or ty == "HTTP_TRANSACTION_QUIC_READ_RESPONSE_HEADERS":
            hs = prm.get("headers") or []
            line = hs[0] if hs else ""
            loc = [h for h in hs if h.lower().startswith("location")]
            ck = [re.sub(r"=.*", "", h[len("set-cookie: "):]) for h in hs if h.lower().startswith("set-cookie")]
            print("  +%.2f RESPONSE %s %s cookies_set=%s" % (rel, line, [short(l, 160) for l in loc], ck))
