"""Check the staged tree against dataset.yaml, and optionally hash it.

    python manifest.py dataset.yaml --check  # scope rules + expected totals (fast); exit 1 on failure
    python manifest.py dataset.yaml          # sha256 every staged file -> <staging>/MANIFEST.sha256

Hashing is optional: uploads are verified against the Hub's own checksums with
``hf cache verify`` (``make verify``). The manifest exists to be committed alongside a
published revision as the record of what it contains, and to check a copy of the tree
without contacting the Hub. Its format is the one ``sha256sum -c`` understands.
"""
import argparse
import fnmatch
import hashlib
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from config import load

MANIFEST_NAME = "MANIFEST.sha256"
CHUNK = 64 << 20


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def staged_files(staging: str) -> list[str]:
    out = []
    for dirpath, _, files in os.walk(staging):
        for name in files:
            rel = os.path.relpath(os.path.join(dirpath, name), staging)
            if rel != MANIFEST_NAME:
                out.append(rel)
    return sorted(out)


def read_manifest(path: str) -> dict[str, str]:
    entries = {}
    with open(path) as f:
        for line in f:
            digest, rel = line.rstrip("\n").split("  ", 1)
            entries[rel] = digest
    return entries


def write_manifest(cfg: dict, workers: int) -> None:
    staging = cfg["staging_dir"]
    rels = staged_files(staging)
    print(f"hashing {len(rels)} files under {staging} with {workers} workers ...")
    with ThreadPoolExecutor(workers) as ex:
        digests = list(ex.map(lambda r: sha256_of(os.path.join(staging, r)), rels))
    out = os.path.join(staging, MANIFEST_NAME)
    with open(out, "w") as f:
        for rel, digest in zip(rels, digests):
            f.write(f"{digest}  {rel}\n")
    print(f"wrote {out}")


def check(cfg: dict) -> int:
    staging = cfg["staging_dir"]
    exp = cfg["expected"]
    problems: list[str] = []

    rels = staged_files(staging)
    total = sum(os.path.getsize(os.path.join(staging, r)) for r in rels)

    for r in rels:
        if any(r.startswith(p) for p in exp.get("forbidden_prefixes", [])):
            problems.append(f"forbidden prefix: {r}")
        if any(fnmatch.fnmatch(r, g) for g in exp.get("forbidden_globs", [])):
            problems.append(f"forbidden pattern: {r}")
    for req in exp.get("required_root_files", []):
        if req not in rels:
            problems.append(f"missing required root file: {req}")

    n = len(rels)
    if not exp["min_files"] <= n <= exp["max_files"]:
        problems.append(f"file count {n} outside [{exp['min_files']}, {exp['max_files']}]")
    if not float(exp["total_bytes_min"]) <= total <= float(exp["total_bytes_max"]):
        problems.append(f"total bytes {total} outside [{exp['total_bytes_min']}, {exp['total_bytes_max']}]")

    # The manifest is optional; cross-check it only if one has been written.
    manifest_path = os.path.join(staging, MANIFEST_NAME)
    if os.path.exists(manifest_path):
        listed = set(read_manifest(manifest_path))
        missing = sorted(set(rels) - listed)
        extra = sorted(listed - set(rels))
        if missing:
            problems.append(f"{len(missing)} staged file(s) not in manifest, e.g. {missing[0]}")
        if extra:
            problems.append(f"{len(extra)} manifest entr(ies) not staged, e.g. {extra[0]}")
    else:
        print(f"note: no {MANIFEST_NAME} in the staging tree (optional; see `make manifest`)")

    print(f"staged: {n} files, {total / 1e12:.3f} TB")
    if problems:
        print("CHECK FAILED:")
        for p in problems:
            print("  -", p)
        return 1
    print("CHECK OK")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    cfg = load(args.config)
    if args.check:
        sys.exit(check(cfg))
    write_manifest(cfg, args.workers)


if __name__ == "__main__":
    main()
