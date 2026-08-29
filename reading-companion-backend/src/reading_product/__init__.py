"""Mechanism-neutral Reading Product Output v1 APIs."""

from .builder import build_product_unit, build_source_identity, sha256_file
from .models import (
    CommitResult,
    CompletionEvidence,
    FinalizeResult,
    MarginaliaCandidate,
    ProductFinding,
    ProductMarginalia,
    ProductUnit,
    ReadingProductDocument,
    SourceIdentity,
    UnitBuildResult,
)
from .store import (
    ReadingProductProjectionError,
    ReadingProductStore,
    ReadingProductStoreError,
    public_reading_product_current_file,
    public_reading_product_revision_dir,
    runtime_reading_product_dir,
)
from .validation import ReadingProductValidationError

__all__ = [
    "CommitResult",
    "CompletionEvidence",
    "FinalizeResult",
    "MarginaliaCandidate",
    "ProductFinding",
    "ProductMarginalia",
    "ProductUnit",
    "ReadingProductDocument",
    "ReadingProductStore",
    "ReadingProductProjectionError",
    "ReadingProductStoreError",
    "ReadingProductValidationError",
    "SourceIdentity",
    "UnitBuildResult",
    "build_product_unit",
    "build_source_identity",
    "public_reading_product_current_file",
    "public_reading_product_revision_dir",
    "runtime_reading_product_dir",
    "sha256_file",
]
