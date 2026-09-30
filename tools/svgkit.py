"""
svgkit.py - tiny toolkit for hand-built, animated terminal SVGs.

Everything here produces plain SVG + CSS keyframes:
  * no scripts, no external requests (GitHub's image proxy would block them)
  * only transform / opacity animations (render the same in every browser)
  * a subset of JetBrains Mono embedded as WOFF2, so text looks identical
    everywhere and never shifts
  * all animation switches off for visitors with "reduce motion" enabled;
    the base (non-animated) state of every element is its final state
"""
from __future__ import annotations

import base64
import io
import math
import re
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"

# --------------------------------------------------------------------------
# palette - change these to re-skin every asset at once
# --------------------------------------------------------------------------
P = dict(
    bg="#0b0f14",       # terminal background
    panel="#10161d",    # title bars, keycaps
    deep="#070a0e",     # inset areas
    line="#1f2833",     # borders
    grid="#18202a",
    text="#c9d1d9",
    dim="#6e7681",
    mute="#3b4450",
    lime="#c6ff00",     # primary accent (your old profile used #CCFF03)
    cyan="#22d3ee",
    crimson="#ff3860",
    amber="#ffb020",
    violet="#a78bfa",
)

FONT_FILES = {
    400: "JetBrainsMono-Regular.ttf",
    700: "JetBrainsMono-Bold.ttf",
    800: "JetBrainsMono-ExtraBold.ttf",
}
ADV = 0.6          # JetBrains Mono advance width, in em
TB = 34            # window title-bar height

BASE_CSS = (
    # NB: no fill/font-size here - CSS would override per-element attributes
    "text{font-family:'JBM',ui-monospace,SFMono-Regular,Menlo,Consolas,"
    "'Liberation Mono',monospace;white-space:pre}"
    # appear at a given moment (delay set inline) and stay
    ".ap{animation:ap .01s linear both}"
    "@keyframes ap{from{opacity:0}to{opacity:1}}"
    # visible only while the animation runs (duration/delay set inline)
    ".vis{opacity:0;animation:vis 1s linear}"
    "@keyframes vis{from,to{opacity:1}}"
    # typewriter curtain: shrinks towards its right edge in steps
    ".tw{transform-box:fill-box;transform-origin:100%% 50%%;transform:scaleX(0)}"
    "@keyframes tw{from{transform:scaleX(1)}to{transform:scaleX(0)}}"
    ".blink{animation:blink 1.1s steps(1,end) infinite}"
    "@keyframes blink{50%%{opacity:0}}"
    ".pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@keyframes pulse{50%%{opacity:.3}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
) % P


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def n(v: float) -> str:
    """compact number formatting"""
    if isinstance(v, int):
        return str(v)
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


_face_cache: dict[tuple[int, str], str] = {}


def font_face(weight: int, chars: set[str]) -> str:
    text = "".join(sorted(chars | {" "}))
    key = (weight, text)
    if key in _face_cache:
        return _face_cache[key]
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = []          # no ligatures: pure terminal look
    opts.hinting = False
    opts.desubroutinize = True
    opts.notdef_outline = True
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]   # keep copyright + OFL notice
    # recalcTimestamp=False keeps builds reproducible (no git diff when nothing changed)
    font = TTFont(FONTS / FONT_FILES[weight], recalcTimestamp=False)
    missing = {c for c in text if ord(c) not in font.getBestCmap()}
    if missing:
        print(f"    ! weight {weight}: glyphs not in font -> {''.join(sorted(missing))!r}")
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    font.flavor = "woff2"
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    face = ("@font-face{font-family:'JBM';font-weight:%d;"
            "src:url(data:font/woff2;base64,%s) format('woff2')}" % (weight, b64))
    _face_cache[key] = face
    return face


class Doc:
    def __init__(self, w: int, h: int, title: str, desc: str = ""):
        self.w, self.h, self.title, self.desc = w, h, title, desc
        self.css: list[str] = []
        self.defs: list[str] = []
        self.parts: list[str] = []
        self.glyphs: dict[int, set[str]] = {400: set(), 700: set(), 800: set()}
        self._uid = 0

    # -- plumbing ----------------------------------------------------------
    def uid(self, prefix: str = "e") -> str:
        self._uid += 1
        return f"{prefix}{self._uid}"

    def add(self, *s: str) -> "Doc":
        self.parts.extend(x for x in s if x)
        return self

    def style(self, css: str) -> None:
        self.css.append(css)

    def define(self, svg: str) -> None:
        self.defs.append(svg)

    def render(self) -> str:
        faces = "".join(font_face(w, c) for w, c in self.glyphs.items() if c)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="t d" '
            f'font-size="13" fill="{P["text"]}" xml:space="preserve">'
            f'<title id="t">{esc(self.title)}</title><desc id="d">{esc(self.desc)}</desc>'
            f'<style>{faces}{BASE_CSS}{"".join(self.css)}</style>'
            f'<defs>{"".join(self.defs)}</defs>'
            f'{"".join(self.parts)}</svg>'
        )

    def save(self, path: Path) -> int:
        svg = self.render()
        path.write_text(svg, encoding="utf-8")
        return len(svg.encode())

    # -- text --------------------------------------------------------------
    def text(self, x: float, y: float, s: str, *, size: float = 13, weight: int = 400,
             fill: str | None = None, anchor: str | None = None, cls: str | None = None,
             style: str | None = None, opacity: float | None = None, fixed: bool = True,
             spacing: float | None = None) -> str:
        """One <text>. `fixed` pins its width to the monospace grid via textLength,
        so columns stay aligned even if the embedded font were ever unavailable."""
        if not s:
            return ""
        self.glyphs[weight].update(s)
        a = [f'x="{n(x)}"', f'y="{n(y)}"']
        if size != 13:
            a.append(f'font-size="{n(size)}"')
        if weight != 400:
            a.append(f'font-weight="{weight}"')
        if fill:
            a.append(f'fill="{fill}"')
        if anchor:
            a.append(f'text-anchor="{anchor}"')
        if cls:
            a.append(f'class="{cls}"')
        if style:
            a.append(f'style="{style}"')
        if opacity is not None:
            a.append(f'opacity="{n(opacity)}"')
        if spacing is not None:
            a.append(f'letter-spacing="{n(spacing)}"')
        elif fixed and len(s) > 1:
            a.append(f'textLength="{n(len(s) * size * ADV)}"')
        return f'<text {" ".join(a)}>{esc(s)}</text>'

    def mono(self, x: float, y: float, spans, *, size: float = 13, weight: int = 400,
             col: int = 0) -> str:
        """A terminal line built from (text, colour[, weight]) spans laid out on the
        character grid. Runs of 2+ spaces become gaps, so alignment never depends
        on whitespace handling."""
        cw = size * ADV
        out = []
        for sp in spans:
            if isinstance(sp, str):
                sp = (sp, None)
            t, fill = sp[0], sp[1]
            w = sp[2] if len(sp) > 2 else weight
            for tok in re.split(r"( {2,})", t):
                if not tok:
                    continue
                if tok.startswith("  ") and not tok.strip():
                    col += len(tok)
                    continue
                lead = len(tok) - len(tok.lstrip(" "))
                col += lead
                core = tok.strip(" ")
                out.append(self.text(x + col * cw, y, core, size=size, weight=w, fill=fill))
                col += len(core) + (len(tok) - lead - len(core))
        return "".join(out)

    # -- animation helpers -------------------------------------------------
    @staticmethod
    def at(svg: str, t: float, cls: str = "ap", extra: str = "") -> str:
        """wrap content so it appears at time t (seconds)"""
        return f'<g class="{cls}" style="animation-delay:{t:.2f}s{extra}">{svg}</g>'

    @staticmethod
    def during(svg: str, start: float, end: float) -> str:
        """content visible only between start and end"""
        return (f'<g class="vis" style="animation-duration:{end - start:.2f}s;'
                f'animation-delay:{start:.2f}s">{svg}</g>')

    def typed(self, x: float, y: float, s: str, start: float, *, cps: float = 14,
              size: float = 13, weight: int = 400, fill: str | None = None,
              bg: str | None = None, caret: str | None = None) -> tuple[str, float]:
        """Typewriter text: a background-coloured curtain shrinks one character per
        step, a caret rides along. Returns (svg, end_time)."""
        bg = bg or P["bg"]
        caret = caret or P["lime"]
        k = len(s)
        dur = k / cps
        cw = size * ADV
        width = k * cw
        txt = self.text(x, y, s, size=size, weight=weight, fill=fill)
        curtain = (f'<rect x="{n(x - 1)}" y="{n(y - size)}" width="{n(width + 2)}" '
                   f'height="{n(size * 1.5)}" fill="{bg}" class="tw" '
                   f'style="animation:tw {dur:.2f}s steps({k},end) {start:.2f}s both"/>')
        mv = self.uid("mv")
        self.style(f"@keyframes {mv}{{from{{transform:translateX(0)}}"
                   f"to{{transform:translateX({n(width)}px)}}}}")
        car = (f'<rect x="{n(x)}" y="{n(y - size + 1)}" width="{n(cw)}" height="{n(size * 1.25)}" '
               f'fill="{caret}" style="opacity:0;animation:{mv} {dur:.2f}s steps({k},end) '
               f'{start:.2f}s both,vis {dur + .45:.2f}s linear {start - .35:.2f}s 1"/>')
        return txt + curtain + car, start + dur

    def caret(self, x: float, y: float, size: float = 13, fill: str | None = None,
              t: float | None = None) -> str:
        cw = size * ADV
        r = (f'<rect x="{n(x)}" y="{n(y - size + 1)}" width="{n(cw)}" '
             f'height="{n(size * 1.25)}" fill="{fill or P["lime"]}" class="blink"/>')
        return self.at(r, t) if t is not None else r

    # -- chrome ------------------------------------------------------------
    def window(self, title: str, *, x: float = 8, y: float = 6, w: float | None = None,
               h: float | None = None, dots: bool = True) -> str:
        w = w if w is not None else self.w - 16
        h = h if h is not None else self.h - 14
        if "#sh" not in "".join(self.defs):
            self.define('<filter id="sh" x="-4%" y="-6%" width="108%" height="118%">'
                        '<feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#000" '
                        'flood-opacity=".35"/></filter>')
        r = 10
        parts = [
            f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" '
            f'fill="{P["bg"]}" filter="url(#sh)"/>',
            f'<path d="M{n(x)} {n(y + r)}a{r} {r} 0 0 1 {r} -{r}h{n(w - 2 * r)}a{r} {r} 0 0 1 {r} {r}'
            f'v{TB - r}h-{n(w)}z" fill="{P["panel"]}"/>',
            f'<path d="M{n(x)} {n(y + TB)}h{n(w)}" stroke="{P["line"]}"/>',
            f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(w - 1)}" height="{n(h - 1)}" '
            f'rx="{r}" fill="none" stroke="{P["line"]}"/>',
        ]
        if dots:
            for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
                parts.append(f'<circle cx="{n(x + 18 + i * 18)}" cy="{n(y + TB / 2)}" r="5.5" '
                             f'fill="{c}" opacity=".85"/>')
        parts.append(self.text(x + w / 2, y + TB / 2 + 4, title, size=12, fill=P["dim"],
                               anchor="middle"))
        return "".join(parts)

    def chip(self, x: float, y: float, label: str, color: str, *, size: float = 11,
             filled: bool = False, pad: float = 7) -> tuple[str, float]:
        """rounded tag; returns (svg, width)"""
        w = len(label) * size * ADV + pad * 2
        h = size + 9
        if filled:
            box = (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{n(h / 2)}" '
                   f'fill="{color}"/>')
            tfill = P["bg"]
        else:
            box = (f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(w - 1)}" height="{n(h - 1)}" '
                   f'rx="{n(h / 2)}" fill="{color}" fill-opacity=".08" stroke="{color}" '
                   f'stroke-opacity=".55"/>')
            tfill = color
        t = self.text(x + pad, y + h / 2 + size * .36, label, size=size, fill=tfill,
                      weight=700 if filled else 400)
        return box + t, w

    def scanlines(self, x, y, w, h, clip_r: float = 10) -> str:
        """subtle CRT scanlines + a slow refresh band, clipped to the given area"""
        pid, cid = self.uid("scan"), self.uid("clip")
        self.define(f'<pattern id="{pid}" width="4" height="3" patternUnits="userSpaceOnUse">'
                    f'<rect width="4" height="1" fill="#000" opacity=".22"/></pattern>'
                    f'<clipPath id="{cid}"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" '
                    f'height="{n(h)}" rx="{clip_r}"/></clipPath>'
                    f'<linearGradient id="{cid}g" x1="0" y1="0" x2="0" y2="1">'
                    f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                    f'<stop offset=".5" stop-color="#fff" stop-opacity=".045"/>'
                    f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
        self.style(f"@keyframes {cid}r{{from{{transform:translateY(0)}}"
                   f"to{{transform:translateY({n(h + 90)}px)}}}}")
        return (f'<g clip-path="url(#{cid})" pointer-events="none">'
                f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{pid})"/>'
                f'<rect x="{n(x)}" y="{n(y - 90)}" width="{n(w)}" height="90" fill="url(#{cid}g)" '
                f'style="animation:{cid}r 7s linear infinite"/></g>')


def ansi_shadow(text: str, cw: float, ch: float, ox: float, oy: float):
    """Render figlet 'ANSI Shadow' art as crisp vector paths instead of glyphs:
    returns (blocks_path_d, shadow_path_d, cols, rows)."""
    import pyfiglet
    art = pyfiglet.figlet_format(text, font="ansi_shadow", width=400)
    rows = [r for r in art.rstrip("\n").split("\n") if r.strip()]
    g = ch * .13
    blocks, lines = [], []
    for r, row in enumerate(rows):
        y0 = oy + r * ch
        y1, cy = y0 + ch, y0 + ch / 2
        c = 0
        while c < len(row):
            ch_ = row[c]
            if ch_ == "█":
                c2 = c
                while c2 < len(row) and row[c2] == "█":
                    c2 += 1
                blocks.append(f"M{n(ox + c * cw)} {n(y0)}h{n((c2 - c) * cw)}v{n(ch)}"
                              f"h-{n((c2 - c) * cw)}z")
                c = c2
                continue
            x0 = ox + c * cw
            x1, cx = x0 + cw, x0 + cw / 2
            L = lines.append
            if ch_ == "═":
                L(f"M{n(x0)} {n(cy - g)}H{n(x1)}M{n(x0)} {n(cy + g)}H{n(x1)}")
            elif ch_ == "║":
                L(f"M{n(cx - g)} {n(y0)}V{n(y1)}M{n(cx + g)} {n(y0)}V{n(y1)}")
            elif ch_ == "╗":
                L(f"M{n(x0)} {n(cy - g)}H{n(cx + g)}V{n(y1)}M{n(x0)} {n(cy + g)}H{n(cx - g)}V{n(y1)}")
            elif ch_ == "╔":
                L(f"M{n(x1)} {n(cy - g)}H{n(cx - g)}V{n(y1)}M{n(x1)} {n(cy + g)}H{n(cx + g)}V{n(y1)}")
            elif ch_ == "╝":
                L(f"M{n(x0)} {n(cy + g)}H{n(cx + g)}V{n(y0)}M{n(x0)} {n(cy - g)}H{n(cx - g)}V{n(y0)}")
            elif ch_ == "╚":
                L(f"M{n(x1)} {n(cy + g)}H{n(cx - g)}V{n(y0)}M{n(x1)} {n(cy - g)}H{n(cx + g)}V{n(y0)}")
            c += 1
    cols = max(len(r) for r in rows)
    return "".join(blocks), "".join(lines), cols, len(rows)


def session_clock(d: Doc, x: float, y: float, size: float = 11, fill: str | None = None) -> str:
    """HH:MM:SS that genuinely ticks: every digit is a vertical strip of numbers,
    clipped to one cell and stepped with CSS - a pure-CSS odometer."""
    cw = size * ADV
    lh = size * 1.4
    fill = fill or P["text"]
    d.style(f"@keyframes t10{{to{{transform:translateY(-{n(lh * 10)}px)}}}}"
            f"@keyframes t6{{to{{transform:translateY(-{n(lh * 6)}px)}}}}")
    # (digits, period seconds) per position, left to right; None = separator
    spec = [("0", None), ("0123456789", 36000), (":", None),
            ("012345", 3600), ("0123456789", 600), (":", None),
            ("012345", 60), ("0123456789", 10)]
    out = []
    for i, (digits, period) in enumerate(spec):
        cx = x + i * cw
        if period is None:
            out.append(d.text(cx, y, digits, size=size, fill=fill))
            continue
        cid = d.uid("dg")
        d.define(f'<clipPath id="{cid}"><rect x="{n(cx - 1)}" y="{n(y - size)}" '
                 f'width="{n(cw + 2)}" height="{n(size * 1.3)}"/></clipPath>')
        k = len(digits)
        strip = "".join(d.text(cx, y + j * lh, dg, size=size, fill=fill)
                        for j, dg in enumerate(digits))
        out.append(f'<g clip-path="url(#{cid})"><g style="animation:t{k} {period}s '
                   f'steps({k},end) infinite">{strip}</g></g>')
    return "".join(out)
