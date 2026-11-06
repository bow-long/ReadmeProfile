from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
from shapely.affinity import rotate, translate
from shapely.geometry import LineString, Point, Polygon


@dataclass
class Body:
    polygon: Polygon
    velocity: np.ndarray
    angle: float
    angular_velocity: float
    centroid: np.ndarray


def _line_signed_distance(point: np.ndarray, line_start: np.ndarray, line_end: np.ndarray) -> float:
    v = line_end - line_start
    p = point - line_start
    return (v[0] * p[1] - v[1] * p[0])


def init_bodies(fragments: Iterable[Polygon], slice_line: LineString) -> list[Body]:
    coords = np.asarray(slice_line.coords)
    p1, p2 = coords[0], coords[-1]

    bodies: list[Body] = []
    for frag in fragments:
        c = np.array(frag.centroid.coords[0], dtype=float)
        side = np.sign(_line_signed_distance(c, p1, p2)) or 1.0
        push = np.array([0.0, -100.0]) + np.array([65.0 * side, -45.0])
        spin = 0.8 * side
        bodies.append(
            Body(
                polygon=frag,
                velocity=push,
                angle=0.0,
                angular_velocity=spin,
                centroid=c,
            )
        )
    return bodies


def step_bodies(bodies: list[Body], dt: float, gravity: float = 380.0) -> list[Body]:
    stepped: list[Body] = []
    for body in bodies:
        velocity = body.velocity.copy()
        velocity[1] += gravity * dt
        dx, dy = velocity * dt
        angle = body.angle + body.angular_velocity * dt
        angular_velocity = body.angular_velocity * 0.999

        moved = translate(body.polygon, xoff=float(dx), yoff=float(dy))
        c = np.array(moved.centroid.coords[0], dtype=float)
        rotated = rotate(moved, angle * 57.2958, origin=Point(c[0], c[1]))

        stepped.append(
            Body(
                polygon=rotated,
                velocity=velocity,
                angle=angle,
                angular_velocity=angular_velocity,
                centroid=c,
            )
        )
    return stepped
