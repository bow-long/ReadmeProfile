from __future__ import annotations

from typing import Iterable

from shapely.geometry import LineString, Polygon
from shapely.ops import split


def build_slice_line(start: tuple[float, float], end: tuple[float, float], extend: float = 5000) -> LineString:
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        raise ValueError("slice start and end cannot be identical")

    length = (dx**2 + dy**2) ** 0.5
    ux, uy = dx / length, dy / length
    return LineString([(x1 - ux * extend, y1 - uy * extend), (x2 + ux * extend, y2 + uy * extend)])


def slice_polygons(polygons: Iterable[Polygon], line: LineString) -> list[Polygon]:
    fragments: list[Polygon] = []
    for poly in polygons:
        if not poly.intersects(line):
            fragments.append(poly)
            continue

        result = split(poly, line)
        if result.geom_type == "GeometryCollection":
            geoms = list(result.geoms)
        else:
            geoms = [result]

        for geom in geoms:
            if geom.geom_type == "Polygon" and geom.area > 0.5:
                # Preserve winding by rebuilding polygon from coordinates.
                fragments.append(Polygon(list(geom.exterior.coords)))

    return fragments
