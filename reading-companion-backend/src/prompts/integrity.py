"""Version fingerprints and append-only publication checks; no model calls."""

import hashlib
import json
import re
import subprocess

from .releases import BACKEND, read_texts

LOCK = BACKEND / "src/attentional_v2/prompts/versions/published.json"


def canonical(value) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode()


def file_receipt(relative: str) -> dict:
    path = BACKEND / relative
    raw = path.read_bytes()
    return {
        "path": relative,
        "file_sha256": hashlib.sha256(raw).hexdigest(),
        "text_sha256": hashlib.sha256(canonical(read_texts(path))).hexdigest(),
        "private_assets": sorted(
            set(re.findall(r"\{\{private:([a-f0-9]{64})\}\}", raw.decode()))
        ),
    }


def release_receipt(entry: dict) -> dict:
    files = [file_receipt(path) for path in entry["files"]]
    return {
        "version": entry["version"],
        "release_sha256": hashlib.sha256(canonical(files)).hexdigest(),
        "files": files,
    }


def active_releases() -> dict:
    from src.attentional_v2.prompts import ATTENTIONAL_V2_PROMPTS as prompts

    entries = json.loads(LOCK.read_text())["releases"]
    versions = (
        prompts.chapter_zone_version,
        prompts.ingest_version,
        prompts.digest_version,
    )
    return {version: release_receipt(entries[version]) for version in versions}


def check_published(base_ref: str | None = "HEAD") -> dict:
    lock = json.loads(LOCK.read_text())
    acceptance = lock.get("migration_acceptance")
    if (
        acceptance
        and hashlib.sha256((BACKEND / acceptance["path"]).read_bytes()).hexdigest()
        != acceptance["sha256"]
    ):
        raise ValueError("Original migration acceptance fixture changed")
    for key, entry in lock["releases"].items():
        if release_receipt(entry)["release_sha256"] != entry["release_sha256"]:
            raise ValueError(f"Published prompt changed: {key}; publish a new version")
    if base_ref:
        relative = str(LOCK.relative_to(BACKEND.parent))
        old = subprocess.run(
            ["git", "-C", str(BACKEND), "show", f"{base_ref}:{relative}"],
            capture_output=True,
            text=True,
        )
        if old.returncode == 0:
            previous = json.loads(old.stdout)
            if (
                previous.get("migration_acceptance")
                and lock.get("migration_acceptance") != previous["migration_acceptance"]
            ):
                raise ValueError("Original migration acceptance lock changed")
            for key, entry in previous["releases"].items():
                if lock["releases"].get(key) != entry:
                    raise ValueError(f"Published lock entry changed/removed: {key}")
    return lock
