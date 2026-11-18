import time
from replay import price_check
UID = "<anon-id-chrome-test-profile>"
TITLE = "DEWALT 20-volt Max 1/2-in Cordless Drill (2-Batteries Included, Charger Included and Soft Bag included)"
for mpn in ("DCD771C2", ""):
    for price in ("89.00", "99.00", "119.00", "128.99", "129.00", "139.00", "149.00"):
        cat, fin, _ = price_check(28, TITLE, price, "DEWALT", sku="506283", uid=<redacted> mpn=mpn)
        print("mpn=%-8s" % (mpn or "-"), "$" + price, "| test", fin.get("test"), "| sellers", len(cat.get("retailers") or []), "| msg:", (fin.get("message") or "")[:60], "| ship:", (fin.get("ship_message") or "")[:70])
        time.sleep(0.8)
