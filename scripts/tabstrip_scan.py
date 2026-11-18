"""Scan a screen recording for sideways jumps of the Firefox tab strip (17 Nov 2026).

A new pinned tab opening at the far left pushes every other tab and the "+" button to the right; closing it
pulls them back. A loading spinner inside an existing tab moves nothing. So a jump of the whole strip is the
test that tells the two apart.

Method: ffmpeg decodes every frame (10 per second) of the top strip (x 0-1400, y 4-40 at 1920 wide), halves it
and turns it grey. For each frame the script compares the strip's column profile with the previous frame's,
trying horizontal offsets of -45 to +45 half-pixels, and reports frames where the best offset is clearly
non-zero.

Limits (from the 17 Nov independent review): it finds CANDIDATE times for review, it is not a tab classifier.
It does NOT detect when another window covers the browser, so "no sideways jumps" doesn't mean the strip was
visible and nothing happened. It can miss a close when other tabs change width at the same time (it missed one
in attempt 1). It samples 10 of 30 frames per second, and its thresholds aren't calibrated. Check every hit,
and every stretch that matters, on full-resolution frames.

Usage: python -I tabstrip_scan.py <video> [more videos...]
"""
import sys, subprocess

W, H = 700, 18          # half-resolution strip
FPS = 10
BAND = range(3, 15)     # rows that hold tab icons and titles

def profiles(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf",
           f"fps={FPS},crop=1400:36:0:4,scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = W * H
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        prof = [0] * W
        for r in BAND:
            row = buf[r * W:(r + 1) * W]
            for x in range(W): prof[x] += row[x]
        yield [v / len(BAND) for v in prof], sum(buf) / n
    if p.wait() != 0:
        raise RuntimeError(f"ffmpeg failed on {path} (exit code {p.returncode}); the scan is incomplete")

def mad(a, b, s, lo=50, hi=W - 50):
    # compare a[x] with b[x - s]
    tot = 0.0; cnt = 0
    for x in range(lo, hi):
        y = x - s
        if 0 <= y < W:
            tot += abs(a[x] - b[y]); cnt += 1
    return tot / cnt

def scan(path):
    prev = None; events = []; i = -1; bright = []
    for i, (prof, mean) in enumerate(profiles(path)):
        bright.append(mean)
        if prev is not None:
            m0 = mad(prof, prev, 0)
            if m0 > 2.0:   # something changed in the strip; look for a sideways move
                best = min(range(-45, 46), key=lambda s: mad(prof, prev, s))
                mb = mad(prof, prev, best)
                if best != 0 and mb < m0 * 0.5:
                    events.append((i / FPS, best * 2, round(m0, 1), round(mb, 1)))
        prev = prof
    return events, bright, i + 1

for path in sys.argv[1:]:
    ev, bright, n = scan(path)
    print(f"\n=== {path.split('/')[-1]}  ({n} frames at {FPS}/s)")
    # strip visibility: the Firefox strip is dark purple; mark long stretches where mean brightness changes a lot
    if not ev:
        print("   no sideways jumps of the tab strip")
    for t, px, m0, mb in ev:
        print(f"   t={t:6.1f}s  strip moved {px:+4d} px  (difference before alignment {m0}, after {mb})")
