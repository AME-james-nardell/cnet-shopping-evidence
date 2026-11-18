import time
from replay import price_check
UID = "<anon-id-chrome-test-profile>"
TITLE = "DEWALT 20-volt Max 1/2-in Cordless Drill (2-Batteries Included, Charger Included and Reciprocating Saw)"
for price in ("199.00", "249.00", "299.00"):
    for mpn in ("DCD771380BVB", ""):
        cat, fin, _ = price_check(28, TITLE, price, "DEWALT", sku="957788", uid=<redacted> mpn=mpn)
        print(price, "mpn=%s" % (mpn or "-"), "| test", fin.get("test"), "| catalog sellers", len(cat.get("retailers") or []), "| message:", fin.get("message"), "| ship:", fin.get("ship_message"), "| close:", bool(fin.get("affiliate_close_click_url")))
        for r in (cat.get("retailers") or [])[:4]:
            print("     ", r.get("name", "")[:80], r.get("price"))
        time.sleep(1)
