"""Focused tests for neutral reading-runtime artifact path helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.reading_runtime.artifacts import (
    annotation_pack_annotations_file,
    annotation_pack_current_pointer_file,
    annotation_pack_last_failed_report_file,
    annotation_pack_revision_dir,
    annotation_pack_revisions_dir,
    annotation_pack_track_dir,
    annotation_pack_validation_report_file,
    annotation_packs_dir,
)


REVISION_ID = "a" * 64
TRACK_SLUG = "second-reader-a0b1c2d3e4f5"


def test_annotation_pack_helpers_build_the_public_immutable_revision_layout(
    tmp_path: Path,
) -> None:
    track_dir = tmp_path / "public" / "annotation-packs" / TRACK_SLUG
    revision_dir = track_dir / "revisions" / REVISION_ID

    assert annotation_packs_dir(tmp_path) == tmp_path / "public" / "annotation-packs"
    assert annotation_pack_track_dir(tmp_path, TRACK_SLUG) == track_dir
    assert annotation_pack_revisions_dir(tmp_path, TRACK_SLUG) == track_dir / "revisions"
    assert annotation_pack_revision_dir(tmp_path, TRACK_SLUG, REVISION_ID) == revision_dir
    assert annotation_pack_current_pointer_file(tmp_path, TRACK_SLUG) == track_dir / "current.json"
    assert annotation_pack_last_failed_report_file(
        tmp_path,
        TRACK_SLUG,
    ) == track_dir / "last-failed-validation-report.json"
    assert annotation_pack_annotations_file(
        tmp_path,
        TRACK_SLUG,
        REVISION_ID,
    ) == revision_dir / "annotations.json"
    assert annotation_pack_validation_report_file(
        tmp_path,
        TRACK_SLUG,
        REVISION_ID,
    ) == revision_dir / "validation-report.json"
    assert not (tmp_path / "public").exists()


@pytest.mark.parametrize(
    "track_slug",
    [
        "",
        ".hidden",
        "UPPERCASE",
        "with/slash",
        r"with\\backslash",
        "../escape",
        "/absolute",
        "a" * 82,
        "unicode-轨道",
    ],
)
def test_annotation_pack_track_helpers_reject_unsafe_slugs(
    tmp_path: Path,
    track_slug: str,
) -> None:
    with pytest.raises(ValueError, match="track slug is invalid"):
        annotation_pack_track_dir(tmp_path, track_slug)


@pytest.mark.parametrize("track_slug", [None, 1, True, Path("track")])
def test_annotation_pack_track_helpers_reject_non_strings(
    tmp_path: Path,
    track_slug: object,
) -> None:
    with pytest.raises(TypeError, match="exact string"):
        annotation_pack_track_dir(tmp_path, track_slug)


def test_annotation_pack_track_helpers_reject_string_subclasses(tmp_path: Path) -> None:
    class TrackSlug(str):
        pass

    with pytest.raises(TypeError, match="exact string"):
        annotation_pack_track_dir(tmp_path, TrackSlug(TRACK_SLUG))


@pytest.mark.parametrize(
    "revision_id",
    [
        "",
        "a" * 63,
        "a" * 65,
        "A" * 64,
        "g" * 64,
        "../" + "a" * 61,
        "/" + "a" * 63,
    ],
)
def test_annotation_pack_revision_helpers_reject_unsafe_revision_ids(
    tmp_path: Path,
    revision_id: str,
) -> None:
    with pytest.raises(ValueError, match="revision id is invalid"):
        annotation_pack_revision_dir(tmp_path, TRACK_SLUG, revision_id)


@pytest.mark.parametrize("revision_id", [None, 1, True, Path("revision")])
def test_annotation_pack_revision_helpers_reject_non_strings(
    tmp_path: Path,
    revision_id: object,
) -> None:
    with pytest.raises(TypeError, match="exact string"):
        annotation_pack_revision_dir(tmp_path, TRACK_SLUG, revision_id)


def test_annotation_pack_revision_helpers_reject_string_subclasses(tmp_path: Path) -> None:
    class RevisionId(str):
        pass

    with pytest.raises(TypeError, match="exact string"):
        annotation_pack_revision_dir(tmp_path, TRACK_SLUG, RevisionId(REVISION_ID))
