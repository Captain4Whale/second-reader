#!/usr/bin/env python3
"""Build the strict GitHub Pages projection for Annotation Pack v0."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract" / "annotation-pack" / "v0"
SCHEMA_SOURCE = CONTRACT / "schema"
EXAMPLES_SOURCE = CONTRACT / "examples"
SITE_ROOT = Path("schema") / "annotation-pack" / "v0"
SCHEMA_IRI = (
    "https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/"
    "annotation-pack.schema.json"
)
PROJECTION: tuple[tuple[Path, Path], ...] = (
    (
        SCHEMA_SOURCE / "annotation-pack.schema.json",
        SITE_ROOT / "annotation-pack.schema.json",
    ),
    (
        SCHEMA_SOURCE / "publication-pointer.schema.json",
        SITE_ROOT / "publication-pointer.schema.json",
    ),
    (
        SCHEMA_SOURCE / "validation-report.schema.json",
        SITE_ROOT / "validation-report.schema.json",
    ),
    (
        EXAMPLES_SOURCE / "highlight.annotation.json",
        SITE_ROOT / "examples" / "highlight.annotation.json",
    ),
    (
        EXAMPLES_SOURCE / "minimal-pack.json",
        SITE_ROOT / "examples" / "minimal-pack.json",
    ),
    (
        EXAMPLES_SOURCE / "note.annotation.json",
        SITE_ROOT / "examples" / "note.annotation.json",
    ),
)


def _copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise ValueError(f"missing Pages authority file: {source.relative_to(ROOT)}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _projected_files(destination: Path) -> dict[Path, bytes]:
    return {
        path.relative_to(destination): path.read_bytes()
        for path in destination.rglob("*")
        if path.is_file()
    }


def build(destination: Path) -> None:
    destination = destination.resolve()
    if destination in {Path.home().resolve(), ROOT.resolve(), Path("/").resolve()}:
        raise ValueError(f"refusing unsafe Pages destination: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / ".nojekyll").write_bytes(b"")
    for source, relative_destination in PROJECTION:
        _copy_file(source, destination / relative_destination)


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="annotation-pack-pages-") as temporary:
        destination = Path(temporary) / "_site"
        build(destination)
        expected = {Path(".nojekyll"): b""}
        expected.update(
            (relative_destination, source.read_bytes())
            for source, relative_destination in PROJECTION
        )
        actual = _projected_files(destination)
        if set(actual) != set(expected):
            missing = sorted(str(path) for path in set(expected) - set(actual))
            unexpected = sorted(str(path) for path in set(actual) - set(expected))
            raise ValueError(
                "Pages projection allowlist mismatch: "
                f"missing={missing}, unexpected={unexpected}"
            )
        for relative_path, expected_bytes in expected.items():
            if actual[relative_path] != expected_bytes:
                raise ValueError(
                    "published file is not byte-identical to authority: "
                    f"{relative_path}"
                )
        forbidden_roots = (
            destination / "ns" / "annotation-pack",
            destination / SITE_ROOT / "context",
        )
        if any(path.exists() for path in forbidden_roots):
            raise ValueError("minimal v0 must not publish a namespace or context")
        schema_bytes = actual[SITE_ROOT / "annotation-pack.schema.json"]
        digest = hashlib.sha256(schema_bytes).hexdigest()
        print(
            "Annotation Pack Pages projection is valid: "
            f"schema_iri={SCHEMA_IRI} schema_sha256={digest} files={len(actual)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output-dir", type=Path)
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        build(args.output_dir)
        print(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
