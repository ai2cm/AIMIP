"""Materialize source_dir from the DKRZ S3 archive, one `include` entry at a time.

    python fetch_source.py dataset.yaml [--dry-run]

Directories are fetched with ``aws s3 sync`` and single files with ``aws s3 cp``, both
anonymous (``--no-sign-request``) against ``s3_endpoint``. Only works while the DKRZ
store is reachable; otherwise point ``source_dir`` at an existing mirror.
"""
import argparse
import os
import subprocess
import sys

from config import load


def is_file_entry(entry: str) -> bool:
    # Include entries are either CMIP-style directories or a handful of documentation
    # files; the latter are the only ones carrying an extension.
    return "." in os.path.basename(entry)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--dry-run", action="store_true", help="print the aws commands without running them")
    args = ap.parse_args()
    cfg = load(args.config)
    src, endpoint, dest = cfg["s3_source"].rstrip("/"), cfg["s3_endpoint"], cfg["source_dir"]
    common = ["--endpoint-url", endpoint, "--no-sign-request"]

    for entry in cfg["include"]:
        local = os.path.join(dest, entry)
        if is_file_entry(entry):
            cmd = ["aws", "s3", "cp", f"{src}/{entry}", local, *common]
        else:
            cmd = ["aws", "s3", "sync", f"{src}/{entry}/", f"{local}/", *common]
        print(" ".join(cmd))
        if not args.dry_run:
            os.makedirs(os.path.dirname(local), exist_ok=True)
            if subprocess.run(cmd).returncode != 0:
                sys.exit(f"failed: {entry}")


if __name__ == "__main__":
    main()
