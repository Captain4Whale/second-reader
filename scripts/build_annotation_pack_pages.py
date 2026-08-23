#!/usr/bin/env python3
"""Build the allowlisted GitHub Pages projection for Annotation Pack v0."""

from __future__ import annotations

import argparse
import hashlib
from html import escape
from pathlib import Path
import shutil
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "contract" / "annotation-pack" / "v0"
SCHEMA_SOURCE = CONTRACT / "schema"
CONTEXT_SOURCE = CONTRACT / "context"
EXAMPLES_SOURCE = CONTRACT / "examples"
NAMESPACE_IRI = "https://captain4whale.github.io/second-reader/ns/annotation-pack#"
SCHEMA_IRI = (
    "https://captain4whale.github.io/second-reader/schema/annotation-pack/v0/"
    "annotation-pack.schema.json"
)
CONTEXT_SHA256 = "eb72eb498c4bb70360ed57d6f97a85ead6985b9c88921124dfb27e37f3400f70"
CONTEXT_FILENAME = "second-reader-annotation-context.jsonld"


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _namespace_index() -> bytes:
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Second Reader Annotation Pack namespace</title>
</head>
<body>
  <h1>Second Reader Annotation Pack namespace</h1>
  <p>Stable namespace: <code>{escape(NAMESPACE_IRI)}</code></p>
  <p>This vocabulary extends a W3C Web Annotation-aligned project profile. It is not a W3C vocabulary or a claim of full EPUB Annotations conformance.</p>
  <ul>
    <li><a href="{escape(SCHEMA_IRI)}">Canonical v0 Pack schema</a></li>
    <li><a href="../../schema/annotation-pack/v0/context/second-reader-annotation-context.jsonld">Committed JSON-LD context</a></li>
  </ul>
</body>
</html>
"""
    return document.encode("utf-8")


def build(destination: Path) -> None:
    destination = destination.resolve()
    if destination in {Path.home().resolve(), ROOT.resolve(), Path("/").resolve()}:
        raise ValueError(f"refusing unsafe Pages destination: {destination}")
    destination.mkdir(parents=True, exist_ok=False)
    (destination / ".nojekyll").write_bytes(b"")

    namespace_index = destination / "ns" / "annotation-pack" / "index.html"
    namespace_index.parent.mkdir(parents=True)
    namespace_index.write_bytes(_namespace_index())

    schema_destination = destination / "schema" / "annotation-pack" / "v0"
    for source_root, relative_root in (
        (SCHEMA_SOURCE, Path()),
        (CONTEXT_SOURCE, Path("context")),
        (EXAMPLES_SOURCE, Path("examples")),
    ):
        for source in sorted(path for path in source_root.iterdir() if path.is_file()):
            _copy_file(source, schema_destination / relative_root / source.name)


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="annotation-pack-pages-") as temporary:
        destination = Path(temporary) / "_site"
        build(destination)
        schema_target = (
            destination
            / "schema"
            / "annotation-pack"
            / "v0"
            / "annotation-pack.schema.json"
        )
        if (
            schema_target.read_bytes()
            != (SCHEMA_SOURCE / schema_target.name).read_bytes()
        ):
            raise ValueError(
                "published Pack schema is not byte-identical to the authority"
            )
        context_target = (
            destination
            / "schema"
            / "annotation-pack"
            / "v0"
            / "context"
            / CONTEXT_FILENAME
        )
        if (
            context_target.read_bytes()
            != (CONTEXT_SOURCE / context_target.name).read_bytes()
        ):
            raise ValueError("published context is not byte-identical to the authority")
        context_bytes = context_target.read_bytes()
        context_digest = hashlib.sha256(context_bytes).hexdigest()
        if context_digest != CONTEXT_SHA256:
            raise ValueError(
                "published context digest mismatch: "
                f"expected {CONTEXT_SHA256}, found {context_digest}"
            )
        if (
            NAMESPACE_IRI.rstrip("#").encode()
            not in (destination / "ns" / "annotation-pack" / "index.html").read_bytes()
        ):
            raise ValueError(
                "namespace landing page does not name the stable namespace"
            )
        digest = hashlib.sha256(schema_target.read_bytes()).hexdigest()
        print(f"Annotation Pack Pages projection is valid: schema_sha256={digest}")


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
