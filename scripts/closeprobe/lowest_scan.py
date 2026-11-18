"""Which answer shape does each retailer get when the shopper's price is the LOWEST that CNET's catalog knows of?
That is the only shape in which the 'You've found the best price!' popup (with the Close button) is shown automatically.
Step 1: ask at $1.00 to learn the next lowest catalog price. Step 2: ask again at 95% of it."""
import csv, json, re, time, urllib.parse
from replay import price_check

UID = "<anon-id-chrome-test-profile>"
OUT = "<workdir>/CNET Shopping replication/data/close-probe-2026-11-09/lowest-price-shape.csv"

RETAILERS = {28: "Lowes", 207: "Macys", 7417: "Belk", 1827: "AbeBooks", 21: "Home Depot", 4: "Staples", 26: "Target", 10: "Walmart"}
# (title, brand, mpn, isbn-ish unused)
PRODUCTS = [
    ("DEWALT 20-volt Max 1/2-in Cordless Drill (1-Battery Included)", "DEWALT", "DCD771C2"),
    ("Apple AirPods Pro 2", "Apple", "MTJV3AM/A"),
    ("Instant Pot Duo 6-Quart 7-in-1 Electric Pressure Cooker", "Instant Pot", "Duo60"),
    ("Keurig K-Elite Single Serve Coffee Maker", "Keurig", "K-Elite"),
    ("Ninja Professional Blender 1000", "Ninja", "BL610"),
]

def dest(u):
    if not u:
        return ""
    q = urllib.parse.parse_qs(urllib.parse.urlparse(u).query)
    inner = urllib.parse.unquote(q.get("url", [""])[0])
    return urllib.parse.urlparse(inner).netloc or ""

rows = []
for rid, rname in RETAILERS.items():
    for title, brand, mpn in PRODUCTS:
        row = {"rid": rid, "retailer": rname, "product": title[:40]}
        try:
            cat, fin, _ = price_check(rid, title, "1.00", brand, uid=<redacted> mpn=mpn)
            m = re.search(r"\$([\d,]+\.\d\d)", fin.get("ship_message") or "")
            row["catalog_sellers"] = len(cat.get("retailers") or [])
            if m and "next lowest" in (fin.get("ship_message") or ""):
                x = float(m.group(1).replace(",", ""))
                row["next_lowest"] = x
                time.sleep(0.6)
                cat, fin, _ = price_check(rid, title, "%.2f" % (x * 0.95), brand, uid=<redacted> mpn=mpn)
            ac = fin.get("affiliate_close_click_url") or ""
            row.update({
                "test": fin.get("test"),
                "message": (fin.get("message") or "")[:60],
                "ship_message": (fin.get("ship_message") or "")[:70],
                "retailers_in_final": len(fin["retailers"]) if isinstance(fin.get("retailers"), list) else "",
                "has_aff_close": "Y" if ac else "N",
                "close_first_host": dest(ac),
                "has_aff_compare": "Y" if fin.get("affiliate_compare_prices_click_url") else "N",
                "has_best_price_close_url": "Y" if fin.get("best_price_close_url") else "N",
                "has_price_history_message": "Y" if fin.get("price_history_message") else "N",
            })
        except Exception as e:
            row["error"] = str(e)[:100]
        rows.append(row)
        print(rid, rname, "|", row.get("product"), "|", row.get("test"), "|", row.get("message"), "| sellers", row.get("retailers_in_final"), "| close", row.get("has_aff_close"), row.get("close_first_host"), "| cmp", row.get("has_aff_compare"), "|", row.get("error", ""), flush=True)
        time.sleep(0.8)

fields = ["rid", "retailer", "product", "catalog_sellers", "next_lowest", "test", "message", "ship_message", "retailers_in_final", "has_aff_close", "close_first_host", "has_aff_compare", "has_best_price_close_url", "has_price_history_message", "error"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for r in rows:
        w.writerow({k: r.get(k, "") for k in fields})
print("saved", OUT)
