"""Python port of the ASKO branch generator (same geometry as asko-vetvi.html)."""
import math

COL = {'copper': '#B8764B', 'copperL': '#E0B08A', 'copperD': '#8C5532', 'steel': '#8B919B',
       'white': '#F6F4F0', 'concrete': '#E3E1DC', 'graphite': '#17191E'}

DEF = dict(n=3, sides='right', stem=False, stemExtra=120, stemColor='steel', bend='arc', arc=55, arcVar=35, angle=6,
           len=560, lenMode='random', lenVar=15, step=260, start=520, spacing='even', cluster=65, sw=1.3, gap=4,
           colors=['steel', 'copperL'], combo='alt', tip='none', tipSize=100, bg='graphite', seed=11, glow=90, glowSize=75)

# v3 «Листья»: тонкая линия + мягкий свет внутри изгиба; медь и сталь
PRESETS = {
    'Лист': {},
    'Пара': dict(n=2, colors=['copperL', 'steel'], arc=60, arcVar=25, step=300, start=600, seed=4),
    'Крона': dict(n=5, sides='both', stem=True, stemExtra=140, arc=45, arcVar=30, angle=10, len=480, step=150, start=480,
                  colors=['copperL', 'steel'], glow=75, seed=5),
    'Росток': dict(n=2, sides='both', stem=True, stemExtra=60, arc=30, arcVar=10, angle=24, len=260, lenMode='equal',
                   step=40, start=200, colors=['copperL'], combo='one', glow=80, glowSize=70, sw=1.6),
    'Поток': dict(n=8, arc=70, arcVar=40, angle=3, len=700, lenVar=30, step=110, start=300, spacing='cluster', cluster=50,
                  glow=55, glowSize=60, colors=['steel', 'copperL', 'steel'], seed=8),
    'Блокчейн': dict(n=6, sides='both', stem=True, stemExtra=80, bend='corner', angle=34, len=300, lenMode='shrink',
                     lenVar=40, step=150, start=320, tip='square', tipSize=70, colors=['copperL', 'steel'], glow=0),
}


def rng(seed):
    a = [seed & 0xFFFFFFFF]

    def imul(x, y):
        return ((x & 0xFFFFFFFF) * (y & 0xFFFFFFFF)) & 0xFFFFFFFF

    def r():
        a[0] = (a[0] + 0x6D2B79F5) & 0xFFFFFFFF
        t = a[0]
        t = imul(t ^ (t >> 15), 1 | t)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & 0xFFFFFFFF) ^ t
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296
    return r


def _mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(A, B))


def f(v):
    return round(v, 1)


def preset(name, **over):
    p = dict(DEF)
    p.update(PRESETS[name])
    p.update(over)
    return p


def build(S, bg=None):
    """Return (svg_inner, box) in world coords: trunk base at (0,0), tree grows to -y."""
    R = rng(S['seed']); R2 = rng(S['seed'] * 7 + 3); R3 = rng(S['seed'] * 13 + 5); R4 = rng(S['seed'] * 17 + 9)
    glow = S.get('glow', 0) / 100; gsz = S.get('glowSize', 60) / 100; gdefs = ''; glows = ''; uid = S.get('uid', 'g')
    n, sw = S['n'], S['sw']
    gap = sw + S['gap']
    bgHex = bg if bg else ({'graphite': '#17191E', 'white': '#F6F4F0', 'concrete': '#E3E1DC', 'copper': '#B8764B'}.get(S['bg'], 'none'))
    box = [math.inf, math.inf, -math.inf, -math.inf]

    def grow(x, y, r):
        box[0] = min(box[0], x - r); box[2] = max(box[2], x + r)
        box[1] = min(box[1], y - r); box[3] = max(box[3], y + r)
    side = [(-1 if S['sides'] == 'left' else 1 if S['sides'] == 'right' else (-1 if i % 2 == 0 else 1)) for i in range(n)]
    gaps = []
    for i in range(1, n):
        if S['spacing'] == 'even':
            gaps.append(S['step'])
        else:
            c = S['cluster'] / 100
            gaps.append(S['step'] * (1 - 0.85 * c) * (0.4 + R() * 0.6) if R() < 0.35 + 0.55 * c else S['step'] * (1 + 2.5 * c) * (0.6 + R() * 0.8))
    if S['spacing'] == 'cluster' and gaps:
        sm = sum(gaps) or 1; tgt = S['step'] * (n - 1)
        gaps = [g * tgt / sm for g in gaps]
    p = [S['start']]
    for g in gaps:
        p.append(p[-1] + g)
    minSep = max(gap * 1.15, sw * 1.5)
    for s in (-1, 1):
        last = -1e9
        for i in range(n):
            if side[i] != s:
                continue
            if p[i] < last + minSep:
                p[i] = last + minSep
            last = p[i]
    lens = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 1; v = S['lenVar'] / 100; L = S['len']
        if S['lenMode'] == 'grow': L = S['len'] * (1 - v + v * t)
        elif S['lenMode'] == 'shrink': L = S['len'] * (1 - v * t)
        elif S['lenMode'] == 'random': L = S['len'] * (1 - v + 2 * v * R2())
        lens.append(max(10, L))
    pal = [COL[k] for k in (S['colors'] or ['copper'])]
    cols = []
    for i in range(n):
        if S['combo'] == 'one': cols.append(pal[0])
        elif S['combo'] == 'alt': cols.append(pal[i % len(pal)])
        elif S['combo'] == 'random': cols.append(pal[int(R3() * len(pal))])
        else:
            t = i / (n - 1) if n > 1 else 0
            if len(pal) == 1: cols.append(pal[0])
            else:
                seg = t * (len(pal) - 1); k = min(len(pal) - 2, int(seg)); cols.append(_mix(pal[k], pal[k + 1], seg - k))
    xs = [0] * n
    for s in (-1, 1):
        idx = [i for i in range(n) if side[i] == s]
        k = len(idx); off = gap if S['stem'] else gap / 2
        for j, i in enumerate(idx):
            xs[i] = s * (off + (k - 1 - j) * gap)
    tipS = S['tipSize'] / 100; hs = sw / 2
    fillbg = 'none' if bgHex == 'none' else bgHex

    def tip(x, y, c):
        r = 0; out = ''
        t = S['tip']
        if t == 'dot':
            r = sw * 1.9 * tipS; out = f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{c}"/>'
        elif t == 'square':
            a = sw * 3.6 * tipS; r = a / 2; out = f'<rect x="{f(x-a/2)}" y="{f(y-a/2)}" width="{f(a)}" height="{f(a)}" fill="{c}"/>'
        elif t == 'node':
            a = sw * 4.6 * tipS; r = a / 2 + hs; out = f'<rect x="{f(x-a/2)}" y="{f(y-a/2)}" width="{f(a)}" height="{f(a)}" fill="{fillbg}" stroke="{c}" stroke-width="{f(sw)}"/>'
        elif t == 'ring':
            r = sw * 2.6 * tipS; out = f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fillbg}" stroke="{c}" stroke-width="{f(sw)}"/>'; r += hs
        grow(x, y, max(r, hs)); return out
    th = (90 - S['angle']) * math.pi / 180
    paths = ''; tips = ''; topY = 0
    cap = 'round' if S['tip'] == 'none' else 'butt'
    for i in range(n):
        s = side[i]; x = xs[i]; yd = -p[i]; L = lens[i]; c = cols[i]
        d = f'M{f(x)} 0 L{f(x)} {f(yd)}'
        grow(x, 0, hs); grow(x, yd, hs)
        if S['bend'] == 'corner' or S['arc'] == 0:
            a = S['angle'] * math.pi / 180; ex = x + s * L * math.cos(a); ey = yd - L * math.sin(a); d += f' L{f(ex)} {f(ey)}'
        else:
            Rr = (8 + S['arc'] / 100 * 620) * (1 - S.get('arcVar', 0) / 100 + 2 * S.get('arcVar', 0) / 100 * R4()); arcLen = Rr * th
            phi = L / Rr if L < arcLen else th; rest = max(0, L - arcLen)
            for k in range(1, 17):
                a = phi * k / 16; grow(x + s * (Rr - Rr * math.cos(a)), yd - Rr * math.sin(a), hs)
            ax = x + s * (Rr - Rr * math.cos(phi)); ay = yd - Rr * math.sin(phi)
            d += f' A{f(Rr)} {f(Rr)} 0 0 {1 if s > 0 else 0} {f(ax)} {f(ay)}'
            ex = ax + rest * s * math.sin(phi); ey = ay - rest * math.cos(phi)
            if rest > 0: d += f' L{f(ex)} {f(ey)}'
            if glow > 0:
                gi = f'{uid}{i}'; GW = Rr * gsz; B = Rr * 3
                down = yd + Rr * 0.7
                gpath = f'M{f(x)} {f(down)} L{f(x)} {f(yd)} A{f(Rr)} {f(Rr)} 0 0 {1 if s > 0 else 0} {f(ax)} {f(ay)}' + (f' L{f(ex)} {f(ey)}' if rest > 0 else '')
                clip = (f'M{f(x)} {f(yd + B)} L{f(x)} {f(yd)} A{f(Rr)} {f(Rr)} 0 0 {1 if s > 0 else 0} {f(ax)} {f(ay)}'
                        + (f' L{f(ex)} {f(ey)}' if rest > 0 else '') + f' L{f(ex + s * B)} {f(ey)} L{f(ex + s * B)} {f(yd + B)} Z')
                gdefs += (f'<clipPath id="{gi}c"><path d="{clip}"/></clipPath>'
                          f'<filter id="{gi}f" filterUnits="userSpaceOnUse" x="{f(x - B)}" y="{f(ey - B)}" width="{f(2 * B + abs(ex - x) + B)}" height="{f(3 * B)}"><feGaussianBlur stdDeviation="{f(GW * 0.32)}"/></filter>'
                          f'<linearGradient id="{gi}t" gradientUnits="userSpaceOnUse" x1="{f(x)}" y1="{f(yd)}" x2="{f(ex)}" y2="{f(ey)}"><stop offset="0" stop-color="#fff"/><stop offset=".45" stop-color="#fff" stop-opacity=".85"/><stop offset=".9" stop-color="#fff" stop-opacity="0"/></linearGradient>'
                          f'<linearGradient id="{gi}v" gradientUnits="userSpaceOnUse" x1="0" y1="{f(down)}" x2="0" y2="{f(yd - Rr * 0.3)}"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient>'
                          f'<mask id="{gi}m" maskUnits="userSpaceOnUse" x="{f(x - B)}" y="{f(ey - B)}" width="{f(2 * B + abs(ex - x) + B)}" height="{f(3 * B)}"><rect x="{f(x - B)}" y="{f(ey - B)}" width="{f(2 * B + abs(ex - x) + B)}" height="{f(3 * B)}" fill="url(#{gi}t)"/></mask>'
                          f'<mask id="{gi}n" maskUnits="userSpaceOnUse" x="{f(x - B)}" y="{f(ey - B)}" width="{f(2 * B + abs(ex - x) + B)}" height="{f(3 * B)}"><rect x="{f(x - B)}" y="{f(ey - B)}" width="{f(2 * B + abs(ex - x) + B)}" height="{f(3 * B)}" fill="url(#{gi}v)"/></mask>')
                glows += (f'<g clip-path="url(#{gi}c)"><g mask="url(#{gi}m)"><g mask="url(#{gi}n)">'
                          f'<path d="{gpath}" fill="none" stroke="{c}" stroke-opacity="{round(glow,3)}" stroke-width="{f(GW)}" filter="url(#{gi}f)"/></g></g></g>')
        grow(ex, ey, hs); topY = min(topY, ey, yd)
        paths += f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{f(sw)}" stroke-linecap="{cap}" stroke-linejoin="round"/>'
        tips += tip(ex, ey, c)
    stem = ''
    if S['stem']:
        top = topY - S['stemExtra']; sc = COL[S['stemColor']]
        grow(0, 0, hs); grow(0, top, hs)
        stem = f'<line x1="0" y1="0" x2="0" y2="{f(top)}" stroke="{sc}" stroke-width="{f(sw)}" stroke-linecap="{cap}"/>' + tip(0, top, sc)
    box[3] = 0
    pre = (f'<defs>{gdefs}</defs>' + glows) if glows else ''
    return pre + stem + paths + tips, box


def place(S, cx, base_y, height=None, width=None, bg=None, extend=0):
    """Place a tree with its trunk base at (cx, base_y), scaled to fit height/width. extend: extra trunk below base (in px, after scale)."""
    inner, b = build(S, bg)
    h = b[3] - b[1]; w = b[2] - b[0]
    k = 1.0
    if height: k = height / h
    if width: k = min(k, width / w) if height else width / w
    ext = ''
    if extend:
        # draw trunk lines below base by stretching: simple approach — translate copy of trunk segment
        pass
    return f'<g transform="translate({f(cx)} {f(base_y)}) scale({round(k,4)})">{inner}</g>', k, b


def trunk_extension(S, length):
    """Vertical continuation of all strands below base (world coords, 0..length)."""
    n, sw = S['n'], S['sw']; gap = sw + S['gap']
    side = [(-1 if S['sides'] == 'left' else 1 if S['sides'] == 'right' else (-1 if i % 2 == 0 else 1)) for i in range(n)]
    inner, _ = build(S)
    # reuse colors by parsing strokes in order is complex; recompute xs/colors
    import re
    xs = re.findall(r'<path d="M(-?[\d.]+) 0', inner)
    cs = re.findall(r'stroke="(#[0-9A-Fa-f]{6})" stroke-width', inner)
    out = ''
    if S['stem']:
        out += f'<line x1="0" y1="0" x2="0" y2="{length}" stroke="{COL[S["stemColor"]]}" stroke-width="{sw}"/>'
        cs = cs[1:]
    for x, c in zip(xs, cs):
        out += f'<line x1="{x}" y1="0" x2="{x}" y2="{length}" stroke="{c}" stroke-width="{sw}"/>'
    return out
