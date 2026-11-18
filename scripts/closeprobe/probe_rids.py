"""Ask CNET's price-check API about a made-up product with no other seller, for many retailers, using the author's registered anonymous ID.
Writes data/close-probe-2026-11-09/close-link-by-retailer.csv incrementally."""
import json, csv, os, time, glob, urllib.parse, sys
from replay import price_check

REPL = "<workdir>/CNET Shopping replication"
OUT = REPL + "/data/close-probe-2026-11-09"
os.makedirs(OUT, exist_ok=True)
UID = "<anon-id-chrome-test-profile>"
PRODUCT = dict(title="Zzyzx Test Item 4471", price="49.99", brand="Zzyzx", upc="", sku="", mpn="ZZ4471")

RET = {int(r["id"]): (r.get("name"), (r.get("url") or "")) for r in json.load(open("<workdir>/CNET-Shopping-evidence-private/review-package-builder/inputs/retailers.js", encoding="utf-8"))}
sweep = json.load(open(REPL + "/data/sweep-2026-11-09/selection-manifest.json"))["selected_rids"]
big = [4, 26, 3, 10, 21, 28, 35, 1070, 1912, 1915, 1923, 233, 1696, 207, 17354, 7440, 30, 232, 1, 7417, 21, 6007]
rids = list(dict.fromkeys(big + sweep))
print("retailers to probe:", len(rids))

def dest_chain(u):
    if not u: return ""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
    inner = urllib.parse.unquote(q.get("url", [""])[0])
    return urllib.parse.urlparse(inner).netloc or inner[:60]

path = OUT + "/close-link-by-retailer.csv"
done = set()
if os.path.exists(path):
    done = {int(r["rid"]) for r in csv.DictReader(open(path, encoding="utf-8"))}
new = not os.path.exists(path)
f = open(path, "a", newline="", encoding="utf-8")
w = csv.DictWriter(f, fieldnames=["rid", "retailer", "domain", "test", "retailers_in_catalog", "has_aff_close", "close_origin", "close_first_host", "has_aff_compare", "has_best_price_close_url", "best_price_close_dest", "has_price_history_message", "message", "keys", "error"])
if new: w.writeheader()
for n, rid in enumerate(rids, 1):
    if rid in done: continue
    row = {"rid": rid, "retailer": RET.get(rid, ("?", ""))[0], "domain": RET.get(rid, ("?", ""))[1]}
    try:
        cat, fin, _ = price_check(rid, uid=<redacted> **PRODUCT)
        ac = fin.get("affiliate_close_click_url") or ""
        q = urllib.parse.parse_qs(urllib.parse.urlparse(ac).query) if ac else {}
        row.update({"test": fin.get("test"), "retailers_in_catalog": len(cat.get("retailers") or []), "has_aff_close": "Y" if ac else "N",
                    "close_origin": (q.get("origin") or [""])[0], "close_first_host": dest_chain(ac),
                    "has_aff_compare": "Y" if fin.get("affiliate_compare_prices_click_url") else "N",
                    "has_best_price_close_url": "Y" if fin.get("best_price_close_url") else "N", "best_price_close_dest": dest_chain(fin.get("best_price_close_url") or ""),
                    "has_price_history_message": "Y" if fin.get("price_history_message") else "N", "message": (fin.get("message") or fin.get("ship_message") or "")[:80], "keys": ",".join(sorted(fin.keys()))[:200]})
    except Exception as e:
        row["error"] = str(e)[:120]
    w.writerow(row); f.flush()
    if n % 25 == 0: print("done", n, "of", len(rids), flush=True)
    time.sleep(1.0)
f.close(); print("finished")
