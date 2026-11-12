#!/usr/bin/env python3
"""가로 배너를 만든다. GitHub 프로필 대문에 싣는 그림이다.

그림은 표지(build_cover.py)와 같은 부품으로 그린다. 무지개색으로 얽힌 코드 줄이 배너를 덮고,
그 줄 가닥이 손으로 적은 획의 뼈대(STROKES)를 따라 제목을 쓴다. 바꾼 것은 캔버스(가로 1680×700)와 배치뿐이다.
제목은 한 줄(DIRTY CODE), 왼쪽 위에 IN THE AGE OF AI, 왼쪽 아래에 부제, 오른쪽 아래에 저자 이름.

  /usr/bin/python3 assets/build_banner.py
      → assets/banner.png (1680×700), assets/banner-web.jpg (대문에 싣는 가벼운 JPEG, 같은 크기)
  /usr/bin/python3 assets/build_banner.py svg
      → assets/banner.svg 도 함께 쓴다 (글꼴을 품지 않으므로 글꼴이 깔린 곳에서만 제대로 보인다)

난수의 씨앗을 못 박아서 돌릴 때마다 같은 그림이 나온다. 필요한 것(크롬, Pillow, 글꼴)은 build_cover.py와 같다.
"""
import math
import pathlib
import random
import subprocess
import sys
import tempfile

from PIL import Image, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
import build_cover as cover  # noqa: E402

W, H = 1680, 700
CAP = 172                         # 제목 글자 높이 (표지는 310)
TITLE_TOP = 226                   # 제목 글자 윗변의 y
WORD_GAP = CAP * 0.60             # DIRTY와 CODE 사이
TOP_BAND, BOTTOM_BAND = 175, 520  # 작은 글자가 읽히도록 어둡게 누르는 위 띠의 높이, 아래 띠가 시작하는 y
# (글, x, 기준선 y, 글자 크기, 굵기, 정렬, 자간)
COPY = [
    (cover.TOP_LINE, 80, 94, 52, 600, "start", 1),
    (cover.SUBTITLE, 80, 646, 52, 600, "start", 0),
    (cover.AUTHOR, W - 80, 646, 54, 700, "end", 2),
]


def word_width(word):
    return sum(cover.STROKES[ch][0] for ch in word) * CAP + cover.GAP * CAP / cover.CAP * (len(word) - 1)


def title_words():
    """제목 한 줄: (낱말, 왼쪽 x)의 목록. 가운데에 놓는다."""
    start = (W - word_width("DIRTY") - WORD_GAP - word_width("CODE")) / 2
    return [("DIRTY", start), ("CODE", start + word_width("DIRTY") + WORD_GAP)]


def background_loops(seed=11):
    """배너 전체에 고르게 흩뿌린 코드 고리. 반환: (점들, 글자 크기)의 목록."""
    rng = random.Random(seed)
    scale = math.sqrt(W * H / (cover.W * cover.H))
    out = []
    for row in range(3):
        for col in range(6):
            for _ in range(2):
                cx = (col + rng.uniform(-0.10, 1.10)) * W / 6
                cy = (row + rng.uniform(-0.20, 1.20)) * H / 3
                radius = rng.uniform(420, 820) * scale
                size = rng.choice([18, 20, 22, 25]) * scale
                out.append((cover.loop(rng, cx, cy, radius), size))
    return out


def word_strands(rng, word, left):
    """표지의 word_strands와 같은 가닥을 표지 좌표에서 만든 뒤, 제목 자리로 옮기고 줄인다."""
    scale = CAP / cover.CAP
    x0, out = 0, []
    for ch in word:
        w, pts = cover.STROKES[ch]
        base = [(x0 + px * w * cover.CAP, py * cover.CAP) for px, py in pts]
        x0 += w * cover.CAP + cover.GAP
        for k in range(cover.STRANDS):
            off = cover.HALF * (2 * k / (cover.STRANDS - 1) - 1)
            phase, amp = rng.uniform(0, 6.28), rng.uniform(4, 10)
            line = []
            for i, (x, y) in enumerate(base):
                a, b = base[max(0, i - 1)], base[min(len(base) - 1, i + 1)]
                tx, ty = b[0] - a[0], b[1] - a[1]
                norm = math.hypot(tx, ty) or 1.0
                d = off + amp * math.sin(phase + i * 0.9)
                line.append((x - ty / norm * d, y + tx / norm * d))
            head = cover.tail(rng, line[0], line[1], rng.randint(4, 7))[::-1] if rng.random() < 0.28 else []
            end = cover.tail(rng, line[-1], line[-2], rng.randint(4, 7)) if rng.random() < 0.28 else []
            out.append(([(left + x * scale, TITLE_TOP + y * scale) for x, y in head + line + end],
                        rng.choice([15, 16, 17, 18]) * scale))
    return out


def gradient(gid, stops):
    return ('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="0" y1="%.1f" x2="%d" y2="%.1f">'
            % (gid, H * .16, W, H * .90)
            + "".join('<stop offset="%d%%" stop-color="%s"/>' % s for s in stops) + "</linearGradient>")


def build_svg():
    rng = random.Random(99)
    paths, back_text, back_line, word_text, word_line = [], [], [], [], []
    for i, (pts, size) in enumerate(background_loops()):
        paths.append('<path id="b%d" d="%s"/>' % (i, cover.smooth_path(pts)))
        back_line.append('<use href="#b%d"/>' % i)
        back_text.append('<text font-size="%.2f"><textPath href="#b%d">%s</textPath></text>' % (
            size, i, cover.code_for(rng, cover.polyline_length(pts, True), size)))
    yarn = [strand for word, left in title_words() for strand in word_strands(rng, word, left)]
    for i, (pts, size) in enumerate(yarn):
        paths.append('<path id="w%d" d="%s"/>' % (i, cover.smooth_open(pts)))
        word_line.append('<use href="#w%d"/>' % i)
        word_text.append('<text font-size="%.2f"><textPath href="#w%d">%s</textPath></text>' % (
            size, i, cover.code_for(rng, cover.polyline_length(pts, False), size)))
    scale = CAP / cover.CAP
    defs = (
        "<defs>" + "".join(paths) + gradient("rb", cover.RAINBOW) + gradient("hot", cover.RAINBOW_HOT)
        + '<filter id="glow" x="-5%%" y="-5%%" width="110%%" height="110%%"><feGaussianBlur stdDeviation="%.2f"/></filter>'
        % (12 * scale)
        + '<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0.9"/>'
        + '<stop offset="1" stop-color="#000" stop-opacity="0"/></linearGradient>'
        + '<linearGradient id="bot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
        + '<stop offset="0.55" stop-color="#000" stop-opacity="0.88"/><stop offset="1" stop-color="#000" stop-opacity="0.96"/>'
        + "</linearGradient></defs>"
    )
    body = (
        '<rect width="%d" height="%d" fill="%s"/>' % (W, H, cover.BG)
        # 배너 전체의 얽힘
        + '<g fill="none" stroke="url(#rb)" stroke-width="%.2f" opacity="0.30">' % (1.3 * scale) + "".join(back_line) + "</g>"
        + '<g class="m" fill="url(#rb)" opacity="0.34">' + "".join(back_text) + "</g>"
        # 그 줄이 제목을 쓴다
        + '<g fill="none" stroke="url(#rb)" stroke-width="%.2f" opacity="0.55" filter="url(#glow)">' % (9 * scale)
        + "".join(word_line) + "</g>"
        + '<g fill="none" stroke="url(#rb)" stroke-width="%.2f" opacity="0.9">' % (2.2 * scale) + "".join(word_line) + "</g>"
        + '<g class="m" fill="url(#hot)">' + "".join(word_text) + "</g>"
        # 작은 글자가 읽히도록 위아래를 어둡게 누른다
        + '<rect width="%d" height="%d" fill="url(#top)"/>' % (W, TOP_BAND)
        + '<rect y="%d" width="%d" height="%d" fill="url(#bot)"/>' % (BOTTOM_BAND, W, H - BOTTOM_BAND)
        + "".join('<text x="%d" y="%d" font-size="%d" font-weight="%d" text-anchor="%s" letter-spacing="%g" fill="%s">%s</text>'
                  % (x, y, size, weight, anchor, spacing, cover.INK, text)
                  for text, x, y, size, weight, anchor, spacing in COPY)
    )
    head = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" '
            'aria-label="Dirty Code. %s. %s. %s.">' % (W, H, W, H, cover.TOP_LINE, cover.SUBTITLE, cover.AUTHOR))
    return head + cover.STYLE + defs + body + "</svg>\n"


def check_copy():
    """문구가 배너 안에 들고, 폭 700px로 줄여도 글자 높이가 14px 이상인지 확인한다."""
    for text, x, y, size, weight, anchor, spacing in COPY:
        path = next(p for name, wt, p in cover.FONT_FILES if name == "Pretendard" and wt == weight)
        font = ImageFont.truetype(str(path), size)
        _, top, _, bottom = font.getbbox(text, anchor="ls")
        length = font.getlength(text) + spacing * (len(text) - 1)
        left = x - {"start": 0, "middle": length / 2, "end": length}[anchor]
        if (bottom - top) * 700 / W < 14 or left < 24 or left + length > W - 24 or y + top < 20 or y + bottom > H - 12:
            sys.exit("문구 자리가 맞지 않습니다: %s" % text)


def render_svg(svg_text, png_path, css):
    """SVG 글을 크롬으로 찍어 PNG로 저장한다(build_cover.render_svg와 같고 크기만 다르다)."""
    html = ("<!doctype html><meta charset='utf-8'><style>%s\n"
            "html,body{margin:0;background:#000}svg{display:block}</style>%s" % (css, svg_text))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        page, shot = tmp / "banner.html", tmp / "shot.png"
        page.write_text(html, encoding="utf-8")
        subprocess.run([
            cover.CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
            "--no-first-run", "--no-default-browser-check", "--user-data-dir=%s" % (tmp / "profile"),
            "--force-device-scale-factor=1", "--window-size=%d,%d" % (W, H + 120),
            "--virtual-time-budget=15000", "--screenshot=%s" % shot, page.as_uri(),
        ], check=True, timeout=300, capture_output=True)
        img = Image.open(shot).convert("RGB")
        if img.width < W or img.height < H:
            sys.exit("찍힌 그림이 작습니다: %dx%d" % img.size)
        img.crop((0, 0, W, H)).save(png_path, optimize=True)
    return "%s: %d KB" % (png_path.name, png_path.stat().st_size // 1024)


def main():
    cover.ensure_fonts()
    check_copy()
    svg_text = build_svg()
    if "svg" in sys.argv[1:]:
        (HERE / "banner.svg").write_text(svg_text, encoding="utf-8")
        print("banner.svg")
    print(render_svg(svg_text, HERE / "banner.png", cover.font_css()))
    web = HERE / "banner-web.jpg"
    Image.open(HERE / "banner.png").save(web, quality=86, subsampling=0, optimize=True)
    print("%s: %d KB" % (web.name, web.stat().st_size // 1024))


if __name__ == "__main__":
    main()
