"""Sketchy switxhlabs logo: hand-wobbled DM Mono wordmark, a pencil-drawn toggle x on a lime marker scribble."""
import math, random, sys
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

FONT, OUTDIR = sys.argv[1], sys.argv[2]
font = TTFont(FONT)
gs, cmap = font.getGlyphSet(), font.getBestCmap()
UPM = font["head"].unitsPerEm
XH = font["OS/2"].sxHeight

PAL = {
    "light": dict(ink="#17221f", muted="#58635b", lime="#c5ec45", xink="#17221f"),
    "dark":  dict(ink="#edf3ee", muted="#aeb9b1", lime="#c5ec45", xink="#17221f"),
}

# ---------- smooth noise -------------------------------------------------------
class Noise:
    def __init__(self, seed, scale):
        r = random.Random(seed)
        self.waves = [(r.uniform(0, 2 * math.pi), f, r.uniform(0, 2 * math.pi), a)
                      for f, a in ((0.6, 1.0), (1.3, 0.55), (2.9, 0.25), (6.5, 0.12))]
        self.scale = scale
    def __call__(self, x, y):
        s = 0
        for th, f, ph, a in self.waves:
            s += a * math.sin(f * (x * math.cos(th) + y * math.sin(th)) / self.scale + ph)
        return s / 1.92

# ---------- glyph flattening + wobble -----------------------------------------
class FlatPen(BasePen):
    def __init__(self, gs, step):
        super().__init__(gs); self.contours, self.step = [], step
    def _moveTo(self, p): self.contours.append([p])
    def _lineTo(self, p):
        a = self.contours[-1][-1]; n = max(1, int(math.dist(a, p) / self.step))
        self.contours[-1] += [(a[0] + (p[0] - a[0]) * t / n, a[1] + (p[1] - a[1]) * t / n) for t in range(1, n + 1)]
    def _curveToOne(self, p1, p2, p3):
        p0 = self.contours[-1][-1]
        n = max(4, int((math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)) / self.step))
        for i in range(1, n + 1):
            t = i / n; u = 1 - t
            self.contours[-1].append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                                      u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
    def _closePath(self): pass
    def _endPath(self): pass

def poly_d(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"

def wobbly_glyph(ch, ox, base, nx, ny, amp):
    pen = FlatPen(gs, UPM * 0.012); gs[cmap[ord(ch)]].draw(pen)
    d = []
    for c in pen.contours:
        pts = []
        for x, y in c:
            X, Y = ox + x, base - y
            pts.append((X + amp * nx(X, Y), Y + amp * ny(X, Y)))
        d.append(poly_d(pts))
    return "".join(d)

# ---------- pencil strokes ------------------------------------------------------
def pencil(p, q, w, seed, bow=0.0, taper=0.35, wob=0.0):
    """Filled polygon for a hand-drawn stroke from p to q: slight bow, pressure taper, wobble, round-ish ends."""
    r = random.Random(seed)
    L = math.dist(p, q); ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L; nx_, ny_ = -uy, ux
    nz = Noise(seed, L * 0.25)
    N = 40; left, right = [], []
    for i in range(N + 1):
        t = i / N
        off = bow * L * math.sin(math.pi * t) + wob * w * nz(t * L, 0)
        cx, cy = p[0] + ux * L * t + nx_ * off, p[1] + uy * L * t + ny_ * off
        press = 1 - taper * (abs(2 * t - 1) ** 2.2)
        hw = w / 2 * press * (1 + 0.07 * nz(0, t * L * 3))
        left.append((cx + nx_ * hw, cy + ny_ * hw)); right.append((cx - nx_ * hw, cy - ny_ * hw))
    def cap(c, a, b, sgn):  # semicircle cap from a to b around centre c
        ang0 = math.atan2(a[1] - c[1], a[0] - c[0]); rad = math.dist(a, c)
        return [(c[0] + rad * math.cos(ang0 + sgn * math.pi * k / 24), c[1] + rad * math.sin(ang0 + sgn * math.pi * k / 24)) for k in range(1, 24)]
    end_c = ((left[-1][0] + right[-1][0]) / 2, (left[-1][1] + right[-1][1]) / 2)
    start_c = ((left[0][0] + right[0][0]) / 2, (left[0][1] + right[0][1]) / 2)
    pts = left + cap(end_c, left[-1], right[-1], -1) + right[::-1] + cap(start_c, right[0], left[0], -1)
    return poly_d(pts)

def wobbly_circle(c, rad, seed, amp=0.06, n=48):
    nz = Noise(seed, 0.6)
    return poly_d([(c[0] + rad * (1 + amp * nz(math.cos(a), math.sin(a))) * math.cos(a),
                    c[1] + rad * (1 + amp * nz(math.cos(a), math.sin(a))) * math.sin(a))
                   for a in (2 * math.pi * k / n for k in range(n))])

def scribble(x0, y0, w, h, sw, seed, passes=5):
    """Lime marker zig-zag filling a box, like a quick highlighter scribble."""
    r = random.Random(seed); pts = []
    for i in range(passes + 1):
        t = i / passes
        x = x0 + w * t + r.uniform(-0.04, 0.04) * w
        pts.append((x - w * 0.18 + r.uniform(-0.03, 0.03) * w, y0 + h + r.uniform(-0.05, 0.08) * h))
        pts.append((x + w * 0.18 + r.uniform(-0.03, 0.03) * w, y0 + r.uniform(-0.08, 0.05) * h))
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="LIME" stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>'

def guide(p, q, w, seed, over=0.14, shift=0.0):
    """Thin overshooting pencil guide line, offset a little from the stroke it belongs to."""
    L = math.dist(p, q); ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L; nx_, ny_ = -uy, ux
    a = (p[0] - ux * L * over + nx_ * shift, p[1] - uy * L * over + ny_ * shift)
    b = (q[0] + ux * L * over * 0.6 + nx_ * shift * 1.4, q[1] + uy * L * over * 0.6 + ny_ * shift * 1.4)
    return pencil(a, b, w, seed, bow=0.01, taper=0.7)

def toggle_x(x0, top, w, h, sw, col, seed, guides=True):
    """The x as two pencil strokes; the rising one is a toggle lever with a ball knob, mid-flip."""
    out = []
    pad = sw * 0.5
    p1, q1 = (x0 + pad, top + pad), (x0 + w - pad, top + h - pad)
    a, b = (x0 + pad, top + h - pad), (x0 + w * 0.8, top + h * 0.2)
    out.append(pencil(p1, q1, sw, seed, bow=0.015, taper=0.12, wob=0.06))
    out.append(pencil(a, b, sw, seed + 1, bow=-0.02, taper=0.12, wob=0.06))
    kc = (b[0] + sw * 0.15, b[1] - sw * 0.15)
    out.append(wobbly_circle(kc, sw * 0.78, seed + 2, amp=0.05))
    if guides:
        out.append(guide(p1, q1, sw * 0.13, seed + 3, shift=-sw * 0.85))
        out.append(guide(a, b, sw * 0.13, seed + 4, shift=sw * 0.9))
    return "".join(f'<path d="{d}" fill="{col}"/>' for d in out), kc

def pencil_path(pts, w, seed, taper=0.12, wob=0.05):
    """Hand-drawn stroke along a centreline polyline: pressure taper, slight wobble, round ends."""
    nz = Noise(seed, w * 2.5)
    n = len(pts); left, right = [], []
    for i, (cx, cy) in enumerate(pts):
        a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        L = math.dist(a, b) or 1; tx, ty = (b[0] - a[0]) / L, (b[1] - a[1]) / L; nx_, ny_ = -ty, tx
        t = i / (n - 1)
        off = wob * w * nz(cx, cy)
        hw = w / 2 * (1 - taper * abs(2 * t - 1) ** 2.2) * (1 + 0.06 * nz(cy * 2, cx * 2))
        cx, cy = cx + nx_ * off, cy + ny_ * off
        left.append((cx + nx_ * hw, cy + ny_ * hw)); right.append((cx - nx_ * hw, cy - ny_ * hw))
    def cap(a, b):
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2); r = math.dist(a, c); g = math.atan2(a[1] - c[1], a[0] - c[0])
        return [(c[0] + r * math.cos(g - math.pi * k / 24), c[1] + r * math.sin(g - math.pi * k / 24)) for k in range(1, 24)]
    return poly_d(left + cap(left[-1], right[-1]) + right[::-1] + cap(right[0], left[0]))

def bez(p0, p1, p2, p3, n=48):
    return [tuple((1-t)**3*p0[i] + 3*(1-t)**2*t*p1[i] + 3*(1-t)*t*t*p2[i] + t**3*p3[i] for i in (0, 1))
            for t in (k / n for k in range(n + 1))]

_mask = [0]
def shuffle_x(x0, top, w, h, sw, col, seed, gap=0.38):
    """The x as a sketched shuffle icon: two S-paths swap lanes and leave right through arrowheads.
    The rising path passes over; the falling one is cut where it goes under."""
    _mask[0] += 1; mid = f"under{_mask[0]}"
    ah = h * 0.25                      # arrowhead arm length
    T, B = top + ah * 0.62, top + h - ah * 0.62
    xl, xr = x0 + sw * 0.5, x0 + w - sw * 0.75
    tipx = x0 + w - sw * 0.4
    bend = w * 0.36
    rise = bez((xl, B), (xl + bend, B + h * 0.02), (xr - bend, T - h * 0.02), (xr, T))
    fall = bez((xl, T), (xl + bend, T - h * 0.02), (xr - bend, B + h * 0.02), (xr, B))
    def arrow(tip, k):
        return "".join(f'<path d="{pencil((tipx, tip[1]), (tipx - ah * math.cos(a), tip[1] - ah * math.sin(a)), sw * 0.78, seed + k + j, taper=0.15, wob=0.03)}" fill="{col}"/>'
                       for j, a in enumerate((math.radians(-46), math.radians(46))))
    cut = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in rise)
    pad = sw * 2
    mask = (f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="{x0-pad:.1f}" y="{top-pad:.1f}" width="{w+2*pad:.1f}" height="{h+2*pad:.1f}">'
            f'<rect x="{x0-pad:.1f}" y="{top-pad:.1f}" width="{w+2*pad:.1f}" height="{h+2*pad:.1f}" fill="#fff"/>'
            f'<path d="{cut}" fill="none" stroke="#000" stroke-width="{sw * (1 + 2 * gap):.1f}"/></mask>')
    return (mask
            + f'<g mask="url(#{mid})"><path d="{pencil_path(fall, sw, seed + 1)}" fill="{col}"/>{arrow(fall[-1], 20)}</g>'
            + f'<path d="{pencil_path(rise, sw, seed + 2)}" fill="{col}"/>' + arrow(rise[-1], 30))

def motion_ticks(c, r0, sw, col, seed, angles=(-80, -45, -10)):
    out = []
    for k, a in enumerate(angles):
        a = math.radians(a)
        p = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a))
        q = (c[0] + r0 * 1.55 * math.cos(a), c[1] + r0 * 1.55 * math.sin(a))
        out.append(f'<path d="{pencil(p, q, sw, seed + k, taper=0.5)}" fill="{col}"/>')
    return "".join(out)

# ---------- wordmark ------------------------------------------------------------
def wordmark(pal):
    adv = gs[cmap[ord("s")]].width
    asc = max(gs[cmap[ord(c)]].width and 0 for c in "a") or font["OS/2"].sCapHeight
    base = UPM * 0.78
    nx, ny = Noise(11, UPM * 0.08), Noise(23, UPM * 0.08)
    amp = UPM * 0.013
    parts, x = [], 0.0
    track = -UPM * 0.02
    knob_c = None
    for i, ch in enumerate("switxhlabs"):
        col = pal["ink"] if i < 6 else pal["muted"]
        if ch == "x":
            sw = UPM * 0.095
            hl = scribble(x + UPM * 0.06, base - XH - UPM * 0.02, adv - UPM * 0.12, XH + UPM * 0.05, UPM * 0.09, 5, passes=5)
            parts.append(hl.replace("LIME", pal["lime"]))
            parts.append(shuffle_x(x + UPM * 0.015, base - XH - UPM * 0.035, adv - UPM * 0.02, XH + UPM * 0.05, UPM * 0.082, pal["xink"], 7))
        else:
            d = wobbly_glyph(ch, x, base, nx, ny, amp)
            parts.append(f'<path d="{d}" fill="{col}" stroke="{col}" stroke-width="{UPM*0.018:.1f}" stroke-linejoin="round" fill-rule="nonzero"/>')
        x += adv + track
    return "".join(parts), x - track, UPM * 0.98

def svg(body, vb, title="switxhlabs"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{body}</svg>\n')

def rough_squircle(S, seed, amp=0.012, extra=0):
    """Superellipse tile with a hand-cut wobble."""
    nz = Noise(seed, 0.5); pts = []; n = 160; e = 4.2
    for k in range(n + extra):
        a = 2 * math.pi * k / n; c, s = math.cos(a), math.sin(a)
        rx = abs(c) ** (2 / e) * (1 if c >= 0 else -1); ry = abs(s) ** (2 / e) * (1 if s >= 0 else -1)
        f = (1 + amp * nz(c, s)) * (1 - 0.008 * k / n)
        pts.append((S / 2 + S * 0.45 * rx * f, S / 2 + S * 0.45 * ry * f))
    return poly_d(pts)

def tile(outline_col, S=512, outline=True, sw=0.088, box=(0.25, 0.28, 0.5, 0.44)):
    body = f'<path d="{rough_squircle(S, 3, amp=0.02)}" fill="{PAL["light"]["lime"]}"/>'
    if outline:
        o = rough_squircle(S, 8, amp=0.025, extra=5).replace("Z", "")
        body += (f'<path d="{o}" transform="translate({S*0.018:.1f} {S*0.022:.1f}) rotate(-1.2 {S/2} {S/2})" '
                 f'fill="none" stroke="{outline_col}" stroke-width="{S*0.02:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    bx, by, bw, bh = box
    body += shuffle_x(S * bx, S * by, S * bw, S * bh, S * sw, "#17221f", 9)
    return body

for mode, pal in PAL.items():
    body, w, h = wordmark(pal)
    pad = UPM * 0.06
    name = "logo.svg" if mode == "light" else "logo-dark.svg"
    open(f"{OUTDIR}/{name}", "w").write(svg(body, f"{-pad:.0f} {UPM*0.05:.0f} {w + 2*pad:.0f} {h - UPM*0.05:.0f}"))
open(f"{OUTDIR}/logo-mark.svg", "w").write(svg(tile("#17221f"), "0 0 512 512"))
open(f"{OUTDIR}/logo-mark-dark.svg", "w").write(svg(tile("#edf3ee"), "0 0 512 512"))
# small sizes (favicon): no offset outline, heavier strokes, bigger glyph
open(f"{OUTDIR}/logo-mark-small.svg", "w").write(svg(tile(None, outline=False, sw=0.115, box=(0.17, 0.22, 0.66, 0.56)), "0 0 512 512"))
print("ok")
