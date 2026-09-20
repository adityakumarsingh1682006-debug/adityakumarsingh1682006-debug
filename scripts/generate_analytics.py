#!/usr/bin/env python3
"""Generates assets/analytics.svg (stats + languages + 3D contribution graph) and
assets/activity.svg (weekly activity line chart) from live GitHub data.

Pure standard library. Used by .github/workflows/update-analytics.yml

  python scripts/generate_analytics.py          # live data (needs GH_TOKEN)
  python scripts/generate_analytics.py --demo   # offline preview with placeholder data
"""
import argparse
import datetime as dt
import json
import math
import os
import random
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgkit import *  # noqa

USER = os.environ.get("GH_USER", "adityakumarsingh1682006-debug")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

QUERY = """
query($login: String!) {
  user(login: $login) {
    repoCount: repositories(ownerAffiliations: OWNER, isFork: false) { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { date contributionCount weekday } }
      }
    }
    repos: repositories(first: 100, ownerAffiliations: OWNER, isFork: false, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } }
      }
    }
  }
}
"""

LANG_COLORS = [G1, G3, G4, "#2BD97C", "#9BFFC9"]


# ------------------------------------------------------------------ data
def fetch():
    if not TOKEN:
        sys.exit("GH_TOKEN / GITHUB_TOKEN is not set (use --demo for an offline preview)")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "profile-analytics"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.load(r)
    if "errors" in payload or not payload.get("data", {}).get("user"):
        sys.exit("GraphQL error: " + json.dumps(payload.get("errors", payload))[:600])
    return payload["data"]["user"]


def streaks(days):
    """days: list of (date, count) sorted ascending"""
    best = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        best = max(best, run)
    cur = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:  # today may not be over yet
        seq = seq[:-1]
    for _, c in reversed(seq):
        if c > 0:
            cur += 1
        else:
            break
    return cur, best


def parse(u):
    cal = u["contributionsCollection"]["contributionCalendar"]
    grid, week_dates, flat = [], [], []
    for w in cal["weeks"]:
        col = [None] * 7
        for d in w["contributionDays"]:
            col[d["weekday"]] = d["contributionCount"]
            flat.append((d["date"], d["contributionCount"]))
        grid.append(col)
        week_dates.append(w["firstDay"])
    flat.sort()
    cur, best = streaks(flat)
    sizes = {}
    stars = 0
    for r in u["repos"]["nodes"]:
        stars += r["stargazerCount"]
        for e in r["languages"]["edges"]:
            sizes[e["node"]["name"]] = sizes.get(e["node"]["name"], 0) + e["size"]
    tot = sum(sizes.values()) or 1
    langs = [(n, 100 * s / tot) for n, s in sorted(sizes.items(), key=lambda kv: -kv[1])[:5]]
    return dict(grid=grid, week_dates=week_dates, total=cal["totalContributions"],
                commits=u["contributionsCollection"]["totalCommitContributions"],
                repos=u["repoCount"]["totalCount"], stars=stars, cur=cur, best=best, langs=langs, demo=False)


def demo_data():
    """Placeholder pattern so the SVG has something to draw before the first Actions run."""
    rnd = random.Random(21)
    today = dt.date.today()
    start = today - dt.timedelta(days=today.weekday() + 1 + 52 * 7)  # a Sunday, 52 weeks back
    grid, week_dates = [], []
    for w in range(53):
        col = []
        for d in range(7):
            day = start + dt.timedelta(days=w * 7 + d)
            if day > today:
                col.append(None)
                continue
            wave = 0.5 + 0.5 * math.sin(w / 5.0) * math.sin(w / 11.0 + 1)
            col.append(int(max(0, rnd.gauss(3.2 * wave, 2.2))) if rnd.random() > .28 else 0)
        grid.append(col)
        week_dates.append((start + dt.timedelta(days=w * 7)).isoformat())
    return dict(grid=grid, week_dates=week_dates, total=None, commits=None, repos=None, stars=None,
                cur=None, best=None, langs=[], demo=True)


# ------------------------------------------------------------------ helpers
def fmt(n):
    if n is None:
        return "--"
    if n >= 10000:
        return f"{n/1000:.0f}K"
    if n >= 1000:
        return f"{n/1000:.1f}K"
    return str(n)


LEVELS = [  # top, left face, right face
    ("#1B4033", "#12312A", "#0C221C"),
    ("#23A862", "#188049", "#106237"),
    ("#2FD37A", "#1FA95F", "#168047"),
    ("#39FF88", "#27D46E", "#1AA654"),
    ("#C4FFDD", "#66FFAA", "#33D67E"),
]


def level(c, mx):
    if not c:
        return 0
    return min(4, max(1, math.ceil(4 * c / mx)))


# ------------------------------------------------------------------ analytics.svg
def render_analytics(d):
    W, H = 1000, 344
    grid = d["grid"]
    N = len(grid)
    mx = max([c for col in grid for c in col if c is not None] + [1])
    b = [bg(W, H, 22)]

    # ---- left: stats
    b.append(panel(18, 18, 400, 308, 16))
    b.append(text(38, 50, "GitHub Analytics", 16, "#fff", 700))
    b.append(label(176, 50, "LAST 12 MONTHS", 10, DIM))
    stats = [("CONTRIBUTIONS", fmt(d["total"]), ""), ("COMMITS", fmt(d["commits"]), ""), ("PUBLIC REPOS", fmt(d["repos"]), ""),
             ("STARS EARNED", fmt(d["stars"]), ""), ("CURRENT STREAK", fmt(d["cur"]), " days"), ("LONGEST STREAK", fmt(d["best"]), " days")]
    for i, (k, v, unit) in enumerate(stats):
        r, c = divmod(i, 3)
        x, y = 36 + c * 126, 68 + r * 76
        b.append(f'<rect x="{x}" y="{y}" width="116" height="66" rx="12" fill="#fff" fill-opacity=".06" stroke="url(#edge)"/>')
        b.append(label(x + 12, y + 20, k, 8.5, DIM, "start", .8))
        b.append(f'<text x="{x+12}" y="{y+52}" font-family="{SANS}" font-size="26" font-weight="800" fill="url(#greenText)">{esc(v)}'
                 f'<tspan font-size="11" font-weight="600" fill="{MUTED}">{esc(unit if v != "--" else "")}</tspan></text>')
    # languages
    b.append(label(38, 236, "TOP LANGUAGES", 10, DIM))
    b.append(f'<rect x="36" y="246" width="362" height="10" rx="5" fill="#fff" fill-opacity=".08"/>')
    if d["langs"]:
        x = 36
        tot = sum(p for _, p in d["langs"])
        for i, (n, p) in enumerate(d["langs"]):
            w = 362 * p / tot
            b.append(f'<rect x="{x:.1f}" y="246" width="{max(w-2,2):.1f}" height="10" rx="3" fill="{LANG_COLORS[i % 5]}"/>')
            col, row = divmod(i, 3)
            lx, ly = 38 + col * 176, 278 + row * 18
            b.append(f'<circle cx="{lx+4}" cy="{ly-4}" r="4" fill="{LANG_COLORS[i % 5]}"/>')
            b.append(text(lx + 14, ly, n, 12, "#EAFFF4", 500))
            b.append(text(lx + 150, ly, f"{p:.0f}%", 11.5, MUTED, 600, "end", True))
            x += w
    else:
        b.append(text(38, 284, "Awaiting first sync. Run the “Update profile analytics”", 11.5, MUTED, 400))
        b.append(text(38, 302, "workflow once from the Actions tab to load live data.", 11.5, MUTED, 400))

    # ---- right: 3D contribution graph
    b.append(panel(434, 18, 548, 308, 16))
    b.append(text(454, 50, "Contribution Graph", 16, "#fff", 700))
    b.append(label(618, 50, "ACTIVITY // 3D", 10, DIM))
    b.append(label(962, 50, "CONSISTENT PROGRESS", 10, G1, "end"))
    u = 9.4
    a, bb = .866 * u, .32 * u
    ox = 708 - 23 * a * (N / 53)
    oy = 104
    s = .84

    def P(w, dd, h=0):
        return ox + (w - dd) * a, oy + (w + dd) * bb - h

    def poly(pts, fill, extra=""):
        return f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}"{extra}/>'

    # glow + slab
    cxm, cym = ox + 23 * a, oy + 30 * bb + 4
    b.append(f'<ellipse cx="{cxm:.0f}" cy="{cym+22:.0f}" rx="230" ry="46" fill="{G1}" opacity=".16" filter="url(#blur22)"/>')
    m = .5
    corners = [P(-m, -m), P(N + m, -m), P(N + m, 7 + m), P(-m, 7 + m)]
    th = 9
    ll = [corners[3], corners[2], (corners[2][0], corners[2][1] + th), (corners[3][0], corners[3][1] + th)]
    rr = [corners[2], corners[1], (corners[1][0], corners[1][1] + th), (corners[2][0], corners[2][1] + th)]
    b.append(poly(ll, "#0A2A20", f' stroke="{G4}" stroke-opacity=".35"'))
    b.append(poly(rr, "#071C15", f' stroke="{G4}" stroke-opacity=".25"'))
    b.append(poly(corners, "#0F3126", f' stroke="url(#edge)" stroke-width="1.2"'))
    b.append(poly(corners, "url(#glass)"))
    # blocks (painter's order: back to front)
    cells = [(w, dd, grid[w][dd]) for w in range(N) for dd in range(7) if grid[w][dd] is not None]
    cells.sort(key=lambda t: (t[0] + t[1], t[0]))
    tops = sorted(cells, key=lambda t: -t[2])[:8]
    pulse = {(w, dd): i for i, (w, dd, _) in enumerate(tops) if _ > 0}
    for w, dd, c in cells:
        lv = level(c, mx)
        h = 1.6 + (28 * math.sqrt(c / mx) if c else 0)
        top, lf, rt = LEVELS[lv]
        A, B, C, D = P(w, dd, h), P(w + s, dd, h), P(w + s, dd + s, h), P(w, dd + s, h)
        b.append(poly([D, C, (C[0], C[1] + h), (D[0], D[1] + h)], lf))
        b.append(poly([C, B, (B[0], B[1] + h), (C[0], C[1] + h)], rt))
        if (w, dd) in pulse:
            pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (A, B, C, D))
            b.append(f'<polygon points="{pts}" fill="{top}"><animate attributeName="fill" values="{top};#FFFFFF;{top}" '
                     f'dur="{3 + pulse[(w, dd)] * .4:.1f}s" repeatCount="indefinite"/></polygon>')
        else:
            b.append(poly([A, B, C, D], top))
    # legend
    b.append(text(454, 314, "Less", 10.5, DIM, 500))
    for i in range(5):
        b.append(f'<rect x="{484+i*15}" y="305" width="11" height="11" rx="3" fill="{LEVELS[i][0]}"/>')
    b.append(text(566, 314, "More", 10.5, DIM, 500))
    stamp = "PREVIEW DATA" if d["demo"] else "SYNCED " + dt.date.today().isoformat()
    b.append(label(962, 314, stamp, 9.5, DIM, "end", 1))
    save("analytics.svg", svg(W, H, "".join(b), "GitHub analytics: contributions, repositories, streaks, languages and a 3D contribution graph"))


# ------------------------------------------------------------------ activity.svg
def smooth(pts):
    if len(pts) < 3:
        return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    p = [pts[0]] + pts + [pts[-1]]
    dpath = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        dpath += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return dpath


def render_activity(d):
    W, H = 1000, 214
    grid = d["grid"]
    weekly = [sum(c for c in col if c) for col in grid]
    n = len(weekly)
    mx = max(weekly + [1])
    x0, x1, yb, yt = 50, 950, 168, 82
    xs = [x0 + i * (x1 - x0) / (n - 1) for i in range(n)]
    pts = [(xs[i], yb - (weekly[i] / mx) * (yb - yt)) for i in range(n)]
    extra = (f'<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G1}" stop-opacity=".45"/>'
             f'<stop offset="1" stop-color="{G1}" stop-opacity="0"/></linearGradient>'
             f'<linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G3}"/><stop offset="1" stop-color="{G1}"/></linearGradient>')
    b = [bg(W, H, 22), panel(18, 18, 964, 178, 16)]
    b.append(text(38, 50, "Contribution Activity", 16, "#fff", 700))
    b.append(label(214, 50, "ACTIVITY OVER TIME // WEEKLY", 10, DIM))
    total = sum(weekly)
    if d["demo"]:
        stat = "TOTAL --   BEST WEEK --   AVG / WEEK --"
    else:
        stat = f"TOTAL {total}   BEST WEEK {max(weekly)}   AVG / WEEK {total/n:.1f}"
    b.append(label(962, 50, stat, 10, G1, "end", 1))
    for i in range(4):
        y = yb - i * (yb - yt) / 3
        b.append(f'<path d="M{x0} {y:.0f}H{x1}" stroke="{G1}" stroke-opacity=".10" stroke-dasharray="2 5"/>')
    line = smooth(pts)
    b.append(f'<path d="{line} L{x1},{yb} L{x0},{yb}Z" fill="url(#area)"/>')
    b.append(f'<path d="{line}" stroke="url(#line)" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" filter="url(#glowS)" pathLength="1" stroke-dasharray="1">'
             f'<animate attributeName="stroke-dashoffset" values="1;0;0" keyTimes="0;.35;1" dur="9s" repeatCount="indefinite"/></path>')
    pk = max(range(n), key=lambda i: weekly[i])
    if weekly[pk] > 0:
        px, py = pts[pk]
        b.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="#fff" filter="url(#glow)"/>')
        b.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" stroke="{G1}"><animate attributeName="r" values="4.5;12" dur="2s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="2s" repeatCount="indefinite"/></circle>')
        if not d["demo"]:
            b.append(label(px, py - 12, f"PEAK {weekly[pk]}", 9.5, G2, "middle", 1))
    last = None
    for i, ds in enumerate(d["week_dates"]):
        mth = dt.date.fromisoformat(ds).strftime("%b")
        if mth != last:
            b.append(label(xs[i], 186, mth.upper(), 9.5, DIM, "middle", 1))
            last = mth
    save("activity.svg", svg(W, H, "".join(b), "Weekly contribution activity over the last 12 months", extra))


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name, len(content) // 1024, "KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    data = demo_data() if args.demo else parse(fetch())
    render_analytics(data)
    render_activity(data)
