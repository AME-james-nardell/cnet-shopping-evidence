"""Where do the template-matching domains sit in the click traces? (17 Nov 2026)
Usage: python -I template_matches.py <replication-folder> <retailers.js> <template-check-dir>"""
import json, sys, os, glob, re, collections, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
REPL, RETAILERS, CHK = sys.argv[1:4]
log = json.load(open(os.path.join(CHK, "fetch-log.json"), encoding="utf-8"))
match = [r for r in log if "gmail_handle" in (r.get("signatures") or [])]
M = {r["domain"] for r in match}
print("== matches and raw-file hashes (same hash = byte-identical page):")
for r in match:
    txt = open(os.path.join(CHK, "raw", r["raw_file"]), encoding="utf-8", errors="replace").read()
    handles = sorted(set(re.findall(r"([a-z0-9._-]+)\+\"\s*\+\s*domain|mailto:([a-z0-9._-]+)\+", txt)))
    print(f"   {r['domain']:18s} sha256 {r['sha256'][:16]}  bytes {r['bytes']}  hosts seen {r['hosts_seen']}")
def host(u): return (urllib.parse.urlsplit("//" + (u or "").lower().split("://")[-1]).hostname or "").replace("www.", "")
def reg(h):
    p = h.lower().split(".")
    if len(p) >= 3 and p[-2] in ("co","com","org","net") and len(p[-1]) == 2: return ".".join(p[-3:])
    return ".".join(p[-2:])
RET = {int(r["id"]): (r.get("name") or "", host(r.get("url"))) for r in json.load(open(RETAILERS, encoding="utf-8"))}
sets = []
for c in json.load(open(os.path.join(REPL, "data/derived/clicks-nov6-417.json"), encoding="utf-8")): sets.append(("Nov 6", c.get("exit",""), int(c["rid"]), c["hops"]))
for c in json.load(open(os.path.join(REPL, "data/derived/clicks-nov7-132-incl-excluded-atlanta.json"), encoding="utf-8")): sets.append(("Nov 7" + (" (EXCLUDED run)" if c["provider"].startswith("EXCL") else ""), c.get("provider",""), int(c["rid"]), c["hosts"]))
for p in sorted(glob.glob(os.path.join(REPL, "data/sweep-2026-11-09/traces-shard*.json"))):
    for v in json.load(open(p, encoding="utf-8")).values(): sets.append(("Nov 9 sweep", "Thailand", int(v["rid"]), [h["host"] for h in v["hops"]]))
by = collections.defaultdict(list)
for day, ex, rid, hs in sets:
    regs = [reg(h) for h in hs if h]
    hit = [d for d in M if d in regs]
    for d in hit: by[d].append((day, ex, rid, hs))
print("\n== appearances")
for d in sorted(by):
    rows = by[d]
    print(f"\n-- {d}: {len(rows)} clicks; merchants: {sorted(collections.Counter(RET.get(r[2],('?',''))[0] for r in rows).items())}; days: {dict(collections.Counter(r[0] for r in rows))}")
    seen = collections.Counter()
    for day, ex, rid, hs in rows:
        # compress consecutive duplicate registrable domains
        chain = []
        for h in hs:
            if not h: continue
            r_ = reg(h)
            if not chain or chain[-1] != r_: chain.append(r_)
        seen[(RET.get(rid,('?',''))[0], " > ".join(chain))] += 1
    for (mer, ch), n in seen.most_common(8):
        print(f"   {n:3d}x {mer}: {ch}")
both = [s for s in sets if len({d for d in M if d in [reg(h) for h in s[3] if h]}) >= 2]
print(f"\n== clicks containing two or more of the matching domains: {len(both)}")
for day, ex, rid, hs in both[:5]: print("  ", day, RET.get(rid,('?',''))[0], [reg(h) for h in hs if h])
