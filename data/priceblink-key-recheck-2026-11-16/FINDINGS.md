# VigLink key re-check, CNET Shopping vs PriceBlink coupon feeds (16 Nov 2026)

**Why:** the 13 Nov Sovrn email said the VigLink key in CNET Shopping's Macy's `final-prices.php` answer matched "the same VigLink account key I saw in a November 6 test of PriceBlink's own coupon feed." The 6 Nov test compared coupon sets but never saved raw responses, so that match rested on a written note. An independent review (16 Nov) flagged it as unsupported.

**Method:** same 20 merchant IDs, same anonymous ID (`<anon-id-coupon-test-1>`) and same request parameters as the 6 Nov comparison (`analysis_hopcounts_tags_priceblink.py`, section c). One request per feed per merchant, 0.6 s apart, 40 requests in all:
- CNET Shopping: `https://shopping.cnet.com/api/v1/coupons?rid=...&ver=14.33&partnerid=1&...`
- PriceBlink: `https://tb.priceblink.com/coupons?rid=...&ver=9.18&partnerid=0&...`

Scripts: `figures-src/recheck_keys.py` (fetch, writes raw responses here plus `fetch-log.json`) and `figures-src/extract_keys.py` (parses VigLink first hops). Hashes in `SHA256.txt`.

**Result:** 40 of 40 fetched. 187 coupons in each feed.

| Feed | VigLink key | `loc` values | VigLink links | Merchants |
|---|---|---|---|---|
| CNET Shopping | `6d74c794741ad9843115dedcfec54ee9` | `http://www.getinvisiblehand.com` (all) | 17 | 1749, 5504, 6133, 7402, 29321 |
| PriceBlink | `85302bbca33bc27776a967aeb764eb5d` | `priceblink.com` (4), or the merchant's own site: `hertz.com` (5), `waterford.com` (5), `sixt.com` (2), `paylesscar.com` (1) | 17 | same 5 |

No overlap: CNET Shopping's feed never used `85302bbc...`; PriceBlink's never used `6d74c794...`.

**What this confirms:** the VigLink URL in CNET Shopping's 13 Nov Macy's answer (`firefox-attempt13-macys-NO-CHAIN.har`, key `85302bbc...`, `loc=http://www.priceblink.com`) uses the key PriceBlink's own coupon feed uses, not the key CNET Shopping's own coupon feed uses.

**What it does not show:** who holds either key, how VigLink credits clicks, or why CNET Shopping's server returned PriceBlink's key in that answer. The Macy's link was never clicked.

**Correction to earlier wording:** `loc` is not a reliable "site identifier." PriceBlink's own feed sets it to the merchant's domain on 13 of its 17 links. Describe the key, not `loc`, as the evidence.

**Caveat:** one day, one connection, 20 merchants, and the feed used the 14.33 / 9.18 version parameters from the 6 Nov test, not the installed 14.34.
