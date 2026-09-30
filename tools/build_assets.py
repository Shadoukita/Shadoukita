#!/usr/bin/env python3
"""
build_assets.py - generates every animated SVG used in github.com/Shadoukita

    pip install fonttools brotli pyfiglet
    python tools/build_assets.py          # (re)writes assets/*.svg

Edit the text in the builders below (or the palette in svgkit.py), re-run,
and commit the assets/ folder.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svgkit import ADV, P, TB, Doc, ansi_shadow, n, session_clock  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets"


def prompt(d: Doc, x: float, y: float, path: str = "~", host: str = "github",
           size: float = 13) -> tuple[str, float]:
    """`shadou@host:path$ ` - returns (svg, x where the command starts)"""
    spans = [("shadou@" + host, P["lime"], 700), (":", P["dim"]), (path, P["cyan"], 700),
             ("$ ", P["dim"])]
    cols = len("shadou@" + host) + 1 + len(path) + 2
    return d.mono(x, y, spans, size=size), x + cols * size * ADV


# ==========================================================================
# header - boot log -> clear -> shadoufetch
# ==========================================================================
def build_header() -> Doc:
    W, H = 900, 470
    d = Doc(W, H, "SHADOUKITA // personal terminal",
            "A terminal boots, clears, then runs shadoufetch: the SHADOUKITA logo "
            "plus a few facts - developer and gamer from Germany, coding since 2019, "
            "building Listly., peaked Master in League.")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("shadou@github: ~", x=wx, y=wy, w=ww, h=wh))

    # title bar, right side: online + ticking session clock
    tb_y = wy + TB / 2 + 4
    d.add(f'<circle cx="{wx + ww - 196}" cy="{n(tb_y - 3.5)}" r="3.5" fill="{P["lime"]}" class="pulse"/>')
    d.add(d.text(wx + ww - 187, tb_y, "ONLINE", size=11, fill=P["lime"], weight=700))
    d.add(d.text(wx + ww - 128, tb_y, "SESSION", size=11, fill=P["dim"]))
    d.add(session_clock(d, wx + ww - 76, tb_y, size=11, fill=P["text"]))
    d.add(d.text(wx + 78, tb_y, "◆ PERSONAL TERMINAL v1.0", size=11, fill=P["dim"]))

    X = 32
    LH = 20

    # ---- phase 1: boot log (0 - 2.95s) ----------------------------------
    boot = [
        ("OK", "Started shadou.session — hi, welcome in"),
        ("OK", "Mounted /home/shadou/projects"),
        ("OK", "Started listly.service — self-hosted household app"),
        ("OK", "Loaded shadoucmdb — Rust · Axum · sqlx · PostgreSQL"),
        ("OK", "Loaded feralheart — C++ · OGRE 14 engine port"),
        ("OK", "Reached target homelab.target (i5-14600K · 48 GB · 66 TB+)"),
        ("IDLE", "game-server.service — standby, powers on when needed"),
        ("OK", "Connected discord-relay (@shadoukita) — all systems nominal"),
    ]
    rows = []
    for i, (st, msg) in enumerate(boot):
        y = 66 + i * LH
        col = P["lime"] if st == "OK" else P["amber"]
        line = d.mono(X, y, [("[", P["dim"]), (f"{st:^6}", col, 700), ("]", P["dim"]),
                             ("  " + msg, P["text"])])
        rows.append(d.at(line, .25 + i * .27))
    d.add(d.during("".join(rows), 0, 3.0))

    # ---- phase 2: prompt + typed command ---------------------------------
    y = 66
    p, cx = prompt(d, X, y)
    typed, t_end = d.typed(cx, y, "shadoufetch", 3.35, cps=13)
    d.add(d.at(p + typed, 3.05))

    # ---- logo --------------------------------------------------------------
    cw, chh = 10, 20
    blocks, shadow, cols, nrows = ansi_shadow("SHADOUKITA", cw, chh, 0, 0)
    lw, lh = cols * cw, nrows * chh
    lx, ly = (W - lw) / 2, 86
    d.define(f'<path id="lgb" d="{blocks}"/><path id="lgs" d="{shadow}"/>'
             f'<linearGradient id="lgg" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0" stop-color="{P["lime"]}"/>'
             f'<stop offset=".55" stop-color="#7dffb2"/>'
             f'<stop offset="1" stop-color="{P["cyan"]}"/></linearGradient>'
             f'<clipPath id="lgc"><use href="#lgb"/></clipPath>'
             f'<clipPath id="lgsl"><rect x="0" y="8" width="{lw}" height="14"/>'
             f'<rect x="0" y="52" width="{lw}" height="9"/>'
             f'<rect x="0" y="84" width="{lw}" height="18"/></clipPath>')
    d.style(
        "@keyframes crt{0%{opacity:0;transform:scaleY(.02)}6%{opacity:1;transform:scaleY(.02)}"
        "12%{transform:scaleY(1)}16%{opacity:.25}22%{opacity:1}27%{opacity:.5}34%,100%{opacity:1}}"
        ".crt{transform-box:fill-box;transform-origin:50% 50%;animation:crt .9s linear 4.05s both}"
        "@keyframes shine{0%,72%{transform:translateX(0)}100%{transform:translateX(1000px)}}"
        ".shine{animation:shine 6.5s ease-in 5.2s infinite}"
        "@keyframes gl{0%,90.5%,100%{opacity:0;transform:translate(0,0)}"
        "91%{opacity:.85;transform:translate(-4px,0)}92.2%{opacity:.85;transform:translate(3px,1px)}"
        "93%{opacity:0}}"
        ".g1{animation:gl 8.3s linear 6s infinite}.g2{animation:gl 8.3s linear 6.04s infinite;"
        "animation-direction:reverse}.g1,.g2{opacity:0}"
    )
    logo = (
        f'<g transform="translate({n(lx)} {n(ly)})"><g class="crt">'
        f'<use href="#lgs" fill="none" stroke="{P["cyan"]}" stroke-opacity=".5" stroke-width="1.3"/>'
        f'<use href="#lgb" fill="url(#lgg)"/>'
        f'<g clip-path="url(#lgc)"><path class="shine" d="M-150 -10h46l-40 {lh + 20}h-46z" '
        f'fill="#fff" opacity=".55"/></g>'
        f'<g clip-path="url(#lgsl)"><use href="#lgb" fill="{P["crimson"]}" class="g1"/>'
        f'<use href="#lgb" fill="{P["cyan"]}" class="g2"/></g>'
        f'</g></g>'
    )
    d.add(logo)

    # ---- tagline + facts --------------------------------------------------
    ty = ly + lh + 30
    tag = "developer  ·  gamer  ·  homelab tinkerer  ·  Germany"
    d.add(d.at(d.text(W / 2, ty, tag, fill=P["dim"], anchor="middle"), 4.6))

    left = [
        ("operator", "Shadou · aka Shadoukita"),
        ("trade", "IT Systems Electronics Technician"),
        ("location", "Germany · NRW"),
        ("uptime", "coding since 2019 · self-taught"),
        ("stack", "Python · Vue 3 · Rust · C++"),
        ("tools", "VS Code · Git · Docker · Linux"),
    ]
    right = [
        ("building", "Listly. — self-hosted household app"),
        ("also", "ShadouCMDB · FeralHeart engine port"),
        ("guild", "Discord bot for my DMW guild"),
        ("main", "Katarina · mid · peaked Master · EUW"),
        ("learning", "Godot — game dev on the side"),
        ("homelab", "2 self-built servers · 66 TB+"),
    ]
    fy = ty + 30
    t = 4.8
    for i in range(6):
        y = fy + i * 21
        for colx, (k, v) in ((lx, left[i]), (470, right[i])):
            line = d.mono(colx, y, [(f"{k:<10}", P["lime"], 700), (v, P["text"])])
            d.add(d.at(line, t))
            t += .065

    # neofetch-style colour strip
    py = fy + 6 * 21 + 8
    strip = "".join(
        f'<rect x="{n(lx + i * 34)}" y="{n(py)}" width="30" height="12" rx="2" fill="{c}"/>'
        for i, c in enumerate((P["mute"], P["crimson"], P["lime"], P["amber"], P["cyan"],
                               P["violet"], P["dim"], P["text"])))
    d.add(d.at(strip, t + .1))

    # final prompt with blinking caret
    fy2 = py + 44
    p2, cx2 = prompt(d, X, fy2)
    d.add(d.at(p2 + d.caret(cx2, fy2), t + .3))

    d.add(d.scanlines(wx + 1, wy + TB, ww - 2, wh - TB - 1))
    return d


# ==========================================================================
# currently - htop
# ==========================================================================
def build_currently() -> Doc:
    W, H = 900, 312
    d = Doc(W, H, "htop - what Shadou is up to",
            "An htop screen: Listly. at the top of the process list, then a Discord "
            "bot for a DMW guild, League of Legends (Katarina mid) and Godot.")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("htop — shadou@github", x=wx, y=wy, w=ww, h=wh))
    X, cw = 32, 13 * ADV

    meters = [  # label, (lo, hi) fill range, colour split, period
        ("listly.", (.72, .93), (.70, .20), 3.2),
        ("dmw-bot", (.30, .48), (.55, .30), 2.6),
        ("league", (.44, .66), (.40, .45), 3.8),
        ("godot", (.12, .26), (.60, .25), 4.4),
    ]
    BAR = 34
    for i, (label, (lo, hi), (a, b), per) in enumerate(meters):
        y = 68 + i * 20
        na, nb = round(BAR * a), round(BAR * b)
        nc = BAR - na - nb
        spans = [(f"{i + 1:>2}", P["cyan"]), (" [", P["text"], 700),
                 ("|" * na, P["lime"]), ("|" * nb, P["crimson"]), ("|" * nc, P["cyan"]),
                 (f"{label:>8}", P["dim"]), ("]", P["text"], 700)]
        d.add(d.mono(X, y, spans))
        # curtain hides the right part of the bar and breathes between lo..hi
        x0 = X + 4 * cw
        kf = d.uid("m")
        d.style(f"@keyframes {kf}{{from{{transform:scaleX({1 - lo:.3f})}}"
                f"to{{transform:scaleX({1 - hi:.3f})}}}}")
        d.add(f'<rect x="{n(x0)}" y="{y - 13}" width="{n(BAR * cw)}" height="18" fill="{P["bg"]}" '
              f'style="transform-box:fill-box;transform-origin:100% 50%;'
              f'transform:scaleX({1 - (lo + hi) / 2:.3f});'
              f'animation:{kf} {per}s ease-in-out {-i * .7:.1f}s infinite alternate"/>')
    side = [
        [("Tasks: ", P["cyan"]), ("4", P["text"], 700), (", ", P["cyan"]),
         ("3", P["lime"], 700), (" running", P["cyan"])],
        [("Uptime: ", P["cyan"]), ("since 2019", P["text"], 700)],
        [("Focus: ", P["cyan"]), ("Listly.", P["lime"], 700),
         (" — self-hosted household app", P["dim"])],
        [("Queue: ", P["cyan"]), ("Godot side quest", P["text"])],
    ]
    for i, sp in enumerate(side):
        d.add(d.mono(X + 52 * cw, 68 + i * 20, sp))

    # table header (inverted bar)
    hy = 160
    d.add(f'<rect x="{wx + 1}" y="{hy - 14}" width="{ww - 2}" height="20" fill="{P["lime"]}"/>')
    d.add(d.mono(X, hy, [("  PID USER      PRI  NI  S  FOCUS%  COMMAND", P["bg"], 700)]))
    procs = [
        ("2026", "20", " 0", "R", "62.0", "listly.", " --stack vue3,flask,sqlite --in docker"),
        ("1337", "20", " 0", "R", "18.5", "dmw-guild-bot", ' --for "my DMW guild (DMO private server)"'),
        ("1024", "20", " 0", "R", "13.0", "league", " --main katarina --role mid --peak master --euw"),
        ("2025", "25", " 5", "S", " 6.5", "godot", ' --side-quest "dipping my toes into game dev"'),
    ]
    for i, (pid, pri, ni, st, cpu, prog, args) in enumerate(procs):
        y = hy + 26 + i * 20
        stc = P["lime"] if st == "R" else P["dim"]
        d.add(d.mono(X, y, [
            (f"{pid:>5}", P["text"]), (" shadou   ", P["text"]), (f"{pri:>4}", P["text"]),
            (f"{ni:>4}", P["dim"] if ni.strip() == "0" else P["amber"]), ("  " + st, stc, 700),
            (f"{cpu:>8}", P["text"]), ("  " + prog, P["lime"], 700), (args, P["text"])]))
    # moving selection bar, like someone scrolling with the arrow keys
    d.style("@keyframes sel{0%,22%{transform:translateY(0)}25%,47%{transform:translateY(20px)}"
            "50%,72%{transform:translateY(40px)}75%,97%{transform:translateY(60px)}"
            "100%{transform:translateY(0)}}")
    d.add(f'<rect x="{wx + 1}" y="{hy + 12}" width="{ww - 2}" height="20" fill="{P["cyan"]}" '
          f'opacity=".14" style="animation:sel 12s ease-in-out 1.5s infinite"/>')

    # F-key bar
    fy = H - 28
    x = X
    for key, act in (("F1", "Help"), ("F2", "Setup"), ("F3", "Search"), ("F4", "Filter"),
                     ("F5", "Tree"), ("F6", "SortBy"), ("F7", "Nice -"), ("F8", "Nice +"),
                     ("F9", "Kill"), ("F10", "Quit")):
        d.add(d.text(x, fy, key, fill=P["text"], weight=700))
        x += len(key) * cw
        d.add(f'<rect x="{n(x)}" y="{fy - 13}" width="{n(6 * cw)}" height="18" fill="{P["cyan"]}"/>')
        d.add(d.text(x, fy, f"{act:<6}".rstrip(), fill=P["bg"]))
        x += 6 * cw + 4
    return d


# ==========================================================================
# project cards
# ==========================================================================
def card(name: str, title: tuple, kicker: str, tagline: list[str], chips: list[str],
         lang: tuple[str, str], snippet, desc: str) -> Doc:
    W, H = 900, 262
    d = Doc(W, H, f"{name} - project card", desc)
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window(f"shadou@github: ~/projects/{name.lower()}", x=wx, y=wy, w=ww, h=wh))
    d.add(d.text(wx + ww - 16, wy + TB / 2 + 4, f"github.com/Shadoukita/{name} ↗", size=11,
                 fill=P["dim"], anchor="end"))
    X = 32
    d.add(d.text(X, 66, kicker, size=11, weight=700, fill=P["lime"], spacing=1.2))
    # big title: (text, colour) parts
    x = X
    for part, col in title:
        d.add(d.text(x, 104, part, size=34, weight=800, fill=col))
        x += len(part) * 34 * ADV
    for i, line in enumerate(tagline):
        d.add(d.text(X, 134 + i * 19, line, fill=P["text"], opacity=.86))
    cx = X
    cy = 134 + len(tagline) * 19 + 6
    for i, c in enumerate(chips):
        svg, w = d.chip(cx, cy, c, (P["lime"], P["cyan"], P["violet"], P["amber"], P["crimson"])[i % 5])
        d.add(svg)
        cx += w + 6
    ly = H - 30
    d.add(f'<circle cx="{X + 5}" cy="{ly - 4}" r="5" fill="{lang[1]}"/>')
    d.add(d.mono(X + 16, ly, [(lang[0], P["text"]), ("  ·  view source ", P["dim"]),
                              ("→", P["lime"], 700)], size=12))
    # terminal inset on the right
    tx, ty, tw, th = 436, 50, 440, H - 76
    d.add(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="8" fill="{P["deep"]}" '
          f'stroke="{P["line"]}"/>')
    snippet(d, tx + 16, ty + 24)
    d.add(d.scanlines(tx + 1, ty + 1, tw - 2, th - 2, clip_r=8))
    return d


def snip_listly(d: Doc, x: float, y: float) -> None:
    S, L = 12, 18
    cw = S * ADV
    t = .6
    d.add(d.mono(x, y, [("$ ", P["lime"], 700)], size=S))
    tw, t = d.typed(x + 2 * cw, y, "tree -L 1 Listly/", t, cps=16, size=S, bg=P["deep"])
    d.add(tw)
    lines = [
        [("Listly/", P["cyan"], 700)],
        [("├── ", P["dim"]), ("backend/  ", P["cyan"]), ("# Python 3.12 · Flask · JWT", P["dim"])],
        [("├── ", P["dim"]), ("frontend/ ", P["cyan"]), ("# Vue 3 · Vite · Pinia · i18n", P["dim"])],
        [("├── ", P["dim"]), ("docker/   ", P["cyan"]), ("# multi-stage → Gunicorn", P["dim"])],
        [("└── ", P["dim"]), ("doc/", P["cyan"])],
    ]
    t += .25
    for i, sp in enumerate(lines):
        d.add(d.at(d.mono(x, y + (i + 1) * L, sp, size=S), t + i * .09))
    y2 = y + 6 * L
    t2 = t + .8
    d.add(d.at(d.mono(x, y2, [("$ ", P["lime"], 700)], size=S), t2))
    tw, t3 = d.typed(x + 2 * cw, y2, "docker compose up -d --build", t2 + .3, cps=18, size=S,
                     bg=P["deep"])
    d.add(d.at(tw, t2))
    d.add(d.at(d.mono(x, y2 + L, [(" ✓ ", P["lime"], 700), ("Container listly  ", P["text"]),
                                   ("Started", P["lime"], 700)], size=S), t3 + .5))
    d.add(d.at(d.mono(x, y2 + 2 * L, [("$ ", P["lime"], 700)], size=S) + d.caret(x + 2 * cw, y2 + 2 * L, S),
               t3 + .8))


def snip_cmdb(d: Doc, x: float, y: float) -> None:
    S, L = 12, 18
    cw = S * ADV
    d.add(d.mono(x, y, [("$ ", P["lime"], 700)], size=S))
    tw, t = d.typed(x + 2 * cw, y, "shadoucmdb migrate", .6, cps=15, size=S, bg=P["deep"])
    d.add(tw)
    out = [
        [("Connected to database ", P["text"]), ('"shadoucmdb"', P["amber"]),
         (" (PostgreSQL 18.1)", P["text"])],
        [("Migrations: ", P["text"]), ("10", P["cyan"], 700), (" in binary, 0 applied, ", P["text"]),
         ("10", P["cyan"], 700), (" pending", P["text"])],
        [("  applied ", P["dim"]), ("0000_extensions", P["lime"])],
        [("  applied ", P["dim"]), ("0001_core_schema", P["lime"])],
        [("  applied ", P["dim"]), ("0002_integrity_triggers", P["lime"])],
        [("  …", P["dim"])],
        [("Database is at migration ", P["text"]), ("10/10", P["lime"], 700), ("  ✓", P["lime"], 700)],
    ]
    t += .35
    delays = [0, .35, .7, .82, .94, 1.06, 1.5]
    for i, sp in enumerate(out):
        d.add(d.at(d.mono(x, y + (i + 1) * L, sp, size=S), t + delays[i]))
    yl = y + 8 * L
    d.add(d.at(d.mono(x, yl, [("$ ", P["lime"], 700)], size=S) + d.caret(x + 2 * cw, yl, S), t + 1.9))


def snip_feral(d: Doc, x: float, y: float) -> None:
    S, L = 12, 18
    rows = [
        ("--- a/FeralHeart (2011 client)", P["crimson"], .55),
        ("+++ b/FeralHeart (modernized)", P["lime"], .55),
        ("- OGRE 1.7.4 · VS2013 · x86 · Direct3D", P["crimson"], 1),
        ("+ OGRE 14.5.2 · VS2022 · x64 · OpenGL 3+", P["lime"], 1),
        ("- flat water plane · SkyX · MD5 passwords", P["crimson"], 1),
        ("+ simplex-noise water · synced sky dome", P["lime"], 1),
        ("+ soft PCF shadows · 48 lights · bloom", P["lime"], 1),
        ("+ SHA-256 on the client → Argon2id server", P["lime"], 1),
    ]
    for i, (s, col, op) in enumerate(rows):
        yy = y + i * L
        if s[0] in "+-" and s[1] == " ":
            band = "#0f2a12" if s[0] == "+" else "#2a0f16"
            d.add(d.at(f'<rect x="{n(x - 10)}" y="{n(yy - 13)}" width="420" height="{L}" '
                       f'fill="{band}" opacity=".9"/>', .5 + i * .18))
        d.add(d.at(d.text(x, yy, s, size=S, fill=col, opacity=op if op < 1 else None), .5 + i * .18))


def build_card_listly() -> Doc:
    return card(
        "Listly", [("Listly", P["text"]), (".", P["lime"])], "◆ FEATURED BUILD",
        ["Self-hosted household management: shared",
         "shopping lists, a recipe cookbook, meal",
         "planner & storage inventory — as a PWA."],
        ["Vue 3", "Flask", "SQLite", "Docker", "PWA"], ("Vue", "#41b883"), snip_listly,
        "Listly. - a self-hosted household app with shared shopping lists, recipes, "
        "a meal planner and storage inventory. Vue 3, Flask, SQLite, Docker.")


def build_card_cmdb() -> Doc:
    return card(
        "ShadouCMDB", [("Shadou", P["text"]), ("CMDB", P["cyan"])], "◆ BUILD · RUST",
        ["A self-hosted Configuration Management",
         "Database: servers, VMs, apps & services",
         "as CIs, joined by typed relationships."],
        ["Rust", "Axum", "sqlx", "PostgreSQL", "Vue 3"], ("Rust", "#dea584"), snip_cmdb,
        "ShadouCMDB - a self-hosted Configuration Management Database written in Rust "
        "(Axum, Tokio, sqlx) on PostgreSQL, with a Vue 3 web UI.")


def build_card_feral() -> Doc:
    return card(
        "FeralHeart", [("Feral", P["text"]), ("Heart", P["crimson"])], "◆ ENGINE MODERNIZATION",
        ["KovuLKD's 2011 3D online multiplayer RPG:",
         "full C++ client + 3-process server stack,",
         "dragged into the modern era."],
        ["C++", "OGRE 14", "OpenGL", "MySQL", "Argon2id"], ("C++", "#f34b7d"), snip_feral,
        "FeralHeart - modernizing the 2011 C++ codebase: OGRE 1.7 to 14.5, x64, OpenGL, "
        "new water, sky, soft shadows, bloom and Argon2id authentication.")


# ==========================================================================
# loadout - MOBA ability bar
# ==========================================================================
def keycap(d: Doc, x, y, s, key, mono, name, tag, color, *, cast=None, cycle=7.0,
           mono_size=28, name_size=13) -> None:
    r = 10
    cid = d.uid("kc")
    d.define(f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{r}"/></clipPath>')
    d.add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{r}" fill="{P["panel"]}"/>'
          f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{r}" fill="{color}" opacity=".07"/>'
          f'<rect x="{x + .75}" y="{y + .75}" width="{s - 1.5}" height="{s - 1.5}" rx="{r}" fill="none" '
          f'stroke="{color}" stroke-opacity=".75" stroke-width="1.5"/>')
    d.add(d.text(x + s / 2, y + s / 2 + mono_size * .36, mono, size=mono_size, weight=800,
                 fill=color, anchor="middle"))
    if cast is not None:
        R = s * .75
        C = 2 * math.pi * (R / 2)
        kf = f"cd{int(s)}"
        if kf not in "".join(d.css):
            d.style(f"@keyframes {kf}{{0%{{stroke-dashoffset:0;opacity:1}}"
                    f"38%{{stroke-dashoffset:{C:.1f};opacity:1}}39%,100%{{stroke-dashoffset:{C:.1f};opacity:0}}}}"
                    "@keyframes flash{0%{opacity:.55}8%,100%{opacity:0}}")
        cxm, cym = x + s / 2, y + s / 2
        d.add(f'<g clip-path="url(#{cid})">'
              f'<circle cx="{n(cxm)}" cy="{n(cym)}" r="{n(R / 2)}" fill="none" stroke="#000" '
              f'stroke-width="{n(R)}" stroke-dasharray="{C:.1f} {C:.1f}" '
              f'transform="rotate(90 {n(cxm)} {n(cym)}) scale(-1 1) translate({n(-2 * cxm)} 0)" '
              f'style="opacity:0;animation:{kf} {cycle}s linear {cast:.2f}s infinite" '
              f'stroke-opacity=".62"/>'
              f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{color}" '
              f'style="opacity:0;animation:flash {cycle}s linear {cast:.2f}s infinite"/></g>')
    # keybind badge
    b = 18 if s > 70 else 16
    d.add(f'<rect x="{x - 5}" y="{y - 5}" width="{b}" height="{b}" rx="4" fill="{color}"/>')
    d.add(d.text(x - 5 + b / 2, y - 5 + b / 2 + 4, key, size=11, weight=800, fill=P["bg"],
                 anchor="middle"))
    d.add(d.text(x + s / 2, y + s + 20, name, size=name_size, weight=700, fill=P["text"],
                 anchor="middle"))
    if tag:
        d.add(d.text(x + s / 2, y + s + 36, tag, size=11, fill=P["dim"], anchor="middle"))


def build_loadout() -> Doc:
    W, H = 900, 300
    d = Doc(W, H, "Loadout - the stack as a MOBA ability bar",
            "Abilities: Python (main), Vue 3, Rust, Docker. Summoners: Linux, Git. "
            "Inventory: C++, JavaScript, TypeScript, Java, PostgreSQL, SQLite, HTML/CSS; "
            "trinket: VS Code. "
            "Currently leveling: Godot.")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("loadout — keybinds.cfg", x=wx, y=wy, w=ww, h=wh))
    lab = dict(size=11, weight=700, fill=P["dim"], spacing=1.5)
    d.add(d.text(32, 64, "ABILITIES", **lab))
    d.add(d.text(448, 64, "SUMMONERS", **lab))
    d.add(d.text(612, 64, "INVENTORY", **lab))
    abil = [("Q", "Py", "Python", "main", P["lime"], .8),
            ("W", "Vue", "Vue 3", "Listly. UI", P["cyan"], 1.9),
            ("E", "Rs", "Rust", "ShadouCMDB", P["crimson"], 1.35),
            ("R", "Dk", "Docker", "ships it all", P["violet"], 2.6)]
    for i, (k, m, nm, tg, c, cast) in enumerate(abil):
        keycap(d, 36 + i * 102, 82, 84, k, m, nm, tg, c, cast=cast)
    for i, (k, m, nm, tg, cast) in enumerate((("D", "Lx", "Linux", "home turf", 4.2),
                                              ("F", "Git", "Git", "flash back", 4.9))):
        keycap(d, 452 + i * 78, 82, 60, k, m, nm, tg, P["amber"], cast=cast, mono_size=20,
               name_size=12)
    inv = [("C++", "C++", "FeralHeart"), ("JS", "JavaScript", None), ("TS", "TypeScript", None),
           ("Jv", "Java", None), ("PG", "PostgreSQL", None), ("SQ", "SQLite", "Listly."),
           ("</>", "HTML/CSS", None), ("VSC", "VS Code", "trinket")]
    for i, (m, nm, note) in enumerate(inv):
        c, r = i % 2, i // 2
        x, y = 612 + c * 136, 76 + r * 44
        trinket = note == "trinket"
        col = P["cyan"] if trinket else P["mute"]
        rx_ = 17 if trinket else 7
        d.add(f'<rect x="{x}" y="{y}" width="34" height="34" rx="{rx_}" fill="{P["panel"]}" '
              f'stroke="{col}" stroke-width="1.3"/>')
        d.add(d.text(x + 17, y + 21.5, m, size=11 if len(m) > 2 else 12, weight=800,
                     fill=P["cyan"] if trinket else P["text"], anchor="middle"))
        d.add(d.text(x + 44, y + 15, nm, size=12, weight=700, fill=P["text"]))
        if note:
            d.add(d.text(x + 44, y + 30, note, size=10, fill=P["lime"] if trinket else P["dim"]))

    # xp bar
    by = H - 42
    d.add(d.mono(32, by + 4, [("LEVELING ", P["dim"], 700), ("Godot", P["lime"], 800)], size=12))
    bx, bw = 160, 540
    d.add(f'<rect x="{bx}" y="{by - 6}" width="{bw}" height="10" rx="5" fill="{P["panel"]}" '
          f'stroke="{P["line"]}"/>')
    d.define(f'<linearGradient id="xp" x1="0" x2="1"><stop offset="0" stop-color="{P["lime"]}"/>'
             f'<stop offset="1" stop-color="{P["cyan"]}"/></linearGradient>')
    d.style("@keyframes xp{0%{transform:scaleX(.18)}70%,100%{transform:scaleX(.62)}}")
    d.add(f'<rect x="{bx + 2}" y="{by - 4}" width="{bw - 4}" height="6" rx="3" fill="url(#xp)" '
          f'style="transform-box:fill-box;transform-origin:0 50%;transform:scaleX(.62);'
          f'animation:xp 5s cubic-bezier(.2,.7,.2,1) .8s both"/>')
    d.add(d.mono(bx + bw + 16, by + 4, [("side quest · 2025", P["dim"])], size=12))
    return d


# ==========================================================================
# homelab - rack
# ==========================================================================
def rack_unit(d: Doc, x, y, w, h, *, online: bool, label: str) -> None:
    d.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{P["panel"]}" '
          f'stroke="{P["line"]}" stroke-width="1.5"/>')
    # screws
    for sx in (x + 8, x + w - 8):
        for sy in (y + 10, y + h - 10):
            d.add(f'<circle cx="{sx}" cy="{sy}" r="2.2" fill="{P["mute"]}"/>')
    # power + status led
    px, py = x + 34, y + h / 2 - 8
    col = P["lime"] if online else P["amber"]
    d.add(f'<circle cx="{px}" cy="{py}" r="10" fill="none" stroke="{P["dim"]}" stroke-width="1.5"/>'
          f'<path d="M{px} {py - 6}v6" stroke="{P["dim"]}" stroke-width="1.5" stroke-linecap="round"/>')
    anim = "pulse" if online else "breathe"
    d.add(f'<circle cx="{px}" cy="{py + 22}" r="3.2" fill="{col}" class="{anim}"/>')
    d.add(d.text(px, y + h - 12, label, size=9, weight=800, fill=P["dim"], anchor="middle",
                 spacing=1))
    # drive bays
    for i in range(6):
        bx = x + 64 + i * 34
        d.add(f'<rect x="{bx}" y="{y + 12}" width="28" height="{h - 24}" rx="3" fill="{P["deep"]}" '
              f'stroke="{P["line"]}"/>')
        for k in range(4):
            d.add(f'<path d="M{bx + 6} {y + 22 + k * 5}h16" stroke="{P["mute"]}" stroke-width="1.2"/>')
        led = f'<rect x="{bx + 10}" y="{y + h - 24}" width="8" height="3" rx="1.5" fill="{col}"'
        if online:
            dur = (1.1, .7, 1.7, .9, 2.3, 1.3)[i]
            delay = (0, .3, .9, .15, .6, 1.1)[i]
            d.add(led + f' style="animation:hdd {dur}s steps(1,end) {delay}s infinite"/>')
        else:
            d.add(led + ' opacity=".25"/>')
    # fan
    fx, fy = x + w - 58, y + h / 2
    d.add(f'<circle cx="{fx}" cy="{fy}" r="30" fill="{P["deep"]}" stroke="{P["line"]}"/>')
    for rr in (24, 17, 10):
        d.add(f'<circle cx="{fx}" cy="{fy}" r="{rr}" fill="none" stroke="{P["mute"]}" '
              f'stroke-width=".8" opacity=".6"/>')
    blades = "".join(
        f'<path d="M{fx} {fy}q10 -6 6 -24q-12 2 -6 24z" fill="{P["dim"]}" opacity=".85" '
        f'transform="rotate({a} {fx} {fy})"/>' for a in range(0, 360, 72))
    spin = ' style="transform-box:view-box;transform-origin:%spx %spx;animation:spin .9s linear infinite"' % (fx, fy) \
        if online else ""
    d.add(f'<g{spin}>{blades}</g>')
    d.add(f'<circle cx="{fx}" cy="{fy}" r="5" fill="{P["mute"]}"/>')


def build_homelab() -> Doc:
    W, H = 900, 452
    d = Doc(W, H, "Homelab - two self-built servers",
            "Main server (online 24/7): Intel Core i5-14600K, 48 GB DDR4, 66 TB+, running "
            "Home Assistant, Zigbee2MQTT, Mosquitto, Jellyfin, n8n, a personal cloud, Listly., "
            "Nginx Proxy Manager and PostgreSQL. Game server on standby with AMP and MinIO.")
    d.style("@keyframes hdd{0%{opacity:1}50%{opacity:.15}}"
            "@keyframes spin{to{transform:rotate(360deg)}}"
            "@keyframes breathe{50%{opacity:.2}}.breathe{animation:breathe 4s ease-in-out infinite}")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("shadou@homelab: ~ — rack view", x=wx, y=wy, w=ww, h=wh))
    # rack frame
    rx, ry, rw, rh = 32, 56, 420, 226
    d.add(f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="8" fill="{P["deep"]}" '
          f'stroke="{P["line"]}" stroke-width="1.5"/>')
    for sx in (rx + 6, rx + rw - 16):
        d.add(f'<rect x="{sx}" y="{ry + 6}" width="10" height="{rh - 12}" rx="2" fill="{P["panel"]}"/>')
        for k in range(17):
            d.add(f'<rect x="{sx + 3}" y="{ry + 12 + k * 12.5}" width="4" height="4" rx="1" '
                  f'fill="{P["deep"]}"/>')
    rack_unit(d, rx + 22, ry + 12, rw - 44, 94, online=True, label="MAIN")
    rack_unit(d, rx + 22, ry + 120, rw - 44, 94, online=False, label="GAME")

    X = 482
    S = 12
    d.add(d.mono(X, 84, [("MAIN SERVER", P["text"], 800), ("  ● ONLINE 24/7", P["lime"], 700)], size=13))
    specs = [("CPU", "Intel Core i5-14600K"), ("MEMORY", "48 GB DDR4"), ("STORAGE", "66 TB+ disk space")]
    for i, (k, v) in enumerate(specs):
        d.add(d.mono(X, 108 + i * 19, [(f"{k:<9}", P["dim"], 700), (v, P["text"])], size=S))

    d.add(d.mono(X, 200, [("GAME SERVER", P["text"], 800), ("  ○ STANDBY", P["amber"], 700)], size=13))
    d.add(d.mono(X, 224, [("CPU ", P["dim"], 700), ("TBD", P["text"]), ("  MEMORY ", P["dim"], 700),
                          ("TBD", P["text"]), ("  STORAGE ", P["dim"], 700), ("TBD", P["text"])], size=S))
    d.add(d.mono(X, 243, [("READY    ", P["dim"], 700), ("AMP", P["amber"], 700), (" game panel", P["dim"]),
                          (" · ", P["dim"]), ("MinIO", P["amber"], 700), (" storage", P["dim"])], size=S))
    d.add(d.mono(X, 262, [("powers on when needed — game hosting", P["dim"])], size=S))

    # services grid
    d.add(d.text(32, 316, "// RUNNING ON MAIN", size=11, weight=700, fill=P["dim"], spacing=1.5))
    svcs = [("Home Assistant", "smart home hub"), ("Zigbee2MQTT", "zigbee bridge"),
            ("Mosquitto", "MQTT broker"), ("Jellyfin", "media streaming"),
            ("n8n", "automations"), ("Personal Cloud", "my own storage"),
            ("Listly.", "household app"), ("Nginx Proxy Manager", "proxy"),
            ("PostgreSQL", "some databases")]
    for i, (nm, role) in enumerate(svcs):
        c, r = i % 3, i // 3
        x, y = 32 + c * 284, 334 + r * 34
        d.add(f'<rect x="{x}" y="{y}" width="272" height="28" rx="6" fill="{P["panel"]}" '
              f'stroke="{P["line"]}"/>')
        delay = (i * .37) % 2.4
        d.add(f'<circle cx="{x + 14}" cy="{y + 14}" r="3.5" fill="{P["lime"]}" class="pulse" '
              f'style="animation-delay:{delay:.2f}s"/>')
        d.add(d.mono(x + 26, y + 18, [(nm, P["text"], 700), ("  " + role, P["dim"])], size=12))
    return d


# ==========================================================================
# system log - journalctl
# ==========================================================================
def build_syslog() -> Doc:
    W, H = 900, 322
    d = Doc(W, H, "System log - a few moments worth remembering",
            "2018 Nightcore videos; 2019 first lines of code; 2020 Shizume, a Discord bot in Python; "
            "2021 closed the Nightcore chapter; 2022 apprenticeship as IT Systems Electronics "
            "Technician, completed 2025; 2025 picked up Godot; 2026 Listly. takes shape; now tinkering.")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("journalctl — shadou.service", x=wx, y=wy, w=ww, h=wh))
    X, cw = 32, 13 * ADV
    p, cx = prompt(d, X, 66)
    tw, t = d.typed(cx, 66, "journalctl -u shadou --since 2018 --no-pager", .5, cps=24)
    d.add(p + tw)
    d.add(d.at(d.text(X, 92, "-- Journal begins 2018 · host: shadou@germany --", fill=P["dim"]), t + .2))
    log = [
        ("2018", "nightcore", "started making & uploading Nightcore videos — my first taste of creating online", None),
        ("2019", "code", "first lines of code — no course, no plan, just curiosity and trial & error", None),
        ("2020", "shizume", "Shizume goes online — my first Discord bot, written from scratch in Python", "hi"),
        ("2021", "nightcore", "closing the Nightcore chapter after three years", "warn"),
        ("2022", "career", "started my apprenticeship as an IT Systems Electronics Technician", None),
        ("2025", "career", "apprenticeship completed ✓", "ok"),
        ("2025", "godot", "picked up Godot — game dev in my spare time", None),
        ("2026", "listly", "Listly. takes shape — self-hosted household app, Vue 3 + Flask in Docker", "hi"),
        ("NOW ", "*", "tinkering around — head-down on Listly., always picking up something new", "now"),
    ]
    t0 = t + .45
    for i, (yr, unit, msg, lvl) in enumerate(log):
        y = 116 + i * 21
        msg_col = {"warn": P["amber"], "ok": P["lime"], "hi": P["text"], "now": P["text"]}.get(lvl, P["text"])
        wgt = 700 if lvl in ("hi", "now", "ok") else 400
        unit_s = f"shadou[{unit}]:"
        spans = [(yr, P["cyan"], 700), ("  " + f"{unit_s:<19}", P["lime"] if lvl == "now" else P["dim"]),
                 (msg, msg_col, wgt)]
        line = d.mono(X, y, spans)
        if lvl == "now":
            end_x = X + (4 + 2 + 19 + len(msg) + 1) * cw
            line += d.caret(end_x, y)
            d.add(f'<rect x="{wx + 1}" y="{y - 15}" width="{ww - 2}" height="21" fill="{P["lime"]}" '
                  f'fill-opacity=".07" class="ap" style="animation-delay:{t0 + i * .17:.2f}s"/>')
        d.add(d.at(line, t0 + i * .17))
    return d


# ==========================================================================
# footer - exit + tmux status line
# ==========================================================================
def build_footer() -> Doc:
    W, H = 900, 176
    d = Doc(W, H, "End of line - thanks for stopping by",
            "The session logs out: connection to shadoukita.com closed. A tmux status bar "
            "shows the windows readme, listly, homelab.")
    wx, wy, ww, wh = 8, 6, W - 16, H - 14
    d.add(d.window("shadou@github: ~", x=wx, y=wy, w=ww, h=wh))
    X = 32
    p, cx = prompt(d, X, 66)
    tw, t = d.typed(cx, 66, "exit", .8, cps=8)
    d.add(p + tw)
    d.add(d.at(d.text(X, 88, "logout", fill=P["dim"]), t + .3))
    d.add(d.at(d.mono(X, 110, [("Connection to ", P["dim"]), ("shadoukita.com", P["cyan"], 700),
                                (" closed.", P["dim"])]), t + .7))
    d.add(d.at(d.mono(X, 132, [("// end of line — ", P["lime"], 700), ("thanks for stopping by", P["text"]),
                                ("  ◆", P["lime"], 700)]) + d.caret(X + 44 * 13 * ADV, 132), t + 1.2))
    # tmux status bar
    by = wy + wh - 22
    d.add(f'<path d="M{wx} {by}h{ww}v12a10 10 0 0 1 -10 10h-{ww - 20}a10 10 0 0 1 -10 -10z" '
          f'fill="{P["lime"]}"/>')
    d.add(d.mono(X - 12, by + 15, [("[shadou] ", P["bg"], 800), ("0:readme*", P["bg"], 800),
                                   ("  1:listly  2:homelab  3:godot", P["bg"])], size=12))
    d.add(d.text(wx + ww - 14, by + 15, "◆ shadoukita.com │ DE │ since 2019", size=12, weight=700,
                 fill=P["bg"], anchor="end"))
    return d


# ==========================================================================
# link buttons
# ==========================================================================
def button(glyph: str, label: str, handle: str, color: str) -> Doc:
    W, H = 212, 52
    d = Doc(W, H, f"{label} - {handle}", f"Link button: {label} {handle}")
    d.add(f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{P["bg"]}" '
          f'stroke="{P["line"]}" stroke-width="1.5"/>')
    d.add(f'<rect x="10" y="10" width="32" height="32" rx="8" fill="{color}" fill-opacity=".12" '
          f'stroke="{color}" stroke-opacity=".7"/>')
    d.add(d.text(26, 31, glyph, size=15, weight=800, fill=color, anchor="middle"))
    d.add(d.text(54, 23, label, size=13, weight=700, fill=P["text"]))
    d.add(d.text(54, 40, handle, size=11, fill=P["dim"]))
    d.add(d.text(W - 14, 31, "↗", size=13, weight=700, fill=color, anchor="end"))
    return d


BUILDERS = {
    "header": build_header,
    "currently": build_currently,
    "card-listly": build_card_listly,
    "card-shadoucmdb": build_card_cmdb,
    "card-feralheart": build_card_feral,
    "loadout": build_loadout,
    "homelab": build_homelab,
    "syslog": build_syslog,
    "footer": build_footer,
    "btn-website": lambda: button("◆", "website", "shadoukita.com", P["lime"]),
    "btn-discord": lambda: button("#", "discord", "@shadoukita", P["violet"]),
    "btn-x": lambda: button("X", "x / twitter", "@Shadoukita1", P["text"]),
    "btn-instagram": lambda: button("◎", "instagram", "@shadoukita", P["crimson"]),
}


def main(names: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in BUILDERS.items():
        if names and name not in names:
            continue
        size = fn().save(OUT / f"{name}.svg")
        print(f"  assets/{name}.svg  {size / 1024:6.1f} KB")
    if not names or "diamond" in names:
        (OUT / "diamond.stl").write_text(diamond_stl() + "\n", encoding="utf-8")
        print("  assets/diamond.stl  (also pasted into the README's ```stl block)")



# ==========================================================================
# ◆ in 3D - ASCII STL gem (GitHub renders ```stl blocks as a 3D viewer)
# ==========================================================================
def diamond_stl() -> str:
    """A brilliant-style gem: 8-sided table, 16-point girdle, pointed pavilion.
    Every facet's normal points outwards; the mesh is closed."""
    tz, cz, pz = .38, 0.0, -1.05          # table height, girdle, culet depth
    tr, gr = .56, 1.0                      # table / girdle radius
    T = [(tr * math.cos(math.radians(45 * i)), tr * math.sin(math.radians(45 * i)), tz) for i in range(8)]
    G = [(gr * math.cos(math.radians(22.5 * j)), gr * math.sin(math.radians(22.5 * j)), cz) for j in range(16)]
    top, cul = (0.0, 0.0, tz), (0.0, 0.0, pz)
    tris = []
    for i in range(8):                                     # table
        tris.append((top, T[i], T[(i + 1) % 8]))
    for i in range(8):                                     # crown: 3 facets per sector
        a, b = T[i], T[(i + 1) % 8]
        g0, g1, g2 = G[2 * i], G[2 * i + 1], G[(2 * i + 2) % 16]
        tris += [(a, g0, g1), (a, g1, b), (b, g1, g2)]
    for j in range(16):                                    # pavilion
        tris.append((cul, G[(j + 1) % 16], G[j]))

    def sub(p, q):
        return (p[0] - q[0], p[1] - q[1], p[2] - q[2])

    def cross(u, v):
        return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])

    out = ["solid diamond"]
    for a, b, c in tris:
        nx, ny, nz = cross(sub(b, a), sub(c, a))
        cen = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3)
        if nx * cen[0] + ny * cen[1] + nz * (cen[2] - (tz + pz) / 2) < 0:   # force outward
            b, c = c, b
            nx, ny, nz = -nx, -ny, -nz
        ln = math.sqrt(nx * nx + ny * ny + nz * nz)
        f = lambda v: " ".join(f"{x:.4f}".rstrip("0").rstrip(".").replace("-0", "0") if abs(x) < 5e-5
                               else f"{x:.4f}".rstrip("0").rstrip(".") for x in v)
        out.append(f"facet normal {f((nx / ln, ny / ln, nz / ln))}")
        out.append("outer loop")
        for v in (a, b, c):
            out.append(f"vertex {f(v)}")
        out.append("endloop")
        out.append("endfacet")
    out.append("endsolid diamond")
    return "\n".join(out)


if __name__ == "__main__":
    main(sys.argv[1:])
