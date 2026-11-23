# CNET Shopping: evidence files

Evidence for "[Deeper Down the Rabbit Hole: CNET Shopping's Compare Button Opens Affiliate Links Too](https://affiliatemanager.expert/2026/11/23/cnet-shopping-compare-button-affiliate-links/)" by James Nardell (Affiliate Manager Expert), which builds on [Ben Edelman's CNET Shopping research](https://www.benedelman.org/close-and-laundering-from-cnet-shopping/). The [methods and evidence note](https://affiliatemanager.expert/cnet-shopping-methods-and-evidence/) maps each claim to the files here.

Everything here is a scrubbed copy of a private original. This page says what was removed, what was kept, and how to check both.

## What's here

| Folder | Contents |
|---|---|
| `har/` | Network logs for the live button tests: the Chrome log for capture 1 (November 9), and the Firefox HAR files for captures 2 to 14 (November 13 and 17). Captures are numbered as in the methods note. |
| `recordings/` | Screen recordings of the live tests (1920x1128, original frame timing, no audio). |
| `stills/` | Screenshots and frame sheets cited in the methods note. |
| `data/` | Coupon-link tests (November 6, 7 and 9), the coupon-feed census, the Close-link replay, the VigLink key re-check, the tab-strip scan, the four matching template pages and the November 6 DNS lookup. |
| `scripts/` | The scripts that produced the counts and checks. |

## What was removed

**Network logs.**
- The extension's anonymous IDs are replaced with placeholders, the same one everywhere for each browser profile: `<anon-id-profile-A>`, `<anon-id-profile-B>` and `<anon-id-chrome-test-profile>`. So you can still tell which captures share a profile.
- Cookie values are replaced with `<redacted>`. Cookie names and attributes are kept, so you can still see, for example, that CNET's redirect set `IHUID` and `lastclick` for `.getinvisiblehand.com`.
- Removed values: network click IDs (`cjevent`, `awc` and any parameter named like `*clickid` or `*click_id`, such as `irclickid`, `ir_clickid` and `pub_click_id`), the per-click `subid` that CNET writes into `unctew.com` links, the client address CNET's answers echo back (`userip`), and RetailMeNot's per-click reference values. These are removed in plain and URL-encoded form, including inside nested links.
- CNET's per-click reference numbers (its coupon links carry a `PQRST` placeholder that its redirect replaces with a number, which then appears in fields such as `cuid`, `track_code`, `xcust`, `ref` and `sid`) are replaced with stable placeholders, `<click-ref-0001>` and so on. The same number always gets the same placeholder, in every file, so a click can still be followed along its chain.
- Requests that aren't evidence (store page assets, analytics and ad tech) keep their host, path, status and timing. They lose their query strings, request and response bodies, cookies and non-standard headers. Ad-tech parameters carried in the path are removed too.
- Kept in full, apart from the values above: CNET Shopping's own requests and answers (`shopping.cnet.com/api/v1/...`), the redirect chains (`rdr.php`, `cc.cnet.com`, `unctew.com`, Impact's `sjv.io` links, `cc.retailmenot.com`) and the store landing pages.
- Every entry is kept, in its original order. Entry counts and positions are unchanged.
- The Chrome log also loses its browser-state section (`polledData`) and the command line. Chrome had already stripped its own cookie values when the log was saved.

**Recordings.** Each recording is re-encoded at full size with its original frame timestamps, so every time cited in the methods note still holds. Audio is dropped. Solid boxes cover:

| Recording | Covered |
|---|---|
| capture-03 | Page area 0 to 5.5 s (Firefox settings and address suggestions); everything from 41.4 s (Browser Toolbox) |
| capture-04 | Page area 0 to 4.5 s (new-tab page and address suggestions); everything from 126.9 s |
| capture-05 | Page area 0 to 3.9 s; everything from 90.5 s |
| capture-06 | Page area 0 to 4.6 s; everything from 90.6 s |
| capture-07 | Page area 0 to 7.2 s (the add-on debugging page, which shows the add-on's per-install ID, and the new-tab page); everything from 128.4 s |
| capture-08 | Page area 0 to 6.8 s; everything from 74.3 s |
| capture-09 | Page area 0 to 3.8 s; everything from 35.7 s |
| capture-10 | Page area 0 to 3.5 s; the click ID in the address bar, 18.1 to 38.6 s; everything from 144.0 s |
| capture-11 | Everything from 70.2 s |
| capture-12 | The click ID in the address bar, 29.4 to 63.0 s; everything from 147.0 s |
| capture-13 | Everything from 67.9 s |
| capture-14 | The click ID in the address bar, 23.9 to 43.7 s; everything from 43.3 s |
| capture-14-first-slickdeals-click | The click ID in the address bar, 25.9 s to the end |
| extra-lowes-one-hour-limit | Everything from 143.0 s |
| extra-lowes-oven-compare | Page area 0 to 3.6 s; everything from 63.7 s (Browser Toolbox, the Windows desktop and a file dialog) |

"Everything from" spans start when the Browser Toolbox comes up to save the network log. It shows identifiers and cookie values, and the network log itself is in `har/`. The address-bar boxes cover only the click ID's value, so the parameter name and the stand-down flags after it (`irgwc=1&afsrc=1`) stay readable.

**Stills.** Boxes cover the anonymous ID, cookie values, the per-click sub ID and the click IDs where they show: one network-panel screenshot (`extra-lowes-oven-2026-11-13-devtools-redirect.png`) and the address bar in two frame sheets (`capture-12-frames-30-to-150s.png`, `capture-14-frames-2-to-56s.png`).

**Coupon data.**
- Anonymous IDs are replaced with placeholders.
- Network click IDs and CNET's per-click reference numbers are handled as in the network logs (above), along with two client addresses and one third-party email address in a coupon description.
- In `data/retailer-domains.json`, three retailer names that are email addresses read `<email removed>`. Every other name, ID and domain matches the extension's list exactly, including HTML entities such as `&amp;`.
- Local file paths in the scripts are replaced with `<workdir>`.
- The Gmail account name behind the four template pages is replaced with `<gmail-handle-withheld>`, in the pages and in `template_check.py`.

## What isn't here

- **CNET Shopping's add-on files.** It's CNET's software. The methods note cites it by version, file and line. To check you have the same packages: Firefox version 14.34, SHA-256 `ae179954f11e0087f6222344408127ee18a49c0bc4a5dccbe07a587d3396f5f2`; version 14.35, `f406de4b33cc6d9a9fd4453160aacf96f3b62b18cf00c8f67fcdbbb1c7e9fb76`.
- **The extension's own retailer file.** It includes CNET's page-scraping rules. `data/retailer-domains.json` keeps only the fields the scripts read (retailer ID, name and domain), in the same format, so it works as a drop-in.
- **51 of the 55 home pages saved in the template check.** They're other companies' pages, and none matched. `data/template-check-2026-11-17/fetch-log.json` lists all 55 with the SHA-256 of each page as fetched. The four published pages differ from those hashes only where the Gmail account name is withheld.
- **Private correspondence and the independent reviews,** which contain identifiers.

## Checking the figures

Run on these copies, `scripts/sweep/sweep_ids.py` and `scripts/article_numbers.py` give the same output as on the originals, with one exception. Three of the eight November 6 landing URLs that were cut at 400 characters are shorter after scrubbing, so the script counts five. The eight are listed in `data/derived/landing-urls-cut-at-400-characters.json`.

The scripts have their local paths replaced. Point them at this folder's `data/` and at `data/retailer-domains.json`. Note that `sweep_ids.py` writes `publisher-id-table.csv` next to the traces it reads.

## Hashes

- `SHA256SUMS.txt`: every public file in this repository.
- `ORIGINALS-SHA256.txt`: each public file's private original, by its original name, with that file's SHA-256. The originals are kept and can be shared with a lawyer or reviewer on request.

Some original names were wrong: three Nov 13 recordings were named "no tab visible", and a tab is visible in them. Two stills said "before click" and "tab closed", and capture 6's file said "new profile". The public names fix this.
