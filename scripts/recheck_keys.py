import json, os, sys, time, urllib.request, urllib.parse, datetime

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
UID = "<anon-id-coupon-test-1>"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
FEEDS = {
    "cnet": ("https://shopping.cnet.com/api/v1/coupons", "14.33", 1),
    "priceblink": ("https://tb.priceblink.com/coupons", "9.18", 0),
}
RIDS = [7402, 1749, 1655, 1923, 225, 4, 233, 3699, 1713, 1824, 1696, 162, 240, 174, 29321, 6133, 5504, 7754, 10284, 21]

log = []
for rid in RIDS:
    for name, (base, ver, pid) in FEEDS.items():
        u = f"{base}?rid={rid}&uid=<redacted>&browser=chrome&ver={ver}&partnerid={pid}&code=1&ab=webravoTest"
        rec = {"rid": rid, "feed": name, "request_url": u, "fetched_utc": datetime.datetime.utcnow().isoformat() + "Z"}
        try:
            r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=30)
            body = r.read()
            rec["status"] = r.status
            fn = f"{name}-rid{rid}.json"
            open(os.path.join(OUT, fn), "wb").write(body)
            rec["raw_file"] = fn
        except Exception as e:
            rec["error"] = repr(e)
        log.append(rec)
        time.sleep(0.6)
json.dump(log, open(os.path.join(OUT, "fetch-log.json"), "w"), indent=2)
print("fetched", sum(1 for r in log if "raw_file" in r), "of", len(log))
