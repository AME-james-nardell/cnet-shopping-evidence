"""Cross-merchant publisher-ID table from the day-one, day-two and sweep traces.
Writes data/sweep-2026-11-09/publisher-id-table.csv and prints a summary."""
import json, re, csv, glob, collections, urllib.parse, os

REPL = "<workdir>/CNET Shopping replication"
SW = REPL + "/data/sweep-2026-11-09"
D = REPL + "/data/derived/"

def reg(h):
    p = h.lower().split(".");
    if len(p) >= 3 and p[-2] in ("co", "com", "org", "net") and len(p[-1]) == 2: return ".".join(p[-3:])
    return ".".join(p[-2:])

def ids_from(url):
    out = []
    u = urllib.parse.urlparse(url); host = u.netloc.lower(); path = urllib.parse.unquote(u.path)
    q = {k.lower(): v for k, v in urllib.parse.parse_qs(u.query).items()}
    m = re.match(r"^/c/(\d+)/(\d+)/(\d+)", path)
    if m and any(x in host for x in ("pxf.io", "sjv.io", "evyy.net", "7eer.net", "ztk5.net", "ojrq")): out.append(("Impact partner ID", m.group(1)))
    m = re.search(r"/click-(\d+)-(\d+)", path)
    if m: out.append(("CJ website ID", m.group(1)))
    if "linksynergy" in host and "id" in q: out.append(("Rakuten publisher token", q["id"][0]))
    if "raneaid" in q: out.append(("Rakuten publisher token", q["raneaid"][0]))
    if "awinaffid" in q: out.append(("Awin publisher ID", q["awinaffid"][0]))
    m = re.search(r"camref:([0-9A-Za-z]+)", path)
    if m: out.append(("Partnerize camref", m.group(1)))
    if host == "redirect.viglink.com" and "key" in q: out.append(("VigLink key", q["key"][0]))
    if "redirectingat" in host and "id" in q: out.append(("Skimlinks ID", q["id"][0]))
    m = re.search(r"pid=(\d+)-([a-z0-9.-]+\.[a-z]+)", u.query)
    if m: out.append(("intxfwd pid (named)", m.group(1) + "-" + m.group(2)))
    return out

RET = {int(r["id"]): (urllib.parse.urlsplit("//" + (r.get("url") or "").lower().split("://")[-1]).hostname or "").replace("www.", "") for r in json.load(open("<workdir>/CNET-Shopping-evidence-private/review-package-builder/inputs/retailers.js", encoding="utf-8"))}

rows = []   # (set, merchant, rid, hosts, urls)
for c in json.load(open(D + "clicks-nov6-417.json", encoding="utf-8")): rows.append(("day1", c["merchant"], int(c["rid"]), c["hops"], c["urls"]))
for c in json.load(open(D + "clicks-nov7-132-incl-excluded-atlanta.json", encoding="utf-8")):
    if not c["provider"].startswith("EXCL"): rows.append(("day2", c["merchant"], int(c["rid"]), c["hosts"], c["urls"]))
sweep = []
for p in sorted(glob.glob(SW + "/traces-shard*.json")):
    for rdr, v in json.load(open(p, encoding="utf-8")).items():
        r = ("sweep", v["retailer"] or str(v["rid"]), int(v["rid"]), [h["host"] for h in v["hops"]], [h["url"] for h in v["hops"]])
        sweep.append(r); rows.append(r)
print("rows:", collections.Counter(r[0] for r in rows))

# sweep outcome accounting
def left(hs): return any(h not in ("shopping.cnet.com", "cc.cnet.com") for h in hs)
def reached(r):
    d = RET.get(r[2], ""); m = reg(d) if d else None
    return bool(m) and any(reg(h) == m for h in r[3])
print("sweep clicks:", len(sweep), "| left CNET:", sum(left(r[3]) for r in sweep), "| reached merchant domain:", sum(reached(r) for r in sweep), "| merchants:", len({r[2] for r in sweep}))

tab = collections.defaultdict(lambda: {"merchants": set(), "clicks": 0, "sets": collections.Counter(), "first_pos": []})
for st, mer, rid, hs, us in rows:
    seen = set()
    for pos, (h, u) in enumerate(zip(hs, us)):
        for kind, val in ids_from(u):
            key = (kind, val); e = tab[key]; e["merchants"].add(mer)
            if key not in seen: e["clicks"] += 1; e["sets"][st] += 1; seen.add(key)
            e["first_pos"].append(pos)

# IDs that are CNET's own first-hop accounts: seen at the first non-CNET host in most clicks
out = []
for (kind, val), e in tab.items():
    avg = sum(e["first_pos"]) / len(e["first_pos"])
    out.append({"network_and_kind": kind, "id": val, "merchants": len(e["merchants"]), "clicks": e["clicks"], "day1": e["sets"]["day1"], "day2": e["sets"]["day2"], "sweep": e["sets"]["sweep"],
                "avg_hop_position": round(avg, 1), "example_merchants": "; ".join(sorted(e["merchants"])[:8])})
out.sort(key=lambda r: (-r["merchants"], -r["clicks"]))
with open(SW + "/publisher-id-table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print("distinct IDs:", len(out), "| on 3+ merchants:", sum(1 for r in out if r["merchants"] >= 3), "| on 5+:", sum(1 for r in out if r["merchants"] >= 5))
by_kind = collections.defaultdict(list)
for r in out: by_kind[r["network_and_kind"]].append(r)
for k in sorted(by_kind):
    L = by_kind[k]; print(f"\n{k}: {len(L)} distinct IDs, {sum(1 for r in L if r['merchants']>=3)} on 3+ merchants")
    for r in L[:6]: print(f"   {r['id'][:36]:36s} merchants={r['merchants']:3d} clicks={r['clicks']:3d} (d1 {r['day1']}, d2 {r['day2']}, sweep {r['sweep']}) pos~{r['avg_hop_position']}  {r['example_merchants'][:90]}")
