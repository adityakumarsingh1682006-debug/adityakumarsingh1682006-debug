"""svgkit - shared helpers for the profile's hand-built SVG interface.
Everything here is plain SVG (no scripts, no external requests) so it renders on GitHub."""
import html
import random

G1, G2, G3, G4 = "#39FF88", "#65FFB0", "#00FFC6", "#7CFFD4"
TXT, MUTED, DIM = "#F1FFF7", "#B9D9CB", "#86AC9B"
SANS = "'SF Pro Display','Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','SF Mono',Menlo,Consolas,'DejaVu Sans Mono',monospace"


def esc(s):
    return html.escape(str(s), quote=False)


DEFS = f"""
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#112a21"/><stop offset=".55" stop-color="#0d1f18"/><stop offset="1" stop-color="#0a1712"/></linearGradient>
<radialGradient id="bgGlow" cx=".5" cy=".25" r=".75"><stop offset="0" stop-color="{G1}" stop-opacity=".20"/><stop offset="1" stop-color="{G1}" stop-opacity="0"/></radialGradient>
<linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".13"/><stop offset="1" stop-color="#fff" stop-opacity=".03"/></linearGradient>
<linearGradient id="edge" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{G4}" stop-opacity=".8"/><stop offset=".5" stop-color="{G1}" stop-opacity=".2"/><stop offset="1" stop-color="{G3}" stop-opacity=".6"/></linearGradient>
<linearGradient id="greenText" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="{G2}"/><stop offset="1" stop-color="{G1}"/></linearGradient>
<linearGradient id="greenFill" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{G3}"/><stop offset="1" stop-color="{G1}"/></linearGradient>
<linearGradient id="tileFace" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A8FFD6" stop-opacity=".30"/><stop offset=".5" stop-color="{G1}" stop-opacity=".07"/><stop offset="1" stop-color="{G3}" stop-opacity=".18"/></linearGradient>
<filter id="glow" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="glowS" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="blur4" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
<filter id="blur10" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="blur22" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="22"/></filter>
<filter id="shadow" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" flood-opacity=".45"/></filter>
<pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" stroke="{G1}" stroke-opacity=".055" stroke-width="1"/></pattern>
"""


def svg(w, h, body, title="", extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'fill="none" role="img" aria-label="{esc(title)}">\n<title>{esc(title)}</title>\n'
            f'<defs>{DEFS}{extra_defs}</defs>\n{body}\n</svg>\n')


def bg(w, h, r=22):
    return (f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#bg)"/>'
            f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#bgGlow)"/>'
            f'<rect width="{w}" height="{h}" rx="{r}" fill="url(#grid)"/>'
            f'<rect x=".75" y=".75" width="{w-1.5}" height="{h-1.5}" rx="{r}" stroke="url(#edge)" stroke-width="1.5"/>')


def panel(x, y, w, h, r=18, dark=.62):
    return (f'<g filter="url(#shadow)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="#081711" fill-opacity="{dark}"/></g>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#glass)" stroke="url(#edge)" stroke-width="1.2"/>'
            f'<path d="M{x+r} {y+.8}H{x+w-r}" stroke="#fff" stroke-opacity=".22" stroke-linecap="round"/>')


def text(x, y, s, size=12, fill=TXT, weight=400, anchor="start", mono=False, ls=0, extra=""):
    fam = MONO if mono else SANS
    lsx = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{lsx} {extra}>{esc(s)}</text>')


def label(x, y, s, size=10.5, fill=G1, anchor="start", ls=1.4):
    return text(x, y, s, size, fill, 600, anchor, True, ls)


def pill(x, y, w, h, s, color=G1, size=11, mono=True, dot=False, weight=600, fill_op=.10):
    tx = x + w / 2 + (7 if dot else 0)
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}" fill="{color}" fill-opacity="{fill_op}" '
           f'stroke="{color}" stroke-opacity=".55"/>')
    if dot:
        out += (f'<circle cx="{x+13}" cy="{y+h/2}" r="3.2" fill="{color}"><animate attributeName="opacity" '
                f'values="1;.25;1" dur="1.8s" repeatCount="indefinite"/></circle>')
    out += text(tx, y + h / 2 + size * .36, s, size, G2 if color == G1 else color, weight, "middle", mono, .6 if mono else 0)
    return out


def arrow(x, y, color=G1, s=1):
    return (f'<path d="M{x} {y}H{x+12*s}M{x+8*s} {y-4*s}L{x+12*s} {y}L{x+8*s} {y+4*s}" stroke="{color}" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def qr(x, y, size, color=G4, seed=5):
    """decorative QR-like pattern (not a functional code)"""
    n = 11
    c = size / n
    out = []
    rnd = random.Random(seed)

    def finder(fx, fy):
        return (f'<rect x="{x+fx*c:.1f}" y="{y+fy*c:.1f}" width="{3*c:.1f}" height="{3*c:.1f}" rx="{c*.5:.1f}" stroke="{color}" stroke-width="{c*.55:.1f}"/>'
                f'<rect x="{x+(fx+1)*c+c*.05:.1f}" y="{y+(fy+1)*c+c*.05:.1f}" width="{c*.9:.1f}" height="{c*.9:.1f}" fill="{color}"/>')
    out.append(finder(0, 0)); out.append(finder(n - 3, 0)); out.append(finder(0, n - 3))
    for i in range(n):
        for j in range(n):
            if (i < 4 and j < 4) or (i > n - 5 and j < 4) or (i < 4 and j > n - 5):
                continue
            if rnd.random() > .52:
                out.append(f'<rect x="{x+i*c+c*.08:.1f}" y="{y+j*c+c*.08:.1f}" width="{c*.84:.1f}" height="{c*.84:.1f}" rx="{c*.18:.1f}" fill="{color}"/>')
    return "".join(out)


# ------------------------------------------------------------------ icons (centred, +-28 box)
ICONS = {
    "python": ('<g stroke-linecap="round" stroke-linejoin="round" stroke-width="10">'
               '<path d="M-17,3 V-9 Q-17,-19 -7,-19 H5 Q13,-19 13,-11 V-5 Q13,1 7,1 H-8" stroke="#5FA4E6"/>'
               '<path d="M17,-3 V9 Q17,19 7,19 H-5 Q-13,19 -13,11 V5 Q-13,-1 -7,-1 H8" stroke="#FFD24A"/></g>'
               '<circle cx="-4" cy="-12" r="2" fill="#fff"/><circle cx="4" cy="12" r="2" fill="#fff"/>'),
    "ai": (f'<path d="M-2,-24 L2,-8 L18,-4 L2,0 L-2,16 L-6,0 L-22,-4 L-6,-8Z" fill="url(#greenText)" filter="url(#glowS)"/>'
           f'<path d="M14,10 L16,16 L22,18 L16,20 L14,26 L12,20 L6,18 L12,16Z" fill="{G4}"/>'),
    "opencv": ('<g stroke-width="8" fill="none"><circle cx="0" cy="-12" r="9" stroke="#FF5A5A"/>'
               '<circle cx="-13" cy="11" r="9" stroke="#3DDC84"/><circle cx="13" cy="11" r="9" stroke="#5B9BFF"/></g>'),
    "mediapipe": (f'<g stroke="{G1}" stroke-width="2.4" stroke-linecap="round"><path d="M-16,14 L-10,-4 L2,-20 L14,-6 L12,12 Z M-10,-4 L14,-6 M2,-20 L-2,6"/></g>'
                  f'<g fill="#fff"><circle cx="-16" cy="14" r="4"/><circle cx="-10" cy="-4" r="4"/><circle cx="2" cy="-20" r="4"/>'
                  f'<circle cx="14" cy="-6" r="4"/><circle cx="12" cy="12" r="4"/><circle cx="-2" cy="6" r="3.2" fill="{G1}"/></g>'),
    "react": ('<g stroke="#61DAFB" stroke-width="2.6" fill="none"><ellipse rx="24" ry="9.5"/>'
              '<ellipse rx="24" ry="9.5" transform="rotate(60)"/><ellipse rx="24" ry="9.5" transform="rotate(120)"/></g>'
              '<circle r="4.4" fill="#61DAFB"/>'),
    "nextjs": ('<circle r="23" fill="#fff"/><text x="0" y="8.5" font-family="Arial,Helvetica,sans-serif" font-size="26" font-weight="800" fill="#0b0b0b" text-anchor="middle">N</text>'),
    "figma": ('<path d="M0,-21 h-7 a7,7 0 0 0 0,14 h7z" fill="#F24E1E"/><path d="M0,-21 h7 a7,7 0 0 1 0,14 h-7z" fill="#FF7262"/>'
              '<path d="M0,-7 h-7 a7,7 0 0 0 0,14 h7z" fill="#A259FF"/><circle cx="7" cy="0" r="7" fill="#1ABCFE"/>'
              '<path d="M0,7 h-7 a7,7 0 1 0 7,7z" fill="#0ACF83"/>'),
    "supabase": ('<path d="M7,-26 L-17,3 H-3 L-7,26 L17,-4 H3 Z" fill="#3ECF8E"/>'
                 '<path d="M7,-26 L-3,3 H-17Z" fill="#fff" opacity=".22"/>'),
    "github": '<path transform="translate(-24,-24) scale(3)" fill="#fff" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>',
    "js": ('<rect x="-22" y="-22" width="44" height="44" rx="6" fill="#F7DF1E"/>'
           '<text x="16" y="16" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="800" fill="#111" text-anchor="end">JS</text>'),
    "flask": (f'<path d="M-6,-24 H6 M-4,-24 V-8 L-19,18 Q-22,25 -14,25 H14 Q22,25 19,18 L4,-8 V-24" stroke="#fff" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>'
              f'<path d="M-12,8 H12 L18,19 Q20,23 14,23 H-14 Q-20,23 -18,19Z" fill="{G1}" opacity=".9"/>'),
    "git": ('<g transform="rotate(45)"><rect x="-19" y="-19" width="38" height="38" rx="7" fill="#F05133"/></g>'
            '<g stroke="#fff" stroke-width="3" stroke-linecap="round"><path d="M-5,-7 V8 M-5,-7 L8,2"/></g>'
            '<g fill="#fff"><circle cx="-5" cy="-8" r="4"/><circle cx="-5" cy="9" r="4"/><circle cx="9" cy="2.5" r="4"/></g>'),
    "framer": '<path d="M-13,-24 H13 V-11 H0 Z M-13,-11 H0 L13,2 H-13 Z M-13,2 H0 V15 Z" fill="#fff"/>',
    "uiux": (f'<rect x="-22" y="-20" width="30" height="24" rx="5" stroke="{G4}" stroke-width="2.6"/>'
             f'<path d="M4,-2 L26,10 L16,12 L21,22 L16,24 L11,14 L4,20Z" fill="{G1}" stroke="#062017" stroke-width="1.6" stroke-linejoin="round"/>'),
    "eye": (f'<path d="M-25,0 Q0,-24 25,0 Q0,24 -25,0Z" stroke="{G1}" stroke-width="3" stroke-linejoin="round"/>'
            f'<circle r="8" fill="{G4}"/><circle r="3.2" fill="#062017"/>'),
    "chip": (f'<rect x="-14" y="-14" width="28" height="28" rx="5" stroke="{G1}" stroke-width="2.8"/>'
             f'<rect x="-6" y="-6" width="12" height="12" rx="2" fill="{G4}"/>'
             f'<path d="M-6,-22V-14M6,-22V-14M-6,14V22M6,14V22M-22,-6H-14M-22,6H-14M14,-6H22M14,6H22" stroke="{G1}" stroke-width="2.6" stroke-linecap="round"/>'),
    "browser": (f'<rect x="-24" y="-19" width="48" height="38" rx="6" stroke="{G1}" stroke-width="2.8"/>'
                f'<path d="M-24,-8H24" stroke="{G1}" stroke-width="2.4"/><circle cx="-17" cy="-13.5" r="1.8" fill="{G4}"/><circle cx="-11" cy="-13.5" r="1.8" fill="{G4}"/>'
                f'<path d="M-10,4 L-16,9 L-10,14 M10,4 L16,9 L10,14 M3,2 L-3,16" stroke="{G4}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'),
    "cube": (f'<path d="M0,-24 L21,-12 V12 L0,24 L-21,12 V-12Z" stroke="{G1}" stroke-width="2.8" stroke-linejoin="round"/>'
             f'<path d="M0,0 V24 M0,0 L-21,-12 M0,0 L21,-12" stroke="{G4}" stroke-width="2.4" stroke-linejoin="round"/>'),
    "person": (f'<circle cy="-18" r="6" fill="{G1}"/>'
               f'<path d="M-20,-6 H20 M0,-6 V8 M0,8 L-11,24 M0,8 L11,24" stroke="{G1}" stroke-width="3.4" stroke-linecap="round"/>'),
    "bolt": f'<path d="M8,-26 L-14,4 H-2 L-6,26 L16,-6 H3 Z" fill="none" stroke="{G1}" stroke-width="3" stroke-linejoin="round"/>',
    "code": (f'<path d="M-12,-14 L-24,0 L-12,14 M12,-14 L24,0 L12,14" stroke="{G1}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<path d="M4,-20 L-4,20" stroke="{G4}" stroke-width="3.2" stroke-linecap="round"/>'),
    "bulb": (f'<path d="M0,-24 A14,14 0 0 0 -7,2 Q-9,8 -9,12 H9 Q9,8 7,2 A14,14 0 0 0 0,-24Z" stroke="{G1}" stroke-width="2.8" stroke-linejoin="round"/>'
             f'<path d="M-6,19 H6 M-4,24 H4" stroke="{G4}" stroke-width="2.8" stroke-linecap="round"/>'),
    "heart": ('<defs><linearGradient id="hg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#C9FFE6"/><stop offset="1" stop-color="#39FF88"/></linearGradient></defs>'
              '<path d="M0,22 C-34,0 -26,-24 -12,-24 C-4,-24 0,-17 0,-13 C0,-17 4,-24 12,-24 C26,-24 34,0 0,22Z" fill="url(#hg)" fill-opacity=".9"/>'
              '<path d="M-22,-2 H-8 L-4,-10 L2,8 L6,-2 H22" stroke="#0A2B1F" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'),
    "hand": (f'<g stroke="{G4}" stroke-width="5.4" stroke-linecap="round" fill="none"><path d="M-14,4 L-25,-8 M-8,-4 L-10,-24 M0,-6 L0,-28 M8,-4 L10,-24 M15,2 L21,-14"/></g>'
             f'<rect x="-16" y="-8" width="32" height="34" rx="14" fill="#0d2a20" stroke="{G4}" stroke-width="2.6"/>'
             f'<g fill="#fff"><circle cx="-25" cy="-8" r="2.8"/><circle cx="-10" cy="-24" r="2.8"/><circle cx="0" cy="-28" r="2.8"/><circle cx="10" cy="-24" r="2.8"/><circle cx="21" cy="-14" r="2.8"/></g>'),
    "doc": (f'<path d="M-16,-24 H6 L18,-12 V24 H-16Z" fill="#0d2a20" stroke="{G1}" stroke-width="2.6" stroke-linejoin="round"/>'
            f'<path d="M6,-24 V-12 H18" stroke="{G1}" stroke-width="2.4" stroke-linejoin="round"/>'
            f'<path d="M-9,2 H11 M-9,10 H11 M-9,18 H3" stroke="{G4}" stroke-width="2.6" stroke-linecap="round"/>'),
    "store": (f'<path d="M-24,-6 L-19,-22 H19 L24,-6 Z" fill="{G1}" fill-opacity=".85"/>'
              f'<path d="M-24,-6 Q-16,4 -8,-6 Q0,4 8,-6 Q16,4 24,-6" stroke="#0a2b1f" stroke-width="2.4"/>'
              f'<rect x="-19" y="0" width="38" height="24" rx="3" stroke="{G4}" stroke-width="2.6"/>'
              f'<rect x="-6" y="8" width="12" height="16" rx="2" fill="{G4}"/>'),
    "bag": (f'<rect x="-18" y="-8" width="36" height="32" rx="7" fill="#0d2a20" stroke="{G1}" stroke-width="2.8"/>'
            f'<path d="M-8,-8 V-14 A8,8 0 0 1 8,-14 V-8" stroke="{G4}" stroke-width="2.8" stroke-linecap="round"/>'
            f'<path d="M0,3 L2.8,9 L9,9.8 L4.4,14 L5.6,20 L0,17 L-5.6,20 L-4.4,14 L-9,9.8 L-2.8,9Z" fill="{G1}"/>'),
    "wifi": (f'<g stroke="{G1}" stroke-width="3" stroke-linecap="round" fill="none"><path d="M-20,-4 A28,28 0 0 1 20,-4"/><path d="M-12,4 A16,16 0 0 1 12,4"/></g>'
             f'<circle cy="14" r="3.6" fill="{G4}"/>'),
}


def tile(cx, cy, s, icon, rot=0, skew=-5, dur=6.0, delay=0.0, amp=7, glow=G1, shadow=True):
    """A floating 3D-looking glass tile: extrusion, glass face, rim light, floor shadow, gentle bob."""
    h = s / 2
    r = s * .26
    d = s * .11
    ic = ICONS[icon] if icon in ICONS else icon
    floor = (f'<ellipse cx="0" cy="{s*.72:.1f}" rx="{s*.42:.1f}" ry="{s*.07:.1f}" fill="{glow}" opacity=".30" filter="url(#blur4)"/>'
             if shadow else "")
    return (f'<g transform="translate({cx} {cy})"><g>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -{amp};0 0" keyTimes="0;.5;1" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" dur="{dur}s" begin="-{delay}s" repeatCount="indefinite"/>'
            f'{floor}<g transform="rotate({rot}) skewY({skew})">'
            f'<rect x="{-h}" y="{-h+d:.1f}" width="{s}" height="{s}" rx="{r:.1f}" fill="#03100a" stroke="{glow}" stroke-opacity=".4"/>'
            f'<rect x="{-h}" y="{-h}" width="{s}" height="{s}" rx="{r:.1f}" fill="#0f2f24" fill-opacity=".94"/>'
            f'<rect x="{-h}" y="{-h}" width="{s}" height="{s}" rx="{r:.1f}" fill="url(#tileFace)" stroke="url(#edge)" stroke-width="1.4"/>'
            f'<path d="M{-h+r:.1f} {-h+1.6:.1f}H{h-r:.1f}" stroke="#fff" stroke-opacity=".4" stroke-linecap="round"/>'
            f'<ellipse cx="{-s*.18:.1f}" cy="{-s*.32:.1f}" rx="{s*.28:.1f}" ry="{s*.1:.1f}" fill="#fff" opacity=".11" transform="rotate(-18 {-s*.18:.1f} {-s*.32:.1f})"/>'
            f'<g transform="scale({s/100:.3f})">{ic}</g></g></g></g>')


def bars(x, y, n, w=4, gap=3, hmax=22, color=G1, seed=3):
    """tiny animated equaliser, purely decorative"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        hh = rnd.uniform(.35, 1) * hmax
        lo = rnd.uniform(.2, .5) * hmax
        dur = f"{rnd.uniform(1.4, 3):.1f}s"
        bx = x + i * (w + gap)
        out.append(f'<rect x="{bx}" y="{y-hh:.1f}" width="{w}" height="{hh:.1f}" rx="1.5" fill="{color}" opacity=".85">'
                   f'<animate attributeName="height" values="{hh:.1f};{lo:.1f};{hh:.1f}" dur="{dur}" repeatCount="indefinite"/>'
                   f'<animate attributeName="y" values="{y-hh:.1f};{y-lo:.1f};{y-hh:.1f}" dur="{dur}" repeatCount="indefinite"/></rect>')
    return "".join(out)
