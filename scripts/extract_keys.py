import json, os, sys, collections, urllib.parse

D = sys.argv[1]
log = json.load(open(os.path.join(D, "fetch-log.json")))

def first_hop(coupon_url):
    q = urllib.parse.parse_qs(urllib.parse.urlparse(coupon_url).query)
    return q.get("url", [coupon_url])[0]

pairs = collections.Counter()      # (feed, key, loc) -> count
rids_by = collections.defaultdict(set)
coupon_counts = collections.Counter()
for rec in log:
    if "raw_file" not in rec:
        continue
    try:
        j = json.load(open(os.path.join(D, rec["raw_file"]), encoding="utf-8"))
    except Exception as e:
        print("parse fail", rec["raw_file"], e); continue
    for blk in (j if isinstance(j, list) else [j]):
        for c in (blk.get("coupons") or []):
            coupon_counts[rec["feed"]] += 1
            hop = first_hop(c.get("url", ""))
            if "viglink.com" in hop:
                q = urllib.parse.parse_qs(urllib.parse.urlparse(hop).query)
                key = q.get("key", ["(none)"])[0]
                loc = q.get("loc", ["(none)"])[0]
                pairs[(rec["feed"], key, loc)] += 1
                rids_by[(rec["feed"], key, loc)].add(rec["rid"])

print("coupons per feed:", dict(coupon_counts))
print("\nVigLink key / loc pairs found in each feed:")
for (feed, key, loc), n in sorted(pairs.items()):
    print(f"  {feed:10s} key={key}  loc={loc}  links={n}  merchants={sorted(rids_by[(feed,key,loc)])}")
