import pytest

from scripts.q1_private_snapshot import capture, verify


def test_snapshot_is_independent_and_never_overwrites(tmp_path):
    source, dest = tmp_path / "source", tmp_path / "snapshot"
    source.mkdir()
    (source / "journal.jsonl").write_bytes(b'{"revision":1}\n')
    capture(source, dest)
    (source / "journal.jsonl").write_bytes(b'{"revision":1}\n{"revision":2}\n')
    assert verify(dest)["files"]["journal.jsonl"]["bytes"] == 15
    with pytest.raises(FileExistsError):
        capture(source, dest)
    (dest / "files/journal.jsonl").write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="hash mismatch"):
        verify(dest)


def test_external_symlink_is_not_silently_backed_up(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "external").symlink_to(tmp_path / "secret")
    with pytest.raises(ValueError, match="Symlink"):
        capture(source, tmp_path / "snapshot")
