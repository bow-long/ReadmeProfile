from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from renderer.geometry import Canvas, text_to_polygons
from renderer.physics import init_bodies, step_bodies
from renderer.slicing import build_slice_line, slice_polygons

FPS = 30
DURATION_SECONDS = 10
TOTAL_FRAMES = FPS * DURATION_SECONDS


def _validate_payload(payload: dict[str, Any]) -> tuple[str, str, tuple[float, float], tuple[float, float]]:
    allowed_top = {"name", "timestamp", "slice"}
    if set(payload.keys()) != allowed_top:
        raise ValueError("payload must contain only: name, timestamp, slice")

    name = payload.get("name")
    timestamp = payload.get("timestamp")
    slice_payload = payload.get("slice")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("name must be non-empty string")
    if not isinstance(timestamp, str):
        raise ValueError("timestamp must be ISO-8601 string")
    if not isinstance(slice_payload, dict) or set(slice_payload.keys()) != {"start", "end"}:
        raise ValueError("slice must contain only start and end")

    start = slice_payload["start"]
    end = slice_payload["end"]
    if not (
        isinstance(start, list)
        and isinstance(end, list)
        and len(start) == 2
        and len(end) == 2
        and all(isinstance(v, (int, float)) for v in [*start, *end])
    ):
        raise ValueError("slice start/end must be numeric [x, y]")

    return name, timestamp, (float(start[0]), float(start[1])), (float(end[0]), float(end[1]))


def _fmt_timestamp(raw_ts: str) -> str:
    dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00")).astimezone(timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M UTC")


def _draw_poly(draw: ImageDraw.ImageDraw, coords: list[tuple[float, float]], fill: tuple[int, int, int]) -> None:
    draw.polygon(coords, fill=fill)


def _draw_slice_glow(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float]) -> None:
    colors = [(65, 220, 255, 60), (65, 220, 255, 130), (145, 245, 255, 230)]
    widths = [16, 10, 4]
    for color, width in zip(colors, widths):
        draw.line([start, end], fill=color, width=width)


def render_frames(slice_json: Path, out_dir: Path, canvas: Canvas = Canvas()) -> tuple[list[Path], str]:
    payload = json.loads(slice_json.read_text(encoding="utf-8"))
    name, raw_ts, start, end = _validate_payload(payload)
    ts_overlay = _fmt_timestamp(raw_ts)

    text_polys = text_to_polygons(name, canvas)
    slice_line = build_slice_line(start, end)
    fragments = slice_polygons(text_polys, slice_line)
    bodies = init_bodies(fragments, slice_line)

    out_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()

    dt = 1 / FPS
    half = TOTAL_FRAMES // 2
    states: list[list] = []
    sim_bodies = bodies
    for _ in range(half + 1):
        states.append(sim_bodies)
        sim_bodies = step_bodies(sim_bodies, dt)

    frames: list[Path] = []
    slash_visible_until = int(FPS * 1.7)

    for i in range(TOTAL_FRAMES):
        frame_bodies = states[i] if i <= half else states[TOTAL_FRAMES - i]
        img = Image.new("RGBA", (canvas.width, canvas.height), (13, 17, 23, 255))
        draw = ImageDraw.Draw(img, "RGBA")

        for body in frame_bodies:
            coords = [(float(x), float(y)) for x, y in body.polygon.exterior.coords]
            _draw_poly(draw, coords, (245, 245, 245))

        if i < slash_visible_until:
            _draw_slice_glow(draw, start, end)

        draw.text((40, canvas.height - 70), f"Last Slice:\n{ts_overlay}", fill=(155, 170, 190), font=font)

        frame_path = out_dir / f"frame_{i:03d}.png"
        img.save(frame_path, optimize=True)
        frames.append(frame_path)

    return frames, ts_overlay
