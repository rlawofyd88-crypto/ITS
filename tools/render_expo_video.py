#!/usr/bin/env python3
"""Render a COEX-ready Brycen Korea promo video about Android ITS."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageFont


WIDTH = 1920
HEIGHT = 1080
BG = "#07110f"
PANEL = "#0e1a17"
PANEL_2 = "#12231d"
INK = "#f4f0e8"
MUTED = "#aab4ae"
GREEN = "#61d394"
GREEN_2 = "#88e3b0"
AMBER = "#ffcc66"
RED = "#ff6b57"
CYAN = "#79d7ff"
DARK_INK = "#08110d"

FONT_REGULAR = [
    Path("C:/Windows/Fonts/malgun.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
]
FONT_BOLD = [
    Path("C:/Windows/Fonts/malgunbd.ttf"),
    Path("C:/Windows/Fonts/segoeuib.ttf"),
]


@dataclass
class Slide:
    title: str
    duration: int
    subtitle: str


SLIDES = [
    Slide("Android ITS, Camera Quality You Can Prove", 8, "브라이센코리아 Android 카메라 검증 홍보 영상"),
    Slide("ITS란 무엇인가", 8, "ITS는 카메라를 눈대중이 아니라 표준화된 장면과 절차로 확인합니다"),
    Slide("왜 ITS가 필요한가", 8, "카메라 품질은 감각이 아니라 반복 가능한 검증이 필요합니다"),
    Slide("무엇을 검증하는가", 10, "브라이센코리아는 Camera ITS가 실제 현장에서 작동하도록 연결합니다"),
    Slide("브라이센코리아는 실행만이 아니라 결과 해석까지 연결합니다.", 10, "환경 구축부터 자동화, 분석, 설명형 산출물까지"),
    Slide("From Demo To Deployment", 8, "ITS 환경 구축부터 설명 가능한 시연물까지"),
]

header_canvas: Image.Image | None = None


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = FONT_BOLD if bold else FONT_REGULAR + FONT_BOLD
    for path in candidates:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    return right - left, bottom - top


def split_long_token(draw: ImageDraw.ImageDraw, token: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    parts: list[str] = []
    current = ""
    for char in token:
        candidate = current + char
        if text_size(draw, candidate, font)[0] <= max_width or not current:
            current = candidate
        else:
            parts.append(current)
            current = char
    if current:
        parts.append(current)
    return parts


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    tokens = re.findall(r"\S+|\s+", text)
    lines: list[str] = []
    current = ""
    for token in tokens:
        if token.isspace():
            candidate = current + token
            if text_size(draw, candidate, font)[0] <= max_width:
                current = candidate
            continue
        pieces = [token] if text_size(draw, token, font)[0] <= max_width else split_long_token(draw, token, font, max_width)
        for piece in pieces:
            candidate = current + piece
            if text_size(draw, candidate, font)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current.rstrip())
                current = piece
    if current.strip():
        lines.append(current.rstrip())
    return lines


def fit_wrapped_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    bold: bool,
    line_gap: int,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        lines = wrap_text(draw, text, font, max_width)
        line_height = text_size(draw, "Ag", font)[1]
        total_height = len(lines) * line_height + max(0, len(lines) - 1) * line_gap
        if total_height <= max_height:
            return font, lines, line_height
    font = load_font(min_size, bold=bold)
    lines = wrap_text(draw, text, font, max_width)
    return font, lines, text_size(draw, "Ag", font)[1]


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    fill: str,
    start_size: int,
    min_size: int = 18,
    bold: bool = False,
    line_gap: int = 10,
    align: str = "left",
) -> int:
    x1, y1, x2, y2 = box
    font, lines, line_height = fit_wrapped_font(draw, text, x2 - x1, y2 - y1, start_size, min_size, bold, line_gap)
    y = y1
    for line in lines:
        width, _ = text_size(draw, line, font)
        if align == "center":
            x = x1 + ((x2 - x1 - width) / 2)
        elif align == "right":
            x = x2 - width
        else:
            x = x1
        draw.text((x, y), line, fill=fill, font=font)
        y += line_height + line_gap
    return y


def draw_fit_single_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    start_size: int,
    min_size: int,
    fill: str,
    bold: bool = True,
) -> tuple[int, int]:
    for size in range(start_size, min_size - 1, -2):
        font = load_font(size, bold=bold)
        width, height = text_size(draw, text, font)
        if width <= max_width:
            draw.text((x, y), text, fill=fill, font=font)
            return width, height
    font = load_font(min_size, bold=bold)
    draw.text((x, y), text, fill=fill, font=font)
    return text_size(draw, text, font)


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))


def create_background() -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), BG)
    px = canvas.load()
    c1 = hex_to_rgb("#07110f")
    c2 = hex_to_rgb("#14110c")
    for y in range(HEIGHT):
        mix = y / max(1, HEIGHT - 1)
        for x in range(WIDTH):
            mix2 = (x / WIDTH) * 0.35
            r = int(c1[0] * (1 - mix) + c2[0] * mix2 + 8 * mix)
            g = int(c1[1] * (1 - mix) + c2[1] * mix + 4 * mix2)
            b = int(c1[2] * (1 - mix2) + c2[2] * mix2)
            px[x, y] = (r, g, b)

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, WIDTH, 48):
        od.line((x, 0, x, HEIGHT), fill=(255, 255, 255, 12), width=1)
    for y in range(0, HEIGHT, 48):
        od.line((0, y, WIDTH, y), fill=(255, 255, 255, 10), width=1)
    od.ellipse((70, 40, 620, 520), fill=(97, 211, 148, 30))
    od.ellipse((1360, 30, 1900, 460), fill=(255, 204, 102, 24))
    overlay = overlay.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")


def draw_header(draw: ImageDraw.ImageDraw, logo: Image.Image | None, title: str, subtitle: str) -> None:
    global header_canvas
    eyebrow_font = load_font(24, bold=True)

    if logo and header_canvas is not None:
        logo_box = Image.new("RGBA", (280, 110), (10, 18, 16, 220))
        logo_draw = ImageDraw.Draw(logo_box)
        logo_draw.rounded_rectangle((0, 0, 279, 109), radius=22, outline=(97, 211, 148, 90), width=2)
        logo_draw.rounded_rectangle((18, 24, 262, 86), radius=16, fill=(245, 242, 233, 235))
        logo_copy = logo.copy()
        logo_copy.thumbnail((232, 74))
        logo_box.paste(logo_copy, ((280 - logo_copy.width) // 2, (110 - logo_copy.height) // 2), logo_copy if logo_copy.mode == "RGBA" else None)
        header_canvas.paste(logo_box, (72, 58), logo_box)
        text_x = 384
    else:
        text_x = 90

    draw.text((text_x, 62), "COEX LIVE DEMO", fill=AMBER, font=eyebrow_font)
    title_w = WIDTH - text_x - 96
    _, title_h = draw_fit_single_line(draw, title, text_x, 98, title_w, 68, 42, INK, bold=True)
    draw_wrapped(draw, subtitle, (text_x, 112 + title_h, text_x + title_w, 252), MUTED, 30, min_size=22, bold=False, line_gap=6)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, accent: str = GREEN) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=24, fill=PANEL, outline=(255, 255, 255, 24), width=2)
    draw.rounded_rectangle((x1, y1, x2, y1 + 54), radius=24, fill=PANEL_2)
    draw.rectangle((x1, y1 + 32, x2, y1 + 54), fill=PANEL_2)
    draw.text((x1 + 24, y1 + 12), title, fill=accent, font=load_font(24, bold=True))


def fit_cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = image.size
    src_ratio = src_w / src_h
    target_ratio = target_w / target_h
    if src_ratio > target_ratio:
        crop_w = int(src_h * target_ratio)
        left = (src_w - crop_w) // 2
        image = image.crop((left, 0, left + crop_w, src_h))
    else:
        crop_h = int(src_w / target_ratio)
        top = (src_h - crop_h) // 2
        image = image.crop((0, top, src_w, top + crop_h))
    return image.resize(size)


def paste_card(base: Image.Image, image_path: Path, box: tuple[int, int, int, int], outline: str = GREEN) -> None:
    if not image_path.exists():
        return
    x1, y1, x2, y2 = box
    img = Image.open(image_path).convert("RGB")
    fitted = fit_cover(img, (x2 - x1 - 20, y2 - y1 - 20))
    base.paste(fitted, (x1 + 10, y1 + 10))
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle(box, radius=18, outline=outline, width=3)


def load_metrics(status_path: Path) -> dict:
    if not status_path.exists():
        return {
            "status": "RUN",
            "metrics": {"overallScore": 94},
            "counts": {"pass": 318, "fail": 9},
        }
    return json.loads(status_path.read_text(encoding="utf-8"))


def pill(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill: str, ink: str = DARK_INK) -> None:
    draw.rounded_rectangle(box, radius=18, fill=fill)
    x1, y1, x2, y2 = box
    max_w = x2 - x1 - 20
    font = load_font(24, bold=True)
    tw, th = text_size(draw, text, font)
    for size in range(24, 15, -1):
        font = load_font(size, bold=True)
        tw, th = text_size(draw, text, font)
        if tw <= max_w:
            break
    draw.text((x1 + ((x2 - x1 - tw) / 2), y1 + ((y2 - y1 - th) / 2) - 2), text, fill=ink, font=font)


def service_row(draw: ImageDraw.ImageDraw, y: int, title: str, desc: str, color: str, right_x: int) -> None:
    draw.rounded_rectangle((138, y, 972, y + 104), radius=22, fill="#182420")
    pill(draw, (166, y + 24, 382, y + 74), title, color)
    draw_wrapped(draw, desc, (428, y + 24, right_x, y + 82), INK, 24, min_size=18, bold=False, line_gap=6)


def help_row(draw: ImageDraw.ImageDraw, y: int, title: str, desc: str) -> None:
    draw.rounded_rectangle((148, y, 1772, y + 98), radius=22, fill="#182420")
    pill(draw, (176, y + 24, 450, y + 72), title, AMBER)
    draw_wrapped(draw, desc, (498, y + 24, 1718, y + 74), INK, 24, min_size=18, bold=False, line_gap=6)


def info_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, desc: str, color: str, badge: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=26, fill=PANEL, outline=color, width=4)
    pill(draw, (x2 - 194, y1 + 28, x2 - 34, y1 + 84), badge, color)
    title_bottom = draw_wrapped(draw, title, (x1 + 34, y1 + 34, x2 - 230, y1 + 98), INK, 34, min_size=24, bold=True, line_gap=6)
    draw_wrapped(draw, desc, (x1 + 34, title_bottom + 12, x2 - 40, y2 - 30), MUTED, 26, min_size=20, bold=False, line_gap=8)


def flow_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, desc: str, color: str) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=28, fill=PANEL, outline=color, width=4)
    title_bottom = draw_wrapped(draw, title, (x1 + 30, y1 + 30, x2 - 30, y1 + 90), INK, 34, min_size=26, bold=True, line_gap=4)
    draw_wrapped(draw, desc, (x1 + 30, title_bottom + 16, x2 - 30, y2 - 34), MUTED, 24, min_size=18, bold=False, line_gap=6)


def arrow_label(draw: ImageDraw.ImageDraw, center: tuple[int, int], text: str) -> None:
    cx, cy = center
    box = (cx - 92, cy - 24, cx + 92, cy + 24)
    draw.rounded_rectangle(box, radius=12, fill="#1a241f")
    draw_wrapped(draw, text, (box[0] + 12, box[1] + 10, box[2] - 12, box[3] - 8), INK, 18, min_size=14, bold=True, line_gap=2, align="center")


def slide_1(base: Image.Image, logo: Image.Image | None) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[0].title, "보이는 느낌이 아닌, 기준과 데이터로 카메라 품질을 증명합니다")

    panel(draw, (86, 286, 1038, 882), "ANDROID CAMERA VALIDATION")
    panel(draw, (1082, 286, 1834, 570), "ITS MESSAGE", AMBER)
    panel(draw, (1082, 602, 1834, 882), "BRYCEN KOREA", CYAN)

    draw.text((132, 366), "반복 가능한 카메라 품질 검증", fill=INK, font=load_font(48, bold=True))
    bullets = [
        "동일 조건에서 scene 기반 자동 테스트 수행",
        "정량 지표로 카메라 동작을 객관적으로 검증",
        "인증 대응과 개발 효율을 함께 고려한 접근",
    ]
    y = 460
    for bullet in bullets:
        draw.rounded_rectangle((134, y + 14, 150, y + 30), radius=6, fill=GREEN)
        draw_wrapped(draw, bullet, (174, y, 960, y + 44), MUTED, 28, min_size=22, bold=False, line_gap=4)
        y += 82

    draw_wrapped(draw, "ITS는 이미지 튜닝 도구가 아닙니다.", (1118, 346, 1776, 392), INK, 28, min_size=22, bold=True, line_gap=4)
    draw_wrapped(draw, "카메라가 기준에 맞게 동작하는지 검증하는 자동 테스트 체계입니다.", (1118, 404, 1776, 520), MUTED, 26, min_size=20, bold=False, line_gap=6)

    cards = [
        ("검증 관점", "카메라 품질을 '느낌'이 아닌 기준으로 설명"),
        ("인증 대응", "Camera ITS 환경 bring-up 및 실행 흐름 구성"),
        ("브라이센코리아", "환경 구축, 자동화, 분석까지 연결"),
    ]
    cy = 656
    for title, desc in cards:
        draw.rounded_rectangle((1118, cy, 1794, cy + 58), radius=16, fill="#182420")
        draw_wrapped(draw, title, (1146, cy + 10, 1320, cy + 46), INK, 24, min_size=18, bold=True, line_gap=2)
        draw_wrapped(draw, desc, (1352, cy + 10, 1766, cy + 46), MUTED, 20, min_size=16, bold=False, line_gap=2)
        cy += 72
    return base


def slide_2(base: Image.Image, logo: Image.Image | None) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[1].title, SLIDES[1].subtitle)

    positions = {
        "Standard Scene": (140, 350, 580, 600),
        "Camera Capture": (740, 280, 1180, 530),
        "Measured Result": (1340, 350, 1780, 600),
        "Repeatability": (640, 680, 1280, 870),
    }
    descriptions = {
        "Standard Scene": "기준 chart와 장면을 사용해 동일 조건을 구성합니다",
        "Camera Capture": "검증 대상 단말의 카메라 동작을 실행합니다",
        "Measured Result": "색, 초점, 노출, 메타데이터를 정량 분석합니다",
        "Repeatability": "반복 가능한 조건으로 개발과 인증 판단의 일관성을 확보합니다",
    }
    colors = {
        "Standard Scene": AMBER,
        "Camera Capture": GREEN,
        "Measured Result": CYAN,
        "Repeatability": GREEN_2,
    }
    for label, box in positions.items():
        flow_box(draw, box, label, descriptions[label], colors[label])

    draw.line((580, 474, 740, 404), fill=AMBER, width=6)
    draw.ellipse((728, 392, 752, 416), fill=AMBER)
    arrow_label(draw, (654, 418), "기준 장면")

    draw.line((1180, 404, 1340, 474), fill=AMBER, width=6)
    draw.ellipse((1328, 462, 1352, 486), fill=AMBER)
    arrow_label(draw, (1260, 418), "결과 분석")

    draw.line((960, 530, 960, 680), fill=AMBER, width=6)
    draw.ellipse((948, 668, 972, 692), fill=AMBER)
    arrow_label(draw, (960, 590), "반복 검증")

    panel(draw, (126, 906, 1794, 1008), "핵심 의미", AMBER)
    draw_wrapped(draw, "ITS는 '테스트를 돌린다'보다 '동일한 기준으로 검증한다'는 점이 중요합니다.", (162, 942, 1750, 990), INK, 26, min_size=22, bold=True, line_gap=4)
    return base


def slide_3(base: Image.Image, logo: Image.Image | None) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[2].title, "카메라 품질은 좋아 보이는 것만으로는 설명할 수 없습니다")

    cards = [
        ("개발 관점", "기기별 편차와 회귀를 반복 가능한 조건에서 빠르게 확인", GREEN),
        ("인증 관점", "기준 절차에 맞춘 검증 환경으로 대응 준비", AMBER),
        ("품질 관점", "감성 평가가 아닌 수치와 조건 기반으로 판단", CYAN),
        ("운영 관점", "로그, 결과, 실행 흐름을 체계적으로 관리", RED),
    ]
    positions = [
        (100, 340, 910, 560),
        (1010, 340, 1820, 560),
        (100, 610, 910, 830),
        (1010, 610, 1820, 830),
    ]
    for (title, desc, color), box in zip(cards, positions):
        info_box(draw, box, title, desc, color, "WHY")

    draw_wrapped(draw, "핵심 메시지: ITS는 '왜 해야 하는가'에 대해, 반복성·객관성·인증 대응이라는 답을 줍니다.", (120, 902, 1820, 958), INK, 26, min_size=22, bold=True, line_gap=4)
    return base


def slide_4(base: Image.Image, logo: Image.Image | None, demo_frame: Path) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[3].title, SLIDES[3].subtitle)

    panel(draw, (82, 298, 1148, 914), "WHAT ITS CHECKS")
    panel(draw, (1184, 298, 1838, 914), "REFERENCE VISUAL", AMBER)

    steps = [
        ("01", "Color Accuracy", "기준 chart 대비 색 재현과 일관성 확인"),
        ("02", "Focus / Sharpness", "초점 동작과 세부 해상력 검증"),
        ("03", "Exposure / Dynamic Range", "밝기와 대비, 장면 대응 특성 확인"),
        ("04", "Metadata", "3A 및 프레임워크 메타데이터 일관성 확인"),
        ("05", "Stability", "반복 실행 시 재현성과 회귀 여부 확인"),
    ]
    y = 370
    for idx, title, desc in steps:
        draw.rounded_rectangle((128, y, 1098, y + 88), radius=18, fill="#182420")
        pill(draw, (150, y + 18, 224, y + 70), idx, AMBER)
        draw_wrapped(draw, title, (256, y + 18, 630, y + 48), INK, 26, min_size=20, bold=True, line_gap=2)
        draw_wrapped(draw, desc, (256, y + 48, 1060, y + 76), MUTED, 20, min_size=16, bold=False, line_gap=2)
        y += 102

    paste_card(base, demo_frame, (1220, 360, 1800, 840), outline=GREEN)
    draw_wrapped(draw, "실제 장면과 기준 시각 자료를 함께 사용하는 설명형 화면", (1242, 858, 1790, 902), MUTED, 22, min_size=18, bold=False, line_gap=4)
    return base


def slide_5(base: Image.Image, logo: Image.Image | None, metrics: dict, dashboard: Path) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[4].title, "환경 구축부터 자동화, 분석, 설명형 산출물까지")

    panel(draw, (84, 294, 1026, 924), "SERVICE SCOPE")
    panel(draw, (1060, 294, 1838, 924), "DELIVERABLE EXAMPLE", CYAN)

    score = float(metrics.get("metrics", {}).get("overallScore", 93))
    counts = metrics.get("counts", {})
    services = [
        ("환경 구축", "DUT / Tablet / Host / ITS Box bring-up"),
        ("테스트 자동화", "scene 실행, 결과 수집, 로그 정리"),
        ("결과 분석", "PASS/FAIL 요약, 메트릭 해석, 이슈 추적"),
        ("대외 시연", "대시보드, 영상, 브로셔 형태로 전달력 강화"),
    ]
    y = 390
    for title, desc in services:
        service_row(draw, y, title, desc, GREEN, 930)
        y += 120

    draw.rounded_rectangle((138, 860, 972, 908), radius=14, fill="#182420")
    draw_wrapped(draw, f"Sample score {round(score)}  ·  Pass {counts.get('pass', 0)}  /  Fail {counts.get('fail', 0)}", (170, 870, 930, 900), MUTED, 22, min_size=18, bold=True, line_gap=2)

    paste_card(base, dashboard, (1090, 362, 1808, 850), outline=CYAN)
    draw_wrapped(draw, "예시 산출물: 결과 대시보드, 대표 장면, 설명형 콘텐츠로 확장 가능", (1118, 866, 1790, 906), MUTED, 22, min_size=18, bold=False, line_gap=4)
    return base


def slide_6(base: Image.Image, logo: Image.Image | None) -> Image.Image:
    global header_canvas
    header_canvas = base
    draw = ImageDraw.Draw(base)
    draw_header(draw, logo, SLIDES[5].title, SLIDES[5].subtitle)

    panel(draw, (98, 304, 1820, 860), "BRYCEN KOREA CAN HELP", GREEN)
    items = [
        ("ITS 환경 구축", "Android 기반 검증 환경 bring-up 및 실행 준비"),
        ("자동화/분석", "실행 흐름 정리, 결과 수집, 해석 지원"),
        ("인증 대응 준비", "Camera ITS 관점의 검증 체계 구성"),
        ("홍보/시연 콘텐츠", "영상, 보드, 브로셔로 고객 전달력 강화"),
    ]
    y = 392
    for title, desc in items:
        help_row(draw, y, title, desc)
        y += 116

    draw_wrapped(draw, "Brycen Korea · Android Camera ITS Enablement & Showcase", (148, 898, 1750, 944), MUTED, 28, min_size=22, bold=True, line_gap=4)
    return base


def write_srt(target: Path) -> None:
    captions = [
        (1, "00:00:00,000", "00:00:08,000", "Android ITS, Camera Quality You Can Prove\n브라이센코리아 Android 카메라 검증 홍보 영상"),
        (2, "00:00:08,000", "00:00:16,000", "ITS는 카메라가 기준에 맞게 동작하는지 자동으로 검증하는 체계입니다."),
        (3, "00:00:16,000", "00:00:24,000", "카메라 품질은 감각이 아니라 반복 가능한 검증과 정량 기준이 필요합니다."),
        (4, "00:00:24,000", "00:00:34,000", "색, 초점, 노출, 메타데이터, 안정성까지 Camera ITS 관점으로 확인합니다."),
        (5, "00:00:34,000", "00:00:44,000", "브라이센코리아는 환경 구축, 자동화, 분석, 설명형 산출물까지 연결합니다."),
        (6, "00:00:44,000", "00:00:52,000", "Brycen Korea와 함께 ITS 검증 체계를 시작하세요."),
    ]
    lines = []
    for idx, start, end, text in captions:
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")


def write_narration(target: Path) -> None:
    text = """# COEX Android ITS Box Promo Narration

1. Android ITS는 카메라 품질을 기준과 데이터로 증명하기 위한 검증 체계입니다.
2. ITS는 이미지를 예쁘게 만드는 도구가 아니라, 카메라가 기준에 맞게 동작하는지 자동으로 확인하는 절차입니다.
3. 카메라 품질은 좋아 보인다는 느낌만으로 판단할 수 없습니다. 반복 가능한 장면과 정량 기준이 필요합니다.
4. Color, Focus, Exposure, Metadata, Stability와 같은 항목을 통해 개발과 인증 대응에 필요한 근거를 확보할 수 있습니다.
5. Brycen Korea는 ITS 환경 구축, 자동화, 결과 분석, 그리고 고객이 이해하기 쉬운 시연 콘텐츠 제작까지 지원합니다.
6. Android Camera ITS, Brycen Korea와 함께 시작할 수 있습니다.
"""
    target.write_text(text, encoding="utf-8")


def render_video(slide_dir: Path, output_video: Path) -> None:
    input_args: list[str] = []
    for idx, slide in enumerate(SLIDES, start=1):
        input_args.extend(["-loop", "1", "-t", str(slide.duration), "-i", str(slide_dir / f"slide_{idx:02d}.png")])

    cumulative = 0
    transition = 1
    filter_parts = []
    last = "[0:v]"
    for idx in range(1, len(SLIDES)):
        cumulative += SLIDES[idx - 1].duration - transition
        current = f"[{idx}:v]"
        out = f"[v{idx}]"
        filter_parts.append(f"{last}{current}xfade=transition=fade:duration={transition}:offset={cumulative}{out}")
        last = out
    filter_parts.append(f"{last}format=yuv420p[video]")
    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg",
        "-y",
        *input_args,
        "-filter_complex",
        filter_complex,
        "-map",
        "[video]",
        "-r",
        "30",
        "-pix_fmt",
        "yuv420p",
        str(output_video),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    workspace = Path(__file__).resolve().parents[1]
    runtime = workspace / "runtime" / "expo-video"
    slide_dir = runtime / "slides"
    runtime.mkdir(parents=True, exist_ok=True)
    slide_dir.mkdir(parents=True, exist_ok=True)

    logo_path = workspace / "assets" / "brycen-logo.png"
    logo = Image.open(logo_path).convert("RGBA") if logo_path.exists() else None
    demo_frame = workspace / "data" / "live-demo-frame.png"
    dashboard = workspace / "data" / "live-demo-frame.png"
    metrics = load_metrics(workspace / "data" / "latest-its-status.json")

    rendered = [
        slide_1(create_background(), logo),
        slide_2(create_background(), logo),
        slide_3(create_background(), logo),
        slide_4(create_background(), logo, demo_frame),
        slide_5(create_background(), logo, metrics, dashboard),
        slide_6(create_background(), logo),
    ]

    for idx, image in enumerate(rendered, start=1):
        image.save(slide_dir / f"slide_{idx:02d}.png", format="PNG")

    video_path = runtime / "BrycenKorea_Android_ITS_Promo_2026.mp4"
    render_video(slide_dir, video_path)
    write_srt(runtime / "BrycenKorea_Android_ITS_Promo_2026.srt")
    write_narration(workspace / "Doc" / "COEX_ITS_PROMO_NARRATION_KR.md")


if __name__ == "__main__":
    main()
