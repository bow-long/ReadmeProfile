from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.textpath import TextPath
from shapely.geometry import Polygon
from shapely.ops import unary_union


@dataclass(frozen=True)
class Canvas:
    width: int = 1280
    height: int = 720


def _as_polygon(points: np.ndarray) -> Polygon | None:
    if len(points) < 3:
        return None
    poly = Polygon(points)
    if poly.is_empty or not poly.is_valid or poly.area <= 0.5:
        return None
    return poly.buffer(0)


def text_to_polygons(name: str, canvas: Canvas) -> list[Polygon]:
    if not name.strip():
        raise ValueError("name must be non-empty")

    font = FontProperties(fname=findfont("DejaVu Sans"), weight="bold")
    path = TextPath((0, 0), name, size=180, prop=font)
    raw_polys = path.to_polygons(closed_only=True)

    polygons: list[Polygon] = []
    for coords in raw_polys:
        poly = _as_polygon(np.asarray(coords, dtype=float))
        if poly is not None:
            polygons.append(poly)

    if not polygons:
        raise ValueError("failed to build text polygons")

    merged = unary_union(polygons)
    geom_list: Iterable[Polygon]
    if merged.geom_type == "Polygon":
        geom_list = [merged]
    else:
        geom_list = [g for g in merged.geoms if g.geom_type == "Polygon"]

    min_x, min_y, max_x, max_y = unary_union(list(geom_list)).bounds
    text_w = max_x - min_x
    text_h = max_y - min_y
    x_off = (canvas.width - text_w) / 2 - min_x
    y_off = (canvas.height - text_h) / 2 - min_y

    centered: list[Polygon] = []
    for poly in geom_list:
        coords = np.array(poly.exterior.coords)
        coords[:, 0] += x_off
        coords[:, 1] += y_off
        new_poly = Polygon(coords)
        if new_poly.is_valid and new_poly.area > 0.5:
            centered.append(new_poly)

    return centered
