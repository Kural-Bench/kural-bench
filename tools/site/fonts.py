#!/usr/bin/env python3
"""Subset the site fonts and write them as woff2 into site/fonts/ (the output is committed).

    python -m venv /tmp/v && /tmp/v/bin/pip install fonttools brotli && /tmp/v/bin/python tools/site/fonts.py

IBM Plex Sans 400/500/600 (Latin, Latin-1, punctuation), IBM Plex Mono 400 (Latin), Noto Sans Tamil 400/600 (the Tamil
block, joiners, digits and basic punctuation). The source TTFs come from tools/brand/fonts.py, which checks their
sha256. Also writes fonts/metrics.json (the size-adjust values for the fallback faces) and fonts/OFL.txt.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "site" / "fonts"

spec = importlib.util.spec_from_file_location("brand_fonts", ROOT / "tools" / "brand" / "fonts.py")
brand_fonts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(brand_fonts)

from fontTools import subset  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

LATIN = ([*range(0x20, 0x7F), *range(0xA0, 0x100)] + [0x2010, 0x2011, 0x2012, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C,
         0x201D, 0x2022, 0x2026, 0x2032, 0x2033, 0x2190, 0x2191, 0x2192, 0x2193, 0x2212, 0x2264, 0x2265, 0x2248, 0x00D7])
TAMIL = [*range(0x0B80, 0x0C00), 0x200C, 0x200D, *range(0x20, 0x7F), 0xA0, 0xB7, 0x2013, 0x2014, 0x2018, 0x2019,
         0x201C, 0x201D, 0x2026]
LATIN_FEATURES = ["kern", "liga", "calt", "tnum", "lnum", "pnum", "case", "ccmp", "locl", "mark", "mkmk", "zero"]

# output name -> (source ttf, code points, features)
FACES = {
    "plex-sans-400.woff2": ("IBMPlexSans-Regular.ttf", LATIN, LATIN_FEATURES),
    "plex-sans-500.woff2": ("IBMPlexSans-Medium.ttf", LATIN, LATIN_FEATURES),
    "plex-sans-600.woff2": ("IBMPlexSans-SemiBold.ttf", LATIN, LATIN_FEATURES),
    "plex-mono-400.woff2": ("IBMPlexMono-Regular.ttf", LATIN, LATIN_FEATURES),
    "noto-sans-tamil-400.woff2": ("NotoSansTamil-Regular.ttf", TAMIL, ["*"]),
    "noto-sans-tamil-600.woff2": ("NotoSansTamil-SemiBold.ttf", TAMIL, ["*"]),
}
OFL = """Copyright 2017 IBM Corp. (IBM Plex Sans, IBM Plex Mono), with Reserved Font Name "Plex".
Copyright 2022 The Noto Project Authors (https://github.com/notofonts/tamil).

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at: https://openfontlicense.org

-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded,
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply
to any document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components as
distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to a
new environment.

"Author" refers to any designer, engineer, programmer, technical
writer or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining
a copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components,
in Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name as
presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
"""
FREQ = "etaoinshrdlcumwfgypbvkjxqz"  # rough English letter order, for the fallback width estimate
WEIGHTS = [12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3, 4.0, 2.8, 2.8, 2.4, 2.4, 2.2, 2.0, 2.0, 1.9, 1.5, 1.0, 0.8,
           0.15, 0.15, 0.1, 0.07]


def subset_font(src, codepoints, features, dst):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = features
    opts.name_IDs = [1, 2, 3, 4, 6]
    opts.notdef_outline = True
    opts.glyph_names = False
    opts.drop_tables = opts.drop_tables + ["meta"]
    opts.hinting = False
    opts.desubroutinize = True
    font = TTFont(src)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=codepoints)
    sub.subset(font)
    font.flavor = "woff2"
    font.save(dst)


def avg_width(path):
    f = TTFont(path)
    cmap, hmtx, upem = f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm
    w = sum(hmtx[cmap[ord(c)]][0] * k for c, k in zip(FREQ, WEIGHTS)) / sum(WEIGHTS)
    return w / upem


def vmetrics(path):
    f = TTFont(path)
    h, upem = f["hhea"], f["head"].unitsPerEm
    return h.ascent / upem, -h.descent / upem, h.lineGap / upem


def metrics():
    """Size-adjust and vertical overrides for a local fallback that makes Plex Sans / Mono / Noto Tamil lay out like the
    web font before it loads."""
    out = {}
    fb = {"sans": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "mono": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"}
    src = {"sans": brand_fonts.DIR / "IBMPlexSans-Regular.ttf", "mono": brand_fonts.DIR / "IBMPlexMono-Regular.ttf"}
    for k in ("sans", "mono"):
        if not Path(fb[k]).exists():
            continue
        adj = avg_width(src[k]) / avg_width(fb[k])
        a, d, g = vmetrics(src[k])
        out[k] = {"size_adjust": round(adj, 4), "ascent": round(a / adj, 4), "descent": round(d / adj, 4),
                  "line_gap": round(g / adj, 4)}
    return out


def main():
    brand_fonts.ensure()
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (ttf, cps, feats) in FACES.items():
        subset_font(str(brand_fonts.DIR / ttf), cps, feats, str(OUT / name))
        print(f"{name:30s} {(OUT / name).stat().st_size / 1024:6.1f} KB")
    (OUT / "OFL.txt").write_text(OFL, encoding="utf8")
    (OUT / "metrics.json").write_text(json.dumps(metrics(), indent=1, sort_keys=True) + "\n", encoding="utf8")


if __name__ == "__main__":
    sys.exit(main())
