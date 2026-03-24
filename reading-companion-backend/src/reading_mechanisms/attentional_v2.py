"""Phase 1-8 adapter scaffold for the attentional_v2 reading mechanism."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from src.attentional_v2.evaluation import (
    MechanismIntegrityReport,
    build_normalized_eval_bundle,
    persist_normalized_eval_bundle,
    run_mechanism_integrity_checks,
)
from src.attentional_v2.runner import parse_attentional_v2, read_attentional_v2
from src.attentional_v2.storage import (
    ATTENTIONAL_V2_MECHANISM_KEY,
    artifact_map,
    initialize_artifact_tree,
)
from src.attentional_v2.survey import write_book_survey_artifacts
from src.reading_core import BookDocument
from src.reading_core.runtime_contracts import MechanismInfo, ParseRequest, ParseResult, ReadRequest, ReadResult


class AttentionalV2Mechanism:
    """Thin adapter for the in-progress attentional_v2 mechanism."""

    info = MechanismInfo(
        key=ATTENTIONAL_V2_MECHANISM_KEY,
        label="Attentional V2 scaffold (Phase 1-8)",
    )

    @property
    def key(self) -> str:
        """Backwards-compatible access to the mechanism key."""

        return self.info.key

    @property
    def label(self) -> str:
        """Backwards-compatible access to the mechanism label."""

        return self.info.label

    def initialize_artifacts(self, output_dir: Path) -> dict[str, object]:
        """Initialize the mechanism shell and schema-bearing Phase 1 artifacts."""

        return initialize_artifact_tree(output_dir)

    def describe_artifact_map(self, output_dir: Path) -> dict[str, str]:
        """Return the concrete Phase 1 artifact map for one output directory."""

        return artifact_map(output_dir)

    def build_survey_artifacts(
        self,
        output_dir: Path,
        book_document: BookDocument,
        *,
        policy_snapshot: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Persist the orientation-only survey artifacts for one parsed book."""

        return write_book_survey_artifacts(
            output_dir,
            book_document,
            policy_snapshot=policy_snapshot,
        )

    def build_normalized_eval_bundle(
        self,
        output_dir: Path,
        *,
        config_payload: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        """Build the Phase 8 normalized eval bundle from persisted artifacts."""

        return build_normalized_eval_bundle(output_dir, config_payload=config_payload)

    def persist_normalized_eval_bundle(
        self,
        output_dir: Path,
        *,
        config_payload: Mapping[str, object] | None = None,
    ) -> Path:
        """Persist the explicit normalized eval bundle for an eval run."""

        return persist_normalized_eval_bundle(output_dir, config_payload=config_payload)

    def run_mechanism_integrity_checks(self, output_dir: Path) -> MechanismIntegrityReport:
        """Run the Phase 8 structural integrity checks over persisted artifacts."""

        return run_mechanism_integrity_checks(output_dir)

    def parse_book(self, request: ParseRequest) -> ParseResult:
        """Run the real parse-stage attentional_v2 integration path."""

        return parse_attentional_v2(request, self.info)

    def read_book(self, request: ReadRequest) -> ReadResult:
        """Run the real attentional_v2 sequential live runner."""

        return read_attentional_v2(request, self.info)
