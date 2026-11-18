"""Headline numbers for the article, with the CORRECTED merchant boundary (6 Nov 2026).

Boundary rule: a click "reached the merchant" if some hop host is on the merchant's own registrable domain
(exact match; merchant-owned tracking subdomains count as the merchant). The old rule matched any host that
contained the merchant's brand name, which put network tracking hosts such as tillys.pxf.io on the merchant side.

  third parties  = distinct registrable domains before the first request on the merchant's own domain,
                   excluding cnet.com
  landing URL    = the first request on the merchant's own domain
  inventory      = registrable domains before that first request (or anywhere, if the merchant was never
                   reached), excluding cnet.com and the merchant's own domain

Usage:  python article_numbers.py <clicks.json> <retailers.js>
  clicks.json   list of {exit, merchant, rid, hops: [hosts], urls: [urls]}  (whoswho/clicks.json in the scratch folder)
  retailers.js  the extension's retailer list (id, name, url)
Exit-name "Miami" is the 10 later clicks; the article's earlier (pre-Miami) set is shown separately."""
import json, sys, collections, re, urllib.parse

clicks = json.load(open(sys.argv[1], encoding="utf-8"))
# Hostname only: some list entries carry a path (scarosso.com/en, cvs.com/photo). Fixed 16 Nov 2026; before this,
# a Scarosso click that reached the merchant counted as unreached (sweep 197 -> 198, 62% -> 63%, 39 -> 38 domains).
RET = {int(r["id"]): (urllib.parse.urlsplit("//" + (r.get("url") or "").lower().split("://")[-1]).hostname or "").replace("www.", "") for r in json.load(open(sys.argv[2], encoding="utf-8"))}

def reg(h):
    p = h.lower().split(".")
    if len(p) >= 3 and p[-2] in ("co", "com", "org", "net") and len(p[-1]) == 2: return ".".join(p[-3:])
    return ".".join(p[-2:])

WRAP = {"url", "u", "destination", "dest", "redirect", "r", "out", "target", "ued"}

def keys_of(url, depth=0):
    """Keys in the query, tracking tokens in the path (camref:, pubref:) and keys inside nested destination addresses."""
    p = urllib.parse.urlparse(url)
    q = urllib.parse.parse_qs(p.query)
    keys = {k.lower() for k in q}
    path = urllib.parse.unquote(p.path)
    path_tag = bool(re.search(r"(camref|pubref):", path))
    nested = []
    for k, vs in q.items():
        if k.lower() in WRAP:
            for v in vs:
                v = urllib.parse.unquote(v)
                if v.startswith(("http://", "https://")): nested.append(v)
    m = re.search(r"destination:(https?://.+)$", path)
    if m: nested.append(m.group(1))
    if depth < 2:
        for n_ in nested:
            k2, t2 = keys_of(n_, depth + 1)
            keys |= k2; path_tag = path_tag or t2
    return keys, path_tag

def classify(url):
    keys, path_tag = keys_of(url)
    t = []
    if keys & {"ranmid", "raneaid", "ransiteid"}: t.append("Rakuten")
    if keys & {"irclickid", "irgwc"}: t.append("Impact")
    if keys & {"cjevent", "cjdata"}: t.append("CJ")
    awin = bool(keys & {"awc", "sv_campaign_id"} or "awin" in url.lower())
    if awin: t.append("Awin")
    if keys & {"pubref"} or "prf.hn" in url or path_tag or ("clickref" in keys and not awin): t.append("Partnerize")
    if keys & {"clickid", "aff_sub", "upstream", "subid", "sub_id"}: t.append("tracker params")
    if not t:
        resid = keys - WRAP
        t.append("afsrc only" if resid == {"afsrc"} else ("none" if not resid else "other params"))
    return "+".join(t)

def merchant_domain(c):
    d = RET.get(int(c["rid"]), "")
    return reg(d) if d else None

def analyze(subset, label):
    rows = []
    for c in subset:
        m = merchant_domain(c); hs = c["hops"]
        first = next((i for i, h in enumerate(hs) if m and reg(h) == m), None)
        if first is None: continue
        orgs = []
        for h in [h for h in hs[:first] if "cnet.com" not in h]:
            r = reg(h)
            if r not in orgs: orgs.append(r)
        url = c["urls"][first]
        rows.append((len(orgs), classify(url), len(url) >= 400))
    n = len(rows)
    print(f"\n== {label}: {len(subset)} clicks, {n} reached the merchant's own domain, {len({c['merchant'] for c in subset})} merchants")
    for t in (3, 4):
        k = sum(1 for r in rows if r[0] >= t); print(f"   {t} or more distinct domains before the merchant: {k}/{n} = {100 * k / n:.1f}%")
    cls = collections.Counter(r[1] for r in rows)
    print("   first merchant-domain URL carried:", {k: f"{v} ({100 * v / n:.0f}%)" for k, v in cls.most_common()})
    unt = cls["afsrc only"] + cls["none"]
    print(f"   untagged (only afsrc=1, or nothing): {unt}/{n} = {100 * unt / n:.1f}% | landing URLs cut at 400 characters: {sum(1 for r in rows if r[2])}")

analyze([c for c in clicks if c["exit"] != "Miami"], "pre-Miami set (the draft's original 407)")
analyze(clicks, "all clicks (the draft's current figures)")

inv = set()
for c in clicks:
    m = merchant_domain(c); hs = c["hops"]
    first = next((i for i, h in enumerate(hs) if m and reg(h) == m), len(hs))
    for h in hs[:first]:
        r = reg(h)
        if r != "cnet.com" and r != m: inv.add(r)
print(f"\ninventory: {len(inv)} registrable domains (draft says 87)")
unm = [c for c in clicks if not any(merchant_domain(c) and reg(h) == merchant_domain(c) for h in c["hops"])]
cn = [c for c in unm if not [h for h in c["hops"] if h not in ("shopping.cnet.com", "cc.cnet.com")]]
print(f"unmatched: {len(unm)} (CNET-only {len(cn)}, left CNET without a match {len(unm) - len(cn)}); draft says 111, 29, 82")
