"""Does any other intermediary host in the click traces serve the same template as unctew.com? (17 Nov 2026)

Builds the list of intermediary registrable domains from the Nov 6, Nov 7 and Nov 9 click traces (the same
boundary rule as article_numbers.py: domains before the first request on the merchant's own domain, or anywhere
if the merchant was never reached, excluding cnet.com and the merchant's domain), adds unctew.com as the
positive control, fetches each domain's home page once (https, then http), saves the raw HTML untouched and
looks for the template's signatures. Nothing fetched is executed.

Usage: python -I template_check.py <replication-folder> <retailers.js> <out-dir>
"""
import json, sys, os, glob, time, re, hashlib, datetime, urllib.request, urllib.parse, ssl

REPL, RETAILERS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
RAW = os.path.join(OUT, "raw")
os.makedirs(RAW, exist_ok=True)

def host(u):
    return (urllib.parse.urlsplit("//" + (u or "").lower().split("://")[-1]).hostname or "").replace("www.", "")

def reg(h):
    p = h.lower().split(".")
    if len(p) >= 3 and p[-2] in ("co", "com", "org", "net") and len(p[-1]) == 2: return ".".join(p[-3:])
    return ".".join(p[-2:])

RET = {int(r["id"]): host(r.get("url")) for r in json.load(open(RETAILERS, encoding="utf-8"))}

traces = []  # (rid, [hosts])
for c in json.load(open(os.path.join(REPL, "data/derived/clicks-nov6-417.json"), encoding="utf-8")):
    traces.append((int(c["rid"]), c["hops"]))
for c in json.load(open(os.path.join(REPL, "data/derived/clicks-nov7-132-incl-excluded-atlanta.json"), encoding="utf-8")):
    traces.append((int(c["rid"]), c["hosts"]))
for p in sorted(glob.glob(os.path.join(REPL, "data/sweep-2026-11-09/traces-shard*.json"))):
    for v in json.load(open(p, encoding="utf-8")).values():
        traces.append((int(v["rid"]), [h["host"] for h in v["hops"]]))

inter = {}
for rid, hs in traces:
    m = reg(RET[rid]) if RET.get(rid) else None
    first = next((i for i, h in enumerate(hs) if m and h and reg(h) == m), len(hs))
    for h in hs[:first]:
        if not h: continue
        r = reg(h)
        if r != "cnet.com" and r != m:
            inter.setdefault(r, set()).add(h)
inter.setdefault("unctew.com", set()).add("unctew.com")   # positive control

SIGS = {
    "gmail_handle": re.compile(r"<gmail-handle-withheld>", re.I),
    "forget_js": re.compile(r"PushTheButtonForget"),
    "churchill": re.compile(r"Courage is the only thing", re.I),
    "foil_cookie": re.compile(r"foil=1"),
    "sitename_class": re.compile(r'class="sitename"'),
    "bidding_system": re.compile(r"bidding system", re.I),
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0"
ctx = ssl.create_default_context()

log = []
for d in sorted(inter):
    rec = {"domain": d, "hosts_seen": sorted(inter[d]), "fetched_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    for scheme in ("https", "http"):
        url = f"{scheme}://{d}/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
            r = urllib.request.urlopen(req, timeout=15, context=ctx if scheme == "https" else None)
            body = r.read(2_000_000)
            rec.update(url=url, status=r.status, final_url=r.geturl(), bytes=len(body))
            fn = re.sub(r"[^a-z0-9.-]", "_", d) + ".html"
            open(os.path.join(RAW, fn), "wb").write(body)
            rec["raw_file"] = fn
            rec["sha256"] = hashlib.sha256(body).hexdigest()
            txt = body.decode("utf-8", "replace")
            rec["signatures"] = sorted(k for k, rx in SIGS.items() if rx.search(txt))
            t = re.search(r"<title[^>]*>(.*?)</title>", txt, re.I | re.S)
            rec["title"] = (t.group(1).strip()[:80] if t else "")
            break
        except Exception as e:
            rec.setdefault("errors", []).append(f"{url}: {type(e).__name__}: {str(e)[:120]}")
    log.append(rec)
    time.sleep(0.4)

json.dump(log, open(os.path.join(OUT, "fetch-log.json"), "w", encoding="utf-8"), indent=2)
ok = [r for r in log if "raw_file" in r]
print(f"intermediary domains: {len(log) - 1} (+ unctew.com control); fetched: {len(ok)}; failed: {len(log) - len(ok)}")
for r in log:
    s = r.get("signatures")
    if s:
        print(f"  {r['domain']:32s} {len(s)} sigs {s}  title={r.get('title')!r}  final={r.get('final_url')}")
