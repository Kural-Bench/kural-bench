#!/usr/bin/env python3
"""Write the site's PNG icons from .github/avatar.png (stdlib only; the output in site/ is committed).

    python tools/site/icons.py

apple-touch-icon.png (180), icon-192.png, icon-512.png and favicon.ico (16, 32 and 48 px, PNG-encoded).
"""
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / ".github" / "avatar.png"
OUT = ROOT / "site"


def read_png(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, w, h = 8, b"", 0, 0
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
            assert (depth, ctype, interlace) == (8, 2, 0), "expected 8-bit RGB, not interlaced"
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    raw = zlib.decompress(idat)
    stride, bpp, rows, prev = w * 3, 3, [], bytearray(w * 3)
    for y in range(h):
        f = raw[y * (stride + 1)]
        cur = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        if f == 1:
            for i in range(bpp, stride):
                cur[i] = (cur[i] + cur[i - bpp]) & 255
        elif f == 2:
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                cur[i] = (cur[i] + ((cur[i - bpp] if i >= bpp else 0) + prev[i]) // 2) & 255
        elif f == 4:
            for i in range(stride):
                a, b, c = (cur[i - bpp] if i >= bpp else 0), prev[i], (prev[i - bpp] if i >= bpp else 0)
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                cur[i] = (cur[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(cur)
        prev = cur
    return w, h, rows


def resize(w, h, rows, size):
    """Box filter: each output pixel is the mean of the source area it covers."""
    k = w / size
    # horizontal pass
    tmp = []
    for row in rows:
        out = bytearray(size * 3)
        for x in range(size):
            x0, x1 = x * k, (x + 1) * k
            i0, i1 = int(x0), min(w, int(x1 + 0.999999))
            for c in range(3):
                s = tot = 0.0
                for i in range(i0, i1):
                    wt = min(i + 1, x1) - max(i, x0)
                    s += row[i * 3 + c] * wt
                    tot += wt
                out[x * 3 + c] = int(s / tot + 0.5)
        tmp.append(out)
    res = []
    for y in range(size):
        y0, y1 = y * k, (y + 1) * k
        j0, j1 = int(y0), min(h, int(y1 + 0.999999))
        out = bytearray(size * 3)
        for i in range(size * 3):
            s = tot = 0.0
            for j in range(j0, j1):
                wt = min(j + 1, y1) - max(j, y0)
                s += tmp[j][i] * wt
                tot += wt
            out[i] = int(s / tot + 0.5)
        res.append(out)
    return res


def png(size, rows):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def ico(images):
    head = struct.pack("<HHH", 0, 1, len(images))
    offset, entries, blobs = 6 + 16 * len(images), b"", b""
    for size, data in images:
        entries += struct.pack("<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        blobs += data
        offset += len(data)
    return head + entries + blobs


def main():
    w, h, rows = read_png(SRC)
    made = {}
    for size in (16, 32, 48, 180, 192, 512):
        made[size] = png(size, resize(w, h, rows, size))
    (OUT / "apple-touch-icon.png").write_bytes(made[180])
    (OUT / "icon-192.png").write_bytes(made[192])
    (OUT / "icon-512.png").write_bytes(made[512])
    (OUT / "favicon.ico").write_bytes(ico([(s, made[s]) for s in (16, 32, 48)]))
    for n in ("apple-touch-icon.png", "icon-192.png", "icon-512.png", "favicon.ico"):
        print(n, (OUT / n).stat().st_size)


if __name__ == "__main__":
    sys.exit(main())
