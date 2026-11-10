"""Offline, non-destructive private directory snapshots with byte verification."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path


def fingerprint(path):
    h = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(root):
    root = Path(root).resolve(strict=True)
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlink requires explicit source selection: {path}")
        if path.is_file():
            result[path.relative_to(root).as_posix()] = {
                "bytes": path.stat().st_size,
                "sha256": fingerprint(path),
            }
    return result


def verify(folder):
    folder = Path(folder)
    receipt = json.loads((folder / "manifest.json").read_bytes())
    if inventory(folder / "files") != receipt["files"]:
        raise ValueError("Snapshot file inventory/hash mismatch")
    return receipt


def capture(source, destination):
    source, destination = (
        Path(source).resolve(strict=True),
        Path(destination).absolute(),
    )
    if destination.is_relative_to(source):
        raise ValueError("Snapshot destination must be outside source")
    before = inventory(source)
    destination.mkdir(parents=True, exist_ok=False)
    payload = destination / "files"
    payload.mkdir()
    for name in before:
        target = payload / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as out, (source / name).open("rb") as src:
            for chunk in iter(lambda: src.read(1024 * 1024), b""):
                out.write(chunk)
    if inventory(source) != before or inventory(payload) != before:
        raise ValueError("Source changed during capture; incomplete snapshot retained")
    receipt = {
        "schema": "q1-private-snapshot/1",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source),
        "files": before,
    }
    with (destination / "manifest.json").open("x") as out:
        json.dump(receipt, out, ensure_ascii=False, indent=2)
        out.write("\n")
    verify(destination)
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", nargs="?", type=Path)
    args = parser.parse_args()
    result = (
        capture(args.source, args.destination)
        if args.destination
        else verify(args.source)
    )
    print(
        json.dumps(
            {"files": len(result["files"]), "captured_at": result["captured_at"]}
        )
    )
