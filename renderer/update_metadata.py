from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def update_metadata(timestamp_display: str, assets_dir: Path) -> None:
    assets_dir.mkdir(parents=True, exist_ok=True)
    latest_slice = assets_dir / "latest_slice.json"
    stats_file = assets_dir / "stats.json"

    latest_slice.write_text(
        json.dumps(
            {
                "last_slice": timestamp_display,
                "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    stats = {"render_count": 0}
    if stats_file.exists():
        try:
            stats = json.loads(stats_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            stats = {"render_count": 0}

    stats["render_count"] = int(stats.get("render_count", 0)) + 1
    stats["last_render_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    stats_file.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update render metadata")
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--assets-dir", default="assets")
    args = parser.parse_args()

    update_metadata(args.timestamp, Path(args.assets_dir))
