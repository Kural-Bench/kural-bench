# Brand

## The 4 + 3 grid

A kural has seven feet: four on line 1, three on line 2. That shape is the mark and the layout rule of every figure.

- Mark: seven palm leaves fanned on one pin, four long, then a gap, then three shorter (`draw_mark` in `tools/brand/figures.py`). Each leaf is a straight strip with round ends, separated from its neighbours by a true gap, not a stroke. The seventh leaf, the closing foot, is the shortest and is drawn in the accent.
- Wordmark: KuralBench in IBM Plex Sans SemiBold, with the Tamil word for kural small beside it.
- In figures a kural is always laid out in this grid, one seer per cell; cells are as wide as the widest seer needs, and the seventh is 72% of that.

## Colour

Two tones plus neutrals. No gradients, glow, drop shadows, emoji or pill-shaped chips; no second hue beside the accent.

| Role | Light | Dark |
|---|---|---|
| Background | `#FBFAF7` | `#0D1117` |
| Ink | `#16161A` | `#E8E6E1` |
| Rule | `#E4E1DA` | `#30363D` |
| Muted | `#6B6A66` | `#8B949E` |
| Accent (vermilion) | `#D23C2A` | `#FF6A55` |

The accent marks one thing per figure: the changed letter, the one-letter edit, the nirai label, the arrow out of the model.

## Type

IBM Plex Sans for text, IBM Plex Mono for ids and commands, Noto Sans Tamil for Tamil (see `tools/brand/FONTS.md` for why, and the font sources and checksums). All SIL OFL 1.1.

Every glyph is outlined to an SVG path. Text is shaped by HarfBuzz as whole runs, so Tamil vowel signs and pulli come out right; nothing is placed letter by letter. Each figure exists as `-light.svg` and `-dark.svg` in `.github/assets/` and is used through `<picture>` with `prefers-color-scheme`.

## Generating

`.venv/bin/python tools/brand/build.py` rebuilds the figures, the social preview, the README, `LEADERBOARD.md` and the results issue form. Every count comes from `data/dev/MANIFEST.json`, the item files, `source/` and a gold run; every Tamil string comes from the items, the source files or `kuralbench/prosody.py`.
