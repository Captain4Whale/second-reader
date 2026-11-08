import hashlib
import json

import pytest

from src.prompts.integrity import LOCK, check_published
from src.prompts.releases import read_texts
from tests.prompt_release_cases import render_hashes


def test_migration_preserves_all_complete_prompt_bytes():
    fixture = __import__("pathlib").Path(__file__).parent / "fixtures/prompt_migration_v1.json"
    assert render_hashes() == json.loads(fixture.read_text())


def test_published_release_files_and_resolved_text_are_immutable():
    check_published()


def test_private_asset_missing_or_changed_fails_without_fallback(tmp_path):
    raw = b"invented private example"
    digest = hashlib.sha256(raw).hexdigest()
    version = tmp_path / "v1.md"
    version.write_text("<!-- prompt:example -->\n{{private:" + digest + "}}\n<!-- /prompt -->")
    with pytest.raises(FileNotFoundError, match="no example-free fallback"):
        read_texts(version, private_assets=tmp_path)
    (tmp_path / f"{digest}.txt").write_bytes(b"changed")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        read_texts(version, private_assets=tmp_path)
    (tmp_path / f"{digest}.txt").write_bytes(raw)
    assert read_texts(version, private_assets=tmp_path)["example"] == raw.decode()
