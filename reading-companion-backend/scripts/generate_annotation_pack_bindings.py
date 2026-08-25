#!/usr/bin/env python3
"""Generate Annotation Pack v0 Pydantic bindings and runtime schema copies."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


BACKEND_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = BACKEND_ROOT.parent
CONTRACT_ROOT = WORKSPACE_ROOT / "contract" / "annotation-pack" / "v0"
CANONICAL_SCHEMA = CONTRACT_ROOT / "schema" / "annotation-pack.schema.json"
AUXILIARY_SCHEMAS = (
    CONTRACT_ROOT / "schema" / "publication-pointer.schema.json",
    CONTRACT_ROOT / "schema" / "validation-report.schema.json",
)
GENERATED_MODEL = BACKEND_ROOT / "src" / "annotation_pack" / "_generated_models.py"
RUNTIME_RESOURCES = BACKEND_ROOT / "src" / "annotation_pack" / "resources"
CODEGEN_DISTRIBUTION = "datamodel-code-generator"
CODEGEN_VERSION = "0.74.0"
RUFF_DISTRIBUTION = "ruff"
RUFF_VERSION = "0.15.5"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_local_refs(value: Any, *, pointer: str = "") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}/{key}"
            if key == "$ref" and isinstance(child, str) and not child.startswith("#/"):
                raise SystemExit(
                    f"error: remote or external $ref is forbidden at {child_pointer}: {child}"
                )
            _assert_local_refs(child, pointer=child_pointer)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_local_refs(child, pointer=f"{pointer}/{index}")


def _codegen_executable() -> Path:
    candidate = Path(sys.executable).with_name("datamodel-codegen")
    if candidate.is_file():
        return candidate
    discovered = shutil.which("datamodel-codegen")
    if discovered:
        return Path(discovered)
    raise SystemExit(
        "error: datamodel-codegen is missing; install backend development dependencies"
    )


def _verify_tool_version(distribution: str, expected: str) -> None:
    try:
        installed = version(distribution)
    except PackageNotFoundError as exc:
        raise SystemExit(
            f"error: {distribution} is missing; install backend development dependencies"
        ) from exc
    if installed != expected:
        raise SystemExit(
            f"error: expected {distribution}=={expected}, found {installed}"
        )


def _render_generated_model(destination: Path) -> bytes:
    schema_bytes = CANONICAL_SCHEMA.read_bytes()
    _assert_local_refs(_load_json(CANONICAL_SCHEMA))
    _verify_tool_version(CODEGEN_DISTRIBUTION, CODEGEN_VERSION)
    _verify_tool_version(RUFF_DISTRIBUTION, RUFF_VERSION)
    header = (
        "# Generated file; do not edit. "
        f"source=contract/annotation-pack/v0/schema/{CANONICAL_SCHEMA.name} "
        f"sha256={_sha256(schema_bytes)} "
        f"tool=datamodel-code-generator=={CODEGEN_VERSION} "
        f"formatter=ruff=={RUFF_VERSION}"
    )
    command = [
        os.fspath(_codegen_executable()),
        "--input",
        os.fspath(CANONICAL_SCHEMA),
        "--input-file-type",
        "jsonschema",
        "--schema-version",
        "2020-12",
        "--schema-version-mode",
        "strict",
        "--strict-refs",
        "--no-allow-remote-refs",
        "--output",
        os.fspath(destination),
        "--output-model-type",
        "pydantic_v2.BaseModel",
        "--class-name",
        "AnnotationPackDocument",
        "--target-python-version",
        "3.11",
        "--target-pydantic-version",
        "2",
        "--snake-case-field",
        "--allow-population-by-field-name",
        "--use-standard-collections",
        "--use-union-operator",
        "--extra-fields",
        "forbid",
        "--formatters",
        "builtin",
        "ruff-format",
        "--disable-timestamp",
        "--custom-file-header",
        header,
        "--custom-file-header-mode",
        "replace",
    ]
    completed = subprocess.run(
        command,
        cwd=BACKEND_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode:
        raise SystemExit(completed.stdout.rstrip() or "error: model generation failed")
    return destination.read_bytes()


def _diff(path: Path, expected: bytes, actual: bytes) -> str:
    return "".join(
        difflib.unified_diff(
            actual.decode("utf-8").splitlines(keepends=True),
            expected.decode("utf-8").splitlines(keepends=True),
            fromfile=os.fspath(path),
            tofile=f"generated:{path.name}",
        )
    )


def _write_if_changed(path: Path, content: bytes) -> None:
    if path.is_file() and path.read_bytes() == content:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def _expected_artifacts(generated_model: bytes) -> dict[Path, bytes]:
    artifacts = {GENERATED_MODEL: generated_model}
    for schema in (CANONICAL_SCHEMA, *AUXILIARY_SCHEMAS):
        artifacts[RUNTIME_RESOURCES / schema.name] = schema.read_bytes()
    return artifacts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="report drift without modifying committed artifacts",
    )
    args = parser.parse_args()

    for schema in (CANONICAL_SCHEMA, *AUXILIARY_SCHEMAS):
        if not schema.is_file():
            raise SystemExit(f"error: missing contract schema: {schema}")
        _assert_local_refs(_load_json(schema))
    with tempfile.TemporaryDirectory(prefix="annotation-pack-codegen-") as temp_dir:
        generated_model = _render_generated_model(
            Path(temp_dir) / "_generated_models.py"
        )

    artifacts = _expected_artifacts(generated_model)
    if args.check:
        failures: list[str] = []
        for path, expected in artifacts.items():
            if not path.is_file():
                failures.append(f"missing generated artifact: {path}\n")
                continue
            actual = path.read_bytes()
            if actual != expected:
                failures.append(_diff(path, expected, actual))
        if failures:
            sys.stderr.write("".join(failures))
            return 1
        print("Annotation Pack generated artifacts are current.")
        return 0

    for path, content in artifacts.items():
        _write_if_changed(path, content)
        print(path.relative_to(WORKSPACE_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
