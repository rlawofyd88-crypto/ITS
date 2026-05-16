#!/usr/bin/env python3
"""Capture DUT/tablet screenshots for milestone-driven demo updates."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


SCENE_RE = re.compile(r"(scene(?:_extensions[/\\])?scene_[a-z_]+|scene\d(?:_\d|_[a-z])?)", re.IGNORECASE)
FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/segoeuib.ttf"),
    Path("C:/Windows/Fonts/segoeui.ttf"),
    Path("C:/Windows/Fonts/malgunbd.ttf"),
    Path("C:/Windows/Fonts/malgun.ttf"),
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def capture_screen(serial: str, remote_path: str, local_path: Path) -> None:
    temp_path = local_path.with_suffix(local_path.suffix + ".tmp")
    run(["adb", "-s", serial, "shell", "screencap", "-p", remote_path])
    run(["adb", "-s", serial, "pull", remote_path, str(temp_path)])
    os.replace(temp_path, local_path)


def is_mostly_dark(image_path: Path) -> bool:
    if not image_path.exists():
        return True
    with Image.open(image_path) as image:
        sample = image.convert("L").resize((64, 64))
        pixels = list(sample.getdata())
    return (sum(pixels) / max(1, len(pixels))) < 18


def find_chart_asset(workspace_root: Path, label: str) -> Path | None:
    match = SCENE_RE.search(label)
    if not match:
        return None
    scene_name = match.group(1).replace("\\", "/")
    camera_its_root = workspace_root / "aosp-cts" / "apps" / "CameraITS"
    if "scene_extensions/" in scene_name:
        chart_name = scene_name.split("/")[-1] + ".png"
        candidate = camera_its_root / "tests" / "scene_extensions" / scene_name.split("/")[-1] / chart_name
        return candidate if candidate.exists() else None
    candidate = camera_its_root / "tests" / scene_name / f"{scene_name}.png"
    return candidate if candidate.exists() else None


def extract_scene_name(label: str) -> str | None:
    match = SCENE_RE.search(label)
    if not match:
        return None
    return match.group(1).replace("\\", "/")


def force_open_tablet_chart(tablet_serial: str, scene_name: str) -> None:
    scene_leaf = scene_name.split("/")[-1]
    png_name = f"{scene_leaf}.png"
    try:
        run([
            "adb", "-s", tablet_serial, "shell",
            "am", "broadcast",
            "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file:///sdcard/Download/{png_name}",
        ])
    except subprocess.CalledProcessError:
        pass
    run([
        "adb", "-s", tablet_serial, "shell",
        "am", "start",
        "-a", "android.intent.action.VIEW",
        "-t", "image/png",
        "-d", f"file:///sdcard/Download/{png_name}",
    ])
    time.sleep(1.2)


def fit_crop(image: Image.Image, width: int, height: int) -> Image.Image:
    source_ratio = image.width / image.height
    target_ratio = width / height
    if source_ratio > target_ratio:
        crop_width = int(image.height * target_ratio)
        left = (image.width - crop_width) // 2
        image = image.crop((left, 0, left + crop_width, image.height))
    else:
        crop_height = int(image.width / target_ratio)
        top = (image.height - crop_height) // 2
        image = image.crop((0, top, image.width, top + crop_height))
    return image.resize((width, height))


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    preferred = FONT_CANDIDATES[:2] if bold else FONT_CANDIDATES
    for candidate in preferred:
        if candidate.exists():
            try:
                return ImageFont.truetype(str(candidate), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def build_demo_frame(
    workspace_root: Path,
    label: str,
    stage: str,
    dut_path: Path,
    tablet_path: Path | None,
    output_path: Path,
) -> None:
    canvas = Image.new("RGB", (1600, 900), "#07110f")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(40, bold=True)
    subtitle_font = load_font(25, bold=True)
    body_font = load_font(22)
    label_font = load_font(20, bold=True)
    badge_font = load_font(24, bold=True)

    dut_image = Image.open(dut_path).convert("RGB") if dut_path.exists() else Image.new("RGB", (1080, 2400), "#000000")
    tablet_image = Image.open(tablet_path).convert("RGB") if tablet_path and tablet_path.exists() else None
    chart_asset_path = find_chart_asset(workspace_root, label)
    chart_image = Image.open(chart_asset_path).convert("RGB") if chart_asset_path else None

    left_panel = fit_crop(dut_image, 980, 620)
    if is_mostly_dark(dut_path):
        gradient = Image.new("RGB", (980, 620), "#08110d")
        gradient_draw = ImageDraw.Draw(gradient)
        gradient_draw.rectangle((0, 0, 980, 620), fill="#08110d")
        gradient_draw.rectangle((0, 420, 980, 620), fill="#101d17")
        left_panel = gradient

        if chart_image:
            chart_card = fit_crop(chart_image, 640, 360)
            left_panel.paste(chart_card, (38, 40))
            draw_left = ImageDraw.Draw(left_panel)
            draw_left.rectangle((38, 40, 678, 400), outline="#6fd8a1", width=3)
            draw_left.text((52, 414), "ITS Chart Asset", fill="#dff6e8", font=label_font)

        if tablet_image:
            tablet_card = fit_crop(tablet_image, 240, 426)
            left_panel.paste(tablet_card, (700, 40))
            draw_left = ImageDraw.Draw(left_panel)
            draw_left.rectangle((700, 40, 940, 466), outline="#ffcc66", width=3)
            draw_left.text((712, 480), "Tablet State", fill="#f6f4ef", font=label_font)

    else:
        overlay = Image.new("RGBA", left_panel.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle((0, 540, 980, 620), fill=(5, 10, 8, 180))
        left_panel = Image.alpha_composite(left_panel.convert("RGBA"), overlay).convert("RGB")

    right_top = fit_crop(tablet_image, 480, 260) if tablet_image else Image.new("RGB", (480, 260), "#111915")
    right_bottom = fit_crop(chart_image, 480, 260) if chart_image else Image.new("RGB", (480, 260), "#14110c")

    canvas.paste(left_panel, (40, 170))
    canvas.paste(right_top, (1080, 170))
    canvas.paste(right_bottom, (1080, 460))

    draw.rectangle((40, 170, 1020, 790), outline="#2b4337", width=2)
    draw.rectangle((1080, 170, 1560, 430), outline="#2b4337", width=2)
    draw.rectangle((1080, 460, 1560, 720), outline="#2b4337", width=2)

    draw.text((40, 28), "ITS Milestone Capture", fill="#ffcc66", font=title_font)
    draw.text((40, 86), label, fill="#f6f4ef", font=subtitle_font)
    draw.text((1080, 132), "Tablet Snapshot", fill="#dff6e8", font=label_font)
    draw.text((1080, 422), "Chart Reference", fill="#dff6e8", font=label_font)

    badge_fill = "#61d394"
    if stage.upper() == "FAIL":
        badge_fill = "#ff6b57"
    elif stage.upper() in ("RUN", "CHART", "QUEUE"):
        badge_fill = "#ffcc66"
    draw.rounded_rectangle((1380, 34, 1548, 92), radius=10, fill=badge_fill)
    badge_text = stage.upper()
    text_box = draw.textbbox((0, 0), badge_text, font=badge_font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    text_x = 1380 + ((1548 - 1380) - text_width) / 2
    text_y = 34 + ((92 - 34) - text_height) / 2 - 2
    draw.text((text_x, text_y), badge_text, fill="#06110c", font=badge_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG")


def main() -> None:
    parser = argparse.ArgumentParser(description="Capture milestone screenshots for ITS demo.")
    parser.add_argument("--dut-serial", required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--stage", default="LIVE")
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--tablet-serial")
    args = parser.parse_args()

    data_dir = args.workspace_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    dut_output = data_dir / "live-dut-feed.png"
    capture_screen(args.dut_serial, "/sdcard/Download/codex_dut_live.png", dut_output)

    tablet_output = None
    scene_name = extract_scene_name(args.label)
    if args.tablet_serial:
        try:
            if args.stage.upper() == "CHART" and scene_name:
                force_open_tablet_chart(args.tablet_serial, scene_name)
            tablet_output = data_dir / "live-tablet-feed.png"
            capture_screen(args.tablet_serial, "/sdcard/Download/codex_tablet_live.png", tablet_output)
        except subprocess.CalledProcessError:
            pass

    build_demo_frame(
        args.workspace_root,
        args.label,
        args.stage,
        dut_output,
        tablet_output,
        data_dir / "live-demo-frame.png",
    )

    state = {
        "label": args.label,
        "stage": args.stage,
        "updatedAt": time.time(),
    }
    (data_dir / "live-demo-state.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
