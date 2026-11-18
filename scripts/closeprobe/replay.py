"""Replay the extension's price check against CNET's API: catalog-products.php (GET), then final-prices.php (POST, JSON).
Usage as a module: price_check(rid, title, price, brand, upc, uid) -> (catalog_obj, final_obj)"""
import json, urllib.request, urllib.parse, uuid, time

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
BASE = "https://shopping.cnet.com/api/v1/"

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"User-Agent": UA, "Content-type": "application/json", "x-cdn-debug": "fastly"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))

def price_check(rid, title, price, brand, upc="", sku="", uid=<redacted> scraped=None, mpn="", model=""):
    uid = uid or str(uuid.uuid4())
    q = {"rid": rid, "title": title, "price": price, "model": model, "mpn": mpn, "brand": brand, "upc": upc, "sku": sku, "isbn": "", "ship": "",
         "rating": "", "in_stock": "", "c1": "", "c2": "", "c3": "", "c4": "", "c5": "", "uid": uid, "ver": "14.34", "browser": "chrome", "step": 2, "tax": 0, "partnerid": 1}
    cat = get(BASE + "catalog-products.php?" + urllib.parse.urlencode(q))
    cat0 = cat[0] if isinstance(cat, list) and cat else cat
    body = {"gpid": "", "productId": "", "scraped_retailers": scraped if scraped is not None else [], "catalog_products": cat0,
            "bg_source": "Merged Products", "isTitleSearch": False, "tax": 1}
    fin = post(BASE + "final-prices.php?n=%d&browser=chrome&partnerid=1" % (int(time.time() * 1000) % 1000), body)
    return cat0, (fin[0] if isinstance(fin, list) and fin else fin), uid

if __name__ == "__main__":
    # 1) replay James's own Belk check with his uid
    uid = "<anon-id-chrome-test-profile>"
    cat, fin, _ = price_check(7417, "Womens 3/4 Sleeve Printed Top", "9.75", "Kim", upc="480022212603", sku='"0480022212603', uid=<redacted>
    print("catalog keys:", list(cat.keys()), "| retailers:", cat.get("retailers"), "| log_id:", cat.get("log_id"))
    print("final keys:", list(fin.keys()))
    print("test:", fin.get("test"), "| message:", repr(fin.get("message")), "| ship_message:", repr(fin.get("ship_message")))
    for k in ("affiliate_close_click_url", "affiliate_compare_prices_click_url", "best_price_close_url", "price_history_message", "price_history_lowestprurl"):
        print(k, "->", (fin.get(k) or "")[:200])
