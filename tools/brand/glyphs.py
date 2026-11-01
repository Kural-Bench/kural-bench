"""Text to SVG outlines: HarfBuzz shaping (uharfbuzz) and glyph drawing (fontTools).

Every glyph that is used is written once into <defs> as a path (font units, y flipped) and placed with <use>, so the
SVG needs no fonts at view time. Tamil is shaped by HarfBuzz as whole runs (vowel-sign reordering, pulli, conjuncts);
glyphs are never placed one letter at a time by this code.
"""
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

FONT_DIR = Path(__file__).resolve().parent / "fonts"

# role + weight -> (Latin face file, Tamil face file)
FACES = {
    ("sans", "regular"): ("IBMPlexSans-Regular.ttf", "NotoSansTamil-Regular.ttf"),
    ("sans", "medium"): ("IBMPlexSans-Medium.ttf", "NotoSansTamil-Medium.ttf"),
    ("sans", "semibold"): ("IBMPlexSans-SemiBold.ttf", "NotoSansTamil-SemiBold.ttf"),
    ("mono", "regular"): ("IBMPlexMono-Regular.ttf", "NotoSansTamil-Regular.ttf"),
}


def num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def is_tamil(ch):
    return 0x0B80 <= ord(ch) <= 0x0BFF


class Face:
    def __init__(self, fname):
        path = FONT_DIR / fname
        self.fname = fname
        self.key = fname.rsplit(".", 1)[0].replace("-", "").replace("IBMPlex", "").replace("NotoSans", "N")
        self.hbfont = hb.Font(hb.Face(hb.Blob(path.read_bytes())))
        self.tt = TTFont(str(path))
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        self.upem = self.tt["head"].unitsPerEm
        self._paths = {}

    def shape(self, s, script, lang):
        buf = hb.Buffer()
        buf.add_str(s)
        buf.direction = "ltr"
        buf.script = script
        buf.language = lang
        hb.shape(self.hbfont, buf, {"kern": True, "liga": True, "ccmp": True})
        return buf.glyph_infos, buf.glyph_positions

    def path(self, gid):
        if gid not in self._paths:
            pen = SVGPathPen(self.gs, ntos=lambda v: str(int(round(v))))
            self.gs[self.order[gid]].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
            self._paths[gid] = pen.getCommands()
        return self._paths[gid]


_faces = {}


def face(fname):
    if fname not in _faces:
        _faces[fname] = Face(fname)
    return _faces[fname]


class Run:
    """A shaped string at one size. glyphs: (face, gid, x_px, y_px, adv_px, cluster)."""

    def __init__(self, text, glyphs, width, size, style):
        self.text, self.glyphs, self.width, self.size, self.style = text, glyphs, width, size, style
        cl = sorted({g[5] for g in glyphs})
        self._ext = {}
        for i, c in enumerate(cl):
            self._ext[c] = (c, cl[i + 1] if i + 1 < len(cl) else len(text))

    def hit(self, g, ranges):
        a, b = self._ext[g[5]]
        return any(a < r1 and r0 < b for r0, r1 in ranges)

    def span(self, ranges):
        """(x0, x1) in px of the glyphs touching any of the char ranges, or None."""
        xs = [(g[2], g[2] + g[4]) for g in self.glyphs if self.hit(g, ranges)]
        if not xs:
            return None
        return min(a for a, _ in xs), max(b for _, b in xs)


def _segments(text):
    """Split into (is_tamil, start, string); neutral characters join the run before them."""
    segs = []
    for i, ch in enumerate(text):
        if is_tamil(ch):
            t = True
        elif ch in " \t.,;:!?()[]'\"-«»–—→/" and segs:
            t = segs[-1][0]
        else:
            t = False
        if segs and segs[-1][0] == t:
            segs[-1][2] += ch
        else:
            segs.append([t, i, ch])
    return segs


_cache = {}


def shape(text, role="sans", weight="regular", size=16):
    key = (text, role, weight, size)
    if key in _cache:
        return _cache[key]
    lat, tam = FACES[(role, weight)]
    glyphs, x = [], 0.0
    for is_ta, start, s in _segments(text):
        f = face(tam if is_ta else lat)
        infos, poss = f.shape(s, "Taml" if is_ta else "Latn", "ta" if is_ta else "en")
        k = size / f.upem
        for inf, pos in zip(infos, poss):
            glyphs.append((f, inf.codepoint, x + pos.x_offset * k, -pos.y_offset * k, pos.x_advance * k,
                           start + inf.cluster))
            x += pos.x_advance * k
    run = Run(text, glyphs, x, size, (role, weight))
    _cache[key] = run
    return run


def wrap(text, role, weight, size, max_w):
    """Greedy word wrap using the shaped width of each candidate line."""
    lines, cur = [], ""
    for w in text.split(" "):
        cand = w if not cur else cur + " " + w
        if cur and shape(cand, role, weight, size).width > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


class Doc:
    def __init__(self, w, h, theme, title, desc, bg=True, border=True, radius=10):
        self.w, self.h, self.t = w, h, theme
        self.title, self.desc = title, desc
        self.body, self.defs = [], {}
        self.bg, self.border, self.radius = bg, border, radius

    def slot(self):
        """Reserve a place in the drawing order (for a frame whose size is known only after its content)."""
        self.body.append(None)
        return len(self.body) - 1

    def rect(self, x, y, w, h, rx=0, fill="none", stroke=None, sw=1, slot=None):
        s = f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}"'
        if rx:
            s += f' rx="{num(rx)}"'
        s += f' fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}"' + (f' stroke-width="{num(sw)}"' if sw != 1 else "")
        if slot is not None:
            self.body[slot] = s + "/>"
        else:
            self.body.append(s + "/>")

    def line(self, x1, y1, x2, y2, stroke, sw=1):
        self.body.append(f'<path d="M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}" stroke="{stroke}" '
                         f'stroke-width="{num(sw)}" fill="none"/>')

    def path(self, d, fill="none", stroke=None, sw=1):
        s = f'<path d="{d}" fill="{fill}"'
        if stroke:
            s += f' stroke="{stroke}" stroke-width="{num(sw)}" stroke-linejoin="round" stroke-linecap="round"'
        self.body.append(s + "/>")

    def text(self, s, x, y, role="sans", weight="regular", size=16, fill=None, anchor="start", hl=None,
             hl_fill=None, run=None):
        """Place text with its baseline at y. hl: char ranges drawn in hl_fill. Returns (run, x0)."""
        fill = fill or self.t["ink"]
        r = run or shape(s, role, weight, size)
        x0 = x - (r.width / 2 if anchor == "middle" else r.width if anchor == "end" else 0)
        groups = {}
        for g in r.glyphs:
            col = hl_fill if hl and r.hit(g, hl) else fill
            groups.setdefault((g[0].fname, col), []).append(g)
        for (fname, col), gl in groups.items():
            f = face(fname)
            k = r.size / f.upem
            uses = []
            for g in gl:
                p = f.path(g[1])
                if not p:
                    continue
                gid = f"{f.key}{g[1]}"
                self.defs.setdefault(gid, p)
                uses.append(f'<use href="#{gid}" x="{round(g[2] / k)}"' + (f' y="{round(g[3] / k)}"' if g[3] else "") + "/>")
            if uses:
                self.body.append(f'<g transform="translate({num(x0)} {num(y)}) scale({k:.5f})" '
                                 f'fill="{col}">' + "".join(uses) + "</g>")
        return r, x0

    def render(self):
        pre = []
        if self.bg:
            pre.append(f'<rect width="{num(self.w)}" height="{num(self.h)}" rx="{self.radius}" fill="{self.t["bg"]}"/>')
            if self.border:
                pre.append(f'<rect x=".5" y=".5" width="{num(self.w - 1)}" height="{num(self.h - 1)}" '
                           f'rx="{self.radius}" fill="none" stroke="{self.t["rule"]}"/>')
        d = "".join(f'<path id="{k}" d="{v}"/>' for k, v in sorted(self.defs.items()))
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{num(self.w)}" height="{num(self.h)}" '
                f'viewBox="0 0 {num(self.w)} {num(self.h)}" role="img" aria-labelledby="t d">'
                f'<title id="t">{self.title}</title><desc id="d">{self.desc}</desc>'
                f'<defs>{d}</defs>' + "".join(pre) + "".join(b for b in self.body if b) + "</svg>\n")
