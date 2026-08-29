#!/usr/bin/env python3
"""Build the unified strict GitHub Pages projection for public contracts."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile

from build_annotation_pack_pages import PROJECTION as ANNOTATION_PACK_PROJECTION


ROOT = Path(__file__).resolve().parents[1]
READING_PRODUCT = ROOT / "contract" / "reading-product" / "v1"
READING_PRODUCT_SITE = Path("schema") / "reading-product" / "v1"
READING_PRODUCT_SCHEMA_IRI = (
    "https://captain4whale.github.io/second-reader/schema/reading-product/v1/"
    "reading-product-output.schema.json"
)
READING_PRODUCT_PROJECTION: tuple[tuple[Path, Path], ...] = (
    (
        READING_PRODUCT / "schema" / "reading-product-output.schema.json",
        READING_PRODUCT_SITE / "reading-product-output.schema.json",
    ),
    (
        READING_PRODUCT / "schema" / "publication-pointer.schema.json",
        READING_PRODUCT_SITE / "publication-pointer.schema.json",
    ),
    (
        READING_PRODUCT / "schema" / "validation-report.schema.json",
        READING_PRODUCT_SITE / "validation-report.schema.json",
    ),
    (
        READING_PRODUCT / "examples" / "complete-reading-product.json",
        READING_PRODUCT_SITE / "examples" / "complete-reading-product.json",
    ),
    (
        READING_PRODUCT / "examples" / "partial-reading-product.json",
        READING_PRODUCT_SITE / "examples" / "partial-reading-product.json",
    ),
)
PROJECTION = ANNOTATION_PACK_PROJECTION + READING_PRODUCT_PROJECTION


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


def augment(destination: Path) -> None:
    """Add Reading Product files to one exact Annotation Pack projection."""

    destination = destination.resolve()
    if destination in {Path.home().resolve(), ROOT.resolve(), Path("/").resolve()}:
        raise ValueError(f"refusing unsafe Pages destination: {destination}")
    if not destination.is_dir():
        raise ValueError(f"Pages destination does not exist: {destination}")
    expected_existing = {Path(".nojekyll"): b""}
    expected_existing.update(
        (relative_destination, source.read_bytes())
        for source, relative_destination in ANNOTATION_PACK_PROJECTION
    )
    actual_existing = _projected_files(destination)
    if actual_existing != expected_existing:
        raise ValueError("existing site is not the exact Annotation Pack projection")
    for source, relative_destination in READING_PRODUCT_PROJECTION:
        _copy_file(source, destination / relative_destination)

    expected_final = dict(expected_existing)
    expected_final.update(
        (relative_destination, source.read_bytes())
        for source, relative_destination in READING_PRODUCT_PROJECTION
    )
    if _projected_files(destination) != expected_final:
        raise ValueError("augmented unified contract projection is not exact")


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="second-reader-contract-pages-") as temporary:
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
            destination / "ns",
            destination / READING_PRODUCT_SITE / "context",
        )
        if any(path.exists() for path in forbidden_roots):
            raise ValueError("contract site must not publish a private namespace/context")
        schema_bytes = actual[
            READING_PRODUCT_SITE / "reading-product-output.schema.json"
        ]
        digest = hashlib.sha256(schema_bytes).hexdigest()
        print(
            "Contract Pages projection is valid: "
            f"reading_product_schema_iri={READING_PRODUCT_SCHEMA_IRI} "
            f"reading_product_schema_sha256={digest} files={len(actual)}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output-dir", type=Path)
    group.add_argument("--augment-output-dir", type=Path)
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    elif args.augment_output_dir is not None:
        augment(args.augment_output_dir)
        print(args.augment_output_dir)
    else:
        build(args.output_dir)
        print(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
