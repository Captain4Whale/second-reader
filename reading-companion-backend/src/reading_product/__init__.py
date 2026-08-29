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
    "ReadingProductValidationError",
    "SourceIdentity",
    "UnitBuildResult",
    "build_product_unit",
    "build_source_identity",
    "sha256_file",
]
