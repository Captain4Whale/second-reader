from copy import deepcopy
import json

import pytest

from scripts.q1_comparison import build_bundle, digest, encode, load_output, overlaps
from scripts.q1_comparison_fixture import synthetic_inputs, source_range


def test_half_open_ranges_crossing_and_unique_start_owner():
    inputs = synthetic_inputs()
    batch, mixed, key = build_bundle(*inputs)
    assert not overlaps(source_range(0, 14), source_range(14, 20))
    crossing = next(m for m in batch["marginalia"] if m["crosses_boundary"])
    assert len(crossing["overlapping_window_ids"]) == 2
    assert crossing["mixed_window_id"] == batch["windows"][0]["window_id"]
    appearances = [
        m
        for w in mixed["windows"]
        for m in w["marginalia"]
        if m["marginalia_id"] == crossing["marginalia_id"]
    ]
    assert len(appearances) == 1
    assert (
        len(key["marginalia"]) == 5
    )  # identical original m1/m2 across groups stay distinct
    assert (
        len({m["marginalia_id"] for w in mixed["windows"] for m in w["marginalia"]})
        == 5
    )


def test_start_outside_windows_is_reported_even_when_overlapping():
    sources, windows, groups, unit_set = synthetic_inputs()
    windows[0]["original_source_range"] = source_range(4, 14)
    batch, mixed, _ = build_bundle(sources, windows, groups, unit_set)
    assert len(batch["unassigned_items"]) == 2
    assert {r["reason"] for r in batch["unassigned_items"]} == {
        "anchor_start_outside_windows"
    }
    assert sum(len(w["marginalia"]) for w in mixed["windows"]) == 3


def test_projection_has_no_provenance_membership_or_predictable_ids():
    batch, mixed, key = build_bundle(*synthetic_inputs())
    text = encode(mixed).decode()
    for forbidden in [
        "run_id",
        "source_id",
        "prompt",
        "experiment_id",
        "group",
        "reconstructed",
        "request_sha256",
        "unit_id",
        "synthetic-model",
        "synthetic-run",
    ]:
        assert forbidden not in text
    assert set(mixed) == {"schema", "synthetic", "windows", "batch_id"}
    for w in mixed["windows"]:
        for m in w["marginalia"]:
            assert set(m) == {
                "marginalia_id",
                "type",
                "body_text",
                "source_quote",
                "original_source_range",
                "crosses_boundary",
            }
            assert len(m["marginalia_id"]) == 36
    assert batch["mixed_sha256"] == digest(mixed)
    assert batch["blind_key_sha256"] == digest(key)
    assert build_bundle(*synthetic_inputs())[1]["batch_id"] != mixed["batch_id"]


def test_empty_group_is_supported_but_missing_coverage_and_overlapping_windows_reject():
    sources, windows, groups, unit_set = synthetic_inputs()
    groups[1]["marginalia"] = []
    assert len(build_bundle(sources, windows, groups, unit_set)[0]["groups"]) == 2
    groups[1]["coverage"] = []
    with pytest.raises(ValueError, match="coverage"):
        build_bundle(sources, windows, groups, unit_set)
    windows[1]["original_source_range"] = source_range(13, 20)
    with pytest.raises(ValueError, match="overlap"):
        build_bundle(sources, windows, groups, unit_set)


def test_digest_contract_validates_source_quote_hashes_and_experiment_link(tmp_path):
    sources, windows, groups, _ = synthetic_inputs()
    text = "".join(w["paragraphs"][0]["text"] for w in windows)
    doc = {
        "chapters": [
            {
                "id": 1,
                "title": "合成章节",
                "paragraphs": [
                    {"paragraph_index": 1, "text": text, "href": "synthetic.xhtml"}
                ],
            }
        ]
    }
    (tmp_path / "source.json").write_bytes(encode(doc))
    g = deepcopy(groups[0])
    g["sources"][0]["book_document_path"] = "source.json"
    p = tmp_path / "output.json"
    p.write_bytes(encode(g))
    assert load_output(p, tmp_path / "absent-log")["synthetic"]
    g["marginalia"][0]["source_quote"] = "wrong"
    p.write_bytes(encode(g))
    with pytest.raises(ValueError):
        load_output(p, tmp_path / "absent-log")
    g["marginalia"][0]["source_quote"] = text[2:5]
    g.update(synthetic=False, experiment_id="E1")
    g["prompt"]["release_sha256"] = "a" * 64
    p.write_bytes(encode(g))
    log = tmp_path / "log.jsonl"
    log.write_text(
        json.dumps(
            dict(experiment_id="E1", run_ids=[g["run_id"]], prompts=[g["prompt"]])
        )
        + "\n"
    )
    assert load_output(p, log)["experiment_id"] == "E1"
    log.write_text("\n")
    with pytest.raises(ValueError, match="registered"):
        load_output(p, log)
