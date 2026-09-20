"""Builds the hand-designed (static + SMIL-animated) SVGs in ../assets.
Run:  python scripts/build_static_assets.py
The dynamic ones (analytics.svg / activity.svg) are built by generate_analytics.py."""
import math
import os
import random

from svgkit import *  # noqa

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")


def save(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name, len(content) // 1024, "KB")


# ---------------------------------------------------------------- typing helper (pure SMIL)
def typing_block(x, y0, lines, step, size=10.5, cycle=16.0, first=.6, gap=2.5, colors=None):
    cw = size * .6
    out, defs = [], []
    for i, s in enumerate(lines):
        W = len(s) * cw
        y = y0 + i * step
        t0 = first + i * gap
        t1 = t0 + len(s) * .055
        nxt = first + (i + 1) * gap if i < len(lines) - 1 else cycle * .95
        k = lambda t: f"{t / cycle:.4f}"
        cid = f"tc{i}"
        col = (colors[i] if colors else G1)
        defs.append(f'<clipPath id="{cid}"><rect x="{x-2}" y="{y-size-2}" width="{W+4:.1f}" height="{size+7}">'
                    f'<animate attributeName="width" values="0;0;{W+4:.1f};{W+4:.1f};0" keyTimes="0;{k(t0)};{k(t1)};.95;1" '
                    f'dur="{cycle}s" repeatCount="indefinite"/></rect></clipPath>')
        out.append(f'<g clip-path="url(#{cid})"><text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" font-weight="600" '
                   f'fill="{col}" textLength="{W:.1f}" lengthAdjust="spacingAndGlyphs" filter="url(#glowS)">{esc(s)}</text></g>')
        out.append(f'<rect x="{x}" y="{y-size+1}" width="{cw*.8:.1f}" height="{size+1}" fill="{G1}" opacity="0">'
                   f'<animate attributeName="x" values="{x};{x};{x+W:.1f};{x+W:.1f}" keyTimes="0;{k(t0)};{k(t1)};1" dur="{cycle}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;{k(t0)};{k(nxt)};1" calcMode="discrete" dur="{cycle}s" repeatCount="indefinite"/></rect>')
    return "".join(out), "".join(defs)


# ================================================================== HERO
def hero():
    W, H = 1000, 668
    cx, cy, R = 500, 252, 140
    rnd = random.Random(11)
    b = [bg(W, H, 26)]
    extra = f"""
<radialGradient id="orb" cx=".35" cy=".28" r=".9"><stop offset="0" stop-color="#2F8A66"/><stop offset=".42" stop-color="#14483A"/><stop offset="1" stop-color="#061812"/></radialGradient>
<radialGradient id="orbRim" cx=".5" cy=".5" r=".5"><stop offset=".8" stop-color="{G3}" stop-opacity="0"/><stop offset="1" stop-color="{G3}" stop-opacity=".55"/></radialGradient>
<linearGradient id="ringG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G3}" stop-opacity=".1"/><stop offset=".3" stop-color="{G1}"/><stop offset=".7" stop-color="{G4}"/><stop offset="1" stop-color="{G3}" stop-opacity=".1"/></linearGradient>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{G1}" stop-opacity="0"/><stop offset=".5" stop-color="{G1}" stop-opacity=".30"/><stop offset="1" stop-color="{G1}" stop-opacity="0"/></linearGradient>
<clipPath id="orbClip"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>
"""
    # particles
    for _ in range(80):
        x, y = rnd.uniform(10, 990), rnd.uniform(44, 655)
        r = rnd.choice([.8, 1, 1.2, 1.7])
        b.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{rnd.choice([G1, G4, "#fff"])}" opacity=".3">'
                 f'<animate attributeName="opacity" values=".08;.85;.08" dur="{rnd.uniform(2.5,6):.1f}s" begin="-{rnd.uniform(0,5):.1f}s" repeatCount="indefinite"/></circle>')

    # macOS-style menu bar
    b.append(f'<path d="M0 34H1000V26A26 26 0 0 0 974 0H26A26 26 0 0 0 0 26Z" fill="#000" fill-opacity=".30"/>'
             f'<path d="M0 34.5H1000" stroke="{G1}" stroke-opacity=".22"/>')
    b.append(f'<path d="M22 9 L29 13 V21 L22 25 L15 21 V13Z" fill="{G1}" filter="url(#glowS)"/><path d="M22 14 L26 16.5 V20 L22 22.5 L18 20 V16.5Z" fill="#0b2a1e"/>')
    b.append(text(42, 22, "aditya.os", 13, TXT, 700))
    for mx, m in zip([124, 176, 228, 300], ["Code", "Build", "Innovate", "Repeat"]):
        b.append(text(mx, 22, m, 12, MUTED, 500))
    b.append(text(500, 22, "adityakumarsingh1682006-debug", 11, DIM, 500, "middle", True, .4))
    b.append(f'<circle cx="742" cy="17.5" r="3.4" fill="{G1}"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    b.append(label(752, 21.5, "SYSTEM ONLINE", 10.5, G1, "start", 1.2))
    b.append(text(976, 21.5, "DU // B.COM", 10.5, DIM, 600, "end", True, 0.6))

    # ---- orbit ring geometry
    def ring(rx, ry, rot, stroke, dash, front_only=False, back_only=False, dur=14):
        g = f'<g transform="rotate({rot} {cx} {cy})">'
        if not front_only:
            g += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" stroke="{stroke}" stroke-opacity=".28" stroke-width="1.4"/>'
        if front_only:
            g += (f'<path d="M{cx-rx} {cy}A{rx} {ry} 0 0 0 {cx+rx} {cy}" stroke="url(#ringG)" stroke-width="2.6" filter="url(#glowS)"/>'
                  f'<path d="M{cx-rx} {cy}A{rx} {ry} 0 0 0 {cx+rx} {cy}" stroke="#fff" stroke-opacity=".55" stroke-width="1" stroke-dasharray="{dash}">'
                  f'<animate attributeName="stroke-dashoffset" values="0;-40" dur="{dur/4}s" repeatCount="indefinite"/></path>')
        g += '</g>'
        return g

    # hologram platform under orb
    b.append(f'<ellipse cx="{cx}" cy="420" rx="230" ry="26" fill="{G1}" opacity=".16" filter="url(#blur10)"/>')
    for rx_, op in [(196, .55), (150, .38), (104, .28)]:
        b.append(f'<ellipse cx="{cx}" cy="418" rx="{rx_}" ry="{rx_*.11:.1f}" stroke="{G1}" stroke-opacity="{op}" stroke-dasharray="3 6"/>')
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R+46}" fill="{G1}" opacity=".16" filter="url(#blur22)"/>')

    # back rings
    b.append(ring(236, 70, -16, G1, "3 9"))
    b.append(ring(202, 52, 15, G3, "3 9"))

    # back floating tiles
    back = [("python", 332, 142, 60, -6, 5.5, 0), ("ai", 588, 84, 56, 5, 6.2, 1.2), ("react", 716, 152, 60, 7, 5.0, 2.1),
            ("supabase", 438, 66, 44, -4, 4.6, 0.6), ("opencv", 290, 240, 58, -7, 6.6, 3.0)]
    for n, x, y, s, r, d, dl in back:
        b.append(tile(x, y, s, n, rot=r, dur=d, delay=dl, amp=6))

    # orb
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#orb)" stroke="url(#edge)" stroke-width="1.8"/>')
    g = [f'<g clip-path="url(#orbClip)">']
    for dy in (-96, -52, 0, 52, 96):
        rr = math.sqrt(R * R - dy * dy)
        g.append(f'<ellipse cx="{cx}" cy="{cy+dy}" rx="{rr:.1f}" ry="{rr*.2:.1f}" stroke="{G1}" stroke-opacity=".16"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="{R-1}" stroke="{G1}" stroke-opacity=".14"/>')
    for i, dur in enumerate([10, 10, 10]):
        ph = i * dur / 3
        g.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R}" ry="{R}" stroke="{G4}" stroke-opacity=".2">'
                 f'<animate attributeName="rx" values="{R};{R*.7:.0f};0;{R*.7:.0f};{R}" keyTimes="0;.15;.5;.85;1" dur="{dur}s" begin="-{ph:.1f}s" repeatCount="indefinite"/></ellipse>')
    g.append(f'<rect x="{cx-R}" y="{cy-R-60}" width="{2*R}" height="60" fill="url(#scan)">'
             f'<animate attributeName="y" values="{cy-R-60};{cy+R}" dur="5s" repeatCount="indefinite"/></rect>')
    g.append(f'<ellipse cx="{cx-52}" cy="{cy-82}" rx="76" ry="34" fill="#fff" opacity=".10" transform="rotate(-28 {cx-52} {cy-82})" filter="url(#blur4)"/>')
    g.append('</g>')
    b.append("".join(g))
    b.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#orbRim)"/>')
    # orb text
    b.append(f'<text x="{cx}" y="{cy+22}" font-family="{SANS}" font-size="98" font-weight="800" fill="url(#greenText)" text-anchor="middle" '
             f'textLength="212" lengthAdjust="spacingAndGlyphs" filter="url(#glow)">AKS</text>')
    b.append(f'<text x="{cx}" y="{cy+56}" font-family="{SANS}" font-size="22" font-weight="600" fill="#fff" text-anchor="middle" textLength="108" lengthAdjust="spacing">Aditya</text>')
    b.append(f'<path d="M{cx-52} {cy+66}H{cx+52}" stroke="{G1}" stroke-opacity=".6"/>')
    b.append(f'<text x="{cx}" y="{cy+83}" font-family="{MONO}" font-size="9.5" font-weight="600" fill="{G2}" text-anchor="middle" textLength="204" lengthAdjust="spacing">AI • COMPUTER VISION • WEB • PRODUCT</text>')

    # front rings + travelling light
    b.append(ring(236, 70, -16, G1, "3 9", front_only=True, dur=14))
    b.append(ring(202, 52, 15, G3, "3 9", front_only=True, dur=12))
    for rx_, ry_, rot, dur, col in [(236, 70, -16, 9, "#fff"), (202, 52, 15, 7, G4)]:
        p = f"M{cx-rx_} {cy}A{rx_} {ry_} 0 1 1 {cx+rx_} {cy}A{rx_} {ry_} 0 1 1 {cx-rx_} {cy}Z"
        b.append(f'<g transform="rotate({rot} {cx} {cy})"><circle r="4.2" fill="{col}" filter="url(#glow)"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{p}"/></circle></g>')

    # front tiles
    front = [("mediapipe", 360, 366, 64, -6, 5.8, 0.4), ("nextjs", 730, 262, 60, 6, 6.4, 1.6),
             ("github", 706, 356, 54, -5, 5.2, 2.6), ("figma", 612, 402, 68, 5, 6.0, 0.9)]
    for n, x, y, s, r, d, dl in front:
        b.append(tile(x, y, s, n, rot=r, dur=d, delay=dl, amp=7))

    # ---- LEFT column: terminal
    b.append(panel(24, 52, 204, 172, 16))
    for i, c in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        b.append(f'<circle cx="{42+i*15}" cy="70" r="4.2" fill="{c}"/>')
    b.append(text(214, 74, "aditya.sys", 10, DIM, 600, "end", True))
    b.append(f'<path d="M24 86H228" stroke="{G1}" stroke-opacity=".2"/>')
    lines = ["> INITIALIZING ADITYA.SYS...", "> DEVELOPER PROFILE ONLINE", "> AI × COMPUTER VISION × WEB",
             "> BUILDING DIGITAL SYSTEMS", "> SYSTEM STATUS: ONLINE"]
    t_svg, t_defs = typing_block(38, 110, lines, 24, 10.5, 16, colors=[G2, G1, G1, G1, "#FFFFFF"])
    extra += t_defs
    b.append(t_svg)

    # slogan
    b.append(f'<text x="30" y="272" font-family="{SANS}" font-size="32" font-weight="700" fill="url(#greenText)" filter="url(#glowS)">Turning</text>')
    b.append(f'<text x="30" y="308" font-family="{SANS}" font-size="32" font-weight="700" fill="url(#greenText)">Ideas</text>')
    b.append(f'<text x="30" y="344" font-family="{SANS}" font-size="32" font-weight="700" fill="url(#greenText)">Into</text>')
    b.append(f'<text x="30" y="380" font-family="{SANS}" font-size="32" font-weight="700" fill="url(#greenText)" textLength="110" lengthAdjust="spacingAndGlyphs">Impact</text>')
    b.append(f'<rect x="146" y="373" width="14" height="4" fill="{G1}"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>')
    b.append(text(30, 414, "B.Com student at DU,", 12.5, MUTED, 500))
    b.append(text(30, 432, "exploring the future", 12.5, MUTED, 500))
    b.append(text(30, 450, "through technology.", 12.5, MUTED, 500))
    b.append(pill(24, 470, 190, 30, "CURRENTLY BUILDING", G1, 10.5, True, dot=True))

    # ---- RIGHT column: status
    b.append(panel(772, 52, 204, 176, 16))
    b.append(f'<circle cx="792" cy="76" r="4" fill="{G1}"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    b.append(label(804, 80, "SYSTEM ONLINE", 10.5, G1, "start", 1.2))
    b.append(f'<path d="M772 92H976" stroke="{G1}" stroke-opacity=".2"/>')
    for i, (n, p) in enumerate([("Learning", 1.0), ("Building", .8), ("Exploring", .7), ("Improving", .9)]):
        y = 118 + i * 30
        b.append(text(790, y + 4, n, 12, MUTED, 500))
        b.append(f'<rect x="862" y="{y-3}" width="98" height="9" rx="4.5" fill="#fff" fill-opacity=".08"/>')
        b.append(f'<rect x="862" y="{y-3}" width="{98*p:.1f}" height="9" rx="4.5" fill="url(#greenFill)" filter="url(#glowS)">'
                 f'<animate attributeName="width" values="0;{98*p:.1f};{98*p:.1f};0" keyTimes="0;.25;.9;1" dur="8s" begin="{i*.35}s" repeatCount="indefinite"/></rect>')
    b.append(panel(772, 246, 204, 100, 16))
    b.append(text(788, 282, "“", 40, G1, 700))
    for i, s in enumerate(["A small step in code,", "a big leap for", "possibilities."]):
        b.append(text(814, 274 + i * 18, s, 11.5, MUTED, 500, "start", True))
    b.append(panel(772, 364, 204, 78, 16))
    b.append(label(788, 388, "ACTIVE PROJECT", 9.5, DIM))
    b.append(f'<circle cx="958" cy="384" r="3.4" fill="{G1}"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    b.append(text(788, 414, "MediKey", 21, "#fff", 700))
    b.append(text(788, 431, "Digital medical identity", 11, MUTED, 500))

    # ---- centre: name block
    # bottom-left: education module
    b.append(panel(24, 522, 176, 118, 16))
    b.append(label(42, 548, "EDUCATION // DU", 10, DIM))
    b.append(text(42, 584, "B.Com", 30, "#fff", 800))
    b.append(text(42, 606, "University of Delhi", 13, MUTED, 500))
    b.append(f'<rect x="42" y="618" width="140" height="5" rx="2.5" fill="#fff" fill-opacity=".08"/><rect x="42" y="618" width="90" height="5" rx="2.5" fill="url(#greenFill)"><animate attributeName="width" values="24;90;24" dur="6s" repeatCount="indefinite"/></rect>')
    # bottom-right: active modules
    b.append(panel(800, 462, 176, 178, 16))
    b.append(label(818, 488, "ACTIVE MODULES", 10, DIM))
    for i, n in enumerate(["AI Systems", "Computer Vision", "Web Development", "Product Design"]):
        yy = 516 + i * 32
        b.append(f'<circle cx="820" cy="{yy}" r="3.4" fill="{G1}"><animate attributeName="opacity" values="1;.3;1" dur="{1.6+i*.3:.1f}s" repeatCount="indefinite"/></circle>')
        b.append(text(832, yy + 4, n, 12, "#EAFFF4", 500))
        b.append(bars(944, yy + 6, 5, 3, 2, 12, G1, i + 20))
    b.append(text(500, 456, "Hi, I’m", 20, MUTED, 500, "middle"))
    b.append(f'<text x="500" y="524" font-family="{SANS}" font-size="80" font-weight="800" fill="url(#greenText)" text-anchor="middle" '
             f'textLength="392" lengthAdjust="spacingAndGlyphs" filter="url(#glowS)">ADITYA</text>')
    b.append(f'<text x="500" y="558" font-family="{SANS}" font-size="13.5" font-weight="600" fill="#E5FFF1" text-anchor="middle" '
             f'textLength="588" lengthAdjust="spacing">AI  |  COMPUTER VISION  |  WEB TECHNOLOGIES  |  PRODUCT DEVELOPMENT</text>')
    chips = [("B.Com @ DU", 120), ("Hackathon Builder", 158), ("Tech Explorer", 130), ("Problem Solver", 138)]
    tot = sum(w for _, w in chips) + 12 * 3
    x = 500 - tot / 2
    for s, w in chips:
        b.append(f'<rect x="{x:.0f}" y="576" width="{w}" height="30" rx="15" fill="#fff" fill-opacity=".07" stroke="url(#edge)"/>'
                 f'<circle cx="{x+16:.0f}" cy="591" r="3" fill="{G1}"/>')
        b.append(text(x + w / 2 + 6, 596, s, 12.5, "#fff", 500, "middle"))
        x += w + 12
    b.append(text(500, 628, "B.Com student at the University of Delhi. I learn by building real projects,", 13.5, MUTED, 400, "middle"))
    b.append(text(500, 648, "experimenting with new technologies and turning ideas into working systems.", 13.5, MUTED, 400, "middle"))

    save("hero.svg", svg(W, H, "".join(b), "Aditya - developer operating system hero", extra))


# ================================================================== PROFILE
def profile():
    W, H = 1000, 196
    b = [bg(W, H, 22)]
    # monogram badge
    b.append(tile(96, 92, 108, f'<text x="0" y="10" font-family="{SANS}" font-size="40" font-weight="800" fill="url(#greenText)" text-anchor="middle" textLength="76" lengthAdjust="spacingAndGlyphs">AKS</text>',
                  rot=-4, dur=6, amp=5))
    b.append(label(176, 44, "DEVELOPER PROFILE // ONLINE", 10.5, G1, "start", 1.6))
    b.append(text(176, 88, "Aditya", 44, "#fff", 800))
    b.append(pill(176, 100, 132, 26, "B.Com @ DU", G1, 11.5, True))
    b.append(text(318, 118, "University of Delhi", 13, MUTED, 500))
    b.append(text(176, 152, "AI  •  Computer Vision  •  Web  •  Product Development", 14, G2, 600))
    b.append(text(176, 176, "UI/UX  •  Accessibility Technology  •  Rapid Prototyping  •  Hackathons", 12, DIM, 500))
    # description panel
    b.append(panel(566, 24, 410, 148, 16))
    b.append(label(586, 50, "ABOUT // SYSTEM NOTE", 10, DIM))
    for i, s in enumerate(["Building experimental digital systems by",
                           "combining intelligent technologies,",
                           "human-computer interaction and",
                           "product-focused engineering."]):
        b.append(text(586, 76 + i * 22, s, 14.5, "#EAFFF4", 500))
    b.append(bars(936, 158, 6, 4, 3, 22, G1, 8))
    save("profile.svg", svg(W, H, "".join(b), "Aditya - B.Com at DU - AI, Computer Vision, Web, Product Development"))


# ================================================================== PROJECT CARDS
def card(name, slug, sub, desc, techs, art, button=None, foot_label=None):
    W, H = 500, 292
    b = [bg(W, H, 22)]
    b.append(f'<circle cx="410" cy="100" r="90" fill="{G1}" opacity=".13" filter="url(#blur22)"/>')
    b.append(text(26, 46, name, 24, "#fff", 800, "start", False, 1.2))
    b.append(text(26, 68, sub, 13.5, G1, 700))
    for i, s in enumerate(desc):
        b.append(text(26, 100 + i * 19, s, 12.5, MUTED, 400))
    b.append(art)
    x = 26
    for t in techs:
        w = len(t) * 7 + 22
        b.append(f'<rect x="{x}" y="196" width="{w}" height="24" rx="12" fill="#fff" fill-opacity=".07" stroke="{G1}" stroke-opacity=".35"/>')
        b.append(text(x + w / 2, 212, t, 11, "#E5FFF1", 600, "middle", True))
        x += w + 7
    if button:
        b.append(f'<rect x="26" y="238" width="152" height="34" rx="10" fill="{G1}" fill-opacity=".10" stroke="{G1}" stroke-opacity=".8"/>')
        b.append(text(44, 260, button, 13, G2, 700))
        b.append(arrow(146, 255, G1))
    else:
        b.append(label(26, 260, foot_label or "PROJECT // ACTIVE", 10.5, DIM))
    b.append(f'<rect x="368" y="242" width="106" height="26" rx="13" fill="{G1}" fill-opacity=".10" stroke="{G1}" stroke-opacity=".5"/>')
    b.append(f'<circle cx="384" cy="255" r="3.4" fill="{G1}"><animate attributeName="opacity" values="1;.3;1" dur="1.7s" repeatCount="indefinite"/></circle>')
    b.append(label(395, 259, "ACTIVE", 10.5, G2, "start", 1.2))
    save(f"card-{slug}.svg", svg(W, H, "".join(b), f"{name} project card"))


def cards():
    art_medikey = (tile(420, 92, 82, "heart", rot=8, dur=6.2, amp=6) +
                   tile(372, 138, 78, f'<g transform="translate(-40,-40)">{qr(0, 0, 80, G4, 5)}</g>', rot=-6, dur=5.4, delay=1.5, amp=6))
    card("MEDIKEY", "medikey", "Digital Medical Identity",
         ["A digital medical identity platform", "designed around QR-based identification,", "medical information management and", "healthcare-oriented identity systems."],
         ["Next.js", "Supabase", "QR", "React", "Tailwind"], art_medikey, None, "IDENTITY // HEALTH // QR")

    art_sign = (tile(408, 104, 108, "hand", rot=4, dur=6.6, amp=6) +
                tile(456, 46, 42, "eye", rot=8, dur=5, delay=1, amp=4) +
                f'<circle cx="352" cy="60" r="3" fill="{G1}" opacity=".7"><animate attributeName="opacity" values=".2;1;.2" dur="2s" repeatCount="indefinite"/></circle>')
    card("SIGNBRIDGE-AI", "signbridge", "Accessibility Interface",
         ["A computer-vision accessibility interface", "using blink detection and hand", "gestures for hands-free digital", "interaction."],
         ["Python", "OpenCV", "MediaPipe", "Flask"], art_sign, "View Project")

    art_air = (f'<path d="M372 104 C 400 40, 450 60, 430 132" stroke="{G1}" stroke-width="1.8" stroke-dasharray="4 6" opacity=".9">'
               f'<animate attributeName="stroke-dashoffset" values="0;-20" dur="1.2s" repeatCount="indefinite"/></path>'
               f'<circle r="4" fill="#fff" filter="url(#glow)"><animateMotion dur="3.2s" repeatCount="indefinite" path="M372 104 C 400 40, 450 60, 430 132"/></circle>'
               + tile(372, 104, 58, "doc", rot=-8, dur=5.4, amp=5) + tile(436, 146, 68, "doc", rot=6, dur=6.4, delay=1.2, amp=6)
               + tile(444, 50, 40, "wifi", rot=4, dur=4.8, delay=.4, amp=4))
    card("AIRSHARE", "airshare", "Gesture Controlled File Sharing",
         ["A gesture-controlled wireless", "file-sharing prototype using computer", "vision and local network", "communication."],
         ["Python", "OpenCV", "MediaPipe", "Flask"], art_air, "View Project")

    art_kala = (tile(410, 100, 92, "store", rot=6, dur=6.2, amp=6) + tile(360, 152, 56, "bag", rot=-8, dur=5.2, delay=1.4, amp=5)
                + f'<path d="M452 40 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3z" fill="{G4}"><animate attributeName="opacity" values=".3;1;.3" dur="2.4s" repeatCount="indefinite"/></path>')
    card("APNI KALA", "apnikala", "Home-Based Creator Marketplace",
         ["A digital platform concept designed", "to connect skilled home-based", "creators with opportunities to", "showcase and sell their work."],
         ["Web", "Marketplace", "Social Impact", "Entrepreneurship"], art_kala, "View Project")


# ================================================================== TECH STACK
def stack():
    W, H = 1000, 360
    b = [bg(W, H, 22)]
    b.append(tile(46, 40, 34, "chip", rot=0, dur=5, amp=3, shadow=False))
    b.append(text(74, 46, "Tech Stack", 18, "#fff", 700))
    b.append(label(184, 46, "TOOLS I WORK WITH", 10.5, DIM))
    b.append(label(976, 46, "15 MODULES LOADED", 10.5, G1, "end"))
    groups = [
        ("INTELLIGENT SYSTEMS", [("AI", "ai"), ("Computer Vision", "eye"), ("OpenCV", "opencv"), ("MediaPipe", "mediapipe")], 20, 66),
        ("DEVELOPMENT", [("Python", "python"), ("JavaScript", "js"), ("React", "react"), ("Next.js", "nextjs"), ("Flask", "flask")], 510, 66),
        ("DATA / INFRASTRUCTURE", [("Supabase", "supabase"), ("Git", "git"), ("GitHub", "github")], 20, 214),
        ("DESIGN", [("Figma", "figma"), ("Framer", "framer"), ("UI/UX", "uiux")], 510, 214),
    ]
    for gi, (title, items, gx, gy) in enumerate(groups):
        b.append(panel(gx, gy, 470, 136, 16))
        b.append(f'<rect x="{gx+20}" y="{gy+18}" width="7" height="7" rx="2" fill="{G1}" filter="url(#glowS)"/>')
        b.append(label(gx + 36, gy + 26, title, 11, G2, "start", 1.6))
        b.append(label(gx + 450, gy + 26, f"{len(items):02d}", 10.5, DIM, "end"))
        for i, (n, ic) in enumerate(items):
            cx_ = gx + 52 + i * 88
            b.append(tile(cx_, gy + 70, 54, ic, rot=(-4 if i % 2 else 4), dur=5 + (i % 3) * .7, delay=i * .8 + gi, amp=4))
            b.append(text(cx_, gy + 122, n, 11.5, MUTED, 500, "middle"))
        used = 52 + len(items) * 88 - 20
        nbars = 6 if len(items) == 4 else (14 if len(items) == 3 else 0)
        if len(items) == 4:
            b.append(bars(gx + 396, gy + 104, 9, 4, 3, 26, G1, gi + 2))
        elif len(items) == 3:
            b.append(bars(gx + 330, gy + 104, 18, 4, 3, 30, G1, gi + 2))
    save("stack.svg", svg(W, H, "".join(b), "Technology stack: intelligent systems, development, data and infrastructure, design"))


# ================================================================== INNOVATION TIMELINE
def innovation():
    W, H = 1000, 212
    b = [bg(W, H, 22)]
    b.append(text(28, 44, "Innovation Pipeline", 18, "#fff", 700))
    b.append(label(214, 44, "SYSTEM TIMELINE // MODULES", 10.5, DIM))
    b.append(label(972, 44, "ALL MODULES ONLINE", 10.5, G1, "end"))
    items = [("HACKATHONS", "Build under", "pressure"), ("RAPID", "PROTOTYPING", "Idea to demo"), ("AI", "EXPERIMENTATION", "Models in practice"),
             ("COMPUTER", "VISION", "Camera as interface"), ("ACCESSIBILITY", "TECHNOLOGY", "Hands-free access"),
             ("SOCIAL", "IMPACT", "Tech for people"), ("PRODUCT", "INNOVATION", "Concept to product")]
    subs = ["Build under pressure", "Idea to working demo", "Models in practice", "Camera as interface",
            "Hands-free access", "Technology for people", "Concept to product"]
    t1 = ["HACKATHONS", "RAPID", "AI", "COMPUTER", "ACCESSIBILITY", "SOCIAL", "PRODUCT"]
    t2 = ["", "PROTOTYPING", "EXPERIMENTATION", "VISION", "TECHNOLOGY", "IMPACT", "INNOVATION"]
    x0, x1, ly = 78, 922, 98
    b.append(f'<path d="M{x0} {ly}H{x1}" stroke="{G1}" stroke-opacity=".25" stroke-width="3" stroke-linecap="round"/>')
    b.append(f'<path d="M{x0} {ly}H{x1}" stroke="url(#greenFill)" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 10" filter="url(#glowS)">'
             f'<animate attributeName="stroke-dashoffset" values="0;-64" dur="3s" repeatCount="indefinite"/></path>')
    b.append(f'<circle r="5" cy="{ly}" fill="#fff" filter="url(#glow)"><animate attributeName="cx" values="{x0};{x1}" dur="7s" repeatCount="indefinite"/></circle>')
    pitch = (x1 - x0) / 6
    for i in range(7):
        x = x0 + i * pitch
        b.append(f'<circle cx="{x:.0f}" cy="{ly}" r="17" fill="{G1}" opacity=".18" filter="url(#blur4)"/>')
        b.append(f'<circle cx="{x:.0f}" cy="{ly}" r="16" fill="#0d2a20" stroke="url(#edge)" stroke-width="1.6"/>')
        b.append(f'<circle cx="{x:.0f}" cy="{ly}" r="16" stroke="{G1}" stroke-width="2" fill="none" opacity="0">'
                 f'<animate attributeName="r" values="16;28" dur="2.4s" begin="{i*.9:.1f}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="opacity" values=".8;0" dur="2.4s" begin="{i*.9:.1f}s" repeatCount="indefinite"/></circle>')
        b.append(text(x, ly + 4.5, f"{i+1:02d}", 12, G1, 700, "middle", True))
        b.append(text(x, ly + 44, t1[i], 12, "#fff", 700, "middle", False, .6))
        if t2[i]:
            b.append(text(x, ly + 59, t2[i], 12, "#fff", 700, "middle", False, .6))
        b.append(text(x, ly + (78 if t2[i] else 63), subs[i], 10.5, MUTED, 400, "middle"))
        b.append(f'<path d="M{x:.0f} {ly-40}V{ly-24}" stroke="{G1}" stroke-opacity=".4"/><circle cx="{x:.0f}" cy="{ly-44}" r="2.6" fill="{G4}"/>')
    save("innovation.svg", svg(W, H, "".join(b), "Innovation pipeline: hackathons, rapid prototyping, AI experimentation, computer vision, accessibility technology, social impact, product innovation"))


# ================================================================== INTERESTS + FOCUS
def focus():
    W, H = 1000, 262
    b = [bg(W, H, 22)]
    b.append(panel(18, 18, 578, 226, 16))
    b.append(text(40, 50, "Areas of Interest", 16, "#fff", 700))
    b.append(label(176, 50, "WHAT DRAWS ME IN", 10, DIM))
    items = [("Artificial\nIntelligence", "chip"), ("Computer\nVision", "eye"), ("Web\nDevelopment", "browser"), ("Product\nDevelopment", "cube"),
             ("UI / UX\nDesign", "uiux"), ("Accessibility\nTechnology", "person"), ("Rapid\nPrototyping", "bolt"), ("Hackathons", "code"),
             ("Digital\nInnovation", "bulb")]
    for i, (n, ic) in enumerate(items):
        r, c = divmod(i, 5)
        cx_ = 74 + c * 112
        cy_ = 96 + r * 84
        b.append(tile(cx_, cy_, 42, ic, rot=(3 if c % 2 else -3), dur=5 + (i % 4) * .6, delay=i * .5, amp=3))
        for j, ln in enumerate(n.split("\n")):
            b.append(text(cx_, cy_ + 41 + j * 12.5, ln, 10.5, MUTED, 500, "middle"))
    b.append(panel(612, 18, 370, 226, 16))
    b.append(text(634, 50, "Current Focus", 16, "#fff", 700))
    b.append(label(752, 50, "WHAT I'M WORKING ON", 10, DIM))
    rows = ["Advanced AI & computer vision projects", "Hackathon participation", "Product development",
            "Learning new technologies", "Building for real-world impact"]
    for i, s in enumerate(rows):
        y = 88 + i * 30
        b.append(f'<circle cx="644" cy="{y}" r="10" fill="{G1}" filter="url(#glowS)"><animate attributeName="opacity" values="1;.65;1" dur="3s" begin="{i*.5}s" repeatCount="indefinite"/></circle>')
        b.append(f'<path d="M639.5 {y}L643 {y+3.6}L649 {y-3.6}" stroke="#062017" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>')
        b.append(text(664, y + 4.5, s, 13, "#EAFFF4", 500))
    save("focus.svg", svg(W, H, "".join(b), "Areas of interest and current focus"))


# ================================================================== FOOTER
def footer():
    W, H = 1000, 248
    rnd = random.Random(4)
    extra = f"""<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d2219"/><stop offset=".7" stop-color="#15493a"/><stop offset="1" stop-color="#2b8f6a"/></linearGradient>
<radialGradient id="sun" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#E8FFF2" stop-opacity=".95"/><stop offset=".25" stop-color="{G4}" stop-opacity=".45"/><stop offset="1" stop-color="{G1}" stop-opacity="0"/></radialGradient>
<clipPath id="fclip"><rect width="{W}" height="{H}" rx="22"/></clipPath>"""
    b = [f'<g clip-path="url(#fclip)"><rect width="{W}" height="{H}" fill="url(#sky)"/>']
    for _ in range(50):
        b.append(f'<circle cx="{rnd.uniform(6,994):.0f}" cy="{rnd.uniform(6,110):.0f}" r="{rnd.choice([.7,1,1.4])}" fill="#fff" opacity=".5">'
                 f'<animate attributeName="opacity" values=".1;.9;.1" dur="{rnd.uniform(2,5):.1f}s" begin="-{rnd.uniform(0,4):.1f}s" repeatCount="indefinite"/></circle>')
    b.append(f'<circle cx="500" cy="176" r="150" fill="url(#sun)"><animate attributeName="r" values="140;158;140" dur="7s" repeatCount="indefinite"/></circle>')

    def ridge(base, amp, seed, fill, op, step=40):
        r = random.Random(seed)
        pts = [(0, H)]
        x = -20
        while x <= W + 20:
            pts.append((x, base - r.uniform(0, amp) * (1 - abs(x - 500) / 900)))
            x += step
        pts += [(W, H)]
        return f'<polygon points="{" ".join(f"{px:.0f},{py:.0f}" for px, py in pts)}" fill="{fill}" fill-opacity="{op}"/>'
    b.append(ridge(178, 90, 21, "#1c6b52", .75, 46))
    b.append(ridge(196, 80, 22, "#0f3d30", .92, 38))
    b.append(ridge(214, 60, 23, "#082018", 1, 34))
    b.append('</g>')
    b.append(f'<rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="22" stroke="url(#edge)" stroke-width="1.5"/>')
    b.append(f'<text x="500" y="70" font-family="{SANS}" font-size="20" font-weight="700" fill="#fff" text-anchor="middle" textLength="560" lengthAdjust="spacing" filter="url(#glowS)">BUILD  •  EXPLORE  •  INNOVATE  •  REPEAT</text>')
    b.append(f'<circle cx="418" cy="100" r="4" fill="{G1}"><animate attributeName="opacity" values="1;.25;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    b.append(f'<text x="430" y="104" font-family="{MONO}" font-size="12" font-weight="700" fill="{G1}" textLength="150" lengthAdjust="spacing" filter="url(#glowS)">SYSTEM STATUS:</text>')
    b.append(f'<text x="588" y="104" font-family="{MONO}" font-size="12" font-weight="700" fill="#fff" textLength="60" lengthAdjust="spacing">ONLINE</text>')
    for i in range(4):
        b.append(f'<rect x="{462+i*20}" y="118" width="16" height="4" rx="2" fill="{G1}"><animate attributeName="opacity" values=".25;1;.25" dur="2s" begin="{i*.35}s" repeatCount="indefinite"/></rect>')
    # bottom bar
    b.append(f'<path d="M0 {H-44}H{W}V{H-22}A22 22 0 0 1 {W-22} {H}H22A22 22 0 0 1 0 {H-22}Z" fill="#03100b" fill-opacity=".82"/>')
    b.append(f'<path d="M0 {H-44.5}H{W}" stroke="{G1}" stroke-opacity=".3"/>')
    b.append(f'<g transform="translate(24 {H-34}) scale(1.3)">{ICONS["github"].replace("translate(-24,-24) scale(3)", "scale(1)")}</g>')
    b.append(text(58, H-17, "Let's build something amazing together", 12.5, MUTED, 500))
    b.append(label(500, H-17, "IDEAS  •  CODE  •  PEOPLE  •  IMPACT", 10.5, G2, "middle", 1.6))
    b.append(text(928, H-17, "Thank you for visiting", 12.5, MUTED, 500, "end"))
    b.append(f'<path d="M958 {H-20}c-6-4-9-7-9-10 0-2 1.6-3.4 3.4-3.4 1.4 0 2.6.8 3.2 1.9.6-1.1 1.8-1.9 3.2-1.9 1.8 0 3.4 1.4 3.4 3.4 0 3-3 6-9 10z" fill="{G1}" transform="translate(-6 2)"><animate attributeName="opacity" values="1;.5;1" dur="1.4s" repeatCount="indefinite"/></path>')
    save("footer.svg", svg(W, H, "".join(b), "Build, explore, innovate, repeat - system status online", extra))


if __name__ == "__main__":
    hero(); profile(); cards(); stack(); innovation(); focus(); footer()
