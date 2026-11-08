import hashlib
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

from src.prompts.integrity import LOCK, check_published
from src.prompts.releases import read_texts
from tests.prompt_release_cases import render_hashes


def test_migration_preserves_all_complete_prompt_bytes():
    fixture = Path(__file__).parent / "fixtures/prompt_migration_v1.json"
    assert render_hashes() == json.loads(fixture.read_text())


def test_published_release_files_and_resolved_text_are_immutable():
    check_published()


def test_private_asset_missing_or_changed_fails_without_fallback(tmp_path):
    raw = b"invented private example"
    digest = hashlib.sha256(raw).hexdigest()
    version = tmp_path / "v1.md"
    version.write_text(
        "<!-- prompt:example -->\n{{private:" + digest + "}}\n<!-- /prompt -->"
    )
    with pytest.raises(FileNotFoundError, match="no example-free fallback"):
        read_texts(version, private_assets=tmp_path)
    (tmp_path / f"{digest}.txt").write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        read_texts(version, private_assets=tmp_path)
    (tmp_path / f"{digest}.txt").write_bytes(raw)
    assert read_texts(version, private_assets=tmp_path)["example"] == raw.decode()


def test_release_and_lock_cannot_be_edited_together(tmp_path, monkeypatch):
    from src.prompts import integrity

    original = json.loads(LOCK.read_text())
    for name in (
        "src/attentional_v2/prompts/versions",
        "src/prompts/versions",
        "tests/fixtures",
    ):
        shutil.copytree(integrity.BACKEND / name, tmp_path / name)
    monkeypatch.setattr(integrity, "BACKEND", tmp_path)
    monkeypatch.setattr(
        integrity,
        "LOCK",
        tmp_path / "src/attentional_v2/prompts/versions/published.json",
    )
    path = tmp_path / "src/attentional_v2/prompts/versions/digest/v24.md"
    path.write_text(path.read_text() + "changed\n")
    with pytest.raises(ValueError, match="Published prompt changed"):
        integrity.check_published(None)
    changed = json.loads(integrity.LOCK.read_text())
    entry = changed["releases"]["attentional_v2.digest.v24"]
    entry["release_sha256"] = integrity.release_receipt(entry)["release_sha256"]
    integrity.LOCK.write_text(json.dumps(changed))
    monkeypatch.setattr(
        integrity.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=json.dumps(original)),
    )
    with pytest.raises(ValueError, match="lock entry changed"):
        integrity.check_published("trusted-base")


def test_run_receipt_loads_only_active_releases(tmp_path, monkeypatch):
    from src.prompts import integrity

    lock = json.loads(LOCK.read_text())
    lock["releases"]["attentional_v2.digest.v0"] = {
        "version": "attentional_v2.digest.v0",
        "files": ["absent-retired-release.md"],
    }
    path = tmp_path / "published.json"
    path.write_text(json.dumps(lock))
    monkeypatch.setattr(integrity, "LOCK", path)
    assert set(integrity.active_releases()) == {
        "attentional_v2.chapter_zone.v2",
        "attentional_v2.ingest.v19",
        "attentional_v2.digest.v24",
    }
