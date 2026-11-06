# Bao Long Ho

## Slice My Name

![Slice My Name](assets/slice.gif)

**Last slice timestamp:** See `assets/latest_slice.json`

**Total render count:** See `assets/stats.json`

This repository generates a pre-rendered Fruit Ninja-style slicing animation for GitHub profile README usage.

### Input format

`slice.json` accepts only:

- `name`
- `timestamp`
- `slice.start`
- `slice.end`

### Local rendering

```bash
pip install -r requirements.txt
python -m renderer.build_gif --slice-json slice.json --output-gif assets/slice.gif --preview assets/preview.png --temp-dir /tmp/slice-frames
python -m renderer.update_metadata --timestamp "$(python -m renderer.build_gif --slice-json slice.json --output-gif assets/slice.gif --preview assets/preview.png --temp-dir /tmp/slice-frames)" --assets-dir assets
```

### Optional GitHub Pages

You can publish `assets/preview.png` and metadata JSON files using GitHub Pages if you want external embedding.
