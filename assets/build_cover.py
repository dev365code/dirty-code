#!/usr/bin/env python3
"""표지 그림을 만든다. SVG로 그리고 크롬으로 찍는다.

그림: 표지 전체가 실타래처럼 얽힌 스파게티 코드다. 줄 하나하나가 코드 글자이고 무지개색이다.
그 줄이 제목을 쓴다. 제목은 활자가 아니다. 손으로 적은 획의 뼈대(STROKES)를 줄 여러 가닥이 따라가고,
가닥의 끝은 얽힘 속으로 풀려 나간다.

  /usr/bin/python3 assets/build_cover.py
      → assets/cover.png (1600×2400), assets/cover-web.jpg (대문에 싣는 1200×1800)
  /usr/bin/python3 assets/build_cover.py svg
      → assets/cover.svg 도 함께 쓴다 (글꼴을 품지 않으므로 글꼴이 깔린 곳에서만 제대로 보인다)

난수의 씨앗을 못 박아서 돌릴 때마다 같은 그림이 나온다.

필요한 것: 구글 크롬, Pillow, 글꼴 파일. 글꼴은 저장소에 넣지 않는다(둘 다 SIL OFL).
  - Pretendard: ~/.cache/dirty-code-fonts/ (없으면 jsDelivr에서 받는다)
  - IBM Plex Mono: ~/Library/Fonts/
"""
import base64
import math
import pathlib
import random
import subprocess
import sys
import tempfile
import urllib.request

from PIL import Image

HERE = pathlib.Path(__file__).resolve().parent
CACHE = pathlib.Path.home() / ".cache" / "dirty-code-fonts"
USER_FONTS = pathlib.Path.home() / "Library" / "Fonts"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PRETENDARD_URL = (
    "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/"
    "packages/pretendard/dist/public/static/Pretendard-%s.otf"
)
W, H = 1600, 2400
LEFT = 128
BG, INK = "#040405", "#f6f5f1"

FONT_FILES = [
    ("Pretendard", 500, CACHE / "Pretendard-Medium.otf"),
    ("Pretendard", 600, CACHE / "Pretendard-SemiBold.otf"),
    ("Pretendard", 700, CACHE / "Pretendard-Bold.otf"),
    ("Pretendard", 900, CACHE / "Pretendard-Black.otf"),
    ("IBM Plex Mono", 600, USER_FONTS / "IBMPlexMono-SemiBold.ttf"),
]

TOP_LINE, SUBTITLE, AUTHOR = "IN THE AGE OF AI", "Writing Code for AI Readers", "Wooyong Lee"
TITLE = [("DIRTY", 770), ("CODE", 1310)]   # 제목의 두 줄: (낱말, 글자 윗변의 y)
STRANDS, HALF = 7, 26                      # 글자 하나를 쓰는 가닥 수, 다발 너비의 절반
CAP, GAP = 310, 86                         # 글자 높이, 글자 사이

# 줄에 흐르는 글자. 일부러 얽히게 쓴 코드다.
SPAGHETTI = [
    "if (flag) { goto retry; } else if (!done && tmp2) { x = y ? z : (w ? q : 0); } ",
    "for (i = 0; i < n; i++) { if (a[i]) { for (j = i; j; j--) { t = a[j]; a[j] = a[j-1]; a[j-1] = t; } } } ",
    "def handle(o, f=None, x=0): return f(o) if f else (o.get('a') or o.get('b') or x) ",
    "while (1) { switch (s) { case 0: s = t ? 3 : 1; break; case 1: goto L7; default: s--; } } ",
    "try: r = do(x) except Exception: pass; r = r or fix(r) or fix2(r, tmp, tmp2, flag3) ",
    "L7: if (--k) goto L2; else { data2 = data; data = old_data; old_data = data2; } ",
    "function p(a,b,c){return a?b?c?1:2:c?3:4:b?5:c?6:7} var q=p(x,y,z)||p(z,y,x); ",
    "result = [f(g(h(v))) for v in vals if v and not skip(v) or force] + extra[::-1] ",
    "#define DO(x) do { if (x) { cnt++; goto again; } } while (0) /* TODO fix later */ ",
    "else: flag = not flag; tmp = tmp2; tmp2 = tmp3; tmp3 = handle(tmp, None, flag) ",
]

# 무지개. 왼쪽 위에서 오른쪽 아래로 흐른다. HOT은 제목 글자에 쓰는 더 밝은 무지개다.
RAINBOW = [(0, "#a855ff"), (16, "#ff3fa4"), (33, "#ff5c3a"), (50, "#ffc02e"), (67, "#4be06a"), (84, "#22d3ee"), (100, "#5b7cff")]
RAINBOW_HOT = [(0, "#d6adff"), (16, "#ff9fd1"), (33, "#ffae9c"), (50, "#ffe29a"), (67, "#a9f5b6"), (84, "#9aefff"), (100, "#b3c2ff")]

STYLE = """
<style>
  text{font-family:'Pretendard','Apple SD Gothic Neo','Noto Sans KR',sans-serif}
  .m text{font-family:'IBM Plex Mono','Menlo',monospace;font-weight:600}
</style>
"""

# 손으로 적은 글자의 뼈대. 한 글자를 한 붓으로 긋는다. (가로 0~1, 세로 0=위 1=아래)
STROKES = {
    "D": (0.78, [(0.10, 1.00), (0.10, 0.66), (0.10, 0.33), (0.10, 0.02), (0.38, 0.00), (0.72, 0.08), (0.94, 0.34),
                 (0.94, 0.66), (0.72, 0.92), (0.38, 1.00), (0.06, 0.98)]),
    "I": (0.20, [(0.50, 0.00), (0.50, 0.25), (0.50, 0.50), (0.50, 0.75), (0.50, 1.00)]),
    "R": (0.78, [(0.10, 1.00), (0.10, 0.66), (0.10, 0.33), (0.10, 0.02), (0.45, 0.00), (0.80, 0.06), (0.92, 0.26),
                 (0.80, 0.46), (0.45, 0.52), (0.14, 0.52), (0.40, 0.56), (0.66, 0.78), (0.95, 1.00)]),
    "T": (0.80, [(0.00, 0.04), (0.33, 0.02), (0.66, 0.02), (1.00, 0.04), (0.86, -0.10), (0.60, -0.06), (0.50, 0.10),
                 (0.50, 0.40), (0.50, 0.70), (0.50, 1.00)]),
    "Y": (0.84, [(0.00, 0.00), (0.25, 0.26), (0.50, 0.52), (0.75, 0.26), (1.00, 0.00), (0.86, 0.30), (0.60, 0.50),
                 (0.50, 0.66), (0.50, 0.83), (0.50, 1.00)]),
    "C": (0.80, [(0.90, 0.27), (0.76, 0.08), (0.52, 0.00), (0.26, 0.08), (0.08, 0.30), (0.04, 0.52), (0.10, 0.74),
                 (0.28, 0.93), (0.54, 1.00), (0.76, 0.92), (0.90, 0.73)]),
    "O": (0.88, [(0.50, 0.00), (0.24, 0.07), (0.07, 0.28), (0.04, 0.52), (0.10, 0.76), (0.28, 0.94), (0.50, 1.00),
                 (0.72, 0.94), (0.90, 0.76), (0.96, 0.50), (0.90, 0.24), (0.74, 0.07), (0.50, 0.00), (0.30, 0.05)]),
    "E": (0.70, [(0.92, 0.03), (0.60, 0.01), (0.30, 0.01), (0.10, 0.03), (0.10, 0.26), (0.10, 0.46), (0.40, 0.49),
                 (0.74, 0.50), (0.42, 0.54), (0.10, 0.56), (0.10, 0.78), (0.10, 0.97), (0.34, 0.99), (0.64, 0.99),
                 (0.94, 0.97)]),
}


def smooth_path(pts):
    """점들을 부드럽게 잇는 닫힌 path (캣멀-롬 곡선을 3차 베지어로)."""
    n = len(pts)
    d = ["M%.1f,%.1f" % pts[0]]
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append("C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return " ".join(d)


def smooth_open(pts):
    """점들을 부드럽게 잇는 열린 path."""
    n = len(pts)
    get = lambda i: pts[max(0, min(n - 1, i))]
    d = ["M%.1f,%.1f" % pts[0]]
    for i in range(n - 1):
        p0, p1, p2, p3 = get(i - 1), get(i), get(i + 1), get(i + 2)
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append("C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1[0], c1[1], c2[0], c2[1], p2[0], p2[1]))
    return " ".join(d)


def loop(rng, cx, cy, radius):
    """가운데를 한 번에서 세 번 감아 도는 닫힌 줄 하나. 꺾이지 않고 흐른다."""
    wind = rng.choice([1, 2, 2, 3])
    knots = {1: 7, 2: 11, 3: 13}[wind]
    phase, squash, tilt = rng.uniform(0, 2 * math.pi), rng.uniform(0.55, 1.0), rng.uniform(0, math.pi)
    pts = []
    for k in range(knots):
        t = phase + 2 * math.pi * wind * k / knots
        r = radius * rng.uniform(0.42, 1.0)
        x, y = r * math.cos(t), r * math.sin(t) * squash
        pts.append((cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)))
    return pts


def tail(rng, p, q, steps):
    """q에서 p 쪽으로 오던 방향을 이어, p에서 멀어지며 휘는 줄의 끝."""
    ang = math.atan2(p[1] - q[1], p[0] - q[0]) + rng.uniform(-0.3, 0.3)
    turn, out, x, y = rng.choice([-1, 1]) * rng.uniform(0.25, 0.55), [], p[0], p[1]
    for _ in range(steps):
        ang += turn + rng.uniform(-0.08, 0.08)
        step = rng.uniform(100, 170)
        x, y = x + step * math.cos(ang), y + step * math.sin(ang)
        out.append((x, y))
    return out


def word_strands(rng, word, top):
    """낱말 하나를 줄로 쓴다. 글자마다 여러 가닥이 뼈대를 따라가고, 양 끝은 얽힘 속으로 풀려 나간다."""
    width = sum(STROKES[ch][0] for ch in word) * CAP + GAP * (len(word) - 1)
    x0, out = (W - width) / 2, []
    for ch in word:
        w, pts = STROKES[ch]
        base = [(x0 + px * w * CAP, top + py * CAP) for px, py in pts]
        x0 += w * CAP + GAP
        for k in range(STRANDS):
            off = HALF * (2 * k / (STRANDS - 1) - 1)
            phase, amp = rng.uniform(0, 6.28), rng.uniform(4, 10)
            line = []
            for i, (x, y) in enumerate(base):
                a, b = base[max(0, i - 1)], base[min(len(base) - 1, i + 1)]
                tx, ty = b[0] - a[0], b[1] - a[1]
                norm = math.hypot(tx, ty) or 1.0
                d = off + amp * math.sin(phase + i * 0.9)
                line.append((x - ty / norm * d, y + tx / norm * d))
            head = tail(rng, line[0], line[1], rng.randint(4, 7))[::-1] if rng.random() < 0.28 else []
            end = tail(rng, line[-1], line[-2], rng.randint(4, 7)) if rng.random() < 0.28 else []
            out.append((head + line + end, rng.choice([15, 16, 17, 18])))
    return out


def background_loops(seed=11):
    """표지 전체를 덮는 줄들. 반환: (점들, 글자 크기)의 목록."""
    rng = random.Random(seed)
    return [(loop(rng, rng.uniform(-80, W + 80), rng.uniform(-80, H + 80), rng.uniform(420, 820)),
             rng.choice([18, 20, 22, 25])) for _ in range(44)]


def gradient(gid, stops):
    return (
        '<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="0" y1="500" x2="%d" y2="1900">' % (gid, W)
        + "".join('<stop offset="%d%%" stop-color="%s"/>' % s for s in stops) + "</linearGradient>"
    )


def code_for(rng, length_px, size):
    """길이 length_px인 줄을 채울 만큼의 코드 글자."""
    need = int(length_px * 1.3 / (size * 0.6)) + 40
    start, code = rng.randrange(len(SPAGHETTI)), ""
    while len(code) < need:
        code += SPAGHETTI[start % len(SPAGHETTI)]
        start += 1
    return code[:need].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def polyline_length(pts, closed):
    n = len(pts)
    return sum(math.hypot(pts[(k + 1) % n][0] - pts[k][0], pts[(k + 1) % n][1] - pts[k][1])
               for k in range(n if closed else n - 1))


def build_svg():
    rng = random.Random(99)
    paths, back_text, back_line, word_text, word_line = [], [], [], [], []
    for i, (pts, size) in enumerate(background_loops()):
        paths.append('<path id="b%d" d="%s"/>' % (i, smooth_path(pts)))
        back_line.append('<use href="#b%d"/>' % i)
        back_text.append('<text font-size="%d"><textPath href="#b%d">%s</textPath></text>' % (
            size, i, code_for(rng, polyline_length(pts, True), size)))
    yarn = [strand for word, top in TITLE for strand in word_strands(rng, word, top)]
    for i, (pts, size) in enumerate(yarn):
        paths.append('<path id="w%d" d="%s"/>' % (i, smooth_open(pts)))
        word_line.append('<use href="#w%d"/>' % i)
        word_text.append('<text font-size="%d"><textPath href="#w%d">%s</textPath></text>' % (
            size, i, code_for(rng, polyline_length(pts, False), size)))
    defs = (
        "<defs>" + "".join(paths) + gradient("rb", RAINBOW) + gradient("hot", RAINBOW_HOT)
        + '<filter id="glow" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="12"/></filter>'
        + '<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0.9"/>'
        + '<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
        + '<linearGradient id="bot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
        + '<stop offset="0.55" stop-color="#000" stop-opacity="0.88"/><stop offset="1" stop-color="#000" stop-opacity="0.96"/></linearGradient>'
        + "</defs>"
    )
    body = (
        '<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG)
        # 표지 전체의 얽힘
        + '<g fill="none" stroke="url(#rb)" stroke-width="1.3" opacity="0.30">' + "".join(back_line) + "</g>"
        + '<g class="m" fill="url(#rb)" opacity="0.34">' + "".join(back_text) + "</g>"
        # 그 줄이 제목을 쓴다
        + '<g fill="none" stroke="url(#rb)" stroke-width="9" opacity="0.55" filter="url(#glow)">' + "".join(word_line) + "</g>"
        + '<g fill="none" stroke="url(#rb)" stroke-width="2.2" opacity="0.9">' + "".join(word_line) + "</g>"
        + '<g class="m" fill="url(#hot)">' + "".join(word_text) + "</g>"
        # 작은 글자가 읽히도록 위아래를 어둡게 누른다
        + '<rect width="%d" height="360" fill="url(#top)"/>' % W
        + '<rect y="1900" width="%d" height="500" fill="url(#bot)"/>' % W
        + '<text x="%d" y="196" font-size="46" font-weight="600" letter-spacing="1" fill="%s">%s</text>' % (LEFT, INK, TOP_LINE)
        + '<text x="%d" y="2148" font-size="52" font-weight="500" fill="%s">%s</text>' % (LEFT, INK, SUBTITLE)
        + '<text x="%d" y="2262" font-size="54" font-weight="700" letter-spacing="4" fill="%s">%s</text>' % (LEFT, INK, AUTHOR)
    )
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">' % (W, H, W, H)
    return head + STYLE + defs + body + "</svg>\n"


def ensure_fonts():
    CACHE.mkdir(parents=True, exist_ok=True)
    for _name, _weight, path in FONT_FILES:
        if path.exists():
            continue
        if path.parent == CACHE and path.name.startswith("Pretendard-"):
            style = path.stem.split("-", 1)[1]
            print("글꼴 받는 중:", path.name)
            urllib.request.urlretrieve(PRETENDARD_URL % style, path)
        else:
            sys.exit("글꼴 파일이 없습니다: %s" % path)


def font_css():
    rules = []
    for name, weight, path in FONT_FILES:
        fmt = "opentype" if path.suffix == ".otf" else "truetype"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        rules.append(
            "@font-face{font-family:'%s';font-weight:%d;"
            "src:url(data:font/%s;base64,%s) format('%s')}"
            % (name, weight, path.suffix[1:], data, fmt)
        )
    return "\n".join(rules)


def render_svg(svg_text, png_path, css):
    """SVG 글을 크롬으로 찍어 PNG로 저장한다."""
    html = (
        "<!doctype html><meta charset='utf-8'><style>%s\n"
        "html,body{margin:0;background:#000}svg{display:block}</style>%s" % (css, svg_text)
    )
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        page = tmp / "cover.html"
        page.write_text(html, encoding="utf-8")
        shot = tmp / "shot.png"
        cmd = [
            CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check",
            "--user-data-dir=%s" % (tmp / "profile"),
            "--force-device-scale-factor=1",
            "--window-size=%d,%d" % (W, H + 120),
            "--virtual-time-budget=15000",
            "--screenshot=%s" % shot,
            page.as_uri(),
        ]
        subprocess.run(cmd, check=True, timeout=300, capture_output=True)
        img = Image.open(shot).convert("RGB")
        if img.width < W or img.height < H:
            sys.exit("찍힌 그림이 작습니다: %dx%d" % img.size)
        img.crop((0, 0, W, H)).save(png_path, optimize=True)
    return "%s: %d KB" % (png_path.name, png_path.stat().st_size // 1024)


def main():
    ensure_fonts()
    svg_text = build_svg()
    if "svg" in sys.argv[1:]:
        (HERE / "cover.svg").write_text(svg_text, encoding="utf-8")
        print("cover.svg")
    print(render_svg(svg_text, HERE / "cover.png", font_css()))
    web = HERE / "cover-web.jpg"
    Image.open(HERE / "cover.png").resize((1200, 1800), Image.LANCZOS).save(web, quality=88, subsampling=0, optimize=True)
    print("%s: %d KB" % (web.name, web.stat().st_size // 1024))


if __name__ == "__main__":
    main()
