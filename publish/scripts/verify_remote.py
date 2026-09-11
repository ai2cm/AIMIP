"""Compare an uploaded revision with the local MANIFEST.sha256 (no local re-hashing).

    python verify_remote.py dataset.yaml [--revision main]

The Hub reports a sha256 for every Xet/LFS-tracked file, so comparing those against a
manifest that was hashed in parallel beforehand takes seconds. Small files stored inline
have no sha256; their git blob SHA-1 is computed locally instead (they are a few kB).

Reports files missing from the repo, extra files in the repo, and size or hash
mismatches; exits 1 on any difference.

Without a manifest, `hf cache verify` (make verify-full) does the same end-to-end check by
re-reading every local file, but hashes single-threaded: hours for a multi-TB tree.
"""
import argparse
import os
import sys

from huggingface_hub import HfApi
from huggingface_hub.hf_api import RepoFile
from huggingface_hub.utils.sha import git_hash

from config import load
from manifest import MANIFEST_NAME, read_manifest, sha256_of


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--revision", default="main")
    args = ap.parse_args()
    cfg = load(args.config)
    staging = cfg["staging_dir"]
    repo_id, repo_type = cfg["repo_id"], cfg["repo_type"]

    manifest_path = os.path.join(staging, MANIFEST_NAME)
    if not os.path.exists(manifest_path):
        sys.exit(f"{manifest_path} not found: run `make manifest`, or use `make verify-full`.")
    local = read_manifest(manifest_path)
    local[MANIFEST_NAME] = sha256_of(manifest_path)  # the manifest is uploaded too

    api = HfApi()
    remote: dict[str, RepoFile] = {
        e.path: e
        for e in api.list_repo_tree(repo_id, repo_type=repo_type, revision=args.revision, recursive=True)
        if isinstance(e, RepoFile)
    }

    missing = sorted(set(local) - set(remote))
    extra = sorted(set(remote) - set(local))
    mismatched: list[str] = []
    for rel in sorted(set(local) & set(remote)):
        entry = remote[rel]
        path = os.path.join(staging, rel)
        local_size = os.path.getsize(path)
        if entry.size != local_size:
            mismatched.append(f"{rel}: size remote {entry.size} != local {local_size}")
            continue
        lfs_sha = getattr(entry.lfs, "sha256", None) if entry.lfs else None
        if lfs_sha:
            if lfs_sha.lower() != local[rel]:
                mismatched.append(f"{rel}: sha256 differs")
        else:
            # Inline (non-Xet) file: the Hub reports a git blob SHA-1, so hash the local
            # copy the same way. These are only the small text files.
            with open(path, "rb") as f:
                if git_hash(f.read()) != str(entry.blob_id).lower():
                    mismatched.append(f"{rel}: git blob sha1 differs")

    print(f"manifest: {len(local)} files; remote revision '{args.revision}': {len(remote)} files")
    print(f"missing from repo: {len(missing)}; extra in repo: {len(extra)}; mismatched: {len(mismatched)}")
    for label, items in (("MISSING", missing), ("EXTRA", extra), ("MISMATCH", mismatched)):
        for x in items[:20]:
            print(f"  {label}: {x}")
        if len(items) > 20:
            print(f"  ... {len(items) - 20} more {label.lower()}")
    if missing or extra or mismatched:
        sys.exit(1)
    print("VERIFY OK: the uploaded revision matches the manifest")


if __name__ == "__main__":
    main()
