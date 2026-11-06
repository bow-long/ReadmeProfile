from __future__ import annotations

import argparse
from pathlib import Path

import imageio.v2 as imageio

from renderer.render import FPS, render_frames


def build_gif(slice_json: Path, output_gif: Path, preview_png: Path, temp_dir: Path) -> str:
    frames, ts = render_frames(slice_json=slice_json, out_dir=temp_dir)

    images = [imageio.imread(frame) for frame in frames]
    output_gif.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(output_gif, images, duration=1 / FPS, loop=0)

    preview_png.parent.mkdir(parents=True, exist_ok=True)
    imageio.imwrite(preview_png, images[min(10, len(images) - 1)])
    return ts


def main() -> None:
    parser = argparse.ArgumentParser(description="Build slice animation gif")
    parser.add_argument("--slice-json", default="slice.json")
    parser.add_argument("--output-gif", default="assets/slice.gif")
    parser.add_argument("--preview", default="assets/preview.png")
    parser.add_argument("--temp-dir", default="/tmp/slice-frames")
    args = parser.parse_args()

    ts = build_gif(
        slice_json=Path(args.slice_json),
        output_gif=Path(args.output_gif),
        preview_png=Path(args.preview),
        temp_dir=Path(args.temp_dir),
    )
    print(ts)


if __name__ == "__main__":
    main()
