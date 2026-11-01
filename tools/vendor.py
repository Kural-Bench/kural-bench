#!/usr/bin/env python3
"""Copy the listed fields of the pinned upstream files into source/ and write source/MANIFEST.json.

All text is read from the upstream repository and written back unchanged (no editing, no renormalisation).
Usage: python tools/vendor.py [--src PATH_TO_THIRUKKURAL] [--out source]
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

COMMIT = "f5e2b6753052d098b745b6857bfd3378071e6d65"
UPSTREAM = "ashwingopalsamy/thirukkural"
FILES = [
    ("kurals.jsonl", "data/core/kurals.jsonl",
     ["id", "number", "paal_number", "adhikaram_number", "position", "lines_ta", "text_status"], "CC0-1.0"),
    ("adhikarams.jsonl", "data/core/adhikarams.jsonl",
     ["number", "paal_number", "first_kural", "last_kural", "name_ta", "name_en"], "CC0-1.0"),
    ("pope1886-en.jsonl", "data/layers/pope1886-en.jsonl",
     ["kural_id", "text", "author", "work_title", "license"], "public domain"),
    ("drew-lazarus-en.jsonl", "data/layers/drew-lazarus-en.jsonl",
     ["kural_id", "text", "author", "work_title", "license"], "public domain"),
    ("aiyar1916-en.jsonl", "data/layers/aiyar1916-en.jsonl",
     ["kural_id", "text", "author", "work_title", "license"], "public domain"),
]
# 1.1.0 additions: (vendored name, upstream path, kept fields, upstream config, row filter name)
SIGNATURE_FILES = [
    ("variants_atlas.jsonl", "data/signature/variants_atlas.jsonl",
     ["kural_id", "reading_id", "text", "status", "same_letters_as_canonical", "ledger_id", "carrier_licences",
      "text_sha256"], "release/configs/variants_atlas.json", "not_share_alike_only"),
    ("parimelazhagar_struct.jsonl", "data/signature/parimelazhagar_struct.jsonl",
     ["kural_id", "pada_urai", "flags", "source_id", "locator", "source_sha256"],
     "release/configs/parimelazhagar_struct.json", None),
]
MIT_UPSTREAM = "release/licenses/MIT.txt"
MIT_OUT = "LICENSES/MIT-parimelazhagar_struct.txt"
MIT_NOTE = (
    "\n\n---\n"
    "Notes added by KuralBench (the text above is the file {up} of {repo} at commit {commit}, unchanged):\n"
    "- It applies to source/parimelazhagar_struct.jsonl, which carries Parimelazhagar's commentary as transcribed in\n"
    "  the dataset Selvakumarduraipandian/Thirukural (column Parimezhalagar_Urai), shared there under MIT terms.\n"
    "- The upstream repository records no copyright line (year or holder) for this notice, neither in the file above,\n"
    "  in release/configs/parimelazhagar_struct.json nor in docs/licensing.md; none is stated here either.\n"
)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _vendor_signature(src, out, manifest):
    for name, up, fields, cfg_path, flt in SIGNATURE_FILES:
        raw = (src / up).read_bytes()
        cfg_raw = (src / cfg_path).read_bytes()
        cfg = json.loads(cfg_raw)
        lines = []
        for line in raw.decode("utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if flt == "not_share_alike_only" and set(row["carrier_licences"]) == {"CC-BY-SA-4.0"}:
                continue  # these readings live in variants_atlas_sa (CC-BY-SA-4.0)
            lines.append(json.dumps({k: row[k] for k in fields}, ensure_ascii=False, separators=(",", ":")))
        data = ("\n".join(lines) + "\n").encode("utf-8")
        (out / name).write_bytes(data)
        manifest["files"][name] = {
            "upstream_path": up, "upstream_commit": COMMIT, "upstream_sha256": sha256_bytes(raw),
            "sha256": sha256_bytes(data), "rows": len(lines), "licence": cfg["license"], "fields": fields,
            "upstream_config": {"path": cfg_path, "sha256": sha256_bytes(cfg_raw), "name": cfg["name"],
                                "license": cfg["license"], "rows": cfg.get("rows"),
                                "description": cfg["description"], "data": cfg["data"]},
        }
        print(f"{name}: {len(lines)} rows")


def _vendor_mit(src, root, manifest):
    raw = (src / MIT_UPSTREAM).read_bytes()
    note = MIT_NOTE.format(up=MIT_UPSTREAM, repo=UPSTREAM, commit=COMMIT).encode("utf-8")
    dest = root / MIT_OUT
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(raw + note)
    manifest["licence_files"] = {MIT_OUT: {
        "upstream_path": MIT_UPSTREAM, "upstream_sha256": sha256_bytes(raw), "sha256": sha256_bytes(raw + note),
        "applies_to": "parimelazhagar_struct.jsonl"}}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", default=str(Path(__file__).resolve().parent.parent.parent / "thirukkural"))
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "source"))
    a = ap.parse_args(argv)
    src, out = Path(a.src), Path(a.out)
    try:
        head = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        head = None
    if head is not None and head != COMMIT:
        sys.exit(f"upstream is at {head}, expected {COMMIT}")
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"upstream_repo": UPSTREAM, "upstream_commit": COMMIT, "files": {}}
    for name, up, fields, lic in FILES:
        raw = (src / up).read_bytes()
        lines = []
        for line in raw.decode("utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            lines.append(json.dumps({k: row[k] for k in fields}, ensure_ascii=False, separators=(",", ":")))
        data = ("\n".join(lines) + "\n").encode("utf-8")
        (out / name).write_bytes(data)
        manifest["files"][name] = {
            "upstream_path": up, "upstream_commit": COMMIT, "upstream_sha256": sha256_bytes(raw),
            "sha256": sha256_bytes(data), "rows": len(lines), "licence": lic, "fields": fields,
        }
        print(f"{name}: {len(lines)} rows")
    _vendor_signature(src, out, manifest)
    _vendor_mit(src, out.parent, manifest)
    (out / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")


if __name__ == "__main__":
    main()
