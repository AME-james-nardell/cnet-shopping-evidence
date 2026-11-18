import re, sys
src = open("<home>/cnet-test/cnet-shopping-14.34/js/app.js", encoding="utf-8", errors="replace").read()
print("size", len(src))
for key in sys.argv[1:]:
    print("=" * 20, key)
    for m in re.finditer(re.escape(key), src):
        s = max(0, m.start() - 700); e = min(len(src), m.end() + 700)
        print("--- at", m.start())
        print(src[s:e])
