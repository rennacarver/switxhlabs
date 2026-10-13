"""Blend: the current switxhlabs letterforms (four-arm x, notched h) with the sketch logo's hand-cut wobble and lime marker scribble."""
import math, random, re, sys

SRC, OUTDIR = sys.argv[1], sys.argv[2]
src = open(SRC).read()
paths = dict((fill, d) for d, fill in re.findall(r'<path d="([^"]+)" fill="(#[0-9a-f]+)"', src))
INK_D, LIME_D, MUTED_D = paths["#17221f"], paths["#c5ec45"], paths["#58635b"]

PAL = {
    "light": dict(ink="#17221f", muted="#58635b", lime="#c5ec45"),
    "dark":  dict(ink="#edf3ee", muted="#aeb9b1", lime="#c5ec45"),
}
X_INK = "#17221f"   # the x sits on lime in both modes, so it stays dark

# ---------- parse M/C/Z paths into flattened subpaths ---------------------------
def subpaths(d, steps=10):
    toks = re.findall(r'[MCZ]|-?\d*\.?\d+', d)
    out, cur, i, pos = [], None, 0, None
    while i < len(toks):
        t = toks[i]
        if t == "M":
            pos = (float(toks[i + 1]), float(toks[i + 2])); cur = [pos]; out.append(cur); i += 3
        elif t == "C":
            i += 1
            while i < len(toks) and toks[i] not in "MCZ":
                p1 = (float(toks[i]), float(toks[i + 1])); p2 = (float(toks[i + 2]), float(toks[i + 3])); p3 = (float(toks[i + 4]), float(toks[i + 5]))
                p0 = pos
                for k in range(1, steps + 1):
                    s = k / steps; u = 1 - s
                    cur.append((u**3*p0[0] + 3*u*u*s*p1[0] + 3*u*s*s*p2[0] + s**3*p3[0],
                                u**3*p0[1] + 3*u*u*s*p1[1] + 3*u*s*s*p2[1] + s**3*p3[1]))
                pos = p3; i += 6
        else:
            i += 1
    return out

def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def area(pts):
    return abs(sum(pts[k][0] * pts[k - 1][1] - pts[k - 1][0] * pts[k][1] for k in range(len(pts)))) / 2

class Noise:
    def __init__(self, seed, scale):
        r = random.Random(seed)
        self.waves = [(r.uniform(0, 2 * math.pi), f, r.uniform(0, 2 * math.pi), a)
                      for f, a in ((0.6, 1.0), (1.3, 0.55), (2.9, 0.25), (6.5, 0.12))]
        self.scale = scale
    def __call__(self, x, y):
        return sum(a * math.sin(f * (x * math.cos(th) + y * math.sin(th)) / self.scale + ph)
                   for th, f, ph, a in self.waves) / 1.92

NX, NY = Noise(11, 10.0), Noise(23, 10.0)
AMP = 0.75     # letters are ~80 units at x-height: about 1% wobble

def wobble(pts, amp=None):
    a = AMP if amp is None else amp
    return [(x + a * NX(x, y), y + a * NY(x, y)) for x, y in pts]

def d_of(polys):
    return "".join("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in p) + "Z" for p in polys)

ink = [p for p in subpaths(INK_D) if len(p) > 2]
muted = [p for p in subpaths(MUTED_D) if len(p) > 2]

# Wordmark pieces. Drop trace slivers (tiny or hairline-thin bits) and the tile's "sl".
def keep(p, xmin):
    x0, y0, x1, y1 = bbox(p)
    return x0 > xmin and area(p) > 25 and min(x1 - x0, y1 - y0) > 3
word_ink = [p for p in ink if keep(p, 200)]
word_muted = [p for p in muted if keep(p, 720)]
is_x = lambda p: 540 < bbox(p)[0] and bbox(p)[2] < 626
x_arms = [p for p in word_ink if is_x(p)]
letters = [p for p in word_ink if not is_x(p)]
h_parts = [p for p in word_ink if bbox(p)[0] > 636 and bbox(p)[2] < 716]
print("ink", len(word_ink), "x arms", len(x_arms), "h parts", len(h_parts), "muted", len(word_muted))

def scribble(x0, y0, w, h, sw, col, seed, passes=5):
    r = random.Random(seed); pts = []
    for i in range(passes + 1):
        t = i / passes; x = x0 + w * t + r.uniform(-0.04, 0.04) * w
        pts.append((x - w * 0.16 + r.uniform(-0.03, 0.03) * w, y0 + h + r.uniform(-0.04, 0.07) * h))
        pts.append((x + w * 0.16 + r.uniform(-0.03, 0.03) * w, y0 + r.uniform(-0.07, 0.04) * h))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'

def svg(body, vb, title="switxhlabs"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg>\n')

def path(polys, col):
    return f'<path d="{d_of(polys)}" fill="{col}" fill-rule="evenodd"/>'

# ---------- wordmark -----------------------------------------------------------
for mode, pal in PAL.items():
    body = (scribble(548, 494, 70, 86, 10, pal["lime"], 5, passes=4)
            + path([wobble(p) for p in letters], pal["ink"])
            + path([wobble(p) for p in x_arms], X_INK)
            + path([wobble(p) for p in word_muted], pal["muted"]))
    name = "logo.svg" if mode == "light" else "logo-dark.svg"
    open(f"{OUTDIR}/{name}", "w").write(svg(body, "204 452 864 140"))

# Detail: just "xh", large, for the construction board
for mode, pal in PAL.items():
    body = (scribble(548, 494, 70, 86, 10, pal["lime"], 5, passes=4)
            + path([wobble(p) for p in x_arms], X_INK)
            + path([wobble(p) for p in h_parts], pal["ink"]))
    open(f"{OUTDIR}/xh-detail{'-dark' if mode == 'dark' else ''}.svg", "w").write(svg(body, "530 452 196 140", "xh"))

# ---------- marks ---------------------------------------------------------------
def rough_squircle(S, seed, amp=0.02, extra=0, k_in=0.45):
    nz = Noise(seed, 0.5); pts = []; n = 160; e = 4.2
    for k in range(n + extra):
        a = 2 * math.pi * k / n; c, s = math.cos(a), math.sin(a)
        rx = abs(c) ** (2 / e) * (1 if c >= 0 else -1); ry = abs(s) ** (2 / e) * (1 if s >= 0 else -1)
        f = (1 + amp * nz(c, s)) * (1 - 0.008 * k / n)
        pts.append((S / 2 + S * k_in * rx * f, S / 2 + S * k_in * ry * f))
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)

def tile_base(S, outline_col):
    b = f'<path d="{rough_squircle(S, 3)}Z" fill="#c5ec45"/>'
    if outline_col:
        b += (f'<path d="{rough_squircle(S, 8, amp=0.025, extra=5)}" transform="translate({S*0.018:.1f} {S*0.022:.1f}) rotate(-1.2 {S/2} {S/2})" '
              f'fill="none" stroke="{outline_col}" stroke-width="{S*0.02:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return b

def fit(polys, S, frac, cy_shift=0.0):
    """Scale + centre a group of polygons into an S×S tile at `frac` of its width."""
    x0 = min(bbox(p)[0] for p in polys); x1 = max(bbox(p)[2] for p in polys)
    y0 = min(bbox(p)[1] for p in polys); y1 = max(bbox(p)[3] for p in polys)
    s = S * frac / (x1 - x0)
    ox = (S - (x1 - x0) * s) / 2; oy = (S - (y1 - y0) * s) / 2 + S * cy_shift
    return [[((x - x0) * s + ox, (y - y0) * s + oy) for x, y in p] for p in polys]

S = 512
# Mark A: the "xh" pair, carrying the shuffle nod
xh = [wobble(p, 0.45) for p in x_arms + h_parts]
xh_fit = fit(xh, S, 0.56)
n_x = len(x_arms)
for name, oc, outline in (("logo-mark", "#17221f", True), ("logo-mark-dark", "#edf3ee", True), ("logo-mark-small", None, False)):
    frac = 0.56 if outline else 0.66
    g = fit(xh, S, frac)
    body = tile_base(S, oc) + path(g[:n_x], "#17221f") + path(g[n_x:], "#17221f")
    open(f"{OUTDIR}/{name}.svg", "w").write(svg(body, f"0 0 {S} {S}"))

# Mark B: the current "sl" monogram, sketched
sl_s = [p for p in ink if bbox(p)[2] < 110]
sl_l = [p for p in muted if bbox(p)[0] > 100 and bbox(p)[2] < 140 and area(p) > 25]
g = fit([wobble(p, 0.3) for p in sl_s + sl_l], S, 0.52, cy_shift=0.02)
for name, oc in (("logo-mark-sl", "#17221f"), ("logo-mark-sl-dark", "#edf3ee")):
    body = tile_base(S, oc) + path(g[:len(sl_s)], "#17221f") + path(g[len(sl_s):], "#3f4a43")
    open(f"{OUTDIR}/{name}.svg", "w").write(svg(body, f"0 0 {S} {S}"))
# sl small cut: no offset outline, bigger letters
g = fit([wobble(p, 0.3) for p in sl_s + sl_l], S, 0.54, cy_shift=0.02)
body = tile_base(S, None) + path(g[:len(sl_s)], "#17221f") + path(g[len(sl_s):], "#3f4a43")
open(f"{OUTDIR}/logo-mark-sl-small.svg", "w").write(svg(body, f"0 0 {S} {S}"))
print("ok")

# ---------- dark-mode x workshop: four treatments ---------------------------------
LOGO_LIME = {"light": "#5d8500", "dark": "#d4ff4d"}   # the site's --logo-lime tokens

def swipe(x0, y0, x1, y1, col, seed, amp=2.2, slant=6):
    """A filled, rough-edged marker swipe: a slanted box with a torn outline."""
    nz = Noise(seed, 6.0); pts = []
    corners = [(x0 + slant, y0), (x1 + slant, y0), (x1 - slant, y1), (x0 - slant, y1)]
    for k in range(4):
        a, b = corners[k], corners[(k + 1) % 4]
        n = int(math.dist(a, b) / 2)
        for i in range(n):
            t = i / n; x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t
            pts.append((x + amp * nz(x, y), y + amp * nz(y, x)))
    return f'<path d="{d_of([pts])}" fill="{col}"/>'

def underline(x0, x1, y, col, sw, seed):
    r = random.Random(seed)
    pts = [(x0 + (x1 - x0) * t, y + 1.6 * math.sin(t * 5.5 + 1) + r.uniform(-0.4, 0.4)) for t in (k / 16 for k in range(17))]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/>'

def variant(v, mode):
    pal = PAL[mode]
    rest = path([wobble(p) for p in letters], pal["ink"]) + path([wobble(p) for p in word_muted], pal["muted"])
    arms = [wobble(p) for p in x_arms]
    if v == "a":    # solid marker swipe, dark x
        return swipe(538, 488, 628, 586, pal["lime"], 4) + rest + path(arms, X_INK)
    if v == "b":    # dense scribble, wider than the x, dark x
        return scribble(536, 488, 94, 98, 16, pal["lime"], 5, passes=9) + rest + path(arms, X_INK)
    if v == "c":    # lime x, no scribble
        return rest + path(arms, LOGO_LIME[mode])
    if v == "d":    # x matches the letters; lime marker underline
        return underline(541, 627, 591, pal["lime"], 7, 3) + rest + path(arms, pal["ink"])

for v in "abcd":
    for mode in PAL:
        open(f"{OUTDIR}/wm-{v}-{mode}.svg", "w").write(svg(variant(v, mode), "204 452 864 146"))
print("variants ok")

# ---------- lockup: sl monogram out front + option D wordmark ----------------------
# Proportions follow the current logo: a ~134-unit tile from the ascender line to just
# below the baseline, ~36 units before the "s".
def sl_tile(outline_col, small=False):
    frac = 0.54 if small else 0.52
    g = fit([wobble(p, 0.3) for p in sl_s + sl_l], S, frac, cy_shift=0.02)
    return tile_base(S, None if small else outline_col) + path(g[:len(sl_s)], "#17221f") + path(g[len(sl_s):], "#3f4a43")

TILE = 140   # the 512 tile's drawn square fills ~90%, so this lands at ~126 units visible
for mode, oc in (("light", "#17221f"), ("dark", "#edf3ee")):
    for small in (False, True):
        tile = (f'<svg x="{213 - 30 - TILE:.0f}" y="{457:.0f}" width="{TILE}" height="{TILE}" viewBox="0 0 {S} {S}">'
                f'{sl_tile(oc, small)}</svg>')
        name = f"lockup{'-small' if small else ''}{'-dark' if mode == 'dark' else ''}.svg"
        open(f"{OUTDIR}/{name}", "w").write(svg(tile + variant("d", mode), f"{213 - 30 - TILE - 4} 452 {1068 - (213 - 30 - TILE - 4)} 148"))
print("lockups ok")

# ---------- hand-placed letters: per-letter tilt + baseline bounce -----------------
def letter_groups(polys):
    """Cluster polygons whose x-ranges overlap into letters (dot + stem, bowl + counter, h ascender + body)."""
    groups = []
    for p in sorted(polys, key=lambda q: bbox(q)[0]):
        x0, _, x1, _ = bbox(p)
        if groups and x0 <= groups[-1][1]:
            groups[-1][0].append(p); groups[-1][1] = max(groups[-1][1], x1)
        else:
            groups.append([[p], x1])
    return [g[0] for g in groups]

# Hand-placed offsets per letter, left to right: s w i t x h | l a b s  (degrees, units of drop)
JIGGLE = {
    "subtle": [(-1.6, 0.6), (1.2, -0.8), (-1.0, 1.0), (1.8, -0.4), (0.0, 0.0), (-1.2, 0.8), (1.0, -0.6), (-1.6, 0.8), (1.2, -0.6), (-1.0, 0.6)],
    "bouncy": [(-3.0, 1.2), (2.2, -1.6), (-2.0, 2.0), (3.2, -0.8), (0.0, 0.0), (-2.4, 1.6), (2.0, -1.2), (-3.0, 1.6), (2.4, -1.2), (-2.0, 1.2)],
}
JIGGLE["edges"] = [(0.0, 0.0)] * 10   # straight letters, hand-cut edges only
EDGE = {"subtle": 0.95, "bouncy": 1.1, "edges": 1.1}

def place(group, deg, dy):
    x0 = min(bbox(p)[0] for p in group); x1 = max(bbox(p)[2] for p in group)
    cx, cy = (x0 + x1) / 2, 540
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    return [[(cx + (x - cx) * c - (y - cy) * s, cy + (x - cx) * s + (y - cy) * c + dy) for x, y in p] for p in group]

def playful(mode, strength):
    pal = PAL[mode]; amp = EDGE[strength]
    ink_groups = letter_groups(letters)        # s w i t h
    muted_groups = letter_groups(word_muted)   # l a b s
    j = JIGGLE[strength]
    ink_jig = [j[0], j[1], j[2], j[3], j[5]]
    body = underline(541, 627, 591, pal["lime"], 7, 3)
    body += path([wobble(p, amp) for g, (d, dy) in zip(ink_groups, ink_jig) for p in place(g, d, dy)], pal["ink"])
    body += path([wobble(p, amp) for p in x_arms], pal["ink"])
    body += path([wobble(p, amp) for g, (d, dy) in zip(muted_groups, j[6:]) for p in place(g, d, dy)], pal["muted"])
    return body

assert len(letter_groups(letters)) == 5 and len(letter_groups(word_muted)) == 4, (len(letter_groups(letters)), len(letter_groups(word_muted)))
for strength in ("subtle", "bouncy", "edges"):
    for mode, oc in (("light", "#17221f"), ("dark", "#edf3ee")):
        for small in (False, True):
            tile = (f'<svg x="{213 - 30 - TILE:.0f}" y="457" width="{TILE}" height="{TILE}" viewBox="0 0 {S} {S}">{sl_tile(oc, small)}</svg>')
            name = f"lockup-{strength}{'-small' if small else ''}{'-dark' if mode == 'dark' else ''}.svg"
            open(f"{OUTDIR}/{name}", "w").write(svg(tile + playful(mode, strength), f"{213 - 30 - TILE - 4} 450 {1068 - (213 - 30 - TILE - 4)} 152"))
print("playful ok")

# ---------- xh detail in the final style (straight letters, hand-cut edges, underline) ----
for mode, pal in PAL.items():
    body = (underline(541, 627, 591, pal["lime"], 7, 3)
            + path([wobble(p, 1.1) for p in x_arms], pal["ink"])
            + path([wobble(p, 1.1) for p in h_parts], pal["ink"]))
    open(f"{OUTDIR}/xh-edges{'-dark' if mode == 'dark' else ''}.svg", "w").write(svg(body, "530 452 196 148", "xh"))
print("xh-edges ok")
