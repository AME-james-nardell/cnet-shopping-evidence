"""Replay the extension's price check for realistic products (not made-up ones) at Lowe's, to see the answer shape James's pages would get."""
import json, time, os
from replay import price_check

UID = "<anon-id-chrome-test-profile>"
OUT = "<workdir>/CNET Shopping replication/data/close-probe-2026-11-09/lowes-real-products.json"

CASES = [
    (28, "Project Source Style Selections 28-in to 48-in Light Oil Rubbed Bronze Steel Single Curtain Rod", "12.98", "Project Source", "", "3031529", ""),
    (28, "Project Source Light Gray Utility Tub with Stainless Steel Sink", "149.00", "Project Source", "", "5013113833", ""),
    (28, "Kobalt 50-Piece Standard (SAE) and Metric Polished Chrome Mechanics Tool Set with Hard Case", "29.98", "Kobalt", "", "5015276017", ""),
    (28, "DEWALT 20-volt Max 1/2-in Cordless Drill (1-Battery Included)", "99.00", "DEWALT", "", "", "DCD771C2"),
    (28, "Apple AirPods Pro 2", "189.00", "Apple", "", "", "MTJV3AM/A"),
    (207, "Apple AirPods Pro 2", "189.00", "Apple", "", "", "MTJV3AM/A"),
    (7417, "Keurig K-Elite Single Serve Coffee Maker", "139.99", "Keurig", "", "", "K-Elite"),
]
KEYS = ("affiliate_close_click_url", "affiliate_compare_prices_click_url", "best_price_close_url", "price_history_message", "affiliate_click_url_savings_present")
res = []
for rid, title, price, brand, upc, sku, mpn in CASES:
    row = {"rid": rid, "title": title, "price": price}
    try:
        cat, fin, _ = price_check(rid, title, price, brand, upc=upc, sku=sku, uid=<redacted> mpn=mpn)
        row["test"] = fin.get("test")
        row["catalog_retailers"] = len(cat.get("retailers") or [])
        row["ship_message"] = fin.get("ship_message")
        row["message"] = fin.get("message")
        for k in KEYS:
            v = fin.get(k)
            row[k] = (v[:140] if isinstance(v, str) else v)
        row["retailers_in_final"] = len(fin.get("retailers") or []) if isinstance(fin.get("retailers"), list) else fin.get("retailers")
        row["final_keys"] = sorted(fin.keys())
    except Exception as e:
        row["error"] = str(e)[:200]
    res.append(row)
    print(json.dumps({k: v for k, v in row.items() if k != "final_keys"}, ensure_ascii=False))
    time.sleep(1.0)
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("saved", OUT)
