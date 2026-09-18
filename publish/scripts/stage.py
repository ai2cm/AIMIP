"""Assemble the publishable tree described by dataset.yaml.

Every in-scope file under ``source_dir`` is hard-linked (same filesystem, no extra disk)
into ``staging_dir`` at the same relative path; files under ``assets_dir`` are then copied
on top. Prints a per-top-level-directory summary.

    python stage.py dataset.yaml            # link/copy
    python stage.py dataset.yaml --dry-run  # summary only
    python stage.py dataset.yaml --prune    # also delete staged files no longer in scope
"""
import argparse
import fnmatch
import os
import shutil
import sys
from collections import defaultdict

from config import load

MANIFEST_NAME = "MANIFEST.sha256"


def excluded(rel: str, cfg: dict) -> bool:
    """True if a staging-relative path is excluded by name or by glob.

    `exclude_dirs` is matched against every path component, so a directory is dropped
    wherever it appears, including at the root (a glob like `*/.ipynb_checkpoints/*`
    silently misses that case).
    """
    parts = rel.split("/")
    if any(p in cfg.get("exclude_dirs", []) for p in parts[:-1]):
        return True
    return any(fnmatch.fnmatch(rel, g) for g in cfg.get("exclude_globs", []))


def plan_source(cfg: dict) -> dict[str, str]:
    """Map staging-relative path -> absolute source path for every in-scope source file."""
    src_root = cfg["source_dir"]
    planned: dict[str, str] = {}
    for entry in cfg["include"]:
        abs_entry = os.path.join(src_root, entry)
        if os.path.isfile(abs_entry):
            if not excluded(entry, cfg):
                planned[entry] = abs_entry
            continue
        if not os.path.isdir(abs_entry):
            sys.exit(f"include entry not found under source_dir: {entry}")
        for dirpath, _, files in os.walk(abs_entry):
            for name in files:
                abs_path = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_path, src_root)
                if not excluded(rel, cfg):
                    planned[rel] = abs_path
    return planned


def plan_assets(cfg: dict) -> dict[str, str]:
    """Assets are filtered by the same rules: editing a card in Jupyter leaves a
    .ipynb_checkpoints directory next to it, which must not reach the dataset."""
    assets_root = cfg["assets_dir"]
    planned: dict[str, str] = {}
    for dirpath, _, files in os.walk(assets_root):
        for name in files:
            abs_path = os.path.join(dirpath, name)
            rel = os.path.relpath(abs_path, assets_root)
            if not excluded(rel, cfg):
                planned[rel] = abs_path
    return planned


def place(rel: str, src: str, staging: str, link: bool) -> None:
    dst = os.path.join(staging, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.lexists(dst):
        if link and os.path.samefile(src, dst):
            return  # already the right hard link
        os.remove(dst)  # never write through an existing hard link into source_dir
    if link:
        try:
            os.link(src, dst)
            return
        except OSError as err:  # cross-device etc.
            print(f"warning: hard link failed for {rel} ({err}); copying", file=sys.stderr)
    shutil.copy2(src, dst)


def summarize(planned: dict[str, str]) -> None:
    files = defaultdict(int)
    nbytes = defaultdict(int)
    for rel, src in planned.items():
        parts = rel.split("/")
        top = "/".join(parts[:2]) if len(parts) > 2 else parts[0]
        files[top] += 1
        nbytes[top] += os.path.getsize(src)
    width = max(len(k) for k in files)
    print(f"{'path':{width}s} {'files':>6s} {'GB':>9s}")
    for top in sorted(files, key=lambda k: -nbytes[k]):
        print(f"{top:{width}s} {files[top]:6d} {nbytes[top] / 1e9:9.2f}")
    print(f"{'TOTAL':{width}s} {sum(files.values()):6d} {sum(nbytes.values()) / 1e9:9.2f}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, change nothing")
    ap.add_argument("--prune", action="store_true", help="remove staged files that are no longer in scope")
    args = ap.parse_args()

    cfg = load(args.config)
    staging = cfg["staging_dir"]
    source = plan_source(cfg)
    assets = plan_assets(cfg)
    planned = {**source, **assets}  # assets override source at the same path
    overridden = sorted(set(source) & set(assets))
    if overridden:
        print("assets override source files:", ", ".join(overridden))

    summarize(planned)
    if args.dry_run:
        print(f"(dry run) would stage into {staging}")
        return

    os.makedirs(staging, exist_ok=True)
    for rel, src in source.items():
        if rel not in assets:
            place(rel, src, staging, link=True)
    for rel, src in assets.items():
        place(rel, src, staging, link=False)

    if args.prune:
        removed = 0
        for dirpath, dirs, files in os.walk(staging, topdown=False):
            for name in files:
                rel = os.path.relpath(os.path.join(dirpath, name), staging)
                if rel not in planned and rel != MANIFEST_NAME:
                    os.remove(os.path.join(dirpath, name))
                    removed += 1
            for d in dirs:
                full = os.path.join(dirpath, d)
                if not os.listdir(full):
                    os.rmdir(full)
        print(f"pruned {removed} out-of-scope file(s)")
    print(f"staged {len(planned)} files into {staging}")


if __name__ == "__main__":
    main()
