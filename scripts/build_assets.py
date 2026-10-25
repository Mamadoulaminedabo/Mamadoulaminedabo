"""Builds the animated SVGs of the profile README into `assets/`.

- fonts are subset by Google Fonts (`text=`) and embedded as data URIs: an SVG
  served as an image may not load anything external
- stdlib only; run from the repo root: `python3 scripts/build_assets.py`
"""

import base64
import math
import re
import textwrap
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

BG, LINE, TEXT, MUTED, DIM = "#07080b", "#ffffff", "#eceef3", "#9298a6", "#5d6270"
GREEN, CYAN, VIOLET = "#00e5a0", "#5ee7ff", "#7c6fff"
MONO_ADV = 0.6  # Geist Mono advance, in em

ROLES = ["real-time voice agents", "LLMs on real phone lines", "data pipelines", "web & mobile apps"]
HEADER = {
    "label": "MAMADOU LAMINE DABO  /  FULL-STACK & AI DEVELOPER  /  QUÉBEC",
    "tagline": "Real-time voice agents, data pipelines, web & mobile apps — built for production.",
    "prompt": "~/lamine >",
}
CARDS = [
    {
        "id": "voice", "meta": "CLIENT PROJECT", "badge": "PRIVATE CODE",
        "title": "Real-time AI voice agent",
        "desc": "A phone agent on a real number: streamed audio, a Realtime model, caller authentication, hand-off to a human and every call archived.",
        "chips": ["Python", "FastAPI", "Twilio", "Azure OpenAI"],
    },
    {
        "id": "off", "meta": "DATA ENGINEERING",
        "title": "OpenFoodFacts Pipeline",
        "desc": "Medallion architecture (bronze, silver, gold): MinIO data lake, columnar PostgreSQL, Airflow, a FastAPI API and a React UI.",
        "chips": ["Airflow", "MinIO", "PostgreSQL", "React"],
    },
    {
        "id": "shazam", "meta": "AUDIO PROCESSING",
        "title": "Shazam Clone",
        "desc": "Music recognition by audio fingerprinting: a few seconds of microphone input are enough to find the track.",
        "chips": ["librosa", "NumPy", "Flask", "Web Audio"],
    },
    {
        "id": "can", "meta": "MACHINE LEARNING",
        "title": "AFCON 2025 Prediction",
        "desc": "An ensemble of Random Forest, Gradient Boosting and a neural network predicting the winner of the Africa Cup of Nations.",
        "chips": ["scikit-learn", "XGBoost", "pandas"],
    },
    {
        "id": "circles", "meta": "C · SDL2",
        "title": "Circles",
        "desc": "An arcade game in C: a rotating player dodges dynamically generated circular obstacles, with sound and scoring.",
        "chips": ["C", "SDL2", "Make", "GitLab CI"],
    },
    {
        "id": "weather", "meta": "MOBILE",
        "title": "Sweet Weather",
        "desc": "A Flutter app with live weather for five cities through OpenWeatherMap, an animated gauge and periodic API calls.",
        "chips": ["Flutter", "Dart", "Retrofit"],
    },
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def font_faces() -> str:
    """One @font-face per family, subset to every glyph the SVGs use."""
    mono = " ".join([HEADER["label"], HEADER["prompt"], *ROLES] + [c["meta"] + c.get("badge", "") + "".join(c["chips"]) for c in CARDS])
    sans = " ".join([HEADER["tagline"], "Lamine"] + [c["title"] + c["desc"] for c in CARDS])
    families = [("Geist", "wght@400..700", sans, "normal", "400 700"),
                ("Geist Mono", "wght@400", mono, "normal", "400"),
                ("Instrument Serif", "ital@1", "Dabo.", "italic", "400")]
    css = []
    for name, axis, text, style, weight in families:
        q = urllib.parse.urlencode({"family": f"{name}:{axis}", "text": "".join(sorted(set(text)))})
        req = urllib.request.Request(f"https://fonts.googleapis.com/css2?{q}", headers={"User-Agent": UA})
        url = re.search(r"src: url\((.+?)\)", urllib.request.urlopen(req).read().decode()).group(1)
        data = base64.b64encode(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA})).read()).decode()
        css.append(f"@font-face{{font-family:'{name}';font-style:{style};font-weight:{weight};src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return "".join(css)


BASE_CSS = (
    ".sans{font-family:Geist,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}"
    ".mono{font-family:'Geist Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
    ".serif{font-family:'Instrument Serif',Georgia,serif;font-style:italic}"
    "@keyframes blink{50%{opacity:0}}"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
)


def wave_path(period: float, amp: float, y0: float, phase: float, width: float) -> str:
    pts = []
    x = -period
    while x <= width + period:
        t = 2 * math.pi * x / period
        y = y0 + amp * (0.72 * math.sin(t + phase) + 0.28 * math.sin(2 * t + phase * 1.7))
        pts.append(f"{x:.0f},{y:.1f}")
        x += 4
    return "M" + " L".join(pts)


def header(fonts: str) -> str:
    W, H = 1200, 420
    layers = [(300, 22, 9, 0.0, 1.0, 1.8), (220, 16, 7, 1.3, 0.55, 1.2), (400, 28, 13, 2.1, 0.35, 1.0), (260, 12, 5.5, 0.6, 0.28, 1.0)]
    waves, wave_css = [], []
    for i, (p, a, dur, ph, op, sw) in enumerate(layers):
        wave_css.append(f".w{i}{{animation:w{i} {dur}s linear infinite}}@keyframes w{i}{{to{{transform:translateX(-{p}px)}}}}")
        waves.append(f'<path class="w{i}" d="{wave_path(p, a, 368, ph, W)}" fill="none" stroke="#fff" stroke-opacity="{op}" stroke-width="{sw}"/>')

    x0, adv, cycle = 72, 17 * MONO_ADV, 3.2
    role_x = x0 + adv * (len(HEADER["prompt"]) + 1)
    roles = []
    for i, r in enumerate(ROLES):
        caret_x = role_x + adv * len(r) + 4
        roles.append(
            f'<g class="role" style="animation-delay:{i * cycle}s"><text class="mono" x="{role_x:.1f}" y="306" font-size="17" fill="{TEXT}">{esc(r)}</text>'
            f'<rect class="caret" x="{caret_x:.1f}" y="292" width="9" height="18" fill="{GREEN}"/></g>'
        )
    role_css = (f".role{{opacity:0;animation:role {cycle * len(ROLES)}s infinite}}"
                f"@keyframes role{{0%{{opacity:0;transform:translateY(8px)}}3%,22%{{opacity:1;transform:none}}25%,100%{{opacity:0;transform:translateY(-8px)}}}}"
                ".caret{animation:blink 1s steps(1) infinite}"
                ".glow{animation:pulse 9s ease-in-out infinite}.glow2{animation-delay:-4.5s}"
                "@keyframes pulse{50%{opacity:.45}}")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Lamine Dabo — full-stack and AI developer">
<defs>
<style>{fonts}{BASE_CSS}{"".join(wave_css)}{role_css}</style>
<linearGradient id="name" x1="430" x2="760" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{GREEN}"/><stop offset=".5" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<linearGradient id="wg" x1="0" x2="{W}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{GREEN}" stop-opacity="0"/><stop offset=".18" stop-color="{GREEN}"/><stop offset=".55" stop-color="{CYAN}"/><stop offset=".85" stop-color="{VIOLET}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
<radialGradient id="g1"><stop offset="0" stop-color="{GREEN}" stop-opacity=".22"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
<radialGradient id="g2"><stop offset="0" stop-color="{VIOLET}" stop-opacity=".22"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse"><path d="M48 0H0V48" fill="none" stroke="#fff" stroke-opacity=".045"/></pattern>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="gridmask"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
<mask id="wm">{"".join(waves)}</mask>
<clipPath id="clip"><rect width="{W}" height="{H}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#clip)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridmask)"/>
<circle class="glow" cx="140" cy="20" r="360" fill="url(#g1)"/>
<circle class="glow glow2" cx="1090" cy="140" r="330" fill="url(#g2)"/>
<rect x="{x0}" y="80" width="26" height="1.5" fill="{GREEN}"/>
<text class="mono" x="{x0 + 38}" y="86" font-size="13.5" letter-spacing="2.4" fill="{GREEN}">{esc(HEADER["label"])}</text>
<text x="{x0 - 6}" y="214"><tspan class="sans" font-size="124" font-weight="700" letter-spacing="-6.5" fill="{TEXT}">Lamine </tspan><tspan class="serif" font-size="136" letter-spacing="-3" fill="url(#name)">Dabo</tspan><tspan class="serif" font-size="136" fill="{GREEN}">.</tspan></text>
<text class="sans" x="{x0}" y="262" font-size="23" fill="{MUTED}">{esc(HEADER["tagline"])}</text>
<text class="mono" x="{x0}" y="306" font-size="17" fill="{GREEN}">{esc(HEADER["prompt"])}</text>
{"".join(roles)}
<rect y="322" width="{W}" height="98" fill="url(#wg)" mask="url(#wm)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="27.5" fill="none" stroke="#fff" stroke-opacity=".09"/>
</svg>
'''


def motif(kind: str) -> tuple[str, str]:
    """Small animated illustration (svg, css), drawn in a 96x80 box."""
    if kind == "voice":
        bars, css = [], []
        for i in range(14):
            h = 14 + 52 * abs(math.sin(i * 0.9 + 0.4)) * math.sin(math.pi * (i + 0.5) / 14)
            bars.append(f'<rect class="eq" x="{i * 7}" y="{40 - h / 2:.1f}" width="4" height="{h:.1f}" rx="2" fill="url(#mg)" style="animation-duration:{0.6 + (i * 37 % 50) / 70:.2f}s;animation-delay:-{(i * 53 % 90) / 100:.2f}s"/>')
        css.append(".eq{transform-box:fill-box;transform-origin:center;animation:eq .8s ease-in-out infinite alternate}@keyframes eq{from{transform:scaleY(.2)}}")
        return "".join(bars), "".join(css)
    if kind == "off":
        rows, css = [], []
        for i, (c, dur) in enumerate([("#d8935f", 1.4), ("#c3cbd8", 1.8), ("#f2c45a", 2.3)]):
            y = 14 + i * 26
            dots = "".join(f'<circle cx="{x}" cy="{y}" r="2.4" fill="{c}"/>' for x in range(-16, 112, 16))
            rows.append(f'<rect x="0" y="{y - 4}" width="96" height="8" rx="4" fill="#fff" fill-opacity=".05"/><g class="lane" style="animation-duration:{dur}s">{dots}</g>')
        css.append(".lane{animation:lane 1.6s linear infinite}@keyframes lane{to{transform:translateX(16px)}}")
        return f'<clipPath id="lc"><rect width="96" height="80"/></clipPath><g clip-path="url(#lc)">{"".join(rows)}</g>', "".join(css)
    if kind == "shazam":
        seed, pts = 11, []
        for _ in range(26):
            seed = (seed * 16807) % 2147483647
            x = 4 + seed / 2147483647 * 88
            seed = (seed * 16807) % 2147483647
            pts.append((x, 4 + seed / 2147483647 * 72))
        dots = "".join(f'<circle class="pk" cx="{x:.1f}" cy="{y:.1f}" r="1.8" style="animation-delay:{x / 96 * 2.6:.2f}s"/>' for x, y in pts)
        css = (f".pk{{fill:{CYAN};opacity:.25;animation:pk 2.6s linear infinite;transform-box:fill-box;transform-origin:center}}"
               f"@keyframes pk{{0%{{opacity:1;fill:{GREEN};transform:scale(1.8)}}15%,100%{{opacity:.25;transform:none}}}}"
               ".scan{animation:scan 2.6s linear infinite}@keyframes scan{from{transform:translateX(0)}to{transform:translateX(96px)}}")
        return dots + f'<g class="scan"><rect x="-1" width="1.5" height="80" fill="{GREEN}"/></g>', css
    if kind == "can":
        d_all = "M4 8h22v12h18M4 32h22V20M4 48h22v12h18M4 72h22V60M44 20v20h24M44 60V40M68 40h16"
        css = (".br{fill:none;stroke:url(#mg);stroke-width:2;stroke-dasharray:140;stroke-dashoffset:140;animation:br 4.5s ease-in-out infinite}"
               "@keyframes br{35%,85%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}"
               f".tr{{fill:{GREEN};transform-box:fill-box;transform-origin:center;animation:tr 4.5s ease-in-out infinite}}"
               "@keyframes tr{0%,40%{opacity:.15;transform:scale(.6)}55%,85%{opacity:1;transform:none}100%{opacity:.15}}")
        return (f'<path d="{d_all}" fill="none" stroke="#fff" stroke-opacity=".16" stroke-width="1.5"/>'
                '<path class="br" d="M4 8h22v12h18v20h24h16"/><path class="br" style="animation-delay:.35s" d="M4 72h22V60h18V40"/>'
                '<circle class="tr" cx="90" cy="40" r="5"/>'), css
    if kind == "circles":
        css = (".o{fill:none;stroke-width:2.5;stroke-linecap:round;transform-origin:48px 40px}"
               ".o1{animation:sp 8s linear infinite}.o2{animation:sp 5s linear infinite reverse}.o3{animation:sp 3.5s linear infinite}"
               "@keyframes sp{to{transform:rotate(360deg)}}")
        return (f'<circle class="o o1" cx="48" cy="40" r="36" stroke="{GREEN}" stroke-dasharray="86 27"/>'
                f'<circle class="o o2" cx="48" cy="40" r="25" stroke="{CYAN}" stroke-opacity=".7" stroke-dasharray="60 30"/>'
                f'<circle class="o o3" cx="48" cy="40" r="14" stroke="{VIOLET}" stroke-opacity=".6" stroke-dasharray="30 26"/>'
                f'<circle cx="48" cy="40" r="3" fill="{GREEN}"/>'), css
    css = (".gb{stroke-dasharray:126;stroke-dashoffset:126;animation:gb 5s ease-in-out infinite}"
           "@keyframes gb{70%,100%{stroke-dashoffset:0}}")
    return ('<path d="M8 66a40 40 0 0 1 80 0" fill="none" stroke="#fff" stroke-opacity=".09" stroke-width="8" stroke-linecap="round"/>'
            '<path class="gb" d="M8 66a40 40 0 0 1 80 0" fill="none" stroke="url(#mg)" stroke-width="8" stroke-linecap="round"/>'), css


def card(c: dict, fonts: str) -> str:
    W, H, pad = 420, 220, 24
    art, art_css = motif(c["id"])
    badge = f'<tspan fill="{GREEN}">  ·  {esc(c["badge"])}</tspan>' if c.get("badge") else ""
    lines = textwrap.wrap(c["desc"], 54)[:3]
    desc = "".join(f'<text class="sans" x="{pad}" y="{118 + i * 20}" font-size="13.5" fill="{MUTED}">{esc(line)}</text>' for i, line in enumerate(lines))
    chips, x = [], pad
    for chip in c["chips"]:
        w = len(chip) * 11 * MONO_ADV + 20
        chips.append(f'<rect x="{x:.1f}" y="{H - 44}" width="{w:.1f}" height="22" rx="11" fill="#fff" fill-opacity=".03" stroke="#fff" stroke-opacity=".1"/>'
                     f'<text class="mono" x="{x + 10:.1f}" y="{H - 29}" font-size="11" fill="{MUTED}">{esc(chip)}</text>')
        x += w + 7
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(c["title"])}">
<defs>
<style>{fonts}{BASE_CSS}{art_css}</style>
<linearGradient id="mg" x1="0" x2="1"><stop offset="0" stop-color="{GREEN}"/><stop offset=".55" stop-color="{CYAN}"/><stop offset="1" stop-color="{VIOLET}"/></linearGradient>
<radialGradient id="cg" cx="1" cy="0" r="1"><stop offset="0" stop-color="{GREEN}" stop-opacity=".12"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
</defs>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="#0b0d12" stroke="#fff" stroke-opacity=".09"/>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#cg)"/>
<text class="mono" x="{pad}" y="40" font-size="10.5" letter-spacing="1.3" fill="{DIM}">{esc(c["meta"])}{badge}</text>
<text class="sans" x="{pad}" y="78" font-size="21" font-weight="600" letter-spacing="-.5" fill="{TEXT}">{esc(c["title"])}</text>
{desc}
{"".join(chips)}
<g transform="translate({W - pad - 96} 18)">{art}</g>
</svg>
'''


def main() -> None:
    OUT.mkdir(exist_ok=True)
    fonts = font_faces()
    (OUT / "header.svg").write_text(header(fonts))
    for c in CARDS:
        (OUT / f"card-{c['id']}.svg").write_text(card(c, fonts))
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
