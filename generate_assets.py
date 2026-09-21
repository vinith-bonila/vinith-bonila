import math, random, os

THEMES = {
    "light": dict(bg="#EEF1EC", panel="#F7F9F6", grid="#CBD5CE", grid2="#DDE4DF", ink="#1E2A2B",
                  mute="#5D6B67", gr="#2F7D4F", res="#C0392B", neu="#2E5AAC", sand="#E4BE62",
                  shale="#9AA7A0", zone="#E3E9E4"),
    "dark":  dict(bg="#141D1B", panel="#1A2522", grid="#2C3B37", grid2="#223029", ink="#E4EBE7",
                  mute="#93A39D", gr="#5CC08A", res="#EF6F5E", neu="#72A0EC", sand="#D6B257",
                  shale="#5E6E68", zone="#1F2B28"),
}
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "SFMono-Regular,Consolas,'Liberation Mono',Menlo,monospace"


def curve(seed, x0, x1, y0, y1, zones, step=4):
    """Smooth well-log style curve; zones = list of (y_top, y_bot, base 0..1)."""
    rnd = random.Random(seed)
    pts, v = [], 0.5
    y = y0
    while y <= y1:
        base = 0.5
        for zt, zb, b in zones:
            if zt <= y <= zb:
                base = b
        v += (base - v) * 0.18 + rnd.uniform(-0.09, 0.09)
        v = min(0.95, max(0.05, v))
        pts.append((x0 + (x1 - x0) * v, y))
        y += step
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        px, py = pts[i - 1]; cx, cy = pts[i]
        my = (py + cy) / 2
        d += f" C{px:.1f},{my:.1f} {cx:.1f},{my:.1f} {cx:.1f},{cy:.1f}"
    return d


def grid(x0, x1, y0, y1, dx, dy, c, c2):
    out = []
    y = y0
    i = 0
    while y <= y1 + 0.1:
        out.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="{c if i % 5 == 0 else c2}" stroke-width="1"/>')
        y += dy; i += 1
    x = x0
    while x <= x1 + 0.1:
        out.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y1}" stroke="{c2}" stroke-width="1"/>')
        x += dx
    return "\n".join(out)


def hero(t):
    W, H = 1200, 460
    tx0, tx1, ty0, ty1 = 660, 1148, 96, 420
    zones = [  # top = now (surface), bottom = oldest
        ("AI products, agents", "now", 0.72),
        ("Data analytics, BI", "", 0.42),
        ("ONGC internship", "", 0.62),
        ("Petroleum eng., IIPE", "", 0.3),
        ("Freelance design", "2022", 0.5),
    ]
    zh = (ty1 - ty0) / len(zones)
    zrects, zlabels, zcurve1, zcurve2 = [], [], [], []
    for i, (name, dlabel, b) in enumerate(zones):
        yt = ty0 + i * zh
        fill = t["zone"] if i % 2 == 0 else t["panel"]
        zrects.append(f'<rect x="{tx0 + 60}" y="{yt:.1f}" width="{tx1 - tx0 - 60}" height="{zh:.1f}" fill="{fill}"/>')
        zlabels.append(f'<text x="{tx0 + 340}" y="{yt + zh / 2 + 5:.1f}" font-family="{SANS}" font-size="14" fill="{t["ink"]}">{name}</text>')
        if i:
            zlabels.append(f'<line x1="{tx0 + 60}" y1="{yt:.1f}" x2="{tx1}" y2="{yt:.1f}" stroke="{t["mute"]}" stroke-width="1" stroke-dasharray="4 3"/>')
        zcurve1.append((yt, yt + zh, b))
        zcurve2.append((yt, yt + zh, 1 - b * 0.8))
    g1 = curve(7, tx0 + 66, tx0 + 190, ty0, ty1, zcurve1)
    g2 = curve(21, tx0 + 196, tx0 + 326, ty0, ty1, zcurve2)
    ticks = []
    for k in range(0, 9):
        y = ty0 + k * (ty1 - ty0) / 8
        ticks.append(f'<line x1="{tx0 + 48}" y1="{y:.1f}" x2="{tx0 + 60}" y2="{y:.1f}" stroke="{t["mute"]}"/>')
    ticks.append(f'<text x="{tx0 + 42}" y="{ty0 + 5}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["ink"]}">2026</text>')
    ticks.append(f'<text x="{tx0 + 42}" y="{ty1 + 4}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t["ink"]}">2022</text>')
    ticks.append(f'<text x="{tx0 + 42}" y="{(ty0 + ty1) / 2 + 4}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t["mute"]}">depth</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Vinith Bonila - AI product engineer. Career shown as a well log, from petroleum engineering at the bottom to AI products at the surface.">
<style>
  .draw {{ stroke-dasharray: 2600; stroke-dashoffset: 2600; animation: log 3.6s cubic-bezier(.45,.05,.25,1) .3s forwards; }}
  .d2 {{ animation-delay: .7s; }}
  .bit {{ animation: bit 3.6s cubic-bezier(.45,.05,.25,1) .3s forwards; }}
  @keyframes log {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes bit {{ from {{ transform: translateY(0); }} to {{ transform: translateY({ty1 - ty0}px); }} }}
  @media (prefers-reduced-motion: reduce) {{ .draw {{ animation: none; stroke-dashoffset: 0; }} .bit {{ animation: none; }} }}
</style>
<rect width="{W}" height="{H}" rx="16" fill="{t["bg"]}"/>

<!-- identity -->
<text xml:space="preserve" x="56" y="92" font-family="{MONO}" font-size="13" fill="{t["mute"]}">well: vinith-bonila  |  field: visakhapatnam, IN</text>
<text x="52" y="170" font-family="{SANS}" font-size="64" font-weight="700" letter-spacing="-1.5" fill="{t["ink"]}">Vinith Bonila</text>
<text x="56" y="214" font-family="{SANS}" font-size="26" fill="{t["ink"]}">AI product engineer</text>
<text x="56" y="268" font-family="{SANS}" font-size="17" fill="{t["mute"]}">Petroleum engineer who now builds AI agents,</text>
<text x="56" y="292" font-family="{SANS}" font-size="17" fill="{t["mute"]}">RAG systems and data products.</text>
<text x="56" y="330" font-family="{SANS}" font-size="17" fill="{t["mute"]}">I still work the way logs taught me:</text>
<text x="56" y="354" font-family="{SANS}" font-size="17" fill="{t["mute"]}">measure first, then decide.</text>
<g font-family="{MONO}" font-size="12" fill="{t["mute"]}">
  <line x1="56" y1="396" x2="80" y2="396" stroke="{t["gr"]}" stroke-width="3"/><text x="88" y="400">what I build</text>
  <line x1="200" y1="396" x2="224" y2="396" stroke="{t["res"]}" stroke-width="3"/><text x="232" y="400">what I learn</text>
</g>

<!-- log track -->
<rect x="{tx0}" y="{ty0 - 40}" width="{tx1 - tx0}" height="{ty1 - ty0 + 48}" rx="10" fill="{t["panel"]}" stroke="{t["grid"]}"/>
<text x="{tx0 + 70}" y="{ty0 - 14}" font-family="{MONO}" font-size="12" fill="{t["gr"]}">build</text>
<text x="{tx0 + 202}" y="{ty0 - 14}" font-family="{MONO}" font-size="12" fill="{t["res"]}">learn</text>
<text x="{tx0 + 340}" y="{ty0 - 14}" font-family="{MONO}" font-size="12" fill="{t["mute"]}">formation</text>
{"".join(zrects)}
<g opacity=".9">{grid(tx0 + 60, tx0 + 330, ty0, ty1, 27, 16.2, t["grid"], t["grid2"])}</g>
<line x1="{tx0 + 193}" y1="{ty0}" x2="{tx0 + 193}" y2="{ty1}" stroke="{t["grid"]}" stroke-width="1.5"/>
<line x1="{tx0 + 330}" y1="{ty0}" x2="{tx0 + 330}" y2="{ty1}" stroke="{t["grid"]}" stroke-width="1.5"/>
{"".join(zlabels)}
{"".join(ticks)}
<path class="draw" d="{g1}" fill="none" stroke="{t["gr"]}" stroke-width="2.2" stroke-linecap="round"/>
<path class="draw d2" d="{g2}" fill="none" stroke="{t["res"]}" stroke-width="2.2" stroke-linecap="round"/>
<g class="bit"><path d="M{tx0 + 334},{ty0} l10,-6 v12 z" fill="{t["ink"]}"/></g>
</svg>'''


def card(t, name, tagline, readings, stack, color, seed):
    W, H = 580, 260
    rows = []
    y = 124
    for label, value in readings:
        rows.append(f'<text x="32" y="{y}" font-family="{SANS}" font-size="13" fill="{t["mute"]}">{label}</text>')
        rows.append(f'<text x="32" y="{y + 28}" font-family="{SANS}" font-size="24" font-weight="700" fill="{t["ink"]}">{value}</text>')
        y += 62
    strip = curve(seed, 488, 548, 24, H - 24, [(0, H, 0.5)], step=5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{name}: {tagline}">
<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>
<rect x="476" y="16" width="84" height="{H - 32}" rx="8" fill="{t["panel"]}" stroke="{t["grid"]}"/>
<g opacity=".8">{grid(482, 554, 24, H - 24, 18, 11.8, t["grid"], t["grid2"])}</g>
<path d="{strip}" fill="none" stroke="{color}" stroke-width="2"/>
<rect x="20" y="30" width="4" height="30" rx="2" fill="{color}"/>
<text x="32" y="54" font-family="{SANS}" font-size="28" font-weight="700" letter-spacing="-.5" fill="{t["ink"]}">{name}</text>
<text x="32" y="84" font-family="{SANS}" font-size="15" fill="{t["mute"]}">{tagline}</text>
{"".join(rows)}
<text x="32" y="{H - 22}" font-family="{MONO}" font-size="12" fill="{t["mute"]}">{stack}</text>
</svg>'''


def strata(t):
    W, H = 1200, 330
    layers = [
        ("Interface", "React, Next.js, TypeScript, Tailwind, Streamlit", "sand"),
        ("Service", "FastAPI, Pydantic, Docker, Render, Vercel", "lime"),
        ("Intelligence", "LLMs, RAG, agents, FAISS, BM25, HuggingFace, Groq, Whisper, spaCy", "shale"),
        ("Data", "Python, Pandas, NumPy, DuckDB, SQL, PostgreSQL, Supabase, Power BI", "base"),
    ]
    lh = 64; y0 = 50
    defs = f'''<defs>
<pattern id="sand" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="{t["sand"]}" opacity=".35"/><circle cx="3" cy="3" r="1.3" fill="{t["sand"]}"/><circle cx="8" cy="7" r="1" fill="{t["sand"]}"/></pattern>
<pattern id="lime" width="24" height="12" patternUnits="userSpaceOnUse"><rect width="24" height="12" fill="{t["neu"]}" opacity=".15"/><path d="M0 .5H24M0 6.5H24M6 .5V6.5M18 6.5V12" stroke="{t["neu"]}" stroke-width="1"/></pattern>
<pattern id="shale" width="16" height="8" patternUnits="userSpaceOnUse"><rect width="16" height="8" fill="{t["shale"]}" opacity=".25"/><path d="M1 4H9" stroke="{t["mute"]}" stroke-width="1.2"/></pattern>
<pattern id="base" width="14" height="14" patternUnits="userSpaceOnUse"><rect width="14" height="14" fill="{t["gr"]}" opacity=".18"/><path d="M0 14L14 0" stroke="{t["gr"]}" stroke-width="1"/></pattern>
</defs>'''
    body = []
    for i, (n, tools, p) in enumerate(layers):
        y = y0 + i * lh
        body.append(f'<rect x="40" y="{y}" width="150" height="{lh}" fill="url(#{p})" stroke="{t["ink"]}" stroke-width="1"/>')
        body.append(f'<text x="222" y="{y + 28}" font-family="{SANS}" font-size="19" font-weight="700" fill="{t["ink"]}">{n}</text>')
        body.append(f'<text x="222" y="{y + 50}" font-family="{SANS}" font-size="15" fill="{t["mute"]}">{tools}</text>')
        if i:
            body.append(f'<line x1="200" y1="{y}" x2="{W - 40}" y2="{y}" stroke="{t["grid"]}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack as rock layers: interface, service, intelligence, data">
{defs}
<rect width="{W}" height="{H}" rx="16" fill="{t["bg"]}"/>
<text x="40" y="34" font-family="{MONO}" font-size="12" fill="{t["mute"]}">stratigraphic column - the stack I build on, top to bedrock</text>
{"".join(body)}
</svg>'''


def footer(t):
    W, H = 1200, 70
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Total depth not reached - still drilling">
<style>.b{{animation:p 2.4s ease-in-out infinite}}@keyframes p{{50%{{opacity:.25}}}}@media (prefers-reduced-motion:reduce){{.b{{animation:none}}}}</style>
<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>
<line x1="40" y1="35" x2="{W - 360}" y2="35" stroke="{t["mute"]}" stroke-dasharray="6 5"/>
<text x="{W - 340}" y="40" font-family="{MONO}" font-size="14" fill="{t["ink"]}">TD not reached - still drilling</text>
<circle class="b" cx="{W - 60}" cy="35" r="6" fill="{t["gr"]}"/>
</svg>'''


CARDS = [
    ("autobi", "AutoBI", "Upload any CSV, get an interactive BI dashboard",
     [("Automated tests", "242 passing"), ("Numbers from", "code, never the LLM")],
     "Next.js / FastAPI / DuckDB / Pandas / Supabase", "gr", 3),
    ("docmind", "DocMind", "Hybrid-retrieval RAG document assistant",
     [("Retrieval", "recall@5 1.00, MRR 0.96"), ("Generation", "0.82 relevance, 0.78 faithful")],
     "FAISS / BM25 / RRF / reranker / FastAPI / Groq", "neu", 5),
    ("payment", "Payment Recovery Agent", "Triages failed payments and picks a recovery action",
     [("Mode", "agentic triage"), ("Improves via", "self-distillation")],
     "Python / FastAPI / LLM agents / Render", "res", 9),
    ("vini", "VINI AI", "NLP-first voice assistant",
     [("Intent routing", "~15-20 ms"), ("Intent catalog", "19 intents")],
     "Whisper / spaCy / sentence-transformers / Groq", "sand", 11),
]

for tn, t in THEMES.items():
    d = f"assets/{tn}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/hero.svg", "w").write(hero(t))
    open(f"{d}/stack.svg", "w").write(strata(t))
    open(f"{d}/footer.svg", "w").write(footer(t))
    for slug, n, tag, rd, st, c, s in CARDS:
        open(f"{d}/card-{slug}.svg", "w").write(card(t, n, tag, rd, st, t[c], s))
print("done")
